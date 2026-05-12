import os
import shutil
try:
    from gradio_client import Client, handle_file
except ImportError:
    Client = None

class AvatarAgent:
    def __init__(self):
        # A list of public SadTalker APIs to try as fallbacks. The first is often the most stable.
        self.api_spaces = [
            "fffiloni/SadTalker",      # A popular and often stable alternative
            "vinthony/SadTalker",      # The original, keep it in case it comes back
            "gorkemgoknar/SadTalker",  # Another fallback
            "fiatrete/SadTalker"       # Additional fallback
        ]

    def animate_image(self, image_path, audio_path, output_path):
        if Client is None:
            print("❌ gradio_client is not installed. Please run: pip install gradio_client")
            return None
            
        print("👤 Animating avatar using Free Hugging Face APIs (SadTalker)...")

        for space in self.api_spaces:
            print(f"⏳ Trying API space: {space}...")
            try:
                # Connect to the public Space
                client = Client(space)
                
                # Pass the image and audio to the SadTalker interface
                result = client.predict(
                    source_image=handle_file(image_path),
                    driven_audio=handle_file(audio_path),
                    preprocess="crop",
                    is_still_mode=True,
                    enhancer="gfpgan",
                    batch_size=1,
                    size=256,
                    pose_style=0,
                    facerender="facevid2vid",
                    exp_scale=1,
                    use_ref_video=False,
                    ref_video=None,
                    ref_info=None,
                    use_idle_mode=False,
                    length_of_audio=0,
                    use_blink=True,
                    api_name="/submit"
                )
                
                if result and os.path.exists(result):
                    shutil.copy(result, output_path)
                    print(f"✅ Avatar animation complete using '{space}'!")
                    return output_path
            except Exception as e:
                print(f"⚠️ API space '{space}' failed: {e}")
                print("➡️ Trying next available API...")
                continue # Move to the next API in the list

        # If the loop completes without returning, all APIs failed.
        print(f"❌ All free APIs failed. The servers might be busy or down.")
        print("💡 To guarantee zero downtime, consider running an open-source model like Wav2Lip locally.")
        return None