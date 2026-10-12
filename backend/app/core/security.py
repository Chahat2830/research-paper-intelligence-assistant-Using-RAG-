import re
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings

# --------------------------------------------------
# Allowed File Types
# --------------------------------------------------

ALLOWED_EXTENSIONS = {".pdf"}
PDF_CONTENT_TYPE = "application/pdf"


# --------------------------------------------------
# Filename Validation
# --------------------------------------------------


def sanitize_filename(filename: str) -> str:
    """Return a safe filename without directory components."""

    if not filename or not filename.strip():
        raise HTTPException(
            status_code=400,
            detail="Filename cannot be empty.",
        )

    # Remove any directory path supplied by the client.
    filename = Path(filename.replace("\\", "/")).name

    # Keep only the filename characters we explicitly allow.
    filename = re.sub(r"[^\w.\- ]", "_", filename)
    filename = filename.strip(" .")

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    return filename


# --------------------------------------------------
# Upload Validation
# --------------------------------------------------


def validate_pdf_filename(filename: str) -> str:
    """Validate and sanitize a PDF filename."""

    return sanitize_filename(filename)


def validate_pdf_content_type(content_type: str | None) -> None:
    """Check the declared MIME type of an uploaded file."""

    if content_type != PDF_CONTENT_TYPE:
        raise HTTPException(
            status_code=400,
            detail="Invalid content type. Please upload a PDF file.",
        )


def validate_file_size(file_size: int) -> None:
    """Reject files larger than the configured upload limit."""

    if file_size <= 0:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File exceeds the maximum allowed size of "
                f"{settings.max_upload_size_mb} MB."
            ),
        )


async def validate_pdf_upload(file: UploadFile) -> str:
    """
    Validate the uploaded PDF's filename, declared content type,
    actual PDF signature, and file size.

    Returns the sanitized filename.
    """

    filename = validate_pdf_filename(file.filename or "")
    validate_pdf_content_type(file.content_type)

    # Read one byte beyond the configured limit to detect oversized files.
    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    content = await file.read(max_size_bytes + 1)

    try:
        validate_file_size(len(content))
    except HTTPException:
        await file.seek(0)
        raise

    # Verify the PDF signature rather than trusting MIME metadata alone.
    if not content.startswith(b"%PDF-"):
        await file.seek(0)
        raise HTTPException(
            status_code=400,
            detail="The uploaded file does not have a valid PDF signature.",
        )

    # Reset the pointer so downstream PDF processing can read the file.
    await file.seek(0)

    return filename
