import json
import time
import random
import uuid
import os
import dotenv
import logging

from typing import Dict
from core.data_factory import DataFactory
from core.event_generator import EventGenerator
from core.user_session import SessionManager
from kafka import KafkaProducer
from kafka.errors import KafkaError

dotenv.load_dotenv()

class EcommerceEventSimulator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Ecommerce Event Simulator...")
       
        probabilities = {
            'view_add_to_cart': 0.15,
            'add_to_cart_order': 0.40,
            'payment_success_rate': 0.85,
        }
       
        max_concurrent_sessions = int(os.getenv('MAX_CONCURRENT_SESSIONS', '50'))
        self.data_factory = DataFactory()
        self.event_generator = EventGenerator(self.data_factory, probabilities)
        self.session_manager = SessionManager(max_concurrent_sessions)

        self.topic = os.getenv('KAFKA_TOPIC')
        self.producer = KafkaProducer(
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda v: v.encode('utf-8') if v else None,
            acks='all',
            retries=3,
            max_in_flight_requests_per_connection=1,
            compression_type='gzip',
        )

    def send_to_kafka(self, event):
        try:
            key = event['user_id']
            future = self.producer.send(topic=self.topic, key=key, value=event)

            future.add_callback(self._delivery_success_callback, event)
            future.add_errback(self._delivery_error_callback, event)
        except Exception as e:
            self.logger.error(f"Error sending event to Kafka: {e}")
            raise e

    def _delivery_success_callback(self, event, metadata):
        self.logger.info(f"Message delivered to Kafka: {metadata.topic} [{metadata.partition}] at offset {metadata.offset}")
    
    def _delivery_error_callback(self, exc, event):
        self.logger.error(f"Error delivering message to Kafka: {exc} on event: {event['event_id']}")

    def flush(self):
        self.producer.flush()

    def shutdown(self):
        self.logger.info("Flushing remaining messages...")
        self.producer.flush()
        self.producer.close()
        self.logger.info("Producer shut down successfully")

    def _create_new_session(self):
        user = self.data_factory.get_random_user()
        session_id = str(uuid.uuid4())
        device = self.data_factory.generate_device()
        location = self.data_factory.get_random_location()

        session = self.session_manager.create_session(user, session_id, device, location)

        return session
    
    def generate_events(self):
        events = []
        self.session_manager.cleanup_inactive()

        if self.session_manager.needs_new_session():
            if random.random() < 0.3:
                self._create_new_session()
    
        session = self.session_manager.get_random_active_session()

        if session:
            events_list = self.event_generator.decide_next_event(session)
            if events_list:
                events.extend(events_list)

        return events