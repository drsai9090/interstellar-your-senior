"""FastAPI service with an isolated synthetic demo enabled by default."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.demo import router as demo_router, seed_demo
from app.middleware.auth import APIKeyMiddleware
from app.routers import admin, health, ingest, query


@asynccontextmanager
async def lifespan(app):
    if get_settings().demo_mode:
        await seed_demo()
    yield


settings = get_settings()
app = FastAPI(
    title="Interstellar — Your Senior",
    description="Evidence-backed document assistant prototype. Default: fixed synthetic corpus and author-written provider stub, not live AI.",
    version="1.1.0", lifespan=lifespan,
)
app.add_middleware(APIKeyMiddleware)
# CORS wraps auth responses as well as successful responses.
app.add_middleware(
    CORSMiddleware, allow_origins=settings.cors_origins_list,
    allow_credentials=False, allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)
app.include_router(health.router)
app.include_router(query.router)
app.include_router(ingest.router)
app.include_router(admin.router)
app.include_router(demo_router)

if settings.static_dir:
    app.mount("/", StaticFiles(directory=settings.static_dir, html=True), name="frontend")
else:
    @app.get("/", include_in_schema=False)
    async def root():
        return {"app": "Interstellar — Your Senior", "version": "1.1.0", "docs": "/docs", "health": "/health"}
