from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# --------------------------------------------------
# Project Paths
# --------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR

load_dotenv(BACKEND_DIR / ".env")


# --------------------------------------------------
# Application Configuration
# --------------------------------------------------


class Settings(BaseSettings):
    """Centralized application settings loaded from .env."""

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Research Paper Intelligence Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = "/api"

    # Groq LLM
    groq_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=2048, gt=0)

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"
    normalize_embeddings: bool = True

    # PDF processing and chunking
    chunk_size: int = Field(default=1000, gt=0)
    chunk_overlap: int = Field(default=150, ge=0)
    max_upload_size_mb: int = Field(default=25, gt=0)

    # Retrieval
    top_k: int = Field(default=5, gt=0)
    similarity_search_type: str = "similarity"

    # Storage
    data_dir: str = "data"
    papers_dir: str = "data/papers"
    chroma_dir: str = "data/chroma_db"
    chroma_collection_name: str = "research_papers"

    # Frontend and CORS
    frontend_url: str = "http://localhost:5173"
    cors_origins: str = "http://localhost:5173"

    # Logging
    log_level: str = "INFO"

    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, value: int, info):
        chunk_size = info.data.get("chunk_size", 1000)

        if value >= chunk_size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE.")

        return value

    @field_validator("api_prefix")
    @classmethod
    def normalize_api_prefix(cls, value: str) -> str:
        value = value.strip()

        if not value:
            return "/api"

        return "/" + value.strip("/")

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert comma-separated CORS origins into a list."""
        return [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def data_path(self) -> Path:
        return self._resolve_path(self.data_dir)

    @property
    def papers_path(self) -> Path:
        return self._resolve_path(self.papers_dir)

    @property
    def chroma_path(self) -> Path:
        return self._resolve_path(self.chroma_dir)

    @staticmethod
    def _resolve_path(path: str) -> Path:
        """Resolve relative storage paths from the backend directory."""
        candidate = Path(path).expanduser()

        if not candidate.is_absolute():
            candidate = BACKEND_DIR / candidate

        return candidate.resolve()

    def create_directories(self) -> None:
        """Create required local storage directories."""
        self.papers_path.mkdir(parents=True, exist_ok=True)
        self.chroma_path.mkdir(parents=True, exist_ok=True)

    def validate_api_configuration(self) -> None:
        """Validate configuration required for LLM operations."""
        if not self.groq_api_key.strip():
            raise ValueError("GROQ_API_KEY is missing. Add it to backend/.env.")


# --------------------------------------------------
# Cached Settings Instance
# --------------------------------------------------


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once and reuse them across the application."""
    settings = Settings()

    settings.create_directories()

    return settings


settings = get_settings()
