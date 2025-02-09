import logging
import os
import requests
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from extract_audio import extract_audio_url, download_audio
from transcriber import transcribe_audio
from notion_helper import create_notion_page
from config import TELEGRAM_BOT_TOKEN, DOWNLOADS_FOLDER

WEBHOOK_URL = "audiotranscription-production.up.railway.app"

# ✅ Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Initialize Telegram Bot
app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def start(update: Update, context: CallbackContext) -> None:
    """Handles /start command."""
    await update.message.reply_text("👋 Send me a podcast link, and I'll transcribe it for you!")

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handles incoming messages."""
    url = update.message.text
    logger.info(f"📥 Received link: {url}")

    audio_url, podcast_title = extract_audio_url(url)
    if not audio_url:
        await update.message.reply_text("❌ Failed to extract audio. Please try another link.")
        return

    await update.message.reply_text(f"✅ Found Audio URL: {audio_url}")
    file_path = download_audio(audio_url, DOWNLOADS_FOLDER)
    
    if not file_path:
        await update.message.reply_text("❌ Failed to download audio.")
        return
A    
    await update.message.reply_text("✅ Download complete. Transcribing...")
    transcript = transcribe_audio(file_path)

    if not transcript:
        await update.message.reply_text("❌ Transcription failed.")
        return
    
    notion_url = create_notion_page(podcast_title, transcript)
    
    if notion_url:
        await update.message.reply_text(f"✅ Notion Page Created: {notion_url}")
    else:
        await update.message.reply_text("❌ Failed to create Notion page.")

# ✅ Register Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    logger.info("🚀 Bot is starting...")
    app.run_polling()
