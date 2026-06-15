import requests
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def clean_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())

def empty_result(platform):
    return {"platform": platform, "found": False, "url": None, "active": False, "followers": None, "error": None}

def check_instagram(company_name):
    result = empty_result("Instagram")
    slug = clean_name(company_name)
    url = f"https://www.instagram.com/{slug}/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        text = r.text.lower()
        # Instagram retourne 200 meme si le compte n'existe pas
        # On cherche des signes que le profil existe vraiment
        if r.status_code == 404:
            result["found"] = False
        elif "page introuvable" in text or "page not found" in text or "sorry, this page" in text:
            result["found"] = False
        elif slug in text and ("followers" in text or "abonnes" in text or "posts" in text or "publications" in text):
            result["found"] = True
            result["url"] = url
            result["active"] = True
            match = re.search(r'"edge_followed_by":\{"count":(\d+)\}', r.text)
            if match:
                result["followers"] = int(match.group(1))
        elif r.status_code == 200 and slug in text:
            result["found"] = True
            result["url"] = url
            result["active"] = True
        else:
            result["found"] = False
    except Exception as e:
        result["error"] = str(e)[:80]
    return result

def check_tiktok(company_name):
    result = empty_result("TikTok")
    slug = clean_name(company_name)
    url = f"https://www.tiktok.com/@{slug}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        text = r.text.lower()
        if r.status_code == 404:
            result["found"] = False
        elif "couldn't find this account" in text or "ce compte est introuvable" in text:
            result["found"] = False
        elif f"@{slug}" in text or f'"uniqueid":"{slug}"' in text:
            result["found"] = True
            result["url"] = url
            result["active"] = True
            match = re.search(r'"followercount":(\d+)', text)
            if match:
                result["followers"] = int(match.group(1))
        else:
            result["found"] = False
    except Exception as e:
        result["error"] = str(e)[:80]
    return result

def check_facebook(company_name):
    result = empty_result("Facebook")
    slug = clean_name(company_name)
    url = f"https://www.facebook.com/{slug}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        text = r.text.lower()
        final_url = r.url.lower()
        # Facebook redirige vers login ou retourne une page generique
        if "login" in final_url and slug not in final_url:
            result["found"] = False
        elif r.status_code == 404:
            result["found"] = False
        elif "this page isn't available" in text or "cette page n'est pas disponible" in text:
            result["found"] = False
        elif slug in final_url or (slug in text and "facebook" in text):
            result["found"] = True
            result["url"] = url
            result["active"] = True
        else:
            result["found"] = False
    except Exception as e:
        result["error"] = str(e)[:80]
    return result

def check_linkedin(company_name):
    result = empty_result("LinkedIn")
    slug = clean_name(company_name)
    url = f"https://www.linkedin.com/company/{slug}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        text = r.text.lower()
        final_url = r.url.lower()
        # LinkedIn redirige toujours vers authwall si non connecte
        # On verifie si le slug apparait dans l'URL finale ou le contenu
        if "authwall" in final_url:
            # Le compte existe probablement — LinkedIn bloque mais la page existe
            if slug in text or slug in final_url:
                result["found"] = True
                result["url"] = url
                result["active"] = True
            else:
                result["found"] = False
        elif r.status_code == 404 or "page introuvable" in text or "no organization found" in text:
            result["found"] = False
        elif slug in final_url or slug in text:
            result["found"] = True
            result["url"] = url
            result["active"] = True
        else:
            result["found"] = False
    except Exception as e:
        result["error"] = str(e)[:80]
    return result

def analyze_company(company_name, progress_callback=None):
    results = {}
    checks = [
        ("instagram", check_instagram),
        ("tiktok", check_tiktok),
        ("facebook", check_facebook),
        ("linkedin", check_linkedin),
    ]
    names = {"instagram": "Instagram", "tiktok": "TikTok", "facebook": "Facebook", "linkedin": "LinkedIn"}
    for key, fn in checks:
        if progress_callback:
            progress_callback(f"Verification {names[key]}...")
        results[key] = fn(company_name)
        results[key]["platform"] = names[key]

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
