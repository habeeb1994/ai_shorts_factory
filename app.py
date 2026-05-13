import os
from ui import app

if not os.path.exists("assets"):
    os.makedirs("assets")
if not os.path.exists("exports"):
    os.makedirs("exports")

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)