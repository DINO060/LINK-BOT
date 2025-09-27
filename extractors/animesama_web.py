from extractors.base import BaseExtractor, ExtractResult, VideoLink
import httpx
import logging
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class AnimeSamaWebExtractor(BaseExtractor):
    def __init__(self):
        super().__init__()
        self.base_url = "https://anime-sama.fr"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Cache-Control': 'no-cache',
        }
    
    def can_handle(self, domain: str) -> bool:
        return "anime-sama.fr" in domain
    
    async def extract(self, url: str, query: str, lang: str = "vostfr") -> ExtractResult:
        try:
            # Recherche simple sur la page
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code != 200:
                    return ExtractResult(
                        success=False,
                        links=[],
                        error=f"Erreur HTTP {response.status_code}",
                        source="anime-sama-web"
                    )
                
                # Parser le HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                links = []
                
                # Chercher les iframes Sibnet
                iframes = soup.find_all('iframe', src=re.compile(r'sibnet', re.I))
                for iframe in iframes:
                    src = iframe.get('src', '')
                    if src:
                        # Assurer que c'est une URL complète
                        if not src.startswith('http'):
                            src = 'https:' + src if src.startswith('//') else urljoin(url, src)
                        links.append(VideoLink(url=src, format='embedded'))
                
                # Chercher dans les scripts
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        # Patterns pour Sibnet et autres players
                        patterns = [
                            r'src="(https?://video\.sibnet\.ru[^"]+)"',
                            r"src='(https?://video\.sibnet\.ru[^']+)'",
                            r'(https?://[^/]+sibnet[^"\'\\s]+)',
                        ]
                        for pattern in patterns:
                            matches = re.findall(pattern, script.string)
                            for match in matches:
                                if match not in [l.url for l in links]:
                                    links.append(VideoLink(url=match, format='embedded'))
                
                if links:
                    return ExtractResult(
                        success=True,
                        links=links,
                        title=query,
                        source="anime-sama-web"
                    )
                else:
                    return ExtractResult(
                        success=False,
                        links=[],
                        error="Aucun lien vidéo trouvé sur la page",
                        source="anime-sama-web"
                    )
                    
        except Exception as e:
            logger.error(f"AnimeSama extraction error: {e}")
            return ExtractResult(
                success=False,
                links=[],
                error=str(e),
                source="anime-sama-web"
            )
