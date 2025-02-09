import os
import logging
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔥 Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN is missing!")
    exit(1)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("⚠️ Warning: OPENAI_API_KEY is missing! Some features may not work.")

WEBHOOK_URL = "https://audiotranscription-production.up.railway.app/webhook"

# Flask Web Server
app = Flask(__name__)

# Telegram Bot Setup
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

# ✅ Set Webhook on Start
async def set_webhook():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}"
    response = requests.get(url)
    if response.status_code == 200:
        logger.info(f"✅ Webhook set successfully: {WEBHOOK_URL}")
    else:
        logger.error(f"❌ Failed to set webhook: {response.json()}")

# 📩 Handle Incoming Messages
async def handle_message(update: Update, context):
    user_text = update.message.text
    logger.info(f"📥 Received message: {user_text}")

    if user_text.startswith("http"):
        await update.message.reply_text("🔄 Processing your podcast link...")

        # Simulate processing...
        await update.message.reply_text("✅ Transcription complete!")

# �� Webhook Route
@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        update = Update.de_json(request.get_json(), telegram_app.bot)
        logger.info(f"📬 Received Webhook Update: {update}")

        await telegram_app.process_update(update)
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        return "Internal Server Error", 500
    return "OK", 200

# 🚀 Start Flask Server
if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())

    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run(host="0.0.0.0", port=8080)
