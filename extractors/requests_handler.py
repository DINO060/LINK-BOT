import asyncio
import aiohttp
import logging
import re
from bs4 import BeautifulSoup
from extractors.base import BaseExtractor, ExtractResult, VideoLink

logger = logging.getLogger(__name__)

class RequestsExtractor(BaseExtractor):
    """Extracteur basé sur requests/aiohttp comme fallback pour Python 3.13"""
    
    def __init__(self):
        super().__init__()
        self.video_patterns = [
            r'\.mp4(\?|$)',
            r'\.m3u8(\?|$)',
            r'\.webm(\?|$)',
            r'/v/\d+/',
            r'video\.sibnet\.ru/.*?/video',
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def can_handle(self, domain: str) -> bool:
        return True  # Fallback universel
    
    async def extract(self, url: str, query: str, lang: str = "") -> ExtractResult:
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # Récupération de la page
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        return ExtractResult(
                            success=False,
                            links=[],
                            error=f"Erreur HTTP {response.status}",
                            source="requests"
                        )
                    
                    html = await response.text()
                    
                    # Parse avec BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Recherche de liens vidéo
                    video_links = []
                    
                    # Recherche dans les balises video
                    for video in soup.find_all('video'):
                        src = video.get('src')
                        if src:
                            video_links.append(src)
                        
                        # Recherche dans les sources
                        for source in video.find_all('source'):
                            src = source.get('src')
                            if src:
                                video_links.append(src)
                    
                    # Recherche dans les iframes
                    for iframe in soup.find_all('iframe'):
                        src = iframe.get('src')
                        if src and any(pattern in src for pattern in ['video', 'player', 'embed']):
                            video_links.append(src)
                    
                    # Recherche de liens directs
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        for pattern in self.video_patterns:
                            if re.search(pattern, href, re.IGNORECASE):
                                video_links.append(href)
                    
                    # Recherche dans les scripts (pour les URLs cachées)
                    for script in soup.find_all('script'):
                        if script.string:
                            for pattern in self.video_patterns:
                                matches = re.findall(pattern, script.string, re.IGNORECASE)
                                for match in matches:
                                    if isinstance(match, str):
                                        video_links.append(match)
                    
                    # Conversion en VideoLink
                    links = []
                    for video_url in set(video_links):  # Supprime les doublons
                        # Détection du format
                        format_type = "unknown"
                        if '.mp4' in video_url:
                            format_type = "mp4"
                        elif '.m3u8' in video_url:
                            format_type = "m3u8"
                        elif '.webm' in video_url:
                            format_type = "webm"
                        
                        # URL absolue si nécessaire
                        if video_url.startswith('/'):
                            from urllib.parse import urljoin
                            video_url = urljoin(url, video_url)
                        
                        links.append(VideoLink(url=video_url, format=format_type))
                    
                    return ExtractResult(
                        success=bool(links),
                        links=links,
                        title=query,
                        source="requests"
                    )
                    
        except Exception as e:
            logger.error(f"Requests extraction error: {e}")
            return ExtractResult(
                success=False,
                links=[],
                error=str(e),
                source="requests"
            )
