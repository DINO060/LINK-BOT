import subprocess
import json
import logging
from extractors.base import BaseExtractor, ExtractResult, VideoLink

logger = logging.getLogger(__name__)

class AnimeSamaExtractor(BaseExtractor):
    def can_handle(self, domain: str) -> bool:
        return "anime-sama.fr" in domain
    
    async def extract(self, url: str, query: str, lang: str = "vostfr") -> ExtractResult:
        try:
            # Vérifie si anime-sama-api est disponible
            try:
                subprocess.run(["anime-sama", "--version"], capture_output=True, timeout=5)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return ExtractResult(
                    success=False,
                    links=[],
                    error="anime-sama-api non installé - utilisez un autre extracteur",
                    source="anime-sama"
                )
            
            # Utilise anime-sama-api CLI
            cmd = ["anime-sama", "search", query]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return ExtractResult(
                    success=False,
                    links=[],
                    error=f"Erreur anime-sama-api: {result.stderr}",
                    source="anime-sama"
                )
            
            # Parse la sortie JSON (à adapter selon le format réel)
            data = json.loads(result.stdout)
            links = []
            
            for item in data.get("results", []):
                if lang.lower() in item.get("title", "").lower():
                    video_url = item.get("video_url")
                    if video_url:
                        links.append(VideoLink(
                            url=video_url,
                            quality=item.get("quality"),
                            format=item.get("format", "mp4")
                        ))
            
            return ExtractResult(
                success=bool(links),
                links=links,
                title=f"{query} {lang}",
                source="anime-sama"
            )
            
        except Exception as e:
            logger.error(f"AnimeSama extraction error: {e}")
            return ExtractResult(
                success=False,
                links=[],
                error=str(e),
                source="anime-sama"
            )
