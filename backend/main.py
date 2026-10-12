"""Application entry point for Research Paper Intelligence Assistant."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analysis import router as analysis_router
from app.api.chat import router as chat_router
from app.api.comparison import router as comparison_router
from app.api.health import router as health_router
from app.api.literature_review import router as literature_review_router
from app.api.papers import router as papers_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""

    logger.info("%s starting up.", settings.app_name)

    yield

    logger.info("%s shutting down.", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "An AI-powered research assistant for paper analysis, "
        "semantic search, question answering, and literature reviews."
    ),
    debug=settings.debug,
    lifespan=lifespan,
)

# Allow requests from the configured React frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers.
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(papers_router, prefix=settings.api_prefix)
app.include_router(chat_router, prefix=settings.api_prefix)
app.include_router(analysis_router, prefix=settings.api_prefix)
app.include_router(comparison_router, prefix=settings.api_prefix)
app.include_router(literature_review_router, prefix=settings.api_prefix)


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Return basic application information."""

    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }