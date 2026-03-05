"""AI-powered text summarization using Groq."""

import logging
import os

from groq import Groq
from dotenv import load_dotenv

from summarizer.utils import truncate_text

logger = logging.getLogger("smartsummarizer")

# Summary style prompts
STYLE_PROMPTS: dict[str, str] = {
    "brief": (
        "You are a concise summarizer. Provide a short, clear summary "
        "in 3-5 sentences. Focus only on the key points."
    ),
    "detailed": (
        "You are a thorough summarizer. Provide a comprehensive summary "
        "that covers all major points, arguments, and conclusions. "
        "Use paragraphs to organize different topics."
    ),
    "snarky": (
        "You are a witty, sarcastic summarizer. Provide an accurate summary "
        "but deliver it with humor and a bit of attitude. "
        "Keep it informative despite the tone."
    ),
}

DEFAULT_STYLE = "brief"
DEFAULT_MODEL = "llama-3.3-70b-versatile"


class SummarizerError(Exception):
    """Raised when summarization fails."""


def _create_client() -> Groq:
    """Load API key and return a configured Groq client.

    Returns:
        A configured Groq client instance.

    Raises:
        SummarizerError: If the API key is missing.
    """
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise SummarizerError(
            "GROQ_API_KEY not found. "
            "Add it to your .env file or set it as an environment variable."
        )

    return Groq(api_key=api_key)


def summarize(text: str, style: str = DEFAULT_STYLE) -> str:
    """Summarize the given text using Groq.

    Args:
        text: The content to summarize.
        style: Summary style — 'brief', 'detailed', or 'snarky'.

    Returns:
        The generated summary.

    Raises:
        SummarizerError: If the API call fails or returns empty.
    """
    if not text.strip():
        raise SummarizerError("Cannot summarize empty text.")

    if style not in STYLE_PROMPTS:
        logger.warning(
            "Unknown style '%s', falling back to '%s'.", style, DEFAULT_STYLE
        )
        style = DEFAULT_STYLE

    # Truncate to avoid hitting token limits
    text = truncate_text(text)

    model_name = os.getenv("GROQ_MODEL", DEFAULT_MODEL)
    logger.info("Using Groq model: %s", model_name)

    client = _create_client()

    system_prompt = STYLE_PROMPTS[style]
    user_prompt = f"Summarize the following content:\n\n{text}"

    logger.info("Sending %d characters to Groq (style: %s).", len(text), style)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        result = response.choices[0].message.content
        if not result:
            raise SummarizerError("Groq returned an empty response.")

        logger.info("Received summary (%d characters).", len(result))
        return result

    except SummarizerError:
        raise
    except Exception as exc:
        raise SummarizerError(f"Groq API error: {exc}") from exc


def get_available_styles() -> list[str]:
    """Return the list of supported summary styles.

    Returns:
        List of style names.
    """
    return list(STYLE_PROMPTS.keys())