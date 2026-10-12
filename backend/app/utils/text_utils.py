"""Text cleaning and normalization utilities."""

import re
import unicodedata


def normalize_unicode(text: str) -> str:
    """Normalize Unicode characters to a consistent representation."""

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    return unicodedata.normalize("NFKC", text)


def normalize_whitespace(text: str) -> str:
    """Normalize spaces and line breaks while preserving paragraphs."""

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_extracted_text(text: str) -> str:
    """Clean common formatting artifacts in extracted PDF text."""

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    text = normalize_unicode(text)

    # Remove null bytes and non-printing control characters.
    text = "".join(
        character
        for character in text
        if character == "\n" or character == "\t" or character.isprintable()
    )

    # Join words split by a hyphen at a line break.
    text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)

    return normalize_whitespace(text)


def truncate_text(
    text: str,
    max_length: int = 5000,
    suffix: str = "...",
) -> str:
    """Limit text to a maximum character count."""

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    if max_length < 0:
        raise ValueError("max_length cannot be negative.")

    if len(text) <= max_length:
        return text

    if max_length <= len(suffix):
        return suffix[:max_length]

    return text[: max_length - len(suffix)].rstrip() + suffix


def count_words(text: str) -> int:
    """Count whitespace-separated words in text."""

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    return len(text.split())


def remove_repeated_blank_lines(text: str) -> str:
    """Reduce multiple consecutive blank lines to a single blank line."""

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    return re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", text).strip()
