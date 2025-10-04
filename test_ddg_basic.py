#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import urllib.parse

def test_ddg_basic():
    """Test DuckDuckGo avec des termes simples"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    # Test simple
    queries = [
        "site:video.sibnet.ru video",  # Terme très général 
        "sibnet.ru video",             # Sans site:
        "video.sibnet.ru",             # Juste le domaine
    ]
    
    url = "https://duckduckgo.com/html/"
    
    for q in queries:
        try:
            print(f"\n🦆 Test: {q}")
            response = requests.get(url, params={"q": q}, headers=headers, timeout=15)
            print(f"Status: {response.status_code}, Taille: {len(response.text)}")
            
            # Sauvegarder pour debug
            with open(f"ddg_test_{queries.index(q)}.html", "w", encoding="utf-8") as f:
                f.write(response.text[:10000])
            
            soup = BeautifulSoup(response.text, "lxml")
            
            # Compter tous les liens
            all_links = soup.find_all("a", href=True)
            print(f"Total liens: {len(all_links)}")
            
            # Chercher des résultats de recherche
            sibnet_links = []
            ddg_redirects = []
            
            for a in all_links:
                href = a.get("href", "")
                text = a.get_text().strip()
                
                # Lien direct Sibnet
                if "sibnet" in href:
                    sibnet_links.append((href, text))
                
                # Redirect DuckDuckGo
                if "duckduckgo.com/l/" in href and "uddg=" in href:
                    try:
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                        if "uddg" in parsed:
                            actual_url = urllib.parse.unquote(parsed["uddg"][0])
                            if "sibnet" in actual_url:
                                ddg_redirects.append((actual_url, text))
                    except:
                        pass
            
            print(f"Liens Sibnet directs: {len(sibnet_links)}")
            for link, text in sibnet_links[:3]:
                print(f"  - {link} ({text[:40]}...)")
                
            print(f"Redirects DDG vers Sibnet: {len(ddg_redirects)}")  
            for link, text in ddg_redirects[:3]:
                print(f"  - {link} ({text[:40]}...)")
                
            if sibnet_links or ddg_redirects:
                print(f"✅ Trouvé {len(sibnet_links + ddg_redirects)} résultats Sibnet!")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_ddg_basic()