import unittest
from src.rss_feed import RssFeed
from src.redis_client import RedisClient

class TestRssFeedCaching(unittest.TestCase):
    def setUp(self):
        self.redis_client = RedisClient()
        self.feed_url = "https://example.com/rss"
        self.feed = RssFeed(feed_url=self.feed_url, redis_client=self.redis_client)
        self.feed.title = "Example Feed"
        self.feed.description = "This is a test feed."
        self.feed.last_updated = None
        self.feed.entries = [{"title": "Test Entry", "summary": "This is a test summary."}]

    def test_store_feed_in_redis(self):
        self.feed.store_feed_in_redis()  # Store feed data in Redis
        retrieved_feed = self.feed.retrieve_feed_from_redis()  # Retrieve feed data from Redis

        self.assertIsNotNone(retrieved_feed)
        self.assertEqual(retrieved_feed["feed_url"], self.feed_url)
        self.assertEqual(retrieved_feed["title"], self.feed.title)
        self.assertEqual(retrieved_feed["description"], self.feed.description)
        self.assertEqual(retrieved_feed["entries"], self.feed.entries)

    def test_retrieve_nonexistent_feed(self):
        nonexistent_feed_url = "https://nonexistent.com/rss"
        self.feed.feed_url = nonexistent_feed_url
        retrieved_feed = self.feed.retrieve_feed_from_redis()  # Attempt to retrieve nonexistent feed

        self.assertIsNone(retrieved_feed)  # Should return None for nonexistent feed

if __name__ == "__main__":
    unittest.main()