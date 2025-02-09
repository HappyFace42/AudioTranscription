import os
import logging
import asyncio
import requests

from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# ✅ Enable logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ✅ Load Telegram bot token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN is missing!")
    raise ValueError("❌ TELEGRAM_BOT_TOKEN is missing!")

# ✅ Initialize Flask app
app = Flask(__name__)

# ✅ Initialize Telegram bot application
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

# ✅ Create event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


### 📌 BOT COMMAND HANDLERS

async def start(update: Update, context):
    """Start command"""
    await update.message.reply_text("👋 Hello! Send me a podcast link, and I'll transcribe it!")


async def handle_message(update: Update, context):
    """Handle user messages"""
    text = update.message.text
    chat_id = update.message.chat_id

    logger.info(f"📥 Received message: {text}")

    if text.startswith("http"):
        try:
            await context.bot.send_message(chat_id=chat_id, text="🎙️ Processing podcast: " + text)
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
    else:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid link! Please send a valid podcast URL.")


# ✅ Add handlers
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

        # ✅ FIXED: Properly handle updates asynchronously
        asyncio.create_task(telegram_app.process_update(update))

        return "OK", 200
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        return "Internal Server Error", 500


### 📌 SETUP & RUN BOT

async def setup_bot():
    """Initialize and start the bot"""
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

    # ✅ Ensure application is initialized
    await telegram_app.initialize()
    logger.info("🚀 Bot is running with webhook on port 8080")


# ✅ Run bot setup in the background
asyncio.create_task(setup_bot())

# ✅ Start Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
