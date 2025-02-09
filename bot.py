import os
import logging
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

# ✅ **Logging Setup**
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ **Environment Variables**
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = "https://audiotranscription-production.up.railway.app/webhook"
PORT = int(os.getenv("PORT", 8080))

# ✅ **Initialize Flask**
app = Flask(__name__)

# ✅ **Initialize Telegram Application (FIXED)**
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
telegram_app.initialize()  # 🔥 Fix: Ensure the bot is initialized

# ✅ **Message Handler**
async def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    chat_id = update.message.chat_id

    logger.info(f"📥 Received message: {text}")

    if text.startswith("http"):
        await update.message.reply_text("🔄 Processing your podcast link...")
        process_podcast_link(text, chat_id)
    else:
        await update.message.reply_text("🤖 Send me a podcast link!")

# ✅ **Process Podcast Link**
def process_podcast_link(url, chat_id):
    """Process podcast and send a response"""
    logger.info(f"🎙️ Processing podcast: {url}")

    response_message = f"✅ Processed Podcast: {url}"
    
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": response_message},
    )

# ✅ **Webhook Route (FIXED)**
@app.route("/webhook", methods=["POST"])
async def webhook():
    """Receives updates from Telegram"""
    update = Update.de_json(request.get_json(), telegram_app.bot)

    logger.info(f"📬 Received Webhook Update: {update}")

    await telegram_app.process_update(update)  # 🔥 Fix: Ensure async processing

    return "OK", 200

# ✅ **Set Webhook**
def set_webhook():
    """Set the Telegram webhook"""
    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
        json={"url": WEBHOOK_URL},
    )
    
    if response.ok:
        logger.info(f"✅ Webhook set successfully: {WEBHOOK_URL}")
    else:
        logger.error(f"❌ Failed to set webhook: {response.text}")

# ✅ **Main Function**
if __name__ == "__main__":
    set_webhook()  # Set webhook on start
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info(f"🚀 Bot is running with webhook on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
