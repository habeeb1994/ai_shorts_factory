import subprocess
import os
from pathlib import Path
import re
import random

class EditorAgent:
    def _parse_srt_for_duration(self, srt_path):
        """Parses an SRT file to find the end time of the last word."""
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            last_line = ""
            for line in reversed(lines):
                if "-->" in line:
                    last_line = line
                    break
            
            if not last_line:
                return 6.0 # Fallback to 6 seconds if SRT is malformed
                
            end_time_str = last_line.split(' --> ')[1].strip()
            h, m, s_ms = end_time_str.split(':')
            s, ms = s_ms.split(',')
            
            total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0
            return total_seconds
        except Exception:
            return 6.0 # Fallback on any parsing error

    def assemble(self, audio, video_list, subtitles, output, bg_music=None, narrator_video=None, layout="Single Video"):
       # 1. Path Fix for Windows (escaped colons) based on your working code
        safe_sub_path = (
            os.path.abspath(subtitles)
            .replace('\\', '/')
            .replace(':', '\\:')
            .replace(' ', '\\ ')
        )
        print(f"🔍 Absolute safe subtitle path for FFmpeg: {safe_sub_path}")
        # 2. Loop the clips so the video sequence is long enough to cover the entire audio length.
        # Ensure we don't arbitrarily truncate the list, using all downloaded videos.
        if video_list:
            # Target 40 clips total. We will trim each to 4s to ensure fast cuts and that all unique videos are seen.
            target_length = max(len(video_list), 40)
            multiplier = (target_length // len(video_list)) + 1
            video_list = (video_list * multiplier)[:target_length]

        # 3. Build FFmpeg Command and filter_complex for multiple videos
        cmd = ['ffmpeg', '-y']
        
        # Add all video inputs
        for vid in video_list:
            cmd.extend(['-i', vid])
            
        # Add audio input (it will be at the index corresponding to len(video_list))
        cmd.extend(['-i', audio])
        audio_index = len(video_list)
        
        current_index = audio_index + 1
        
        # Add optional background music input
        if bg_music:
            cmd.extend(['-stream_loop', '-1', '-i', bg_music])
            bg_music_index = current_index
            current_index += 1
            
        # Add optional narrator video input
        if narrator_video:
            cmd.extend(['-stream_loop', '-1', '-i', narrator_video])
            narrator_index = current_index
            current_index += 1

        filter_parts = []
        concat_streams = ""
        broll_height = 960 if (layout == "Split Screen" and narrator_video) else 1920

        # Step A: Trim for fast cuts (2.5s per clip), boost saturation, scale, crop, and normalize framerate
        # For split-screen (960 height), we crop from the top-middle to preserve subjects/faces and slightly boost contrast.
        for i in range(len(video_list)):
            if layout == "Split Screen" and narrator_video:
                y_crop = f"(in_h-{broll_height})/4"
                filter_parts.append(f"[{i}:v]trim=duration=2.5,setpts=PTS-STARTPTS,scale=1080:{broll_height}:force_original_aspect_ratio=increase,crop=1080:{broll_height}:(in_w-1080)/2:{y_crop},eq=contrast=1.05:saturation=1.3,setsar=1,fps=30[v{i}]")
            else:
                filter_parts.append(f"[{i}:v]trim=duration=2.5,setpts=PTS-STARTPTS,scale=1080:{broll_height}:force_original_aspect_ratio=increase,crop=1080:{broll_height},eq=saturation=1.3,setsar=1,fps=30[v{i}]")
            concat_streams += f"[v{i}]"
            
        # Step B: Concatenate all normalized video streams
        filter_parts.append(f"{concat_streams}concat=n={len(video_list)}:v=1:a=0[concat_v]")
        
        # Step B.2: Split Screen or Hybrid Mode
        if layout == "Split Screen" and narrator_video:
            filter_parts.append(f"[{narrator_index}:v]setpts=PTS-STARTPTS,scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960,setsar=1,fps=30[narrator_v]")
            filter_parts.append(f"[concat_v][narrator_v]vstack=inputs=2[stacked_v]")
            base_v = "[stacked_v]"
        elif layout == "Hybrid Mode" and narrator_video:
            # Dynamic Hybrid Mode: Hook, Pattern-Interrupt, and CTA
            # This creates a more engaging, less predictable video structure.
            filter_parts.append(f"[{narrator_index}:v]setpts=PTS-STARTPTS,scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960,setsar=1,fps=30[narrator_v]")
            
            total_duration = self._parse_srt_for_duration(subtitles)
            
            # The hook is the first 25% of the video, but no more than 7 seconds.
            hook_duration = min(total_duration * 0.25, 7.0)
            
            # The CTA is the last 4 seconds.
            cta_duration = 4.0
            cta_start_time = max(hook_duration + 1, total_duration - cta_duration)
            
            # A random "pattern interrupt" in the middle for 3s to re-engage viewer.
            interrupt_window_start = hook_duration + 2
            interrupt_window_end = cta_start_time - 5 # 2s buffer + 3s duration
            
            enable_parts = [f"between(t,0,{hook_duration:.2f})"]
            if interrupt_window_start < interrupt_window_end:
                interrupt_start = random.uniform(interrupt_window_start, interrupt_window_end)
                enable_parts.append(f"between(t,{interrupt_start:.2f},{interrupt_start + 3.0:.2f})")
            enable_parts.append(f"between(t,{cta_start_time:.2f},{total_duration:.2f})")
            
            enable_logic = "+".join(enable_parts)
            print(f"✨ Dynamic Hybrid Mode enabled. Split-screen sections: {enable_logic}")

            filter_parts.append("[concat_v]split=2[broll_for_split][broll_full]")
            filter_parts.append("[broll_for_split]crop=1080:960:0:480[broll_split]")
            filter_parts.append("[narrator_v][broll_split]vstack=inputs=2[split_screen]")
            filter_parts.append(f"[broll_full][split_screen]overlay=x=0:y=0:enable='{enable_logic}'[stacked_v]")
            base_v = "[stacked_v]"
        else:
            base_v = "[concat_v]"

        # Step C: Add subtitles to the final concatenated video
        # Updated for high-retention Shorts style: large, yellow, bold, center-screen safe zone.
        style_options = (
            'FontName=Arial Black,FontSize=18,Alignment=2,MarginV=150,'
            'PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BackColour=&H80000000,'
            'BorderStyle=1,Outline=2,Shadow=1,Bold=-1'
        ).replace(',', r'\,')

        filter_parts.append(
            f"{base_v}subtitles='{safe_sub_path}':force_style={style_options}[sub_v]"
        )

        # Step C.2: Add a stylized "Like | Share | Subscribe" button banner at the bottom
        # Specify explicit fontfile to avoid Fontconfig (null) errors on Windows
        if os.name == 'nt':
            btn_font = "C\\:/Windows/Fonts/arialbd.ttf"
        else:
            btn_font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            
        filter_parts.append(
            f"[sub_v]drawtext=fontfile='{btn_font}':text=' LIKE | SHARE | SUBSCRIBE ':fontcolor=white:fontsize=45:box=1:boxcolor=red@0.9:boxborderw=20:x=(w-text_w)/2:y=h-300[final_v]"
        )

        # Step D: Mix background music if provided
        if bg_music:
            # amix naturally halves the volume of both inputs. We counteract this by boosting the voiceover volume significantly (4.0).
            # We set background music lower to 0.2 (which becomes ~0.10) to make the voice pop out more.
            filter_parts.append(f"[{audio_index}:a:0]volume=4.0[a1];[{bg_music_index}:a:0]volume=0.2[a2];[a1][a2]amix=inputs=2:duration=first[a_out]")
            audio_map = '[a_out]'
        else:
            # Slightly boost standalone voiceover just in case
            filter_parts.append(f"[{audio_index}:a:0]volume=1.5[a_out]")
            audio_map = '[a_out]'

        filter_complex = ";".join(filter_parts)

        cmd.extend([
            '-filter_complex', filter_complex,
            '-c:v', 'libx264', 
            '-crf', '23',
            '-preset', 'veryfast', # Speeds up rendering on Windows
            '-c:a', 'aac', 
            '-map', '[final_v]',          # Map the final filtered video stream
            '-map', audio_map,            # Map the mixed audio (or original if no bg music)
            '-shortest',
            output
        ])

        print(f"🎬 Rendering video with command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ FFmpeg Error: {result.stderr}")
            raise Exception("FFmpeg rendering failed.")
            
        return os.path.abspath(output)

if __name__ == "__main__":
    # Quick test block to run editor.py standalone
    editor = EditorAgent()
    
    # Assuming these files were left over from a previous run of main.py
    test_audio = "assets/temp_production/voice.mp3"
    test_videos = [
        "assets/raw_clips/clip_0.mp4",
        "assets/raw_clips/clip_1.mp4",
        "assets/raw_clips/clip_2.mp4"
    ]
    test_subtitles = "assets/temp_production/captions.srt"
    test_output = "exports/test_short.mp4"
    
    narrator_video = "assets/narrator.mp4" if os.path.exists("assets/narrator.mp4") else None
    
    print("🛠️ Running EditorAgent Test...")
    editor.assemble(test_audio, test_videos, test_subtitles, test_output, narrator_video=narrator_video, layout="Hybrid Mode")
    print(f"✅ Test successful! Video saved to {test_output}")