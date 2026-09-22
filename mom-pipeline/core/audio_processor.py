import av
import os
from utils.logger import logger

class AudioProcessor:
    @staticmethod
    def process_to_wav(input_path: str) -> str:
        """
        Converts input audio/video file to 16kHz mono WAV using PyAV (no system FFmpeg needed).
        """
        logger.info(f"Processing media with PyAV: {input_path}")
        output_wav = os.path.splitext(input_path)[0] + "_processed.wav"

        container = av.open(input_path)
        audio_stream = next((s for s in container.streams if s.type == 'audio'), None)

        if not audio_stream:
            raise ValueError("No audio track found in the provided media file.")

        # Resample audio to 16kHz Mono PCM 16-bit
        resampler = av.AudioResampler(format='s16', layout='mono', rate=16000)
        
        out_container = av.open(output_wav, mode='w')
        out_stream = out_container.add_stream('pcm_s16le', rate=16000)

        for frame in container.decode(audio_stream):
            resampled_frames = resampler.resample(frame)
            for r_frame in resampled_frames:
                for packet in out_stream.encode(r_frame):
                    out_container.mux(packet)

        # Flush buffer
        for packet in out_stream.encode():
            out_container.mux(packet)

        out_container.close()
        container.close()

        logger.info(f"Audio extraction complete: {output_wav}")
        return output_wav