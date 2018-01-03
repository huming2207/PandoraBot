import json
import os


class Settings:

    @staticmethod
    def get(key):
        with open(os.path.join(os.path.dirname(__file__), "settings.json")) as f:
            data = json.load(f)
            return data[key]

