"""Document Query Assistant - Main Streamlit Application with Vector DB."""

import logging
import os
from datetime import datetime

import streamlit as st

from config import get_gemini_api_key, validate_api_key
from services import (
    DocumentChunker,
    EmbeddingService,
    VectorDB,
    extract_text,
)
from services.gemini_service import generate_response, initialize_gemini
from utils import (
    add_message,
    clear_all,
    clear_messages,
    get_messages,
    get_recent_history,
    get_uploaded_files,
    initialize_session_state,
    remove_file,
)

# Configure Page
st.set_page_config(
    page_title="Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Enhanced CSS for better UI
st.markdown("""
<style>
    .stChatFloatingInputContainer {
        padding-bottom: 20px;
    }
    .welcome-title {
        text-align: center;
        margin-top: 50px;
        font-size: 2.5rem;
    }
    .welcome-subtitle {
        text-align: center;
        color: gray;
        font-size: 1.1rem;
    }
    .doc-card {
        background: #f0f2f6;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    .chat-timestamp {
        font-size: 0.75rem;
        color: gray;
        margin-top: 4px;
    }
    .vector-badge {
        background: linear-gradient(90deg, #FF4B4B, #FF6B6B);
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


def initialize_services():
    """Initialize vector DB and related services."""
    if "vector_db" not in st.session_state:
        st.session_state.vector_db = VectorDB()
    if "chunker" not in st.session_state:
        st.session_state.chunker = DocumentChunker(
            chunk_size=1000,
            chunk_overlap=200
        )
    if "embedding_service" not in st.session_state:
        st.session_state.embedding_service = EmbeddingService()


# Initialize session state
initialize_session_state()
initialize_services()


def process_document_with_vector_db(filename: str, text: str) -> bool:
    """
    Process a document and add to vector database.

    Args:
        filename: Document filename.
        text: Extracted text content.

    Returns:
        True if successful, False otherwise.
    """
    try:
        api_key = get_gemini_api_key()

        # Initialize embeddings if needed
        if not st.session_state.embedding_service.is_ready():
            if not st.session_state.embedding_service.initialize(api_key):
                logger.error("Failed to initialize embeddings")
                return False

        # Set embeddings for vector DB
        embeddings = st.session_state.embedding_service.get_embeddings()
        st.session_state.vector_db.set_embeddings(embeddings)

        # Chunk the document
        chunks = st.session_state.chunker.chunk_with_metadata(
            text=text,
            source=filename
        )

        # Add to vector DB
        success = st.session_state.vector_db.add_document(
            doc_id=filename,
            chunks=chunks
        )

        if success:
            stats = st.session_state.vector_db.get_stats()
            logger.info(
                f"Document '{filename}' processed: "
                f"{len(chunks)} chunks, {stats['total_chunks']} total in DB"
            )
            return True
        else:
            logger.error(f"Failed to add document '{filename}' to vector DB")
            return False

    except Exception as e:
        logger.error(f"Error processing document with vector DB: {e}")
        return False


def search_and_answer(
    query: str,
    selected_file: str,
    conversation_context: str
) -> str:
    """
    Search vector DB and generate answer using Gemini.

    Args:
        query: User's question.
        selected_file: Selected document filename.
        conversation_context: Recent conversation context.

    Returns:
        Generated answer text.
    """
    try:
        # Search for relevant chunks
        relevant_chunks = st.session_state.vector_db.search(
            query=query,
            doc_id=selected_file,
            k=5
        )

        if not relevant_chunks:
            return (
                "I couldn't find relevant information in the document to "
                "answer your question. Try rephrasing your question."
            )

        # Build context from relevant chunks
        chunk_contexts = []
        for i, (chunk_text, score, metadata) in enumerate(relevant_chunks, 1):
            chunk_contexts.append(
                f"Relevant excerpt {i} (relevance: {score:.2f}):\n"
                f"{chunk_text}\n"
            )

        context = "\n---\n".join(chunk_contexts)

        # Build the prompt
        full_prompt = (
            "You are a document query assistant. Answer questions based on "
            "the relevant document excerpts provided below.\n\n"
            f"{context}\n\n"
            f"Recent conversation:\n{conversation_context}\n\n"
            f"Question: {query}\n\n"
            "Provide a concise, accurate answer. If the answer cannot be "
            "found in the excerpts, state: 'The document does not contain "
            "information to answer this question.' Reference specific parts "
            "of the text when possible."
        )

        # Initialize Gemini
        api_key = get_gemini_api_key()
        model = initialize_gemini(api_key)

        if not model:
            return "Error: Gemini model not configured properly."

        # Generate response
        response_text, error = generate_response(model, full_prompt)

        if response_text:
            return response_text
        else:
            return f"Error: {error}"

    except Exception as e:
        logger.error(f"Error in search_and_answer: {e}")
        return f"Error generating response: {str(e)}"


def render_api_key_config():
    """Render API key configuration in sidebar if not set."""
    api_key = get_gemini_api_key()

    if not validate_api_key(api_key):
        st.sidebar.warning("⚠️ API Key Required")
        api_key_input = st.sidebar.text_input(
            "Enter your Gemini API Key",
            type="password",
            help="Get your API key from https://aistudio.google.com/app/apikey",
            key="api_key_input"
        )

        if api_key_input and len(api_key_input) > 20:
            os.environ["GEMINI_API_KEY"] = api_key_input
            st.sidebar.success("✅ API key configured!")
            st.rerun()
        return False

    return True


def render_sidebar():
    """Render the sidebar with document upload and management."""
    with st.sidebar:
        st.title("📄 Document Intelligence")
        st.markdown('<span class="vector-badge">⚡ Vector DB Enabled</span>', unsafe_allow_html=True)
        st.write("Upload documents and ask questions about their content.")
        st.divider()

        # Document Upload
        st.markdown("### Upload Document")
        uploaded_file = st.file_uploader(
            "Upload a PDF, DOCX, or TXT file",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            filename = uploaded_file.name
            uploaded_files = get_uploaded_files()

            if filename not in uploaded_files:
                with st.spinner(f"Processing {filename}..."):
                    try:
                        # Log file info for debugging
                        uploaded_file.seek(0)
                        file_content = uploaded_file.read()
                        file_size = len(file_content)
                        logger.info(f"Processing file: {filename}, size: {file_size:,} bytes")

                        # Reset and extract
                        uploaded_file.seek(0)
                        text = extract_text(uploaded_file, filename)

                        has_error = (
                            text.startswith("Error") or
                            text.startswith("Unsupported") or
                            text.startswith("No text could be extracted")
                        )
                        
                        if text and not has_error:
                            # Store raw text
                            st.session_state.uploaded_files[filename] = text

                            # Process with vector DB
                            with st.spinner("🔍 Creating vector index..."):
                                vector_success = process_document_with_vector_db(filename, text)

                            if vector_success:
                                st.success(f"✅ Processed: {filename}")

                                # Show file stats
                                word_count = len(text.split())
                                char_count = len(text)
                                chunk_count = st.session_state.chunker.estimate_chunks(text)

                                st.info(
                                    f"📊 {word_count:,} words | "
                                    f"{char_count:,} chars | "
                                    f"~{chunk_count['estimated_chunks']} chunks"
                                )
                            else:
                                st.warning(
                                    "⚠️ Document uploaded but vector indexing failed. "
                                    "Basic search will be used."
                                )
                        else:
                            # Show detailed error message
                            st.error(f"❌ Failed to process {filename}")

                            # Show error details in expandable section
                            with st.expander("🔍 View error details"):
                                st.error(text)

                                # Provide helpful suggestions based on error
                                error_lower = text.lower()

                                if "encrypted" in error_lower:
                                    st.warning(
                                        "**Solution:** Please remove the password from the PDF "
                                        "and try uploading again."
                                    )
                                elif "not a valid pdf" in error_lower:
                                    st.warning(
                                        "**Solution:** The file appears to be corrupted or not "
                                        "a PDF. Please check the file format."
                                    )
                                elif "no text could be extracted" in error_lower:
                                    st.warning(
                                        "**Possible reasons:**\n"
                                        "- The PDF is a scanned image (no text layer)\n"
                                        "- The PDF uses complex formatting\n\n"
                                        "**Solutions:**\n"
                                        "1. Use OCR software to extract text first\n"
                                        "2. Convert to TXT format and upload\n"
                                        "3. Copy text manually and save as .txt file"
                                    )
                                elif "txt" in filename.lower() or "text" in filename.lower():
                                    st.warning(
                                        "**TXT File Troubleshooting:**\n"
                                        "- Check if the file is actually a text file\n"
                                        "- Try opening in Notepad to verify it's readable\n"
                                        "- Ensure the file isn't empty\n"
                                        "- Check file permissions"
                                    )
                                else:
                                    st.warning(
                                        "**Try these solutions:**\n"
                                        "1. Ensure the file is not corrupted\n"
                                        "2. Try converting to a different format\n"
                                        "3. Check the file extension matches the content"
                                    )

                            logger.error(f"Document processing failed for {filename}: {text}")

                    except Exception as upload_error:
                        st.error(f"❌ Unexpected error processing {filename}")
                        with st.expander("🔍 View error details"):
                            st.exception(upload_error)
                        logger.exception(f"Unexpected error during file upload: {upload_error}")

        st.divider()

        # Active Documents
        st.markdown("### Active Documents")
        uploaded_files = get_uploaded_files()

        if not uploaded_files:
            st.info("No documents uploaded yet.")
        else:
            for filename in uploaded_files.keys():
                cols = st.columns([4, 1])
                with cols[0]:
                    st.markdown(f"📄 **{filename}**")
                with cols[1]:
                    if st.button("🗑️", key=f"del_{filename}"):
                        remove_file(filename)
                        st.session_state.vector_db.remove_document(filename)
                        st.rerun()

            st.divider()

            # Vector DB stats
            stats = st.session_state.vector_db.get_stats()
            st.markdown("**📊 Vector DB Stats:**")
            st.markdown(f"- Documents: {stats['total_documents']}")
            st.markdown(f"- Chunks: {stats['total_chunks']}")

            st.divider()

            # Clear buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    clear_messages()
                    st.rerun()
            with col2:
                if st.button("🗑️ Clear All", type="primary", use_container_width=True):
                    clear_all()
                    st.session_state.vector_db.clear_all()
                    st.rerun()


def render_welcome_screen():
    """Render the welcome screen when no documents are uploaded."""
    st.markdown(
        "<h1 class='welcome-title'>📄 Document Intelligence Platform</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p class='welcome-subtitle'>"
        "Get started by uploading a document in the sidebar to the left.</p>",
        unsafe_allow_html=True
    )

    # Feature highlights
    st.markdown("---")
    st.markdown("### ✨ Features")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("📤 **Upload Documents**\n\nSupport for PDF, DOCX, and TXT files")
    with col2:
        st.markdown("💬 **Ask Questions**\n\nNatural language queries about document content")
    with col3:
        st.markdown("🤖 **AI-Powered**\n\nIntelligent responses using Google Gemini")

    st.markdown("---")
    st.markdown("### 🚀 Vector DB Features")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🔍 **Semantic Search**\n\nFinds relevant content by meaning, not just keywords")
    with col2:
        st.markdown("📦 **Smart Chunking**\n\nDocuments split intelligently for better retrieval")
    with col3:
        st.markdown("🎯 **Context-Aware**\n\nAnswers based on most relevant document sections")


def render_chat_interface():
    """Render the main chat interface for document queries."""
    uploaded_files = get_uploaded_files()

    if not uploaded_files:
        render_welcome_screen()
        return

    # Document Selection Bar
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("**📋 Selected Document:**")
    with col2:
        file_options = list(uploaded_files.keys())

        # Maintain selection across reruns
        current_selection = st.session_state.get("selected_file")
        default_idx = 0
        if current_selection and current_selection in file_options:
            default_idx = file_options.index(current_selection)

        selected_file = st.selectbox(
            "Select document scope",
            file_options,
            index=default_idx,
            label_visibility="collapsed"
        )
        st.session_state.selected_file = selected_file

    st.divider()

    # Display chat history with timestamps
    for msg in get_messages():
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "timestamp" in msg:
                st.markdown(
                    f"<div class='chat-timestamp'>{msg['timestamp']}</div>",
                    unsafe_allow_html=True
                )

    # Chat Input
    if user_question := st.chat_input("Ask a question about your document..."):
        # Add user message with timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        add_message("user", user_question)

        with st.chat_message("user"):
            st.markdown(user_question)
            st.markdown(f"<div class='chat-timestamp'>{timestamp}</div>", unsafe_allow_html=True)

        # Generate response
        with st.chat_message("assistant"):
            if not selected_file:
                error_msg = "Please select a document first."
                st.error(error_msg)
                add_message("assistant", error_msg)
            else:
                with st.spinner("🔍 Searching document..."):
                    # Get recent conversation history
                    recent_history = get_recent_history(n=5)
                    conversation_context = "\n".join([
                        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                        for m in recent_history
                    ])

                    # Search and answer using vector DB
                    response_text = search_and_answer(
                        query=user_question,
                        selected_file=selected_file,
                        conversation_context=conversation_context
                    )

                    if response_text and not response_text.startswith("Error"):
                        st.markdown(response_text)
                        add_message("assistant", response_text)
                    else:
                        st.error(f"❌ {response_text}")
                        add_message("assistant", response_text)
                        logger.error(f"Response generation failed: {response_text}")


def main():
    """Main application entry point."""
    # Check API key configuration
    api_configured = render_api_key_config()

    if api_configured:
        render_sidebar()
        render_chat_interface()
    else:
        render_sidebar()
        st.info("👈 Please configure your API key in the sidebar to continue.")


if __name__ == "__main__":
    main()
