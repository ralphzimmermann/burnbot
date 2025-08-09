from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

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

    return app


app = create_app()


