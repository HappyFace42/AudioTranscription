import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ✅ OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Notion API Key & Page ID
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")  # Make sure this is a PAGE ID, not a database ID!

# ✅ Audio Processing Config
DOWNLOADS_FOLDER = "downloads"
MAX_FILE_SIZE_MB = 25  # OpenAI limit is 25MB
