import requests
from bs4 import BeautifulSoup

def analyze_sibnet_html():
    """Analyser le HTML de Sibnet pour comprendre la structure"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    # Faire une recherche
    resp = requests.get('https://video.sibnet.ru/search.php', 
                       params={'text': 'видео', 'inname': '1', 'intext': '1', 'inkeyw': '1'},
                       headers=headers)
    
    print(f"Status: {resp.status_code}, Taille: {len(resp.text)}")
    
    # Sauvegarder le HTML complet
    with open('sibnet_full_search.html', 'w', encoding='utf-8') as f:
        f.write(resp.text)
    
    # Analyser avec BeautifulSoup
    soup = BeautifulSoup(resp.text, 'lxml')
    
    # Tous les liens
    all_links = soup.find_all('a', href=True)
    print(f'Total liens: {len(all_links)}')
    
    # Liens contenant "video"
    video_links = []
    for a in all_links:
        href = a.get('href')
        text = a.get_text().strip()
        if href and 'video' in href:
            video_links.append((href, text))
    
    print(f'Liens avec "video": {len(video_links)}')
    for i, (link, text) in enumerate(video_links[:10]):
        print(f'{i+1:2d}. {link} -> {text[:50]}...')
    
    print("\n" + "="*60)
    
    # Chercher des patterns spécifiques
    patterns = [
        r'/video\d+',
        r'video\d+',
        r'\.ru/video',
        r'sibnet.*video'
    ]
    
    for pattern in patterns:
        import re
        matches = []
        for a in all_links:
            href = a.get('href', '')
            if re.search(pattern, href):
                matches.append(href)
        print(f'Pattern "{pattern}": {len(matches)} matches')
        for m in matches[:3]:
            print(f'  - {m}')
    
    print("\n" + "="*60)
    
    # Analyser la structure de la page
    # Chercher des éléments qui pourraient contenir des vidéos
    possible_containers = [
        'div[class*="video"]',
        'div[class*="item"]', 
        'div[class*="result"]',
        'tr',
        'td',
        '.video',
        '.item',
        '.result'
    ]
    
    for container in possible_containers:
        elements = soup.select(container)
        if elements:
            print(f'Conteneur "{container}": {len(elements)} éléments')
            
            # Examiner le premier élément
            first = elements[0]
            links_in_first = first.find_all('a', href=True)
            print(f'  Premier élément a {len(links_in_first)} liens')
            
            for link in links_in_first[:3]:
                href = link.get('href', '')
                text = link.get_text().strip()[:30]
                print(f'    -> {href} ({text})')

if __name__ == "__main__":
    analyze_sibnet_html()