import unittest
from notion_helper import create_notion_page

class TestNotion(unittest.TestCase):
    def test_create_page(self):
        """Ensure Notion page creation works."""
        test_title = "Test Notion Page"
        test_summary = "This is a test summary for Notion page."
        
        notion_page_url = create_notion_page(test_title, test_summary)  # ✅ Only 2 arguments
        print("✅ Notion Page Created:", notion_page_url)
        
        self.assertTrue(notion_page_url.startswith("https://www.notion.so/"))

if __name__ == "__main__":
    unittest.main()
