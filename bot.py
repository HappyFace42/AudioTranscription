import os
import logging
import asyncio
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# 🚀 Initialize Flask App
app = Flask(__name__)

# 🚀 Set up Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🚀 Load Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN is missing!")
    exit(1)

# 🚀 Initialize Telegram Bot
bot = Bot(token=TELEGRAM_TOKEN)
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

# ✅ Ensure Bot is initialized
async def setup_bot():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook("https://audiotranscription-production.up.railway.app/webhook")
    logger.info("✅ Webhook set successfully")

# 🚀 Command: Start
async def start(update: Update, context):
    """Handle /start command"""
    await update.message.reply_text("👋 Hello! Send me a podcast URL to process.")

# 🚀 Handle incoming messages
async def handle_message(update: Update, context):
    """Handle user messages and reply"""
    text = update.message.text
    chat_id = update.message.chat_id

    logger.info(f"📥 Received message: {text}")

    if text.startswith("http"):
        try:
            logger.info(f"📤 Sending processing message to {chat_id}")
            await context.bot.send_message(chat_id=chat_id, text="🎙️ Processing podcast: " + text)

            # ✅ Ensure proper Telegram API request
            response = await context.bot.send_message(chat_id=chat_id, text="✅ Message received!")

            if response:
                logger.info(f"📤 Message successfully sent to {chat_id}")

        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
    else:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid link! Please send a valid podcast URL.")

# 🚀 Webhook Route
@app.route("/webhook", methods=["POST"])
async def webhook():
    """Handle incoming Telegram updates via webhook"""
    try:
        update_data = request.get_json()
        logger.info(f"📬 Received Webhook Update: {update_data}")

        update = Update.de_json(update_data, bot)

        # ✅ FIXED: Properly process updates asynchronously
        await telegram_app.process_update(update)

        return "OK", 200
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        return "Internal Server Error", 500

# 🚀 Main Entry Point
if __name__ == "__main__":
    asyncio.run(setup_bot())  # ✅ Properly initializes the bot
    app.run(host="0.0.0.0", port=8080)
