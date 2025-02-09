import unittest
from notion_helper import create_notion_page

class TestNotionHelper(unittest.TestCase):
    def test_create_notion_page(self):
        response = create_notion_page("Test Title", "Test Content")
        self.assertTrue(response.startswith("https://www.notion.so/"), "Notion page URL invalid!")

if __name__ == "__main__":
    unittest.main()
