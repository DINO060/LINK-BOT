from yt_dlp import YoutubeDL
import logging
from extractors.base import BaseExtractor, ExtractResult, VideoLink

logger = logging.getLogger(__name__)

class YtdlpExtractor(BaseExtractor):
    def __init__(self):
        super().__init__()
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
            'socket_timeout': 30,
        }
    
    def can_handle(self, domain: str) -> bool:
        # yt-dlp peut potentiellement gérer n'importe quel site
        return True
    
    async def extract(self, url: str, query: str = "", lang: str = "") -> ExtractResult:
        try:
            # Améliore les options pour les sites difficiles
            ydl_opts = self.ydl_opts.copy()
            ydl_opts.update({
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'referer': url,
                'sleep_interval': 1,
                'max_sleep_interval': 5,
            })
            
            with YoutubeDL(ydl_opts) as ydl:
                # Si on a une URL de page spécifique
                info = ydl.extract_info(url, download=False)
                
                links = []
                
                # Extraction des formats disponibles
                if info and 'formats' in info:
                    formats = sorted(
                        info['formats'], 
                        key=lambda f: (
                            f.get('height', 0),
                            f.get('tbr', 0)
                        ), 
                        reverse=True
                    )
                    
                    for fmt in formats[:5]:  # Top 5 qualités
                        if 'url' in fmt:
                            quality = f"{fmt.get('height', 'N/A')}p" if fmt.get('height') else fmt.get('format_note', 'N/A')
                            links.append(VideoLink(
                                url=fmt['url'],
                                quality=quality,
                                format=fmt.get('ext', 'unknown'),
                                size=fmt.get('filesize')
                            ))
                
                # Si pas de formats mais URL directe
                elif info and 'url' in info:
                    links.append(VideoLink(
                        url=info['url'],
                        format=info.get('ext', 'unknown')
                    ))
                
                return ExtractResult(
                    success=bool(links),
                    links=links,
                    title=info.get('title', query) if info else query,
                    source="yt-dlp"
                )
                
        except Exception as e:
            logger.error(f"yt-dlp extraction error: {e}")
            return ExtractResult(
                success=False,
                links=[],
                error=str(e),
                source="yt-dlp"
            )
