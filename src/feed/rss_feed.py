import requests
import datetime
from typing import List, Dict, Optional
import feedparser  # Import feedparser to parse the RSS feed
import hashlib  # Import hashlib to compute hashes
import logging  # Import logging for logging errors and information
from .redis_client import RedisClient  # Import the RedisClient from the current package
from transformers import pipeline  # Import the pipeline from transformers
from googletrans import Translator  # Import the Translator from googletrans
from pyspark.sql import SparkSession  # Import SparkSession for PySpark

# Configure logging
logging.basicConfig(level=logging.INFO)

class RssFeed:
    def __init__(self,
                 feed_url: str,
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 last_updated: Optional[datetime.datetime] = None,
                 entries: Optional[List[Dict]] = None,
                 redis_client: Optional[RedisClient] = None):
        """
        :param feed_url: URL of the RSS feed
        :param title: Optional, feed's title if known upfront
        :param description: Optional, feed's description if known
        :param last_updated: Last fetch time (UTC)
        :param entries: Pre-parsed entries if available
        """
        self.feed_url = feed_url
        self.title = title
        self.description = description
        self.last_updated = last_updated
        self.entries = entries or []
        self.redis_client = redis_client or RedisClient()  # Initialize Redis client
        logging.info("Initializing RssFeed with URL: %s", self.feed_url)
        self.feed_hash = None  # Initialize feed_hash
        self.summarizer = pipeline("summarization")  # Initialize the summarization pipeline
        self.sentiment_analyzer = pipeline("sentiment-analysis")  # Initialize the sentiment analysis pipeline
        self.ner_model = pipeline("ner", aggregation_strategy="simple")  # Initialize the NER pipeline

    def to_spark_dataframe(self):
        """
        Converts feed entries to a PySpark DataFrame for distributed processing.
        """
        spark = SparkSession.builder.appName("RssFeedProcessing").getOrCreate()
        df = spark.createDataFrame(self.entries)
        logging.info("Converted feed entries to Spark DataFrame.")
        return df

    def process_entries_with_spark(self):
        """
        Process entries using PySpark for distributed NLP tasks.
        This is a placeholder for actual NLP processing logic.
        """
        df = self.to_spark_dataframe()
        # Example processing: Here you can integrate your NLP tasks using PySpark's MLlib or other libraries
        df.show()  # Display the DataFrame for demonstration purposes
        logging.info("Processed entries with Spark.")

    def fetch_feed(self) -> None:
        """
        Fetches the RSS feed data from the feed URL and updates the metadata and entries.
        """
        try:
            response = requests.get(self.feed_url, timeout=10)
            response.raise_for_status()  # Raise an error for bad responses
            raw_feed = response.text
            self.parse_feed(raw_feed)  # Call the parse_feed method to process the feed
            self.last_updated = datetime.datetime.utcnow()  # Update the last updated timestamp
            logging.info(f"Successfully fetched feed from {self.feed_url}")

            # Check for delta entries before storing in Redis
            old_hash = self.feed_hash
            self.feed_hash = self._compute_feed_hash()  # Update feed hash after parsing
            if old_hash is None or old_hash != self.feed_hash:
                self.store_feed_in_redis()  # Store feed data in Redis if changed
            else:
                logging.info(f"No changes detected for feed {self.feed_url}. Not storing in Redis.")
        except requests.RequestException as e:
            logging.error(f"Failed to fetch {self.feed_url}: {e}", exc_info=True)
            raise

    def parse_feed(self, raw_feed: str) -> None:
        """
        Parses raw feed data and updates the feed's attributes and entries.
        """
        try:
            parsed = feedparser.parse(raw_feed)

            # Update feed-level info if not set
            self.title = self.title or parsed.feed.get("title", "")
            self.description = self.description or parsed.feed.get("description", "")
            self.last_updated = datetime.datetime.utcnow()  # Update the last updated timestamp

            # Build a new list of entries
            new_entries = []
            for entry in parsed.entries:
                item = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", ""),
                    "authors": entry.get("authors", []),
                    "topics": [],
                    "sentiment": None,
                    "emotion": None,
                    "entities": [],
                    "translation": None,
                    "auto_category": None,
                }
                new_entries.append(item)

            self.entries = new_entries  # Update the entries list
            logging.info(f"Parsed {len(self.entries)} entries from {self.feed_url}")
        except Exception as e:
            logging.error(f"Failed to parse feed: {e}", exc_info=True)
            raise

    def store_feed_in_redis(self) -> None:
        """
        Stores the current feed data in Redis.
        """
        feed_data = {
            "feed_url": self.feed_url,
            "title": self.title,
            "description": self.description,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "entries": self.entries,
        }
        try:
            self.redis_client.client.set(self.feed_url, str(feed_data))  # Store serialized feed data
            logging.info(f"[INFO] Feed data for {self.feed_url} stored in Redis.")
        except Exception as e:
            logging.error(f"Failed to store feed data in Redis: {e}", exc_info=True)

    def retrieve_feed_from_redis(self) -> Optional[Dict]:
        """
        Retrieves the feed data from Redis.
        :return: The feed data as a dictionary if found, None otherwise.
        """
        try:
            feed_data = self.redis_client.client.get(self.feed_url)
            if feed_data:
                logging.info(f"[INFO] Feed data for {self.feed_url} retrieved from Redis.")
                return eval(feed_data)  # Convert string back to dictionary
            else:
                logging.warning(f"[WARNING] No feed data found for {self.feed_url} in Redis.")
                return None
        except Exception as e:
            logging.error(f"Failed to retrieve feed data from Redis: {e}", exc_info=True)
            return None

    def summarize_entry(self, entry: Dict) -> str:
        """
        Creates a concise summary of the entry's content using a pre-trained model.
        """
        try:
            # Combine title and summary to create input for summarization
            input_text = f"{entry['title']} {entry['summary']}"
            summary = self.summarizer(input_text, max_length=50, min_length=25, do_sample=False)
            logging.info(f"Summarized entry: {summary[0]['summary_text']}")
            return summary[0]['summary_text']  # Return the summarized text
        except Exception as e:
            logging.error(f"Error summarizing entry: {e}", exc_info=True)
            return "Summary could not be generated."

    def apply_nlp_to_all_entries(self) -> None:
        """
        Applies summarization and sentiment analysis to all feed entries.
        """
        try:
            for entry in self.entries:
                entry["summary"] = self.summarize_entry(entry)  # Update the entry with the summarized text
                entry["sentiment"] = self.analyze_sentiment(entry)  # Update the entry with the sentiment score
            logging.info("Applied NLP to all entries.")
        except Exception as e:
            logging.error(f"Error applying NLP to all entries: {e}", exc_info=True)

    def apply_nlp_to_entry(self, entry: Dict) -> None:
        """
        Applies NLP processing to a single entry.
        :param entry: The entry dictionary to process.
        """
        try:
            entry["summary"] = self.summarize_entry(entry)
            entry["sentiment"] = self.analyze_sentiment(entry)
            entry["emotion"] = self.analyze_emotion(entry)
            entry["entities"] = self.extract_entities(entry)
            logging.info(f"Applied NLP to entry: {entry['title']}")
        except Exception as e:
            logging.error(f"Error applying NLP to entry {entry['title']}: {e}", exc_info=True)

    def translate_entry(self, entry: Dict, target_language: str = "en") -> str:
        """
        Translates entry summary to the target language using the Google Translate API.
        Caches the translated summary to avoid repeated translation requests.
        :param entry: The entry dictionary containing the summary to be translated.
        :param target_language: The target language code (default is English).
        :return: A string representing the translated summary.
        """
        # Check if the translation is already cached
        cache_key = f"{entry['title']}_{target_language}"
        cached_translation = self.redis_client.client.get(cache_key)

        if cached_translation:
            logging.info(f"Retrieved cached translation for entry: {entry['title']} to {target_language}")
            return cached_translation.decode('utf-8')  # Decode from bytes to string

        translator = Translator()  # Initialize the Translator
        try:
            # Translate the summary of the entry
            translation = translator.translate(entry['summary'], dest=target_language)
            logging.info(f"Translated entry: {entry['title']} to {target_language}")

            # Store the translation in cache
            self.redis_client.client.set(cache_key, translation.text)
            return translation.text  # Return the translated text
        except Exception as e:
            logging.error(f"Error translating entry: {e}", exc_info=True)
            return entry['summary']  # Return original summary in case of error

    def analyze_sentiment(self, entry: Dict) -> float:
        """
        Calculates a sentiment score using a pre-trained model.
        """
        try:
            # Analyze sentiment using the sentiment analysis pipeline
            result = self.sentiment_analyzer(entry['summary'])
            sentiment_score = result[0]['score'] if result[0]['label'] == 'POSITIVE' else -result[0]['score']
            logging.info(f"Analyzed sentiment for entry: {entry['title']} - Score: {sentiment_score}")
            return sentiment_score
        except Exception as e:
            logging.error(f"Error analyzing sentiment: {e}", exc_info=True)
            return 0.0  # Return neutral sentiment score in case of error

    def analyze_emotion(self, entry: Dict) -> Dict[str, float]:
        """
        Classifies content into various emotions (joy, sadness, anger, etc.).
        Placeholder implementation that returns fixed scores for demonstration purposes.
        """
        # Placeholder implementation for emotion analysis
        return {
            "joy": 0.5,
            "sadness": 0.2,
            "anger": 0.1,
            "fear": 0.1,
            "surprise": 0.1,
        }

    def _compute_feed_hash(self) -> str:
        """
        Computes a hash of the current feed entries for comparison.
        :return: A string representing the computed hash.
        """
        try:
            hash_input = ''.join(entry['title'] + entry['summary'] for entry in self.entries)
            feed_hash = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
            logging.info(f"Computed feed hash: {feed_hash}")
            return feed_hash
        except Exception as e:
            logging.error(f"Error computing feed hash: {e}", exc_info=True)
            raise

    def get_delta_entries(self, old_hash: str) -> List[Dict]:
        """
        Returns only entries that are new or changed compared to old_hash.
        """
        new_entries = []
        current_hash = self._compute_feed_hash()  # Compute the current hash

        # If the hash is the same, return an empty list
        if current_hash == old_hash:
            return new_entries

        # Otherwise, find new or changed entries
        for entry in self.entries:
            # Assuming each entry has a unique title for simplicity
            entry_hash = hashlib.md5((entry["title"] + entry["summary"]).encode("utf-8")).hexdigest()
            if entry_hash != old_hash:
                new_entries.append(entry)

        return new_entries

    def extract_entities(self, entry: Dict) -> List[str]:
        """
        Performs named entity recognition (NER) on the title and summary of the entry.
        :param entry: The entry dictionary containing title and summary.
        :return: A list of recognized entities with their types.
        """
        try:
            # Combine title and summary for entity recognition
            input_text = f"{entry['title']} {entry['summary']}"
            entities = self.ner_model(input_text)

            # Format entities to return a list of strings with the format "entity (type)"
            recognized_entities = [f"{entity['word']} ({entity['entity_group']})" for entity in entities]
            logging.info(f"Extracted entities: {recognized_entities}")
            return recognized_entities
        except Exception as e:
            logging.error(f"Error extracting entities: {e}", exc_info=True)
            return []