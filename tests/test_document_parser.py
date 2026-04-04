"""Tests for document parser module."""

import io
from unittest.mock import Mock, patch

from services.document_parser import (
    extract_text,
    extract_text_from_docx,
    extract_text_from_pdf,
    extract_text_from_txt,
)


class TestPDFExtraction:
    """Test PDF text extraction functionality."""

    def test_extract_text_from_pdf_success(self):
        """Test successful PDF text extraction."""
        import io

        mock_pdf_reader = Mock()
        mock_pdf_reader.is_encrypted = False
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "This is page one content."
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "This is page two content."
        mock_pdf_reader.pages = [mock_page1, mock_page2]

        # Create a mock file with PDF header
        mock_file = io.BytesIO(b'%PDF-1.4 mock content')

        with patch("services.document_parser.PyPDF2.PdfReader", return_value=mock_pdf_reader):
            result = extract_text_from_pdf(mock_file)

        assert "page one content" in result.lower()
        assert "page two content" in result.lower()

    def test_extract_text_from_pdf_empty(self):
        """Test PDF with no extractable text."""
        import io

        mock_pdf_reader = Mock()
        mock_pdf_reader.is_encrypted = False
        mock_page = Mock()
        mock_page.extract_text.return_value = None
        mock_pdf_reader.pages = [mock_page]

        mock_file = io.BytesIO(b'%PDF-1.4 empty content')

        with patch("services.document_parser.PyPDF2.PdfReader", return_value=mock_pdf_reader):
            result = extract_text_from_pdf(mock_file)

        assert "No text could be extracted" in result

    def test_extract_text_from_pdf_error(self):
        """Test PDF extraction error handling."""
        import io

        # Create a mock file that's not a valid PDF
        mock_file = io.BytesIO(b'NOT_A_PDF content')

        result = extract_text_from_pdf(mock_file)

        assert "not a valid PDF" in result


class TestDOCXExtraction:
    """Test DOCX text extraction functionality."""

    def test_extract_text_from_docx_success(self):
        """Test successful DOCX text extraction."""
        mock_doc = Mock()
        mock_para1 = Mock()
        mock_para1.text = "First paragraph content."
        mock_para2 = Mock()
        mock_para2.text = "Second paragraph content."
        mock_doc.paragraphs = [mock_para1, mock_para2]

        mock_file = Mock()

        with patch("services.document_parser.docx.Document", return_value=mock_doc):
            result = extract_text_from_docx(mock_file)

        assert "First paragraph content" in result
        assert "Second paragraph content" in result

    def test_extract_text_from_docx_empty(self):
        """Test DOCX with no text content."""
        mock_doc = Mock()
        mock_para = Mock()
        mock_para.text = ""
        mock_doc.paragraphs = [mock_para]

        mock_file = Mock()

        with patch("services.document_parser.docx.Document", return_value=mock_doc):
            result = extract_text_from_docx(mock_file)

        assert "No text could be extracted" in result

    def test_extract_text_from_docx_error(self):
        """Test DOCX extraction error handling."""
        mock_file = Mock()

        with patch("services.document_parser.docx.Document", side_effect=Exception("Corrupted DOCX")):
            result = extract_text_from_docx(mock_file)

        assert "Error extracting text from DOCX" in result
        assert "Corrupted DOCX" in result


class TestTXTExtraction:
    """Test TXT text extraction functionality."""

    def test_extract_text_from_txt_success(self):
        """Test successful TXT text extraction."""
        mock_file = io.BytesIO(b"This is plain text content.\nWith multiple lines.")

        result = extract_text_from_txt(mock_file)

        assert "plain text content" in result
        assert "multiple lines" in result

    def test_extract_text_from_txt_empty(self):
        """Test TXT file with no content."""
        mock_file = io.BytesIO(b"   \n\n   ")

        result = extract_text_from_txt(mock_file)

        assert "No text could be extracted" in result

    def test_extract_text_from_txt_encoding_fallback(self):
        """Test TXT extraction with encoding fallback."""
        # Create content that might fail UTF-8 decoding
        mock_file = io.BytesIO(b"Content with special chars: \xe9\xe8\xe0")

        result = extract_text_from_txt(mock_file)
        # Should succeed with latin-1 fallback
        assert "special chars" in result


class TestExtractTextRouter:
    """Test the unified extract_text router function."""

    def test_extract_text_pdf(self):
        """Test router routes to PDF extractor."""
        mock_file = Mock()

        with patch("services.document_parser.extract_text_from_pdf", return_value="PDF content"):
            result = extract_text(mock_file, "document.pdf")

        assert result == "PDF content"

    def test_extract_text_docx(self):
        """Test router routes to DOCX extractor."""
        mock_file = Mock()

        with patch("services.document_parser.extract_text_from_docx", return_value="DOCX content"):
            result = extract_text(mock_file, "report.docx")

        assert result == "DOCX content"

    def test_extract_text_txt(self):
        """Test router routes to TXT extractor."""
        mock_file = io.BytesIO(b"TXT content")

        result = extract_text(mock_file, "notes.txt")

        assert result == "TXT content"

    def test_extract_text_unsupported_extension(self):
        """Test router returns error for unsupported file type."""
        mock_file = Mock()

        result = extract_text(mock_file, "image.png")

        assert "Unsupported file type" in result
        assert ".png" in result


class TestErrorHandling:
    """Test general error handling scenarios."""

    def test_corrupted_pdf_file(self):
        """Test handling of corrupted PDF file."""
        mock_file = Mock()
        mock_file.read.side_effect = Exception("File corrupted")

        with patch("services.document_parser.PyPDF2.PdfReader", side_effect=Exception("File corrupted")):
            result = extract_text_from_pdf(mock_file)

        assert "Error" in result

    def test_none_file_object(self):
        """Test handling of None file object - function catches error and returns error string."""
        result = extract_text_from_pdf(None)
        # The function catches the error and returns an error string
        assert "Error extracting text from PDF" in result

    def test_large_text_file(self):
        """Test handling of large TXT files."""
        large_content = b"Line content.\n" * 10000
        mock_file = io.BytesIO(large_content)

        result = extract_text_from_txt(mock_file)

        assert len(result) > 0
        assert "Line content" in result

    def test_mixed_case_extension(self):
        """Test handling of mixed case file extensions."""
        mock_file = Mock()

        with patch("services.document_parser.extract_text_from_pdf", return_value="PDF content"):
            result = extract_text(mock_file, "DOCUMENT.PDF")

        assert result == "PDF content"
