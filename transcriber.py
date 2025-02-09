import logging
import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
logger = logging.getLogger(__name__)

def transcribe_audio(file_path: str) -> str:
    """Transcribes audio using OpenAI Whisper API."""
    try:
        with open(file_path, "rb") as audio_file:
            response = openai.Audio.transcribe("whisper-1", audio_file)
        return response["text"]
    except Exception as e:
        logger.error(f"❌ Transcription failed: {e}")
        return None
