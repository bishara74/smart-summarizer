# SmartSummarizer

A multi-source content summarizer that extracts text from **web pages** and **PDF files**, then generates AI-powered summaries using **Groq** (Llama 3.3 70B). Available as both a CLI tool and a web app.

## Features

- **Web scraping** — extracts visible text from any URL using headless Chrome via Selenium
- **PDF extraction** — pulls text from PDF files with optional page range selection
- **AI summarization** — generates summaries in three styles: brief, detailed, or snarky
- **CLI interface** — full-featured command-line tool with argparse
- **Web UI** — React frontend with drag-and-drop PDF upload, backed by a FastAPI server
- **Tested** — 24 unit tests with full mocking of external services

## Demo

```bash
# Summarize a web page
python main.py --url "https://en.wikipedia.org/wiki/Python_(programming_language)" --style snarky

# Summarize a PDF
python main.py --pdf "./report.pdf" --style detailed

# Summarize specific pages
python main.py --pdf "./book.pdf" --pages 1-5 --style brief
```

## Architecture

```
smart-summarizer/
├── main.py                  # CLI entry point (argparse)
├── server.py                # FastAPI backend for web UI
├── frontend.html            # React frontend (single-file, CDN-loaded)
├── summarizer/
│   ├── web_scraper.py       # Selenium headless Chrome scraper
│   ├── pdf_reader.py        # PyMuPDF text extraction
│   ├── ai_summarizer.py     # Groq API integration
│   └── utils.py             # Logging setup, text truncation
├── tests/
│   ├── test_web_scraper.py  # Scraper tests (mocked Selenium)
│   ├── test_pdf_reader.py   # PDF reader tests (mocked PyMuPDF)
│   └── test_summarizer.py   # Summarizer tests (mocked Groq)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Setup

### Prerequisites

- Python 3.11+
- Google Chrome (for web scraping)
- A free [Groq API key](https://console.groq.com/keys)

### Installation

```bash
git clone https://github.com/yourusername/smart-summarizer.git
cd smart-summarizer
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate
pip install -r requirements.txt
cp .env.example .env             # Add your Groq API key
```

### Running the CLI

```bash
python main.py --url "https://example.com" --style brief
python main.py --pdf "./document.pdf" --pages 1-3 --style detailed
python main.py --help
```

### Running the Web UI

```bash
# Start the backend
python -m uvicorn server:app --reload --port 8000

# Open frontend.html in your browser
```

### Running Tests

```bash
python -m pytest tests/ -v
```

### Docker

```bash
docker compose up --build
# Server runs at http://localhost:8000
```

## Tech Stack

- **Python 3.11+** — core language
- **Selenium** — headless Chrome web scraping
- **PyMuPDF (fitz)** — PDF text extraction
- **Groq API** — LLM inference (Llama 3.3 70B)
- **FastAPI + Uvicorn** — web API backend
- **React** — frontend UI (CDN-loaded, no build step)
- **pytest** — unit testing with mocked external services
- **Docker** — containerized deployment

## License

MIT
