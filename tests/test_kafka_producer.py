import unittest
from src.kafka_producer import KafkaProducerService
import time
from kafka import KafkaConsumer

class TestKafkaProducerService(unittest.TestCase):
    def setUp(self):
        self.producer = KafkaProducerService()
        self.topic = "test_topic"  # Define a test topic

        # Create a consumer to verify messages
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers='localhost:9092',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='test-group'
        )

    def test_send_message(self):
        message = {"key": "value", "status": "test"}
        self.producer.send_message(self.topic, message)

        # Allow some time for the message to be produced
        time.sleep(1)

        # Check if the message appears in the topic
        for msg in self.consumer:
            self.assertEqual(msg.value.decode('utf-8'), '{"key": "value", "status": "test"}')
            break  # Exit after the first message

    def tearDown(self):
        self.producer.close()
        self.consumer.close()

if __name__ == "__main__":
    unittest.main()