import json, os


class Settings:

    @staticmethod
    def load_settings(key):
        with open(os.path.join(os.path.dirname(__file__), "settings.json")) as f:
            data = json.load(f)
            return data[key]

