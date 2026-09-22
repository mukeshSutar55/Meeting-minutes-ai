from utils.logger import logger

class TranscriptAligner:
    @staticmethod
    def align(diarized_segments: list[dict], transcript_segments: list[dict]) -> list[dict]:
        """
        Maps each transcribed text segment to the dominant speaker based on time overlaps.

        Args:
            diarized_segments (list[dict]): Speaker segments with 'start', 'end', and 'speaker'.
            transcript_segments (list[dict]): Text segments with 'start', 'end', and 'text'.

        Returns:
            list[dict]: Chronological transcript aligned with speaker labels and timestamps.
        """
        logger.info("Aligning Whisper transcription segments with PyAnnote speaker diarization...")
        aligned_transcript = []

        for t_seg in transcript_segments:
            t_start = t_seg["start"]
            t_end = t_seg["end"]
            text = t_seg["text"]

            if not text:
                continue

            best_speaker = "Person Unknown"
            max_overlap = 0.0

            # Find speaker segment with the maximum temporal overlap
            for d_seg in diarized_segments:
                d_start = d_seg["start"]
                d_end = d_seg["end"]

                overlap_start = max(t_start, d_start)
                overlap_end = min(t_end, d_end)
                overlap = max(0.0, overlap_end - overlap_start)

                if overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker = d_seg["speaker"]

            aligned_transcript.append({
                "speaker": best_speaker,
                "start": t_start,
                "end": t_end,
                "text": text
            })

        logger.info(f"Alignment completed for {len(aligned_transcript)} segment(s).")
        return aligned_transcript