from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List
import uuid


def new_id() -> str:
    return str(uuid.uuid4())


@dataclass
class User:
    id: str
    username: str
    password: str

    @staticmethod
    def create(username: str, password: str):
        return User(id=new_id(), username=username, password=password)


@dataclass
class Customer:
    id: str
    name: str
    address: str
    phone: str
    email: str

    @staticmethod
    def create(name: str, address: str, phone: str, email: str):
        return Customer(
            id=new_id(),
            name=name,
            address=address,
            phone=phone,
            email=email
        )


@dataclass
class Product:
    id: str
    name: str
    sales_price: float
    cost_price: float
    quantity: int

    @staticmethod
    def create(name: str, sales_price: float, cost_price: float, quantity: int):
        return Product(
            id=new_id(),
            name=name,
            sales_price=sales_price,
            cost_price=cost_price,
            quantity=quantity
        )


@dataclass
class OrderLine:
    product_id: str
    product_name: str
    quantity: int
    sales_price: float
    cost_price: float
    margin_eur: float
    margin_percent: float
    line_total: float

    @staticmethod
    def from_product(product: Product, quantity: int):
        margin_per_unit = product.sales_price - product.cost_price
        line_total = product.sales_price * quantity
        margin_eur = margin_per_unit * quantity
        margin_percent = 0.0
        if product.sales_price > 0:
            margin_percent = (margin_per_unit / product.sales_price) * 100

        return OrderLine(
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            sales_price=product.sales_price,
            cost_price=product.cost_price,
            margin_eur=margin_eur,
            margin_percent=margin_percent,
            line_total=line_total
        )


@dataclass
class Order:
    id: str
    customer_id: str
    customer_name: str
    created_by_user: str
    created_at: str
    lines: List[OrderLine] = field(default_factory=list)
    total_price: float = 0.0
    total_margin: float = 0.0

    @staticmethod
    def create(customer_id: str, customer_name: str, created_by_user: str, lines: List[OrderLine]):
        total_price = sum(line.line_total for line in lines)
        total_margin = sum(line.margin_eur for line in lines)

        return Order(
            id=new_id(),
            customer_id=customer_id,
            customer_name=customer_name,
            created_by_user=created_by_user,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            lines=lines,
            total_price=total_price,
            total_margin=total_margin
        )


def to_dict(obj):
    return asdict(obj)