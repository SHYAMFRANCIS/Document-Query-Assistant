import streamlit as st
import os
import google.generativeai as genai
import logging
import PyPDF2
import docx

# Configure Page
st.set_page_config(page_title="Document Intelligence", page_icon="📄", layout="wide")

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Basic CSS to make it clean
st.markdown("""
<style>
    .stChatFloatingInputContainer {
        padding-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialization function for session state
def initialize_session_state():
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = {} # dict mapping filename -> text
    if "messages" not in st.session_state:
        st.session_state.messages = [] # list of dicts: {"role": "user"/"assistant", "content": text}

initialize_session_state()

# Gemini setup
@st.cache_resource
def get_gemini_model():
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDYDnb5_fZNK_IXg3Uw-GynalxsCrkqlog")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {str(e)}")
        st.error(f"Failed to configure Gemini API: {str(e)}")
        return None

model = get_gemini_model()

def extract_text_from_pdf(file_obj):
    try:
        text = ""
        pdf_reader = PyPDF2.PdfReader(file_obj)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text if text else "No text could be extracted from the PDF."
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def extract_text_from_docx(file_obj):
    try:
        doc = docx.Document(file_obj)
        text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        return text if text else "No text could be extracted from the DOCX."
    except Exception as e:
        return f"Error extracting text from DOCX: {str(e)}"

# Sidebar Layout
with st.sidebar:
    st.title("📄 Document Intelligence")
    st.write("Upload documents and ask questions about their content.")
    st.divider()
    
    st.markdown("### Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF or DOCX", type=["pdf", "docx"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        filename = uploaded_file.name
        if filename not in st.session_state.uploaded_files:
            with st.spinner(f"Processing {filename}..."):
                ext = os.path.splitext(filename)[1].lower()
                text = ""
                if ext == ".pdf":
                    text = extract_text_from_pdf(uploaded_file)
                elif ext == ".docx":
                    text = extract_text_from_docx(uploaded_file)
                
                if text and "Error" not in text:
                    st.session_state.uploaded_files[filename] = text
                    st.success(f"Processed: {filename}")
                else:
                    st.error(f"Failed to process {filename}")

    st.divider()
    st.markdown("### Active Documents")
    if not st.session_state.uploaded_files:
        st.info("No documents uploaded yet.")
    else:
        for file in st.session_state.uploaded_files.keys():
            st.markdown(f"- **{file}**")
        
        if st.button("Clear All Files", type="primary", use_container_width=True):
            st.session_state.uploaded_files = {}
            st.session_state.messages = []
            st.rerun()

# Main Interface
if not st.session_state.uploaded_files:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>Document Intelligence Platform</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Get started by uploading a document in the sidebar to the left.</p>", unsafe_allow_html=True)
else:
    # Top bar for context selection
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("**Selected Document:**")
    with col2:
        selected_file = st.selectbox("Select document scope", list(st.session_state.uploaded_files.keys()), label_visibility="collapsed")

    st.divider()

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if user_question := st.chat_input("Ask a question about your document..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        # Generate response
        with st.chat_message("assistant"):
            if not model:
                st.error("Gemini model is not configured properly.")
            elif not selected_file:
                st.error("Please select a document first.")
            else:
                with st.spinner("Thinking..."):
                    file_content = st.session_state.uploaded_files[selected_file]
                    file_context = f"Content from file '{selected_file}':\n\n{file_content}"
                    
                    recent_history = st.session_state.messages[-6:-1] # get last 5 msgs max
                    conversation_context = "\n".join([
                        f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}"
                        for m in recent_history
                    ])

                    full_prompt = (
                        "You are a document query-answering bot. Answer questions based solely on the provided document content.\n\n"
                        f"{file_context}\n\n"
                        f"Recent conversation:\n{conversation_context}\n\n"
                        f"Question: {user_question}\n\n"
                        "Provide a concise and accurate answer. If the answer cannot be found in the document, state: 'The document does not contain information to answer this question.'"
                    )
                    
                    try:
                        response = model.generate_content(full_prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")