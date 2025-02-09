import os
import logging
import asyncio
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters
from openai import OpenAI
from pydub import AudioSegment
import yt_dlp
import notion_client

# 🚀 Initialize Flask App
app = Flask(__name__)

# 🚀 Set up Logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 🚀 Load Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN is missing!")
    exit(1)

if not OPENAI_API_KEY:
    logger.error("❌ OPENAI_API_KEY is missing!")
    exit(1)

if not NOTION_API_KEY or not NOTION_DATABASE_ID:
    logger.error("❌ Notion credentials are missing!")
    exit(1)

# 🚀 Initialize Telegram Bot & Application
bot = Bot(token=TELEGRAM_TOKEN)
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

# 🚀 Initialize OpenAI & Notion Clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
notion = notion_client.Client(auth=NOTION_API_KEY)

# ✅ Ensure Bot is initialized
async def setup_bot():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook("https://audiotranscription-production.up.railway.app/webhook")
    logger.info("✅ Webhook set successfully")

# 🚀 Function to Download & Convert Audio
def download_and_convert_audio(url):
    """Downloads and converts podcast audio."""
    logger.info(f"🔽 Downloading audio from: {url}")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '64',  # Lower bitrate to reduce size
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # Convert to WAV and Check Size
    audio_path = "downloads/audio.wav"
    audio = AudioSegment.from_file(audio_path)
    if os.path.getsize(audio_path) > 25 * 1024 * 1024:  # If > 25MB, split
        chunks = split_audio(audio, 24 * 1024 * 1024)
        return chunks
    return [audio_path]

# 🚀 Function to Split Audio if Too Large
def split_audio(audio, max_size):
    """Splits audio into chunks under the max size limit."""
    chunks = []
    chunk_length = len(audio) // (len(audio) // (max_size // (1024 * 1024)))
    for i, chunk in enumerate(audio[::chunk_length]):
        chunk_path = f"downloads/audio_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks

# 🚀 Function to Transcribe Audio in Chunks
def transcribe_audio(chunks):
    """Transcribes audio chunks and merges results."""
    transcript = ""
    for i, chunk in enumerate(chunks):
        logger.info(f"🎙️ Transcribing chunk {i + 1} of {len(chunks)}...")
        with open(chunk, "rb") as audio_file:
            response = openai_client.Audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        transcript += response["text"] + "\n"
    return transcript

# 🚀 Function to Summarize Transcript
def summarize_text(text):
    """Summarizes podcast transcript with GPT-4."""
    logger.info("📝 Generating summary...")
    response = openai_client.Completion.create(
        model="gpt-4",
        prompt=f"Summarize this podcast transcript:\n{text}",
        max_tokens=200
    )
    return response.choices[0].text.strip()

# 🚀 Function to Store in Notion (Handles Large Text)
def save_to_notion(title, summary, transcript):
    """Stores transcript & summary in Notion (splitting large text)."""
    logger.info("📥 Storing transcript in Notion...")
    notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={"title": {"title": [{"text": {"content": title}}]}},
        children=[
            {"object": "block", "type": "paragraph", "paragraph": {"text": [{"text": {"content": summary}}]}},
            *split_text_to_notion_blocks(transcript)
        ]
    )

# 🚀 Function to Split Long Transcripts for Notion
def split_text_to_notion_blocks(text, max_chars=2000):
    """Splits transcript into Notion-compatible 2000-character blocks."""
    blocks = []
    for i in range(0, len(text), max_chars):
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"text": [{"text": {"content": text[i:i+max_chars]}}]}
        })
    return blocks

# 🚀 Handle incoming messages
async def handle_message(update: Update, context):
    """Handles incoming messages and processes podcasts."""
    if update.message:
        text = update.message.text
        chat_id = update.message.chat_id
        logger.info(f"📥 Received message: {text}")

        if text.startswith("http"):
            try:
                logger.info(f"📤 Sending confirmation message to {chat_id}")
                await context.bot.send_message(chat_id=chat_id, text=f"🎙️ Processing podcast: {text}")

                # ✅ Step 1: Download & Convert Audio
                audio_chunks = download_and_convert_audio(text)

                # ✅ Step 2: Transcribe
                transcript = transcribe_audio(audio_chunks)

                # ✅ Step 3: Summarize
                summary = summarize_text(transcript)

                # ✅ Step 4: Save to Notion
                save_to_notion("Podcast Summary", summary, transcript)

                # ✅ Step 5: Send back to Telegram
                await context.bot.send_message(chat_id=chat_id, text=f"✅ Transcription Complete!\n\nSummary:\n{summary}")
            except Exception as e:
                logger.error(f"❌ Error processing podcast: {e}")
                await context.bot.send_message(chat_id=chat_id, text=f"❌ Failed to process podcast.")

# ✅ Add message handler
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 🚀 Webhook Route
@app.route("/webhook", methods=["POST"])
async def webhook():
    """Process incoming Telegram updates via webhook"""
    try:
        update_data = request.get_json()
        logger.info(f"📬 Received Webhook Update: {update_data}")

        update = Update.de_json(update_data, bot)

        # ✅ Properly process the update
        await telegram_app.process_update(update)

        return "OK", 200
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        return "Internal Server Error", 500

# 🚀 Main Entry Point
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_bot())
    app.run(host="0.0.0.0", port=8080)
