# -*- coding: utf-8 -*-
import re
import urllib.parse
from typing import Optional
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

def normalize_sibnet_url(url: str) -> Optional[str]:
    """
    Convertit divers formats Sibnet en lien partage public:
      - .../shell.php?videoid=XXXX   -> https://video.sibnet.ru/videoXXXX
      - .../frame.php?videoid=XXXX   -> https://video.sibnet.ru/videoXXXX
      - .../videoXXXX-Titre/         -> garde le format complet (avec titre)
    Retourne None si ce n'est pas Sibnet.
    """
    if not url:
        return None
    low = url.lower()
    if "sibnet" not in low:
        return None

    # Cas 1: embed shell/frame -> convertir en videoXXX
    m = re.search(r"(?:shell|frame)\.php\?videoid=(\d+)", url, flags=re.I)
    if m:
        return f"https://video.sibnet.ru/video{m.group(1)}"

    # Cas 2: déjà un lien /videoXXX -> garder tel quel (avec titre si présent)
    if re.search(r"/video\d+", url, flags=re.I):
        # S'assurer que c'est une URL complète
        if url.startswith("https://video.sibnet.ru/"):
            return url
        elif url.startswith("/video"):
            return f"https://video.sibnet.ru{url}"
        else:
            return url

    # Cas 3: autre format Sibnet -> renvoyer brut
    return url

def ddg_first_sibnet(query: str, timeout: int = 15) -> Optional[str]:
    """
    Fait 'site:video.sibnet.ru "query"' sur DuckDuckGo HTML et renvoie le 1er lien
    qui ressemble à /videoXXXX avec titre complet.
    """
    # Essayer plusieurs variantes de recherche pour améliorer les résultats
    search_queries = [
        f'site:video.sibnet.ru "{query}"',  # Recherche exacte
        f'site:video.sibnet.ru {query}',     # Recherche normale
        f'{query} site:video.sibnet.ru'      # Ordre différent
    ]
    
    url = "https://duckduckgo.com/html/"
    
    for q in search_queries:
        try:
            print(f"🦆 DuckDuckGo: {q}")
            html = requests.get(url, params={"q": q}, headers=HEADERS, timeout=timeout).text
            soup = BeautifulSoup(html, "lxml")
            
            results_found = []
            
            # Chercher les résultats avec différents sélecteurs
            selectors = [".result", ".web-result", ".results_links"]
            
            for selector in selectors:
                for res in soup.select(selector):
                    # Chercher le lien principal
                    link_selectors = [".result__a", "h2 a", ".result-link", "a"]
                    
                    for link_sel in link_selectors:
                        a = res.select_one(link_sel)
                        if not a:
                            continue
                            
                        href = a.get("href", "")
                        title = a.get_text().strip()
                        
                        # Vérifier si c'est un lien Sibnet vidéo (direct ou via redirect DuckDuckGo)
                        actual_url = href
                        
                        # Gérer les redirects DuckDuckGo
                        if "duckduckgo.com/l/" in href and "uddg=" in href:
                            import urllib.parse
                            # Extraire l'URL réelle du paramètre uddg
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                            if "uddg" in parsed:
                                actual_url = urllib.parse.unquote(parsed["uddg"][0])
                                print(f"🔗 URL extraite du redirect: {actual_url}")
                        
                        if ("video.sibnet.ru" in actual_url or "sibnet" in actual_url) and re.search(r"video\d+", actual_url):
                            # Prioriser les liens avec des titres pertinents
                            relevance_score = 0
                            query_words = query.lower().split()
                            
                            for word in query_words:
                                if word in title.lower() or word in actual_url.lower():
                                    relevance_score += 1
                            
                            results_found.append((actual_url, title, relevance_score))
            
            # Trier par pertinence et retourner le meilleur
            if results_found:
                results_found.sort(key=lambda x: x[2], reverse=True)
                best_url = results_found[0][0]
                best_title = results_found[0][1]
                
                print(f"✅ DDG trouvé: {best_url}")
                print(f"   Titre: {best_title[:60]}...")
                
                # Normaliser et retourner
                normalized = normalize_sibnet_url(best_url)
                return normalized if normalized else best_url
                
        except Exception as e:
            print(f"❌ Erreur DDG: {e}")
            continue
    
    print("❌ DDG: aucun résultat trouvé")
    return None

def sibnet_internal_search(query: str, timeout: int = 15) -> Optional[str]:
    """
    ⚠️  Sibnet bloque les recherches automatisées avec un captcha "Я не робот"
    Nous utilisons donc directement DuckDuckGo avec site:video.sibnet.ru
    """
    
    print(f"🔍 Recherche Sibnet via DuckDuckGo: {query}")
    print("ℹ️  Sibnet bloque les robots - utilisation de DuckDuckGo")
    
    # Utiliser directement DuckDuckGo au lieu de la recherche interne Sibnet
    return ddg_first_sibnet(query, timeout)

# Fonction sibnet_search_php supprimée car Sibnet bloque les robots

def get_sibnet_share_link(query_or_url: str) -> Optional[str]:
    """
    ⚠️  LIMITATION ACTUELLE: Sibnet et DuckDuckGo bloquent les recherches automatisées
    
    1) Si c'est un lien Sibnet direct -> normalise et retourne
    2) Pour les recherches: impossible à cause des captchas anti-bot
    """
    
    # Si c'est déjà une URL Sibnet, on peut la normaliser
    if query_or_url.startswith("http") and "sibnet" in query_or_url.lower():
        print(f"🔗 Normalisation URL Sibnet: {query_or_url}")
        normalized = normalize_sibnet_url(query_or_url)
        if normalized:
            return normalized
        return query_or_url  # Retourner l'original si normalisation échoue
    
    # Pour les recherches, expliquer la limitation
    print(f"⚠️  Recherche Sibnet impossible: '{query_or_url}'")
    print("   Raison: Sibnet et DuckDuckGo bloquent les bots avec des captchas")
    print("   Suggestion: Utiliser un autre site ou fournir un lien Sibnet direct")
    
    return None  # Retourner None pour indiquer l'échec

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python sibnet_simple.py <mot-clé ou URL sibnet>")
        raise SystemExit(1)
    print(get_sibnet_share_link(" ".join(sys.argv[1:])))