"""PDF extraction and metadata services."""

from pathlib import Path
from typing import Any

import fitz


class PDFProcessingError(Exception):
    """Raised when a PDF cannot be processed."""


def extract_pdf_text(pdf_path: str | Path) -> str:
    """Extract text from every page of a PDF."""

    path = Path(pdf_path)

    if not path.is_file():
        raise PDFProcessingError(f"PDF file not found: {path.name}")

    if path.suffix.lower() != ".pdf":
        raise PDFProcessingError("The supplied file must be a PDF.")

    extracted_pages: list[str] = []

    try:
        with fitz.open(path) as document:
            if document.is_encrypted:
                raise PDFProcessingError("The PDF is password-protected or encrypted.")

            for page_number, page in enumerate(document, start=1):
                page_text = page.get_text("text").strip()

                if page_text:
                    extracted_pages.append(f"[Page {page_number}]\n{page_text}")

    except PDFProcessingError:
        raise
    except (fitz.FileDataError, RuntimeError, OSError) as exc:
        raise PDFProcessingError(
            "Unable to read the PDF. The file may be corrupted or invalid."
        ) from exc

    full_text = "\n\n".join(extracted_pages).strip()

    if not full_text:
        raise PDFProcessingError(
            "No extractable text was found. The PDF may contain scanned "
            "images and require OCR."
        )

    return full_text


def extract_pdf_metadata(pdf_path: str | Path) -> dict[str, Any]:
    """Extract document metadata and page count from a PDF."""

    path = Path(pdf_path)

    if not path.is_file():
        raise PDFProcessingError(f"PDF file not found: {path.name}")

    if path.suffix.lower() != ".pdf":
        raise PDFProcessingError("The supplied file must be a PDF.")

    try:
        with fitz.open(path) as document:
            if document.is_encrypted:
                raise PDFProcessingError("The PDF is password-protected or encrypted.")

            metadata = document.metadata or {}

            return {
                "filename": path.name,
                "title": metadata.get("title") or None,
                "author": metadata.get("author") or None,
                "subject": metadata.get("subject") or None,
                "page_count": len(document),
                "file_size_bytes": path.stat().st_size,
            }

    except PDFProcessingError:
        raise
    except (fitz.FileDataError, RuntimeError, OSError) as exc:
        raise PDFProcessingError("Unable to extract metadata from the PDF.") from exc


def extract_pdf_pages(pdf_path: str | Path) -> list[dict[str, Any]]:
    """Extract text page by page while preserving page numbers."""

    path = Path(pdf_path)

    if not path.is_file():
        raise PDFProcessingError(f"PDF file not found: {path.name}")

    if path.suffix.lower() != ".pdf":
        raise PDFProcessingError("The supplied file must be a PDF.")

    pages: list[dict[str, Any]] = []

    try:
        with fitz.open(path) as document:
            if document.is_encrypted:
                raise PDFProcessingError("The PDF is password-protected or encrypted.")

            for page_number, page in enumerate(document, start=1):
                pages.append(
                    {
                        "page_number": page_number,
                        "text": page.get_text("text").strip(),
                    }
                )

    except PDFProcessingError:
        raise
    except (fitz.FileDataError, RuntimeError, OSError) as exc:
        raise PDFProcessingError("Unable to extract pages from the PDF.") from exc

    return pages
