import os
import requests
import replicate

class AIVideoScoutAgent:
    def __init__(self):
        # Automatically picks up REPLICATE_API_TOKEN from your environment
        pass

    def generate_clips(self, prompts, save_path):
        """
        Generates AI videos from text prompts using Replicate (e.g., Minimax model).
        prompts: A list of text descriptions.
        """
        paths = []
        for i, prompt in enumerate(prompts):
            print(f"🪄 Generating AI Video for prompt: '{prompt}'...")
            
            # Using Minimax Video-01 via Replicate (Replace with your preferred model)
            output_url = replicate.run(
                "minimax/video-01",
                input={
                    "prompt": prompt,
                    "prompt_optimizer": True
                }
            )
            
            # Replicate returns a URL to the finished MP4
            if output_url:
                file_path = os.path.join(save_path, f"ai_clip_{i}.mp4")
                print(f"⬇️ Downloading generated video to {file_path}")
                
                with requests.get(output_url, stream=True) as r:
                    with open(file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                paths.append(os.path.abspath(file_path))
                
        return paths