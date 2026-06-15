import requests
import re

def clean_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())

def empty_result(platform):
    return {"platform": platform, "found": False, "url": None, "followers": None, "active": False, "error": None}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

def check_instagram(company_name):
    result = empty_result("Instagram")
    slug = clean_name(company_name)
    url = f"https://www.instagram.com/{slug}/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200 and slug in r.text:
            result["found"] = True
            result["url"] = url
            result["active"] = True
            match = re.search(r'"edge_followed_by":\{"count":(\d+)\}', r.text)
            if match:
                result["followers"] = int(match.group(1))
        elif r.status_code == 404:
            result["found"] = False
        else:
            result["found"] = True
            result["url"] = url
            result["active"] = True
    except Exception as e:
        result["error"] = str(e)[:80]
    return result

def check_tiktok(company_name):
    result = empty_result("TikTok")
    slug = clean_name(company_name)
    url = f"https://www.tiktok.com/@{slug}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            result["found"] = True
            result["url"] = url
            result["active"] = True
            match = re.search(r'"followerCount":(\d+)', r.text)
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
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200 and slug in r.url:
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
        if r.status_code == 200 or "authwall" in r.url:
            result["found"] = True
            result["url"] = url
            result["active"] = True
        else:
            result["found"] = False
    except Exception as e:
        result["error"] = str(e)[:80]
    return result

def calculate_score(results):
    score = 0
    details = {}
    ig = results.get("instagram", {})
    ig_score = 0
    if ig.get("found"):
        ig_score += 20
        if ig.get("active"):
            ig_score += 10
        followers = ig.get("followers") or 0
        if followers > 10000:
            ig_score += 10
        elif followers > 1000:
            ig_score += 5
        elif followers > 0:
            ig_score += 2
    details["instagram"] = ig_score
    score += ig_score
    tt = results.get("tiktok", {})
    tt_score = 20 if tt.get("found") else 0
    details["tiktok"] = tt_score
    score += tt_score
    fb = results.get("facebook", {})
    fb_score = 20 if fb.get("found") else 0
    details["facebook"] = fb_score
    score += fb_score
    li = results.get("linkedin", {})
    li_score = 20 if li.get("found") else 0
    details["linkedin"] = li_score
    score += li_score
    return {"total": score, "max": 100, "details": details, "label": score_label(score)}

def score_label(score):
    if score >= 80:
        return "Excellente présence 🌟"
    elif score >= 60:
        return "Bonne présence ✅"
    elif score >= 40:
        return "Présence partielle ⚠️"
    elif score >= 20:
        return "Présence faible 📉"
    else:
        return "Absent du digital ❌"

def analyze_company(company_name, progress_callback=None):
    results = {}
    if progress_callback:
        progress_callback("Vérification Instagram...")
    results["instagram"] = check_instagram(company_name)
    if progress_callback:
        progress_callback("Vérification TikTok...")
    results["tiktok"] = check_tiktok(company_name)
    if progress_callback:
        progress_callback("Vérification Facebook...")
    results["facebook"] = check_facebook(company_name)
    if progress_callback:
        progress_callback("Vérification LinkedIn...")
    results["linkedin"] = check_linkedin(company_name)
    results["score"] = calculate_score(results)
    results["company_name"] = company_name
    return results
    elif score >= 20:
        return "Présence faible 📉"
    else:
        return "Absent du digital ❌"
