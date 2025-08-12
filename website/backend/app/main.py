from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from pathlib import Path
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles

from app.api.recommendations import router as recommendations_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        FastAPI: Configured FastAPI app.
    """
    app = FastAPI(title="BM EventGuide Backend", version="0.1.0")

    # Load environment variables from .env (if present)
    load_dotenv()
    origins_env = os.environ.get("CORS_ORIGINS")
    if not origins_env or not origins_env.strip():
        origins_env = "http://localhost:5173,http://127.0.0.1:5173"
    allow_origins = [o.strip() for o in origins_env.split(",") if o.strip()]

    # If wildcard requested, also set a permissive regex to satisfy preflight
    allow_origin_regex = ".*" if "*" in allow_origins else None
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins if allow_origin_regex is None else ["*"],
        allow_origin_regex=allow_origin_regex,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict:
        return {"message": "Hello World"}

    app.include_router(recommendations_router)

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


