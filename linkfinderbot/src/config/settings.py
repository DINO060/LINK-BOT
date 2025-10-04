import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration settings for the Telegram link finder bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in environment variables")

# Configuration du crawler
CRAWLER_CONFIG = {
    "max_pages": 60,
    "max_depth": 2,
    "timeout_ms": 15000,
    "headless": True
}

# Configuration de la recherche
SEARCH_CONFIG = {
    "top_k_results": int(os.getenv("MAX_RESULTS", 3)),
    "min_score_threshold": 85,
    "snippet_score_threshold": 70
}

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LANGUAGE = os.getenv("LANGUAGE", "fr")