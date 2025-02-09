import openai
import os
import logging
import pydub

from config import OPENAI_API_KEY

logger = logging.getLogger("transcriber")

def transcribe_audio(audio_file: str) -> str:
    """Transcribes an MP3 file using OpenAI's Whisper API."""
    logger.info(f"🎙️ Transcribing audio: {audio_file}")

    if os.path.getsize(audio_file) > 25 * 1024 * 1024:
        logger.warning("⚠️ File too large, splitting into chunks...")
        return transcribe_large_file(audio_file)

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        with open(audio_file, "rb") as file:
            response = client.audio.transcriptions.create(model="whisper-1", file=file)
            return response.text.strip()
    except Exception as e:
        logger.error(f"❌ OpenAI API Error: {e}")
        return None

def transcribe_large_file(audio_file: str) -> str:
    """Splits large files and transcribes each chunk separately."""
    audio = pydub.AudioSegment.from_file(audio_file)
    chunk_length = 4 * 60 * 1000  # 4 minutes
    chunks = [audio[i:i+chunk_length] for i in range(0, len(audio), chunk_length)]
    os.makedirs("chunks", exist_ok=True)

    transcript = ""
    for i, chunk in enumerate(chunks):
        chunk_path = f"chunks/chunk_{i}.mp3"
        chunk.export(chunk_path, format="mp3")
        logger.info(f"🎙️ Transcribing chunk: {chunk_path}")

        text = transcribe_audio(chunk_path)
        transcript += text + "\n"

    return transcript.strip()
