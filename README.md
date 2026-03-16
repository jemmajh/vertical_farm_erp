# Y2_2026_791623
##Mini ERP System for Company Inventory and Sales Management


##Project overveiw
This project implements a mini ERP system with a graphical user interface.
The system manages customers, products (inventory), and sales quotations/orders.

The program allows multiple users to log in and create orders. Each order records the user who created it.

The system also calculates product margins and provides basic statistics about sales and inventory.

The goal of the project is to demonstrate the core functionality of an ERP system in a simplified environment.



##Features
User System
	•	Registration and login
	•	Multiple users
	•	Orders record which user created them

Customer Module
	•	Create and edit customers
	•	Store contact information

Inventory Module
	•	Manage products
	•	Each product includes:
	•	name
	•	sales price
	•	cost price
	•	quantity

Product Variants

Products can have templates and variants.

Sales/Quotation Module
    Users can create orders by selecting:
        •	a customer
        •	products from inventory
        •	quantities

    Each order can contain multiple order lines.

    Each order line calculates:
        •	margin €
        •	margin %

    The order also shows:
        •	total price
        •	total margin


statistics Module
    The program provides useful statistics such as:
        •	sold product quantities
        •	inventory levels
        •	best salesperson

##Technology
	•	Python
	•	Tkinter GUI
	•	JSON data storage
	•	Python standard libraries

##Running the program
	1.	Install Python (3.10 or newer)
	2.	Run the program:`python main.py`

##Project Structure
project
│
├── main.py
├── models
│   ├── user.py
│   ├── customer.py
│   ├── product.py
│   ├── order.py
│   └── orderline.py
│
├── gui
│   ├── login_window.py
│   ├── main_window.py
│   ├── customer_view.py
│   ├── product_view.py
│   ├── order_view.py
│   └── statistics_view.py
│
├── data
│   ├── users.json
│   ├── customers.json
│   ├── products.json
│   └── orders.json
│
└── tests
    └── test_order.py

##Course Requirements
- GUI
- Customer Management
- Inventory Management
- Sales Quotation/orders
- Editable orders
- Automatic data saving
- User Registration/login
- Product variants
- Margin calculations
- Order statistics
- Unit tests

##Author
Hanjemma Jeong
791623
Digital Systems and Design

