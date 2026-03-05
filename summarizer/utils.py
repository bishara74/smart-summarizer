"""Logging setup and shared utilities."""

import logging
import sys


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure and return the application-wide logger.

    Args:
        verbose: If True, set level to DEBUG; otherwise INFO.

    Returns:
        Configured root logger for the application.
    """
    level = logging.DEBUG if verbose else logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    logger = logging.getLogger("smartsummarizer")
    logger.setLevel(level)

    # Avoid duplicate handlers on repeated calls
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


def truncate_text(text: str, max_chars: int = 30_000) -> str:
    """Truncate text to stay within token-friendly limits.

    Args:
        text: The input text to truncate.
        max_chars: Maximum character count (rough proxy for token limits).

    Returns:
        The original or truncated text.
    """
    if len(text) <= max_chars:
        return text

    logger = logging.getLogger("smartsummarizer")
    logger.warning(
        "Text truncated from %d to %d characters.", len(text), max_chars
    )
    return text[:max_chars]