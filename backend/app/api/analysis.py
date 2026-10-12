"""API endpoints for research-paper analysis."""

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.schemas.analysis import PaperAnalysis
from app.services.analysis_service import (
    AnalysisServiceError,
    analyze_paper_text,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analysis",
    tags=["Paper Analysis"],
)


class AnalyzeTextRequest(BaseModel):
    """Request body for analyzing extracted paper text."""

    paper_id: str = Field(..., min_length=1, max_length=200)
    paper_text: str = Field(..., min_length=1)


class AnalyzeTextResponse(BaseModel):
    """Response containing structured paper analysis."""

    success: bool = True
    paper_id: str
    analysis: PaperAnalysis


@router.post(
    "/",
    response_model=AnalyzeTextResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_research_paper(
    request: AnalyzeTextRequest,
) -> AnalyzeTextResponse:
    """Analyze research-paper text and return structured findings."""

    paper_id = request.paper_id.strip()
    paper_text = request.paper_text.strip()

    if not paper_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="paper_id cannot be empty.",
        )

    if not paper_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="paper_text cannot be empty.",
        )

    try:
        analysis = analyze_paper_text(paper_text)

        return AnalyzeTextResponse(
            success=True,
            paper_id=paper_id,
            analysis=analysis,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except AnalysisServiceError as exc:
        logger.warning(
            "Analysis failed for paper %s: %s",
            paper_id,
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not generate a valid paper analysis.",
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected error analyzing paper %s.",
            paper_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during paper analysis.",
        ) from exc
