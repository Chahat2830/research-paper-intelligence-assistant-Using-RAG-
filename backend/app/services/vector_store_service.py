"""ChromaDB vector storage service for research papers."""

from functools import lru_cache
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.core.config import settings
from app.services.embedding_service import get_embedding_model


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    """Initialize and cache the persistent ChromaDB collection."""

    return Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=get_embedding_model(),
        persist_directory=str(settings.chroma_path),
        collection_metadata={"hnsw:space": "cosine"},
    )


def add_chunks(chunks: list[dict[str, Any]]) -> list[str]:
    """Store text chunks and their metadata in ChromaDB."""

    if not chunks:
        return []

    documents: list[Document] = []
    ids: list[str] = []

    for chunk in chunks:
        text = chunk.get("text")

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Every chunk must contain non-empty text.")

        chunk_id = chunk.get("chunk_id")

        if not isinstance(chunk_id, str) or not chunk_id.strip():
            raise ValueError("Every chunk must have a valid chunk_id.")

        metadata = {
            key: value
            for key, value in chunk.items()
            if key not in {"text", "chunk_id"}
            and value is not None
            and isinstance(value, (str, int, float, bool))
        }

        documents.append(
            Document(
                page_content=text,
                metadata=metadata,
            )
        )
        ids.append(chunk_id)

    if len(ids) != len(set(ids)):
        raise ValueError("Chunk IDs must be unique within a batch.")

    get_vector_store().add_documents(
        documents=documents,
        ids=ids,
    )

    return ids


def search_chunks(
    query: str,
    k: int | None = None,
    paper_ids: list[str] | None = None,
) -> list[Document]:
    """Search for relevant chunks, optionally filtering by paper IDs."""

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    limit = k if k is not None else settings.top_k

    if limit < 1:
        raise ValueError("k must be greater than zero.")

    search_kwargs: dict[str, Any] = {}

    if paper_ids:
        valid_ids = [paper_id.strip() for paper_id in paper_ids if paper_id.strip()]

        if not valid_ids:
            return []

        if len(valid_ids) == 1:
            search_kwargs["filter"] = {"paper_id": valid_ids[0]}
        else:
            search_kwargs["filter"] = {
                "$or": [{"paper_id": paper_id} for paper_id in valid_ids]
            }

    return get_vector_store().similarity_search(
        query=query,
        k=limit,
        **search_kwargs,
    )


def delete_paper_chunks(paper_id: str) -> int:
    """Delete all stored chunks associated with a paper."""

    if not paper_id or not paper_id.strip():
        raise ValueError("paper_id cannot be empty.")

    vector_store = get_vector_store()
    collection = vector_store._collection

    existing = collection.get(
        where={"paper_id": paper_id.strip()},
        include=[],
    )

    chunk_ids = existing.get("ids", [])

    if not chunk_ids:
        return 0

    vector_store.delete(ids=chunk_ids)

    return len(chunk_ids)


def get_stored_chunk_count(paper_id: str | None = None) -> int:
    """Return the number of stored chunks, optionally for one paper."""

    collection = get_vector_store()._collection

    if paper_id is None:
        return collection.count()

    if not paper_id.strip():
        raise ValueError("paper_id cannot be empty.")

    result = collection.get(
        where={"paper_id": paper_id.strip()},
        include=[],
    )

    return len(result.get("ids", []))
