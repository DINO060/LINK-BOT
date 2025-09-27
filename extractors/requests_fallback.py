from extractors.base import BaseExtractor, ExtractResult, VideoLink
import httpx
import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class RequestsFallbackExtractor(BaseExtractor):
    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
        }
        
    def can_handle(self, domain: str) -> bool:
        return True
    
    async def extract(self, url: str, query: str, lang: str = "") -> ExtractResult:
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code != 200:
                    return ExtractResult(
                        success=False,
                        links=[],
                        error=f"HTTP {response.status_code}",
                        source="requests-fallback"
                    )
                
                soup = BeautifulSoup(response.text, 'html.parser')
                links = []
                
                # Chercher toutes les sources vidéo possibles
                # 1. Balises video
                for video in soup.find_all('video'):
                    src = video.get('src')
                    if src:
                        links.append(VideoLink(url=urljoin(url, src), format='mp4'))
                    for source in video.find_all('source'):
                        src = source.get('src')
                        if src:
                            links.append(VideoLink(url=urljoin(url, src), format='mp4'))
                
                # 2. Iframes
                for iframe in soup.find_all('iframe'):
                    src = iframe.get('src', '')
                    if any(x in src.lower() for x in ['video', 'player', 'embed']):
                        full_url = src if src.startswith('http') else urljoin(url, src)
                        links.append(VideoLink(url=full_url, format='embedded'))
                
                # 3. Scripts
                for script in soup.find_all('script'):
                    if script.string:
                        patterns = [
                            r'"(https?://[^"]+\.mp4[^"]*)"',
                            r'"(https?://[^"]+\.m3u8[^"]*)"',
                        ]
                        for pattern in patterns:
                            for match in re.findall(pattern, script.string):
                                links.append(VideoLink(url=match, format='video'))
                
                # Dédupliquer
                seen = set()
                unique_links = []
                for link in links:
                    if link.url not in seen:
                        seen.add(link.url)
                        unique_links.append(link)
                
                return ExtractResult(
                    success=bool(unique_links),
                    links=unique_links[:5],  # Max 5 liens
                    title=query or "Video",
                    source="requests-fallback"
                )
                
        except Exception as e:
            logger.error(f"Requests fallback error: {e}")
            return ExtractResult(
                success=False,
                links=[],
                error=str(e),
                source="requests-fallback"
            )
