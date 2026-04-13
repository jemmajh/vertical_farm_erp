from __future__ import annotations

import json
import os
from models import User, Customer, Product, OrderLine, Order, FarmConfig, to_dict

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_PATH = os.path.join(_BASE_DIR, "data", "app_data.json")

_EMPTY_DB = {
    "users": [],
    "customers": [],
    "products": [],
    "orders": [],
    "farm": None,
    "next_order_number": 1,
}

class Storage:
    def __init__(self, filepath: str = None):
        self.filepath = filepath or _DEFAULT_PATH
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(_EMPTY_DB, f, indent=2)

    def load_data(self) -> dict:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_data(self, data: dict):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_users(self) -> list[User]:
        data = self.load_data()
        return [User(u["id"], u["username"], u["password"]) for u in data.get("users", [])]

    def save_users(self, users: list[User]):
        data = self.load_data()
        data["users"] = [to_dict(u) for u in users]
        self.save_data(data)

    # customers

    def load_customers(self) -> list[Customer]:
        data = self.load_data()
        return [
            Customer(c["id"], c["name"], c["address"], c["phone"], c["email"])
            for c in data.get("customers", [])
        ]

    def save_customers(self, customers: list[Customer]):
        data = self.load_data()
        data["customers"] = [to_dict(c) for c in customers]
        self.save_data(data)

    #products

    def load_products(self) -> list[Product]:
        data = self.load_data()
        return [
            Product(
                id=p["id"],
                name=p["name"],
                sales_price=p["sales_price"],
                cost_price=p["cost_price"],
                quantity=p["quantity"],
                description=p.get("description", ""),
            )
            for p in data.get("products", [])
        ]

    def save_products(self, products: list[Product]):
        data = self.load_data()
        data["products"] = [to_dict(p) for p in products]
        self.save_data(data)

    #orders

    def load_orders(self) -> list[Order]:
        data = self.load_data()
        orders = []
        for o in data.get("orders", []):
            lines = [
                OrderLine(
                    product_id=l["product_id"],
                    product_name=l["product_name"],
                    quantity=l["quantity"],
                    sales_price=l["sales_price"],
                    cost_price=l["cost_price"],
                    margin_eur=l["margin_eur"],
                    margin_percent=l["margin_percent"],
                    line_total=l["line_total"],
                )
                for l in o.get("lines", [])
            ]
            orders.append(
                Order(
                    id=o["id"],
                    order_number=o.get("order_number", 0),
                    customer_id=o["customer_id"],
                    customer_name=o["customer_name"],
                    customer_address=o.get("customer_address", ""),
                    customer_phone=o.get("customer_phone", ""),
                    customer_email=o.get("customer_email", ""),
                    created_by_user=o["created_by_user"],
                    created_at=o["created_at"],
                    status=o.get("status", "order"),
                    lines=lines,
                    total_price=o["total_price"],
                    total_cost=o.get("total_cost", 0.0),
                    total_margin=o["total_margin"],
                )
            )
        return orders

    def save_orders(self, orders: list[Order]):
        data = self.load_data()
        data["orders"] = [to_dict(o) for o in orders]
        self.save_data(data)


    def get_next_order_number(self) -> int:
        data = self.load_data()
        n = data.get("next_order_number", 1)
        data["next_order_number"] = n + 1
        self.save_data(data)
        return n

    #farm

    def load_farm(self) -> FarmConfig | None:
        f = self.load_data().get("farm")
        if not f:
            return None
        # Fill in defaults for any new fields missing from older saved data
        defaults = {
            "electricity_rate": 0.25,
            "water_rate": 0.003,
            "kwh_per_sqm_per_day": 0.3,
            "liters_per_sqm_per_day": 3.0,
            "seed_cost_per_sqm": 1.0,
            "yield_kg_per_sqm": 3.0,
            "price_per_kg": 8.0,
            "cycle_days": 30,
        }
        for key, val in defaults.items():
            if key not in f:
                f[key] = val
        return FarmConfig(**f)

    def save_farm(self, farm: FarmConfig):
        data = self.load_data()
        data["farm"] = to_dict(farm)
        self.save_data(data)
