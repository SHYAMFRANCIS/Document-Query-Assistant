from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from datetime import datetime
import json
import logging
import tempfile
import PyPDF2
import docx

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gemini setup
api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDYDnb5_fZNK_IXg3Uw-GynalxsCrkqlog")
try:
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set.")
    genai.configure(api_key=api_key)
    logger.info("Gemini API configured successfully.")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")
    exit(1)

model = genai.GenerativeModel('gemini-1.5-flash')

# Conversation history
HISTORY_FILE = "conversation_history.json"
conversation_history = []
uploaded_files = {}  # Store file contents with filenames

def load_history():
    global conversation_history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            conversation_history = json.load(f)

def save_history():
    with open(HISTORY_FILE, 'w') as f:
        json.dump(conversation_history, f, indent=2)

def extract_text_from_pdf(path):
    try:
        text = ""
        with open(path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text if text else "No text could be extracted from the PDF."
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return f"Error extracting text from PDF: {str(e)}"

def extract_text_from_docx(path):
    try:
        doc = docx.Document(path)
        text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        return text if text else "No text could be extracted from the DOCX."
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        return f"Error extracting text from DOCX: {str(e)}"

def process_file(file):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx"]:
        return f"Unsupported file type: {ext}. Please upload a PDF or DOCX file."

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    file.save(temp.name)
    text = ""
    try:
        if ext == ".pdf":
            text = extract_text_from_pdf(temp.name)
        elif ext == ".docx":
            text = extract_text_from_docx(temp.name)
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        text = f"Error processing file: {str(e)}"
    finally:
        temp.close()
        try:
            os.unlink(temp.name)
        except Exception as e:
            logger.error(f"Could not delete temporary file {temp.name}: {str(e)}")
    return text

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        file = request.files.get("file")
        if not file or file.filename == '':
            logger.error("No file selected for upload")
            return jsonify({"response": "⚠️ No file selected."})

        logger.info(f"Processing file: {file.filename}")
        filename = file.filename
        file_content = process_file(file)

        if file_content.startswith("Unsupported file type") or file_content.startswith("Error"):
            logger.error(f"File processing failed: {file_content}")
            return jsonify({"response": file_content})

        uploaded_files[filename] = file_content
        logger.info(f"Successfully processed file: {filename}")

        conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": f"[Uploaded file: {filename}]",
            "bot": f"✅ File '{filename}' uploaded and processed. Ask questions about its content."
        })
        save_history()

        return jsonify({
            "response": f"✅ File '{filename}' uploaded and processed. Ask questions about its content.",
            "files": list(uploaded_files.keys())
        })
    except Exception as e:
        logger.error(f"Error in file upload: {str(e)}")
        return jsonify({"response": f"⚠️ Error uploading file: {str(e)}"}), 500

@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.form.get("user_input", "").strip()
    selected_file = request.form.get("selected_file", "").strip()

    if not user_question:
        return jsonify({"response": "⚠️ Please enter a question."})
    if not selected_file or selected_file not in uploaded_files:
        return jsonify({"response": "⚠️ Please select a valid uploaded file."})

    file_content = uploaded_files[selected_file]
    file_context = f"Content from file '{selected_file}':\n\n{file_content}"

    # Include recent conversation history for context
    recent_history = conversation_history[-5:] if len(conversation_history) > 0 else []
    conversation_context = "\n".join([
        f"User: {item['user']}\nAssistant: {item['bot']}"
        for item in recent_history if 'user' in item and 'bot' in item
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
        response_text = response.text.strip()
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        response_text = f"⚠️ Error generating response: {str(e)}"

    conversation_history.append({
        "timestamp": datetime.now().isoformat(),
        "user": user_question,
        "bot": response_text,
        "file": selected_file
    })
    save_history()

    return jsonify({
        "response": response_text,
        "files": list(uploaded_files.keys())
    })

@app.route("/files", methods=["GET"])
def get_files():
    return jsonify({"files": list(uploaded_files.keys())})

if __name__ == "__main__":
    load_history()
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
    except OSError as e:
        logger.error(f"Server error: {str(e)}")
        raise