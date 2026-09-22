import os
from deepgram import DeepgramClient
from config.settings import settings
from utils.logger import logger

class SpeakerDiarizer:
    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY or os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            logger.error("DEEPGRAM_API_KEY is missing in settings/environment.")
            raise ValueError("DEEPGRAM_API_KEY is required for Deepgram speaker diarization.")
        
        logger.info("Initializing Deepgram Client...")
        self.client = DeepgramClient(api_key=self.api_key)

    def diarize(self, audio_path: str, num_speakers: int = None) -> list[dict]:
        """
        Runs speaker diarization via Deepgram API and returns timed speaker segments.
        """
        logger.info(f"Sending audio to Deepgram API: {audio_path}")

        try:
            with open(audio_path, "rb") as file_stream:
                buffer_data = file_stream.read()

            options = {
                "model": "nova-3",
                "diarize": True,
                "utterances": True,
                "punctuate": True
            }

            # Handle method structure across SDK v3/v4/v5
            if hasattr(self.client.listen, "v1"):
                # v5+ modern SDK structure
                response = self.client.listen.v1.media.transcribe_file(
                    request=buffer_data,
                    **options
                )
            elif hasattr(self.client.listen, "prerecorded"):
                # v3/v4 SDK structure
                response = self.client.listen.prerecorded.v1.transcribe_file(
                    {"buffer": buffer_data, "mimetype": "audio/wav"},
                    options
                )
            else:
                # v3 legacy fallback
                response = self.client.listen.rest.v("1").transcribe_file(
                    {"buffer": buffer_data, "mimetype": "audio/wav"},
                    options
                )

            results = response.results
            diarized_segments = []
            speaker_mapping = {}
            speaker_counter = 1

            # Extract utterances from response results
            utterances = getattr(results, "utterances", None)

            if utterances:
                for utt in utterances:
                    raw_spk = f"speaker_{utt.speaker}"
                    if raw_spk not in speaker_mapping:
                        speaker_mapping[raw_spk] = f"Person {speaker_counter}"
                        speaker_counter += 1

                    diarized_segments.append({
                        "start": round(utt.start, 2),
                        "end": round(utt.end, 2),
                        "speaker": speaker_mapping[raw_spk]
                    })
            else:
                # Fallback: Group word-level timestamps by speaker
                words = results.channels[0].alternatives[0].words
                if not words:
                    return []

                current_spk = words[0].speaker
                seg_start = words[0].start
                seg_end = words[0].end

                for w in words:
                    if w.speaker != current_spk:
                        raw_spk = f"speaker_{current_spk}"
                        if raw_spk not in speaker_mapping:
                            speaker_mapping[raw_spk] = f"Person {speaker_counter}"
                            speaker_counter += 1

                        diarized_segments.append({
                            "start": round(seg_start, 2),
                            "end": round(seg_end, 2),
                            "speaker": speaker_mapping[raw_spk]
                        })
                        current_spk = w.speaker
                        seg_start = w.start

                    seg_end = w.end

                raw_spk = f"speaker_{current_spk}"
                if raw_spk not in speaker_mapping:
                    speaker_mapping[raw_spk] = f"Person {speaker_counter}"

                diarized_segments.append({
                    "start": round(seg_start, 2),
                    "end": round(seg_end, 2),
                    "speaker": speaker_mapping[raw_spk]
                })

            logger.info(f"Deepgram Diarization finished. Detected {len(speaker_mapping)} speaker(s).")
            return diarized_segments

        except Exception as e:
            logger.error(f"Deepgram diarization call failed: {str(e)}")
            raise RuntimeError(f"Deepgram diarization failed: {str(e)}")