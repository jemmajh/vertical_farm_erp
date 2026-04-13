from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional
import uuid


def new_id() -> str:
    return str(uuid.uuid4())


@dataclass
class User:
    id: str
    username: str
    password: str

    @staticmethod
    def create(username: str, password: str) -> "User":
        return User(id=new_id(), username=username, password=password)


@dataclass
class Customer:
    id: str
    name: str
    address: str
    phone: str
    email: str

    @staticmethod
    def create(name: str, address: str, phone: str, email: str) -> "Customer":
        return Customer(id=new_id(), name=name, address=address, phone=phone, email=email)


@dataclass
class Product:
    id: str
    name: str
    sales_price: float
    cost_price: float
    quantity: int
    quantity: int
    description: str = ""

    @staticmethod
    def create(
            name: str,
            sales_price: float,
            cost_price: float,
            quantity: int,
            description: str = "",
    ) -> "Product":
        return Product(
            id=new_id(),
            name=name,
            sales_price=sales_price,
            cost_price=cost_price,
            quantity=quantity,
            description=description,
        )

    @property
    def margin_eur(self) -> float:
        return self.sales_price - self.cost_price

    @property
    def margin_percent(self) -> float:
        if self.sales_price > 0:
            return (self.margin_eur / self.sales_price) * 100
        return 0.0


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
    def from_product(product: Product, quantity: int) -> "OrderLine":
        margin_per_unit = product.sales_price - product.cost_price
        line_total = product.sales_price * quantity
        margin_eur = margin_per_unit * quantity
        margin_percent = (
            (margin_per_unit / product.sales_price) * 100
            if product.sales_price > 0
            else 0.0
        )
        return OrderLine(
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            sales_price=product.sales_price,
            cost_price=product.cost_price,
            margin_eur=margin_eur,
            margin_percent=margin_percent,
            line_total=line_total,
        )


@dataclass
class Order:
    id: str
    customer_id: str
    customer_name: str
    customer_address: str
    customer_phone: str
    customer_email: str
    created_by_user: str
    created_at: str
    status: str
    lines: List[OrderLine] = field(default_factory=list)
    total_price: float = 0.0
    total_cost: float = 0.0
    total_margin: float = 0.0

    @staticmethod
    def create(
            order_number: int,
            customer: Customer,
            created_by_user: str,
            lines: List[OrderLine],
            status: str = "order",
    ) -> "Order":
        total_price = sum(l.line_total for l in lines)
        total_cost = sum(l.cost_price * l.quantity for l in lines)
        total_margin = sum(l.margin_eur for l in lines)
        return Order(
            id=new_id(),
            order_number=order_number,
            customer_id=customer.id,
            customer_name=customer.name,
            customer_address=customer.address,
            customer_phone=customer.phone,
            customer_email=customer.email,
            created_by_user=created_by_user,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            status=status,
            lines=lines,
            total_price=total_price,
            total_cost=total_cost,
            total_margin=total_margin,
        )

    @property
    def margin_percent_total(self) -> float:
        if self.total_price > 0:
            return (self.total_margin / self.total_price) * 100
        return 0.0


@dataclass
class FarmConfig:
    length: float  # metres
    width: float  # metres
    height: float  # metres
    floors: int  # number of growing levels / racks
    efficiency: float  # fraction of floor area actually used for growing (0–1)

    electricity_rate: float  # €/kWh
    water_rate: float  # €/litre

    kwh_per_sqm_per_day: float
    liters_per_sqm_per_day: float

    seed_cost_per_sqm: float  # € per m² per cycle
    yield_kg_per_sqm: float  # kg harvested per m² per cycle
    price_per_kg: float  # €/kg (selling price)
    cycle_days: int  # days from seeding to harvest

    @property
    def growing_area(self) -> float:
        return self.length * self.width * self.floors * self.efficiency

    def simulate(self, days: int = 365) -> dict:
        area = self.growing_area
        cycles = days / self.cycle_days

        electricity_kwh = area * self.kwh_per_sqm_per_day * days
        electricity_cost = electricity_kwh * self.electricity_rate

        water_liters = area * self.liters_per_sqm_per_day * days
        water_cost = water_liters * self.water_rate

        seed_cost = area * self.seed_cost_per_sqm * cycles

        total_cost = electricity_cost + water_cost + seed_cost

        yield_kg = area * self.yield_kg_per_sqm * cycles
        revenue = yield_kg * self.price_per_kg
        profit = revenue - total_cost
        margin_pct = (profit / revenue * 100) if revenue > 0 else 0.0

        return {
            "days": days,
            "cycles": cycles,
            "growing_area_sqm": area,
            "electricity_kwh": electricity_kwh,
            "electricity_cost": electricity_cost,
            "water_liters": water_liters,
            "water_cost": water_cost,
            "seed_cost": seed_cost,
            "total_cost": total_cost,
            "yield_kg": yield_kg,
            "revenue": revenue,
            "profit": profit,
            "margin_pct": margin_pct,
        }

def to_dict(obj) -> dict:
    return asdict(obj)