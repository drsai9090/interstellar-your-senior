"""Server-only operator authentication and bounded public demo queries."""

from collections import deque
from hmac import compare_digest
from time import monotonic

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import get_settings

_OPEN_PATHS = frozenset({"/health", "/docs", "/redoc", "/openapi.json", "/", "/demo"})


class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.query_times = deque()

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        path = request.url.path.rstrip("/") or "/"
        privileged = path == "/ingest" or path.startswith("/ingest/") or path == "/admin" or path.startswith("/admin/")
        is_query = path == "/query"
        if settings.demo_mode and privileged:
            return JSONResponse(status_code=403, content={"detail": "Ingestion and administration are disabled in the fixed-corpus demo."})
        is_static = settings.static_dir and request.method in {"GET", "HEAD"} and (path.startswith("/assets/") or path == "/favicon.svg")
        public = path in _OPEN_PATHS or is_static or (settings.demo_mode and is_query and request.method == "POST")
        if request.method != "OPTIONS" and not public:
            expected = settings.your_senior_api_key
            if len(expected) < 32:
                return JSONResponse(status_code=503, content={"detail": "Operator access is not configured."})
            supplied = request.headers.get("X-API-Key", "")
            if not compare_digest(supplied.encode(), expected.encode()):
                return JSONResponse(status_code=401, content={"detail": "Invalid or missing operator key."})
        if is_query and request.method == "POST":
            # ponytail: one process-wide budget suits a single demo worker;
            # move limits to a shared gateway before scaling across workers.
            now = monotonic()
            while self.query_times and self.query_times[0] <= now - 60:
                self.query_times.popleft()
            if len(self.query_times) >= 60:
                return JSONResponse(status_code=429, content={"detail": "Demo query limit reached. Try again in one minute."}, headers={"Retry-After": "60"})
            self.query_times.append(now)
            body = bytearray()
            async for part in request.stream():
                if len(body) + len(part) > 16384:
                    return JSONResponse(status_code=413, content={"detail": "Query body exceeds 16 KiB."})
                body.extend(part)
            # Starlette replays this bounded body to the downstream request parser.
            request._body = bytes(body)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response
