import asyncio
import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

def clean_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())

def parse_number(text):
    if not text:
        return 0
    text = text.strip().replace(",", ".").replace(" ", "")
    try:
        if "k" in text.lower():
            return int(float(text.lower().replace("k", "")) * 1000)
        if "m" in text.lower():
            return int(float(text.lower().replace("m", "")) * 1000000)
        return int(float(re.sub(r"[^\d.]", "", text)))
    except Exception:
        return 0

def empty_result(platform):
    return {"platform": platform, "found": False, "url": None, "followers": None, "active": False, "error": None}

async def check_instagram(page, company_name):
    result = empty_result("Instagram")
    slug = clean_name(company_name)
    url = f"https://www.instagram.com/{slug}/"
    try:
        await page.goto(url, timeout=15000)
        await page.wait_for_timeout(3000)
        current_url = page.url
        if "accounts/login" in current_url or "challenge" in current_url:
            result["found"] = True
            result["url"] = url
            result["active"] = True
            return result
        title = await page.title()
        if "Page not found" in title or "Instagram" == title.strip():
            result["found"] = False
            return result
        content = await page.content()
        match = re.search(r'"edge_followed_by":\{"count":(\d+)\}', content)
        if match:
            result["followers"] = int(match.group(1))
        result["found"] = True
        result["url"] = url
        result["active"] = True
    except PlaywrightTimeout:
        result["error"] = "Timeout"
    except Exception as e:
        result["error"] = str(e)[:80]
    return result

async def check_tiktok(page, company_name):
    result = empty_result("TikTok")
    slug = clean_name(company_name)
    url = f"https://www.tiktok.com/@{slug}"
    try:
        await page.goto(url, timeout=15000)
        await page.wait_for_timeout(3000)
        title = await page.title()
        content = await page.content()
        if "couldn't find" in content.lower() or "not found" in title.lower():
            result["found"] = False
            return result
        match = re.search(r'"followerCount":(\d+)', content)
        if match:
            result["followers"] = int(match.group(1))
            result["found"] = True
            result["url"] = url
            result["active"] = True
        elif slug in title.lower() or "@" in title:
            result["found"] = True
            result["url"] = url
            result["active"] = True
    except PlaywrightTimeout:
        result["error"] = "Timeout"
    except Exception as e:
        result["error"] = str(e)[:80]
    return result

async def check_facebook(page, company_name):
    result = empty_result("Facebook")
    slug = clean_name(company_name)
    url = f"https://www.facebook.com/{slug}"
    try:
        await page.goto(url, timeout=15000)
        await page.wait_for_timeout(3000)
        current_url = page.url
        content = await page.content()
        if "login" in current_url and slug not in current_url:
            result["found"] = False
            return result
        if "page not found" in content.lower():
            result["found"] = False
            return result
        likes_match = re.search(r'([\d\s,.]+)\s*(personnes aiment|people like|followers|abonnés)', content.lower())
        if likes_match:
            result["followers"] = parse_number(likes_match.group(1))
        result["found"] = True
        result["url"] = url
        result["active"] = True
    except PlaywrightTimeout:
        result["error"] = "Timeout"
    except Exception as e:
        result["error"] = str(e)[:80]
    return result

async def check_linkedin(page, company_name):
    result = empty_result("LinkedIn")
    slug = clean_name(company_name)
    url = f"https://www.linkedin.com/company/{slug}"
    try:
        await page.goto(url, timeout=15000)
        await page.wait_for_timeout(3000)
        current_url = page.url
        content = await page.content()
        if "authwall" in current_url or "login" in current_url:
            if slug in current_url or slug in content:
                result["found"] = True
                result["url"] = url
                result["active"] = True
            else:
                result["found"] = False
            return result
        followers_match = re.search(r'([\d,]+)\s*(followers|abonnés)', content.lower())
        if followers_match:
            result["followers"] = parse_number(followers_match.group(1))
        if "page not found" not in content.lower():
            result["found"] = True
            result["url"] = url
            result["active"] = True
    except PlaywrightTimeout:
        result["error"] = "Timeout"
    except Exception as e:
        result["error"] = str(e)[:80]
    return result

async def analyze_company(company_name, progress_callback=None):
    results = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_cont
