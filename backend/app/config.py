"""Application settings loaded from environment variables via pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Public demo never uses private storage or calls a paid model.
    demo_mode: bool = True
    static_dir: str = ""
    # Operator/CLI credential only; never deliver to a browser.
    your_senior_api_key: str = ""

    # Anthropic
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-5"

    # Google Drive (service account for document ingestion)
    google_service_account_json: str = "./secrets/service-account.json"
    google_drive_folder_id: str = ""

    # ChromaDB
    chroma_persist_dir: str = "./chromadb_store"
    chroma_collection_name: str = "your_senior_docs"

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # RAG retrieval
    top_k_chunks: int = 5
    max_chunk_tokens: int = 512
    chunk_overlap_tokens: int = 50

    # Admin
    query_log_max_entries: int = 50

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS_ORIGINS as a parsed list of origin strings."""
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (reads .env once at startup)."""
    return Settings()
