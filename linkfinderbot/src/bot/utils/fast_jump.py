# fast_jump.py
import re
from typing import Optional
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def episode_from_text(text: str) -> Optional[int]:
    """Extrait le premier nombre trouvé dans le texte (ex: "ONE PIECE 100 VF" -> 100)"""
    m = re.search(r"\b(\d{1,4})\b", text)
    return int(m.group(1)) if m else None

def ddg_first_site(domain: str, query: str, timeout: int = 15) -> Optional[str]:
    """Cherche via DuckDuckGo avec site: et retourne le premier résultat"""
    q = f'site:{domain} {query}'
    print(f"🦆 DuckDuckGo: {q}")
    
    try:
        url = "https://duckduckgo.com/html/"
        response = requests.get(url, params={"q": q}, headers=HEADERS, timeout=timeout)
        
        if response.status_code != 200:
            print(f"❌ DuckDuckGo erreur: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, "lxml")
        
        # Chercher le premier résultat avec différents sélecteurs
        selectors = [".result .result__a", ".web-result a", ".results_links a"]
        
        for selector in selectors:
            a = soup.select_one(selector)
            if a and a.get("href"):
                href = a.get("href")
                
                # Gérer les redirects DuckDuckGo
                if "duckduckgo.com/l/" in href and "uddg=" in href:
                    import urllib.parse
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                    if "uddg" in parsed:
                        actual_url = urllib.parse.unquote(parsed["uddg"][0])
                        print(f"✅ URL trouvée: {actual_url}")
                        return actual_url
                
                # Lien direct
                if domain in href:
                    print(f"✅ URL trouvée: {href}")
                    return href
        
        print("❌ Aucun résultat trouvé")
        return None
        
    except Exception as e:
        print(f"❌ Erreur DuckDuckGo: {e}")
        return None