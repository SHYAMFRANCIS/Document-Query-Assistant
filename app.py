"""Document Query Assistant - Main Streamlit Application."""

import logging
import os
from datetime import datetime

import streamlit as st

from config import get_gemini_api_key, validate_api_key
from services import extract_text
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
initialize_session_state()


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
                    text = extract_text(uploaded_file, filename)

                    if text and "Error" not in text and "Unsupported" not in text:
                        st.session_state.uploaded_files[filename] = text
                        st.success(f"✅ Processed: {filename}")

                        # Show file stats
                        word_count = len(text.split())
                        st.info(f"📊 {word_count} words extracted")
                    else:
                        st.error(f"❌ Failed to process {filename}")
                        logger.error(f"Document processing failed for {filename}: {text}")

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
                        st.rerun()

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
            # Initialize Gemini model
            api_key = get_gemini_api_key()
            model = initialize_gemini(api_key)

            if not model:
                error_msg = "❌ Gemini model is not configured properly. Please check your API key."
                st.error(error_msg)
                add_message("assistant", error_msg)
            elif not selected_file:
                error_msg = "Please select a document first."
                st.error(error_msg)
                add_message("assistant", error_msg)
            else:
                with st.spinner("🤔 Thinking..."):
                    try:
                        file_content = uploaded_files[selected_file]
                        file_context = f"Content from file '{selected_file}':\n\n{file_content}"

                        # Get recent conversation history
                        recent_history = get_recent_history(n=5)
                        conversation_context = "\n".join([
                            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                            for m in recent_history
                        ])

                        # Build the full prompt
                        full_prompt = (
                            "You are a document query bot. "
                            "Answer questions based solely on the provided document content.\n\n"
                            f"{file_context}\n\n"
                            f"Recent conversation:\n{conversation_context}\n\n"
                            f"Question: {user_question}\n\n"
                            "Provide a concise, accurate answer. If the answer cannot be found "
                            "in the document, state: 'The document does not contain information "
                            "to answer this question.'"
                        )

                        response_text, error = generate_response(model, full_prompt)

                        if response_text:
                            st.markdown(response_text)
                            add_message("assistant", response_text)
                        else:
                            st.error(f"❌ {error}")
                            add_message("assistant", f"Error: {error}")

                    except Exception as e:
                        error_msg = f"❌ Error generating response: {str(e)}"
                        st.error(error_msg)
                        add_message("assistant", error_msg)
                        logger.exception("Unexpected error during response generation")


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
