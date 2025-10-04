#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re

def debug_sibnet_search():
    """Debug détaillé de la recherche Sibnet"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    query = "ONE PIECE"
    
    print("🔬 ANALYSE DÉTAILLÉE SIBNET")
    print("=" * 60)
    
    # Test 1: Page normale vs page avec paramètre q
    print("📋 Comparaison page normale vs recherche")
    
    try:
        # Page normale
        resp_normal = requests.get("https://video.sibnet.ru/", headers=headers, timeout=15)
        print(f"Page normale: {resp_normal.status_code} - {len(resp_normal.text)} chars")
        
        # Page avec paramètre q
        resp_search = requests.get("https://video.sibnet.ru/", params={"q": query}, headers=headers, timeout=15)
        print(f"Page recherche: {resp_search.status_code} - {len(resp_search.text)} chars")
        
        # Comparer les contenus
        if resp_normal.text == resp_search.text:
            print("⚠️  PROBLÈME: Les pages sont identiques! Le paramètre 'q' est ignoré")
        else:
            print("✅ Les pages sont différentes - la recherche fonctionne")
            
        # Analyser les URLs dans le HTML de recherche
        soup = BeautifulSoup(resp_search.text, "lxml")
        
        # Chercher le terme "ONE PIECE" dans la page
        page_text = soup.get_text().lower()
        if "one piece" in page_text:
            print("✅ 'ONE PIECE' trouvé dans le contenu de la page")
        else:
            print("❌ 'ONE PIECE' PAS trouvé dans le contenu")
            
        # Examiner la structure de recherche
        print("\n🔍 Analyse formulaires de recherche")
        forms = soup.find_all("form")
        for i, form in enumerate(forms):
            action = form.get("action", "")
            if "search" in action.lower():
                print(f"  Formulaire {i+1}: {action}")
                inputs = form.find_all("input")
                for inp in inputs:
                    name = inp.get("name", "")
                    if name and name not in ["panel", "iehack"]:
                        print(f"    Input: {name} = {inp.get('value', '')}")
                        
        # Test du vrai formulaire de recherche
        print("\n🎯 Test formulaire /search.php")
        search_params = {
            "text": query,
            "panel": "",
            "inname": "",
            "intext": "1", # Recherche dans le texte
            "inkeyw": "",
            "inalbom": ""
        }
        
        resp_form = requests.get("https://video.sibnet.ru/search.php", 
                                params=search_params, headers=headers, timeout=15)
        print(f"Formulaire search.php: {resp_form.status_code} - {len(resp_form.text)} chars")
        
        if resp_form.status_code == 200:
            soup_form = BeautifulSoup(resp_form.text, "lxml")
            
            # Chercher "ONE PIECE" dans les résultats
            form_text = soup_form.get_text().lower()
            if "one piece" in form_text:
                print("✅ 'ONE PIECE' trouvé dans les résultats de recherche!")
                
                # Extraire les liens vidéo
                video_links = []
                for a in soup_form.find_all("a", href=True):
                    href = a.get("href")
                    if href and re.search(r"/video\d+", href):
                        # Priorité aux liens avec "piece" dans le titre
                        title_text = a.get_text().lower()
                        if "piece" in title_text or "piece" in href.lower():
                            video_links.insert(0, href)
                        else:
                            video_links.append(href)
                
                print(f"🎬 Liens vidéo trouvés: {len(video_links)}")
                for j, link in enumerate(video_links[:5]):
                    if link.startswith("/"):
                        full_link = f"https://video.sibnet.ru{link}"
                    else:
                        full_link = link
                    print(f"  {j+1}. {full_link}")
                    
                # Sauvegarder les résultats
                with open("sibnet_search_results.html", "w", encoding="utf-8") as f:
                    f.write(resp_form.text)
                print("📄 Résultats sauvegardés dans sibnet_search_results.html")
                
                if video_links:
                    best_link = video_links[0]
                    if best_link.startswith("/"):
                        best_link = f"https://video.sibnet.ru{best_link}"
                    print(f"\n🏆 MEILLEUR RÉSULTAT: {best_link}")
                    return best_link
                    
            else:
                print("❌ 'ONE PIECE' PAS trouvé dans les résultats de recherche")
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        
    return None

if __name__ == "__main__":
    result = debug_sibnet_search()
    print(f"\n🎯 RÉSULTAT FINAL: {result}")