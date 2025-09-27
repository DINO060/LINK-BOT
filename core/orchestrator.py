import asyncio
import logging
from typing import Optional
from config import Config
from core.cache import Cache
from core.rate_limiter import RateLimiter
from extractors.base import ExtractResult
from extractors.animesama_web import AnimeSamaWebExtractor
from extractors.animesama_web import AnimeSamaWebExtractor
from extractors.ytdlp_handler import YtdlpExtractor
from extractors.playwright_handler import PlaywrightExtractor
from extractors.requests_fallback import RequestsFallbackExtractor
from extractors.requests_handler import RequestsExtractor
from utils.helpers import extract_domain

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, config: Config):
        self.config = config
        self.cache = Cache(max_size=config.CACHE_SIZE, ttl=config.CACHE_TTL)
        self.rate_limiter = RateLimiter(
            requests_per_minute=config.REQUESTS_PER_MINUTE,
            per_user_limit=config.REQUESTS_PER_USER
        )
        
        # Initialisation des extracteurs
        self.extractors = {
            'animesama': AnimeSamaWebExtractor(),
            'animesama_web': AnimeSamaWebExtractor(),
            'ytdlp': YtdlpExtractor(),
            'playwright': PlaywrightExtractor(),
            'requests': RequestsFallbackExtractor(),
            'requests': RequestsExtractor(),
        }
    
    async def process_request(
        self, 
        user_id: int, 
        site_url: str, 
        query: str, 
        lang: str = "vostfr"
    ) -> ExtractResult:
        """Traite une requête d'extraction"""
        
        # Vérification du rate limit
        if not await self.rate_limiter.check_and_update(user_id):
            wait_time = self.rate_limiter.get_wait_time(user_id)
            return ExtractResult(
                success=False,
                links=[],
                error=f"Limite de requêtes atteinte. Attendez {wait_time} secondes.",
                source="rate_limiter"
            )
        
        # Vérification du cache
        cached_result = self.cache.get(site_url, query, lang)
        if cached_result:
            logger.info(f"Cache hit for {query} on {site_url}")
            return cached_result
        
        # Extraction du domaine
        domain = extract_domain(site_url)
        
        # Choix de l'extracteur
        result = None
        
        # 1. Essai avec extracteur spécialisé pour anime-sama
        if "anime-sama.fr" in domain:
            logger.info(f"Using anime-sama-web for {domain}")
            result = await self.extractors['animesama_web'].extract(site_url, query, lang)
            if result.success:
                pass  # Continue au cache
        else:
            # Autres extracteurs spécialisés
            for handler_name in self.config.DOMAIN_HANDLERS.values():
                if handler_name in self.extractors:
                    extractor = self.extractors[handler_name]
                    if extractor.can_handle(domain):
                        logger.info(f"Using {handler_name} for {domain}")
                        result = await extractor.extract(site_url, query, lang)
                        if result.success:
                            break
        
        # 2. Essai avec yt-dlp si pas de succès
        if not result or not result.success:
            logger.info(f"Trying yt-dlp for {site_url}")
            result = await self.extractors['ytdlp'].extract(site_url, query, lang)
        
        # 3. Fallback sur Playwright
        if not result.success:
            logger.info(f"Fallback to Playwright for {site_url}")
            result = await self.extractors['playwright'].extract(site_url, query, lang)
        
        # 4. Fallback sur Requests si Playwright échoue
        if not result.success:
            logger.info(f"Fallback to Requests for {site_url}")
            result = await self.extractors['requests'].extract(site_url, query, lang)
        
        # Mise en cache si succès
        if result.success:
            self.cache.set(site_url, query, result, lang)
        
        return result
