import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# ✅ Setup Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_TOKEN")  # ✅ Ensure this is set
if not TOKEN:
    logging.error("❌ TELEGRAM_TOKEN is missing! Set it in Railway Variables.")
    exit(1)

# ✅ Initialize Bot
telegram_app = Application.builder().token(TOKEN).build()

# ✅ Define Command Handlers
async def start(update: Update, context):
    await update.message.reply_text("Hello! Send me a podcast link to transcribe.")

async def process_message(update: Update, context):
    text = update.message.text
    logging.info(f"📥 Received message: {text}")
    await update.message.reply_text(f"🎙️ Processing podcast: {text}")

# ✅ Add Handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))

# ✅ Initialize Flask Webhook
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        update = Update.de_json(request.json, telegram_app.bot)
        logging.info(f"📬 Received Webhook Update: {update}")

        await telegram_app.process_update(update)  # ✅ Ensure Async Processing

        return "OK", 200
    except Exception as e:
        logging.error(f"❌ Webhook processing error: {e}")
        return "Error", 500

async def start_bot():
    """ ✅ Initialize and Run Telegram Bot """
    await telegram_app.initialize()  # ✅ Required Fix
    await telegram_app.start()
    logging.info("🚀 Telegram Bot is ready!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())  # ✅ Start the bot properly
    app.run(host="0.0.0.0", port=8080)  # ✅ Webhook Server
