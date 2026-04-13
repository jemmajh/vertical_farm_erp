from __future__ import annotations

import sys
import os
import csv

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QSpinBox,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QGroupBox, QFormLayout, QDialog, QDialogButtonBox,
    QStackedWidget, QFrame, QSizePolicy, QFileDialog, QTextEdit,
    QSplitter, QScrollArea,
)
from PyQt6.QtGui import QFont, QColor

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from erp import ERPSystem


APP_STYLESHEET = """
QWidget {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    color: #1a1a1a;
    background-color: #F7F9F8;
}

/* ── Sidebar ── */
QFrame#sidebar {
    background-color: #1C2526;
    border-right: 2px solid #2E7D32;
}
QPushButton#sidebar_btn {
    background-color: transparent;
    color: #B0BEC5;
    border: none;
    border-radius: 0;
    padding: 14px 20px;
    text-align: left;
    font-size: 13px;
}
QPushButton#sidebar_btn:hover {
    background-color: #263238;
    color: #FFFFFF;
}
QPushButton#sidebar_btn[active=true] {
    background-color: #2E7D32;
    color: #FFFFFF;
    border-left: 4px solid #81C784;
    font-weight: bold;
}
QPushButton#logout_btn {
    background-color: transparent;
    color: #EF9A9A;
    border: none;
    padding: 14px 20px;
    text-align: left;
    font-size: 13px;
}
QPushButton#logout_btn:hover {
    background-color: #4E342E;
    color: #FFCDD2;
}

/* ── Primary Button ── */
QPushButton#primary {
    background-color: #2E7D32;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 9px 18px;
    font-weight: 600;
}
QPushButton#primary:hover { background-color: #1B5E20; }
QPushButton#primary:disabled { background-color: #A5D6A7; }

/* ── Danger Button ── */
QPushButton#danger {
    background-color: #C62828;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 9px 18px;
    font-weight: 600;
}
QPushButton#danger:hover { background-color: #B71C1C; }

/* ── Secondary Button ── */
QPushButton#secondary {
    background-color: white;
    color: #424242;
    border: 1px solid #BDBDBD;
    border-radius: 6px;
    padding: 9px 18px;
}
QPushButton#secondary:hover { background-color: #F5F5F5; }

/* ── Warning/amber Button ── */
QPushButton#warning {
    background-color: #E65100;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 9px 18px;
    font-weight: 600;
}
QPushButton#warning:hover { background-color: #BF360C; }

/* ── Input fields ── */
QLineEdit, QTextEdit {
    background-color: white;
    border: 1px solid #BDBDBD;
    border-radius: 5px;
    padding: 7px 10px;
    font-size: 13px;
}
QLineEdit:focus, QTextEdit:focus { border-color: #4CAF50; }

QComboBox {
    background-color: white;
    border: 1px solid #BDBDBD;
    border-radius: 5px;
    padding: 7px 10px;
    font-size: 13px;
}
QComboBox:focus { border-color: #4CAF50; }
QComboBox::drop-down { border: none; }

QSpinBox, QDoubleSpinBox {
    background-color: white;
    border: 1px solid #BDBDBD;
    border-radius: 5px;
    padding: 7px 8px;
}
QSpinBox:focus, QDoubleSpinBox:focus { border-color: #4CAF50; }

/* ── Table ── */
QTableWidget {
    background-color: white;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    gridline-color: #F5F5F5;
    selection-background-color: #C8E6C9;
    selection-color: #1a1a1a;
}
QTableWidget::item { padding: 8px 10px; }
QTableWidget::item:alternate { background-color: #F9FBF9; }

QHeaderView::section {
    background-color: #E8F5E9;
    color: #2E7D32;
    font-weight: bold;
    padding: 9px;
    border: none;
    border-bottom: 2px solid #4CAF50;
}

/* ── GroupBox ── */
QGroupBox {
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    margin-top: 10px;
    padding: 12px 8px 8px 8px;
    background-color: white;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #2E7D32;
    font-weight: bold;
    font-size: 12px;
}

/* ── Scrollbar ── */
QScrollBar:vertical {
    width: 8px;
    background: #F0F0F0;
}
QScrollBar::handle:vertical {
    background: #BDBDBD;
    border-radius: 4px;
}
"""


def btn(text: str, style: str = "primary", parent=None) -> QPushButton:
    b = QPushButton(text, parent)
    b.setObjectName(style)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b


def make_table(headers: list[str]) -> QTableWidget:
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.verticalHeader().setVisible(False)
    t.setAlternatingRowColors(True)
    t.setShowGrid(True)
    return t


def fill_table_row(table: QTableWidget, values: list):
    row = table.rowCount()
    table.insertRow(row)
    for col, val in enumerate(values):
        item = QTableWidgetItem(str(val))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, col, item)


def section_title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("font-size:18px; font-weight:bold; color:#1B5E20; margin-bottom:4px;")
    return lbl


def confirm_delete(parent, what: str) -> bool:
    reply = QMessageBox.question(
        parent, "Confirm Delete",
        f"Are you sure you want to delete this {what}?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    return reply == QMessageBox.StandardButton.Yes


class CustomerDialog(QDialog):

    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Customer" if customer else "New Customer")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)

        self._name = QLineEdit()
        self._address = QLineEdit()
        self._phone = QLineEdit()
        self._email = QLineEdit()

        form.addRow("Name *", self._name)
        form.addRow("Address", self._address)
        form.addRow("Phone", self._phone)
        form.addRow("Email", self._email)

        if customer:
            self._name.setText(customer.name)
            self._address.setText(customer.address)
            self._phone.setText(customer.phone)
            self._email.setText(customer.email)

        layout.addLayout(form)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._validate)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _validate(self):
        if not self._name.text().strip():
            QMessageBox.warning(self, "Validation", "Customer name is required.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name": self._name.text().strip(),
            "address": self._address.text().strip(),
            "phone": self._phone.text().strip(),
            "email": self._email.text().strip(),
        }


class ProductDialog(QDialog):

    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Product" if product else "New Product")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)

        self._name = QLineEdit()
        self._sales = QDoubleSpinBox()
        self._sales.setPrefix("€ "); self._sales.setMaximum(999999); self._sales.setDecimals(2)
        self._cost = QDoubleSpinBox()
        self._cost.setPrefix("€ "); self._cost.setMaximum(999999); self._cost.setDecimals(2)
        self._qty = QSpinBox()
        self._qty.setMaximum(999999)
        self._desc = QLineEdit()

        form.addRow("Name *", self._name)
        form.addRow("Sales Price *", self._sales)
        form.addRow("Cost Price *", self._cost)
        form.addRow("Quantity *", self._qty)
        form.addRow("Description", self._desc)

        # Live margin preview
        self._margin_lbl = QLabel("Margin: —")
        self._margin_lbl.setStyleSheet("color:#2E7D32; font-weight:bold;")
        form.addRow("", self._margin_lbl)

        self._sales.valueChanged.connect(self._update_margin)
        self._cost.valueChanged.connect(self._update_margin)

        if product:
            self._name.setText(product.name)
            self._sales.setValue(product.sales_price)
            self._cost.setValue(product.cost_price)
            self._qty.setValue(product.quantity)
            self._desc.setText(product.description)

        self._update_margin()

        layout.addLayout(form)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._validate)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _update_margin(self):
        sp, cp = self._sales.value(), self._cost.value()
        margin_eur = sp - cp
        margin_pct = (margin_eur / sp * 100) if sp > 0 else 0.0
        color = "#2E7D32" if margin_eur >= 0 else "#C62828"
        self._margin_lbl.setStyleSheet(f"color:{color}; font-weight:bold;")
        self._margin_lbl.setText(f"Margin: €{margin_eur:.2f}  ({margin_pct:.1f}%)")

    def _validate(self):
        if not self._name.text().strip():
            QMessageBox.warning(self, "Validation", "Product name is required.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name": self._name.text().strip(),
            "sales_price": self._sales.value(),
            "cost_price": self._cost.value(),
            "quantity": self._qty.value(),
            "description": self._desc.text().strip(),
        }


class OrderDialog(QDialog):

    def __init__(self, parent=None, erp: ERPSystem = None, order=None):
        super().__init__(parent)
        self.erp = erp
        self.edit_order = order
        self._lines: list[tuple[str, int]] = []   # [(product_id, qty)]

        self.setWindowTitle("Edit Order" if order else "New Order / Quotation")
        self.setMinimumSize(720, 560)

        root = QVBoxLayout(self)
        root.setSpacing(12)

        hdr = QGroupBox("Order Info")
        hdr_form = QFormLayout(hdr)
        hdr_form.setSpacing(8)

        self._customer_cb = QComboBox()
        self._customer_map = {c.name: c.id for c in erp.customers}
        self._customer_cb.addItems(self._customer_map.keys())

        hdr_form.addRow("Customer *", self._customer_cb)
        root.addWidget(hdr)

        lines_grp = QGroupBox("Order Lines")
        lines_lay = QVBoxLayout(lines_grp)

        self._lines_table = make_table(
            ["Product", "Qty", "Unit Price (€)", "Unit Cost (€)", "Margin (€)", "Margin (%)"]
        )
        self._lines_table.setMinimumHeight(160)
        lines_lay.addWidget(self._lines_table)

        add_row = QHBoxLayout()
        self._product_cb = QComboBox()
        self._product_map = {p.name: p.id for p in erp.products}
        self._product_cb.addItems(self._product_map.keys())
        self._product_cb.setMinimumWidth(180)

        self._qty_spin = QSpinBox()
        self._qty_spin.setMinimum(1); self._qty_spin.setMaximum(99999)

        add_btn = btn("＋ Add Line", "primary")
        add_btn.clicked.connect(self._add_line)
        rem_btn = btn("✕ Remove", "danger")
        rem_btn.clicked.connect(self._remove_line)

        add_row.addWidget(QLabel("Product:"))
        add_row.addWidget(self._product_cb, 2)
        add_row.addWidget(QLabel("Qty:"))
        add_row.addWidget(self._qty_spin, 1)
        add_row.addWidget(add_btn)
        add_row.addWidget(rem_btn)
        lines_lay.addLayout(add_row)

        root.addWidget(lines_grp)

        self._totals_lbl = QLabel("Total: €0.00  |  Margin: €0.00  |  Margin %: 0.0%")
        self._totals_lbl.setStyleSheet("font-weight:bold; color:#2E7D32; font-size:13px; padding:4px;")
        root.addWidget(self._totals_lbl)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._validate)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

        if order:
            if order.customer_name in self._customer_map:
                self._customer_cb.setCurrentText(order.customer_name)
            for line in order.lines:
                self._lines.append((line.product_id, line.quantity))
                fill_table_row(self._lines_table, [
                    line.product_name,
                    line.quantity,
                    f"{line.sales_price:.2f}",
                    f"{line.cost_price:.2f}",
                    f"{line.margin_eur:.2f}",
                    f"{line.margin_percent:.1f}%",
                ])
            self._update_totals()

    def _add_line(self):
        pname = self._product_cb.currentText()
        if not pname:
            return
        pid = self._product_map[pname]
        qty = self._qty_spin.value()
        product = self.erp.get_product_by_id(pid)
        if not product:
            return

        margin_eur = (product.sales_price - product.cost_price) * qty
        margin_pct = (
            ((product.sales_price - product.cost_price) / product.sales_price * 100)
            if product.sales_price > 0 else 0.0
        )

        self._lines.append((pid, qty))
        fill_table_row(self._lines_table, [
            product.name,
            qty,
            f"{product.sales_price:.2f}",
            f"{product.cost_price:.2f}",
            f"{margin_eur:.2f}",
            f"{margin_pct:.1f}%",
        ])
        self._update_totals()

    def _remove_line(self):
        row = self._lines_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No selection", "Select a line to remove.")
            return
        self._lines_table.removeRow(row)
        del self._lines[row]
        self._update_totals()

    def _update_totals(self):
        total = 0.0; margin = 0.0
        for pid, qty in self._lines:
            p = self.erp.get_product_by_id(pid)
            if p:
                total += p.sales_price * qty
                margin += (p.sales_price - p.cost_price) * qty
        pct = (margin / total * 100) if total > 0 else 0.0
        self._totals_lbl.setText(
            f"Total: €{total:.2f}  |  Margin: €{margin:.2f}  |  Margin %: {pct:.1f}%"
        )

    def _validate(self):
        if not self._customer_cb.currentText():
            QMessageBox.warning(self, "Validation", "Please select a customer.")
            return
        if not self._lines:
            QMessageBox.warning(self, "Validation", "Add at least one order line.")
            return
        self.accept()

    def get_data(self) -> dict:
        cname = self._customer_cb.currentText()
        return {
            "customer_id": self._customer_map[cname],
            "status": "order",
            "lines": list(self._lines),
        }


class OrderDetailDialog(QDialog):

    def __init__(self, parent, order):
        super().__init__(parent)
        self.setWindowTitle(f"Order #{order.order_number} – Details")
        self.setMinimumSize(680, 500)

        root = QVBoxLayout(self)
        root.setSpacing(10)

        # Customer info
        info_grp = QGroupBox("Customer")
        info_lay = QFormLayout(info_grp)
        info_lay.addRow("Name:", QLabel(order.customer_name))
        info_lay.addRow("Address:", QLabel(order.customer_address))
        info_lay.addRow("Phone:", QLabel(order.customer_phone))
        info_lay.addRow("Email:", QLabel(order.customer_email))
        root.addWidget(info_grp)

        # Order meta
        meta_grp = QGroupBox("Order Info")
        meta_lay = QFormLayout(meta_grp)
        meta_lay.addRow("Order #:", QLabel(f"#{order.order_number}"))
        meta_lay.addRow("Date:", QLabel(order.created_at))
        meta_lay.addRow("Status:", QLabel(order.status.capitalize()))
        meta_lay.addRow("Created by:", QLabel(order.created_by_user))
        root.addWidget(meta_grp)

        # Lines table
        lines_grp = QGroupBox("Order Lines")
        lines_lay = QVBoxLayout(lines_grp)
        t = make_table(["Product", "Qty", "Unit Price (€)", "Unit Cost (€)", "Margin (€)", "Margin (%)"])
        for line in order.lines:
            fill_table_row(t, [
                line.product_name,
                line.quantity,
                f"{line.sales_price:.2f}",
                f"{line.cost_price:.2f}",
                f"{line.margin_eur:.2f}",
                f"{line.margin_percent:.1f}%",
            ])
        lines_lay.addWidget(t)
        root.addWidget(lines_grp)

        # Totals
        pct = order.margin_percent_total
        tot_lbl = QLabel(
            f"Total: €{order.total_price:.2f}  |  "
            f"Margin: €{order.total_margin:.2f}  |  "
            f"Margin %: {pct:.1f}%"
        )
        tot_lbl.setStyleSheet("font-weight:bold; color:#2E7D32; font-size:13px; padding:4px;")
        root.addWidget(tot_lbl)

        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(self.reject)
        root.addWidget(close_btn)



class DashboardWidget(QWidget):
    def __init__(self, erp: ERPSystem):
        super().__init__()
        self.erp = erp
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)
        root.addWidget(section_title("Dashboard"))

        self._stats_lbl = QLabel()
        self._stats_lbl.setWordWrap(True)
        self._stats_lbl.setStyleSheet("font-size:14px; line-height:1.6;")
        root.addWidget(self._stats_lbl)

        self._canvas = FigureCanvas(Figure(figsize=(6, 3.5)))
        root.addWidget(self._canvas)
        root.addStretch()

    def refresh(self):
        s = self.erp.get_stats()
        self._stats_lbl.setText(
            f"<b>Orders:</b> {s['order_count']}  &nbsp;&nbsp; "
            f"<b>Customers:</b> {s['customer_count']}  &nbsp;&nbsp; "
            f"<b>Products:</b> {s['product_count']}<br><br>"
            f"<b>Revenue:</b> €{s['revenue']:.2f}  &nbsp;&nbsp; "
            f"<b>Cost:</b> €{s['cost']:.2f}  &nbsp;&nbsp; "
            f"<b>Profit:</b> €{s['profit']:.2f}  &nbsp;&nbsp; "
            f"<b>Margin:</b> {s['margin_pct']:.1f}%"
        )
        fig = self._canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        vals = [s["revenue"], s["cost"], s["profit"]]
        colors = ["#4CAF50", "#EF5350", "#1976D2"]
        bars = ax.bar(["Revenue", "Cost", "Profit"], vals, color=colors, width=0.5)
        ax.set_ylabel("€")
        ax.set_title("Financial Overview", fontsize=11)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f"€{val:.0f}", ha="center", va="bottom", fontsize=9)
        self._canvas.draw()


#customers
class CustomerWidget(QWidget):
    def __init__(self, erp: ERPSystem):
        super().__init__()
        self.erp = erp
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)
        root.addWidget(section_title("Customers"))

        # Toolbar
        toolbar = QHBoxLayout()
        self._add_btn = btn("＋ New Customer", "primary")
        self._edit_btn = btn("✏ Edit", "warning")
        self._del_btn = btn("✕ Delete", "danger")
        self._add_btn.clicked.connect(self._on_add)
        self._edit_btn.clicked.connect(self._on_edit)
        self._del_btn.clicked.connect(self._on_delete)
        toolbar.addWidget(self._add_btn)
        toolbar.addWidget(self._edit_btn)
        toolbar.addWidget(self._del_btn)
        toolbar.addStretch()
        root.addLayout(toolbar)

        self._table = make_table(["Name", "Phone", "Email", "Address"])
        self._table.doubleClicked.connect(self._on_edit)
        root.addWidget(self._table)

    def refresh(self):
        self._table.setRowCount(0)
        for c in self.erp.customers:
            fill_table_row(self._table, [c.name, c.phone, c.email, c.address])

    def _selected_customer(self):
        row = self._table.currentRow()
        if row < 0:
            return None
        return self.erp.customers[row]

    def _on_add(self):
        dlg = CustomerDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, msg = self.erp.add_customer(d["name"], d["address"], d["phone"], d["email"])
            if ok:
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_edit(self):
        c = self._selected_customer()
        if not c:
            QMessageBox.information(self, "No selection", "Select a customer to edit.")
            return
        dlg = CustomerDialog(self, customer=c)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, msg = self.erp.update_customer(c.id, d["name"], d["address"], d["phone"], d["email"])
            if ok:
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_delete(self):
        c = self._selected_customer()
        if not c:
            QMessageBox.information(self, "No selection", "Select a customer to delete.")
            return
        if confirm_delete(self, "customer"):
            self.erp.delete_customer(c.id)
            self.refresh()


#products
class ProductWidget(QWidget):
    def __init__(self, erp: ERPSystem):
        super().__init__()
        self.erp = erp
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)
        root.addWidget(section_title("Products & Inventory"))

        toolbar = QHBoxLayout()
        self._add_btn = btn("＋ New Product", "primary")
        self._edit_btn = btn("✏ Edit", "warning")
        self._del_btn = btn("✕ Delete", "danger")
        self._add_btn.clicked.connect(self._on_add)
        self._edit_btn.clicked.connect(self._on_edit)
        self._del_btn.clicked.connect(self._on_delete)
        toolbar.addWidget(self._add_btn)
        toolbar.addWidget(self._edit_btn)
        toolbar.addWidget(self._del_btn)
        toolbar.addStretch()
        root.addLayout(toolbar)

        self._table = make_table(
            ["Name", "Sales €", "Cost €", "Margin €", "Margin %", "Qty", "Description"]
        )
        self._table.doubleClicked.connect(self._on_edit)
        root.addWidget(self._table)

    def refresh(self):
        self._table.setRowCount(0)
        for p in self.erp.products:
            fill_table_row(self._table, [
                p.name,
                f"{p.sales_price:.2f}",
                f"{p.cost_price:.2f}",
                f"{p.margin_eur:.2f}",
                f"{p.margin_percent:.1f}%",
                p.quantity,
                p.description,
            ])

    def _selected_product(self):
        row = self._table.currentRow()
        if row < 0:
            return None
        return self.erp.products[row]

    def _on_add(self):
        dlg = ProductDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, msg = self.erp.add_product(
                d["name"], d["sales_price"], d["cost_price"], d["quantity"], d["description"]
            )
            if ok:
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_edit(self):
        p = self._selected_product()
        if not p:
            QMessageBox.information(self, "No selection", "Select a product to edit.")
            return
        dlg = ProductDialog(self, product=p)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, msg = self.erp.update_product(
                p.id, d["name"], d["sales_price"], d["cost_price"], d["quantity"], d["description"]
            )
            if ok:
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_delete(self):
        p = self._selected_product()
        if not p:
            QMessageBox.information(self, "No selection", "Select a product to delete.")
            return
        if confirm_delete(self, "product"):
            self.erp.delete_product(p.id)
            self.refresh()


#orders
class OrderWidget(QWidget):
    def __init__(self, erp: ERPSystem, username: str):
        super().__init__()
        self.erp = erp
        self.username = username
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)
        root.addWidget(section_title("Orders & Quotations"))

        toolbar = QHBoxLayout()
        self._new_btn = btn("New Order", "primary")
        self._view_btn = btn("View", "secondary")
        self._edit_btn = btn("Edit", "warning")
        self._del_btn = btn("Delete", "danger")
        self._new_btn.clicked.connect(self._on_new)
        self._view_btn.clicked.connect(self._on_view)
        self._edit_btn.clicked.connect(self._on_edit)
        self._del_btn.clicked.connect(self._on_delete)
        toolbar.addWidget(self._new_btn)
        toolbar.addWidget(self._view_btn)
        toolbar.addWidget(self._edit_btn)
        toolbar.addWidget(self._del_btn)
        toolbar.addStretch()
        root.addLayout(toolbar)

        self._table = make_table(
            ["Order #", "Customer", "Date", "Status", "Total (€)", "Margin (€)", "Margin %"]
        )
        self._table.doubleClicked.connect(self._on_view)
        root.addWidget(self._table)

    def refresh(self):
        self._table.setRowCount(0)
        for o in self.erp.orders:
            fill_table_row(self._table, [
                f"#{o.order_number}",
                o.customer_name,
                o.created_at,
                o.status.capitalize(),
                f"{o.total_price:.2f}",
                f"{o.total_margin:.2f}",
                f"{o.margin_percent_total:.1f}%",
            ])

    def _selected_order(self):
        row = self._table.currentRow()
        if row < 0:
            return None
        return self.erp.orders[row]

    def _on_new(self):
        if not self.erp.customers:
            QMessageBox.warning(self, "No Customers", "Please add a customer first.")
            return
        if not self.erp.products:
            QMessageBox.warning(self, "No Products", "Please add a product first.")
            return
        dlg = OrderDialog(self, erp=self.erp)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, msg = self.erp.create_order(d["customer_id"], self.username, d["lines"], d["status"])
            if ok:
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_view(self):
        o = self._selected_order()
        if not o:
            QMessageBox.information(self, "No selection", "Select an order to view.")
            return
        dlg = OrderDetailDialog(self, o)
        dlg.exec()

    def _on_edit(self):
        o = self._selected_order()
        if not o:
            QMessageBox.information(self, "No selection", "Select an order to edit.")
            return
        dlg = OrderDialog(self, erp=self.erp, order=o)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, msg = self.erp.update_order(o.id, d["customer_id"], d["lines"], d["status"])
            if ok:
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_delete(self):
        o = self._selected_order()
        if not o:
            QMessageBox.information(self, "No selection", "Select an order to delete.")
            return
        if confirm_delete(self, "order"):
            self.erp.delete_order(o.id)
            self.refresh()



class FarmWidget(QWidget):

    _FIELDS = [
        ("length",                  "Length (m)",                    "float",  10.0),
        ("width",                   "Width (m)",                     "float",   5.0),
        ("height",                  "Height (m)",                    "float",   3.0),
        ("floors",                  "Growing Floors / Racks",        "int",      3),
        ("efficiency",              "Space Efficiency (0–1)",        "float",  0.75),
        ("electricity_rate",        "Electricity Rate (€/kWh)",      "float",  0.25),
        ("water_rate",              "Water Rate (€/litre)",          "float", 0.003),
        ("kwh_per_sqm_per_day",     "kWh per m² per day",            "float",   0.3),
        ("liters_per_sqm_per_day",  "Litres per m² per day",         "float",   3.0),
        ("seed_cost_per_sqm",       "Seed Cost per m² per cycle (€)","float",   1.0),
        ("yield_kg_per_sqm",        "Yield per m² per cycle (kg)",   "float",   3.0),
        ("price_per_kg",            "Selling Price (€/kg)",          "float",   8.0),
        ("cycle_days",              "Harvest Cycle (days)",           "int",    30),
    ]

    def __init__(self, erp: ERPSystem):
        super().__init__()
        self.erp = erp
        self._inputs: dict[str, QDoubleSpinBox | QSpinBox] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)
        root.addWidget(section_title("Farm Configuration"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        form_lay = QFormLayout(inner)
        form_lay.setSpacing(10)
        form_lay.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        for key, label, typ, default in self._FIELDS:
            if typ == "int":
                spin = QSpinBox()
                spin.setMaximum(999999)
                spin.setValue(int(default))
            else:
                spin = QDoubleSpinBox()
                spin.setMaximum(999999)
                spin.setDecimals(4)
                spin.setValue(float(default))
            self._inputs[key] = spin
            form_lay.addRow(label, spin)

        scroll.setWidget(inner)
        root.addWidget(scroll)

        btn_row = QHBoxLayout()
        save_btn = btn("💾 Save Farm Config", "primary")
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

    def refresh(self):
        farm = self.erp.get_farm()
        if not farm:
            return
        d = farm.__dict__
        for key, spin in self._inputs.items():
            val = d.get(key, 0)
            spin.setValue(val)

    def _on_save(self):
        data = {}
        for key, label, typ, _ in self._FIELDS:
            val = self._inputs[key].value()
            data[key] = int(val) if typ == "int" else float(val)
        ok, msg = self.erp.save_farm(data)
        if ok:
            QMessageBox.information(self, "Saved", msg)
        else:
            QMessageBox.warning(self, "Error", msg)


#farm
class FarmSimWidget(QWidget):

    def __init__(self, erp: ERPSystem):
        super().__init__()
        self.erp = erp

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)
        root.addWidget(section_title("Farm Simulation"))

        # Period selector
        per_row = QHBoxLayout()
        per_row.addWidget(QLabel("Simulation period:"))
        self._period_cb = QComboBox()
        self._period_cb.addItems(["30 days", "90 days", "180 days", "365 days"])
        self._period_cb.setCurrentIndex(3)
        per_row.addWidget(self._period_cb)
        run_btn = btn("▶ Run Simulation", "primary")
        run_btn.clicked.connect(self._run)
        per_row.addWidget(run_btn)
        per_row.addStretch()
        root.addLayout(per_row)

        # Results text
        self._results_lbl = QLabel("Configure and save a farm first, then run the simulation.")
        self._results_lbl.setWordWrap(True)
        self._results_lbl.setStyleSheet("font-size:13px; line-height:1.7;")
        root.addWidget(self._results_lbl)

        # Chart
        self._canvas = FigureCanvas(Figure(figsize=(6, 3.5), constrained_layout=False))
        root.addWidget(self._canvas)
        root.addStretch()

    def refresh(self):
        pass

    def _run(self):
        days_map = {"30 days": 30, "90 days": 90, "180 days": 180, "365 days": 365}
        days = days_map[self._period_cb.currentText()]

        stats = self.erp.calculate_farm_stats(days)
        if not stats:
            QMessageBox.warning(self, "No Farm", "Please configure and save your farm first.")
            return

        a = stats
        self._results_lbl.setText(
            f"<b>Simulation period:</b> {a['days']} days &nbsp;|&nbsp; "
            f"<b>Harvest cycles:</b> {a['cycles']:.1f}<br>"
            f"<b>Growing area:</b> {a['growing_area_sqm']:.1f} m²<br><br>"
            f"<b>Electricity:</b> {a['electricity_kwh']:.0f} kWh → "
            f"<b>€{a['electricity_cost']:.2f}</b><br>"
            f"<b>Water:</b> {a['water_liters']:.0f} L → "
            f"<b>€{a['water_cost']:.2f}</b><br>"
            f"<b>Seeds:</b> <b>€{a['seed_cost']:.2f}</b><br><br>"
            f"<b>Total Cost:</b> €{a['total_cost']:.2f} &nbsp;|&nbsp; "
            f"<b>Yield:</b> {a['yield_kg']:.0f} kg<br>"
            f"<b>Revenue:</b> €{a['revenue']:.2f} &nbsp;|&nbsp; "
            f"<b>Profit:</b> €{a['profit']:.2f} &nbsp;|&nbsp; "
            f"<b>Margin:</b> {a['margin_pct']:.1f}%"
        )

        # Draw stacked bar
        fig = self._canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        labels = ["Electricity", "Water", "Seeds", "Revenue", "Profit"]
        values = [
            a["electricity_cost"], a["water_cost"], a["seed_cost"],
            a["revenue"], a["profit"],
        ]
        colors = ["#EF9A9A", "#90CAF9", "#A5D6A7", "#4CAF50", "#1976D2"]
        bars = ax.bar(labels, values, color=colors, width=0.5)
        ax.set_ylabel("€")
        ax.set_title(f"Farm Economics – {days} days", fontsize=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(values) * 0.01,
                    f"€{val:.0f}", ha="center", va="bottom", fontsize=8)
        self._canvas.draw()


#stats
class StatsWidget(QWidget):
    def __init__(self, erp: ERPSystem):
        super().__init__()
        self.erp = erp

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)
        root.addWidget(section_title("Statistics"))

        self._summary_lbl = QLabel()
        self._summary_lbl.setWordWrap(True)
        self._summary_lbl.setStyleSheet("font-size:13px;")
        root.addWidget(self._summary_lbl)

        self._canvas = FigureCanvas(Figure(figsize=(7, 4), constrained_layout=False))
        root.addWidget(self._canvas)
        root.addStretch()

    def refresh(self):
        s = self.erp.get_stats()
        self._summary_lbl.setText(
            f"<b>Orders:</b> {s['order_count']}  &nbsp;|&nbsp; "
            f"<b>Customers:</b> {s['customer_count']}  &nbsp;|&nbsp; "
            f"<b>Products:</b> {s['product_count']}<br>"
            f"<b>Revenue:</b> €{s['revenue']:.2f}  &nbsp;|&nbsp; "
            f"<b>Cost:</b> €{s['cost']:.2f}  &nbsp;|&nbsp; "
            f"<b>Profit:</b> €{s['profit']:.2f}  &nbsp;|&nbsp; "
            f"<b>Overall Margin:</b> {s['margin_pct']:.1f}%"
        )
        self._draw_charts(s)

    def _draw_charts(self, s: dict):
        fig = self._canvas.figure
        fig.clear()

        axes = fig.subplots(1, 2)

        # Left: financial bar chart
        ax1 = axes[0]
        ax1.bar(
            ["Revenue", "Cost", "Profit"],
            [s["revenue"], s["cost"], s["profit"]],
            color=["#4CAF50", "#EF5350", "#1976D2"],
            width=0.5,
        )
        ax1.set_title("Financials", fontsize=10)
        ax1.set_ylabel("€")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)

        # Right: per-order margin chart
        ax2 = axes[1]
        orders = self.erp.orders
        if orders:
            nums = [f"#{o.order_number}" for o in orders]
            margins = [o.margin_percent_total for o in orders]
            ax2.bar(nums, margins, color="#81C784", width=0.5)
            ax2.axhline(0, color="grey", linewidth=0.8)
            ax2.set_title("Margin % per Order", fontsize=10)
            ax2.set_ylabel("%")
            ax2.tick_params(axis="x", rotation=45)
            ax2.spines["top"].set_visible(False)
            ax2.spines["right"].set_visible(False)
        else:
            ax2.text(0.5, 0.5, "No orders yet", ha="center", va="center", transform=ax2.transAxes)
            ax2.set_title("Margin % per Order", fontsize=10)

        self._canvas.draw()



class ExportWidget(QWidget):
    def __init__(self, erp: ERPSystem):
        super().__init__()
        self.erp = erp

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)
        root.addWidget(section_title("Export Data"))

        desc = QLabel(
            "Export your data as CSV files. You can open these in Excel or any spreadsheet app."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#555; margin-bottom:8px;")
        root.addWidget(desc)

        for label, handler in [
            ("📋 Export Customers (CSV)", self._export_customers),
            ("📦 Export Products (CSV)", self._export_products),
            ("📄 Export Orders (CSV)", self._export_orders),
        ]:
            b = btn(label, "secondary")
            b.setMinimumHeight(44)
            b.clicked.connect(handler)
            root.addWidget(b)

        root.addStretch()

    def refresh(self):
        pass

    def _save_csv(self, content: str, default_name: str):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", default_name, "CSV Files (*.csv)"
        )
        if path:
            with open(path, "w", newline="", encoding="utf-8") as f:
                f.write(content)
            QMessageBox.information(self, "Exported", f"File saved:\n{path}")

    def _export_customers(self):
        self._save_csv(self.erp.export_customers_csv(), "customers.csv")

    def _export_products(self):
        self._save_csv(self.erp.export_products_csv(), "products.csv")

    def _export_orders(self):
        self._save_csv(self.erp.export_orders_csv(), "orders.csv")


# MAIN WINDOWS

class MainWindow(QMainWindow):

    _PAGES = [
        ("Dashboard",    0),
        ("Customers",    1),
        ("Products",     2),
        ("Orders",       3),
        ("Farm Setup",   4),
        ("Simulation",   5),
        ("Statistics",   6),
        ("Export",       7),
    ]

    def __init__(self, erp: ERPSystem, username: str):
        super().__init__()
        self.erp = erp
        self.username = username
        self.setWindowTitle(f"VacuumWood ERP  –  {username}")
        self.setMinimumSize(1050, 660)
        self._active_page = 0

        central = QWidget()
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

#sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(0, 0, 0, 0)
        sb_lay.setSpacing(0)

        # Logo / brand
        brand = QLabel("VACUUM\nWOOD\nTECH.")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet(
            "color:#4CAF50; font-size:16px; font-weight:900; "
            "padding:22px 10px 18px 10px; letter-spacing:2px; line-height:1.4;"
        )
        sb_lay.addWidget(brand)

        self._sidebar_btns: list[QPushButton] = []
        for label, idx in self._PAGES:
            b = QPushButton(label)
            b.setObjectName("sidebar_btn")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setProperty("active", idx == 0)
            b.clicked.connect(lambda _, i=idx: self._navigate(i))
            sb_lay.addWidget(b)
            self._sidebar_btns.append(b)

        sb_lay.addStretch()

        user_lbl = QLabel(f"👤  {username}")
        user_lbl.setStyleSheet("color:#78909C; font-size:11px; padding:8px 16px;")
        sb_lay.addWidget(user_lbl)

        logout_btn = QPushButton("  ⏻  Logout")
        logout_btn.setObjectName("logout_btn")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self._logout)
        sb_lay.addWidget(logout_btn)

        outer.addWidget(sidebar)

        self._stack = QStackedWidget()
        self._widgets: list[QWidget] = [
            DashboardWidget(erp),
            CustomerWidget(erp),
            ProductWidget(erp),
            OrderWidget(erp, username),
            FarmWidget(erp),
            FarmSimWidget(erp),
            StatsWidget(erp),
            ExportWidget(erp),
        ]
        for w in self._widgets:
            self._stack.addWidget(w)

        outer.addWidget(self._stack, 1)

        self._navigate(0)

    def _navigate(self, index: int):
        self._active_page = index
        self._stack.setCurrentIndex(index)
        w = self._widgets[index]
        if hasattr(w, "refresh"):
            w.refresh()
        # sidebar button appearance
        for i, b in enumerate(self._sidebar_btns):
            b.setProperty("active", i == index)
            b.style().unpolish(b)
            b.style().polish(b)

    def _logout(self):
        self.close()
        self._login_window = LoginWindow()
        self._login_window.show()


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.erp = ERPSystem()
        self.setWindowTitle("VacuumWood ERP – Login")
        self.setFixedSize(400, 520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(14)

        brand = QLabel("<b>VACUUM<br>WOOD<br><span style='color:#4CAF50;'>TECH.</span></b>")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet("font-size:36px; color:#1a1a1a; line-height:1.3;")
        layout.addWidget(brand)

        sub = QLabel("Indoor Vertical Farm ERP")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color:#78909C; font-size:12px; margin-bottom:20px;")
        layout.addWidget(sub)

        self._username = QLineEdit()
        self._username.setPlaceholderText("Username")
        self._username.setMinimumHeight(40)

        self._password = QLineEdit()
        self._password.setPlaceholderText("Password")
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.setMinimumHeight(40)
        self._password.returnPressed.connect(self._login)

        layout.addWidget(self._username)
        layout.addWidget(self._password)

        login_btn = btn("Login", "primary")
        login_btn.setMinimumHeight(42)
        login_btn.clicked.connect(self._login)

        reg_btn = btn("Register", "secondary")
        reg_btn.setMinimumHeight(42)
        reg_btn.clicked.connect(self._register)

        layout.addWidget(login_btn)
        layout.addWidget(reg_btn)
        layout.addStretch()

        footer = QLabel("© VacuumWood Tech – Mini ERP Y2 Project")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color:#BDBDBD; font-size:10px;")
        layout.addWidget(footer)

    def _login(self):
        ok, user = self.erp.authenticate(
            self._username.text().strip(),
            self._password.text().strip()
        )
        if ok:
            self._main = MainWindow(self.erp, user.username)
            self._main.show()
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def _register(self):
        ok, msg = self.erp.register_user(
            self._username.text().strip(),
            self._password.text().strip()
        )
        if ok:
            QMessageBox.information(self, "Registered", msg)
        else:
            QMessageBox.warning(self, "Error", msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())