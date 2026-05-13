import edge_tts
import asyncio
import os
import sys

# Fix for Windows-specific asyncio connection lost error
if sys.platform == 'win32':
    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport
        _original_call_connection_lost = _ProactorBasePipeTransport._call_connection_lost

        def _patched_call_connection_lost(self, exc):
            try:
                _original_call_connection_lost(self, exc)
            except ConnectionResetError:
                pass
        _ProactorBasePipeTransport._call_connection_lost = _patched_call_connection_lost
    except Exception:
        pass

class NarratorAgent:
    def __init__(self, voice="en-US-AndrewNeural"):
        # Andrew is currently one of the best for high-retention "Bro-science/Wealth" content
        self.voice = voice 
        
    def save_speech(self, text, output_path):
        print(f"🎙️ Narrator: Synthesizing voice using {self.voice}...")
        asyncio.run(self._generate(text, output_path))
        return os.path.abspath(output_path)

    async def _generate(self, text, output_path):
        # rate="+5%": Makes the speaker sound excited and saves time for more content.
        # pitch="+0Hz": Keeps the voice natural. Change to -2Hz for a deeper "alpha" tone.
        # volume="+0%": Ensures we aren't clipping.
        
        communicate = edge_tts.Communicate(
            text, 
            self.voice, 
            rate="+15%",   # Faster pacing is better for Shorts
            pitch="+0Hz" 
        )
        
        await communicate.save(output_path)