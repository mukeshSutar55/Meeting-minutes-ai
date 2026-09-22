from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from api.routes import router
from utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code executed on application startup
    logger.info("Initializing Multilingual Voice MoM FastAPI Server...")
    logger.info(f"Groq API Key Configured: {bool(settings.GROQ_API_KEY)}")
    logger.info(f"Deepgram API Key Configured: {bool(settings.DEEPGRAM_API_KEY)}")
    yield
    # Code executed on application shutdown
    logger.info("Shutting down Multilingual Voice MoM FastAPI Server...")


app = FastAPI(
    title="Multilingual Voice MoM API",
    description=(
        "Production REST API for speech-to-text, speaker diarization, "
        "and structured Minutes of Meeting (MoM) generation."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routes
app.include_router(router, prefix="/mom/v1")


if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )