import time
from collections import defaultdict
from typing import Dict
import asyncio

class RateLimiter:
    def __init__(self, requests_per_minute: int = 10, per_user_limit: int = 5):
        self.requests_per_minute = requests_per_minute
        self.per_user_limit = per_user_limit
        self.global_requests: list = []
        self.user_requests: Dict[int, list] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def check_and_update(self, user_id: int) -> bool:
        """Vérifie si une requête peut être effectuée"""
        async with self.lock:
            current_time = time.time()
            minute_ago = current_time - 60
            
            # Nettoie les anciennes requêtes
            self.global_requests = [t for t in self.global_requests if t > minute_ago]
            self.user_requests[user_id] = [
                t for t in self.user_requests[user_id] if t > minute_ago
            ]
            
            # Vérifie les limites
            if len(self.global_requests) >= self.requests_per_minute:
                return False
            
            if len(self.user_requests[user_id]) >= self.per_user_limit:
                return False
            
            # Enregistre la nouvelle requête
            self.global_requests.append(current_time)
            self.user_requests[user_id].append(current_time)
            
            return True
    
    def get_wait_time(self, user_id: int) -> int:
        """Retourne le temps d'attente en secondes"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        user_times = [t for t in self.user_requests[user_id] if t > minute_ago]
        if user_times:
            oldest = min(user_times)
            wait = 60 - (current_time - oldest)
            return max(0, int(wait))
        return 0
