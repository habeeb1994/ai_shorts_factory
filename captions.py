from faster_whisper import WhisperModel
import os

class CaptionsAgent:
    def __init__(self):
        self.model = WhisperModel("base", device="cpu", compute_type="int8")

    def generate_srt(self, audio_path, output_path):
        # Enable word_timestamps to break the audio down word-by-word
        segments, _ = self.model.transcribe(audio_path, beam_size=5, word_timestamps=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            counter = 1
            for segment in segments:
                for word in segment.words:
                    f.write(f"{counter}\n")
                    f.write(f"{self._format_time(word.start)} --> {self._format_time(word.end)}\n")
                    f.write(f"{word.word.strip().upper()}\n\n")
                    counter += 1
        return os.path.abspath(output_path)

    def _format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds % 1) * 1000))
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"