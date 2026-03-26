import json
import os
from models import User, to_dict


class Storage:
    def __init__(self, filepath="data/app_data.json"):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as file:
                json.dump({
                    "users": [],
                    "customers": [],
                    "products": [],
                    "orders": []
                }, file, indent=2)

    def load_data(self):
        with open(self.filepath, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_data(self, data):
        with open(self.filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def load_users(self):
        data = self.load_data()
        users = []

        for u in data.get("users", []):
            users.append(User(u["id"], u["username"], u["password"]))

        return users

    def save_users(self, users):
        data = self.load_data()
        data["users"] = [to_dict(u) for u in users]
        self.save_data(data)