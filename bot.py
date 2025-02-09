import os
import logging
import requests
import openai
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# ✅ Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = "https://audiotranscription-production.up.railway.app/webhook"

openai.api_key = OPENAI_API_KEY

# ✅ Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ✅ Flask for webhook handling
app = Flask(__name__)

# ✅ Telegram bot setup
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def start(update: Update, context):
    """Start command handler."""
    await update.message.reply_text("👋 Send me a podcast link, and I'll transcribe it!")

async def process_audio(update: Update, context):
    """Handles incoming audio links for transcription."""
    text = update.message.text
    chat_id = update.message.chat_id
    logger.info(f"📥 Received message: {text}")

    if text.startswith("http"):
        await update.message.reply_text("🎙️ Processing podcast...")
        audio_file = download_audio(text)

        if audio_file:
            await update.message.reply_text("✅ Download complete. Transcribing...")
            transcription = await transcribe_audio(audio_file)
            
            if transcription:
                await update.message.reply_text(f"📝 Transcription:\n{transcription[:4000]}")
            else:
                await update.message.reply_text("❌ Failed to transcribe the audio.")
        else:
            await update.message.reply_text("❌ Could not download the audio.")
    else:
        await update.message.reply_text("🚫 Please send a valid podcast link.")

def download_audio(url):
    """Downloads the audio file from the given URL."""
    try:
        logger.info(f"⬇️ Downloading from: {url}")
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            file_path = "podcast.mp3"
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"✅ Download complete: {file_path}")
            return file_path
        else:
            logger.error(f"❌ Failed to download audio: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"❌ Download error: {e}")
        return None

async def transcribe_audio(file_path):
    """Transcribes the audio using OpenAI."""
    logger.info(f"🎤 Sending audio for transcription: {file_path}")
    try:
        with open(file_path, "rb") as audio_file:
            response = openai.Audio.transcribe("whisper-1", audio_file)
            logger.info(f"📜 Transcription response: {response}")
            return response["text"]
    except Exception as e:
        logger.error(f"❌ Transcription failed: {e}")
        return None

@app.route("/webhook", methods=["POST"])
async def webhook():
    """Receives webhook updates from Telegram."""
    try:
        update = Update.de_json(request.get_json(), telegram_app.bot)
        logger.info(f"📬 Received Webhook Update: {update}")
        await telegram_app.process_update(update)  # 🔥 FIXED: Now using `await`
        return "OK"
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        return "Error", 500

def set_webhook():
    """Sets the webhook for Telegram bot."""
    logger.info("🚀 Setting webhook if needed...")
    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
        json={"url": WEBHOOK_URL}
    )
    result = response.json()
    if result.get("ok"):
        logger.info(f"✅ Webhook set successfully: {WEBHOOK_URL}")
    else:
        logger.error(f"❌ Failed to set webhook: {result}")

if __name__ == "__main__":
    set_webhook()
    logger.info("🚀 Bot is running with webhook on port 8080")
    app.run(host="0.0.0.0", port=8080)
