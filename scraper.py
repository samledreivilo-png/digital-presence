import requests
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())

def check(url, slug, keywords):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        text = r.text.lower()
        final = r.url.lower()
        if r.status_code == 404:
            return False
        for bad in ["page not found", "page introuvable", "this page isn't available", "couldn't find"]:
            if bad in text:
                return False
        if slug in final:
            return True
        for kw in keywords:
            if kw in text:
                return True
        return False
    except Exception:
        return False

def analyze_company(company_name, progress_callback=None):
    slug = clean_name(company_name)
    
    results = {}
    
    if progress_callback:
        progress_callback("Verification Instagram...")
    ig_found = check(f"https://www.instagram.com/{slug}/", slug, ["followers", "posts", "publications"])
    results["instagram"] = {"platform": "Instagram", "found": ig_found, "url": f"https://www.instagram.com/{slug}/" if ig_found else None, "active": ig_found, "followers": None, "error": None}

    if progress_callback:
        progress_callback("Verification TikTok...")
    tt_found = check(f"https://www.tiktok.com/@{slug}", slug, [f"@{slug}", "followers", "likes"])
    results["tiktok"] = {"platform": "TikTok", "found": tt_found, "url": f"https://www.tiktok.com/@{slug}" if tt_found else None, "active": tt_found, "followers": None, "error": None}

    if progress_callback:
        progress_callback("Verification Facebook...")
    fb_found = check(f"https://www.facebook.com/{slug}", slug, ["facebook", slug])
    results["facebook"] = {"platform": "Facebook", "found": fb_found, "url": f"https://www.facebook.com/{slug}" if fb_found else None, "active": fb_found, "followers": None, "error": None}

    if progress_callback:
        progress_callback("Verification LinkedIn...")
    li_found = check(f"https://www.linkedin.com/company/{slug}", slug, ["linkedin", slug])
    results["linkedin"] = {"platform": "LinkedIn", "found": li_found, "url": f"https://www.linkedin.com/company/{slug}" if li_found else None, "active": li_found, "followers": None, "error": None}

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
