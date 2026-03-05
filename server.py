"""FastAPI backend for SmartSummarizer web UI."""

import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from summarizer.ai_summarizer import summarize, SummarizerError
from summarizer.pdf_reader import extract_text as extract_pdf, PDFReadError
from summarizer.web_scraper import fetch_page_text, WebScraperError
from summarizer.utils import setup_logging

logger = setup_logging()

app = FastAPI(title="SmartSummarizer API")

# Allow the frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/summarize/url")
async def summarize_url(url: str, style: str = "brief") -> dict:
    """Summarize a web page by URL."""
    try:
        logger.info("Web request — URL: %s, style: %s", url, style)
        content = fetch_page_text(url)
        summary = summarize(content, style=style)
        return {"summary": summary}
    except WebScraperError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except SummarizerError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/summarize/pdf")
async def summarize_pdf(
    file: UploadFile = File(...),
    style: str = Form("brief"),
    pages: str = Form(None),
) -> dict:
    """Summarize an uploaded PDF file."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files are accepted.")

    # Save upload to a temp file
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        logger.info("PDF request — file: %s, style: %s, pages: %s", file.filename, style, pages)

        # Parse optional page range
        start_page, end_page = None, None
        if pages:
            try:
                parts = pages.split("-")
                start_page, end_page = int(parts[0]), int(parts[1])
            except (ValueError, IndexError):
                raise HTTPException(
                    status_code=422,
                    detail="Invalid page range. Use format 'start-end', e.g. '1-5'.",
                )

        content = extract_pdf(tmp_path, start_page, end_page)
        summary = summarize(content, style=style)
        return {"summary": summary}

    except PDFReadError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except SummarizerError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        Path(tmp_path).unlink(missing_ok=True)