from __future__ import annotations

from models import User, Customer, Product, OrderLine, Order, FarmConfig
from storage import Storage
import uuid
import csv
import io



class ERPSystem:
    def __init__(self, data_path: str = None):
        self.storage = Storage(filepath=data_path)
        self.users: list[User] = self.storage.load_users()
        self.customers: list[Customer] = self.storage.load_customers()
        self.products: list[Product] = self.storage.load_products()
        self.orders: list[Order] = self.storage.load_orders()

    # Users
    def register_user(self, username: str, password: str) -> tuple[bool, str]:
        if not username or not password:
            return False, "Username and password cannot be empty."

        if any(u.username == username for u in self.users):
            return False, f"Username '{username}' is already taken."
        user = User.create(username, password)
        self.users.append(user)
        self.storage.save_users(self.users)
        return True, f"User '{username}' registered successfully."


    def authenticate(self, username: str, password: str):
        for user in self.users:
            if user.username == username and user.password == password:
                return True, user
        return False, None

    #  Customers
    def add_customer(self, name: str, address: str, phone: str, email: str) -> tuple[bool, str]:
        if not name.strip():
            return False, "Customer name is required."

        customer = Customer.create(name.strip(), address.strip(), phone.strip(), email.strip())
        self.customers.append(customer)
        self.storage.save_customers(self.customers)
        return True, f"Customer '{name}' added."

    def update_customer(
            self, customer_id: str, name: str, address: str, phone: str, email: str
    ) -> tuple[bool, str]:
        for c in self.customers:
            if c.id == customer_id:
                c.name = name.strip()
                c.address = address.strip()
                c.phone = phone.strip()
                c.email = email.strip()
                self.storage.save_customers(self.customers)
                return True, "Customer updated."
        return False, "Customer not found."

    def delete_customer(self, customer_id) -> tuple[bool, str]:
        before = len(self.customers)
        self.customers = [c for c in self.customers if c.id != customer_id]
        if len(self.customers) < before:
            self.storage.save_customers(self.customers)
            return True, "Customer deleted."
        return False, "Customer not found."

    def get_customer_by_id(self, customer_id: str) -> Customer | None:
        return next((c for c in self.customers if c.id == customer_id), None)

    # Products
    def add_product(
        self,
        name: str,
        sales_price: float,
        cost_price: float,
        quantity: int,
        description: str = "",
    ) -> tuple[bool, str]:
        if not name.strip():
            return False, "Product name is required."
        if sales_price < 0 or cost_price < 0:
            return False, "Prices must be zero or positive."
        if quantity < 0:
            return False, "Quantity must be zero or positive."
        product = Product.create(name.strip(), sales_price, cost_price, quantity, description.strip())
        self.products.append(product)
        self.storage.save_products(self.products)
        return True, f"Product '{name}' added."


    def update_product(
        self,
        product_id: str,
        name: str,
        sales_price: float,
        cost_price: float,
        quantity: int,
        description: str = "",
    ) -> tuple[bool, str]:
        for p in self.products:
            if p.id == product_id:
                p.name = name.strip()
                p.sales_price = sales_price
                p.cost_price = cost_price
                p.quantity = quantity
                p.description = description.strip()
                self.storage.save_products(self.products)
                return True, "Product updated."
        return False, "Product not found."

    def delete_product(self, product_id: str) -> tuple[bool, str]:
        before = len(self.products)
        self.products = [p for p in self.products if p.id != product_id]
        if len(self.products) < before:
            self.storage.save_products(self.products)
            return True, "Product deleted."
        return False, "Product not found."

    def get_product_by_id(self, product_id: str) -> Product | None:
        return next((p for p in self.products if p.id == product_id), None)


    # Orders
    def create_order(self,
        customer_id: str,
        created_by_user: str,
        order_requests: list[tuple[str, int]],   # [(product_id, qty), …]
        status: str = "order",
    ) -> tuple[bool, str]:
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            return False, "Customer not found."
        if not order_requests:
            return False, "Order must have at least one line."

        lines = []
        for product_id, quantity in order_requests:
            product = self.get_product_by_id(product_id)
            if not product:
                return False, f"Product '{product_id}' not found"

            if quantity <= 0:
                return False, f"Invalid quantity for product {product.name}"

            if product.quantity < quantity:
                return False, f"Not enough stock for '{product.name}' (available: {product.quantity})."

            lines.append(OrderLine.from_product(product, quantity))

        for product_id, quantity in order_requests:
            self.get_product_by_id(product_id).quantity -= quantity
        self.storage.save_products(self.products)

        order_number = self.storage.get_next_order_number()
        order = Order.create(order_number, customer, created_by_user, lines, status)
        self.orders.append(order)
        self.storage.save_orders(self.orders)
        return True, "Order #{order_number} created successfully."

    def update_order(
            self,
            order_id: str,
            customer_id: str,
            order_requests: list[tuple[str, int]],
            status: str = "order",
    ) -> tuple[bool, str]:
        old_order = self.get_order_by_id(order_id)
        if not old_order:
            return False, "Order not found."
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            return False, "Customer not found."
        if not order_requests:
            return False, "Order must have at least one line."

        # Restore stock from the old order first
        for line in old_order.lines:
            product = self.get_product_by_id(line.product_id)
            if product:
                product.quantity += line.quantity

        # Validate new lines against restored stock
        lines = []
        for pid, qty in order_requests:
            product = self.get_product_by_id(pid)
            if not product:
                # Roll back: re-deduct old stock and abort
                for line in old_order.lines:
                    p = self.get_product_by_id(line.product_id)
                    if p:
                        p.quantity -= line.quantity
                return False, f"Product '{pid}' not found."
            if qty <= 0:
                for line in old_order.lines:
                    p = self.get_product_by_id(line.product_id)
                    if p:
                        p.quantity -= line.quantity
                return False, "Quantity must be positive."
            if product.quantity < qty:
                for line in old_order.lines:
                    p = self.get_product_by_id(line.product_id)
                    if p:
                        p.quantity -= line.quantity
                return False, f"Not enough stock for '{product.name}' (available: {product.quantity})."
            lines.append(OrderLine.from_product(product, qty))

        # Deduct new stock
        for pid, qty in order_requests:
            self.get_product_by_id(pid).quantity -= qty
        self.storage.save_products(self.products)

        for o in self.orders:
            if o.id == order_id:
                o.customer_id = customer.id
                o.customer_name = customer.name
                o.customer_address = customer.address
                o.customer_phone = customer.phone
                o.customer_email = customer.email
                o.status = status
                o.lines = lines
                o.total_price = sum(l.line_total for l in lines)
                o.total_cost = sum(l.cost_price * l.quantity for l in lines)
                o.total_margin = sum(l.margin_eur for l in lines)
                self.storage.save_orders(self.orders)
                return True, "Order updated."
        return False, "Order not found."

    def delete_order(self, order_id: str) -> tuple[bool, str]:
        order = self.get_order_by_id(order_id)
        if not order:
            return False, "Order not found."
        for line in order.lines:
            product = self.get_product_by_id(line.product_id)
            if product:
                product.quantity += line.quantity
        self.storage.save_products(self.products)
        self.orders = [o for o in self.orders if o.id != order_id]
        self.storage.save_orders(self.orders)
        return True, "Order deleted."

    def get_order_by_id(self, order_id: str) -> Order | None:
        return next((o for o in self.orders if o.id == order_id), None)

    #statistic
    def get_stats(self) -> dict:
        revenue = sum(o.total_price for o in self.orders)
        cost = sum(o.total_cost for o in self.orders)
        margin = sum(o.total_margin for o in self.orders)
        return {
            "revenue": revenue,
            "cost": cost,
            "margin": margin,
            "profit": revenue - cost,
            "margin_pct": (margin / revenue * 100) if revenue > 0 else 0.0,
            "order_count": len(self.orders),
            "customer_count": len(self.customers),
            "product_count": len(self.products),
        }

    # Farms
    def get_farm(self) -> FarmConfig | None:
        return self.storage.load_farm()

    def save_farm(self, farm_dict: dict) -> tuple[bool, str]:
        try:
            farm = FarmConfig(**farm_dict)
            self.storage.save_farm(farm)
            return True, "Farm configuration saved."
        except Exception as e:
            return False, str(e)

    def calculate_farm_stats(self, days: int = 365) -> dict | None:
        farm = self.get_farm()
        if not farm:
            return None
        return farm.simulate(days)

    #csv
    def export_customers_csv(self) -> str:
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(["Name", "Address", "Phone", "Email"])
        for c in self.customers:
            w.writerow([c.name, c.address, c.phone, c.email])
        return out.getvalue()

    def export_products_csv(self) -> str:
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(["Name", "Sales Price (€)", "Cost Price (€)", "Margin (€)", "Margin (%)", "Quantity", "Description"])
        for p in self.products:
            w.writerow([
                p.name,
                f"{p.sales_price:.2f}",
                f"{p.cost_price:.2f}",
                f"{p.margin_eur:.2f}",
                f"{p.margin_percent:.1f}%",
                p.quantity,
                p.description,
            ])
        return out.getvalue()

    def export_orders_csv(self) -> str:
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(["Order #", "Customer", "Date", "Status", "Total (€)", "Margin (€)", "Margin (%)"])
        for o in self.orders:
            w.writerow([
                f"#{o.order_number}",
                o.customer_name,
                o.created_at,
                o.status.capitalize(),
                f"{o.total_price:.2f}",
                f"{o.total_margin:.2f}",
                f"{o.margin_percent_total:.1f}%",
            ])
        return out.getvalue()

    # Helpers
    """def get_customer_by_id(self, customer_id: str):
        for customer in self.customers:
            if customer.id == customer_id:
                return customer
        return None

    def get_product_by_id(self, product_id: str):
        for product in self.products:
            if product.id == product_id:
                return product
        return None"""