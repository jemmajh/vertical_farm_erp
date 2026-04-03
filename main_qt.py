import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QListWidget, QLineEdit, QPushButton, QMessageBox, QComboBox
)
from erp import ERPSystem
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


BTN_STYLE = """
QPushButton {
    background-color: #3fa66b;
    color: white;
    border-radius: 10px;
    padding: 10px;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #348a59;
}
"""

INPUT_STYLE = """
QLineEdit {
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #ccc;
    font-size: 13px;
}
"""


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.erp = ERPSystem()
        self.current_user = None

        self.setWindowTitle("VacuumWood ERP")
        self.setFixedSize(400, 600)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 60, 40, 40)
        #layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("""
            <div style="text-align: center; line-height: 1.0;">
                <span style="font-size:42px; font-weight:700;">
                    VACUUM <br>
                    WOOD. <br>
                    <span style="color:#0F9D58;">TECH</span>
                </span>
            </div>
        """)

        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(30)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setStyleSheet(INPUT_STYLE)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setStyleSheet(INPUT_STYLE)

        layout.addWidget(self.username)
        layout.addWidget(self.password)

        login_btn = QPushButton("Login")
        login_btn.setStyleSheet(BTN_STYLE)
        login_btn.clicked.connect(self.login)

        register_btn = QPushButton("Register")
        register_btn.setStyleSheet(BTN_STYLE)
        register_btn.clicked.connect(self.register)

        layout.addWidget(login_btn)
        layout.addWidget(register_btn)

        footer = QLabel("Powered by VacuumWood")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(footer)

        self.setLayout(layout)

    def login(self):
        success, user = self.erp.authenticate(
            self.username.text().strip(),
            self.password.text().strip()
        )

        if success:
            self.main = MainMenu(self.erp, user.username)
            self.main.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")

    def register(self):
        success, msg = self.erp.register_user(
            self.username.text().strip(),
            self.password.text().strip()
        )

        if success:
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.warning(self, "Error", msg)


class MainMenu(QWidget):
    def __init__(self, erp, username):
        super().__init__()

        self.erp = erp
        self.username = username

        self.setWindowTitle("Dashboard")

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel(f"Welcome, {username}")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        buttons = [
            ("Customers", self.open_customers),
            ("Products", self.open_products),
            ("Orders", self.open_orders),
            ("Farm Info", self.open_farm),
            ("Statistics", self.open_stats),
        ]

        for text, func in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(BTN_STYLE)
            btn.clicked.connect(func)
            layout.addWidget(btn)

        self.setLayout(layout)

    def open_customers(self):
        self.c = CustomerWindow(self.erp)
        self.c.show()

    def open_products(self):
        self.p = ProductWindow(self.erp)
        self.p.show()

    def open_orders(self):
        self.o = OrderWindow(self.erp, self.username)
        self.o.show()

    def open_farm(self):
        data = self.erp.storage.load_data()

        if "farm" in data:
            self.f = FarmInfoWindow(self.erp)
        else:
            self.f = FarmWindow(self.erp)

        self.f.show()

    def open_stats(self):
        self.s = StatsWindow(self.erp)
        self.s.show()


class CustomerWindow(QWidget):
    def __init__(self, erp):
        super().__init__()
        self.erp = erp

        self.setWindowTitle("Customers")

        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("Customers")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.name = QLineEdit()
        self.name.setPlaceholderText("Name")
        self.name.setStyleSheet(INPUT_STYLE)

        self.address = QLineEdit()
        self.address.setPlaceholderText("Address")
        self.address.setStyleSheet(INPUT_STYLE)

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone")
        self.phone.setStyleSheet(INPUT_STYLE)

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.email.setStyleSheet(INPUT_STYLE)

        self.list = QListWidget()

        btn = QPushButton("Add Customer")
        btn.setStyleSheet(BTN_STYLE)
        btn.clicked.connect(self.add_customer)

        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_customer)

        layout.addWidget(self.name)
        layout.addWidget(self.address)
        layout.addWidget(self.phone)
        layout.addWidget(self.email)
        layout.addWidget(btn)
        layout.addWidget(delete_btn)
        layout.addWidget(self.list)

        self.setLayout(layout)
        self.refresh()

    def add_customer(self):
        success, msg = self.erp.add_customer(
            self.name.text(),
            self.address.text(),
            self.phone.text(),
            self.email.text()
        )

        if success:
            self.name.clear()
            self.address.clear()
            self.phone.clear()
            self.email.clear()
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def delete_customer(self):
        selected = self.list.currentRow()

        if selected < 0:
            QMessageBox.warning(self, "Error", "Select a customer")
            return
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this customer?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.No:
            return
        customer = self.erp.customers[selected]

        self.erp.delete_customer(customer.id)
        self.refresh()

    def refresh(self):
        self.list.clear()
        for c in self.erp.customers:
            self.list.addItem(f"{c.name} | {c.phone}")


class ProductWindow(QWidget):
    def __init__(self, erp):
        super().__init__()
        self.erp = erp

        self.setWindowTitle("Products")

        layout = QVBoxLayout()

        title = QLabel("Products")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.name = QLineEdit()
        self.name.setPlaceholderText("Name")
        self.name.setStyleSheet(INPUT_STYLE)

        self.sales = QLineEdit()
        self.sales.setPlaceholderText("Sales price")
        self.sales.setStyleSheet(INPUT_STYLE)

        self.cost = QLineEdit()
        self.cost.setPlaceholderText("Cost price")
        self.cost.setStyleSheet(INPUT_STYLE)

        self.qty = QLineEdit()
        self.qty.setPlaceholderText("Quantity")
        self.qty.setStyleSheet(INPUT_STYLE)

        self.list = QListWidget()

        btn = QPushButton("Add Product")
        btn.setStyleSheet(BTN_STYLE)
        btn.clicked.connect(self.add_product)
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_product)


        layout.addWidget(self.name)
        layout.addWidget(self.sales)
        layout.addWidget(self.cost)
        layout.addWidget(self.qty)
        layout.addWidget(btn)
        layout.addWidget(delete_btn)
        layout.addWidget(self.list)

        self.setLayout(layout)
        self.refresh()

    def add_product(self):
        try:
            success, msg = self.erp.add_product(
                self.name.text(),
                float(self.sales.text()),
                float(self.cost.text()),
                int(self.qty.text())
            )
        except:
            QMessageBox.warning(self, "Error", "Invalid input")
            return

        if success:
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def delete_product(self):
        selected = self.list.currentRow()

        if selected < 0:
            QMessageBox.warning(self, "Error", "Select a product")
            return
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this product?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.No:
            return

        product = self.erp.products[selected]

        self.erp.delete_product(product.id)
        self.refresh()

    def refresh(self):
        self.list.clear()
        for p in self.erp.products:
            self.list.addItem(f"{p.name} | {p.quantity}")


class OrderWindow(QWidget):
    def __init__(self, erp, user):
        super().__init__()
        self.erp = erp
        self.user = user
        self.lines = []

        self.setWindowTitle("Orders")

        layout = QVBoxLayout()

        self.customer = QComboBox()
        self.product = QComboBox()

        self.qty = QLineEdit()
        self.qty.setPlaceholderText("Quantity")
        self.qty.setStyleSheet(INPUT_STYLE)

        self.list = QListWidget()
        self.orders = QListWidget()

        btn_add = QPushButton("Add Line")
        btn_add.setStyleSheet(BTN_STYLE)
        btn_add.clicked.connect(self.add_line)

        btn_save = QPushButton("Save Order")
        btn_save.setStyleSheet(BTN_STYLE)
        btn_save.clicked.connect(self.save_order)

        delete_btn = QPushButton("Delete Selected Order")
        delete_btn.clicked.connect(self.delete_order)

        layout.addWidget(self.customer)
        layout.addWidget(self.product)
        layout.addWidget(self.qty)
        layout.addWidget(btn_add)
        layout.addWidget(self.list)
        layout.addWidget(btn_save)
        layout.addWidget(delete_btn)
        layout.addWidget(QLabel("Orders"))
        layout.addWidget(self.orders)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        self.customer.clear()
        self.product.clear()
        self.list.clear()
        self.orders.clear()
        self.lines = []

        self.customer_map = {c.name: c.id for c in self.erp.customers}
        self.product_map = {p.name: p.id for p in self.erp.products}

        self.customer.addItems(self.customer_map.keys())
        self.product.addItems(self.product_map.keys())

        for o in self.erp.orders:
            self.orders.addItem(f"{o.customer_name} | €{o.total_price:.2f}")

    def add_line(self):
        try:
            qty = int(self.qty.text())
        except:
            return

        name = self.product.currentText()
        pid = self.product_map[name]

        self.lines.append((pid, qty))
        self.list.addItem(f"{name} x {qty}")
        self.qty.clear()

    def save_order(self):
        cid = self.customer_map[self.customer.currentText()]

        success, msg = self.erp.create_order(cid, self.user, self.lines)

        if success:
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def delete_order(self):
        selected = self.orders.currentRow()

        if selected < 0:
            QMessageBox.warning(self, "Error", "Select an order")
            return
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this order?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.No:
            return

        order = self.erp.orders[selected]

        self.erp.delete_order(order.id)
        self.refresh()


class FarmWindow(QWidget):
    def __init__(self, erp):
        super().__init__()
        self.erp = erp

        self.setWindowTitle("Farm Setup")

        layout = QVBoxLayout()

        title = QLabel("Farm Configuration")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.length = QLineEdit()
        self.length.setPlaceholderText("Length")
        self.length.setStyleSheet(INPUT_STYLE)

        self.width = QLineEdit()
        self.width.setPlaceholderText("Width")
        self.width.setStyleSheet(INPUT_STYLE)

        self.height = QLineEdit()
        self.height.setPlaceholderText("Height")
        self.height.setStyleSheet(INPUT_STYLE)

        self.floors = QLineEdit()
        self.floors.setPlaceholderText("Floors")
        self.floors.setStyleSheet(INPUT_STYLE)

        self.eff = QLineEdit()
        self.eff.setPlaceholderText("Efficiency")
        self.eff.setStyleSheet(INPUT_STYLE)

        btn = QPushButton("Save Farm")
        btn.setStyleSheet(BTN_STYLE)
        btn.clicked.connect(self.save)

        layout.addWidget(self.length)
        layout.addWidget(self.width)
        layout.addWidget(self.height)
        layout.addWidget(self.floors)
        layout.addWidget(self.eff)
        layout.addWidget(btn)

        self.setLayout(layout)

    def save(self):
        try:
            data = self.erp.storage.load_data()
            data["farm"] = {
                "length": float(self.length.text()),
                "width": float(self.width.text()),
                "height": float(self.height.text()),
                "floors": int(self.floors.text()),
                "efficiency": float(self.eff.text())
            }
            self.erp.storage.save_data(data)
            QMessageBox.information(self, "Saved", "Farm saved")
        except:
            QMessageBox.warning(self, "Error", "Invalid input")

class FarmInfoWindow(QWidget):
    def __init__(self, erp):
        super().__init__()
        self.erp = erp

        self.setWindowTitle("Farm Info")

        layout = QVBoxLayout()

        data = self.erp.storage.load_data().get("farm", {})

        self.info = QLabel()
        self.info.setStyleSheet("font-size: 14px;")

        layout.addWidget(QLabel("Farm Info"))
        layout.addWidget(self.info)

        btn = QPushButton("Edit Farm")
        btn.clicked.connect(self.edit)
        layout.addWidget(btn)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        f = self.erp.storage.load_data().get("farm", {})

        text = f"""
                Length: {f.get('length')}
                Width: {f.get('width')}
                Height: {f.get('height')}
                Floors: {f.get('floors')}
                Efficiency: {f.get('efficiency')}
                """
        self.info.setText(text)

    def edit(self):
        self.w = FarmWindow(self.erp)
        self.w.show()



class StatsWindow(QWidget):
    def __init__(self, erp):
        super().__init__()
        self.erp = erp

        self.setWindowTitle("Farm Statistics")

        layout = QVBoxLayout()

        self.label = QLabel()
        self.label.setStyleSheet("font-size: 14px;")

        self.canvas = FigureCanvas(Figure())

        layout.addWidget(QLabel("Farm Performance"))
        layout.addWidget(self.label)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        self.update_stats()

    def update_stats(self):
        stats = self.erp.calculate_farm_stats()

        if not stats:
            self.label.setText("No farm data yet")
            return

        self.label.setText(
            f"Revenue: €{stats['revenue']:.0f}\n"
            f"Energy Cost: €{stats['cost']:.0f}\n"
            f"Profit: €{stats['profit']:.0f}"
        )

        fig = self.canvas.figure
        fig.clear()

        ax = fig.add_subplot(111)

        labels = ["Revenue", "Cost"]
        values = [stats["revenue"], stats["cost"]]

        ax.bar(labels, values)
        ax.set_title("Farm Financial Overview")

        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())