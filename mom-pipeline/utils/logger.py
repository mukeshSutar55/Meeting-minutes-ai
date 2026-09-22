import sys
from pathlib import Path
from loguru import logger

# Base directory setup for logs
LOG_DIR = Path(__file__).resolve().parent.parent / "storage" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Remove default logger configuration
logger.remove()

# Console logging
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# File logging
logger.add(
    LOG_DIR / "pipeline_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}",
    level="DEBUG",
    rotation="00:00",
    retention="10 days",
    compression="zip",
    encoding="utf-8",
)


def log_pipeline_separator():
    """Logs a prominent separator line to mark the completion of a pipeline run."""
    separator = "=" * 80
    logger.info(f"\n{separator}\nPIPELINE EXECUTION COMPLETED SUCCESSFULLY\n{separator}\n")


__all__ = ["logger", "log_pipeline_separator"]