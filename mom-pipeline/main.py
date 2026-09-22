import json
import os
import sys
from config.settings import settings
from utils.logger import logger, log_pipeline_separator
from utils.validation import validate_media_file
from core.audio_processor import AudioProcessor
from core.diarization import SpeakerDiarizer
from core.transcription import GroqTranscriptionEngine
from core.aligner import TranscriptAligner
from core.analytics import ConversationAnalytics
from core.summarizer import GroqMoMSummarizer
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env into os.environ
import static_ffmpeg
static_ffmpeg.add_paths()


def run_pipeline(file_path: str) -> dict:
    """
    Executes the end-to-end Voice MoM processing pipeline with dynamic
    speaker name resolution.

    Args:
        file_path (str): Path to the input audio/video recording.

    Returns:
        dict: Complete structured MoM result including transcript, analytics, and summary.
    """
    logger.info(f"Starting Voice MoM Pipeline for: {file_path}")

    # Step 1: Validate input file
    validate_media_file(file_path)

    # Step 2: Extract & normalize audio to 16kHz mono WAV
    audio_processor = AudioProcessor()
    wav_path = audio_processor.process_to_wav(file_path)

    # Step 3: Speaker Diarization via Deepgram Nova-3
    diarizer = SpeakerDiarizer()
    diarized_segments = diarizer.diarize(wav_path)

    # Step 4: Speech-to-Text Transcription via Groq Whisper
    transcriber = GroqTranscriptionEngine()
    transcription_result = transcriber.transcribe(wav_path)

    # Step 5: Align Transcript with Speaker Labels
    aligned_transcript = TranscriptAligner.align(
        diarized_segments,
        transcription_result["segments"]
    )

    # Step 6: Calculate Initial Speaker & Conversation Statistics
    analytics = ConversationAnalytics.compute_stats(aligned_transcript)

    # Step 7: Generate MoM & Extract Real Speaker Names via Groq LLM
    summarizer = GroqMoMSummarizer()
    summarizer_output = summarizer.generate_mom(aligned_transcript)

    # Unpack speaker map and structured MoM content
    speaker_map = summarizer_output.get("speaker_map", {})
    mom_data = summarizer_output.get("minutes_of_meeting", {})

    # Step 8: Re-map Generic Speaker Labels to Detected Real Names
    resolved_transcript = []
    for seg in aligned_transcript:
        raw_spk = seg["speaker"]
        resolved_spk = speaker_map.get(raw_spk, raw_spk)
        resolved_transcript.append({
            "start": seg["start"],
            "end": seg["end"],
            "speaker": resolved_spk,
            "text": seg["text"]
        })

    raw_speaker_stats = analytics.get("speaker_statistics", {})
    resolved_speaker_stats = {}
    for raw_spk, stats in raw_speaker_stats.items():
        resolved_spk = speaker_map.get(raw_spk, raw_spk)
        resolved_speaker_stats[resolved_spk] = stats

    # Step 9: Compile Final Output Structure
    output_result = {
        "metadata": {
            "source_file": os.path.basename(file_path),
            "primary_language": transcription_result["language"],
            "total_duration_seconds": analytics.get("total_meeting_duration_seconds", 0)
        },
        "speaker_statistics": resolved_speaker_stats,
        "minutes_of_meeting": mom_data,
        "transcript": resolved_transcript
    }

    # Step 10: Save output to JSON file
    file_stem = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(settings.OUTPUT_DIR, f"{file_stem}_mom.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_result, f, indent=2, ensure_ascii=False)

    logger.info(f"Pipeline completed successfully! Output saved to: {output_path}")

    # Log visual separator in execution log file
    log_pipeline_separator()

    # Clean up temporary normalized audio file
    if os.path.exists(wav_path) and wav_path != file_path:
        try:
            os.remove(wav_path)
            logger.info(f"Cleaned up temporary audio file: {wav_path}")
        except Exception as e:
            logger.warning(f"Could not remove temporary file {wav_path}: {e}")

    return output_result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_audio_or_video_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    result = run_pipeline(input_file)
    print("\n--- Generated Minutes of Meeting ---")
    print(json.dumps(result["minutes_of_meeting"], indent=2, ensure_ascii=False))