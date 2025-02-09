import os
import logging
import asyncio
import requests
import tempfile
import subprocess
from flask import Flask, request
from pydub import AudioSegment
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from notion_client import Client

# 📌 Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")

# 🚨 Debug Missing ENV Vars
if not TELEGRAM_BOT_TOKEN:
    logging.error("❌ TELEGRAM_BOT_TOKEN is missing!")
    exit(1)
if not NOTION_API_KEY:
    logging.error("❌ NOTION_API_KEY is missing!")
    exit(1)
if not NOTION_PAGE_ID:
    logging.error("❌ NOTION_PAGE_ID is missing!")
    exit(1)

# ✅ Initialize APIs
bot = Bot(token=TELEGRAM_BOT_TOKEN)
notion = Client(auth=NOTION_API_KEY)
app = Flask(__name__)

# 🚀 Initialize Telegram Bot
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()


@app.route("/webhook", methods=["POST"])
async def webhook():
    """Handle incoming Telegram messages"""
    update = Update.de_json(request.get_json(), bot)
    logging.info(f"📬 Received Webhook Update: {update}")

    # Process update
    await telegram_app.process_update(update)
    return "OK", 200


async def start(update: Update, context):
    """Start command handler"""
    await update.message.reply_text("🤖 Send me a podcast link to transcribe it!")


async def handle_message(update: Update, context):
    """Handle incoming messages"""
    message_text = update.message.text.strip()
    chat_id = update.message.chat_id
    logging.info(f"📥 Received message: {message_text}")

    if message_text.startswith("http"):
        await update.message.reply_text("🎙️ Processing podcast... Please wait!")
        transcript = await process_podcast(message_text)
        if transcript:
            notion_url = store_in_notion(transcript)
            await update.message.reply_text(f"✅ Transcription saved: {notion_url}")
        else:
            await update.message.reply_text("❌ Failed to process podcast!")
    else:
        await update.message.reply_text("❌ Please send a valid podcast URL!")


async def process_podcast(url):
    """Download & Transcribe the Podcast"""
    try:
        logging.info(f"⬇️ Downloading: {url}")
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as temp_audio:
            response = requests.get(url)
            if response.status_code != 200:
                logging.error("❌ Failed to download podcast")
                return None

            temp_audio.write(response.content)
            temp_audio.flush()

            # 🔊 Convert to WAV if needed
            audio = AudioSegment.from_file(temp_audio.name)
            wav_path = temp_audio.name.replace(".mp3", ".wav")
            audio.export(wav_path, format="wav")

            # �� Transcribe using Whisper
            transcript = transcribe_audio(wav_path)
            return transcript

    except Exception as e:
        logging.error(f"❌ Error processing podcast: {e}")
        return None


def transcribe_audio(audio_path):
    """Use Whisper AI to transcribe audio"""
    try:
        logging.info(f"📝 Transcribing: {audio_path}")
        result = subprocess.run(
            ["whisper", audio_path, "--model", "small"],
            capture_output=True,
            text=True
        )
        transcript = result.stdout.strip()
        return transcript
    except Exception as e:
        logging.error(f"❌ Transcription failed: {e}")
        return None


def store_in_notion(text):
    """Store transcript in Notion"""
    try:
        logging.info("📝 Storing transcription in Notion...")

        # 🔥 Ensure text is within Notion limits
        MAX_CHUNK_SIZE = 2000  # Notion has text block limits
        chunks = [text[i:i + MAX_CHUNK_SIZE] for i in range(0, len(text), MAX_CHUNK_SIZE)]

        notion.blocks.children.append(NOTION_PAGE_ID, children=[
            {"object": "block", "type": "paragraph", "paragraph": {"text": [{"type": "text", "text": {"content": chunk}}]}}
            for chunk in chunks
        ])

        return f"https://notion.so/{NOTION_PAGE_ID}"

    except Exception as e:
        logging.error(f"❌ Failed to save transcript in Notion: {e}")
        return None


async def setup_bot():
    """Initialize the bot and set the webhook."""
    global telegram_app

    # ✅ Initialize the bot properly
    await telegram_app.initialize()

    # ✅ Use bot.set_webhook() instead of Application.set_webhook()
    webhook_url = "https://audiotranscription-production.up.railway.app/webhook"
    await telegram_app.bot.set_webhook(url=webhook_url)
    
    print(f"✅ Webhook set successfully: {webhook_url}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(setup_bot())
    app.run(host="0.0.0.0", port=8080)
