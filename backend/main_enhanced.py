"""
Wiki Quiz Generator - Enterprise Production Server v2.0
Features: Rate Limiting, Caching, Monitoring, Security, Enhanced Error Handling
"""
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uuid

# Import our enhanced modules
from config import settings
from logger import setup_logging, get_logger
from middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from models import (
    QuizGenerationRequest,
    QuizResponse,
    QuizQuestion,
    HealthCheck,
    ErrorResponse,
)
from services import (
    wikipedia_service,
    ai_service,
    WikipediaException,
    AIServiceException,
    ServiceException,
)

# Setup logging
setup_logging(log_level=settings.log_level, json_format=False)
logger = get_logger(__name__)

# Application start time for uptime tracking
app_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - handles startup and shutdown
    """
    # Startup
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"📊 Environment: {'DEBUG' if settings.debug else 'PRODUCTION'}")
    logger.info(f"🔑 API Key configured: {bool(settings.google_api_key)}")
    logger.info(f"⚡ Rate limiting: {'ENABLED' if settings.rate_limit_enabled else 'DISABLED'}")
    logger.info(f"💾 Caching: {'ENABLED' if settings.redis_enabled else 'DISABLED'}")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down application")


# Initialize FastAPI with enhanced configuration
app = FastAPI(
    title=settings.app_name,
    description="Enterprise-grade AI-powered quiz generator using Wikipedia and Google Gemini AI",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add middleware (order matters!)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

if settings.rate_limit_enabled:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_window=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window,
    )

# CORS - Configure based on environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)


# Exception Handlers
@app.exception_handler(WikipediaException)
async def wikipedia_exception_handler(request: Request, exc: WikipediaException):
    """Handle Wikipedia scraping errors"""
    logger.error(f"Wikipedia error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ErrorResponse(
            error="WikipediaError",
            message="Failed to fetch Wikipedia content. Please check the topic and try again.",
            details={"original_error": str(exc)},
            path=str(request.url.path),
        ).model_dump(),
    )


@app.exception_handler(AIServiceException)
async def ai_exception_handler(request: Request, exc: AIServiceException):
    """Handle AI service errors"""
    logger.error(f"AI service error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ErrorResponse(
            error="AIServiceError",
            message="AI service temporarily unavailable. Please try again in a moment.",
            details={"original_error": str(exc)},
            path=str(request.url.path),
        ).model_dump(),
    )


@app.exception_handler(ServiceException)
async def service_exception_handler(request: Request, exc: ServiceException):
    """Handle general service errors"""
    logger.error(f"Service error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ErrorResponse(
            error="ServiceError",
            message="Service temporarily unavailable. Circuit breaker may be open.",
            details={"original_error": str(exc)},
            path=str(request.url.path),
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred. Please try again later.",
            details={"type": type(exc).__name__} if settings.debug else None,
            path=str(request.url.path),
        ).model_dump(),
    )


# API Routes
@app.get(
    "/",
    response_model=dict,
    summary="Root endpoint",
    description="Basic health check endpoint",
    tags=["Health"],
)
async def root():
    """Root endpoint with basic info"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get(
    "/health",
    response_model=HealthCheck,
    summary="Detailed health check",
    description="Comprehensive health check with service status",
    tags=["Health"],
)
async def health_check():
    """
    Comprehensive health check endpoint
    Checks all dependent services
    """
    checks = {
        "api": True,
        "ai_configured": bool(settings.google_api_key),
        "wikipedia": True,
    }
    
    # Test Wikipedia service
    try:
        # Quick test - just check if we can make a request
        import requests
        response = requests.get("https://en.wikipedia.org", timeout=5)
        checks["wikipedia"] = response.status_code == 200
    except Exception as e:
        logger.warning(f"Wikipedia health check failed: {e}")
        checks["wikipedia"] = False
    
    # Determine overall status
    if all(checks.values()):
        overall_status = "healthy"
    elif checks["api"]:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"
    
    uptime = time.time() - app_start_time
    
    return HealthCheck(
        status=overall_status,
        version=settings.app_version,
        checks=checks,
        uptime_seconds=uptime,
    )


@app.post(
    "/generate-quiz",
    response_model=QuizResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate quiz from Wikipedia",
    description="Generate AI-powered quiz questions from any Wikipedia topic",
    tags=["Quiz"],
    responses={
        200: {"description": "Quiz generated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def generate_quiz(request: QuizGenerationRequest):
    """
    Generate a quiz from Wikipedia content using Google Gemini AI
    
    - **topic**: Wikipedia article title or URL
    - **num_questions**: Number of questions (3-20)
    - **difficulty**: easy, medium, or hard
    
    Returns a quiz with multiple-choice questions
    """
    logger.info(
        f"Quiz generation requested: {request.topic} "
        f"({request.num_questions} questions, {request.difficulty})"
    )
    
    try:
        # Step 1: Scrape Wikipedia content
        logger.debug("Fetching Wikipedia content...")
        content = wikipedia_service.get_article_summary(
            request.topic,
            max_length=3000
        )
        
        # Step 2: Generate quiz with AI
        logger.debug("Generating quiz with AI...")
        questions = ai_service.generate_quiz(
            content=content,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            topic=request.topic,
        )
        
        # Step 3: Create response
        quiz_id = f"quiz_{uuid.uuid4().hex[:12]}"
        estimated_duration = request.num_questions * 2  # 2 minutes per question
        
        response = QuizResponse(
            topic=request.topic,
            questions=questions,
            total_questions=len(questions),
            difficulty=request.difficulty,
            quiz_id=quiz_id,
            estimated_duration_minutes=estimated_duration,
        )
        
        logger.info(
            f"Quiz generated successfully: {quiz_id} "
            f"({len(questions)} questions)"
        )
        
        return response
        
    except WikipediaException as e:
        logger.error(f"Wikipedia error for topic '{request.topic}': {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "WikipediaError",
                "message": "Failed to fetch Wikipedia content. Please verify the topic exists.",
                "topic": request.topic,
            },
        )
    
    except AIServiceException as e:
        logger.error(f"AI generation error for topic '{request.topic}': {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "AIServiceError",
                "message": "Failed to generate quiz. AI service may be temporarily unavailable.",
            },
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error generating quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalError",
                "message": "An unexpected error occurred. Please try again.",
            },
        )


@app.get(
    "/metrics",
    summary="Prometheus metrics",
    description="Application metrics in Prometheus format",
    tags=["Monitoring"],
    include_in_schema=settings.enable_metrics,
)
async def metrics():
    """
    Expose Prometheus metrics
    """
    # In production, integrate with prometheus_client
    return {
        "uptime_seconds": time.time() - app_start_time,
        "version": settings.app_version,
    }


# Development server runner
if __name__ == "__main__":
    import uvicorn
    
    logger.info("🔥 Starting development server...")
    logger.info(f"📝 API Documentation: http://{settings.host}:{settings.port}/docs")
    logger.info(f"🔍 Health Check: http://{settings.host}:{settings.port}/health")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
