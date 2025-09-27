import re
import logging
from urllib.parse import urlparse, parse_qs
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def extract_domain(url: str) -> str:
    """Extrait le domaine d'une URL"""
    parsed = urlparse(url)
    return parsed.netloc.lower()

def parse_search_command(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse une commande de recherche
    Format: /find <url> "titre episode" [lang]
    """
    pattern = r'/find\s+(\S+)\s+"([^"]+)"(?:\s+(\S+))?'
    match = re.match(pattern, text)
    
    if match:
        url, query, lang = match.groups()
        return url, query, lang or "vostfr"
    return None, None, None

def format_size(bytes_size: int) -> str:
    """Formate une taille en bytes"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def clean_filename(filename: str) -> str:
    """Nettoie un nom de fichier"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)
