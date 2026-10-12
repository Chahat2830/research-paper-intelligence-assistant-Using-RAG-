"""Research paper comparison service."""

import json
import logging
from typing import Any

from pydantic import ValidationError

from app.prompts.research_prompts import build_comparison_prompt
from app.schemas.comparison import ComparisonResponse
from app.services.llm_service import LLMServiceError, generate_response

logger = logging.getLogger(__name__)


class ComparisonServiceError(Exception):
    """Raised when research paper comparison fails."""


def _parse_comparison_response(response: str) -> dict[str, Any]:
    """Parse a JSON object returned by the LLM, including fenced JSON."""

    cleaned = response.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    # Tolerate short introductory text around a JSON object.
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        cleaned = cleaned[start : end + 1]

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.warning("Could not parse comparison JSON: %s", cleaned[:500])
        raise ComparisonServiceError(
            "The AI returned invalid JSON for the paper comparison. "
            "Please try again."
        ) from exc

    if not isinstance(parsed, dict):
        raise ComparisonServiceError(
            "The AI comparison response was not a JSON object."
        )

    return parsed


def _has_findings(parsed: dict[str, Any]) -> bool:
    """Return True only when the response contains actual comparison findings."""

    if isinstance(parsed.get("papers"), list) and parsed["papers"]:
        return True

    for key in ("common_themes", "key_differences", "research_gaps"):
        value = parsed.get(key)
        if isinstance(value, list) and any(str(item).strip() for item in value):
            return True

    summary = parsed.get("overall_summary")
    return isinstance(summary, str) and bool(summary.strip())


def compare_paper_texts(
    papers: list[dict[str, str]],
    comparison_aspects: list[str] | None = None,
) -> ComparisonResponse:
    """Compare supplied research-paper text and return a structured report."""

    if len(papers) < 2:
        raise ValueError("At least two research papers are required.")
    if len(papers) > 10:
        raise ValueError("A maximum of 10 research papers can be compared.")

    formatted_papers: list[str] = []
    expected_ids: list[str] = []
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
            raise ValueError(
                f"No extracted text was provided for paper {paper_id}."
            )

        seen_ids.add(paper_id)
        expected_ids.append(paper_id)
        formatted_papers.append(
            f"Paper ID: {paper_id}\n"
            f"Filename: {filename}\n"
            f"Content:\n{text}"
        )

    aspects = comparison_aspects or [
        "research_objectives",
        "methodology",
        "datasets",
        "key_findings",
        "limitations",
    ]

    base_prompt = build_comparison_prompt(
        papers_text="\n\n---\n\n".join(formatted_papers),
        comparison_aspects=aspects,
    )

    # Explicitly require the exact response structure used by ComparisonResponse.
    # Without this instruction, a valid but empty JSON object can pass through
    # Pydantic defaults and incorrectly look like a successful comparison.
    output_contract = f"""
IMPORTANT OUTPUT REQUIREMENTS:
Return ONLY one valid JSON object. Do not use Markdown fences or add prose.
You MUST analyze the supplied content and populate the report with findings.
Never return empty arrays or an empty object merely because a detail is unclear.
For details that cannot be established from a paper, write
"Not available in the provided paper text." Do not invent results.
Include exactly one item in "papers" for each selected paper, preserving these
paper_id values exactly: {json.dumps(expected_ids)}.

Use this exact JSON structure:
{{
  "success": true,
  "message": "Paper comparison completed successfully.",
  "papers": [
    {{
      "paper_id": "EXACT_ID_FROM_INPUT",
      "title": "Paper title or filename",
      "research_objectives": "Objective supported by the supplied text",
      "methodology": "Methods and model/architecture",
      "datasets": ["Dataset details or unavailable statement"],
      "key_findings": ["Findings supported by the supplied text"],
      "strengths": ["Evidence-based strength"],
      "limitations": ["Stated or evidence-supported limitation"]
    }}
  ],
  "common_themes": ["Shared theme across the selected papers"],
  "key_differences": ["Specific difference between the papers"],
  "research_gaps": ["Gap supported by the comparison; do not speculate"],
  "overall_summary": "A concise synthesis comparing the papers."
}}

The "papers" array must contain {len(papers)} items, one per input paper.
Use these comparison aspects as priorities: {json.dumps(aspects)}.
The input content is separated by paper ID and filename. Keep each paper's
findings attributed to the correct paper.
"""

    prompt = f"{base_prompt}\n\n{output_contract}"

    try:
        response_text = generate_response(
            prompt=prompt,
            temperature=0.1,
            max_tokens=4096,
        )
    except LLMServiceError as exc:
        logger.exception("LLM request failed during paper comparison.")
        raise ComparisonServiceError(
            "Could not generate the research paper comparison."
        ) from exc

    parsed = _parse_comparison_response(response_text)

    # Fill missing metadata without masking a response with no actual findings.
    parsed.setdefault("success", True)
    parsed.setdefault("message", "Paper comparison completed successfully.")

    if not _has_findings(parsed):
        logger.error(
            "LLM returned an empty comparison object. Response keys: %s",
            sorted(parsed.keys()),
        )
        raise ComparisonServiceError(
            "The AI returned an empty comparison report. "
            "Please try again. If this repeats, check the backend logs."
        )

    # Fill in titles from the uploaded filenames and verify the selected IDs
    # are represented in the report. Never silently report an empty success.
    returned_papers = parsed.get("papers")
    if isinstance(returned_papers, list):
        known = {paper["paper_id"]: paper for paper in papers}
        normalized = []
        for item in returned_papers:
            if not isinstance(item, dict):
                continue
            paper_id = str(item.get("paper_id", "")).strip()
            if paper_id not in known:
                continue
            item.setdefault("title", known[paper_id].get("filename", "Research paper"))
            normalized.append(item)
        parsed["papers"] = normalized

    try:
        result = ComparisonResponse.model_validate(parsed)
    except ValidationError as exc:
        logger.warning("LLM comparison did not match the expected schema.")
        raise ComparisonServiceError(
            "The AI comparison did not match the expected response format. "
            "Please try again."
        ) from exc

    if not result.papers:
        raise ComparisonServiceError(
            "The AI did not return per-paper comparison details. "
            "Please try again."
        )

    return result
