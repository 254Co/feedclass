import logging
from .rss_feed_manager import RssFeedManager  # Import the RssFeedManager

class NlpProcessor:
    def __init__(self, feed_manager: RssFeedManager):
        self.feed_manager = feed_manager  # Initialize with the RssFeedManager

    def process_entry(self, entry: dict):
        """
        Processes an incoming feed entry by applying NLP tasks.
        :param entry: The feed entry to process.
        """
        try:
            # Assuming the entry is in the expected format
            feed_url = entry.get("feed_url")
            if feed_url in self.feed_manager.feeds:
                feed = self.feed_manager.feeds[feed_url]
                # Apply NLP processing to the specific entry
                feed.apply_nlp_to_entry(entry)  # Apply NLP to the specific entry
                logging.info(f"Processed entry for feed: {feed_url}")
            else:
                logging.warning(f"Feed URL {feed_url} not found in manager.")
        except Exception as e:
            logging.error(f"Error processing entry: {entry}, error: {e}", exc_info=True)

    def apply_nlp_to_entry(self, entry: dict):
        """
        Applies NLP processing to a single entry.
        :param entry: The entry dictionary to process.
        """
        try:
            feed_url = entry.get("feed_url")
            if feed_url in self.feed_manager.feeds:
                feed = self.feed_manager.feeds[feed_url]
                feed.apply_nlp_to_entry(entry)  # Apply NLP to the specific entry
                logging.info(f"Applied NLP to entry for feed: {feed_url}")
            else:
                logging.warning(f"Feed URL {feed_url} not found in manager.")
        except Exception as e:
            logging.error(f"Error applying NLP to entry: {entry}, error: {e}", exc_info=True)