import logging
from kafka import KafkaProducer
import json

class KafkaProducerService:
    def __init__(self, bootstrap_servers='localhost:9092'):
        """
        Initializes the Kafka Producer.
        :param bootstrap_servers: The Kafka server address.
        """
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize messages to JSON
        )
        logging.info("Kafka Producer initialized.")

    def send_message(self, topic: str, message: dict) -> None:
        """
        Sends a message to the specified Kafka topic.
        :param topic: The Kafka topic to send the message to.
        :param message: The message to send (as a dictionary).
        """
        try:
            self.producer.send(topic, message)
            self.producer.flush()  # Ensure all messages are sent
            logging.info(f"Message sent to topic '{topic}': {message}")
        except Exception as e:
            logging.error(f"Failed to send message to Kafka: {e}", exc_info=True)

    def close(self):
        """
        Closes the Kafka producer connection.
        """
        self.producer.close()
        logging.info("Kafka Producer closed.")