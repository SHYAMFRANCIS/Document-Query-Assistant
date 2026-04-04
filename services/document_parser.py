"""Document parsing services for PDF, DOCX, and TXT files."""

import logging

import docx
import PyPDF2

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_obj) -> str:
    """
    Extract text from a PDF file.

    Args:
        file_obj: File-like object containing PDF data.

    Returns:
        Extracted text or error message.
    """
    try:
        text = ""
        pdf_reader = PyPDF2.PdfReader(file_obj)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text if text else "No text could be extracted from the PDF."
    except Exception as e:
        error_msg = f"Error extracting text from PDF: {str(e)}"
        logger.error(error_msg)
        return error_msg


def extract_text_from_docx(file_obj) -> str:
    """
    Extract text from a DOCX file.

    Args:
        file_obj: File-like object containing DOCX data.

    Returns:
        Extracted text or error message.
    """
    try:
        doc = docx.Document(file_obj)
        text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        return text if text else "No text could be extracted from the DOCX."
    except Exception as e:
        error_msg = f"Error extracting text from DOCX: {str(e)}"
        logger.error(error_msg)
        return error_msg


def extract_text_from_txt(file_obj) -> str:
    """
    Extract text from a TXT file.

    Args:
        file_obj: File-like object containing TXT data.

    Returns:
        Extracted text or error message.
    """
    try:
        # Reset file pointer to beginning
        file_obj.seek(0)
        text = file_obj.read().decode("utf-8")
        return text if text.strip() else "No text could be extracted from the TXT file."
    except UnicodeDecodeError:
        try:
            file_obj.seek(0)
            text = file_obj.read().decode("latin-1")
            return text if text.strip() else "No text could be extracted from the TXT file."
        except Exception as e:
            error_msg = f"Error extracting text from TXT: {str(e)}"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Error extracting text from TXT: {str(e)}"
        logger.error(error_msg)
        return error_msg


def extract_text(file_obj, filename: str) -> str:
    """
    Extract text from a file based on its extension.

    Args:
        file_obj: File-like object containing document data.
        filename: Name of the file (used to determine parser).

    Returns:
        Extracted text or error message.
    """
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext == "pdf":
        return extract_text_from_pdf(file_obj)
    elif ext == "docx":
        return extract_text_from_docx(file_obj)
    elif ext == "txt":
        return extract_text_from_txt(file_obj)
    else:
        return f"Unsupported file type: .{ext}. Supported types: PDF, DOCX, TXT"
