import logging
from notion_client import Client
from config import NOTION_API_KEY, NOTION_PAGE_ID

notion = Client(auth=NOTION_API_KEY)
logger = logging.getLogger(__name__)

def save_transcript_to_notion(transcript: str) -> str:
    """Saves transcript to Notion and returns the page URL."""
    try:
        page = notion.pages.create(
            parent={"database_id": NOTION_PAGE_ID},
            properties={"title": {"title": [{"text": {"content": "Podcast Transcript"}}]}},
            children=[{"object": "block", "type": "paragraph", "paragraph": {"text": [{"text": {"content": transcript}}]}}],
        )
        return page["url"]
    except Exception as e:
        logger.error(f"❌ Notion save failed: {e}")
        return None
