import time
import hashlib
from typing import Optional, Any
from collections import OrderedDict
import json

class Cache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        
    def _make_key(self, site: str, query: str, lang: str = "") -> str:
        """Génère une clé unique pour le cache"""
        raw = f"{site}:{query}:{lang}"
        return hashlib.md5(raw.encode()).hexdigest()
    
    def get(self, site: str, query: str, lang: str = "") -> Optional[Any]:
        """Récupère une valeur du cache"""
        key = self._make_key(site, query, lang)
        
        if key in self.cache:
            entry, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                # Déplace en fin pour LRU
                self.cache.move_to_end(key)
                return entry
            else:
                # Expiré
                del self.cache[key]
        
        return None
    
    def set(self, site: str, query: str, value: Any, lang: str = ""):
        """Ajoute une valeur au cache"""
        key = self._make_key(site, query, lang)
        
        # Limite la taille du cache
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # Supprime le plus ancien
        
        self.cache[key] = (value, time.time())
    
    def clear(self):
        """Vide le cache"""
        self.cache.clear()
