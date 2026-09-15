"""Local text embedder using sentence-transformers (no external API required)."""

import asyncio
import hashlib
import re

from app.config import get_settings

_model = None


def _get_model():
    """Return the shared embedding model, loading it on first call."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _embed_one(text: str) -> list[float]:
    """Embed a single text string synchronously."""
    if get_settings().demo_mode:
        # ponytail: hashed word counts suit three synthetic docs; use the existing
        # sentence transformer for private semantic retrieval and evaluate it.
        vector = [0.0] * 256
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            index = int.from_bytes(hashlib.sha256(word.encode()).digest()[:2]) % 256
            vector[index] += 1.0
        return vector
    return _get_model().encode(text, convert_to_tensor=False).tolist()


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of document chunks for storage in ChromaDB."""
    results = []
    for text in texts:
        embedding = await asyncio.to_thread(_embed_one, text)
        results.append(embedding)
    return results


async def embed_query(text: str) -> list[float]:
    """Embed a single user question for similarity search."""
    return await asyncio.to_thread(_embed_one, text)
