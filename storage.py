import json
import os


class DataManager:
    def __init__(self, filepath="data/app_data.json"):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
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