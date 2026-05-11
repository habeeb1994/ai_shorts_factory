import subprocess
import os
from pathlib import Path

class EditorAgent:
    def assemble(self, audio, video_list, subtitles, output, bg_music=None):
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
        
        # Add optional background music input
        if bg_music:
            cmd.extend(['-stream_loop', '-1', '-i', bg_music])
            bg_music_index = audio_index + 1

        filter_parts = []
        concat_streams = ""

        # Step A: Trim for fast cuts (2.5s per clip), boost saturation, scale, crop, and normalize framerate
        for i in range(len(video_list)):
            filter_parts.append(f"[{i}:v]trim=duration=2.5,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=saturation=1.3,setsar=1,fps=30[v{i}]")
            concat_streams += f"[v{i}]"
            
        # Step B: Concatenate all normalized video streams
        filter_parts.append(f"{concat_streams}concat=n={len(video_list)}:v=1:a=0[concat_v]")
        
        # Step C: Add subtitles to the final concatenated video
        # Updated for high-retention Shorts style: large, yellow, bold, center-screen safe zone.
        style_options = (
            'FontName=Arial Black,FontSize=18,Alignment=2,MarginV=150,'
            'PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BackColour=&H80000000,'
            'BorderStyle=1,Outline=2,Shadow=1,Bold=-1'
        ).replace(',', r'\,')

        filter_parts.append(
            f"[concat_v]subtitles='{safe_sub_path}':force_style={style_options}[sub_v]"
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
    
    print("🛠️ Running EditorAgent Test...")
    editor.assemble(test_audio, test_videos, test_subtitles, test_output)
    print(f"✅ Test successful! Video saved to {test_output}")