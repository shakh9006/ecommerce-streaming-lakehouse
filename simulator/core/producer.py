import json
import time
import random
import uuid
import os
import dotenv

from typing import Dict
from core.data_factory import DataFactory
from core.event_generator import EventGenerator
from core.user_session import SessionManager

dotenv.load_dotenv()

class EcommerceEventSimulator:
    def __init__(self):
        probabilities = {
            'view_add_to_cart': 0.15,
            'add_to_cart_order': 0.40,
            'payment_success_rate': 0.85,
        }
        max_concurrent_sessions = int(os.getenv('MAX_CONCURRENT_SESSIONS', '50'))
        self.data_factory = DataFactory()
        self.event_generator = EventGenerator(self.data_factory, probabilities)
        self.session_manager = SessionManager(max_concurrent_sessions)

        self.stats = {
            'product_viewed': 0,
            'product_added_to_cart': 0,
            'order_created': 0,
            'payment_completed': 0,
            'payment_failed': 0,
        }
    
    def _create_new_session(self):
        user = self.data_factory.get_random_user()
        session_id = str(uuid.uuid4())
        device = self.data_factory.generate_device()
        location = self.data_factory.get_random_location()

        session = self.session_manager.create_session(user, session_id, device, location)

        return session
    
    def run(self):
        events = []
        try:
            for _ in range(150):
                self.session_manager.cleanup_inactive()

                if self.session_manager.needs_new_session():
                    if random.random() < 0.3:
                        self._create_new_session()
            
                session = self.session_manager.get_random_active_session()

                if session:
                    events_list = self.event_generator.decide_next_event(session)
                    if events_list:
                        for event in events_list:
                            events.append(event)
        except Exception as e:
            print(f"Error: {e}")
            return []

        return events