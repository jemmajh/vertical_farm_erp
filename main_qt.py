import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from erp import ERPSystem


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.erp = ERPSystem()
        self.current_user = None

        self.setWindowTitle("Mini ERP Login")
        self.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Login"))

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register)
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        success, user = self.erp.authenticate(username, password)

        if success:
            self.current_user = user.username
            QMessageBox.information(self, "Success", "Login successful")
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")

    def register(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        success, message = self.erp.register_user(username, password)

        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())