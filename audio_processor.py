import logging
import yt_dlp

logger = logging.getLogger(__name__)

def download_audio(url: str) -> str:
    """Downloads audio from a given URL and returns file path."""
    try:
        output_file = "downloads/audio.mp3"
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_file,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_file
    except Exception as e:
        logger.error(f"❌ Audio download failed: {e}")
        return None
