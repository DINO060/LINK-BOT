import requests
from bs4 import BeautifulSoup
import re

def explore_sibnet_search():
    """Explorer les moyens de recherche sur Sibnet"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    print("=== Exploration Sibnet Vidéo ===\n")
    
    # 1. Page principale pour chercher un formulaire de recherche
    try:
        response = requests.get("https://video.sibnet.ru/", headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            
            # Chercher des formulaires
            forms = soup.find_all("form")
            print(f"Formulaires trouvés: {len(forms)}")
            
            for i, form in enumerate(forms):
                action = form.get("action", "")
                method = form.get("method", "GET").upper()
                print(f"  Form {i+1}: action='{action}' method={method}")
                
                # Chercher les champs input
                inputs = form.find_all("input")
                for inp in inputs:
                    name = inp.get("name", "")
                    type_field = inp.get("type", "")
                    if name:
                        print(f"    Input: name='{name}' type='{type_field}'")
            
            print()
            
            # Chercher des liens avec "search" dans l'URL
            search_links = []
            for link in soup.find_all("a", href=True):
                href = link.get("href")
                if "search" in href.lower() or "поиск" in href.lower():
                    search_links.append(href)
            
            print(f"Liens avec 'search': {len(search_links)}")
            for link in search_links[:5]:
                print(f"  - {link}")
            
            print()
            
            # Tenter différents paramètres de recherche sur la page principale
            possible_params = ["q", "query", "search", "s", "keyword", "поиск"]
            query_test = "ONE PIECE"
            
            print("=== Test paramètres de recherche ===")
            for param in possible_params:
                try:
                    search_url = "https://video.sibnet.ru/"
                    resp = requests.get(search_url, params={param: query_test}, headers=headers, timeout=10)
                    print(f"Paramètre '{param}': {resp.status_code}")
                    
                    if resp.status_code == 200 and len(resp.text) > 100000:  # Page non vide
                        # Chercher des résultats de recherche
                        soup_search = BeautifulSoup(resp.text, "lxml")
                        video_links = []
                        
                        for a in soup_search.find_all("a", href=True):
                            href = a.get("href")
                            if href and "/video" in href and re.search(r"video\d+", href):
                                video_links.append(href)
                        
                        if video_links:
                            print(f"  ✅ TROUVÉ! {len(video_links)} liens vidéo")
                            for j, vlink in enumerate(video_links[:3]):
                                print(f"    {j+1}. {vlink}")
                            
                            # Sauvegarder cette recherche réussie
                            with open(f"sibnet_search_success_{param}.html", "w", encoding="utf-8") as f:
                                f.write(resp.text[:20000])
                            
                            return param, video_links[0]  # Retourner le paramètre qui marche
                        
                except Exception as e:
                    print(f"  Erreur avec '{param}': {e}")
                    
    except Exception as e:
        print(f"Erreur page principale: {e}")
    
    print("\n=== Test URLs alternatives ===")
    
    # 2. Tester différentes URLs de recherche possibles
    search_urls = [
        "https://video.sibnet.ru/video/",
        "https://video.sibnet.ru/videos/",
        "https://video.sibnet.ru/browse/",
        "https://video.sibnet.ru/find/",
        "https://sibnet.ru/video/search/",
    ]
    
    for search_url in search_urls:
        try:
            resp = requests.get(search_url, params={"q": "ONE PIECE"}, headers=headers, timeout=10)
            print(f"{search_url} : {resp.status_code}")
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "lxml")
                video_count = len([a for a in soup.find_all("a", href=True) 
                                 if a.get("href") and "/video" in a.get("href")])
                if video_count > 0:
                    print(f"  ✅ {video_count} liens vidéo trouvés!")
                    
        except Exception as e:
            print(f"  Erreur: {e}")

if __name__ == "__main__":
    explore_sibnet_search()