from models import User, Customer, Product, Order, OrderLine, to_dict
from storage import DataManager


class ERPSystem:
    def __init__(self):
        self.data_manager = DataManager()
        self.users = []
        self.customers = []
        self.products = []
        self.orders = []
        self.load_all()

    def load_all(self):
        data = self.data_manager.load_data()

        self.users = [User(**u) for u in data.get("users", [])]
        self.customers = [Customer(**c) for c in data.get("customers", [])]
        self.products = [Product(**p) for p in data.get("products", [])]

        self.orders = []
        for order_data in data.get("orders", []):
            lines = [OrderLine(**line) for line in order_data.get("lines", [])]
            order_data_copy = dict(order_data)
            order_data_copy["lines"] = lines
            self.orders.append(Order(**order_data_copy))

    def save_all(self):
        data = {
            "users": [to_dict(user) for user in self.users],
            "customers": [to_dict(customer) for customer in self.customers],
            "products": [to_dict(product) for product in self.products],
            "orders": [to_dict(order) for order in self.orders],
        }
        self.data_manager.save_data(data)

    # ---------- Users ----------
    def register_user(self, username: str, password: str):
        if not username or not password:
            return False, "Username and password cannot be empty."

        for user in self.users:
            if user.username == username:
                return False, "Username already exists."

        new_user = User.create(username, password)
        self.users.append(new_user)
        self.save_all()
        return True, "User registered successfully."

    def authenticate(self, username: str, password: str):
        for user in self.users:
            if user.username == username and user.password == password:
                return True, user
        return False, None

    # ---------- Customers ----------
    def add_customer(self, name: str, address: str, phone: str, email: str):
        if not name:
            return False, "Customer name is required."

        customer = Customer.create(name, address, phone, email)
        self.customers.append(customer)
        self.save_all()
        return True, "Customer added."

    # ---------- Products ----------
    def add_product(self, name: str, sales_price: float, cost_price: float, quantity: int):
        if not name:
            return False, "Product name is required."

        if sales_price < 0 or cost_price < 0 or quantity < 0:
            return False, "Price and quantity must be non-negative."

        product = Product.create(name, sales_price, cost_price, quantity)
        self.products.append(product)
        self.save_all()
        return True, "Product added."

    # ---------- Orders ----------
    def create_order(self, customer_id: str, created_by_user: str, order_requests):
        customer = self.get_customer_by_id(customer_id)
        if customer is None:
            return False, "Customer not found."

        lines = []

        for product_id, quantity in order_requests:
            product = self.get_product_by_id(product_id)
            if product is None:
                return False, f"Product not found: {product_id}"

            if quantity <= 0:
                return False, f"Invalid quantity for product {product.name}"

            if product.quantity < quantity:
                return False, f"Not enough stock for {product.name}"

            line = OrderLine.from_product(product, quantity)
            lines.append(line)

        for product_id, quantity in order_requests:
            product = self.get_product_by_id(product_id)
            product.quantity -= quantity

        order = Order.create(customer.id, customer.name, created_by_user, lines)
        self.orders.append(order)
        self.save_all()
        return True, "Order created successfully."

    # ---------- Helpers ----------
    def get_customer_by_id(self, customer_id: str):
        for customer in self.customers:
            if customer.id == customer_id:
                return customer
        return None

    def get_product_by_id(self, product_id: str):
        for product in self.products:
            if product.id == product_id:
                return product
        return None