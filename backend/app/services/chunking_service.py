"""Text chunking service for research papers."""

from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


def create_text_splitter() -> RecursiveCharacterTextSplitter:
    """Create a text splitter using application settings."""

    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            "; ",
            ", ",
            " ",
            "",
        ],
        length_function=len,
        keep_separator=True,
        strip_whitespace=True,
    )


def chunk_text(text: str) -> list[str]:
    """Split plain text into overlapping chunks."""

    if not text or not text.strip():
        return []

    splitter = create_text_splitter()
    chunks = splitter.split_text(text)

    return [chunk for chunk in chunks if chunk.strip()]


def chunk_pages(
    pages: list[dict[str, Any]],
    paper_id: str,
    filename: str,
) -> list[dict[str, Any]]:
    """
    Split page-level PDF text into chunks while preserving metadata.

    Expected page format:
        [
            {"page_number": 1, "text": "..."},
            {"page_number": 2, "text": "..."},
        ]
    """

    if not paper_id.strip():
        raise ValueError("paper_id cannot be empty.")

    if not filename.strip():
        raise ValueError("filename cannot be empty.")

    splitter = create_text_splitter()
    chunk_documents: list[dict[str, Any]] = []

    for page in pages:
        page_number = page.get("page_number")
        page_text = page.get("text", "")

        if not isinstance(page_number, int) or page_number < 1:
            raise ValueError("Every page must have a positive integer page_number.")

        if not isinstance(page_text, str) or not page_text.strip():
            continue

        page_chunks = splitter.split_text(page_text)

        for chunk_index, chunk in enumerate(page_chunks):
            if not chunk.strip():
                continue

            chunk_documents.append(
                {
                    "chunk_id": (f"{paper_id}_page_{page_number}_chunk_{chunk_index}"),
                    "paper_id": paper_id,
                    "filename": filename,
                    "page_number": page_number,
                    "chunk_index": chunk_index,
                    "text": chunk,
                }
            )

    return chunk_documents
