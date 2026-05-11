import os
import time
import shutil
import sys
import json
import random
from researcher import ResearcherAgent
from ai_scout import AIVideoScoutAgent
from scout import ScoutAgent
from narrator import NarratorAgent
from captions import CaptionsAgent
from editor import EditorAgent
from manager import ManagerAgent
from trend_agent import TrendAgent
from dotenv import load_dotenv

class AIVideoFactory:
    def __init__(self, scout_method="ai"):
        # Configuration
        self.temp_dir = "assets/temp_production"
        self.output_dir = "exports"
        self._setup_folders()
        self.scout_method = scout_method

        # Load environment variables from .env file
        load_dotenv()

        # Initialize Agents
        print("🤖 Initializing Factory Agents...")
        self.researcher = ResearcherAgent()
        
        if self.scout_method == "ai":
            replicate_key = os.environ.get("REPLICATE_API_TOKEN")
            if not replicate_key:
                raise ValueError("REPLICATE_API_TOKEN is missing. Please set it in your .env file.")
            self.scout = AIVideoScoutAgent()
        else:
            pexels_key = os.environ.get("PEXELS_API_KEY")
            if not pexels_key:
                raise ValueError("PEXELS_API_KEY is missing. Please set it in your .env file.")
            self.scout = ScoutAgent(api_key=pexels_key)
            
        self.narrator = NarratorAgent()
        self.captions = CaptionsAgent()
        self.editor = EditorAgent()
        self.manager = ManagerAgent(secrets_file='client_secrets.json')
        self.trend_agent = TrendAgent()

    def _setup_folders(self):
        """Ensures the workspace is ready."""
        for folder in [self.temp_dir, self.output_dir, "assets/raw_clips", "assets/bg_music"]:
            if not os.path.exists(folder):
                os.makedirs(folder)
    def wait_for_user(self, step_name):
        """Pauses the script and waits for user confirmation."""
        print(f"\n--- ⏸️  PAUSE: {step_name} complete ---")
        user_input = input("👉 Press ENTER to proceed, or type 'exit' to stop: ").strip().lower()
        if user_input == 'exit':
            print("🛑 Shutting down factory...")
            sys.exit()
    def cleanup(self):
        """Cleans up temporary assets to save disk space."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        self._setup_folders()
        print("🧹 Workspace cleaned.")

    def produce_video(self, topic, start_step=1, schedule_minutes=0):
        start_time = time.time()
        print(f"\n--- 🚀 STARTING PRODUCTION: {topic} ---")
        
        try:
            script_file = os.path.join(self.temp_dir, "script.txt")
            content_file = os.path.join(self.temp_dir, "content.json")
            
            # 1. RESEARCH
            if start_step <= 1:
                content = self.researcher.generate_viral_atoms(topic, script_file, self.scout_method)
                with open(content_file, 'w', encoding='utf-8') as f:
                    json.dump(content, f)
                print(f"✅ Script Ready. Title: {content['title']}")
            else:
                with open(content_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    
            # 2. NARRATION
            audio_file = os.path.join(self.temp_dir, "voice.mp3")
            if start_step <= 2:
                self.narrator.save_speech(content['script'], audio_file)
                print("✅ Voiceover Synthesized.")
                
            # 3. SCOUTING
            if start_step <= 3:
                if self.scout_method == "ai":
                    prompts = content.get('video_prompts', content.get('keywords', ['Cinematic shot of AI']))
                    downloaded_clips = self.scout.generate_clips(prompts, "assets/raw_clips")
                else:
                    keywords = content.get('keywords', content.get('tags', ['AI', 'technology', 'wealth']))
                    links = self.scout.find_high_energy_clips(keywords, count=2)
                    downloaded_clips = self.scout.download_clips(links, "assets/raw_clips")
                print(f"✅ Downloaded {len(downloaded_clips)} assets.")
            else:
                downloaded_clips = [os.path.abspath(os.path.join("assets/raw_clips", f)) for f in os.listdir("assets/raw_clips") if f.endswith('.mp4')]
                
            # 4. CAPTIONS
            srt_file = os.path.join(self.temp_dir, "captions.srt")
            if start_step <= 4:
                self.captions.generate_srt(audio_file, srt_file)
                print("✅ Captions Synced (Yellow Safe-Zone Style).")
                self.wait_for_user("CAPTIONS")
                
            # 5. EDITING
            video_path_file = os.path.join(self.temp_dir, "final_video_path.txt")
            if start_step <= 5:
                # Randomly select background music from the library
                bg_music_dir = "assets/bg_music"
                bg_music_file = None
                if os.path.exists(bg_music_dir):
                    music_files = [f for f in os.listdir(bg_music_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
                    if music_files:
                        bg_music_file = os.path.abspath(os.path.join(bg_music_dir, random.choice(music_files)))
                        
                final_video = os.path.join(self.output_dir, f"short_{int(time.time())}.mp4")
                self.editor.assemble(
                    audio=audio_file,
                    video_list=downloaded_clips,
                    subtitles=srt_file,
                    output=final_video,
                    bg_music=bg_music_file
                )
                with open(video_path_file, "w") as f:
                    f.write(final_video)
                print(f"✅ Video Rendered: {final_video}")
                self.wait_for_user("EDITING (Final Quality Control)")
            else:
                with open(video_path_file, "r") as f:
                    final_video = f.read().strip()

            # 6. MANAGEMENT (UPLOAD)
            if start_step <= 6:
                metadata = {
                    "title": content['title'],
                    "description": f"{content['script'][:150]}... #wealth #ai #productivity",
                    "tags": content['tags'],
                    "cta_link": "Master AI Productivity here: https://yourlink.com"
                }
                
                video_id = self.manager.deploy_short(final_video, metadata, schedule_minutes)
                
                if video_id:
                    duration = round((time.time() - start_time) / 60, 2)
                    print(f"🏁 PIPELINE COMPLETE in {duration}m")
                    print(f"🔗 URL: https://youtube.com/shorts/{video_id}")
                
                return video_id

        except Exception as e:
            print(f"❌ PIPELINE CRITICAL ERROR: {str(e)}")
            return None

if __name__ == "__main__":
    scout_choice = input("Select scouting method (1=AI Scout [Replicate], 2=Normal Scout [Pexels]) [1]: ").strip()
    scout_method = "normal" if scout_choice == "2" else "ai"
    
    factory = AIVideoFactory(scout_method=scout_method)
    
    step_input = input("Enter starting step (1=Research, 2=Narration, 3=Scouting, 4=Captions, 5=Editing, 6=Upload) [1]: ").strip()
    start_step = int(step_input) if step_input.isdigit() else 1
    
    schedule_input = input("Enter minutes from now to schedule upload (0 for immediate) [0]: ").strip()
    schedule_minutes = int(schedule_input) if schedule_input.isdigit() else 0
    
    job = ""
    if start_step ==1:
        while True:
            job, source_link = factory.trend_agent.get_trending_topic()
            print(f"\n📈 Found trending topic: {job}")
            if source_link:
                print(f"🔗 Source: {source_link}")
            
            topic_approval = input("👉 Proceed with this topic? (Press ENTER to proceed, 'n' to skip, 'exit' to quit): ").strip().lower()
            if topic_approval == 'exit':
                print("🛑 Shutting down factory...")
                sys.exit()
            elif topic_approval in ['n', 'no']:
                print("⏭️ Skipping topic...")
                factory.trend_agent.log_topic(job)  # Log skipped topic so it isn't repeated
                continue
            break

    factory.produce_video(job, start_step=start_step, schedule_minutes=schedule_minutes)
    factory.trend_agent.log_topic(job)