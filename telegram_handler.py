import logging
from telegram import Update
from telegram.ext import ContextTypes
from audio_processor import download_audio
from transcriber import transcribe_audio
from notion_helper import save_transcript_to_notion

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming messages and handle URLs"""
    message_text = update.message.text.strip()
    
    if message_text.startswith("http"):
        logger.info(f"📥 Received URL: {message_text}")
        
        # Step 1: Download Audio
        audio_file = download_audio(message_text)
        if not audio_file:
            await update.message.reply_text("❌ Failed to download audio.")
            return
        
        # Step 2: Transcribe Audio
        transcript = transcribe_audio(audio_file)
        if not transcript:
            await update.message.reply_text("❌ Failed to transcribe audio.")
            return
        
        # Step 3: Save to Notion
        notion_url = save_transcript_to_notion(transcript)
        if not notion_url:
            await update.message.reply_text("❌ Failed to save transcript.")
            return
        
        await update.message.reply_text(f"✅ Transcript saved! {notion_url}")
    else:
        await update.message.reply_text("Send me a podcast link!")
