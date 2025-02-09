import requests
import re
import os
import logging

logger = logging.getLogger("extract_audio")

def extract_audio_url(url: str):
    """Extracts the MP3 audio URL and podcast title from a given URL."""
    logger.info(f"🔍 Extracting audio from {url}...")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # ✅ Extract MP3 URL
        audio_url_match = re.search(r'https://traffic\.libsyn\.com/[\w\-/]+\.mp3', response.text)
        title_match = re.search(r'<title>(.*?)</title>', response.text)

        if not audio_url_match:
            raise ValueError("❌ No MP3 URL found.")

        audio_url = audio_url_match.group(0)
        podcast_title = title_match.group(1) if title_match else "Unknown Podcast"

        logger.info(f"✅ Found Audio URL: {audio_url}")
        logger.info(f"✅ Extracted Podcast Title: {podcast_title}")

        return audio_url, podcast_title

    except Exception as e:
        logger.error(f"❌ Failed to extract audio: {e}")
        return None, None

def download_audio(url: str, save_folder: str) -> str:
    """Downloads audio from a given URL."""
    os.makedirs(save_folder, exist_ok=True)
    file_path = os.path.join(save_folder, "podcast.mp3")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        logger.info(f"✅ Download complete: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"❌ Failed to download audio: {e}")
        return None
