import asyncio
import re
from playwright.async_api import async_playwright

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())

async def check_page(page, url, slug, bad_words, good_words):
    try:
        await page.goto(url, timeout=20000, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        content = (await page.content()).lower()
        final_url = page.url.lower()
        if any(b in content for b in bad_words):
            return False
        if slug in final_url:
            return True
        if any(g in content for g in good_words):
            return True
        return False
    except Exception:
        return False

async def run_analysis(company_name, progress_callback=None):
    slug = clean_name(company_name)
    results = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=HEADERS["User-Agent"])
        page = await context.new_page()

        if progress_callback:
            progress_callback("Verification Instagram...")
        ig_found = await check_page(
            page,
            f"https://www.instagram.com/{slug}/",
            slug,
            ["page not found", "page introuvable", "sorry, this page"],
            ["followers", "posts", "publications", slug]
        )
        results["instagram"] = {"platform": "Instagram", "found": ig_found, "url": f"https://www.instagram.com/{slug}/" if ig_found else None, "active": ig_found, "followers": None, "error": None}

        if progress_callback:
            progress_callback("Verification TikTok...")
        tt_found = await check_page(
            page,
            f"https://www.tiktok.com/@{slug}",
            slug,
            ["couldn't find this account", "ce compte est introuvable"],
            [f"@{slug}", "followers", slug]
        )
        results["tiktok"] = {"platform": "TikTok", "found": tt_found, "url": f"https://www.tiktok.com/@{slug}" if tt_found else None, "active": tt_found, "followers": None, "error": None}

        if progress_callback:
            progress_callback("Verification Facebook...")
        fb_found = await check_page(
            page,
            f"https://www.facebook.com/{slug}",
            slug,
            ["this page isn't available", "cette page n'est pas disponible", "page not found"],
            [slug, "facebook"]
        )
        results["facebook"] = {"platform": "Facebook", "found": fb_found, "url": f"https://www.facebook.com/{slug}" if fb_found else None, "active": fb_found, "followers": None, "error": None}

        if progress_callback:
            progress_callback("Verification LinkedIn...")
        li_found = await check_page(
            page,
            f"https://www.linkedin.com/company/{slug}",
            slug,
            ["page introuvable", "no organization found", "this page doesn't exist"],
            [slug, "linkedin", "followers", "employes"]
        )
        results["linkedin"] = {"platform": "LinkedIn", "found": li_found, "url": f"https://www.linkedin.com/company/{slug}" if li_found else None, "active": li_found, "followers": None, "error": None}

        await browser.close()

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

def analyze_company(company_name, progress_callback=None):
    return asyncio.run(run_analysis(company_name, progress_callback))
