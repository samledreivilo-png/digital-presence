import asyncio
import re
import os
from playwright.async_api import async_playwright

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
        browser = await p.chromium.launch(
            headless=True,
            executable_path="/opt/render/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell"
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
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
        results["instagram"] = {"platform": "Instagram", "found": ig_found, "url": f"https://www.instagram.com/{slug}/" if ig_found else None, "active": ig
