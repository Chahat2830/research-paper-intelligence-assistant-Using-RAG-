from typing import Any

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """Standard response structure for API endpoints."""

    success: bool = True
    message: str = "Request completed successfully."
    data: Any = None


class ErrorResponse(BaseModel):
    """Standard response structure for API errors."""

    success: bool = False
    message: str = "An error occurred."
    detail: Any = None


class HealthResponse(BaseModel):
    """Response model for the health-check endpoint."""

    status: str = Field(
        description="Current backend health status.",
        examples=["healthy"],
    )
    app_name: str
    version: str
    timestamp: str
