import uuid
import random
from datetime import datetime
from typing import Dict, Optional
from core.user_session import UserSession, SessionState
from core.data_factory import DataFactory

class EventGenerator:

    def __init__(self, data_factory: DataFactory, probabilities: Dict):
        self.data_factory = data_factory
        self.probabilities = probabilities

    def _get_base_event(self, event_type: str, session: UserSession) -> Dict:
        return {
            'event_id': str(uuid.uuid4()),
            'event_type': event_type,
            'event_timestamp': datetime.utcnow().isoformat() + "Z",
            'user_id': session.user['user_id'],
            'username': session.user['username'],
            'session_id': session.session_id,
            'device': session.device,
            'location': {
                "city": session.location['city'],
                "state": session.location['state'],
                "country": session.location['country'],
            },
        }

    def generate_product_viewed(self, session: UserSession) -> Dict:
        product = self.data_factory.get_random_product()
        session.add_view_product(product)

        event = self._get_base_event('product_viewed', session)
        event['event_data'] = {
            'product_id': product['product_id'],
            'product_name': product['name'],
            'category_id': product['category_id'],
            'category': product['category'],
            'brand': product['brand'],
        }
        return event

    def generate_product_added_to_cart(self, session: UserSession) -> Optional[Dict]:
        if not session.viewed_products:
            return None
        
        product = random.choice(session.viewed_products[-3:])
        quantity = random.randint(1, 3)
        
        session.add_to_cart(product, quantity)

        event = self._get_base_event('product_added_to_cart', session)
        event['event_data'] = {
            'product_id': product['product_id'],
            'product_name': product['name'],
            'category_id': product['category_id'],
            'category': product['category'],
            'brand': product['brand'],
            'cart_id': session.cart_id,
            'quantity': quantity,
        }

        return event

    def generate_order_created(self, session: UserSession) -> Optional[Dict]:
        if not session.can_create_order():
            return None
        
        order = session.create_order()

        event = self._get_base_event("order_created", session)
        payment_method = self.data_factory.get_random_payment_method()
        event['event_data'] = {
            **order,
            'order_status': 'pending_payment',
            'currency': 'USD',
            'payment_method': payment_method,
        }

        return event

    def generate_payment_completed(self, session: UserSession) -> Optional[Dict]:
        if not session.can_make_payment():
            return None

        order = session.current_order

        event = self._get_base_event("payment_completed", session)
        event['event_data'] = {
            'transaction_id': str(uuid.uuid4()),
            'order_id': order['order_id'],
            'payment_status': 'completed',
            'message': 'Completed',
        }

        session.state = SessionState.COMPLETED
        return event

    def generate_payment_failed(self, session: UserSession) -> Optional[Dict]:
        if not session.can_make_payment():
            return None

        order = session.current_order
        payment_method = self.data_factory.get_random_payment_method()
        failure_reason = self.data_factory.get_failure_reason()

        event = self._get_base_event("payment_failed", session)
        event['event_data'] = {
            'transaction_id': str(uuid.uuid4()),
            'order_id': order['order_id'],
            'payment_status': 'failed',
            'failure_code': failure_reason['code'],
            'failure_message': failure_reason['message'],
        }

        session.state = SessionState.ABANDONED if random.random() < 0.7 else SessionState.PAYMENT_PENDING
        return event

    def decide_next_event(self, session: UserSession) -> Optional[Dict]:

        if session.state == SessionState.BROWSING:
            if session.can_add_to_cart() and random.random() < self.probabilities['view_add_to_cart']:
                return [self.generate_product_added_to_cart(session)]
            else:
                event = self.generate_product_viewed(session)
                return [event] if event else None
        
        elif session.state == SessionState.HAS_CART:
            if random.random() < self.probabilities['add_to_cart_order']:
                order_event = self.generate_order_created(session)
                
                if order_event:
                    if random.random() < self.probabilities['payment_success_rate']:
                        payment_event = self.generate_payment_completed(session)
                    else:
                        payment_event = self.generate_payment_failed(session)
                    
                    return [order_event, payment_event]
                return None
            else:
                if random.random() < 0.4:
                    return [self.generate_product_added_to_cart(session)]
                else:
                    return [self.generate_product_viewed(session)]
        
        return None