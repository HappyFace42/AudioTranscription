import asyncio
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# --- CONFIG VARIABLES ---
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
WEBHOOK_URL = "https://audiotranscription-production.up.railway.app/webhook"

# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FLASK APP ---
app = Flask(__name__)

# --- TELEGRAM BOT SETUP ---
telegram_app = Application.builder().token(TOKEN).build()

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Handles incoming Telegram updates via webhook."""
    update = Update.de_json(request.get_json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK", 200

async def start_bot():
    """Starts the Telegram bot and sets the webhook."""
    logger.info("🚀 Starting bot...")
    
    # Set Webhook
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}")

    # Run Flask server
    app.run(host="0.0.0.0", port=8080)

# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    try:
        asyncio.run(start_bot())  # Starts event loop properly
    except RuntimeError as e:
        logger.error(f"❌ RuntimeError: {e} - Trying alternative loop handling.")
        
        # Fallback: Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_bot())
