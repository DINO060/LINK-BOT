# -*- coding: utf-8 -*-
import asyncio
import re
import urllib.parse
from collections import deque

from rapidfuzz import fuzz
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

STOP_PARAMS = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid"}

BAD_PATH_HINTS = {
    "login","signin","register","signup","privacy","cookie","terms","conditions",
    "help","aide","support","profil","profile","account","settings","rss","feed"
}

def normalize_url(url: str) -> str:
    try:
        u = urllib.parse.urlsplit(url)
        if u.scheme not in ("http", "https"):
            return ""
        q = urllib.parse.parse_qsl(u.query, keep_blank_values=True)
        q = [(k,v) for (k,v) in q if k not in STOP_PARAMS]
        new_query = urllib.parse.urlencode(q, doseq=True)
        cleaned = urllib.parse.urlunsplit((u.scheme, u.netloc.lower(), u.path.rstrip("/"), new_query, ""))
        return cleaned
    except Exception:
        return url.strip().rstrip("/")

def same_domain(url: str, base_domain: str) -> bool:
    try:
        return urllib.parse.urlsplit(url).netloc.lower().endswith(base_domain.lower())
    except Exception:
        return False

def word_boundary_present(text: str, phrase: str) -> bool:
    pattern = r"\b" + re.escape(phrase) + r"\b"
    return re.search(pattern, text or "", flags=re.IGNORECASE) is not None

def relevance_score(title: str, snippet: str, url: str, query: str) -> float:
    t = title or ""
    s = snippet or ""
    u = url or ""
    t_score = fuzz.token_set_ratio(t, query)
    s_score = fuzz.token_set_ratio(s, query) if s else 0
    u_score = fuzz.partial_ratio(u, query)
    bonus = 0
    if word_boundary_present(t, query): bonus += 8
    if s and word_boundary_present(s, query): bonus += 4
    return round(0.6*t_score + 0.3*s_score + 0.1*u_score + bonus, 2)

def is_strong_candidate(title: str, snippet: str, query: str) -> bool:
    if not (word_boundary_present(title, query) or word_boundary_present(snippet, query)):
        return False
    if fuzz.token_set_ratio(title or "", query) < 85:
        return False
    if snippet and fuzz.token_set_ratio(snippet, query) < 70:
        return False
    return True

def dedupe(results):
    kept = []
    seen_urls = set()
    for r in results:
        key = normalize_url(r["url"])
        if not key or key in seen_urls:
            continue
        is_dup = False
        for k in kept:
            if fuzz.token_set_ratio(k["title"], r["title"]) >= 95:
                is_dup = True
                break
        if is_dup:
            continue
        seen_urls.add(key)
        kept.append(r)
    return kept

def looks_bad_path(url: str) -> bool:
    low = url.lower()
    return any(b in low for b in BAD_PATH_HINTS)

async def extract_page_info(page):
    title = (await page.title()) or ""
    h1 = ""
    try:
        h1_el = page.locator("h1")
        if await h1_el.count() > 0:
            h1 = (await h1_el.first.text_content()) or ""
    except Exception:
        pass

    desc = ""
    try:
        desc = await page.locator("meta[name='description']").get_attribute("content") or ""
    except Exception:
        try:
            html = await page.content()
            soup = BeautifulSoup(html, "lxml")
            if soup.find("meta", attrs={"name":"description"}):
                desc = soup.find("meta", attrs={"name":"description"}).get("content", "")
            elif soup.find("p"):
                desc = soup.find("p").get_text(" ", strip=True)[:300]
        except Exception:
            desc = ""
    return title.strip(), h1.strip(), desc.strip()

def page_is_relevant(title: str, h1: str, url: str, query: str) -> bool:
    t = f"{title or ''} {h1 or ''}"
    if not re.search(r"\b" + re.escape(query) + r"\b", t, flags=re.I):
        return False
    if fuzz.token_set_ratio(t, query) < 85:
        return False
    if looks_bad_path(url):
        return False
    return True

def build_entrypoints(base: str, query: str):
    u = urllib.parse.urlsplit(base)
    base_root = f"{u.scheme}://{u.netloc}"
    q = urllib.parse.quote_plus(query)
    candidates = {
        base_root,
        f"{base_root}/?s={q}",
        f"{base_root}/search?q={q}",
        f"{base_root}/recherche?q={q}",
        f"{base_root}/search/{q}",
    }
    return [normalize_url(x) for x in candidates]

async def crawl_site(base: str, query: str, max_pages: int = 40, max_depth: int = 2, timeout_ms: int = 15000):
    base = normalize_url(base)
    if not base:
        raise ValueError("Base URL invalide.")

    base_domain = urllib.parse.urlsplit(base).netloc
    queue = deque([(url, 0) for url in build_entrypoints(base, query)])
    seen = set()
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        while queue and len(seen) < max_pages:
            url, depth = queue.popleft()
            if not url or url in seen:
                continue
            seen.add(url)
            if not same_domain(url, base_domain):
                continue

            try:
                resp = await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                if not resp or (resp.status < 200 or resp.status >= 400):
                    continue
            except Exception:
                continue

            try:
                anchors = await page.locator("a[href]").all()
                hrefs = set()
                for a in anchors:
                    try:
                        href = await a.get_attribute("href")
                        if not href:
                            continue
                        abs_url = urllib.parse.urljoin(url, href)
                        abs_url = normalize_url(abs_url)
                        if abs_url:
                            hrefs.add(abs_url)
                    except Exception:
                        pass
            except Exception:
                hrefs = set()

            try:
                title, h1, desc = await extract_page_info(page)
            except Exception:
                title, h1, desc = "", "", ""

            if page_is_relevant(title, h1, url, query):
                score = relevance_score(title, desc, url, query)
                results.append({
                    "title": title or h1 or url,
                    "url": url,
                    "snippet": desc,
                    "score": score
                })

            if depth < max_depth:
                for link in hrefs:
                    if link not in seen and same_domain(link, base_domain) and not looks_bad_path(link):
                        queue.append((link, depth + 1))

        await context.close()
        await browser.close()

    results.sort(key=lambda x: x["score"], reverse=True)
    results = dedupe(results)
    return results[:10]

async def precise_site_search(site_or_url: str, query: str, top_k: int = 3):
    site = site_or_url
    if not site.startswith("http"):
        site = "https://" + site.strip("/")
    results = await crawl_site(site, query, max_pages=60, max_depth=2)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]