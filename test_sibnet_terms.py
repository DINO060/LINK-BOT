#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re

def test_sibnet_various_terms():
    """Tester différents termes de recherche sur Sibnet"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    # Différents termes à tester
    search_terms = [
        "anime",
        "мультфильм",  # anime en russe
        "видео",       # vidéo en russe
        "фильм",       # film en russe
        "НАРУТО",      # Naruto en cyrillique
        "Dragon Ball",
        "мультик"      # dessin animé
    ]
    
    print("🔍 TEST DIFFÉRENTS TERMES SIBNET")
    print("=" * 50)
    
    for term in search_terms:
        print(f"\n📝 Recherche: '{term}'")
        
        try:
            # Utiliser le formulaire /search.php avec les bons paramètres
            search_params = {
                "text": term,
                "inname": "1",
                "intext": "1", 
                "inkeyw": "1",
                "inalbom": "0"
            }
            
            resp = requests.get("https://video.sibnet.ru/search.php", 
                              params=search_params, headers=headers, timeout=15)
            
            print(f"  Status: {resp.status_code}, Taille: {len(resp.text)} chars")
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "lxml")
                
                # Chercher le terme dans les résultats
                page_text = soup.get_text().lower()
                if term.lower() in page_text:
                    print(f"  ✅ '{term}' trouvé dans les résultats")
                    
                    # Compter les liens vidéo
                    video_links = []
                    for a in soup.find_all("a", href=True):
                        href = a.get("href")
                        if href and re.search(r"/video\d+", href):
                            video_links.append(href)
                    
                    print(f"  📹 Liens vidéo: {len(video_links)}")
                    
                    # Afficher les premiers liens
                    for i, link in enumerate(video_links[:3]):
                        if link.startswith("/"):
                            full_link = f"https://video.sibnet.ru{link}"
                        else:
                            full_link = link
                        print(f"    {i+1}. {full_link}")
                        
                    # Si c'est le premier terme qui marche, sauvegarder
                    if video_links and term == search_terms[0]:
                        with open(f"sibnet_results_{term}.html", "w", encoding="utf-8") as f:
                            f.write(resp.text)
                        print(f"  📄 Résultats sauvegardés")
                        
                else:
                    print(f"  ❌ '{term}' PAS trouvé dans les résultats")
                    
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
    
    # Test spécial: regarder la structure de la page de résultats
    print(f"\n🔬 ANALYSE STRUCTURE PAGE RÉSULTATS")
    try:
        resp = requests.get("https://video.sibnet.ru/search.php", 
                          params={"text": "anime", "inname": "1", "intext": "1", "inkeyw": "1"}, 
                          headers=headers, timeout=15)
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "lxml")
            
            # Chercher différents types de conteneurs
            containers = [
                (".result", "result"),
                (".video", "video"), 
                (".item", "item"),
                ("tr", "table row"),
                ("div[class*='video']", "video div"),
                ("td", "table cell")
            ]
            
            for selector, name in containers:
                elements = soup.select(selector)
                if elements:
                    print(f"  📦 {name}: {len(elements)} éléments")
                    
                    # Examiner le premier élément
                    first = elements[0]
                    links = first.find_all("a", href=True)
                    video_links_in_first = [a.get("href") for a in links if a.get("href") and "/video" in a.get("href")]
                    
                    if video_links_in_first:
                        print(f"     Premier élément contient {len(video_links_in_first)} lien(s) vidéo")
                        print(f"     Exemple: {video_links_in_first[0]}")
                        
    except Exception as e:
        print(f"❌ Erreur analyse structure: {e}")

if __name__ == "__main__":
    test_sibnet_various_terms()