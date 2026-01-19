import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class SessionState(Enum):
    BROWSING = "browsing"
    HAS_CART = "has_cart"
    CHECKOUT = "checkout"
    PAYMENT_PENDING = "payment_pending"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class UserSession:
    def __init__(self, user: Dict, session_id: str, device: str, location: Dict):
        self.user = user
        self.session_id = session_id
        self.device = device
        self.location = location
        self.state = SessionState.BROWSING

        self.viewed_products: List[Dict] = []
        
        self.cart: List[Dict] = []
        self.cart_id = str(uuid.uuid4())

        self.current_order: Optional[Dict] = None

        self.views_count = 0
        self.max_views_before_actions = random.randint(2, 8)

    def can_add_to_cart(self) -> bool:
        return self.state in [SessionState.BROWSING, SessionState.HAS_CART] and self.views_count >= random.randint(1, 3)

    def can_create_order(self) -> bool:
        return self.state == SessionState.HAS_CART and len(self.cart) > 0

    def can_make_payment(self) -> bool:
        return self.state == SessionState.PAYMENT_PENDING and self.current_order is not None

    def is_active(self) -> bool:
        return self.state not in [SessionState.COMPLETED, SessionState.ABANDONED]

    def add_view_product(self, product: Dict):
        self.viewed_products.append(product)
        self.views_count += 1
    
    def add_to_cart(self, product: Dict, quantity: int = 1):
        self.cart.append({
            **product,
            "quantity": quantity,
            "subtotal": product["price"] * quantity,
        })

        self.state = SessionState.HAS_CART

    def create_order(self) -> Dict:
        order_id = str(uuid.uuid4())
        total = self.get_cart_total()

        self.current_order = {
            "order_id": order_id,
            "items": self.cart.copy(),
            "total_amount": total,
            "total_items": len(self.cart),
        }

        self.state = SessionState.PAYMENT_PENDING

        return self.current_order
    
    def get_cart_total(self) -> float:
        return sum(item["subtotal"] for item in self.cart)
            
class SessionManager:
    def __init__(self, max_concurrent: int = 50):
        self.sessions: Dict[str, UserSession] = {}
        self.max_concurrent = max_concurrent

    def create_session(self, user: Dict, session_id: str, device: str, location: Dict) -> UserSession:
        session = UserSession(user, session_id, device, location)
        self.sessions[session_id] = session
        return session

    def get_random_active_session(self) -> Optional[UserSession]:
        active = [s for s in self.sessions.values() if s.is_active()]
        return random.choice(active) if active else None
    
    def cleanup_inactive(self):
        inactive_ids = [sid for sid, s in self.sessions.items() if not s.is_active()]
        for sid in inactive_ids:
            del self.sessions[sid]

    def get_active_count(self) -> int:
        return sum(1 for s in self.sessions.values() if s.is_active())

    def needs_new_session(self) -> bool:
        return self.get_active_count() < self.max_concurrent