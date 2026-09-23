from utils.logger import logger

class TranscriptAligner:
    @staticmethod
    def align(diarized_segments: list[dict], transcript_segments: list[dict]) -> list[dict]:
        """
        Maps each transcribed text segment to the dominant speaker based on time overlaps
        and merges consecutive turns from the same speaker.

        Args:
            diarized_segments (list[dict]): Speaker segments with 'start', 'end', and 'speaker'.
            transcript_segments (list[dict]): Text segments with 'start', 'end', and 'text'.

        Returns:
            list[dict]: Chronological transcript aligned with speaker labels and timestamps.
        """
        logger.info("Aligning Whisper transcription segments with speaker diarization...")
        
        if not transcript_segments:
            logger.warning("Empty transcript segments passed for alignment.")
            return []

        if not diarized_segments:
            logger.warning("No diarization segments provided. Assigning all turns to 'Person 1'.")
            return [
                {
                    "speaker": "Person 1",
                    "start": t["start"],
                    "end": t["end"],
                    "text": t["text"].strip()
                }
                for t in transcript_segments if t.get("text")
            ]

        raw_aligned = []

        for t_seg in transcript_segments:
            t_start = t_seg["start"]
            t_end = t_seg["end"]
            text = t_seg.get("text", "").strip()

            if not text:
                continue

            best_speaker = None
            max_overlap = 0.0

            # 1. Calculate maximum time overlap
            for d_seg in diarized_segments:
                d_start = d_seg["start"]
                d_end = d_seg["end"]

                overlap_start = max(t_start, d_start)
                overlap_end = min(t_end, d_end)
                overlap = max(0.0, overlap_end - overlap_start)

                if overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker = d_seg["speaker"]

            # 2. Fallback: Find nearest speaker if segment falls in silence/gap
            if best_speaker is None:
                min_distance = float("inf")
                for d_seg in diarized_segments:
                    # Midpoint distance
                    t_mid = (t_start + t_end) / 2.0
                    d_mid = (d_seg["start"] + d_seg["end"]) / 2.0
                    dist = abs(t_mid - d_mid)
                    
                    if dist < min_distance:
                        min_distance = dist
                        best_speaker = d_seg["speaker"]

            raw_aligned.append({
                "speaker": best_speaker or "Person 1",
                "start": t_start,
                "end": t_end,
                "text": text
            })

        # 3. Merge consecutive turns by the same speaker
        merged_aligned = []
        for seg in raw_aligned:
            if merged_aligned and merged_aligned[-1]["speaker"] == seg["speaker"]:
                merged_aligned[-1]["end"] = seg["end"]
                merged_aligned[-1]["text"] += f" {seg['text']}"
            else:
                merged_aligned.append(seg)

        logger.info(f"Alignment completed. Processed into {len(merged_aligned)} dialogue turn(s).")
        return merged_aligned