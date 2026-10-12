from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Request model for analyzing a research paper."""

    paper_id: str = Field(
        ...,
        min_length=1,
        description="Unique ID of the paper to analyze.",
    )


class PaperAnalysis(BaseModel):
    """Structured analysis of a research paper."""

    title: str | None = None
    research_objectives: list[str] = Field(default_factory=list)
    problem_statement: str | None = None
    methodology: str | None = None
    datasets_used: list[str] = Field(default_factory=list)
    key_findings: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    future_research_directions: list[str] = Field(default_factory=list)
    conclusion: str | None = None


class AnalysisResponse(BaseModel):
    """Response returned after paper analysis."""

    paper_id: str
    success: bool = True
    message: str = "Paper analysis completed successfully."
    analysis: PaperAnalysis
