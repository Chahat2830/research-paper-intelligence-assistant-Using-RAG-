"""API endpoints for comparing uploaded research papers."""

import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.comparison import ComparisonRequest, ComparisonResponse
from app.services.comparison_service import (
    ComparisonServiceError,
    compare_paper_texts,
)
from app.services.retrieval_service import retrieve_relevant_chunks

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/comparison", tags=["Paper Comparison"])


def _paper_text(paper_id: str, query: str, top_k: int = 8) -> dict[str, str]:
    """Retrieve and combine indexed chunks for one uploaded paper."""
    documents = retrieve_relevant_chunks(
        question=query,
        paper_ids=[paper_id],
        top_k=top_k,
    )

    # Defensively keep only chunks whose metadata identifies this paper.
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
    response_model=ComparisonResponse,
    status_code=status.HTTP_200_OK,
)
async def compare_research_papers(
    request: ComparisonRequest,
) -> ComparisonResponse:
    """Compare two to ten papers already indexed in the vector store."""
    try:
        aspects = request.comparison_aspects or [
            "research_objectives",
            "methodology",
            "datasets",
            "key_findings",
            "limitations",
        ]
        query = (
            "Find the paper's research objectives, methodology, datasets, "
            "key findings, strengths, limitations, and research gaps. "
            "Focus on: " + ", ".join(aspects)
        )

        papers = [
            _paper_text(paper_id.strip(), query)
            for paper_id in request.paper_ids
        ]
        return compare_paper_texts(
            papers=papers,
            comparison_aspects=aspects,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ComparisonServiceError as exc:
        logger.warning("Paper comparison failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected paper comparison error.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while comparing the papers.",
        ) from exc
