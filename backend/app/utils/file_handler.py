"""Safe local file handling for research-paper PDFs."""

from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.core.security import sanitize_filename


def _resolve_inside_papers_dir(path: Path) -> Path:
    """Ensure a resolved path remains inside the papers directory."""

    papers_dir = settings.papers_path.resolve()
    resolved_path = path.resolve()

    if not resolved_path.is_relative_to(papers_dir):
        raise ValueError("File path must remain inside the papers directory.")

    return resolved_path


def generate_paper_id() -> str:
    """Generate a unique identifier for an uploaded paper."""

    return uuid4().hex


def build_storage_path(
    paper_id: str,
    filename: str,
) -> Path:
    """Build a safe PDF storage path for a paper."""

    if not paper_id or not paper_id.strip():
        raise ValueError("paper_id cannot be empty.")

    if Path(paper_id).name != paper_id or paper_id in {".", ".."}:
        raise ValueError("Invalid paper_id.")

    safe_filename = sanitize_filename(filename)

    # Each paper gets its own directory to avoid filename collisions.
    paper_directory = settings.papers_path / paper_id
    paper_directory.mkdir(parents=True, exist_ok=True)

    return _resolve_inside_papers_dir(paper_directory / safe_filename)


def save_uploaded_file(
    paper_id: str,
    filename: str,
    content: bytes,
) -> Path:
    """Save PDF bytes to local storage without overwriting an existing file."""

    if not content:
        raise ValueError("Cannot save an empty file.")

    destination = build_storage_path(paper_id, filename)

    # Exclusive creation prevents accidentally replacing an existing file.
    try:
        with destination.open("xb") as file:
            file.write(content)
    except FileExistsError as exc:
        raise FileExistsError(
            "A file with this name already exists for this paper."
        ) from exc

    return destination


def get_stored_file_path(
    paper_id: str,
    filename: str,
) -> Path:
    """Return the path of an existing stored PDF."""

    path = build_storage_path(paper_id, filename)

    if not path.is_file():
        raise FileNotFoundError("The requested paper file was not found.")

    return path


def delete_stored_file(
    paper_id: str,
    filename: str,
) -> bool:
    """Delete a stored PDF and remove its empty paper directory."""

    path = get_stored_file_path(paper_id, filename)
    path.unlink()

    paper_directory = path.parent

    try:
        paper_directory.rmdir()
    except OSError:
        # Keep the directory if it contains other files.
        pass

    return True


def delete_paper_directory(paper_id: str) -> bool:
    """Remove a paper directory only when it is empty."""

    if not paper_id or not paper_id.strip():
        raise ValueError("paper_id cannot be empty.")

    if Path(paper_id).name != paper_id or paper_id in {".", ".."}:
        raise ValueError("Invalid paper_id.")

    paper_directory = _resolve_inside_papers_dir(settings.papers_path / paper_id)

    if not paper_directory.is_dir():
        return False

    try:
        paper_directory.rmdir()
    except OSError:
        return False

    return True
