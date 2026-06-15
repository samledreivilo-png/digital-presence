import requests
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())

def get_status(company_name, path):
    slug = clean_name(company_name)
    url = path.format(slug=slug)
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        found = r.status_code == 200
        return {"found": found, "url": url if found else None, "active": found, "followers": None, "error": None}
    except Exception as e:
        return {"found": False, "url": None, "active": False, "followers": None, "error": str(e)[:80]}

def analyze_company(company_name, progress_callback=None):
    results = {}
    platforms = [
        ("instagram", "https://www.instagram.com/{slug}/"),
        ("tiktok", "https://www.tiktok.com/@{slug}"),
        ("facebook", "https://www.facebook.com/{slug}"),
        ("linkedin", "https://www.linkedin.com/company/{slug}"),
    ]
    names = {"instagram": "Instagram", "tiktok": "TikTok", "facebook": "Facebook", "linkedin": "LinkedIn"}
    for key, path in platforms:
        if progress_callback:
            progress_callback(f"Verification {names[key]}...")
        results[key] = get_status(company_name, path)
        results[key]["platform"] = names[key]
    score = 0
    details = {}
    weights = {"instagram": 40, "tiktok": 20, "facebook": 20, "linkedin": 20}
    for key, pts in weights.items():
        v = pts if results[key]["found"] else 0
        details[key] = v
        score += v
    if score >= 80:
        label = "Excellente presence 🌟"
    elif score >= 60:
        label = "Bonne presence ✅"
    elif score >= 40:
        label = "Presence partielle ⚠️"
    elif score >= 20:
        label = "Presence faible 📉"
    else:
        label = "Absent du digital ❌"
    results["score"] = {"total": score, "max": 100, "details": details, "label": label}
    results["company_name"] = company_name
    return results
