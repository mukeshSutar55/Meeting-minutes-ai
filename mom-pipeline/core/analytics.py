from utils.logger import logger

class ConversationAnalytics:
    @staticmethod
    def compute_stats(aligned_transcript: list[dict]) -> dict:
        """
        Calculates speaker statistics including total speaking time, segment count, 
        and speaking time percentages.

        Args:
            aligned_transcript (list[dict]): Aligned transcript containing speaker, start, end, and text.

        Returns:
            dict: Summary statistics per speaker and total meeting duration.
        """
        logger.info("Computing speaker conversation statistics...")
        stats = {}
        total_duration = 0.0

        for segment in aligned_transcript:
            speaker = segment["speaker"]
            duration = max(0.0, segment["end"] - segment["start"])
            total_duration += duration

            if speaker not in stats:
                stats[speaker] = {
                    "total_speaking_time_seconds": 0.0,
                    "speaking_segments_count": 0,
                    "speaking_percentage": 0.0
                }

            stats[speaker]["total_speaking_time_seconds"] += duration
            stats[speaker]["speaking_segments_count"] += 1

        # Calculate proportions and round numerical values
        if total_duration > 0:
            for speaker in stats:
                speaking_sec = stats[speaker]["total_speaking_time_seconds"]
                stats[speaker]["total_speaking_time_seconds"] = round(speaking_sec, 2)
                stats[speaker]["speaking_percentage"] = round((speaking_sec / total_duration) * 100, 2)

        analytics_result = {
            "total_meeting_duration_seconds": round(total_duration, 2),
            "speaker_statistics": stats
        }

        logger.info(f"Analytics calculated across {len(stats)} speaker(s). Total duration: {analytics_result['total_meeting_duration_seconds']}s")
        return analytics_result