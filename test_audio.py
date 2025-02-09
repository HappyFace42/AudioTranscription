import os

AUDIO_FILE = "downloads/podcast.mp3"

if os.path.exists(AUDIO_FILE):
    print(f"✅ Audio file found: {AUDIO_FILE}")
else:
    print(f"❌ Audio file NOT found: {AUDIO_FILE}")
