# -*- coding: utf-8 -*-
from typing import Optional
from .sibnet_simple import get_sibnet_share_link, normalize_sibnet_url

# Optionnel: importe ton extractor Anime-Sama si tu l'as gardé
try:
    from .precise_playwright_adapter import precise_site_search
except Exception:
    precise_site_search = None  # fallback non dispo

import asyncio

async def resolve_media_link(
    site_or_url: str,
    keyword: str,
    episode: Optional[int] = None,
):
    """
    Stratégie intelligente mise à jour:
      A) si c'est explicitement "sibnet" -> utiliser Sibnet uniquement
      B) si site_or_url OU keyword contiennent un lien Sibnet -> normaliser et renvoyer
      C) si c'est un autre site -> utiliser ce site directement
      D) sinon (pas de site spécifié) -> tenter Sibnet puis fallback site générique
    Retourne: dict { source, link, page, title }
    """
    
    # A) Utilisateur demande explicitement Sibnet
    if site_or_url.lower() == "sibnet":
        print(f"[DEBUG] Recherche Sibnet explicite pour: {keyword}")
        sib = get_sibnet_share_link(keyword)
        print(f"[DEBUG] Résultat Sibnet: {sib}")
        if sib:
            return {
                "source": "sibnet-search", 
                "link": sib, 
                "page": "https://video.sibnet.ru/",
                "title": f"Trouvé sur Sibnet: {keyword}"
            }
        else:
            return {
                "source": "sibnet-failed",
                "link": "",
                "page": "",
                "title": "Recherche Sibnet impossible (captcha anti-bot)"
            }
    
    # B) URL Sibnet détectée automatiquement ?
    sib = None
    if site_or_url.startswith("http") and "sibnet" in site_or_url.lower():
        sib = normalize_sibnet_url(site_or_url)
    if not sib and keyword.startswith("http") and "sibnet" in keyword.lower():
        sib = normalize_sibnet_url(keyword)
    if sib:
        return {
            "source": "sibnet-direct", 
            "link": sib, 
            "page": site_or_url,
            "title": f"Lien Sibnet normalisé"
        }

    # C) Site spécifique demandé (pas Sibnet) - utiliser precise_playwright_adapter
    if precise_site_search and site_or_url and site_or_url.lower() != "sibnet":
        print(f"[DEBUG] Recherche sur site spécifique: {site_or_url}")
        # Aller directement au site demandé sans passer par Sibnet
        try:
            results = await precise_site_search(site_or_url, keyword, top_k=1)
            if results:
                best = results[0]
                return {
                    "source": "site-search", 
                    "link": best["url"], 
                    "page": best["url"],
                    "title": best["title"],
                    "score": best.get("score", 0)
                }
        except Exception as e:
            print(f"Erreur fallback site-search: {e}")

    # D) Pas de site spécifique - essayer Sibnet puis fallback générique
    if not site_or_url or site_or_url.lower() == "general":
        print(f"[DEBUG] Recherche générale, tentative Sibnet pour: {keyword}")
        sib = get_sibnet_share_link(keyword)
        print(f"[DEBUG] Résultat Sibnet: {sib}")
        if sib:
            return {
                "source": "sibnet-search", 
                "link": sib, 
                "page": "https://video.sibnet.ru/",
                "title": f"Trouvé sur Sibnet: {keyword}"
            }
    
    # Rien trouvé
    return {"source": "none", "link": "", "page": "", "title": ""}