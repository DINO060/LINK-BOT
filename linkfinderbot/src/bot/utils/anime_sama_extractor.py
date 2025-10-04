# -*- coding: utf-8 -*-
import re
import urllib.parse
from typing import Optional, Dict
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests

def _normalize_site(site_or_url: str) -> str:
    """Normalise l'URL du site"""
    if site_or_url.startswith("http"):
        return site_or_url
    return f"https://{site_or_url.strip('/')}"

def _is_sibnet(iframe_url: str) -> bool:
    """Vérifie si l'URL est un iframe Sibnet"""
    return iframe_url and "sibnet" in iframe_url.lower()

def _to_sibnet_share(iframe_url: str) -> str:
    """Convertit une iframe Sibnet en lien de partage"""
    if not _is_sibnet(iframe_url):
        return iframe_url
    
    # shell.php?videoid=123 → https://video.sibnet.ru/video123
    m = re.search(r"(?:shell|frame)\.php\?videoid=(\d+)", iframe_url, flags=re.I)
    if m:
        return f"https://video.sibnet.ru/video{m.group(1)}"
    
    # Déjà un lien video.sibnet.ru
    if "video.sibnet.ru" in iframe_url:
        return iframe_url
    
    return iframe_url

def ddg_first_result_site(domain: str, keyword: str) -> Optional[str]:
    """Fallback DuckDuckGo pour trouver la page de l'anime"""
    from .fast_jump import ddg_first_site
    return ddg_first_site(domain, keyword)

async def _type_search_or_fallback(page, start_url: str, keyword: str, timeout_ms: int) -> bool:
    """Effectue une recherche sur le site"""
    try:
        # Chercher un champ de recherche
        search_input = page.locator("input[type='search'], input[name*='search'], input[name*='q'], #search")
        
        if await search_input.count() > 0:
            print(f"🔍 Recherche interne: {keyword}")
            await search_input.first.fill(keyword)
            await search_input.first.press("Enter")
            await page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            return True
        else:
            print("⚠️ Pas de champ de recherche trouvé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur recherche interne: {e}")
        return False

async def _pick_first_result(page, timeout_ms: int) -> Optional[str]:
    """Sélectionne le premier résultat de recherche"""
    try:
        # Sélecteurs communs pour les résultats de recherche
        selectors = [
            "a[href*='catalogue']",  # anime-sama.fr spécifique
            ".search-result a", 
            ".result a",
            "article a",
            ".post a",
            ".entry a"
        ]
        
        for selector in selectors:
            links = page.locator(selector)
            if await links.count() > 0:
                first_link = await links.first.get_attribute("href")
                if first_link:
                    # Convertir en URL absolue si nécessaire
                    if first_link.startswith("/"):
                        base_url = urllib.parse.urljoin(page.url, "/")
                        first_link = urllib.parse.urljoin(base_url, first_link)
                    print(f"✅ Premier résultat: {first_link}")
                    return first_link
        
        print("❌ Aucun résultat trouvé")
        return None
        
    except Exception as e:
        print(f"❌ Erreur sélection résultat: {e}")
        return None

async def _episode_dropdown_locators(page):
    """Trouve les sélecteurs d'épisodes et de lecteurs"""
    try:
        # Sélecteurs typiques pour anime-sama.fr
        ep_selectors = [
            "select[name*='episode']",
            "#episode-select", 
            ".episode-select",
            "select option[value*='episode']"
        ]
        
        lecteur_selectors = [
            "select[name*='player']",
            "#player-select",
            ".player-select", 
            "select option[value*='lecteur']"
        ]
        
        ep_sel = None
        for selector in ep_selectors:
            if await page.locator(selector).count() > 0:
                ep_sel = selector
                break
        
        lecteur_sel = None
        for selector in lecteur_selectors:
            if await page.locator(selector).count() > 0:
                lecteur_sel = selector
                break
        
        print(f"📺 Episode selector: {ep_sel}")
        print(f"🎬 Player selector: {lecteur_sel}")
        
        return ep_sel, lecteur_sel
        
    except Exception as e:
        print(f"❌ Erreur localisation dropdowns: {e}")
        return None, None

async def _select_episode(page, ep_selector: Optional[str], episode: Optional[int]) -> str:
    """Sélectionne un épisode spécifique"""
    if not ep_selector or not episode:
        return "(aucun épisode sélectionné)"
    
    try:
        # Chercher l'option avec le numéro d'épisode
        options = page.locator(f"{ep_selector} option")
        count = await options.count()
        
        for i in range(count):
            option = options.nth(i)
            text = await option.text_content()
            value = await option.get_attribute("value")
            
            # Chercher le numéro d'épisode dans le texte ou la valeur
            if str(episode) in text or str(episode) in (value or ""):
                await option.click()
                await page.wait_for_timeout(1000)  # Attendre le chargement
                print(f"✅ Épisode sélectionné: {text}")
                return text.strip()
        
        print(f"⚠️ Épisode {episode} non trouvé")
        return f"(épisode {episode} non trouvé)"
        
    except Exception as e:
        print(f"❌ Erreur sélection épisode: {e}")
        return "(erreur sélection épisode)"

async def _try_each_player_until_sibnet(page, lecteur_selector: Optional[str]):
    """Teste chaque lecteur jusqu'à trouver Sibnet"""
    if not lecteur_selector:
        # Pas de sélecteur de lecteur, chercher directement les iframes
        return await _extract_iframe_from_page(page)
    
    try:
        options = page.locator(f"{lecteur_selector} option")
        count = await options.count()
        
        for i in range(count):
            option = options.nth(i)
            text = await option.text_content()
            
            # Sélectionner ce lecteur
            await option.click()
            await page.wait_for_timeout(2000)  # Attendre le chargement
            
            # Extraire l'iframe
            iframe_url = await _extract_iframe_from_page(page)
            
            if _is_sibnet(iframe_url):
                print(f"🎯 Sibnet trouvé avec lecteur: {text}")
                return text.strip(), iframe_url
        
        # Si aucun Sibnet trouvé, retourner le premier lecteur
        if count > 0:
            first_option = options.first
            await first_option.click()
            await page.wait_for_timeout(2000)
            iframe_url = await _extract_iframe_from_page(page)
            text = await first_option.text_content()
            print(f"⚠️ Sibnet non trouvé, utilisation du premier lecteur: {text}")
            return text.strip(), iframe_url
        
        return "(aucun lecteur)", ""
        
    except Exception as e:
        print(f"❌ Erreur test lecteurs: {e}")
        return "(erreur lecteurs)", ""

async def _extract_iframe_from_page(page) -> str:
    """Extrait l'URL de l'iframe principal"""
    try:
        # Chercher les iframes
        iframes = page.locator("iframe")
        count = await iframes.count()
        
        for i in range(count):
            iframe = iframes.nth(i)
            src = await iframe.get_attribute("src")
            
            if src and ("sibnet" in src.lower() or "video" in src.lower()):
                print(f"📹 Iframe trouvée: {src}")
                return src
        
        # Si pas d'iframe spécifique, prendre la première
        if count > 0:
            first_src = await iframes.first.get_attribute("src")
            if first_src:
                print(f"📹 Première iframe: {first_src}")
                return first_src
        
        print("❌ Aucune iframe trouvée")
        return ""
        
    except Exception as e:
        print(f"❌ Erreur extraction iframe: {e}")
        return ""

async def extract_anime_sama(
    site_or_url: str,
    keyword: str,
    *,
    episode: Optional[int] = None,
    headless: bool = True,
    timeout_ms: int = 15000,
    use_ddg_backup: bool = True,
    direct_url: Optional[str] = None,  # NEW: passer une URL directe si on l'a
) -> Dict:
    """
    Extrait les informations d'un anime depuis anime-sama.fr
    
    Args:
        site_or_url: URL du site ou nom de domaine
        keyword: Mot-clé de recherche
        episode: Numéro d'épisode à sélectionner
        headless: Mode navigateur invisible
        timeout_ms: Timeout en millisecondes
        use_ddg_backup: Utiliser DuckDuckGo en fallback
        direct_url: URL directe vers la page de l'anime (skip recherche)
    
    Returns:
        Dict avec les résultats de l'extraction
    """
    start = _normalize_site(site_or_url)
    domain = urllib.parse.urlsplit(start).netloc

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            locale="fr-FR",
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"),
            viewport={"width": 1366, "height": 768},
            ignore_https_errors=True,
        )
        page = await context.new_page()

        # 0) NEW: si on nous donne déjà l'URL de la fiche → on saute la recherche
        if direct_url:
            first = direct_url
            print(f"🎯 URL directe fournie: {direct_url}")
        else:
            # 1) home
            print(f"🏠 Accès à la page d'accueil: {start}")
            await page.goto(start, wait_until="domcontentloaded", timeout=timeout_ms)
            
            # 2) search interne
            used_internal = await _type_search_or_fallback(page, start, keyword, timeout_ms)
            first = await _pick_first_result(page, timeout_ms)
            
            # 2bis) fallback DDG site:
            if not first and use_ddg_backup:
                print("🔄 Fallback DuckDuckGo...")
                ext = ddg_first_result_site(domain, keyword)
                if ext:
                    first = ext
            
            if not first:
                await context.close()
                await browser.close()
                return {"matched": False, "why": "Aucun résultat", "page_url": page.url}

        # 3) ouvrir la page série / saison (directe ou trouvée)
        print(f"📖 Ouverture de la page: {first}")
        await page.goto(first, wait_until="domcontentloaded", timeout=timeout_ms)

        # 4) EPISODE + LECTEUR
        ep_sel, lecteur_sel = await _episode_dropdown_locators(page)
        chosen_episode_label = await _select_episode(page, ep_sel, episode)
        lecteur_label, raw_iframe = await _try_each_player_until_sibnet(page, lecteur_sel)

        # 5) build final link
        if _is_sibnet(raw_iframe):
            final_url = _to_sibnet_share(raw_iframe)
            why = "sibnet détecté → lien partage normalisé"
            matched = True
        else:
            final_url = raw_iframe or ""
            why = "sibnet absent → lien du 1er lecteur"
            matched = bool(final_url)

        title = await page.title()
        await context.close()
        await browser.close()

        return {
            "matched": matched,
            "page_url": first,
            "titre": title or "",
            "episode_selected": chosen_episode_label,
            "lecteur_label": lecteur_label,
            "raw_iframe": raw_iframe,
            "final_url": final_url,
            "why": why + ("" if direct_url else " (recherche)"),
        }