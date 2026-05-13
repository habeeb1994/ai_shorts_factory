import os
import base64
from huggingface_hub import snapshot_download
from ui import app

if not os.path.exists("assets"):
    os.makedirs("assets")
if not os.path.exists("exports"):
    os.makedirs("exports")

# Sync assets from Hugging Face Dataset (Free cloud storage, keeps GitHub clean)
try:
    print("🔄 Syncing assets from Hugging Face Dataset...")
    snapshot_download(
        repo_id="habeeb94/ai_shorts_assets", 
        repo_type="dataset", 
        local_dir="assets",
        local_dir_use_symlinks=False
    )
    print("✅ Assets synced successfully!")
except Exception as e:
    print(f"⚠️ Could not sync dataset: {e}. Make sure the dataset exists and is public.")

# Reconstruct Google Auth files from Hugging Face Secrets securely
if "GOOGLE_CLIENT_SECRET" in os.environ and not os.path.exists("client_secrets.json"):
    with open("client_secrets.json", "w") as f:
        f.write(os.environ["GOOGLE_CLIENT_SECRET"])

if "GOOGLE_TOKEN_PICKLE_BASE64" in os.environ and not os.path.exists("token.pickle"):
    with open("token.pickle", "wb") as f:
        f.write(base64.b64decode(os.environ["GOOGLE_TOKEN_PICKLE_BASE64"]))

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)