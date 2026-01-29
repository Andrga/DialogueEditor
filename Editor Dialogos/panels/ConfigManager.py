import json, os

class ConfigManager:
    DEFAULT = {
        "audio_folder": "",
        "fonts_folder": "",
        "last_project_path": ""
    }

    def __init__(self, file="config.json"):
        self.file = file
        self.config = self._load()

    def _load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return self.DEFAULT.copy()

    def save(self):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def set(self, key, value):
        self.config[key] = value
        self.save()

    def get(self, key):
        return self.config.get(key, "")

    def files(self, key, exts):
        path = self.get(key)
        if not os.path.isdir(path):
            return []
        return sorted(
            f for f in os.listdir(path)
            if f.lower().endswith(tuple(exts))
        )

    # ---- helpers específicos ----
    def audio_files(self):
        return self.files("audio_folder", [".mp3", ".wav", ".ogg", ".flac", ".m4a"])

    def font_files(self):
        return self.files("fonts_folder", [".ttf", ".otf", ".woff", ".woff2"])
