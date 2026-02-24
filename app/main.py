from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.routes import router
from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.heroes import router as heroes_router
from app.api.v1.players import router as players_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered coaching system for Mobile Legends Bang Bang",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, tags=["coaching"])
app.include_router(auth_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(heroes_router, prefix="/api/v1")
app.include_router(players_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Create database tables (for SQLite dev; production uses Alembic migrations)
    from app.core.database import engine, Base
    from sqlalchemy import text
    import app.models.db  # noqa: F401 — registers all models with Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Add mlbb_username column if it doesn't exist (migration for existing DBs)
        try:
            await conn.execute(text(
                "ALTER TABLE users ADD COLUMN mlbb_username VARCHAR"
            ))
            logger.info("Added mlbb_username column to users table")
        except Exception:
            pass  # Column already exists
    logger.info("Database tables ready")

    # Check LLM providers
    from app.services.llm.provider import LLMFactory
    available_providers = LLMFactory.list_available_providers()
    logger.info(f"Available LLM providers: {[p.value for p in available_providers]}")

    if not available_providers:
        logger.warning("No LLM providers configured! Please set API keys in .env")

    # Check vector store
    if not settings.PINECONE_API_KEY:
        logger.warning("Pinecone API key not configured!")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to MLBB AI Coach API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
