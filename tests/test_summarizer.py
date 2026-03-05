"""Unit tests for the AI summarizer module."""

import pytest
from unittest.mock import patch, MagicMock
from summarizer.ai_summarizer import (
    summarize,
    get_available_styles,
    SummarizerError,
)


class TestSummarize:
    """Tests for the summarize function."""

    def test_empty_text_raises_error(self):
        with pytest.raises(SummarizerError, match="Cannot summarize empty text"):
            summarize("")

    def test_whitespace_only_raises_error(self):
        with pytest.raises(SummarizerError, match="Cannot summarize empty text"):
            summarize("   \n\t  ")

    @patch("summarizer.ai_summarizer._create_client")
    def test_successful_summarization(self, mock_create_client):
        mock_message = MagicMock()
        mock_message.content = "This is a summary."

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_create_client.return_value = mock_client

        result = summarize("Some long text to summarize.", "brief")

        assert result == "This is a summary."
        mock_client.chat.completions.create.assert_called_once()

    @patch("summarizer.ai_summarizer._create_client")
    def test_unknown_style_falls_back_to_default(self, mock_create_client):
        mock_message = MagicMock()
        mock_message.content = "A summary."

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_create_client.return_value = mock_client

        result = summarize("Some text.", "nonexistent_style")

        assert result == "A summary."
        call_kwargs = mock_client.chat.completions.create.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages")
        assert "concise" in messages[0]["content"].lower()

    @patch("summarizer.ai_summarizer._create_client")
    def test_empty_response_raises_error(self, mock_create_client):
        mock_message = MagicMock()
        mock_message.content = ""

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_create_client.return_value = mock_client

        with pytest.raises(SummarizerError, match="empty response"):
            summarize("Some text.")

    @patch("summarizer.ai_summarizer._create_client")
    def test_api_error_raises_summarizer_error(self, mock_create_client):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API down")
        mock_create_client.return_value = mock_client

        with pytest.raises(SummarizerError, match="Groq API error"):
            summarize("Some text.")

    @patch("summarizer.ai_summarizer._create_client")
    def test_all_styles_send_correct_prompts(self, mock_create_client):
        mock_message = MagicMock()
        mock_message.content = "Summary."

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_create_client.return_value = mock_client

        style_keywords = {
            "brief": "concise",
            "detailed": "thorough",
            "snarky": "witty",
        }

        for style, keyword in style_keywords.items():
            summarize("Test text.", style)
            call_kwargs = mock_client.chat.completions.create.call_args
            messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages")
            assert keyword in messages[0]["content"].lower()


class TestGetAvailableStyles:
    """Tests for the get_available_styles function."""

    def test_returns_expected_styles(self):
        styles = get_available_styles()
        assert "brief" in styles
        assert "detailed" in styles
        assert "snarky" in styles

    def test_returns_list(self):
        assert isinstance(get_available_styles(), list)