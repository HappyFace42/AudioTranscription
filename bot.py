import os
import logging
import asyncio
import uuid
import yt_dlp
import openai
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from notion_client import Client

# ✅ Load Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Flask App for Webhook
app = Flask(__name__)

# ✅ Initialize Telegram Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# ✅ Initialize Notion Client
notion = Client(auth=NOTION_API_KEY)

# ✅ Validate API Keys
if not TELEGRAM_BOT_TOKEN:
    logging.error("❌ TELEGRAM_BOT_TOKEN is missing!")
    exit(1)
if not NOTION_API_KEY or not NOTION_PAGE_ID:
    logging.error("❌ Notion API credentials are missing!")
    exit(1)
if not OPENAI_API_KEY:
    logging.error("❌ OpenAI API Key is missing!")
    exit(1)

# ✅ Download Audio Function
async def download_audio(url: str):
    """Downloads audio from the given URL and returns the file path."""
    try:
        logging.info(f"📥 Downloading audio from: {url}")

        output_file = f"downloads/{uuid.uuid4()}.mp3"
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_file,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        logging.info(f"✅ Audio downloaded: {output_file}")
        return output_file

    except Exception as e:
        logging.error(f"❌ Failed to download audio: {e}")
        return None

# ✅ Transcribe Audio Function
async def transcribe_audio(audio_file: str):
    """Transcribes audio using OpenAI Whisper API."""
    try:
        logging.info("🎙️ Transcribing audio...")

        openai.api_key = OPENAI_API_KEY
        with open(audio_file, "rb") as audio:
            transcript = openai.Audio.transcribe("whisper-1", audio)

        logging.info("✅ Transcription complete")
        return transcript["text"]

    except Exception as e:
        logging.error(f"❌ Transcription failed: {e}")
        return None

# ✅ Store in Notion
async def store_in_notion(text: str):
    """Stores the transcribed text in Notion."""
    try:
        logging.info("📝 Storing transcript in Notion...")

        # Split into smaller chunks (Notion limits text block size)
        chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]

        for chunk in chunks:
            notion.pages.create(
                parent={"page_id": NOTION_PAGE_ID},
                properties={"title": {"title": [{"text": {"content": "Podcast Transcript"}}]}},
                children=[{"object": "block", "type": "paragraph", "paragraph": {"text": [{"text": {"content": chunk}}]}}]
            )

        logging.info("✅ Transcript saved in Notion")
        return True

    except Exception as e:
        logging.error(f"❌ Failed to save in Notion: {e}")
        return False

# ✅ Process Podcast Function
async def process_podcast(url: str, chat_id: int, context: CallbackContext):
    """Handles downloading, transcribing, and storing a podcast."""
    try:
        audio_file = await download_audio(url)
        if not audio_file:
            await context.bot.send_message(chat_id, "❌ Failed to download audio.")
            return

        transcript = await transcribe_audio(audio_file)
        if not transcript:
            await context.bot.send_message(chat_id, "❌ Failed to transcribe audio.")
            return

        notion_result = await store_in_notion(transcript)
        if notion_result:
            await context.bot.send_message(chat_id, "✅ Transcript saved in Notion!")
        else:
            await context.bot.send_message(chat_id, "❌ Failed to save transcript.")

    except Exception as e:
        logging.error(f"❌ Error processing podcast: {e}")
        await context.bot.send_message(chat_id, "❌ An error occurred during processing.")

# ✅ Telegram Message Handler
async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handles incoming messages and triggers processing."""
    message_text = update.message.text
    chat_id = update.message.chat_id

    logging.info(f"📥 Received message: {message_text}")

    if message_text.startswith("http"):
        await context.bot.send_message(chat_id, "🎙️ Processing podcast...")
        await process_podcast(message_text, chat_id, context)
    else:
        await context.bot.send_message(chat_id, "❌ Invalid URL. Please send a valid podcast link.")

# ✅ Webhook Route for Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    """Receives Telegram updates and processes them asynchronously."""
    try:
        update = Update.de_json(request.get_json(), bot)
        asyncio.run(handle_message(update, telegram_app.bot))
        return "OK", 200
    except Exception as e:
        logging.error(f"❌ Webhook processing error: {e}")
        return "Internal Server Error", 500

# ✅ Setup Webhook
async def setup_webhook():
    """Sets up Telegram webhook on deployment."""
    webhook_url = "https://audiotranscription-production.up.railway.app/webhook"
    await telegram_app.bot.setWebhook(webhook_url)
    logging.info(f"✅ Webhook set successfully: {webhook_url}")

# ✅ Initialize Bot
async def setup_bot():
    """Initializes bot and sets up webhook."""
    await telegram_app.initialize()
    await setup_webhook()
    await telegram_app.start()
    await telegram_app.run_webhook(listen="0.0.0.0", port=8080, url_path="webhook")

# ✅ Start Bot
if __name__ == "__main__":

loop = asyncio.get_event_loop()
loop.create_task(setup_bot())
loop.run_forever()
