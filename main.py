"""SmartSummarizer — CLI entry point."""

import argparse
import sys

from summarizer.ai_summarizer import summarize, get_available_styles, SummarizerError
from summarizer.pdf_reader import extract_text as extract_pdf, PDFReadError
from summarizer.web_scraper import fetch_page_text, WebScraperError
from summarizer.utils import setup_logging


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to sys.argv).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="smartsummarizer",
        description="Summarize content from web pages or PDF files using a local LLM.",
    )

    # Source — must provide exactly one
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--url",
        type=str,
        help="URL of a web page to summarize.",
    )
    source.add_argument(
        "--pdf",
        type=str,
        help="Path to a PDF file to summarize.",
    )

    # PDF page range
    parser.add_argument(
        "--pages",
        type=str,
        default=None,
        help="Page range for PDF extraction, e.g. '1-3' (1-indexed, inclusive).",
    )

    # Summary style
    parser.add_argument(
        "--style",
        type=str,
        choices=get_available_styles(),
        default="brief",
        help="Summary style (default: brief).",
    )

    # Verbosity
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging.",
    )

    return parser.parse_args(argv)


def _parse_page_range(pages: str) -> tuple[int, int]:
    """Parse a 'start-end' page range string.

    Args:
        pages: Page range string like '1-3' or '5-10'.

    Returns:
        Tuple of (start_page, end_page).

    Raises:
        ValueError: If the format is invalid.
    """
    try:
        parts = pages.split("-")
        if len(parts) != 2:
            raise ValueError
        start, end = int(parts[0]), int(parts[1])
        if start < 1 or end < start:
            raise ValueError
        return start, end
    except ValueError:
        raise ValueError(
            f"Invalid page range '{pages}'. Use format 'start-end', e.g. '1-3'."
        )


def main(argv: list[str] | None = None) -> None:
    """Run the SmartSummarizer CLI.

    Args:
        argv: Argument list (defaults to sys.argv).
    """
    args = parse_args(argv)
    logger = setup_logging(verbose=args.verbose)

    # --- Step 1: Extract content ---
    try:
        if args.url:
            logger.info("Source: web page — %s", args.url)
            content = fetch_page_text(args.url)

        elif args.pdf:
            logger.info("Source: PDF — %s", args.pdf)
            start_page, end_page = None, None
            if args.pages:
                start_page, end_page = _parse_page_range(args.pages)
            content = extract_pdf(args.pdf, start_page, end_page)

    except (WebScraperError, PDFReadError) as exc:
        logger.error("Failed to extract content: %s", exc)
        sys.exit(1)
    except ValueError as exc:
        logger.error(str(exc))
        sys.exit(1)

    # --- Step 2: Summarize ---
    try:
        logger.info("Summarizing with style '%s'...", args.style)
        summary = summarize(content, style=args.style)
    except SummarizerError as exc:
        logger.error("Summarization failed: %s", exc)
        sys.exit(1)

    # --- Step 3: Output ---
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(summary)
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

