"""
FastAPI application entry point for flashcard learning system.
"""

import logging
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import time

from .storage.file_storage import FileStorageService
from .api.flashcard_routes import router as flashcard_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Flashcard Learning API",
    description="API for managing flashcards and study sessions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(flashcard_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", 
        "http://127.0.0.1:8080",
        "http://localhost:3000",  # For development
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# Initialize storage service
data_dir = Path(__file__).parent.parent / "data"
storage = FileStorageService(str(data_dir))


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring."""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response time
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} in {process_time:.4f}s")
    
    return response


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Flashcard Learning API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health():
    """Comprehensive health check for monitoring."""
    try:
        storage_health = storage.health_check()
        return {
            "status": "healthy",
            "version": "1.0.0",
            "storage": storage_health,
            "endpoints": {
                "flashcards": "/api/flashcards",
                "study": "/api/study"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "version": "1.0.0",
            "error": str(e)
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)