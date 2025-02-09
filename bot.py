import logging
import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# 🔥 Enable Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🔑 Load Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = "https://audiotranscription-production.up.railway.app/webhook"

# ✅ Validate API Keys
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN is missing!")
    exit(1)

if not OPENAI_API_KEY:
    logger.error("❌ OPENAI_API_KEY is missing!")
    exit(1)

# 🔥 Initialize Flask App
app = Flask(__name__)

# 🔥 Initialize Telegram Bot
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    chat_id = update.message.chat_id
    logger.info(f"✅ /start command from {chat_id}")
    await context.bot.send_message(chat_id=chat_id, text="Hello! Send me a podcast link to transcribe.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages (URLs)."""
    message_text = update.message.text
    chat_id = update.message.chat_id

    logger.info(f"📥 Received message from {chat_id}: {message_text}")

    # ✅ Reply to the user
    await context.bot.send_message(chat_id=chat_id, text="✅ Processing your request...")

    # 🔥 Process OpenAI API Call (example placeholder)
    response_text = f"🔊 Received podcast link: {message_text}"
    await context.bot.send_message(chat_id=chat_id, text=response_text)


# ✅ Register Handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


@app.route("/webhook", methods=["POST"])
async def webhook():
    """Handle incoming Telegram Webhook updates."""
    try:
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        logger.info(f"📬 Received Webhook Update: {update}")

        await telegram_app.process_update(update)  # ✅ Await process_update

        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {str(e)}")
        return jsonify({"error": str(e)}), 500


async def set_webhook():
    """Set Telegram Webhook."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    response = requests.post(url, json={"url": WEBHOOK_URL})

    if response.status_code == 200:
        logger.info(f"✅ Webhook set successfully: {WEBHOOK_URL}")
    else:
        logger.error(f"❌ Failed to set webhook: {response.text}")


if __name__ == "__main__":
    logger.info("🚀 Setting webhook if needed...")
    asyncio.run(set_webhook())

    logger.info("🚀 Bot is running with webhook on port 8080")
    app.run(host="0.0.0.0", port=8080)
