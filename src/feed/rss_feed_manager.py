from typing import Dict, List
import logging
import hashlib
from .rss_feed import RssFeed
from .kafka_producer import KafkaProducerService  # Import KafkaProducerService
from .elasticsearch_client import ElasticsearchClient  # Import ElasticsearchClient
from pyspark.sql import SparkSession  # Import SparkSession for PySpark

class RssFeedManager:
    def __init__(self, kafka_producer: KafkaProducerService = None, elasticsearch_client: ElasticsearchClient = None):
        """
        Initializes the RssFeedManager with an empty dictionary to hold RssFeed instances.
        Optionally initializes a Kafka producer and an Elasticsearch client for event publishing and searching.
        """
        self.feeds: Dict[str, RssFeed] = {}  # Dictionary to hold RssFeed instances
        self.kafka_producer = kafka_producer  # Initialize Kafka producer
        self.elasticsearch_client = elasticsearch_client  # Initialize Elasticsearch client

    def add_feed(self, feed: RssFeed) -> None:
        """
        Adds a new RssFeed instance to the manager.
        :param feed: An instance of RssFeed to add.
        """
        if feed.feed_url in self.feeds:
            logging.warning(f"Feed {feed.feed_url} is already in the manager.")
        else:
            self.feeds[feed.feed_url] = feed
            logging.info(f"Added feed: {feed.feed_url}")
            logging.debug(f"Current feeds after addition: {self.feeds}")  # Log the state after adding

    def remove_feed(self, feed_url: str) -> None:
        """
        Removes an RssFeed instance from the manager by its URL.
        :param feed_url: The URL of the feed to remove.
        """
        try:
            if feed_url in self.feeds:
                del self.feeds[feed_url]
                logging.info(f"Removed feed: {feed_url}")
            else:
                logging.warning(f"Feed {feed_url} not found in the manager.")
        except Exception as e:
            logging.error(f"Error removing feed {feed_url}: {str(e)}", exc_info=True)

    def list_feeds(self) -> List[str]:
        """
        Returns a list of all tracked feed URLs.
        :return: A list of feed URLs.
        """
        logging.info("Listing all tracked feed URLs.")
        logging.debug(f"Current feeds: {self.feeds}")  # Log the current state of feeds
        return list(self.feeds.keys())

    def publish_events_to_kafka(self, event_data: dict) -> None:
        """
        Publishes events to Kafka for downstream microservices to consume.
        :param event_data: The event data to publish.
        """
        if self.kafka_producer:
            self.kafka_producer.send_message(topic="feed-events", message=event_data)

    def fetch_all_feeds_sync(self) -> None:
        """
        Synchronously fetch all feeds in the manager.
        Updates the feed data by calling the fetch_feed method on each RssFeed instance.
        """
        logging.info("Fetching all feeds synchronously.")
        for feed in self.feeds.values():
            try:
                old_hash = feed.feed_hash  # Store old hash before fetching
                feed.fetch_feed()  # Fetch the feed data
                logging.info(f"Fetched feed: {feed.feed_url}")
                new_hash = self._compute_feed_hash(feed)  # Compute new hash
                feed.feed_hash = new_hash

                if old_hash != new_hash:
                    # If the feed has changed, publish an event
                    event_data = {"type": "feed_updated", "feed_url": feed.feed_url}
                    self.publish_events_to_kafka(event_data)

            except Exception as e:
                logging.error(f"Error fetching feed {feed.feed_url}: {e}", exc_info=True)

    def process_feeds_with_spark(self):
        """
        Processes all feeds using PySpark for distributed computing.
        """
        spark = SparkSession.builder.appName("RssFeedManagerProcessing").getOrCreate()
        all_entries = []

        for feed in self.feeds.values():
            feed.fetch_feed()  # Ensure the feed is fetched
            all_entries.extend(feed.entries)  # Collect all entries

        # Create a DataFrame from all entries
        df = spark.createDataFrame(all_entries)

        # Process the DataFrame for NLP tasks
        df.show()  # Display the DataFrame for demonstration purposes
        logging.info("Processed all feeds with Spark.")

    def apply_nlp_to_all_entries(self) -> None:
        """
        Applies NLP analysis (summarization, sentiment, emotion, entity extraction)
        across all entries of all feeds managed by this instance.
        """
        logging.info("Applying NLP analysis to all entries in all feeds.")
        for feed in self.feeds.values():
            for entry in feed.entries:
                try:
                    feed.apply_nlp_to_entry(entry)  # Apply NLP to the specific entry
                    logging.debug(f"Processed entry: {entry['title']}")
                except Exception as e:
                    logging.error(f"Error processing entry {entry['title']}: {str(e)}", exc_info=True)

    def translate_all_entries(self, target_language: str = "en") -> None:
        """
        Translates the summaries of all entries in all feeds to the target language.
        :param target_language: The target language code (default is English).
        """
        logging.info(f"Translating all entries to {target_language}.")
        for feed in self.feeds.values():
            for entry in feed.entries:
                try:
                    entry["translation"] = feed.translate_entry(entry, target_language)
                    logging.debug(f"Translated entry: {entry['title']} to {target_language}")
                except Exception as e:
                    logging.error(f"Error translating entry {entry['title']}: {str(e)}", exc_info=True)

    def semantic_search(self, query: str) -> List[Dict]:
        """
        Performs a semantic search on the Elasticsearch index based on the user query,
        including fuzzy matching to handle typos or similar queries.
        :param query: The search query string.
        :return: A list of matching entries from the Elasticsearch index.
        """
        if not self.elasticsearch_client:
            logging.error("Elasticsearch client is not initialized.")
            return []

        try:
            search_body = {
                "query": {
                    "match": {
                        "summary": {
                            "query": query,
                            "fuzziness": "AUTO"  # Enable fuzzy matching
                        }
                    }
                }
            }
            response = self.elasticsearch_client.client.search(index="rss_entries", body=search_body)
            hits = response.get("hits", {}).get("hits", [])
            results = [hit["_source"] for hit in hits]  # Extract the source from hits
            logging.info(f"Semantic search for query '{query}' returned {len(results)} results.")
            return results
        except Exception as e:
            logging.error(f"Error performing semantic search: {e}", exc_info=True)
            return []

    def _compute_feed_hash(self, feed: RssFeed) -> str:
        """
        Computes a hash of the current feed entries for comparison.
        :return: A string representing the computed hash.
        """
        try:
            hash_input = ''.join(entry['title'] + entry['summary'] for entry in feed.entries)
            feed_hash = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
            logging.info(f"Computed feed hash: {feed_hash}")
            return feed_hash
        except Exception as e:
            logging.error(f"Error computing feed hash: {e}", exc_info=True)
            raise