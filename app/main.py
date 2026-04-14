from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from app.api.routes import pokemons, favorites
from app.core.config import settings
from app.utils.logger import setup_logger
from app.core.rate_limit import limiter
from app.core.database import engine, Base

# Setup logger
logger = setup_logger()

# Create database tables (apenas se não existirem)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified successfully")
except Exception as e:
    logger.warning(f"Could not create database tables: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="Pokemon API",
    description="API RESTful para consulta de Pokemons com cache, rate limiting, autenticação API Key e CRUD completo com banco de dados",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limit handlers
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include routers
app.include_router(pokemons.router, prefix="/api/v1", tags=["pokemons"])
app.include_router(favorites.router, prefix="/api/v1", tags=["favorites"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Pokemon API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "auth_required": "Use X-API-Key header with valid API key",
        "public_endpoints": "/api/v1/public/pokemons",
        "crud_endpoints": "/api/v1/favorites",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pokemon-api"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )
