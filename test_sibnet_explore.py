import requests
from bs4 import BeautifulSoup

def test_sibnet_urls():
    """Tester différentes URLs Sibnet pour voir laquelle fonctionne"""
    
    urls_test = [
        "https://video.sibnet.ru/",
        "https://video.sibnet.ru/search/",
        "https://sibnet.ru/",
        "https://sibnet.ru/search/",
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    query = "ONE PIECE episode 1089"
    
    for i, url in enumerate(urls_test):
        print(f"\n--- Test {i+1}: {url} ---")
        
        try:
            # Test de base
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ URL accessible - {len(response.text)} caractères")
                
                # Sauvegarder le HTML principal
                with open(f"sibnet_main_{i}.html", "w", encoding="utf-8") as f:
                    f.write(response.text[:5000])  # Premiers 5000 caractères
                
                # Si c'est une URL de recherche, tester avec query
                if "search" in url:
                    try:
                        search_response = requests.get(url, params={"q": query}, headers=headers, timeout=10)
                        print(f"Recherche avec query: {search_response.status_code}")
                        
                        if search_response.status_code == 200:
                            print(f"✅ Recherche OK - {len(search_response.text)} caractères")
                            
                            # Sauvegarder résultat de recherche
                            with open(f"sibnet_search_{i}.html", "w", encoding="utf-8") as f:
                                f.write(search_response.text[:10000])  # Premiers 10000 caractères
                                
                            # Analyser rapidement
                            soup = BeautifulSoup(search_response.text, "lxml")
                            video_links = []
                            
                            for a in soup.find_all("a", href=True):
                                href = a.get("href")
                                if href and "/video" in href and any(c.isdigit() for c in href):
                                    video_links.append(href)
                            
                            print(f"Liens vidéo trouvés: {len(video_links)}")
                            for j, link in enumerate(video_links[:3]):
                                print(f"  {j+1}. {link}")
                                
                        else:
                            print(f"❌ Recherche échouée: {search_response.status_code}")
                    
                    except Exception as e:
                        print(f"❌ Erreur recherche: {e}")
                
            else:
                print(f"❌ URL non accessible: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_sibnet_urls()