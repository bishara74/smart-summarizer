"""Unit tests for the PDF reader module."""

import pytest
from unittest.mock import patch, MagicMock
from summarizer.pdf_reader import extract_text, get_page_count, PDFReadError


class TestExtractText:
    """Tests for the extract_text function."""

    def test_file_not_found_raises_error(self, tmp_path):
        fake_path = str(tmp_path / "nonexistent.pdf")
        with pytest.raises(PDFReadError, match="File not found"):
            extract_text(fake_path)

    def test_non_pdf_extension_raises_error(self, tmp_path):
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("hello")
        with pytest.raises(PDFReadError, match="Not a PDF file"):
            extract_text(str(txt_file))

    @patch("summarizer.pdf_reader.fitz.open")
    def test_extracts_all_pages_by_default(self, mock_open):
        # Set up a fake 2-page document
        mock_page_1 = MagicMock()
        mock_page_1.get_text.return_value = "Page one content."
        mock_page_2 = MagicMock()
        mock_page_2.get_text.return_value = "Page two content."

        mock_doc = MagicMock()
        mock_doc.__len__ = lambda self: 2
        mock_doc.__getitem__ = lambda self, i: [mock_page_1, mock_page_2][i]
        mock_open.return_value = mock_doc

        # Create a real .pdf file so path checks pass
        import tempfile, os
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

        try:
            result = extract_text(path)
            assert "Page one content." in result
            assert "Page two content." in result
        finally:
            os.unlink(path)

    @patch("summarizer.pdf_reader.fitz.open")
    def test_extracts_specific_page_range(self, mock_open):
        pages = [MagicMock() for _ in range(5)]
        for i, page in enumerate(pages):
            page.get_text.return_value = f"Content of page {i + 1}."

        mock_doc = MagicMock()
        mock_doc.__len__ = lambda self: 5
        mock_doc.__getitem__ = lambda self, i: pages[i]
        mock_open.return_value = mock_doc

        import tempfile, os
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

        try:
            result = extract_text(path, start_page=2, end_page=4)
            assert "Content of page 2." in result
            assert "Content of page 3." in result
            assert "Content of page 4." in result
            assert "Content of page 1." not in result
            assert "Content of page 5." not in result
        finally:
            os.unlink(path)

    @patch("summarizer.pdf_reader.fitz.open")
    def test_invalid_page_range_raises_error(self, mock_open):
        mock_doc = MagicMock()
        mock_doc.__len__ = lambda self: 3
        mock_open.return_value = mock_doc

        import tempfile, os
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

        try:
            with pytest.raises(PDFReadError, match="Invalid page range"):
                extract_text(path, start_page=1, end_page=10)
        finally:
            os.unlink(path)

    @patch("summarizer.pdf_reader.fitz.open")
    def test_empty_pages_raises_error(self, mock_open):
        mock_page = MagicMock()
        mock_page.get_text.return_value = "   "

        mock_doc = MagicMock()
        mock_doc.__len__ = lambda self: 1
        mock_doc.__getitem__ = lambda self, i: mock_page
        mock_open.return_value = mock_doc

        import tempfile, os
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

        try:
            with pytest.raises(PDFReadError, match="No extractable text"):
                extract_text(path)
        finally:
            os.unlink(path)


class TestGetPageCount:
    """Tests for the get_page_count function."""

    def test_file_not_found_raises_error(self, tmp_path):
        with pytest.raises(PDFReadError, match="File not found"):
            get_page_count(str(tmp_path / "nope.pdf"))

    @patch("summarizer.pdf_reader.fitz.open")
    def test_returns_correct_count(self, mock_open):
        mock_doc = MagicMock()
        mock_doc.__len__ = lambda self: 42
        mock_open.return_value = mock_doc

        import tempfile, os
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

        try:
            assert get_page_count(path) == 42
        finally:
            os.unlink(path)
