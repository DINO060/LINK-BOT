import sys
import os
import requests
from bs4 import BeautifulSoup

def test_sibnet_simple():
    """Test direct de la recherche Sibnet sans imports complexes"""
    query = "ONE PIECE episode 1089"
    print(f"Test recherche Sibnet: {query}")
    
    # Test 1: Recherche interne Sibnet
    base = "https://video.sibnet.ru/search/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    try:
        print("Tentative de connexion à Sibnet...")
        response = requests.get(base, params={"q": query}, headers=headers, timeout=15)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            print("Analyse du HTML...")
            
            # Chercher tous les liens vidéo
            all_links = soup.find_all("a", href=True)
            video_links = []
            
            for link in all_links:
                href = link.get("href", "")
                if "/video" in href and any(char.isdigit() for char in href):
                    video_links.append(href)
            
            print(f"Trouvé {len(video_links)} liens vidéo potentiels:")
            for i, link in enumerate(video_links[:5]):  # Afficher les 5 premiers
                if link.startswith("/"):
                    full_link = f"https://video.sibnet.ru{link}"
                else:
                    full_link = link
                print(f"{i+1}. {full_link}")
                
                # Si c'est le premier lien complet, le retourner
                if i == 0:
                    return full_link
                    
        else:
            print(f"Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"Erreur: {e}")
    
    # Test 2: Fallback DuckDuckGo
    print("\nTentative DuckDuckGo fallback...")
    try:
        ddg_query = f'site:video.sibnet.ru "{query}"'
        ddg_response = requests.get("https://duckduckgo.com/html/", params={"q": ddg_query}, headers=headers, timeout=15)
        
        if ddg_response.status_code == 200:
            soup = BeautifulSoup(ddg_response.text, "lxml")
            results = soup.find_all("a", class_="result__a")
            
            print(f"DDG trouvé {len(results)} résultats")
            for result in results[:3]:
                href = result.get("href", "")
                if "sibnet.ru" in href and "/video" in href:
                    print(f"DDG: {href}")
                    return href
        else:
            print(f"DDG erreur: {ddg_response.status_code}")
            
    except Exception as e:
        print(f"DDG erreur: {e}")
    
    return None

if __name__ == "__main__":
    result = test_sibnet_simple()
    print(f"\nRésultat final: {result}")