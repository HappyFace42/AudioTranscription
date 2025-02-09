import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL
from telegram_handler import handle_message

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app for webhook
app = Flask(__name__)

# Telegram Bot Application
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

@app.route("/webhook", methods=["POST"])
async def webhook():
    """Process incoming Telegram messages via webhook"""
    update = Update.de_json(request.get_json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK", 200

# Register handlers
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def set_webhook():
    """Set webhook with proper retry handling"""
    try:
        await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"✅ Webhook set: {WEBHOOK_URL}")
    except Exception as e:
        logger.error(f"❌ Webhook setup failed: {e}")
        await asyncio.sleep(5)  # Wait before retrying
        await set_webhook()

async def start_bot():
    """Start the bot using webhook mode"""
    await set_webhook()
    runner = asyncio.create_task(telegram_app.run_webhook(port=8080))
    await runner

if __name__ == "__main__":
    logger.info("🚀 Starting bot...")
    
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(start_bot())  # If already running, schedule as a task
    else:
        asyncio.run(start_bot())  # Normal case
