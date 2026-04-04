"""Document parsing services for PDF, DOCX, and TXT files."""

import logging
import re

import docx
import PyPDF2

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_obj) -> str:
    """
    Extract text from a PDF file with multiple fallback strategies.

    Args:
        file_obj: File-like object containing PDF data.

    Returns:
        Extracted text or error message.
    """
    try:
        # Ensure file pointer is at the beginning
        file_obj.seek(0)

        # Read file content to check if it's a valid PDF
        file_content = file_obj.read()

        if not file_content.startswith(b'%PDF'):
            logger.warning("File does not appear to be a valid PDF")
            return "Error: File is not a valid PDF document."

        # Check for PDF/A or other special formats
        if b'PDF/A' in file_content[:1000]:
            logger.info("PDF/A format detected, may have extraction limitations")

        # Reset pointer for reading
        file_obj.seek(0)

        # Try pypdf first (modern library)
        text = _try_extract_with_pypdf(file_obj)

        # If pypdf failed or returned empty, try PyPDF2
        if not text or text.startswith("Error") or text.startswith("No text"):
            file_obj.seek(0)
            text = _try_extract_with_pypdf2(file_obj)

        # If both libraries failed, try regex fallback
        if not text or text.startswith("Error") or text.startswith("No text"):
            file_obj.seek(0)
            text = _fallback_pdf_extraction(file_obj)

        # Clean up text
        if text:
            text = text.strip()

        if not text or text.startswith("Error") or text.startswith("No text"):
            return (
                "No text could be extracted from the PDF. "
                "This may be a scanned document (image-based PDF). "
                "Try using OCR software to extract text first."
            )

        logger.info(f"Successfully extracted {len(text)} characters from PDF")
        return text

    except Exception as e:
        error_msg = f"Error extracting text from PDF: {str(e)}"
        logger.error(error_msg)
        return error_msg


def _try_extract_with_pypdf(file_obj) -> str:
    """Try to extract text using pypdf library."""
    try:
        from pypdf import PdfReader

        pdf_reader = PdfReader(file_obj)

        # Check if PDF is encrypted
        if pdf_reader.is_encrypted:
            logger.warning("PDF is encrypted")
            return "Error: PDF is encrypted and cannot be processed."

        num_pages = len(pdf_reader.pages)
        logger.info(f"Processing PDF with {num_pages} pages using pypdf")

        text = ""
        for i, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as page_error:
                logger.warning(f"Page {i+1} failed: {page_error}")
                continue

        return text if text else "No text could be extracted."

    except ImportError:
        logger.warning("pypdf not available, falling back to PyPDF2")
        return ""
    except Exception as e:
        logger.warning(f"pypdf failed: {e}")
        return ""


def _try_extract_with_pypdf2(file_obj) -> str:
    """Try to extract text using PyPDF2 library."""
    try:
        pdf_reader = PyPDF2.PdfReader(file_obj)

        # Check if PDF is encrypted
        if pdf_reader.is_encrypted:
            logger.warning("PDF is encrypted")
            return "Error: PDF is encrypted and cannot be processed."

        num_pages = len(pdf_reader.pages)
        logger.info(f"Processing PDF with {num_pages} pages using PyPDF2")

        text = ""
        for i, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as page_error:
                logger.warning(f"Page {i+1} failed: {page_error}")
                continue

        return text if text else "No text could be extracted."

    except Exception as e:
        logger.warning(f"PyPDF2 failed: {e}")
        return ""


def _fallback_pdf_extraction(file_obj) -> str:
    """
    Fallback method for PDF text extraction.

    Args:
        file_obj: File-like object containing PDF data.

    Returns:
        Extracted text.
    """

    file_obj.seek(0)
    content = file_obj.read()

    # Try to extract text using regex patterns
    # This is a basic fallback and won't work for all PDFs
    text_pattern = rb'BT\s*(.*?)\s*ET'
    matches = re.findall(text_pattern, content, re.DOTALL)

    if matches:
        text_parts = []
        for match in matches:
            # Extract text between parentheses
            text_matches = re.findall(rb'\(([^)]*)\)', match)
            for tm in text_matches:
                try:
                    text_parts.append(tm.decode('utf-8', errors='ignore'))
                except Exception:
                    continue
        return '\n'.join(text_parts)

    return ""


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
        # Debug: Log the type of file_obj
        logger.info(f"TXT extract received: type={type(file_obj).__name__}")
        
        # Reset file pointer to beginning
        file_obj.seek(0)
        
        # Read the content
        raw_content = file_obj.read()
        
        # Debug: Log content info
        content_size = len(raw_content) if raw_content else 0
        logger.info(f"TXT content size: {content_size} bytes")
        
        # Handle different input types
        if isinstance(raw_content, str):
            # Already a string (Streamlit might return this)
            text = raw_content
            logger.info("Processing as string content")
        elif isinstance(raw_content, bytes):
            # Bytes object - try to decode
            try:
                text = raw_content.decode("utf-8")
                logger.info("Decoded as UTF-8")
            except UnicodeDecodeError:
                try:
                    text = raw_content.decode("latin-1")
                    logger.info("Decoded as Latin-1")
                except Exception as decode_error:
                    error_msg = f"Error decoding TXT file: {str(decode_error)}"
                    logger.error(error_msg)
                    return error_msg
        else:
            error_msg = (
                f"Error: Unexpected file type for TXT extraction: "
                f"{type(raw_content).__name__}"
            )
            logger.error(error_msg)
            return error_msg
        
        # Check if text is empty
        if not text or not text.strip():
            logger.warning("TXT file is empty or contains only whitespace")
            return "No text could be extracted from the TXT file."
        
        logger.info(
            f"Successfully extracted {len(text)} characters, "
            f"{len(text.split())} words from TXT"
        )
        return text
        
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
    
    # Read first few bytes to detect actual file type
    file_obj.seek(0)
    header = file_obj.read(8)
    file_obj.seek(0)  # Reset pointer
    
    # Check for PDF signature even if extension is .txt
    if header.startswith(b'%PDF'):
        logger.warning(
            f"File '{filename}' has .txt extension but contains PDF data"
        )
        return extract_text_from_pdf(file_obj)
    
    # Check for DOCX signature (PK zip)
    if header.startswith(b'PK'):
        logger.info(
            f"File '{filename}' appears to be a ZIP/DOCX format"
        )
        if ext == "txt":
            # User might have renamed DOCX as TXT
            logger.warning("Attempting DOCX extraction for .txt file")
            try:
                result = extract_text_from_docx(file_obj)
                if "Error" not in result:
                    return result
            except Exception:
                pass
            # If DOCX fails, try as TXT
            file_obj.seek(0)
    
    if ext == "pdf":
        return extract_text_from_pdf(file_obj)
    elif ext == "docx":
        return extract_text_from_docx(file_obj)
    elif ext == "txt":
        return extract_text_from_txt(file_obj)
    else:
        return (
            f"Unsupported file type: .{ext}. "
            f"Supported types: PDF, DOCX, TXT"
        )
