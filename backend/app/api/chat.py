"""API endpoints for research-paper question answering."""

import logging

from fastapi import APIRouter, HTTPException, status

from app.prompts.research_prompts import (
    SYSTEM_PROMPT,
    build_question_answering_prompt,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    SourceReference,
)
from app.services.llm_service import LLMServiceError, generate_response
from app.services.retrieval_service import retrieve_context

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Research Chat"],
)


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def chat_with_research_papers(
    request: ChatRequest,
) -> ChatResponse:
    """Answer a question using retrieved research-paper passages."""

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Question cannot be empty.",
        )

    try:
        retrieval = retrieve_context(
            question=question,
            paper_ids=request.paper_ids,
        )

        context = retrieval["context"]
        sources = retrieval["sources"]

        history_lines = []

        for message in request.chat_history[-10:]:
            role = message.get("role", "").strip().lower()
            content = message.get("content", "").strip()

            if role in {"user", "assistant"} and content:
                history_lines.append(f"{role.title()}: {content}")

        chat_history = "\n".join(history_lines)

        prompt = build_question_answering_prompt(
            question=question,
            context=context,
            chat_history=chat_history,
        )

        answer = generate_response(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
        )

        source_references = [
            SourceReference(
                paper_id=source["paper_id"],
                filename=source["filename"],
                page_number=source.get("page_number"),
                chunk_id=source.get("chunk_id"),
                excerpt=source.get("excerpt"),
                relevance_score=source.get("relevance_score"),
            )
            for source in sources
        ]

        return ChatResponse(
            question=question,
            answer=answer,
            sources=source_references,
            success=True,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except LLMServiceError as exc:
        logger.warning("Research chat LLM request failed: %s", exc)

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI service could not answer your question.",
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected research chat error.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while answering your question.",
        ) from exc
