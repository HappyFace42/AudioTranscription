import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("audiotranscription-production.up.railway.app")  # e.g., https://yourdomain.com/webhook
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 8080))  # Default to 8080

# Logging setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Flask app for webhook
app = Flask(__name__)

# Initialize Telegram bot
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()


@app.route("/webhook", methods=["POST"])
def webhook():
    """Handles incoming Telegram webhook updates."""
    update = Update.de_json(request.get_json(), telegram_app.bot)
    telegram_app.process_update(update)
    return "OK", 200


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    await update.message.reply_text("👋 Hello! Send me a podcast link, and I'll transcribe it for you!")


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles receiving a link, downloading, and transcribing audio."""
    url = update.message.text.strip()
    await update.message.reply_text("�� Processing link...")

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


def setup_webhook():
    """Registers the webhook with Telegram."""
    webhook_url = f"{WEBHOOK_URL}/webhook"
    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
        json={"url": webhook_url},
    )
    if response.status_code == 200:
        logger.info("✅ Webhook set successfully.")
    else:
        logger.error(f"❌ Failed to set webhook: {response.text}")


def main():
    """Main function to start the bot with webhook."""
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_audio))

    # Set up webhook
    setup_webhook()

    logger.info(f"🚀 Bot is running with webhook on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
