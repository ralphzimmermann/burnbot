from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from pathlib import Path
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.recommendations import router as recommendations_router
from app.api.auth import router as auth_router
from app.api.favorites import router as favorites_router
from app.db import init_db, SessionLocal
from app.services.favorites_sync import sync_favorites_with_events


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        FastAPI: Configured FastAPI app.
    """
    app = FastAPI(title="BM EventGuide Backend", version="0.2.0")

    # Load environment variables from .env (if present)
    load_dotenv()
    origins_env = os.environ.get("CORS_ORIGINS")
    if not origins_env or not origins_env.strip():
        origins_env = (
            "http://localhost:5173,http://127.0.0.1:5173,"
            "http://localhost:5174,http://127.0.0.1:5174,"
            "http://localhost:8000,http://127.0.0.1:8000"
        )
    allow_origins = [o.strip() for o in origins_env.split(",") if o.strip()]

    # Configure CORS. If wildcard is used, credentials cannot be allowed.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["set-cookie"],
        max_age=600,
    )

    # Cookie-based sessions
    secret_key = os.environ.get("SECRET_KEY", "dev-insecure-secret")
    app.add_middleware(SessionMiddleware, secret_key=secret_key, same_site="lax")

    # Initialize database (creates tables if needed)
    init_db()

    # On startup, sync favorites with latest events.json so mobile clients
    # receive up-to-date fields (including coordinates)
    @app.on_event("startup")
    async def _sync_favorites_on_startup() -> None:
        base_dir = Path(__file__).resolve().parents[2]  # website/
        data_dir = base_dir / "backend" / "data"
        db = SessionLocal()
        try:
            sync_favorites_with_events(db, data_dir)
        finally:
            db.close()

    @app.get("/health")
    async def health() -> dict:
        return {"message": "Hello World"}

    app.include_router(recommendations_router)
    app.include_router(auth_router)
    app.include_router(favorites_router)

    # --- Frontend static files (Vite build) ---
    # Serve the built frontend from `website/frontend/dist`
    base_dir = Path(__file__).resolve().parents[2]  # website/
    frontend_dist = base_dir / "frontend" / "dist"
    index_html = frontend_dist / "index.html"

    if frontend_dist.exists() and index_html.exists():
        # Serve hashed assets at /assets/*
        assets_dir = frontend_dist / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        # Root index
        @app.get("/")
        async def serve_root() -> FileResponse:  # type: ignore[override]
            return FileResponse(str(index_html))

        # SPA fallback: if requested path is an existing file in dist, serve it; otherwise index.html
        @app.get("/{full_path:path}")
        async def spa_fallback(full_path: str) -> FileResponse:  # type: ignore[override]
            candidate = frontend_dist / full_path
            if candidate.is_file():
                return FileResponse(str(candidate))
            return FileResponse(str(index_html))

    return app


app = create_app()


