from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PaperUploadResponse(BaseModel):
    """Response returned after a paper is uploaded and processed."""

    paper_id: str = Field(
        ...,
        description="Unique identifier assigned to the research paper.",
    )
    filename: str = Field(
        ...,
        description="Name of the uploaded PDF file.",
    )
    status: Literal["uploaded", "processing", "processed", "failed"] = "uploaded"
    message: str = "Paper uploaded successfully."


class PaperMetadata(BaseModel):
    """Metadata describing an uploaded research paper."""

    paper_id: str
    filename: str
    title: str | None = None
    authors: list[str] = Field(default_factory=list)
    page_count: int | None = Field(default=None, ge=0)
    chunk_count: int = Field(default=0, ge=0)
    uploaded_at: datetime
    file_size_bytes: int = Field(ge=0)


class PaperListResponse(BaseModel):
    """Response containing the available research papers."""

    total: int = Field(ge=0)
    papers: list[PaperMetadata] = Field(default_factory=list)


class PaperDeleteResponse(BaseModel):
    """Response returned after deleting a research paper."""

    paper_id: str
    message: str = "Paper deleted successfully."
