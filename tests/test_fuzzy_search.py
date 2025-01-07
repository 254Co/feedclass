import unittest
from unittest.mock import MagicMock
from src.rss_feed_manager import RssFeedManager
from src.elasticsearch_client import ElasticsearchClient

class TestRssFeedManagerFuzzySearch(unittest.TestCase):
    def setUp(self):
        self.elasticsearch_client = ElasticsearchClient()
        self.manager = RssFeedManager(elasticsearch_client=self.elasticsearch_client)

        # Mocking the response from Elasticsearch
        self.elasticsearch_client.client = MagicMock()
        self.elasticsearch_client.client.search.return_value = {
            "hits": {
                "hits": [
                    {"_source": {"title": "Test Title 1", "summary": "Test Summary 1"}},
                    {"_source": {"title": "Test Title 2", "summary": "Test Summary 2"}},
                ]
            }
        }

    def test_fuzzy_search(self):
        query = "Test Summery"  # Intentional typo
        results = self.manager.semantic_search(query)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "Test Title 1")
        self.assertEqual(results[1]["title"], "Test Title 2")

if __name__ == "__main__":
    unittest.main()