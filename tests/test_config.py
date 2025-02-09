import pytest
import config

def test_env_variables():
    assert config.TELEGRAM_BOT_TOKEN, "TELEGRAM_BOT_TOKEN is missing!"
    assert config.OPENAI_API_KEY, "OPENAI_API_KEY is missing!"
    assert config.NOTION_API_KEY, "NOTION_API_KEY is missing!"
