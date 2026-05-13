import os
import shutil
try:
    from gradio_client import Client, handle_file
except ImportError:
    Client = None

class AvatarAgent:
    def __init__(self):
        pass

    def animate_image(self, image_path, audio_path, output_path):
        if Client is None:
            print("❌ gradio_client is not installed. Please run: pip install gradio_client")
            return None
            
        colab_url = os.environ.get("COLAB_SADTALKER_URL")
        if not colab_url:
            print("❌ COLAB_SADTALKER_URL not found. Please set it in your .env file with your active Colab Gradio URL.")
            return None
            
        print(f"👤 Animating avatar using Google Colab ({colab_url})...")

        try:
            client = Client(colab_url)
            print("📤 Uploading files and starting generation (this may take a few minutes)...")
            
            # Pass inputs positionally to ensure they map correctly to the Gradio Interface
            result = client.predict(
                handle_file(image_path),
                handle_file(audio_path),
                api_name="/predict"
            )
            
            print(f"📥 Received response from Colab (type: {type(result).__name__})")
            
            # Extract the file path depending on what format the Gradio server returned
            result_path = None
            if isinstance(result, str):
                result_path = result
            elif isinstance(result, dict):
                result_path = result.get('video') or result.get('path') or result.get('name')
            elif isinstance(result, (list, tuple)) and len(result) > 0:
                if isinstance(result[0], dict):
                    result_path = result[0].get('video') or result[0].get('path') or result[0].get('name')
                elif isinstance(result[0], str):
                    result_path = result[0]

            if result_path and os.path.exists(result_path):
                shutil.copy(result_path, output_path)
                print("✅ Avatar animation complete using Colab!")
                return output_path
            else:
                print(f"❌ Colab returned empty or invalid output. Raw response: {result}")
                return None
        except Exception as e:
            print(f"❌ Error connecting to Colab API: {e}")
            return None