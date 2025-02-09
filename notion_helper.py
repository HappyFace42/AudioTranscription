import requests
import logging
import openai
import unicodedata
from config import NOTION_API_KEY, NOTION_PAGE_ID, OPENAI_API_KEY

logger = logging.getLogger("notion_helper")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def clean_text(text: str) -> str:
    """Removes weird encoding characters."""
    return unicodedata.normalize("NFKC", text).replace("Â", "").replace("â", "-").replace("", "-").strip()

def extract_actionable_points(transcription: str) -> str:
    """Generates structured, well-formatted actionable insights from the transcript using GPT."""
    logger.info("📝 Extracting actionable insights using GPT...")

    if len(transcription) < 500:
        return "**Actionable insights unavailable** (Transcript too short)."

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Extract key actionable insights from this podcast in a structured way, using bullet points with **bolded key takeaways**."},
                {"role": "user", "content": transcription[:8000]}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"❌ OpenAI API Error: {e}")
        return "**Actionable insights unavailable**."

def split_text(text, chunk_size=2000):
    """Splits text into chunks of max 2000 characters."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def create_notion_page(podcast_title: str, full_transcription: str) -> str:
    """Creates a Notion page with podcast details."""
    clean_title = clean_text(podcast_title)
    actionable_points = extract_actionable_points(full_transcription)

    blocks = [
        # ✅ Podcast Title (as a heading)
        {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": clean_title}}]}},
        
        # ✅ Actionable Insights Section
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "🎯 Actionable Insights"}}]}},
    ]

    # ✅ Split "Actionable Insights" into multiple blocks
    actionable_chunks = split_text(actionable_points, 2000)
    for chunk in actionable_chunks:
        blocks.append(
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": chunk}}]}}
        )

    # ✅ Divider
    blocks.append({"object": "block", "type": "divider", "divider": {}})

    # ✅ Full Transcript Section
    blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "📜 Full Transcript".encode("utf-8").decode("utf-8")}}]}})

    # ✅ Split transcript into multiple blocks
    transcript_chunks = split_text(full_transcription, 2000)
    for chunk in transcript_chunks:
        blocks.append(
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": chunk}}]}}
        )

    data = {
        "parent": {"page_id": NOTION_PAGE_ID},
        "properties": {
            "title": {"title": [{"text": {"content": clean_title}}]}
        },
        "children": blocks
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=NOTION_HEADERS, json=data)
    if response.status_code == 200:
        notion_url = response.json().get("url")
        logger.info(f"✅ Notion Page Created: {notion_url}")
        return notion_url
    else:
        logger.error(f"❌ Failed to create Notion page: {response.text}")
        return "Failed to create Notion page."
