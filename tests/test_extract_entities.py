import unittest
from src.rss_feed import RssFeed

class TestRssFeed(unittest.TestCase):
    def setUp(self):
        self.feed = RssFeed("https://example.com/rss")
        self.entry = {
            "title": "Sample Title",
            "summary": "Sample summary content mentioning Alice in Wonderland."
        }

    def test_extract_entities(self):
        entities = self.feed.extract_entities(self.entry)
        expected_entities = ["Alice (PERSON)", "Wonderland (LOC)"]  # Update expected_entities based on the NER model output
        self.assertTrue(any(entity in entities for entity in expected_entities))

if __name__ == "__main__":
    unittest.main()