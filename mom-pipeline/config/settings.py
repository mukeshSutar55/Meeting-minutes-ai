import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "storage" / "uploads"
    OUTPUT_DIR: Path = BASE_DIR / "storage" / "outputs"

    # API Configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Device Configuration (Added this line to fix the error)
    DEVICE: str = "cpu"  # Change to "cuda" if running on a GPU machine

    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
    

    # Groq Models
    GROQ_WHISPER_MODEL: str = "whisper-large-v3"        # Speech-to-Text via Groq
    GROQ_LLM_MODEL: str = "openai/gpt-oss-20b"    # MoM Generation via Groq

    # Target Languages
    SUPPORTED_LANGUAGES: list[str] = ["en", "hi", "or"]  # English, Hindi, Odia

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate settings and ensure storage directories exist
settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)