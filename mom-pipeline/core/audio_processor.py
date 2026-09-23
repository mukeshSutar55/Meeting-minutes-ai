import os
import av
from utils.logger import logger

class AudioProcessor:
    @staticmethod
    def process_to_mp3(input_path: str) -> str:
        """
        Converts input audio/video file to 16kHz mono MP3 (64kbps) using PyAV.
        Slashes file size by ~75% compared to raw WAV for ultra-fast API uploads.
        """
        logger.info(f"Processing media with PyAV: {input_path}")
        output_mp3 = os.path.splitext(input_path)[0] + "_processed.mp3"

        container = None
        out_container = None

        try:
            container = av.open(input_path)
            audio_stream = next((s for s in container.streams if s.type == 'audio'), None)

            if not audio_stream:
                raise ValueError(f"No audio track found in the provided media file: {input_path}")

            # Resample audio to 16kHz Mono FLTP (standard for libmp3lame)
            resampler = av.AudioResampler(format='fltp', layout='mono', rate=16000)

            out_container = av.open(output_mp3, mode='w')
            out_stream = out_container.add_stream('libmp3lame', rate=16000)
            out_stream.bit_rate = 64000  # 64 kbps mono - ideal for speech recognition

            # Process input audio frames
            for frame in container.decode(audio_stream):
                resampled_frames = resampler.resample(frame)
                if resampled_frames:
                    for r_frame in resampled_frames:
                        for packet in out_stream.encode(r_frame):
                            out_container.mux(packet)

            # Flush resampler buffer
            resampled_frames = resampler.resample(None)
            if resampled_frames:
                for r_frame in resampled_frames:
                    for packet in out_stream.encode(r_frame):
                        out_container.mux(packet)

            # Flush encoder buffer
            for packet in out_stream.encode():
                out_container.mux(packet)

            logger.info(f"Audio extraction complete: {output_mp3}")
            return output_mp3

        except Exception as e:
            logger.error(f"Error processing audio file '{input_path}': {str(e)}")
            # Cleanup partially created file on failure
            if os.path.exists(output_mp3):
                try:
                    os.remove(output_mp3)
                except OSError:
                    pass
            raise RuntimeError(f"Audio processing failed: {str(e)}") from e

        finally:
            if out_container:
                out_container.close()
            if container:
                container.close()

    # Backwards-compatibility alias for legacy code calling process_to_wav
    process_to_wav = process_to_mp3