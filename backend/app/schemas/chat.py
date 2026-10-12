from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for asking questions about research papers."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Question about the uploaded research papers.",
    )

    paper_ids: list[str] | None = Field(
        default=None,
        description=(
            "Optional paper IDs to restrict the search. "
            "If omitted, search all available papers."
        ),
    )

    chat_history: list[dict[str, str]] = Field(
        default_factory=list,
        description="Previous conversation messages for context.",
    )


class SourceReference(BaseModel):
    """A source chunk supporting a generated answer."""

    paper_id: str
    filename: str
    page_number: int | None = None
    chunk_id: str | None = None
    excerpt: str | None = None
    relevance_score: float | None = None


class ChatResponse(BaseModel):
    """Response model for research-grounded answers."""

    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    question: str
    success: bool = True
