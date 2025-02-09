import os
import asyncio
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# ✅ Load Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN is missing!")

# ✅ Initialize Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Flask Web Server
app = Flask(__name__)

# ✅ Initialize Telegram Bot
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# 📝 Command: Start
async def start(update: Update, context):
    await update.message.reply_text("🤖 Bot is online! Send a podcast URL to process.")

# 🎧 Message Handler
async def handle_message(update: Update, context):
    text = update.message.text
    chat_id = update.message.chat_id
    logging.info(f"📥 Received message from {chat_id}: {text}")

    if text.startswith("http"):
        response_message = f"🔗 Processing your link: {text}"
    else:
        response_message = "❌ Please send a valid URL."

    await context.bot.send_message(chat_id=chat_id, text=response_message)

# ✅ Register Handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 📡 Webhook Route
@app.route("/webhook", methods=["POST"])
def webhook():
    """Receives updates from Telegram and processes them."""
    update = Update.de_json(request.get_json(), telegram_app.bot)
    logging.info(f"📬 Received Webhook Update: {update.to_dict()}")
    
    asyncio.create_task(telegram_app.process_update(update))  # Process update asynchronously
    return "OK", 200

# ✅ Flask Web Server
def run_flask():
    """Runs the Flask server for webhook handling."""
    app.run(host="0.0.0.0", port=8080)

# ✅ Main Execution
if __name__ == "__main__":
    logging.info("🚀 Starting bot...")

    # Run Flask in a separate thread
    from threading import Thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Run Telegram webhook
    loop = asyncio.get_event_loop()
    loop.create_task(telegram_app.run_webhook(listen="0.0.0.0", port=8080, url_path="webhook"))
    loop.run_forever()
