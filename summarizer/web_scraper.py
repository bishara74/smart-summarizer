"""Web content extraction using Selenium with headless Chrome."""

import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger("smartsummarizer")

# Default timeout in seconds for page loads
DEFAULT_TIMEOUT = 30


class WebScraperError(Exception):
    """Raised when web content cannot be fetched."""


def _create_driver(timeout: int = DEFAULT_TIMEOUT) -> webdriver.Chrome:
    """Create and configure a headless Chrome WebDriver instance.

    Args:
        timeout: Page load timeout in seconds.

    Returns:
        Configured Chrome WebDriver.

    Raises:
        WebScraperError: If the driver cannot be created.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1200x600")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(timeout)
        return driver
    except Exception as exc:
        raise WebScraperError(f"Failed to create Chrome driver: {exc}") from exc


def fetch_page_text(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Fetch and extract visible text from a web page.

    Args:
        url: The URL to scrape.
        timeout: Page load timeout in seconds.

    Returns:
        Visible text content of the page.

    Raises:
        WebScraperError: If the page cannot be loaded or parsed.
    """
    if not url.startswith(("http://", "https://")):
        raise WebScraperError(f"Invalid URL (must start with http/https): {url}")

    logger.info("Fetching URL: %s", url)
    driver = _create_driver(timeout)

    try:
        driver.get(url)
        driver.implicitly_wait(5)

        body = driver.find_element(By.TAG_NAME, "body")
        text = body.text

        if not text.strip():
            logger.warning("Page returned empty text — might be JS-rendered.")
            raise WebScraperError("No visible text found on the page.")

        logger.info("Extracted %d characters from %s", len(text), url)
        return text

    except TimeoutException:
        raise WebScraperError(
            f"Page load timed out after {timeout}s: {url}"
        )
    except WebScraperError:
        raise
    except WebDriverException as exc:
        raise WebScraperError(f"Browser error: {exc}") from exc
    except Exception as exc:
        raise WebScraperError(f"Unexpected error fetching {url}: {exc}") from exc
    finally:
        driver.quit()
        logger.debug("Browser closed.")