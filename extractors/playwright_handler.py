import asyncio
import logging
import re
from extractors.base import BaseExtractor, ExtractResult, VideoLink

logger = logging.getLogger(__name__)

# Import conditionnel de Playwright
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright non disponible - fallback vers requests")

class PlaywrightExtractor(BaseExtractor):
    def __init__(self):
        super().__init__()
        self.video_patterns = [
            r'\.mp4(\?|$)',
            r'\.m3u8(\?|$)',
            r'\.webm(\?|$)',
            r'/v/\d+/',
            r'video\.sibnet\.ru/.*?/video',
        ]
    
    def can_handle(self, domain: str) -> bool:
        return True  # Fallback universel
    
    async def extract(self, url: str, query: str, lang: str = "") -> ExtractResult:
        if not PLAYWRIGHT_AVAILABLE:
            return ExtractResult(
                success=False,
                links=[],
                error="Playwright non disponible - utilisez un autre extracteur",
                source="playwright"
            )
        
        captured_urls = []
        
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()
                
                # Intercepte les requêtes réseau
                async def handle_response(response):
                    url = response.url
                    for pattern in self.video_patterns:
                        if re.search(pattern, url, re.IGNORECASE):
                            captured_urls.append(url)
                            logger.info(f"Captured video URL: {url}")
                
                page.on("response", handle_response)
                
                # Navigation vers la page avec options améliorées
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                
                # Recherche si nécessaire
                if query:
                    # Tente de trouver un champ de recherche
                    search_selectors = [
                        'input[type="search"]',
                        'input[placeholder*="search" i]',
                        'input[placeholder*="recherche" i]',
                        'input[name*="search" i]',
                        'input[name="q"]',
                        '#search',
                        '.search-input'
                    ]
                    
                    for selector in search_selectors:
                        try:
                            search_input = await page.wait_for_selector(selector, timeout=3000)
                            if search_input:
                                await search_input.fill(query)
                                await search_input.press("Enter")
                                await page.wait_for_load_state("networkidle", timeout=10000)
                                break
                        except:
                            continue
                    
                    # Clique sur le premier résultat pertinent
                    await asyncio.sleep(2)
                    
                    # Patterns pour les liens de résultats
                    result_selectors = [
                        f'a[href*="{query.split()[0].lower()}"]',
                        '.video-title a',
                        '.episode-link',
                        '.result-item a'
                    ]
                    
                    for selector in result_selectors:
                        try:
                            result = await page.wait_for_selector(selector, timeout=3000)
                            if result:
                                await result.click()
                                await page.wait_for_load_state("networkidle", timeout=10000)
                                break
                        except:
                            continue
                
                # Attente supplémentaire pour capturer les vidéos
                await asyncio.sleep(3)
                
                # Recherche de liens vidéo dans la page
                video_elements = await page.query_selector_all('video source, video, iframe[src*="video"], a[href$=".mp4"], a[href$=".m3u8"]')
                
                for elem in video_elements:
                    src = await elem.get_attribute('src') or await elem.get_attribute('href')
                    if src and src not in captured_urls:
                        captured_urls.append(src)
                
                await browser.close()
                
                # Conversion en VideoLink
                links = []
                for url in captured_urls:
                    # Détection du format
                    format_type = "unknown"
                    if '.mp4' in url:
                        format_type = "mp4"
                    elif '.m3u8' in url:
                        format_type = "m3u8"
                    elif '.webm' in url:
                        format_type = "webm"
                    
                    links.append(VideoLink(url=url, format=format_type))
                
                return ExtractResult(
                    success=bool(links),
                    links=links,
                    title=query,
                    source="playwright"
                )
                
            except Exception as e:
                logger.error(f"Playwright extraction error: {e}")
                return ExtractResult(
                    success=False,
                    links=[],
                    error=str(e),
                    source="playwright"
                )
