"""
storage.py – SQLite for VacuumWood Mini ERP

Database file: data/app_data.db
Schema
  users              – login credentials
  customers          – contact information
  product_templates  – grouping templates for product variants
  products           – inventory with pricing (optionally linked to a template)
  orders             – order headers
  order_lines        – individual product lines per order
  farm_config        – single-row farm configuration (singleton)
  settings           – key/value store (used for next_order_number counter)
"""
from __future__ import annotations

import sqlite3
import os
from models import User, Customer, Product, ProductTemplate, OrderLine, Order, FarmConfig

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_PATH = os.path.join(_BASE_DIR, "data", "erp.db")

_DDL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id       TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS customers (
    id      TEXT PRIMARY KEY,
    name    TEXT NOT NULL,
    address TEXT DEFAULT '',
    phone   TEXT DEFAULT '',
    email   TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS product_templates (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS products (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    sales_price REAL NOT NULL,
    cost_price  REAL NOT NULL,
    quantity    INTEGER NOT NULL,
    description TEXT DEFAULT '',
    template_id TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id               TEXT PRIMARY KEY,
    order_number     INTEGER NOT NULL,
    customer_id      TEXT NOT NULL,
    customer_name    TEXT NOT NULL,
    customer_address TEXT DEFAULT '',
    customer_phone   TEXT DEFAULT '',
    customer_email   TEXT DEFAULT '',
    created_by_user  TEXT NOT NULL,
    created_at       TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'order',
    total_price      REAL DEFAULT 0.0,
    total_cost       REAL DEFAULT 0.0,
    total_margin     REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS order_lines (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id       TEXT NOT NULL,
    product_id     TEXT NOT NULL,
    product_name   TEXT NOT NULL,
    quantity       INTEGER NOT NULL,
    sales_price    REAL NOT NULL,
    cost_price     REAL NOT NULL,
    margin_eur     REAL NOT NULL,
    margin_percent REAL NOT NULL,
    line_total     REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS farm_config (
    id                    INTEGER PRIMARY KEY CHECK (id = 1),
    length                REAL,
    width                 REAL,
    height                REAL,
    floors                INTEGER,
    efficiency            REAL,
    electricity_rate      REAL,
    water_rate            REAL,
    kwh_per_sqm_per_day   REAL,
    liters_per_sqm_per_day REAL,
    seed_cost_per_sqm     REAL,
    yield_kg_per_sqm      REAL,
    price_per_kg          REAL,
    cycle_days            INTEGER
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR IGNORE INTO settings (key, value) VALUES ('next_order_number', '1');
"""


class Storage:
    def __init__(self, filepath: str = None):
        self.filepath = filepath or _DEFAULT_PATH
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self._init_db()

    # Internal
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.filepath)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        conn = sqlite3.connect(self.filepath)
        conn.row_factory = sqlite3.Row
        conn.executescript(_DDL)
        # Migration: add columns that may be missing from older DB files
        cols = [row[1] for row in conn.execute("PRAGMA table_info(products)").fetchall()]
        if "template_id" not in cols:
            conn.execute("ALTER TABLE products ADD COLUMN template_id TEXT DEFAULT NULL")
            conn.commit()
        conn.close()

    # Users
    def load_users(self) -> list[User]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, username, password FROM users"
            ).fetchall()
        return [User(r["id"], r["username"], r["password"]) for r in rows]

    def save_users(self, users: list[User]):
        with self._connect() as conn:
            conn.execute("DELETE FROM users")
            conn.executemany(
                "INSERT INTO users (id, username, password) VALUES (?, ?, ?)",
                [(u.id, u.username, u.password) for u in users],
            )

    # Customers
    def load_customers(self) -> list[Customer]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, address, phone, email FROM customers"
            ).fetchall()
        return [
            Customer(r["id"], r["name"], r["address"], r["phone"], r["email"])
            for r in rows
        ]

    def save_customers(self, customers: list[Customer]):
        with self._connect() as conn:
            conn.execute("DELETE FROM customers")
            conn.executemany(
                "INSERT INTO customers (id, name, address, phone, email) VALUES (?, ?, ?, ?, ?)",
                [(c.id, c.name, c.address, c.phone, c.email) for c in customers],
            )

    # Product Templates
    def load_templates(self) -> list[ProductTemplate]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, description FROM product_templates ORDER BY name"
            ).fetchall()
        return [ProductTemplate(r["id"], r["name"], r["description"] or "") for r in rows]

    def save_templates(self, templates: list[ProductTemplate]):
        with self._connect() as conn:
            conn.execute("DELETE FROM product_templates")
            conn.executemany(
                "INSERT INTO product_templates (id, name, description) VALUES (?, ?, ?)",
                [(t.id, t.name, t.description) for t in templates],
            )

    # Products
    def load_products(self) -> list[Product]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, sales_price, cost_price, quantity, description, template_id FROM products"
            ).fetchall()
        return [
            Product(
                id=r["id"],
                name=r["name"],
                sales_price=r["sales_price"],
                cost_price=r["cost_price"],
                quantity=r["quantity"],
                description=r["description"] or "",
                template_id=r["template_id"],
            )
            for r in rows
        ]

    def save_products(self, products: list[Product]):
        with self._connect() as conn:
            conn.execute("DELETE FROM products")
            conn.executemany(
                """INSERT INTO products
                   (id, name, sales_price, cost_price, quantity, description, template_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [
                    (p.id, p.name, p.sales_price, p.cost_price, p.quantity,
                     p.description, p.template_id)
                    for p in products
                ],
            )

    # Orders
    def load_orders(self) -> list[Order]:
        with self._connect() as conn:
            order_rows = conn.execute(
                """SELECT id, order_number, customer_id, customer_name,
                          customer_address, customer_phone, customer_email,
                          created_by_user, created_at, status,
                          total_price, total_cost, total_margin
                   FROM orders ORDER BY order_number"""
            ).fetchall()

            orders = []
            for o in order_rows:
                line_rows = conn.execute(
                    """SELECT product_id, product_name, quantity,
                              sales_price, cost_price,
                              margin_eur, margin_percent, line_total
                       FROM order_lines WHERE order_id = ?""",
                    (o["id"],),
                ).fetchall()

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
                    for l in line_rows
                ]

                orders.append(
                    Order(
                        id=o["id"],
                        order_number=o["order_number"],
                        customer_id=o["customer_id"],
                        customer_name=o["customer_name"],
                        customer_address=o["customer_address"] or "",
                        customer_phone=o["customer_phone"] or "",
                        customer_email=o["customer_email"] or "",
                        created_by_user=o["created_by_user"],
                        created_at=o["created_at"],
                        status=o["status"],
                        lines=lines,
                        total_price=o["total_price"],
                        total_cost=o["total_cost"],
                        total_margin=o["total_margin"],
                    )
                )
        return orders

    def save_orders(self, orders: list[Order]):
        with self._connect() as conn:
            conn.execute("DELETE FROM order_lines")
            conn.execute("DELETE FROM orders")
            for o in orders:
                conn.execute(
                    """INSERT INTO orders
                       (id, order_number, customer_id, customer_name,
                        customer_address, customer_phone, customer_email,
                        created_by_user, created_at, status,
                        total_price, total_cost, total_margin)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        o.id, o.order_number, o.customer_id, o.customer_name,
                        o.customer_address, o.customer_phone, o.customer_email,
                        o.created_by_user, o.created_at, o.status,
                        o.total_price, o.total_cost, o.total_margin,
                    ),
                )
                conn.executemany(
                    """INSERT INTO order_lines
                       (order_id, product_id, product_name, quantity,
                        sales_price, cost_price, margin_eur, margin_percent, line_total)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    [
                        (
                            o.id, l.product_id, l.product_name, l.quantity,
                            l.sales_price, l.cost_price,
                            l.margin_eur, l.margin_percent, l.line_total,
                        )
                        for l in o.lines
                    ],
                )

    # Order number counter
    def get_next_order_number(self) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = 'next_order_number'"
            ).fetchone()
            n = int(row["value"])
            conn.execute(
                "UPDATE settings SET value = ? WHERE key = 'next_order_number'",
                (str(n + 1),),
            )
        return n

    # Farm
    def load_farm(self) -> FarmConfig | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM farm_config WHERE id = 1"
            ).fetchone()
        if not row:
            return None
        return FarmConfig(
            length=row["length"],
            width=row["width"],
            height=row["height"],
            floors=row["floors"],
            efficiency=row["efficiency"],
            electricity_rate=row["electricity_rate"],
            water_rate=row["water_rate"],
            kwh_per_sqm_per_day=row["kwh_per_sqm_per_day"],
            liters_per_sqm_per_day=row["liters_per_sqm_per_day"],
            seed_cost_per_sqm=row["seed_cost_per_sqm"],
            yield_kg_per_sqm=row["yield_kg_per_sqm"],
            price_per_kg=row["price_per_kg"],
            cycle_days=row["cycle_days"],
        )

    def save_farm(self, farm: FarmConfig):
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO farm_config
                   (id, length, width, height, floors, efficiency,
                    electricity_rate, water_rate, kwh_per_sqm_per_day,
                    liters_per_sqm_per_day, seed_cost_per_sqm,
                    yield_kg_per_sqm, price_per_kg, cycle_days)
                   VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    farm.length, farm.width, farm.height, farm.floors, farm.efficiency,
                    farm.electricity_rate, farm.water_rate, farm.kwh_per_sqm_per_day,
                    farm.liters_per_sqm_per_day, farm.seed_cost_per_sqm,
                    farm.yield_kg_per_sqm, farm.price_per_kg, farm.cycle_days,
                ),
            )

    # Legacy stubs
    def load_data(self) -> dict:
        """Legacy JSON method — returns empty dict. Use specific load_* methods."""
        return {}

    def save_data(self, data: dict):
        """Legacy JSON method — no-op. Use specific save_* methods."""
        pass
