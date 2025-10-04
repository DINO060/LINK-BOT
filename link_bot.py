# pip install playwright python-telegram-bot==21.6
# playwright install

import re
import difflib
import os
from typing import List, Dict
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Token de ton bot Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "8487001863:AAF5msQHveeFGXrNmxQWBcFWtGDyvgPvxWw")

def normalize_text(text: str) -> str:
    """Normalise le texte pour le matching fuzzy"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def calculate_similarity(keyword: str, title: str) -> float:
    """Calcule la similarité entre le mot-clé et le titre"""
    kw_norm = normalize_text(keyword)
    title_norm = normalize_text(title)
    
    if not kw_norm or not title_norm:
        return 0.0
    
    # Similarité de caractères
    char_sim = difflib.SequenceMatcher(None, kw_norm, title_norm).ratio()
    
    # Similarité de tokens (mots)
    kw_tokens = set(kw_norm.split())
    title_tokens = set(title_norm.split())
    
    if kw_tokens and title_tokens:
        token_sim = len(kw_tokens & title_tokens) / len(kw_tokens | title_tokens)
    else:
        token_sim = 0.0
    
    # Bonus si le titre commence par le mot-clé
    prefix_bonus = 0.1 if title_norm.startswith(kw_norm) else 0.0
    
    # Score final (pondéré)
    return 0.6 * char_sim + 0.3 * token_sim + prefix_bonus

async def extract_stream_links_from_page(page_url: str) -> List[str]:
    """
    Extrait les liens de streaming depuis une page de contenu
    """
    stream_links = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Capturer les requêtes réseau pour les fichiers vidéo
        captured_urls = []
        
        def handle_request(request):
            url = request.url
            # Chercher les fichiers vidéo/streaming
            if any(ext in url.lower() for ext in ['.mp4', '.m3u8', '.mpd', '.avi', '.mkv', '.webm']):
                if url not in captured_urls:
                    captured_urls.append(url)
        
        page.on("request", handle_request)
        
        try:
            # Headers pour éviter la détection de bot
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            await page.goto(page_url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)  # Attendre le JS au lieu de networkidle
            
            # Chercher et cliquer sur les boutons de lecture
            play_selectors = [
                ".play-button", ".vjs-big-play-button", "[aria-label*='play' i]",
                "button[title*='play' i]", ".btn-play", "#play", ".play-btn",
                "iframe", "[src*='player']", "[src*='embed']"
            ]
            
            for selector in play_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.click(selector, timeout=5000)
                        await page.wait_for_timeout(3000)
                        break
                except:
                    continue
            
            # Attendre que les requêtes vidéo se déclenchent
            await page.wait_for_timeout(5000)
            
            # Chercher des liens dans le DOM aussi
            video_elements = await page.locator("video[src], source[src], a[href*='.mp4'], a[href*='.m3u8']").all()
            for elem in video_elements:
                try:
                    src = await elem.get_attribute("src") or await elem.get_attribute("href")
                    if src and src not in captured_urls:
                        captured_urls.append(src)
                except:
                    continue
                    
        except Exception as e:
            print(f"Erreur extraction streaming: {e}")
        finally:
            await browser.close()
    
    return captured_urls

async def find_links_on_page(site_url: str, keyword: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Trouve les liens de fichiers les plus pertinents sur une page web
    """
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Configurer le navigateur pour éviter la détection
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
            })
            
            # Aller sur le site avec timeout plus long
            await page.goto(site_url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)  # Laisser le JS se charger
            
            # Stratégies de recherche multiples
            search_attempted = False
            
            # 1) Stratégie spéciale pour anime-sama.fr
            if "anime-sama" in site_url.lower():
                # Aller directement à la page de catalogue/recherche
                if "/catalogue/" not in site_url:
                    search_url = site_url.rstrip('/') + '/catalogue/'
                    await page.goto(search_url, timeout=60000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(3000)
                
                # Utiliser la barre de recherche d'anime-sama
                search_selectors = [
                    "#search-anime", 
                    "input[placeholder*='recherche' i]",
                    ".search-input",
                    "input[type='text']"
                ]
            else:
                # Sélecteurs génériques
                search_selectors = [
                    "input[type='search']",
                    "input[name*='search']", 
                    "input[placeholder*='search' i]",
                    "input[placeholder*='chercher' i]",
                    "#search",
                    ".search-input",
                    "[data-testid*='search']"
                ]
            
            for selector in search_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.fill(selector, keyword)
                        await page.keyboard.press("Enter")
                        await page.wait_for_timeout(3000)  # Attendre le chargement
                        search_attempted = True
                        break
                except:
                    continue
            
            # 2) Si pas de recherche, essayer les boutons/liens de navigation
            if not search_attempted:
                nav_selectors = [
                    f"a:has-text('{keyword}')",
                    f"[title*='{keyword}' i]",
                    f"[alt*='{keyword}' i]"
                ]
                
                for selector in nav_selectors:
                    try:
                        if await page.locator(selector).count() > 0:
                            await page.click(selector)
                            await page.wait_for_timeout(2000)
                            break
                    except:
                        continue
            
            # 3) Extraire tous les liens pertinents (spécialisé par site)
            if "anime-sama" in site_url.lower():
                link_selectors = [
                    ".anime a", ".anime-card a", ".episode-link a",
                    "a[href*='/catalogue/']", "a[href*='/episode/']",
                    ".card-anime a", ".episode a", "a[href]"
                ]
            else:
                link_selectors = [
                    "a[href]",
                    "[onclick*='http']",
                    ".link",
                    ".result a",
                    ".item a", 
                    ".video a",
                    ".movie a",
                    ".episode a"
                ]
            
            all_links = []
            
            for selector in link_selectors:
                try:
                    elements = await page.locator(selector).all()
                    for elem in elements[:50]:  # Limiter pour éviter trop de liens
                        try:
                            href = await elem.get_attribute("href")
                            title = (await elem.get_attribute("title") or 
                                   await elem.get_attribute("alt") or 
                                   await elem.inner_text() or "").strip()
                            
                            if href and title:
                                # Convertir en URL absolue si nécessaire
                                if href.startswith("/"):
                                    base_url = f"{urlparse(site_url).scheme}://{urlparse(site_url).netloc}"
                                    href = urljoin(base_url, href)
                                elif not href.startswith("http"):
                                    href = urljoin(site_url, href)
                                
                                all_links.append({"title": title, "url": href})
                        except:
                            continue
                except:
                    continue
            
            # 4) Scorer et trier les résultats des pages
            scored_links = []
            for link in all_links:
                score = calculate_similarity(keyword, link["title"])
                if score > 0.1:  # Seuil minimal de pertinence
                    scored_links.append({
                        "title": link["title"],
                        "url": link["url"],
                        "score": score
                    })
            
            # Trier par score décroissant
            scored_links.sort(key=lambda x: x["score"], reverse=True)
            
            # 5) Extraire les vrais liens de streaming depuis les meilleures pages
            top_pages = scored_links[:max_results * 2]  # Prendre plus de pages pour avoir plus de chances
            
            for page_info in top_pages:
                try:
                    print(f"🔍 Extraction streaming de: {page_info['title']}")
                    stream_urls = await extract_stream_links_from_page(page_info['url'])
                    
                    for stream_url in stream_urls:
                        results.append({
                            "title": page_info['title'],
                            "url": stream_url,
                            "score": page_info['score'],
                            "page_url": page_info['url']
                        })
                        
                        # Arrêter si on a assez de résultats
                        if len(results) >= max_results:
                            break
                    
                    if len(results) >= max_results:
                        break
                        
                except Exception as e:
                    print(f"Erreur extraction {page_info['url']}: {e}")
                    continue
            
            # Si pas de liens de streaming trouvés, retourner les pages originales
            if not results:
                results = [{
                    "title": link["title"],
                    "url": link["url"], 
                    "score": link["score"]
                } for link in scored_links[:max_results]]
            
        except Exception as e:
            print(f"Erreur lors du scraping de {site_url}: {e}")
            # En cas d'erreur, essayer une approche plus simple
            try:
                await page.goto(site_url, timeout=30000, wait_until="load")
                await page.wait_for_timeout(2000)
                
                # Extraire tous les liens visibles
                simple_links = await page.locator("a[href]").all()
                for elem in simple_links[:20]:
                    try:
                        href = await elem.get_attribute("href")
                        title = await elem.inner_text() or "Lien trouvé"
                        
                        if href and keyword.lower() in title.lower():
                            if href.startswith("/"):
                                base_url = f"{urlparse(site_url).scheme}://{urlparse(site_url).netloc}"
                                href = urljoin(base_url, href)
                            elif not href.startswith("http"):
                                href = urljoin(site_url, href)
                            
                            score = calculate_similarity(keyword, title)
                            if score > 0.1:
                                results.append({
                                    "title": title.strip(),
                                    "url": href,
                                    "score": score
                                })
                    except:
                        continue
                        
            except Exception as e2:
                print(f"Erreur fallback: {e2}")
        finally:
            await browser.close()
    
    return results

# === BOT TELEGRAM ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /start"""
    help_text = """
🤖 **Bot de recherche de liens**

**Usage:**
Envoie un message au format:
`find https://exemple.com mot-clé`

**Exemple:**
`find https://youtube.com christ`

Le bot va chercher les 3 meilleurs liens correspondant à ton mot-clé sur le site donné.
    """
    await update.message.reply_text(help_text)

async def handle_find_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Traite les commandes de recherche"""
    text = update.message.text.strip()
    
    # Parse le message: "find URL mot-clé"
    parts = text.split(maxsplit=2)
    
    if len(parts) < 3:
        await update.message.reply_text(
            "❌ Format incorrect!\n\n"
            "Usage: `find https://exemple.com mot-clé`\n"
            "Exemple: `find https://youtube.com christ`"
        )
        return
    
    _, site_url, keyword = parts
    
    # Vérifier que l'URL est valide
    if not site_url.startswith(("http://", "https://")):
        await update.message.reply_text("❌ L'URL doit commencer par http:// ou https://")
        return
    
    # Message de chargement
    loading_msg = await update.message.reply_text("🔍 Recherche en cours...")
    
    try:
        # Effectuer la recherche
        results = await find_links_on_page(site_url, keyword, max_results=3)
        
        if not results:
            await loading_msg.edit_text(f"❌ Aucun résultat trouvé pour '{keyword}' sur {site_url}")
            return
        
        # Formater la réponse avec distinction streaming/page
        response_lines = []
        streaming_found = False
        
        for i, result in enumerate(results, 1):
            url = result['url']
            # Détecter si c'est un lien de streaming direct
            is_streaming = any(ext in url.lower() for ext in ['.mp4', '.m3u8', '.mpd', '.avi', '.mkv', '.webm'])
            
            if is_streaming:
                response_lines.append(f"🎬 {url}")
                streaming_found = True
            else:
                response_lines.append(f"📄 {url}")
        
        header = "🎯 **Liens trouvés:**\n" if streaming_found else "📋 **Pages trouvées:**\n"
        response = header + "\n".join(response_lines)
        
        if streaming_found:
            response += "\n\n🎬 = Lien direct de streaming\n📄 = Page de contenu"
        
        await loading_msg.edit_text(response)
        
    except Exception as e:
        await loading_msg.edit_text(f"❌ Erreur: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Traite tous les messages qui ne sont pas des commandes"""
    text = update.message.text.strip()
    
    if text.lower().startswith("find "):
        await handle_find_command(update, context)
    else:
        await update.message.reply_text(
            "💡 Utilise le format: `find https://exemple.com mot-clé`\n"
            "Ou tape /start pour plus d'infos"
        )

def main():
    """Fonction principale"""
    if not BOT_TOKEN or BOT_TOKEN == "TON_TOKEN_ICI":
        print("❌ Erreur: Configure ton BOT_TOKEN!")
        print("Crée une variable d'environnement BOT_TOKEN ou modifie le code.")
        return
    
    # Créer l'application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Ajouter les handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot démarré! Envoie 'find URL mot-clé' pour commencer.")
    
    # Lancer le bot
    app.run_polling()

if __name__ == "__main__":
    main()