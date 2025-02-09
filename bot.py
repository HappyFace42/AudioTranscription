import os
import logging
import asyncio
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pydub import AudioSegment
from pydub.playback import play
from yt_dlp import YoutubeDL
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Telegram bot
app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    await update.message.reply_text("👋 Hello! Send me a podcast link, and I'll transcribe it for you!")


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles receiving a link, downloading, and transcribing audio."""
    url = update.message.text.strip()
    await update.message.reply_text("🔍 Processing link...")

    # Extract audio URL using yt-dlp
    ydl_opts = {"format": "bestaudio", "quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info.get("url")

    if not audio_url:
        await update.message.reply_text("❌ Failed to extract audio.")
        return

    await update.message.reply_text(f"✅ Found Audio URL: {audio_url}")

    # Download audio
    audio_path = "downloads/podcast.mp3"
    response = requests.get(audio_url)
    with open(audio_path, "wb") as f:
        f.write(response.content)

    await update.message.reply_text("✅ Download complete. Transcribing...")

    # Transcribe audio with OpenAI
    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(model="whisper-1", file=audio_file)

    transcription = response["text"]
    await update.message.reply_text(f"📝 Transcription:\n\n{transcription[:4000]}")

    # Cleanup
    os.remove(audio_path)


def main():
    """Main function to start the bot."""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_audio))

    logger.info("🚀 Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
