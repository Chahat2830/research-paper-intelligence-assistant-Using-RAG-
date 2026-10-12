"""Citation extraction and formatting utilities."""

import re
from typing import Any

# Common author-year citation patterns, such as:
# (Smith, 2024), (Smith & Jones, 2023), and Smith et al. (2022).
AUTHOR_YEAR_PATTERN = re.compile(
    r"""
    (?:
        \(
            [A-Z][A-Za-z'’\-]+
            (?:
                \s+(?:et\s+al\.|and\s+[A-Z][A-Za-z'’\-]+|&\s*[A-Z][A-Za-z'’\-]+)
            )?
            ,?\s+\d{4}[a-z]?
            (?:\s*;\s*[^()]+)?
        \)
        |
        \b[A-Z][A-Za-z'’\-]+
        \s+et\s+al\.\s*
        \(\d{4}[a-z]?\)
    )
    """,
    re.VERBOSE,
)


def extract_author_year_citations(text: str) -> list[str]:
    """Extract citation-like author-year strings from text."""

    if not text or not text.strip():
        return []

    matches = AUTHOR_YEAR_PATTERN.findall(text)

    # Preserve order while removing duplicate matches.
    unique_matches: list[str] = []
    seen: set[str] = set()

    for match in matches:
        citation = match.strip()

        if citation and citation not in seen:
            seen.add(citation)
            unique_matches.append(citation)

    return unique_matches


def extract_reference_section(text: str) -> str | None:
    """Extract a likely references or bibliography section."""

    if not text or not text.strip():
        return None

    heading_pattern = re.compile(r"(?im)^\s*(references|bibliography|works cited)\s*$")

    match = heading_pattern.search(text)

    if not match:
        return None

    section = text[match.end() :].strip()

    if not section:
        return None

    # Stop if a likely subsequent top-level section begins.
    next_section_pattern = re.compile(
        r"(?im)^\s*(appendix(?:\s+[A-Z0-9]+)?|acknowledgments|"
        r"acknowledgements|author contributions|conflict of interest)\s*$"
    )

    next_match = next_section_pattern.search(section)

    if next_match:
        section = section[: next_match.start()].strip()

    return section or None


def split_reference_entries(reference_text: str) -> list[str]:
    """Split a references section into likely individual entries."""

    if not reference_text or not reference_text.strip():
        return []

    lines = [line.strip() for line in reference_text.splitlines() if line.strip()]

    entries: list[str] = []
    current_entry: list[str] = []

    numbered_entry_pattern = re.compile(r"^\s*(?:\[\d+\]|\d+[.)])\s+")
    author_entry_pattern = re.compile(r"^[A-Z][A-Za-z'’\-]+,\s*[A-Z]")

    for line in lines:
        starts_new_entry = bool(
            numbered_entry_pattern.match(line) or author_entry_pattern.match(line)
        )

        if starts_new_entry and current_entry:
            entries.append(" ".join(current_entry))
            current_entry = [line]
        elif current_entry:
            current_entry.append(line)
        else:
            current_entry = [line]

    if current_entry:
        entries.append(" ".join(current_entry))

    return entries


def format_reference_list(references: list[str]) -> list[str]:
    """Normalize whitespace in supplied reference strings."""

    formatted: list[str] = []
    seen: set[str] = set()

    for reference in references:
        normalized = " ".join(reference.split())

        if normalized and normalized.casefold() not in seen:
            seen.add(normalized.casefold())
            formatted.append(normalized)

    return formatted


def build_citation_metadata(text: str) -> dict[str, Any]:
    """Extract citation-like strings and reference-section metadata."""

    reference_section = extract_reference_section(text)

    references = split_reference_entries(reference_section) if reference_section else []

    return {
        "in_text_citations": extract_author_year_citations(text),
        "references_found": bool(reference_section),
        "references": format_reference_list(references),
        "reference_count": len(references),
    }
