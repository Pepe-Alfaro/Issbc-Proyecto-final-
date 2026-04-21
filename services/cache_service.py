import os
import json
import time

class CacheService:
    def __init__(self, cache_file=".cache_issbc.json", expiration_hours=1):
        self.cache_file = cache_file
        self.expiration_seconds = expiration_hours * 3600

    def _load_cache(self):
        if not os.path.exists(self.cache_file):
            return {}
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_cache(self, data):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error guardando caché: {e}")

    def get(self, url):
        cache = self._load_cache()
        if url in cache:
            entry = cache[url]
            # Verificar expiración
            if time.time() - entry.get("timestamp", 0) < self.expiration_seconds:
                print(f"⚡ Recuperando datos de {url} desde la caché local...")
                return entry.get("data")
        return None

    def set(self, url, data):
        cache = self._load_cache()
        cache[url] = {
            "timestamp": time.time(),
            "data": data
        }
        self._save_cache(cache)
