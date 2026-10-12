"""API endpoints for literature review generation."""

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.services.literature_review_service import (
    LiteratureReviewResult,
    LiteratureReviewServiceError,
    generate_literature_review,
)
from app.services.retrieval_service import retrieve_relevant_chunks

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/literature-review", tags=["Literature Review"])


class LiteratureReviewRequest(BaseModel):
    """Request body for generating a literature review."""

    research_topic: str = Field(..., min_length=1, max_length=1000)
    paper_ids: list[str] = Field(..., min_length=2, max_length=10)

    @field_validator("research_topic")
    @classmethod
    def topic_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Research topic cannot be empty.")
        return value.strip()

    @field_validator("paper_ids")
    @classmethod
    def paper_ids_must_be_unique_and_nonempty(
        cls, values: list[str]
    ) -> list[str]:
        cleaned = [value.strip() for value in values]
        if any(not value for value in cleaned):
            raise ValueError("Paper IDs cannot be empty.")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("Duplicate paper IDs are not allowed.")
        return cleaned


class LiteratureReviewResponse(BaseModel):
    """Response containing the generated literature review."""

    success: bool = True
    review: LiteratureReviewResult


def _retrieve_paper_text(paper_id: str, topic: str, top_k: int = 8) -> dict[str, str]:
    """Retrieve indexed chunks for a single selected paper."""
    query = (
        f"Research topic: {topic}. Find relevant background, methods, "
        "results, conclusions, limitations, and future research directions."
    )
    documents = retrieve_relevant_chunks(
        question=query,
        paper_ids=[paper_id],
        top_k=top_k,
    )
    matching = [
        doc for doc in documents
        if str((doc.metadata or {}).get("paper_id", "")) == paper_id
    ]
    if not matching:
        raise ValueError(
            f"No indexed text was found for paper ID '{paper_id}'. "
            "Upload the PDF again or select a valid uploaded paper."
        )

    metadata = matching[0].metadata or {}
    filename = str(metadata.get("filename") or "Uploaded research paper")
    text = "\n\n".join(
        doc.page_content.strip()
        for doc in matching
        if doc.page_content and doc.page_content.strip()
    )
    if not text:
        raise ValueError(f"No readable text was retrieved for '{filename}'.")

    return {"paper_id": paper_id, "filename": filename, "text": text[:18000]}


@router.post(
    "/",
    response_model=LiteratureReviewResponse,
    status_code=status.HTTP_200_OK,
)
async def create_literature_review(
    request: LiteratureReviewRequest,
) -> LiteratureReviewResponse:
    """Generate a structured literature review from indexed papers."""
    try:
        papers = [
            _retrieve_paper_text(paper_id, request.research_topic)
            for paper_id in request.paper_ids
        ]
        review = generate_literature_review(
            research_topic=request.research_topic,
            papers=papers,
        )
        return LiteratureReviewResponse(success=True, review=review)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except LiteratureReviewServiceError as exc:
        logger.warning("Literature review generation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected literature review error.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the literature review.",
        ) from exc
