import os
import logging
import requests
import asyncio

from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# ✅ Enable logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ✅ Load Telegram bot token from environment variable
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN is missing!")
    raise ValueError("❌ TELEGRAM_BOT_TOKEN is missing!")

# ✅ Initialize Flask app
app = Flask(__name__)

# ✅ Initialize Telegram Application (async-ready)
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()


### 📌 BOT COMMAND HANDLERS

async def start(update: Update, context):
    """Start command"""
    await update.message.reply_text("👋 Hello! Send me a podcast link, and I'll transcribe it!")


async def handle_message(update: Update, context):
    """Handle messages from users"""
    text = update.message.text
    chat_id = update.message.chat_id

    logger.info(f"📥 Received message: {text}")

    if text.startswith("http"):
        await context.bot.send_message(chat_id=chat_id, text="🎙️ Processing podcast: " + text)
        # TODO: Add podcast download & transcription logic here
    else:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid link! Please send a valid podcast URL.")


# ✅ Add handlers to the Telegram bot
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


### 📌 WEBHOOK HANDLING

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot is running!", 200


@app.route("/webhook", methods=["POST"])
async def webhook():
    """Handle incoming Telegram updates via webhook"""
    try:
        update_data = request.get_json()
        logger.info(f"📬 Received Webhook Update: {update_data}")

        update = Update.de_json(update_data, telegram_app.bot)
        
        # ✅ Properly initialize bot before processing update
        await telegram_app.initialize()
        await telegram_app.process_update(update)
        
        return "OK", 200
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        return "Internal Server Error", 500


### 📌 SETUP & RUN BOT

async def main():
    """Start the bot"""
    logger.info("🚀 Setting webhook if needed...")

    webhook_url = "https://audiotranscription-production.up.railway.app/webhook"

    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
        json={"url": webhook_url}
    )

    if response.ok:
        logger.info(f"✅ Webhook set successfully: {webhook_url}")
    else:
        logger.error(f"❌ Failed to set webhook: {response.text}")

    # ✅ Ensure application is initialized before processing requests
    await telegram_app.initialize()
    logger.info("🚀 Bot is running with webhook on port 8080")


if __name__ == "__main__":
    # ✅ Start the bot asynchronously
    asyncio.run(main())

    # ✅ Start Flask app
    app.run(host="0.0.0.0", port=8080)
