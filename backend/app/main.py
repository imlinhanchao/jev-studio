import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.session import init_db
from app.api.v1.router import api_v1_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("jev")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database tables and default developer key
    logger.info("Initializing database schemas...")
    await init_db()
    logger.info("JEV Decision Model API service initialized successfully.")
    yield
    # Shutdown
    logger.info("Shutting down JEV Decision Model API service...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Liquid AI d1-omni-600M JEV Decision Model API with Key Quotas & Token Consumption Analytics",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "model": settings.MODEL_ID,
    }

# Static directory and Frontend SPA serving
static_path = Path(settings.STATIC_DIR)

if (static_path / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(static_path / "assets")), name="static_assets")

@app.api_route("/{full_path:path}", methods=["GET", "HEAD"], include_in_schema=False)
async def serve_spa_frontend(full_path: str):
    """
    Serves static frontend files and falls back to index.html for Vue Router SPA routes.
    Does not intercept /api or swagger doc routes.
    """
    if full_path.startswith("api/") or full_path == "api":
        raise HTTPException(status_code=404, detail="API endpoint not found")

    target_file = static_path / full_path
    if full_path and target_file.is_file():
        return FileResponse(target_file)

    index_file = static_path / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)

    return {
        "message": "Frontend build not found.",
        "hint": "Run 'pnpm build' in frontend directory to populate the static directory.",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
