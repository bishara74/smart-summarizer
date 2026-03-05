"""Unit tests for the web scraper module."""

import pytest
from unittest.mock import patch, MagicMock
from summarizer.web_scraper import fetch_page_text, WebScraperError


class TestFetchPageText:
    """Tests for the fetch_page_text function."""

    def test_invalid_url_raises_error(self):
        with pytest.raises(WebScraperError, match="Invalid URL"):
            fetch_page_text("not-a-url")

    def test_missing_scheme_raises_error(self):
        with pytest.raises(WebScraperError, match="Invalid URL"):
            fetch_page_text("www.example.com")

    @patch("summarizer.web_scraper._create_driver")
    def test_successful_scrape(self, mock_create_driver):
        mock_body = MagicMock()
        mock_body.text = "Hello, this is page content."

        mock_driver = MagicMock()
        mock_driver.find_element.return_value = mock_body
        mock_create_driver.return_value = mock_driver

        result = fetch_page_text("https://example.com")

        assert result == "Hello, this is page content."
        mock_driver.get.assert_called_once_with("https://example.com")
        mock_driver.quit.assert_called_once()

    @patch("summarizer.web_scraper._create_driver")
    def test_empty_page_raises_error(self, mock_create_driver):
        mock_body = MagicMock()
        mock_body.text = "   "

        mock_driver = MagicMock()
        mock_driver.find_element.return_value = mock_body
        mock_create_driver.return_value = mock_driver

        with pytest.raises(WebScraperError, match="No visible text"):
            fetch_page_text("https://example.com")

        mock_driver.quit.assert_called_once()

    @patch("summarizer.web_scraper._create_driver")
    def test_timeout_raises_error(self, mock_create_driver):
        from selenium.common.exceptions import TimeoutException

        mock_driver = MagicMock()
        mock_driver.get.side_effect = TimeoutException()
        mock_create_driver.return_value = mock_driver

        with pytest.raises(WebScraperError, match="timed out"):
            fetch_page_text("https://example.com")

        mock_driver.quit.assert_called_once()

    @patch("summarizer.web_scraper._create_driver")
    def test_driver_always_quits_on_error(self, mock_create_driver):
        mock_driver = MagicMock()
        mock_driver.get.side_effect = Exception("something broke")
        mock_create_driver.return_value = mock_driver

        with pytest.raises(WebScraperError):
            fetch_page_text("https://example.com")

        mock_driver.quit.assert_called_once()
