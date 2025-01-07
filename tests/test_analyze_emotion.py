import unittest
from src.rss_feed import RssFeed

class TestRssFeedEmotion(unittest.TestCase):
    def setUp(self):
        self.feed = RssFeed("https://example.com/rss")
        self.entry = {
            "title": "Sample Title",
            "summary": "This is a sample summary text for testing emotions."
        }

    def test_analyze_emotion(self):
        expected_emotion_scores = {
            "joy": 0.5,
            "sadness": 0.2,
            "anger": 0.1,
            "fear": 0.1,
            "surprise": 0.1,
        }
        emotion_scores = self.feed.analyze_emotion(self.entry)
        self.assertEqual(emotion_scores, expected_emotion_scores)

if __name__ == "__main__":
    unittest.main()