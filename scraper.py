import asyncio
import re
import os
import glob
from playwright.async_api import async_playwright


def clean_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def find_chromium():
    patterns = [
        "/opt/render/.cache/ms-playwright/**/chrome-headless-shell",
        "/opt/render/.cache/ms-playwright/**/chromium",
        "/opt/render/.cache/ms-playwright/**/chrome",
        "/root/.cache/ms-playwright/**/chrome-headless-shell",
        "/home/**/.cache/ms-playwright/**/chrome-headless-shell",
    ]
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            return matches[0]
    return None


async def run_analysis(company_name, progress_callback=None):
    slug = clean_name(company_name)
    results = {}

    chromium = find_chromium()

    async with async_playwright() as p:
        launch_args = {"headless": True}
        if chromium:
            launch_args["executable_path"] = chromium

        browser = await p.chromium.launch(**launch_args)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        async def check(url, bad, good):
            try:
                await page.goto(url, timeout=20000, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
                content = (await page.content()).lower()
                final = page.url.lower()
                if any(b in content for b in bad):
                    return False
                if slug in final:
                    return True
                if any(g in content for g in good):
                    return True
                return False
            except Exception:
                return False

        if progress_callback:
            progress_callback("Verification Instagram...")
        ig = await check(
            f"https://www.instagram.com/{slug}/",
            ["page not found", "page introuvable", "sorry, this page"],
            ["followers", "posts", slug]
        )

        if progress_callback:
            progress_callback("Verification TikTok...")
        tt = await check(
            f"https://www.tiktok.com/@{slug}",
            ["couldn't find this account", "ce compte est introuvable"],
            [slug, "followers"]
        )

        if progress_callback:
            progress_callback("Verification Facebook...")
        fb = await check(
            f"https://www.facebook.com/{slug}",
            ["this page isn't available", "page not found"],
            [slug, "facebook"]
        )

        if progress_callback:
            progress_callback("Verification LinkedIn...")
        li = await check(
            f"https://www.linkedin.com/company/{slug}",
            ["page introuvable", "no organization found"],
            [slug, "linkedin"]
        )

        await browser.close()

    def make(platform, found, url):
        return {"platform": platform, "found": found, "url": url if found else None, "active": found, "followers": None, "error": None}

    results["instagram"] = make("Instagram", ig, f"https://www.instagram.com/{slug}/")
    results["tiktok"] = make("TikTok", tt, f"https://www.tiktok.com/@{slug}")
    results["facebook"] = make("Facebook", fb, f"https://www.facebook.com/{slug}")
    results["linkedin"] = make("LinkedIn", li, f"https://www.linkedin.com/company/{slug}")

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
