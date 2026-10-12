"""Embedding generation service for research papers."""

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    """Load and cache the configured embedding model."""

    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": settings.embedding_device},
        encode_kwargs={
            "normalize_embeddings": settings.normalize_embeddings,
        },
    )


def embed_text(text: str) -> list[float]:
    """Generate an embedding for a single text."""

    if not text or not text.strip():
        raise ValueError("Cannot generate an embedding for empty text.")

    return get_embedding_model().embed_query(text)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of text chunks."""

    if not texts:
        return []

    if any(not text or not text.strip() for text in texts):
        raise ValueError("All texts must contain non-empty content.")

    return get_embedding_model().embed_documents(texts)


def get_embedding_dimension() -> int:
    """Return the embedding vector dimension."""

    return len(embed_text("Research paper embedding dimension check."))
