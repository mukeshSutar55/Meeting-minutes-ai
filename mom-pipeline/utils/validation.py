import os
import ffmpeg
from fastapi import HTTPException, status
from utils.logger import logger

# Supported input file extensions
ALLOWED_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg",
    ".mp4", ".mkv", ".avi", ".mov", ".webm"
}

def validate_media_file(file_path: str) -> bool:
    """
    Validates file existence, extension, and checks media integrity using FFmpeg.
    
    Raises:
        HTTPException: If file is missing, unsupported, or corrupted.
    Returns:
        bool: True if the file passes all validation checks.
    """
    logger.info(f"Validating media file: {file_path}")

    # Check 1: Existence
    if not os.path.exists(file_path):
        logger.error(f"Validation failed: File not found at {file_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uploaded file not found on disk."
        )

    # Check 2: Allowed extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        logger.error(f"Validation failed: Extension '{ext}' not in allowed set {ALLOWED_EXTENSIONS}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: '{ext}'. Allowed formats: {sorted(list(ALLOWED_EXTENSIONS))}"
        )

    # Check 3: Integrity probe using FFmpeg
    try:
        probe = ffmpeg.probe(file_path)
        audio_streams = [
            stream for stream in probe.get("streams", [])
            if stream.get("codec_type") == "audio"
        ]
        
        if not audio_streams:
            logger.error(f"Validation failed: No valid audio streams found in {file_path}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The provided file contains no valid audio stream."
            )

        logger.info(f"File validation successful. Found {len(audio_streams)} audio stream(s).")
        return True

    except ffmpeg.Error as e:
        stderr_msg = e.stderr.decode("utf-8") if e.stderr else str(e)
        logger.error(f"FFmpeg probe error on {file_path}: {stderr_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Corrupted or unreadable media file. FFmpeg probe failed: {stderr_msg[:200]}"
        )