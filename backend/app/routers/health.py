"""Health check endpoint — public, no API key required."""

from datetime import datetime, timezone

from fastapi import APIRouter, Response

from app.db.chroma import is_connected
from app.models.schemas import HealthResponse

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
async def health_check(response: Response):
    """
    Public health endpoint — no API key required.
    Used by Docker and Railway to verify the container is alive.
    """
    chroma_ok = is_connected()
    if not chroma_ok:
        response.status_code = 503
    return HealthResponse(
        status="ok" if chroma_ok else "degraded",
        app="Your Senior",
        version="1.1.0",
        chroma_connected=chroma_ok,
        timestamp=datetime.now(timezone.utc),
    )
