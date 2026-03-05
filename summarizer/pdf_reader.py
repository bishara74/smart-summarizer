"""PDF text extraction using PyMuPDF."""

import logging
from pathlib import Path

import fitz  # PyMuPDF

logger = logging.getLogger("smartsummarizer")


class PDFReadError(Exception):
    """Raised when a PDF cannot be opened or read."""


def extract_text(
    pdf_path: str,
    start_page: int | None = None,
    end_page: int | None = None,
) -> str:
    """Extract text from a PDF file, optionally limiting to a page range.

    Args:
        pdf_path: Path to the PDF file.
        start_page: First page to extract (1-indexed, inclusive). None = first page.
        end_page: Last page to extract (1-indexed, inclusive). None = last page.

    Returns:
        Extracted text as a single string.

    Raises:
        PDFReadError: If the file doesn't exist, isn't a PDF, or can't be read.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise PDFReadError(f"File not found: {pdf_path}")
    if path.suffix.lower() != ".pdf":
        raise PDFReadError(f"Not a PDF file: {pdf_path}")

    try:
        doc = fitz.open(str(path))
    except Exception as exc:
        raise PDFReadError(f"Failed to open PDF: {exc}") from exc

    total_pages = len(doc)
    logger.info("Opened '%s' — %d pages.", path.name, total_pages)

    # Convert 1-indexed user input to 0-indexed PyMuPDF pages
    first = (start_page - 1) if start_page else 0
    last = (end_page - 1) if end_page else total_pages - 1

    # Validate range
    if first < 0 or last >= total_pages or first > last:
        doc.close()
        raise PDFReadError(
            f"Invalid page range {start_page}-{end_page} "
            f"for a {total_pages}-page document."
        )

    logger.info("Extracting pages %d–%d.", first + 1, last + 1)

    pages: list[str] = []
    for page_num in range(first, last + 1):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            pages.append(text)
        else:
            logger.debug("Page %d is empty or image-only, skipping.", page_num + 1)

    doc.close()

    if not pages:
        raise PDFReadError("No extractable text found in the given page range.")

    result = "\n".join(pages)
    logger.info("Extracted %d characters from %d pages.", len(result), len(pages))
    return result


def get_page_count(pdf_path: str) -> int:
    """Return the total number of pages in a PDF.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Total page count.

    Raises:
        PDFReadError: If the file can't be opened.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise PDFReadError(f"File not found: {pdf_path}")

    try:
        doc = fitz.open(str(path))
        count = len(doc)
        doc.close()
        return count
    except Exception as exc:
        raise PDFReadError(f"Failed to open PDF: {exc}") from exc



