"""
Main FastAPI application
CPS Scaffolding Agent for Creative Metacognition
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
import traceback

from .core.config import settings
from .api import chat, research
from .db import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.LOG_LEVEL == "info" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Application version
VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    logger.info("Starting CPS Scaffolding Agent...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise

    yield
    # Shutdown
    logger.info("Shutting down CPS Scaffolding Agent...")


# Create FastAPI app
app = FastAPI(
    title="CPS Scaffolding Agent",
    description="AI agent for promoting creative metacognition in problem solving",
    version=VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression for production
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Global exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else "unknown"
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "서비스 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            "error_id": id(exc),  # For debugging purposes
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with user-friendly messages"""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "입력 데이터가 올바르지 않습니다.",
            "errors": exc.errors()
        }
    )


# Include routers
app.include_router(chat.router)
app.include_router(research.router)

# Mount static files for production (frontend build)
STATIC_DIR = Path(__file__).parent.parent / "static"
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")
    logger.info(f"Mounted static files from {STATIC_DIR}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CPS Scaffolding Agent API",
        "version": VERSION,
        "docs": "/docs",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway monitoring"""
    return {
        "status": "healthy",
        "version": VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """
    Serve frontend SPA for production
    Falls back to index.html for client-side routing
    """
    # Skip API routes
    if full_path.startswith("api/") or full_path in ["health", "docs", "openapi.json"]:
        return {"error": "Not found"}, 404

    # Serve index.html for SPA routing
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))

    return {"error": "Frontend not built"}, 404


if __name__ == "__main__":
    import uvicorn
    import os

    # Production configuration
    workers = int(os.getenv("UVICORN_WORKERS", "2" if not settings.DEBUG else "1"))

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=workers if not settings.DEBUG else 1,
        log_level=settings.LOG_LEVEL,
        access_log=False  # Disable access log for production (Railway handles this)
    )
