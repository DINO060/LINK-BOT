import os
from dataclasses import dataclass, field
from typing import Dict, List
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

@dataclass
class Config:
    # Bot Telegram
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
    API_ID: int = int(os.getenv("API_ID", "12345"))
    API_HASH: str = os.getenv("API_HASH", "YOUR_API_HASH")
    
    # Rate limiting
    REQUESTS_PER_MINUTE: int = 10
    REQUESTS_PER_USER: int = 5
    
    # Cache
    CACHE_TTL: int = 3600  # 1 heure
    CACHE_SIZE: int = 1000
    
    # Timeouts
    YTDLP_TIMEOUT: int = 30
    PLAYWRIGHT_TIMEOUT: int = 45
    
    # Extracteurs spécialisés par domaine
    DOMAIN_HANDLERS: Dict[str, str] = field(default_factory=lambda: {
        "anime-sama.fr": "animesama",
        "9anime.to": "rawkush",
        "gogoanime.hu": "otakuweber",
        "kissanime.ru": "vnki",
    })
    
    # User agents
    USER_AGENTS: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    ])
    
    # Admins
    ADMIN_IDS: List[int] = field(default_factory=lambda: [123456789])  # Remplacer par vos IDs
