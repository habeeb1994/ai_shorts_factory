import gradio as gr
import os
import json
import time
import datetime
from main import AIVideoFactory

def get_status_msg(step, status_text, is_error=False):
    step_names = {1: "Script", 2: "Voice", 3: "Assets", 4: "Captions", 5: "Render", 6: "Publish"}
    steps = []
    for i in range(1, 7):
        name = step_names[i]
        if i < step:
            steps.append(f"[{i}] {name} ✅")
        elif i == step:
            if is_error:
                steps.append(f"[{i}] {name} ❌")
            else:
                steps.append(f"[{i}] {name} 🔄")
        else:
            steps.append(f"[{i}] {name} ⏳")
    pipeline = " ➔ ".join(steps)
    return f"Pipeline: {pipeline}\nStatus: {status_text}"

def get_local_videos():
    folder = "assets/gameplay"
    if not os.path.exists(folder):
        os.makedirs(folder)
    return [f for f in os.listdir(folder) if f.endswith(('.mp4', '.mov', '.avi', '.mkv'))]

def get_local_avatars():
    folder = "assets/avatars"
    if not os.path.exists(folder):
        os.makedirs(folder)
    return [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

# Define the UI Layout
with gr.Blocks(title="AI Shorts Factory") as app:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("# ⚡ AI Shorts Factory\n*Craft viral vertical videos with complete control.*")
        with gr.Column(scale=2):
            global_status = gr.Textbox(label="🟢 System Status", interactive=False, value=get_status_msg(1, "Ready for action..."), lines=2)
            current_clips_state = gr.State([])
    with gr.Column(visible=False, variant="panel") as gameplay_popup:
        gr.Markdown("#### 🎮 Gameplay Downloader")
        with gr.Row():
            gameplay_url_input_popup = gr.Textbox(label="YouTube URL", lines=1, placeholder="Paste URL here...", scale=4)
            with gr.Column(scale=1):
                download_gameplay_btn_popup = gr.Button("⬇️ Download", variant="primary")
                close_popup_btn = gr.Button("❌ Close")
                
    with gr.Row():
        with gr.Column(scale=15):
            with gr.Tabs():
                with gr.Tab("1️⃣ Idea & Script"):
                    with gr.Row():
                        with gr.Column():
                            scout_method = gr.Radio(["🎥 Normal Scout [Pexels]","🤖 AI Scout [Replicate]"], label="Scouting Method", value="🎥 Normal Scout [Pexels]")
                            topic_input = gr.Textbox(label="Target Topic", lines=1, placeholder="e.g., Passive income with AI")
                            with gr.Row():
                                get_topic_btn = gr.Button("🔥 Find Trending Topic")
                                skip_topic_btn = gr.Button("⏭️ Skip")
                            research_btn = gr.Button("🚀 Step 1: Generate Viral Script", variant="primary")
                        with gr.Column():
                            script_edit = gr.Textbox(label="📝 Generated Script", lines=8)
                            
                with gr.Tab("2️⃣ Voiceover & Subtitle"):
                    with gr.Row():
                        with gr.Column():
                            voice_dropdown = gr.Dropdown(
                                choices=["Andrew (US - Authoritative)", "Christopher (US - Professional)", "Eric (US - Energetic)", "Guy (US - Deep/Calm)", "Ryan (UK - Professional)", "William (AU - Casual)"],
                                label="Select Male Voice",
                                value="Andrew (US - Authoritative)"
                            )
                            audio_btn = gr.Button("🎙️Synthesize Voice", variant="primary")
                        with gr.Column():
                            audio_preview = gr.Audio(label="Playback")
                    with gr.Row():
                        with gr.Column():
                            gen_captions_btn = gr.Button("✍️ Generate Dynamic Captions", variant="primary")
                        with gr.Column():
                            captions_edit = gr.Textbox(label="SRT Format", lines=8)                            
                            
                with gr.Tab("3️⃣ Visual Assets"):
                    with gr.Row():
                        with gr.Column():
                            meta_edit = gr.Textbox(label="🎬 Video Prompts / Keywords", lines=4)
                            scout_btn = gr.Button("🔍 Step 3: Scout & Download Clips", variant="primary")
                            with gr.Row():
                                delete_selected_btn = gr.Button("🗑️ Delete Selected", variant="secondary")
                                delete_all_btn = gr.Button("🗑️ Delete All", variant="stop")
                            selected_clip_indices = gr.State([])
                        with gr.Column():
                            assets_preview = gr.Gallery(label="Scouted Clips (Click to select)", elem_id="gallery", columns=5, height="auto", object_fit="contain")            
            
                with gr.Tab("5️⃣ Final Assembly"):
                    with gr.Row():
                        with gr.Column():
                            video_layout = gr.Dropdown(["Single Video", "Split Screen", "Hybrid Mode"], label="Frame Layout", value="Single Video")
                            with gr.Column(visible=False) as split_screen_options:
                                narrator_mode = gr.Dropdown(["Select Gameplay", "Generate Avatar"], label="Narrator Options", value="Select Gameplay")
                                with gr.Row():
                                    local_video_dropdown = gr.Dropdown(choices=get_local_videos(), label="📂 Local Gameplay Video", value=None)
                                    local_avatar_dropdown = gr.Dropdown(choices=get_local_avatars(), label="🖼️ Local Avatar Image", value=None, visible=False)
                            render_btn = gr.Button("🎬 Step 5: Render Masterpiece", variant="primary")
                        with gr.Column():
                            video_preview = gr.Video(label="Final Output", height=380, interactive=False)
                            gameplay_preview = gr.Video(label="Gameplay Preview", visible=False, height=380, interactive=False)
                            
                with gr.Tab("6️⃣ Publish"):
                    with gr.Row():
                        with gr.Column():
                            enable_schedule = gr.Checkbox(label="📅 Enable Scheduled Upload", value=True)
                            with gr.Row():
                                schedule_date_year = gr.Dropdown(choices=[str(y) for y in range(datetime.datetime.now().year, datetime.datetime.now().year + 5)], label="Year", value=str(datetime.datetime.now().year), min_width=120)
                                schedule_date_month = gr.Dropdown(choices=[f"{m:02d}" for m in range(1, 13)], label="Month", value=f"{datetime.datetime.now().month:02d}", min_width=80)
                                schedule_date_day = gr.Dropdown(choices=[f"{d:02d}" for d in range(1, 32)], label="Day", value=f"{datetime.datetime.now().day:02d}", min_width=80)
                                schedule_time_hour = gr.Dropdown(choices=[f"{h:02d}" for h in range(24)], label="Hour", value="12", min_width=80)
                                schedule_time_minute = gr.Dropdown(choices=[f"{m:02d}" for m in range(60)], label="Minute", value="00", min_width=80)
                            cta_input = gr.Textbox(label="🔗 Affiliate / CTA Link (Added to YouTube Description)", placeholder="https://your-affiliate-link.com/product", lines=1)
                            upload_btn = gr.Button("🚀 Step 6: Publish to YouTube Shorts", variant="primary")
                        with gr.Column():
                            gr.Markdown("<br>### 🎉 Ready to go viral!\nDouble-check the preview in the Final Assembly tab before publishing.")
                            
                with gr.Tab("📚 Topic History"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            refresh_history_btn = gr.Button("🔄 Refresh History")
                            delete_history_btn = gr.Button("🗑️ Delete Selected", variant="stop")
                            delete_all_history_btn = gr.Button("🗑️ Delete All Topics", variant="stop")
                        with gr.Column(scale=3):
                            history_checkboxes = gr.CheckboxGroup(label="Stored Topics", choices=[])

        with gr.Column(scale=1, min_width=150):
            load_data_btn = gr.Button("📂 Load Previous", size="sm")
            clear_workspace_btn = gr.Button("🧹 Clear Workspace", size="sm", variant="stop")
            gr.Markdown("---")
            open_downloader_btn = gr.Button("🎮 Download Gameplay", size="sm")


    # Event Handlers
    def fetch_topic():
        factory = AIVideoFactory(scout_method="ai", auto_proceed=True)
        topic, _ = factory.trend_agent.get_trending_topic()
        return topic
        
    def skip_and_fetch(current):
        factory = AIVideoFactory(scout_method="ai", auto_proceed=True)
        if current:
            factory.trend_agent.log_topic(current)
        topic, _ = factory.trend_agent.get_trending_topic()
        return topic
        
    get_topic_btn.click(fn=fetch_topic, outputs=topic_input)
    skip_topic_btn.click(fn=skip_and_fetch, inputs=topic_input, outputs=topic_input)

    def load_existing_data():
        factory = AIVideoFactory(scout_method="ai", auto_proceed=True)
        content_file = os.path.join(factory.temp_dir, "content.json")
        script_file = os.path.join(factory.temp_dir, "script.txt")
        audio_file = os.path.join(factory.temp_dir, "voice.mp3")
        srt_file = os.path.join(factory.temp_dir, "captions.srt")
        raw_clips_dir = "assets/raw_clips"
        
        # Initialize return values
        topic_val, script_val, meta_val, captions_val, audio_val = "", "", "", "", None
        downloaded_clips = None
        step = 1

        # Load script/content
        if os.path.exists(content_file):
            with open(content_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            topic_val = content.get('title', '')
            script_val = content.get('script', '')
            prompts = content.get('video_prompts', content.get('keywords', []))
            meta_val = "\n".join(prompts)
            step = 2
        elif os.path.exists(script_file):
            with open(script_file, 'r', encoding='utf-8') as f:
                script_val = f.read()
            step = 2

        # Load audio
        if os.path.exists(audio_file):
            audio_val = os.path.abspath(audio_file)
            step = 3

        # Load clips
        if os.path.exists(raw_clips_dir):
            clips = [os.path.abspath(os.path.join(raw_clips_dir, f)) for f in os.listdir(raw_clips_dir) if f.endswith('.mp4')]
            if clips:
                downloaded_clips = clips
                step = 4
        
        # Load captions
        if os.path.exists(srt_file):
            with open(srt_file, 'r', encoding='utf-8') as f:
                captions_val = f.read()
            step = 5
        
        # Return in order of UI elements
        return (
            topic_val, 
            script_val, 
            audio_val, 
            meta_val, 
            downloaded_clips, 
            captions_val, 
            get_status_msg(step, "✅ Loaded previous data. Ready to continue."), 
            downloaded_clips or [],
            []
        )
        
    load_data_btn.click(fn=load_existing_data, outputs=[topic_input, script_edit, audio_preview, meta_edit, assets_preview, captions_edit, global_status, current_clips_state, selected_clip_indices])
    
    def do_research(topic, scout_method):
        if not topic:
            return "", "", get_status_msg(1, "⚠️ Please provide or fetch a topic first.", is_error=True)
        try:
            sm = "ai" if "AI" in scout_method else "normal"
            factory = AIVideoFactory(scout_method=sm, auto_proceed=True)
            script_file = os.path.join(factory.temp_dir, "script.txt")
            content_file = os.path.join(factory.temp_dir, "content.json")
            
            content = factory.researcher.generate_viral_atoms(topic, script_file, factory.scout_method)
            with open(content_file, 'w', encoding='utf-8') as f:
                json.dump(content, f)
                
            meta_str = "\n".join(content.get('video_prompts', content.get('keywords', [])))
            return content.get('script', ''), meta_str, get_status_msg(2, "✅ Research complete. Review Script & Prompts in the next tab!")
        except Exception as e:
            return "", "", get_status_msg(1, f"❌ Error: {str(e)}", is_error=True)
            
    research_btn.click(fn=do_research, inputs=[topic_input, scout_method], outputs=[script_edit, meta_edit, global_status])
    
    def do_audio(script_text, voice_choice):
        if not script_text:
            return None, get_status_msg(2, "⚠️ Please complete Step 1 first.", is_error=True)
        try:
            factory = AIVideoFactory(scout_method="ai", auto_proceed=True)
            content_file = os.path.join(factory.temp_dir, "content.json")
            script_file = os.path.join(factory.temp_dir, "script.txt")
            
            if os.path.exists(content_file):
                with open(content_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
            else:
                content = {"title": "Custom Topic", "tags": ["shorts"]}
                
            content['script'] = script_text
            with open(content_file, 'w', encoding='utf-8') as f:
                json.dump(content, f)
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_text)
                
            audio_file = os.path.abspath(os.path.join(factory.temp_dir, "voice.mp3"))
            
            voice_map = {
                "Andrew (US - Authoritative)": "en-US-AndrewNeural",
                "Christopher (US - Professional)": "en-US-ChristopherNeural",
                "Eric (US - Energetic)": "en-US-EricNeural",
                "Guy (US - Deep/Calm)": "en-US-GuyNeural",
                "Ryan (UK - Professional)": "en-GB-RyanNeural",
                "William (AU - Casual)": "en-AU-WilliamNeural"
            }
            factory.narrator.voice = voice_map.get(voice_choice, "en-US-AndrewNeural")
            
            factory.narrator.save_speech(content['script'], audio_file)
            
            return audio_file, get_status_msg(3, "✅ Audio created. Proceed to Video Scouting!")
        except Exception as e:
            return None, get_status_msg(2, f"❌ Error: {str(e)}", is_error=True)
            
    audio_btn.click(fn=do_audio, inputs=[script_edit, voice_dropdown], outputs=[audio_preview, global_status])

    def do_scout(meta_text, scout_method):
        if not meta_text:
            return get_status_msg(3, "⚠️ Please complete Step 1 to generate prompts.", is_error=True), None
        try:
            sm = "ai" if "AI" in scout_method else "normal"
            factory = AIVideoFactory(scout_method=sm, auto_proceed=True)
            content_file = os.path.join(factory.temp_dir, "content.json")
            
            if os.path.exists(content_file):
                with open(content_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
            else:
                content = {}
                
            lines = [line.strip() for line in meta_text.split('\n') if line.strip()]
            if factory.scout_method == "ai":
                content['video_prompts'] = lines
            else:
                content['keywords'] = lines
                
            with open(content_file, 'w', encoding='utf-8') as f:
                json.dump(content, f)
                
            if factory.scout_method == "ai":
                downloaded_clips = factory.scout.generate_clips(content.get('video_prompts', []), "assets/raw_clips")
            else:
                links = factory.scout.find_high_energy_clips(content.get('keywords', []), count=3)
                downloaded_clips = factory.scout.download_clips(links, "assets/raw_clips")
                
            return get_status_msg(4, f"✅ {len(downloaded_clips)} clips downloaded. Proceed to Captions!"), downloaded_clips, downloaded_clips, []
        except Exception as e:
            return get_status_msg(3, f"❌ Error: {str(e)}", is_error=True), None, [], []
            
    scout_btn.click(fn=do_scout, inputs=[meta_edit, scout_method], outputs=[global_status, assets_preview, current_clips_state, selected_clip_indices])
    
    def do_captions():
        try:
            factory = AIVideoFactory(scout_method="ai", auto_proceed=True)
            audio_file = os.path.join(factory.temp_dir, "voice.mp3")
            srt_file = os.path.join(factory.temp_dir, "captions.srt")
            
            if not os.path.exists(audio_file):
                return "", get_status_msg(4, "⚠️ voice.mp3 not found. Did you run Step 2?", is_error=True)
                
            factory.captions.generate_srt(audio_file, srt_file)
            with open(srt_file, 'r', encoding='utf-8') as f:
                srt_content = f.read()
                
            return srt_content, get_status_msg(5, "✅ Captions generated! You can edit them here before rendering.")
        except Exception as e:
            return "", get_status_msg(4, f"❌ Error: {str(e)}", is_error=True)
            
    gen_captions_btn.click(fn=do_captions, outputs=[captions_edit, global_status])
    
    def do_render(srt_text, video_layout, narrator_mode, local_video_name, local_avatar_name):
        if not srt_text:
            return None, get_status_msg(5, "⚠️ Please generate captions first.", is_error=True)
        try:
            factory = AIVideoFactory(scout_method="ai", auto_proceed=True)
            srt_file = os.path.join(factory.temp_dir, "captions.srt")
            with open(srt_file, 'w', encoding='utf-8') as f:
                f.write(srt_text)
                
            audio_file = os.path.join(factory.temp_dir, "voice.mp3")
            raw_clips_dir = "assets/raw_clips"
            downloaded_clips = [os.path.abspath(os.path.join(raw_clips_dir, f)) for f in os.listdir(raw_clips_dir) if f.endswith('.mp4')]
            
            if video_layout == "Single Video":
                narrator_video = None
            else:
                if narrator_mode == "Generate Avatar":
                    narrator_file = "assets/narrator.mp4"
                    avatar_img = None
                    if local_avatar_name and os.path.exists(os.path.join("assets/avatars", local_avatar_name)):
                        avatar_img = os.path.abspath(os.path.join("assets/avatars", local_avatar_name))
                    if avatar_img:
                        from avatar import AvatarAgent
                        avatar_agent = AvatarAgent()
                        avatar_result = avatar_agent.animate_image(avatar_img, audio_file, narrator_file)
                        if not avatar_result:
                            return gr.update(), gr.update(), get_status_msg(5, "❌ Error: Avatar animation failed. Check console.", is_error=True)
                    else:
                        return gr.update(), gr.update(), get_status_msg(5, "❌ Error: Please select an avatar image.", is_error=True)
                    narrator_video = os.path.abspath(narrator_file) if os.path.exists(narrator_file) else None
                else: # "Select Gameplay"
                    if local_video_name and os.path.exists(os.path.join("assets/gameplay", local_video_name)):
                        narrator_video = os.path.abspath(os.path.join("assets/gameplay", local_video_name))
                    else:
                        narrator_video = os.path.abspath("assets/narrator.mp4") if os.path.exists("assets/narrator.mp4") else None
            
            import random
            bg_music_dir = "assets/bg_music"
            bg_music_file = None
            if os.path.exists(bg_music_dir):
                music_files = [f for f in os.listdir(bg_music_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
                if music_files:
                    bg_music_file = os.path.abspath(os.path.join(bg_music_dir, random.choice(music_files)))
                    
            final_video = os.path.abspath(os.path.join(factory.output_dir, f"short_{int(time.time())}.mp4"))
            factory.editor.assemble(audio_file, downloaded_clips, srt_file, final_video, bg_music_file, narrator_video, layout=video_layout)
            
            return gr.update(value=final_video, visible=True), gr.update(visible=False), get_status_msg(6, "✅ Rendering complete! Watch the preview above.")
        except Exception as e:
            return gr.update(), gr.update(), get_status_msg(5, f"❌ Error: {str(e)}", is_error=True)
            
    render_btn.click(fn=do_render, inputs=[captions_edit, video_layout, narrator_mode, local_video_dropdown, local_avatar_dropdown], outputs=[video_preview, gameplay_preview, global_status])
    
    def toggle_split_screen(layout, mode):
        if layout in ["Split Screen", "Hybrid Mode"]:
            show_video = (mode == "Select Gameplay")
            show_avatar = (mode == "Generate Avatar")
            return gr.update(visible=True), gr.update(visible=show_video, choices=get_local_videos()), gr.update(visible=show_avatar, choices=get_local_avatars()), gr.update(), gr.update()
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(value=None, visible=False), gr.update(visible=True)
        
    video_layout.change(fn=toggle_split_screen, inputs=[video_layout, narrator_mode], outputs=[split_screen_options, local_video_dropdown, local_avatar_dropdown, gameplay_preview, video_preview], show_progress="hidden")

    def toggle_narrator_mode(mode):
        if mode == "Select Gameplay":
            return gr.update(visible=True, choices=get_local_videos()), gr.update(visible=False)
        else:
            return gr.update(visible=False), gr.update(visible=True, choices=get_local_avatars())

    narrator_mode.change(fn=toggle_narrator_mode, inputs=[narrator_mode], outputs=[local_video_dropdown, local_avatar_dropdown], show_progress="hidden")

    def preview_gameplay(video_name):
        if video_name:
            video_path = os.path.abspath(os.path.join("assets/gameplay", video_name))
            if os.path.exists(video_path):
                return gr.update(value=video_path, visible=True), gr.update(visible=False)
        return gr.update(value=None, visible=False), gr.update(visible=True)
        
    local_video_dropdown.change(fn=preview_gameplay, inputs=[local_video_dropdown], outputs=[gameplay_preview, video_preview], show_progress="hidden")

    # Explicit named functions are safer in Gradio and prevent AST parsing issues
    def show_gameplay_modal():
        return gr.update(visible=True)
        
    def hide_gameplay_modal():
        return gr.update(visible=False)

    open_downloader_btn.click(fn=show_gameplay_modal, inputs=[], outputs=[gameplay_popup], show_progress="hidden")
    close_popup_btn.click(fn=hide_gameplay_modal, inputs=[], outputs=[gameplay_popup], show_progress="hidden")

    def do_download_gameplay_popup(url):
        if not url:
            return get_status_msg(1, "⚠️ Please provide a YouTube URL.", is_error=True), gr.update(choices=get_local_videos()), gr.update(visible=True)
        try:
            from download_gameplay import download_youtube_video
            gameplay_folder = "assets/gameplay"
            if not os.path.exists(gameplay_folder):
                os.makedirs(gameplay_folder)
    
            output_filename = f"gameplay_{int(time.time())}.mp4"
            output_path = os.path.join(gameplay_folder, output_filename)
    
            download_youtube_video(url, output_path)
    
            return get_status_msg(1, f"✅ Gameplay '{output_filename}' downloaded!"), gr.update(choices=get_local_videos()), gr.update(visible=False)
        except Exception as e:
            return get_status_msg(1, f"❌ Gameplay Download Error: {str(e)}", is_error=True), gr.update(choices=get_local_videos()), gr.update(visible=True)
    
    download_gameplay_btn_popup.click(fn=do_download_gameplay_popup, inputs=[gameplay_url_input_popup], outputs=[global_status, local_video_dropdown, gameplay_popup])

    def do_upload(enable_schedule_val, year_val, month_val, day_val, hour_val, minute_val, cta_link_val):
        try:
            factory = AIVideoFactory(scout_method="ai", auto_proceed=True)
            content_file = os.path.join(factory.temp_dir, "content.json")
            if not os.path.exists(content_file):
                return get_status_msg(6, "⚠️ Missing content.json", is_error=True)
            with open(content_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
                
            videos = [f for f in os.listdir(factory.output_dir) if f.endswith('.mp4')]
            if not videos:
                return get_status_msg(6, "⚠️ No rendered video found.", is_error=True)
            videos.sort(key=lambda x: os.path.getctime(os.path.join(factory.output_dir, x)), reverse=True)
            final_video = os.path.join(factory.output_dir, videos[0])
            
            metadata = {
                "title": content.get('title', 'AI Video'),
                "description": f"{content.get('script', '')[:150]}...\n\n👇 Check this out:\n{cta_link_val}\n\n#wealth #ai #productivity",
                "tags": content.get('tags', ['ai', 'shorts']),
                "cta_link": cta_link_val
            }
            
            schedule_mins = 0
            if enable_schedule_val:
                try:
                    # Create a target datetime from the picker values
                    schedule_date_val = f"{year_val}-{month_val}-{day_val}"
                    schedule_time_val = f"{hour_val}:{minute_val}"
                    
                    date_part = datetime.datetime.strptime(schedule_date_val, "%Y-%m-%d").date()
                    time_part = datetime.datetime.strptime(schedule_time_val, "%H:%M").time()
                    target_time = datetime.datetime.combine(date_part, time_part)
                    
                    # Adjust 'now' to be naive to match the combined target_time
                    now = datetime.datetime.now()
                    delta = target_time - now
                    schedule_mins = int(delta.total_seconds() / 60)
                    if schedule_mins < 0:
                        return get_status_msg(6, "⚠️ Scheduled time is in the past. Please enter a future time.", is_error=True)
                except Exception as e:
                    return get_status_msg(6, f"⚠️ Invalid date/time format. Please check the picker values.", is_error=True)
            video_id = factory.manager.deploy_short(final_video, metadata, schedule_mins)
            if video_id:
                return get_status_msg(7, f"✅ Upload Complete! Link: https://youtube.com/shorts/{video_id}")
            return get_status_msg(6, "❌ Upload failed or returned no ID.", is_error=True)
        except Exception as e:
            return get_status_msg(6, f"❌ Error: {str(e)}", is_error=True)
            
    upload_btn.click(fn=do_upload, inputs=[enable_schedule, schedule_date_year, schedule_date_month, schedule_date_day, schedule_time_hour, schedule_time_minute, cta_input], outputs=global_status)

    def on_clip_select(evt: gr.SelectData, current_indices, clips):
        indices = list(current_indices) if current_indices else []
        if evt.index in indices:
            indices.remove(evt.index)
        else:
            indices.append(evt.index)
            
        gallery_items = []
        for i, clip in enumerate(clips):
            if i in indices:
                gallery_items.append((clip, "✅ Selected"))
            else:
                gallery_items.append((clip, ""))
                
        return indices, gallery_items

    assets_preview.select(fn=on_clip_select, inputs=[selected_clip_indices, current_clips_state], outputs=[selected_clip_indices, assets_preview])

    def delete_selected_clip(selected_indices, clips):
        if not selected_indices or not clips:
            return clips, clips, get_status_msg(3, "⚠️ No clips selected in the gallery.", is_error=True), []
            
        try:
            for idx in selected_indices:
                if idx < len(clips):
                    clip_path = clips[idx]
                    if os.path.exists(clip_path):
                        os.remove(clip_path)
        except Exception as e:
            pass
            
        raw_clips_dir = "assets/raw_clips"
        new_clips = []
        if os.path.exists(raw_clips_dir):
            new_clips = [os.path.abspath(os.path.join(raw_clips_dir, f)) for f in os.listdir(raw_clips_dir) if f.endswith('.mp4')]
            
        return new_clips, new_clips, get_status_msg(3, f"🗑️ {len(selected_indices)} selected clip(s) deleted."), []

    def delete_all_clips():
        raw_clips_dir = "assets/raw_clips"
        if os.path.exists(raw_clips_dir):
            for f in os.listdir(raw_clips_dir):
                if f.endswith('.mp4'):
                    try:
                        os.remove(os.path.join(raw_clips_dir, f))
                    except:
                        pass
        return [], [], get_status_msg(3, "🗑️ All clips deleted."), []

    delete_selected_btn.click(fn=delete_selected_clip, inputs=[selected_clip_indices, current_clips_state], outputs=[assets_preview, current_clips_state, global_status, selected_clip_indices])
    delete_all_btn.click(fn=delete_all_clips, inputs=[], outputs=[assets_preview, current_clips_state, global_status, selected_clip_indices])

    def fetch_history():
        from trend_agent import TrendAgent
        agent = TrendAgent()
        return gr.update(choices=agent.get_all_topics())

    def delete_history(selected_topics):
        if not selected_topics:
            return gr.update()
        from trend_agent import TrendAgent
        agent = TrendAgent()
        agent.delete_topics(selected_topics)
        return gr.update(choices=agent.get_all_topics(), value=[])

    refresh_history_btn.click(fn=fetch_history, inputs=[], outputs=[history_checkboxes])
    delete_history_btn.click(fn=delete_history, inputs=[history_checkboxes], outputs=[history_checkboxes])

    def delete_all_history():
        from trend_agent import TrendAgent
        agent = TrendAgent()
        all_topics = agent.get_all_topics()
        if all_topics:
            agent.delete_topics(all_topics)
        return gr.update(choices=[], value=[])

    delete_all_history_btn.click(fn=delete_all_history, inputs=[], outputs=[history_checkboxes])

    def clear_workspace():
        factory = AIVideoFactory(scout_method="ai", auto_proceed=True)
        factory.cleanup()
        raw_clips_dir = "assets/raw_clips"
        if os.path.exists(raw_clips_dir):
            for f in os.listdir(raw_clips_dir):
                try:
                    os.remove(os.path.join(raw_clips_dir, f))
                except:
                    pass
        return (
            "", "", None, "", [], "", 
            get_status_msg(1, "🧹 Workspace cleared. Ready for a new project!"), 
            [], []
        )

    clear_workspace_btn.click(fn=clear_workspace, outputs=[topic_input, script_edit, audio_preview, meta_edit, assets_preview, captions_edit, global_status, current_clips_state, selected_clip_indices])

if __name__ == "__main__":
    if not os.path.exists("assets"):
        os.makedirs("assets")
    if not os.path.exists("exports"):
        os.makedirs("exports")
    app.launch(
        theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="blue"),
        allowed_paths=[
            os.path.abspath("assets"),
            os.path.abspath("exports")
        ],
        server_name="0.0.0.0",
        share=True
    )