"""ChromaDB client and collection singleton used throughout the application."""

from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings


@lru_cache()
def get_chroma_client() -> chromadb.PersistentClient:
    """Return a cached ChromaDB persistent client (created once at startup)."""
    settings = get_settings()
    if settings.demo_mode:
        return chromadb.EphemeralClient(
            settings=ChromaSettings(anonymized_telemetry=False)
        )
    return chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_collection() -> chromadb.Collection:
    """Return the application's ChromaDB collection, creating it if absent."""
    settings = get_settings()
    client = get_chroma_client()
    return client.get_or_create_collection(
        name="interstellar_synthetic_v1" if settings.demo_mode else settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},  # cosine similarity → scores in [0, 1]
    )


def is_connected() -> bool:
    """Return True if ChromaDB is reachable and the collection is accessible."""
    try:
        get_collection().count()
        return True
    except Exception:
        return False
