"""Retrieval service for research-paper question answering."""

from typing import Any

from langchain_core.documents import Document

from app.core.config import settings
from app.services.vector_store_service import search_chunks


def retrieve_relevant_chunks(
    question: str,
    paper_ids: list[str] | None = None,
    top_k: int | None = None,
) -> list[Document]:
    """Retrieve the most relevant chunks for a research question."""

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    limit = top_k if top_k is not None else settings.top_k

    if limit < 1:
        raise ValueError("top_k must be greater than zero.")

    return search_chunks(
        query=question.strip(),
        k=limit,
        paper_ids=paper_ids,
    )


def format_retrieved_context(
    documents: list[Document],
) -> str:
    """Format retrieved documents as labeled context for the LLM."""

    if not documents:
        return "No relevant research passages were found."

    sections: list[str] = []

    for index, document in enumerate(documents, start=1):
        metadata = document.metadata or {}

        filename = metadata.get("filename", "Unknown document")
        paper_id = metadata.get("paper_id", "Unknown paper")
        page_number = metadata.get("page_number", "Unknown")
        chunk_id = metadata.get("chunk_id", document.id or f"chunk-{index}")

        sections.append(
            f"[Source {index}]\n"
            f"Paper ID: {paper_id}\n"
            f"Filename: {filename}\n"
            f"Page: {page_number}\n"
            f"Chunk ID: {chunk_id}\n"
            f"Content:\n{document.page_content.strip()}"
        )

    return "\n\n---\n\n".join(sections)


def build_source_references(
    documents: list[Document],
) -> list[dict[str, Any]]:
    """Build source metadata for API responses."""

    sources: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for document in documents:
        metadata = document.metadata or {}

        paper_id = str(metadata.get("paper_id", ""))
        chunk_id = str(metadata.get("chunk_id", document.id or ""))

        # Avoid returning the same source chunk multiple times.
        source_key = (paper_id, chunk_id)

        if source_key in seen:
            continue

        seen.add(source_key)

        page_number = metadata.get("page_number")

        sources.append(
            {
                "paper_id": paper_id,
                "filename": metadata.get(
                    "filename",
                    "Unknown document",
                ),
                "page_number": page_number,
                "chunk_id": chunk_id or None,
                "excerpt": document.page_content[:500].strip(),
            }
        )

    return sources


def retrieve_context(
    question: str,
    paper_ids: list[str] | None = None,
    top_k: int | None = None,
) -> dict[str, Any]:
    """Retrieve passages and return formatted context and source references."""

    documents = retrieve_relevant_chunks(
        question=question,
        paper_ids=paper_ids,
        top_k=top_k,
    )

    return {
        "context": format_retrieved_context(documents),
        "sources": build_source_references(documents),
        "retrieved_count": len(documents),
    }
