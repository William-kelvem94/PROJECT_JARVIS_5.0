"""
Main FastAPI Application Entry Point
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
import logging

from app.core.config import settings
from app.core.logger import setup_logger, get_logger
from app.core.database import init_db
from app.core.redis_client import init_redis, close_redis
from app.api import api_router
from app.core.exceptions import JarvisException

# Setup logging
setup_logger()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - handles startup and shutdown
    """
    logger.info("Starting Jarvis AI Assistant...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize Redis
    await init_redis()
    logger.info("Redis initialized")
    
    # Initialize Ollama connection
    from app.services.llm_service import LLMService
    llm_service = LLMService()
    await llm_service.initialize()
    logger.info("LLM Service initialized")
    
    # Load plugins
    from app.core.plugin_manager import PluginManager
    plugin_manager = PluginManager()
    await plugin_manager.load_all_plugins()
    logger.info(f"Loaded {len(plugin_manager.plugins)} plugins")
    
    logger.info("Jarvis AI Assistant started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Jarvis AI Assistant...")
    await close_redis()
    await plugin_manager.unload_all_plugins()
    logger.info("Jarvis AI Assistant stopped")


# Create FastAPI application
app = FastAPI(
    title="Jarvis AI Assistant API",
    description="Advanced AI Conversational Assistant with Plugin Architecture",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(JarvisException)
async def jarvis_exception_handler(request: Request, exc: JarvisException):
    logger.error(f"Jarvis exception: {exc.message}", exc_info=exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "code": "INTERNAL_ERROR"}
    )


# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "version": "3.0.0",
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Jarvis AI Assistant API",
        "version": "3.0.0",
        "docs": "/api/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

