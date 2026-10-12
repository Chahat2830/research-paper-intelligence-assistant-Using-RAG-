"""API endpoints for uploading and managing research papers."""

import logging
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.security import validate_pdf_upload
from app.schemas.paper import PaperUploadResponse
from app.services.chunking_service import chunk_pages
from app.services.pdf_service import (
    PDFProcessingError,
    extract_pdf_metadata,
    extract_pdf_pages,
)
from app.services.vector_store_service import add_chunks
from app.utils.file_handler import (
    generate_paper_id,
    save_uploaded_file,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/papers",
    tags=["Research Papers"],
)


@router.post(
    "/upload",
    response_model=PaperUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_paper(
    file: Annotated[UploadFile, File()],
) -> PaperUploadResponse:
    """Upload a PDF and index its text for semantic retrieval."""

    paper_id = generate_paper_id()
    saved_path = None

    try:
        # Validate filename, MIME type, size, and PDF signature.
        filename = await validate_pdf_upload(file)

        # Read the validated file into memory.
        content = await file.read()

        if len(content) > settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="The uploaded file exceeds the configured size limit.",
            )

        # Save the PDF locally.
        saved_path = save_uploaded_file(
            paper_id=paper_id,
            filename=filename,
            content=content,
        )

        # Extract page text and metadata.
        pages = extract_pdf_pages(saved_path)
        extract_pdf_metadata(saved_path)

        # Reject PDFs with no extractable text.
        if not any(page["text"].strip() for page in pages):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "No extractable text was found in this PDF. "
                    "Scanned PDFs may require OCR."
                ),
            )

        # Split the PDF into chunks while preserving page metadata.
        chunks = chunk_pages(
            pages=pages,
            paper_id=paper_id,
            filename=filename,
        )

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No usable text chunks could be generated.",
            )

        # Store the chunks and generate embeddings through ChromaDB.
        add_chunks(chunks)

        logger.info(
            "Indexed paper %s with %s chunks.",
            paper_id,
            len(chunks),
        )

        return PaperUploadResponse(
            paper_id=paper_id,
            filename=filename,
            status="processed",
            message=(
                f"Paper uploaded and indexed successfully. "
                f"{len(chunks)} text chunks created."
            ),
        )

    except HTTPException:
        if saved_path is not None:
            saved_path.unlink(missing_ok=True)
        raise

    except PDFProcessingError as exc:
        if saved_path is not None:
            saved_path.unlink(missing_ok=True)

        logger.warning("PDF processing failed: %s", exc)

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except (ValueError, OSError) as exc:
        if saved_path is not None:
            saved_path.unlink(missing_ok=True)

        logger.exception("Paper upload failed.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The paper could not be saved or processed.",
        ) from exc

    except Exception as exc:
        if saved_path is not None:
            saved_path.unlink(missing_ok=True)

        logger.exception("Unexpected error while indexing a paper.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while uploading the paper.",
        ) from exc

    finally:
        await file.close()
