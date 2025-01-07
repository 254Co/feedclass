import unittest
from src.rss_feed_manager import RssFeedManager
from src.rss_feed import RssFeed
import logging

class TestRssFeedManager(unittest.TestCase):
    def setUp(self):
        self.manager = RssFeedManager()
        self.feed1 = RssFeed("https://example.com/rss1")
        self.feed2 = RssFeed("https://example.com/rss2")
        self.manager.add_feed(self.feed1)
        self.manager.add_feed(self.feed2)

    def test_list_feeds(self):
        logging.info("Testing the list_feeds method.")
        expected_feeds = ["https://example.com/rss1", "https://example.com/rss2"]
        self.assertListEqual(sorted(self.manager.list_feeds()), sorted(expected_feeds))

if __name__ == '__main__':
    unittest.main()