from pydantic import BaseModel, Field, model_validator


class ComparisonRequest(BaseModel):
    """Request model for comparing research papers."""

    paper_ids: list[str] = Field(
        ...,
        min_length=2,
        max_length=10,
        description="IDs of 2–10 research papers to compare.",
    )

    comparison_aspects: list[str] = Field(
        default_factory=lambda: [
            "research_objectives",
            "methodology",
            "datasets",
            "key_findings",
            "limitations",
        ],
        description="Research aspects to compare across papers.",
    )

    @model_validator(mode="after")
    def validate_unique_paper_ids(self):
        """Ensure every paper ID is unique."""

        if len(set(self.paper_ids)) != len(self.paper_ids):
            raise ValueError("paper_ids must not contain duplicates.")

        if any(not paper_id.strip() for paper_id in self.paper_ids):
            raise ValueError("paper_ids must not contain empty values.")

        return self


class PaperComparisonItem(BaseModel):
    """Comparison details for one research paper."""

    paper_id: str
    title: str | None = None
    research_objectives: str | None = None
    methodology: str | None = None
    datasets: list[str] = Field(default_factory=list)
    key_findings: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ComparisonResponse(BaseModel):
    """Response returned after comparing research papers."""

    success: bool = True
    message: str = "Paper comparison completed successfully."
    papers: list[PaperComparisonItem] = Field(default_factory=list)
    common_themes: list[str] = Field(default_factory=list)
    key_differences: list[str] = Field(default_factory=list)
    research_gaps: list[str] = Field(default_factory=list)
    overall_summary: str | None = None
