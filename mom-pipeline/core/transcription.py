import os
from groq import Groq
from config.settings import settings
from utils.logger import logger

class GroqTranscriptionEngine:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.error("GROQ_API_KEY is missing in environment or settings.")
            raise ValueError(
                "GROQ_API_KEY is required for Groq Whisper transcription. "
                "Please set GROQ_API_KEY in your .env file or environment variables."
            )
        
        logger.info("Initializing Groq API client for speech transcription...")
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def transcribe(self, audio_path: str, prompt: str = "") -> dict:
        """
        Transcribes audio using Groq API's whisper-large-v3 model with segment timestamps.
        
        Args:
            audio_path (str): Path to normalized 16kHz WAV audio file.
            prompt (str, optional): Prompt hint for terminology or language switching context.
            
        Returns:
            dict: Structured transcript with text, detected language, and timed segments.
        """
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found at {audio_path}")
            raise FileNotFoundError(f"Audio file not found at {audio_path}")

        logger.info(f"Sending audio to Groq Whisper ({settings.GROQ_WHISPER_MODEL}): {os.path.basename(audio_path)}")

        default_prompt = (
            prompt if prompt else 
            "Multilingual transcript featuring English, Hindi, and Odia conversations."
        )

        try:
            with open(audio_path, "rb") as file_stream:
                response = self.client.audio.transcriptions.create(
                    file=(os.path.basename(audio_path), file_stream.read()),
                    model=settings.GROQ_WHISPER_MODEL,
                    prompt=default_prompt,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )

            # Convert response to dictionary
            response_dict = response.model_dump()
            
            raw_segments = response_dict.get("segments", [])
            parsed_segments = []

            for seg in raw_segments:
                parsed_segments.append({
                    "start": round(seg.get("start", 0.0), 2),
                    "end": round(seg.get("end", 0.0), 2),
                    "text": seg.get("text", "").strip()
                })

            detected_language = response_dict.get("language", "unknown")
            full_text = response_dict.get("text", "").strip()

            logger.info(f"Transcription complete. Language detected: {detected_language}. Segments: {len(parsed_segments)}")

            return {
                "text": full_text,
                "language": detected_language,
                "segments": parsed_segments
            }

        except Exception as e:
            logger.error(f"Groq transcription API request failed: {str(e)}")
            raise RuntimeError(f"Groq transcription failed: {str(e)}")