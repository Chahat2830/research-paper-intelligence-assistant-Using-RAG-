"""Literature review generation service."""

import json
import logging
import re
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.prompts.research_prompts import build_literature_review_prompt
from app.services.llm_service import LLMServiceError, generate_response

logger = logging.getLogger(__name__)


class LiteratureReviewServiceError(Exception):
    """Raised when literature review generation fails."""


class LiteratureReviewResult(BaseModel):
    """Structured output of a generated literature review."""

    research_topic: str
    title: str
    introduction: str
    thematic_analysis: list[str] = Field(default_factory=list)
    agreements_and_disagreements: list[str] = Field(default_factory=list)
    research_gaps: list[str] = Field(default_factory=list)
    conclusion: str
    references: list[str] = Field(default_factory=list)


def _parse_json_response(response: str) -> dict[str, Any]:
    """Parse JSON returned by an LLM, including common formatting mistakes."""

    if not response or not response.strip():
        raise LiteratureReviewServiceError(
            "The AI returned an empty literature review."
        )

    cleaned = response.strip().lstrip("\ufeff")

    # Remove Markdown fences if present.
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    # Extract the outermost JSON object if the model added commentary.
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end <= start:
        logger.warning("Literature review response had no JSON object: %s", cleaned[:800])
        raise LiteratureReviewServiceError(
            "The AI response did not contain a JSON object. Please try again."
        )

    cleaned = cleaned[start : end + 1]

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        # Common LLM formatting issue: trailing commas before } or ].
        repaired = re.sub(r",\s*([}\]])", r"\1", cleaned)
        try:
            parsed = json.loads(repaired)
        except json.JSONDecodeError as exc:
            logger.warning(
                "Invalid literature review JSON at line %s column %s. Response preview: %s",
                exc.lineno,
                exc.colno,
                cleaned[:1200],
            )
            raise LiteratureReviewServiceError(
                "The AI returned invalid JSON for the literature review. "
                "Please try again."
            ) from exc

    if not isinstance(parsed, dict):
        raise LiteratureReviewServiceError(
            "The AI literature review must be a JSON object."
        )

    return parsed


def generate_literature_review(
    research_topic: str,
    papers: list[dict[str, str]],
) -> LiteratureReviewResult:
    """Generate a structured literature review from supplied paper text."""

    topic = research_topic.strip()

    if not topic:
        raise ValueError("Research topic cannot be empty.")
    if len(papers) < 2:
        raise ValueError(
            "At least two research papers are required for a literature review."
        )
    if len(papers) > 10:
        raise ValueError("A maximum of 10 research papers can be included.")

    formatted_papers: list[str] = []
    seen_ids: set[str] = set()

    for paper in papers:
        paper_id = paper.get("paper_id", "").strip()
        filename = paper.get("filename", "Unknown document").strip()
        text = paper.get("text", "").strip()

        if not paper_id:
            raise ValueError("Every paper must have a paper_id.")
        if paper_id in seen_ids:
            raise ValueError("Duplicate paper IDs are not allowed.")
        if not text:
            raise ValueError(f"No extracted text was provided for paper {paper_id}.")

        seen_ids.add(paper_id)
        formatted_papers.append(
            f"Paper ID: {paper_id}\n"
            f"Filename: {filename}\n"
            f"Content:\n{text}"
        )

    papers_text = "\n\n---\n\n".join(formatted_papers)

    prompt = build_literature_review_prompt(
        papers_text=papers_text,
        research_topic=topic,
    )

    # Explicit schema helps prevent free-form prose or malformed JSON.
    output_contract = f"""
IMPORTANT OUTPUT FORMAT:
Return only one valid JSON object. Do not use Markdown code fences or text
before or after the JSON. Use double quotes for all JSON keys and string values.
Do not include trailing commas. Do not invent facts or citations. Base the
review only on the supplied paper content. If evidence is missing, say so.

Use exactly this structure:
{{
  "research_topic": {json.dumps(topic)},
  "title": "A clear academic title",
  "introduction": "A concise introduction to the topic and the selected papers",
  "thematic_analysis": [
    "Theme supported by the selected paper content"
  ],
  "agreements_and_disagreements": [
    "Evidence-based agreement or disagreement across papers"
  ],
  "research_gaps": [
    "Research gap supported by the selected paper content"
  ],
  "conclusion": "A synthesis of the literature and its main implications",
  "references": [
    "Filename and page details when available in the supplied text"
  ]
}}

Every field must be present. For list fields, provide informative items; if the
papers do not contain enough evidence for a point, explicitly say so rather
than inventing details. Research topic: {topic}
"""
    prompt = f"{prompt}\n\n{output_contract}"

    try:
        response = generate_response(
            prompt=prompt,
            temperature=0.1,
            max_tokens=4096,
        )
    except LLMServiceError as exc:
        logger.exception("LLM request failed during literature review generation.")
        raise LiteratureReviewServiceError(
            "Could not generate the literature review. Please try again."
        ) from exc

    parsed = _parse_json_response(response)
    parsed.setdefault("research_topic", topic)

    try:
        result = LiteratureReviewResult.model_validate(parsed)
    except ValidationError as exc:
        logger.warning(
            "LLM literature review did not match expected schema: %s",
            exc,
        )
        raise LiteratureReviewServiceError(
            "The AI literature review did not match the expected format. "
            "Please try again."
        ) from exc

    return result
