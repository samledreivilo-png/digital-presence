import os
import re
import requests

SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")

def clean_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower()).strip()

def search_social(company, platform, site, country):
    try:
        slug = clean_name(company)
        country_query = country.strip() if country.strip() else "Malta"
        params = {
            "engine": "google",
            "q": f"{company} {platform} {country_query}",
            "gl": "mt",
            "hl": "en",
            "api_key": SERPAPI_KEY,
            "num": 5,
        }
        r = requests.get("https://serpapi.com/search", params=params, timeout=10)
        data = r.json()
        results = data.get("organic_results", [])
        for result in results:
            link = result.get("link", "").lower()
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            if site not in link:
                continue
            if slug in link:
                return True, result.get("link")
            if slug in title or slug in snippet:
                return True, result.get("link")
        return False, None
    except Exception:
        return False, None

def analyze_company(company_name, country="Malta", progress_callback=None):
    results = {}

    if progress_callback:
        progress_callback("Verification Instagram...")
    ig, ig_url = search_social(company_name, "instagram", "instagram.com", country)
    results["instagram"] = {"platform": "Instagram", "found": ig, "url": ig_url, "active": ig, "followers": None, "error": None}

    if progress_callback:
        progress_callback("Verification TikTok...")
    tt, tt_url = search_social(company_name, "tiktok", "tiktok.com", country)
    results["tiktok"] = {"platform": "TikTok", "found": tt, "url": tt_url, "active": tt, "followers": None, "error": None}

    if progress_callback:
        progress_callback("Verification Facebook...")
    fb, fb_url = search_social(company_name, "facebook", "facebook.com", country)
    results["facebook"] = {"platform": "Facebook", "found": fb, "url": fb_url, "active": fb, "followers": None, "error": None}

    if progress_callback:
        progress_callback("Verification LinkedIn...")
    li, li_url = search_social(company_name, "linkedin", "linkedin.com", country)
    results["linkedin"] = {"platform": "LinkedIn", "found": li, "url": li_url, "active": li, "followers": None, "error": None}

    score = 0
    details = {}
    weights = {"instagram": 40, "tiktok": 20, "facebook": 20, "linkedin": 20}
    for key, pts in weights.items():
        v = pts if results[key]["found"] else 0
        details[key] = v
        score += v

    if score >= 80:
        label = "Excellente presence"
    elif score >= 60:
        label = "Bonne presence"
    elif score >= 40:
        label = "Presence partielle"
    elif score >= 20:
        label = "Presence faible"
    else:
        label = "Absent du digital"

    results["score"] = {"total": score, "max": 100, "details": details, "label": label}
    results["company_name"] = company_name
    return results
