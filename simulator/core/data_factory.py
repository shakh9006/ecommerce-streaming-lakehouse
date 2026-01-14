import random
import uuid
import os
import dotenv
import json
from datetime import datetime
from typing import Dict, List, Any
from faker import Faker

fake = Faker()

class DataFactory:
    """
    A factory for generating synthetic data for the simulator.
    """
    def __init__(self):
        self.products = self._flatten_products()
        self.payment_methods = self._flatten_payment_methods()
        self.locations = self._flatten_locations()
        self.users = self._flatten_users()

    def _flatten_products(self) -> List[Dict]:
        products = []
        categoreies = {}
        with open("core/meta_data/products.json", "r", encoding="utf-8") as f:
            parsed_products = json.load(f)
            for category_data in parsed_products:
                category = category_data["category"]
                if category not in categoreies:
                    categoreies[category] = str(uuid.uuid4())
                    
                for product in category_data["products"]:
                    products.append({
                        "product_id": str(uuid.uuid4()),
                        "category_id": categoreies[category],
                        "category": category,
                        **product,
                    })
        return products
    
    def _flatten_payment_methods(self) -> List[Dict]:
        payment_methods = []

        with open("core/meta_data/payment_methods.json", "r", encoding="utf-8") as f:
            parsed_payment_methods = json.load(f)
            for payment_method in parsed_payment_methods:
                payment_methods.append({
                    "payment_method_id": str(uuid.uuid4()),
                    "payment_method": payment_method,
                })

        return payment_methods

    def _flatten_locations(self) -> List[Dict]:
        locations = []

        with open("core/meta_data/locations.json", "r", encoding="utf-8") as f:
            parsed_locations = json.load(f)

            for location in parsed_locations:
                locations.append({
                    "location_id": str(uuid.uuid4()),
                    **location,
                })

        return locations

    def _flatten_users(self) -> List[Dict]:
        users = []

        with open("core/meta_data/users.json", "r", encoding="utf-8") as f:
            parsed_users = json.load(f)
            for user in parsed_users:
                users.append({
                    "user_id": str(uuid.uuid4()),
                    **user,
                })

        return users

    def get_random_user(self) -> Dict:
        return random.choice(self.users)

    def get_random_product(self) -> Dict:
        return random.choice(self.products)

    def get_random_payment_method(self) -> str:
        return random.choice(self.payment_methods)

    def get_random_location(self) -> Dict:
        return random.choice(self.locations)
    
    def generate_device(self) -> str:
        return random.choice(["mobile", "desktop", "web"])

    def get_failure_reason(self) -> Dict:
        reasons = [
            {
                "reason": "insufficient_funds",
                "code": "INSUFFICIENT_FUNDS",
                "message": "Your card has insufficient funds.",
            },
            {
                "reason": "card_expired",
                "code": "CARD_EXPIRED",
                "message": "Your card has expired.",
            },
            {
                "reason": "card_declined",
                "code": "CARD_DECLINED",
                "message": "Your card has been declined.",
            },
            {
                "reason": "invalid_card",
                "code": "INVALID_CARD",
                "message": "Your card is invalid.",
            },
            {
                "reason": "network_error",
                "code": "NETWORK_ERROR",
                "message": "There was a network error. Please try again.",
            }
        ]
        return random.choice(reasons)