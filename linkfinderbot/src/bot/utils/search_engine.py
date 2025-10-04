from rapidfuzz import fuzz
import re
import urllib.parse
import requests

STOP_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid"}

def normalize_url(url: str) -> str:
    try:
        u = urllib.parse.urlsplit(url)
        q = urllib.parse.parse_qsl(u.query, keep_blank_values=True)
        q = [(k, v) for (k, v) in q if k not in STOP_PARAMS]
        new_query = urllib.parse.urlencode(q, doseq=True)
        cleaned = urllib.parse.urlunsplit((u.scheme, u.netloc, u.path.rstrip("/"), new_query, ""))
        return cleaned.lower()
    except Exception:
        return url.lower().rstrip("/")

def word_boundary_present(text: str, phrase: str) -> bool:
    pattern = r"\b" + re.escape(phrase) + r"\b"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None

def relevance_score(title: str, snippet: str, url: str, query: str) -> float:
    t = title or ""
    s = snippet or ""
    u = url or ""
    t_score = fuzz.token_set_ratio(t, query)
    s_score = fuzz.token_set_ratio(s, query)
    u_score = fuzz.partial_ratio(u, query)
    bonus = 0
    if word_boundary_present(t, query): bonus += 8
    if word_boundary_present(s, query): bonus += 4
    return round(0.6 * t_score + 0.3 * s_score + 0.1 * u_score + bonus, 2)

def is_strong_candidate(title: str, snippet: str, url: str, query: str) -> bool:
    if not (word_boundary_present(title, query) or word_boundary_present(snippet, query)):
        return False
    if fuzz.token_set_ratio(title, query) < 85:
        return False
    if snippet and fuzz.token_set_ratio(snippet, query) < 70:
        return False
    return True

def dedupe(results):
    seen_urls = set()
    kept = []
    for r in results:
        key = normalize_url(r["url"])
        if key in seen_urls:
            continue
        duplicate = False
        for k in kept:
            if fuzz.token_set_ratio(k["title"], r["title"]) >= 95:
                duplicate = True
                break
        if duplicate:
            continue
        seen_urls.add(key)
        kept.append(r)
    return kept

def fetch_candidates_duckduckgo(query: str, lang: str = "fr"):
    url = "https://duckduckgo.com/html/"
    params = {"q": query, "kl": f"{lang}-{lang.upper()}"}
    html = requests.get(url, params=params, timeout=15).text
    out = []
    for res in re.findall(r'<a class="result__a" href="(.*?)">(.*?)</a>', html):
        title = res[1]
        link = res[0]
        snippet = re.search(r'<a class="result__snippet">(.*?)</a>', html)
        snippet = snippet.group(1) if snippet else ""
        out.append({"title": title, "url": link, "snippet": snippet})
    return out

def precise_search(user_query: str, site: str = None, k: int = 3, lang: str = "fr"):
    base_q = f'"{user_query}"'
    q = f'site:{site} {base_q}' if site else base_q
    cands = fetch_candidates_duckduckgo(q, lang=lang)
    filtered = []
    for c in cands:
        if is_strong_candidate(c["title"], c["snippet"], c["url"], user_query):
            c["score"] = relevance_score(c["title"], c["snippet"], c["url"], user_query)
            filtered.append(c)
    filtered.sort(key=lambda x: x["score"], reverse=True)
    filtered = dedupe(filtered)
    return filtered[:k]