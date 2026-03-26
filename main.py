import tkinter as tk
from tkinter import ttk, messagebox
from erp import ERPSystem

print("RUNNING THIS FILE")
class ERPApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mini ERP System")
        self.geometry("900x650")

        self.erp = ERPSystem()
        self.current_user = None
        self.current_order_lines = []

        self.container = tk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for FrameClass in (LoginFrame, MainMenuFrame, CustomerFrame, ProductFrame, OrderFrame):
            frame = FrameClass(self.container, self)
            self.frames[FrameClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        if hasattr(frame, "refresh"):
            frame.refresh()
        frame.tkraise()


class LoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Mini ERP Login", font=("Arial", 18, "bold")).pack(pady=20)

        form = tk.Frame(self)
        form.pack(pady=20)

        tk.Label(form, text="Username").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.username_entry = tk.Entry(form, width=25)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        self.username_entry.focus_set()
        self.after(100, lambda: self.username_entry.focus_force())


        tk.Label(form, text="Password").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = tk.Entry(form, show="*", width=25)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self, text="Login", width=15, command=self.login).pack(pady=5)
        tk.Button(self, text="Register", width=15, command=self.register).pack(pady=5)



    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        success, user = self.app.erp.authenticate(username, password)
        if success:
            self.app.current_user = user.username
            messagebox.showinfo("Success", f"Welcome, {user.username}")
            self.app.show_frame("MainMenuFrame")
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        success, message = self.app.erp.register_user(username, password)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)


class MainMenuFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.title_label = tk.Label(self, text="Main Menu", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=20)

        tk.Button(self, text="Customers", width=25,
                  command=lambda: self.app.show_frame("CustomerFrame")).pack(pady=10)
        tk.Button(self, text="Products / Inventory", width=25,
                  command=lambda: self.app.show_frame("ProductFrame")).pack(pady=10)
        tk.Button(self, text="Orders", width=25,
                  command=lambda: self.app.show_frame("OrderFrame")).pack(pady=10)
        tk.Button(self, text="Logout", width=25, command=self.logout).pack(pady=10)

    def refresh(self):
        self.title_label.config(text=f"Main Menu - Logged in as {self.app.current_user}")

    def logout(self):
        self.app.current_user = None
        self.app.show_frame("LoginFrame")


class CustomerFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Customer Module", font=("Arial", 16, "bold")).pack(pady=10)

        form = tk.Frame(self)
        form.pack(pady=10)

        self.entries = {}
        fields = ["Name", "Address", "Phone", "Email"]

        for i, field in enumerate(fields):
            tk.Label(form, text=field).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(form, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[field.lower()] = entry

        tk.Button(self, text="Add Customer", command=self.add_customer).pack(pady=10)

        self.customer_list = tk.Listbox(self, width=100, height=15)
        self.customer_list.pack(pady=10)

        tk.Button(self, text="Back", command=lambda: self.app.show_frame("MainMenuFrame")).pack(pady=10)

    def add_customer(self):
        name = self.entries["name"].get().strip()
        address = self.entries["address"].get().strip()
        phone = self.entries["phone"].get().strip()
        email = self.entries["email"].get().strip()

        success, message = self.app.erp.add_customer(name, address, phone, email)
        if success:
            messagebox.showinfo("Success", message)
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.refresh()
        else:
            messagebox.showerror("Error", message)

    def refresh(self):
        self.customer_list.delete(0, tk.END)
        for customer in self.app.erp.customers:
            self.customer_list.insert(
                tk.END,
                f"{customer.name} | {customer.phone} | {customer.email} | {customer.address}"
            )


class ProductFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Product / Inventory Module", font=("Arial", 16, "bold")).pack(pady=10)

        form = tk.Frame(self)
        form.pack(pady=10)

        self.entries = {}
        fields = ["Name", "Sales Price", "Cost Price", "Quantity"]

        for i, field in enumerate(fields):
            tk.Label(form, text=field).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(form, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[field.lower().replace(" ", "_")] = entry

        tk.Button(self, text="Add Product", command=self.add_product).pack(pady=10)

        self.product_list = tk.Listbox(self, width=100, height=15)
        self.product_list.pack(pady=10)

        tk.Button(self, text="Back", command=lambda: self.app.show_frame("MainMenuFrame")).pack(pady=10)

    def add_product(self):
        try:
            name = self.entries["name"].get().strip()
            sales_price = float(self.entries["sales_price"].get())
            cost_price = float(self.entries["cost_price"].get())
            quantity = int(self.entries["quantity"].get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")
            return

        success, message = self.app.erp.add_product(name, sales_price, cost_price, quantity)
        if success:
            messagebox.showinfo("Success", message)
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.refresh()
        else:
            messagebox.showerror("Error", message)

    def refresh(self):
        self.product_list.delete(0, tk.END)
        for product in self.app.erp.products:
            self.product_list.insert(
                tk.END,
                f"{product.name} | Sales: {product.sales_price:.2f} | Cost: {product.cost_price:.2f} | Qty: {product.quantity}"
            )


class OrderFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Order Module", font=("Arial", 16, "bold")).pack(pady=10)

        top = tk.Frame(self)
        top.pack(pady=10)

        tk.Label(top, text="Customer").grid(row=0, column=0, padx=5, pady=5)
        self.customer_combo = ttk.Combobox(top, width=30, state="readonly")
        self.customer_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Product").grid(row=1, column=0, padx=5, pady=5)
        self.product_combo = ttk.Combobox(top, width=30, state="readonly")
        self.product_combo.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(top, text="Quantity").grid(row=2, column=0, padx=5, pady=5)
        self.quantity_entry = tk.Entry(top, width=10)
        self.quantity_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Button(top, text="Add Line", command=self.add_line).grid(row=3, column=0, columnspan=2, pady=10)

        self.lines_list = tk.Listbox(self, width=100, height=10)
        self.lines_list.pack(pady=10)

        tk.Button(self, text="Save Order", command=self.save_order).pack(pady=5)

        tk.Label(self, text="Existing Orders", font=("Arial", 12, "bold")).pack(pady=5)
        self.order_list = tk.Listbox(self, width=100, height=10)
        self.order_list.pack(pady=10)

        tk.Button(self, text="Back", command=lambda: self.app.show_frame("MainMenuFrame")).pack(pady=10)

    def refresh(self):
        self.customer_map = {customer.name: customer.id for customer in self.app.erp.customers}
        self.product_map = {product.name: product.id for product in self.app.erp.products}

        self.customer_combo["values"] = list(self.customer_map.keys())
        self.product_combo["values"] = list(self.product_map.keys())

        self.lines_list.delete(0, tk.END)
        self.app.current_order_lines = []

        self.order_list.delete(0, tk.END)
        for order in self.app.erp.orders:
            self.order_list.insert(
                tk.END,
                f"{order.created_at} | {order.customer_name} | By: {order.created_by_user} | Total: {order.total_price:.2f} | Margin: {order.total_margin:.2f}"
            )

    def add_line(self):
        customer_name = self.customer_combo.get()
        product_name = self.product_combo.get()

        if not customer_name:
            messagebox.showerror("Error", "Please select a customer first.")
            return

        if not product_name:
            messagebox.showerror("Error", "Please select a product.")
            return

        try:
            quantity = int(self.quantity_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity.")
            return

        product_id = self.product_map[product_name]
        self.app.current_order_lines.append((product_id, quantity))

        product = self.app.erp.get_product_by_id(product_id)
        self.lines_list.insert(
            tk.END,
            f"{product.name} | Qty: {quantity} | Price: {product.sales_price:.2f} | Margin %: {((product.sales_price - product.cost_price) / product.sales_price * 100 if product.sales_price > 0 else 0):.1f}"
        )

        self.quantity_entry.delete(0, tk.END)

    def save_order(self):
        customer_name = self.customer_combo.get()

        if not customer_name:
            messagebox.showerror("Error", "Please select a customer.")
            return

        if not self.app.current_order_lines:
            messagebox.showerror("Error", "Please add at least one order line.")
            return

        customer_id = self.customer_map[customer_name]

        success, message = self.app.erp.create_order(
            customer_id=customer_id,
            created_by_user=self.app.current_user,
            order_requests=self.app.current_order_lines
        )

        if success:
            messagebox.showinfo("Success", message)
            self.app.current_order_lines = []
            self.refresh()
        else:
            messagebox.showerror("Error", message)


if __name__ == "__main__":
    app = ERPApp()
    app.mainloop()