import os
import sys

try:
    import yt_dlp
except ImportError:
    print("📦 yt-dlp not found. Installing it now...")
    os.system(f"{sys.executable} -m pip install yt-dlp")
    import yt_dlp

def download_youtube_video(url, output_path="assets/narrator.mp4"):
    print(f"\n⬇️ Downloading gameplay video from YouTube...")
    
    # Remove the existing file if it's already there
    if os.path.exists(output_path):
        os.remove(output_path)
        
    # Options to download the best mp4 format and save it as narrator.mp4
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': output_path,
        'quiet': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"\n✅ Successfully saved gameplay video to: {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"\n❌ Error downloading video: {e}")

if __name__ == "__main__":
    print("🎮 High-Retention Gameplay Downloader 🎮")
    url = input("👉 Paste a YouTube URL (e.g., Minecraft Parkour or GTA V): ").strip()
    
    if url:
        if not os.path.exists("assets"):
            os.makedirs("assets")
        download_youtube_video(url)
    else:
        print("❌ No URL provided.")