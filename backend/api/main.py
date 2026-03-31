"""
Search-Score-Send Backend API
Main FastAPI application entry point
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator
import json

from .routers import jd, search, scoring, messages, hitl, progress, data_monetization
from .config import settings
from .database import engine, Base
from .sse import sse_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Search-Score-Send API")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    # Initialize SSE manager
    await sse_manager.start()
    logger.info("SSE manager started")

    yield

    # Shutdown
    logger.info("Shutting down Search-Score-Send API")
    await sse_manager.stop()


# Create FastAPI app
app = FastAPI(
    title="Search-Score-Send API",
    description="Automated recruitment workflow with AI-powered candidate scoring and personalized outreach",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jd.router, prefix="/api/jd", tags=["Job Description"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(scoring.router, prefix="/api/scoring", tags=["Scoring"])
app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
app.include_router(hitl.router, prefix="/api/hitl", tags=["HITL"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(data_monetization.router, prefix="/api/data", tags=["Data Monetization"])


@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "Search-Score-Send API",
        "version": "1.0.0",
        "status": "healthy",
        "features": {
            "hitl_enabled": settings.ENABLE_HITL,
            "sse_enabled": settings.ENABLE_SSE_PROGRESS,
            "audit_logging": settings.ENABLE_AUDIT_LOGGING,
        }
    }


@app.get("/api/health")
async def health():
    """Detailed health check"""
    try:
        # Check database
        from .database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "sse": "healthy" if sse_manager.is_running else "stopped",
        "settings": {
            "gdpr_enabled": settings.ANONYMIZATION_ENABLED,
            "data_retention_days": settings.DATA_RETENTION_DAYS,
        }
    }


@app.get("/api/progress/stream/{execution_id}")
async def stream_progress(execution_id: str):
    """
    Server-Sent Events endpoint for real-time progress updates

    Frontend connects to this endpoint and receives progress updates as they happen.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for this execution"""
        queue = await sse_manager.subscribe(execution_id)

        try:
            while True:
                message = await queue.get()

                # End of stream signal
                if message.get("type") == "close":
                    break

                # Format as SSE
                event_data = f"data: {json.dumps(message)}\n\n"
                yield event_data

        except Exception as e:
            logger.error(f"SSE stream error for {execution_id}: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            await sse_manager.unsubscribe(execution_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler with logging"""
    logger.warning(
        f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}"
    )
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "path": request.url.path,
    }


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {exc}",
        exc_info=True
    )
    return {
        "error": "Internal server error",
        "status_code": 500,
        "path": request.url.path,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
