import unittest
from src.rss_feed import RssFeed

class TestRssFeedSummarization(unittest.TestCase):
    def setUp(self):
        self.feed = RssFeed(feed_url="https://example.com/rss")
        self.feed.entries = [
            {
                "title": "Sample Entry",
                "summary": "This is a long summary of the sample entry that needs to be summarized."
            }
        ]

    def test_summarize_entry(self):
        summary = self.feed.summarize_entry(self.feed.entries[0])
        self.assertIsInstance(summary, str)  # Ensure the output is a string
        self.assertGreater(len(summary), 0)  # Ensure the summary is not empty

if __name__ == '__main__':
    unittest.main()