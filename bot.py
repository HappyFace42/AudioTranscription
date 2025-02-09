import os
import logging
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = "https://audiotranscription-production.up.railway.app/webhook"  # Your Webhook URL
PORT = int(os.getenv("PORT", 8080))  # Default port to 8080

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Flask App
app = Flask(__name__)

# Initialize Telegram Bot Application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

### ✅ TELEGRAM HANDLERS ###

async def start(update: Update, context: CallbackContext) -> None:
    """Responds to /start command."""
    await update.message.reply_text("Hello! Send me a link and I'll process it!")

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handles incoming messages."""
    text = update.message.text
    logging.info(f"📥 Received message: {text}")
    await update.message.reply_text(f"You said: {text}")

# Add Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

### ✅ FLASK ROUTES ###

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """Receives Telegram updates via webhook."""
    update_data = request.get_json()
    if update_data:
        update = Update.de_json(update_data, application.bot)
        application.update_queue.put_nowait(update)
    return "OK", 200

### ✅ WEBHOOK SETUP FUNCTION ###

def set_webhook():
    """Sets the webhook for the bot."""
    webhook_url = f"https://audiotranscription-production.up.railway.app/webhook"
    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
        json={"url": webhook_url}
    )
    result = response.json()
    
    if result.get("ok"):
        logging.info(f"✅ Webhook set successfully: {webhook_url}")
    else:
        logging.error(f"❌ Failed to set webhook: {result}")

if __name__ == "__main__":
    # Set the webhook only if not already set
    logging.info("🚀 Setting webhook if needed...")
    set_webhook()

    # Start Flask server
    logging.info(f"🚀 Bot is running with webhook on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
