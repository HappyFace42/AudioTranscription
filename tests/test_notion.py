import unittest
from notion_helper import create_notion_page

class TestNotion(unittest.TestCase):
    def test_create_page(self):
        """Ensure Notion page creation works."""
        url = create_notion_page("Test Page", "This is a test content")
        self.assertTrue(url.startswith("https://www.notion.so/"))

if __name__ == "__main__":
    unittest.main()
