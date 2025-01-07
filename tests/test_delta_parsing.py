import unittest
from src.rss_feed import RssFeed
from src.redis_client import RedisClient

class TestDeltaParsing(unittest.TestCase):
    def setUp(self):
        self.redis_client = RedisClient()
        self.feed_url = "https://example.com/rss"
        self.feed = RssFeed(feed_url=self.feed_url, redis_client=self.redis_client)
        self.feed.title = "Example Feed"
        self.feed.description = "This is a test feed."
        self.feed.last_updated = None
        self.feed.entries = [{"title": "Test Entry", "summary": "This is a test summary."}]
        self.feed.fetch_feed()  # Initial fetch to store the original state

    def test_delta_parsing(self):
        # Modify the entry to simulate a change
        self.feed.entries[0]["summary"] = "This is a modified summary."
        self.feed.fetch_feed()  # Fetch again to check if it stores the changed entry

        # Retrieve the feed from Redis
        retrieved_feed = self.feed.retrieve_feed_from_redis()
        self.assertIsNotNone(retrieved_feed)
        self.assertEqual(retrieved_feed["entries"][0]["summary"], "This is a modified summary.")

    def tearDown(self):
        # Clean up the Redis data after the test
        self.redis_client.client.delete(self.feed_url)

if __name__ == "__main__":
    unittest.main()