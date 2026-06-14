"""
scraper.py — Moteur de recherche et vérification des réseaux sociaux
Utilise Playwright pour visiter les pages et extraire les infos.
"""

import asyncio
import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ─────────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────────

def clean_name(name: str) -> str:
    """Transforme 'Nike Store' → 'nikestore' pour construire des URLs à tester."""
    return re.sub(r"[^a-z0-9]", "", name.lower())

def parse_number(text: str) -> int:
    """Convertit '12,3 K' ou '1.2M' en entier. Retourne 0 si impossible."""
    if not text:
        return 0
    text = text.strip().replace(",", ".").replace(" ", "")
    try:
        if "k" in text.lower():
            return int(float(text.lower().replace("k", "")) * 1_000)
        if "m" in text.lower():
            return int(float(text.lower().replace("m", "")) * 1_000_000)
        return int(float(re.sub(r"[^\d.]", "", text)))
    except Exception:
        return 0

# ─────────────────────────────────────────────
# RÉSULTATS PAR DÉFAUT (si réseau non trouvé)
# ─────────────────────────────────────────────

def empty_result(platform: str) -> dict:
    return {
        "platform": platform,
        "found": False,
        "url": None,
        "followers": None,
        "active": False,
        "error": None,
    }

# ─────────────────────────────────────────────
# INSTAGRAM
# ─────────────────────────────────────────────

async def check_instagram(page, company_name: str) -> dict:
    result = empty_result("Instagram")
    slug = clean_name(company_name)
    url = f"https://www.instagram.com/{slug}/"

    try:
        await page.goto(url, timeout=15000)
        await page.wait_for_timeout(3000)

        # Vérifie si la page existe (Instagram redirige vers /accounts/login/ si introuvable)
        current_url = page.url
        if "accounts/login" in current_url or "challenge" in current_url:
            # Instagram bloque sans login → on marque comme "potentiellement trouvé"
            result["found"] = True
            result["url"] = url
            result["active"] = True
            result["followers"] = None  # Impossible à lire sans compte
            return result

        # Cherche le titre de la page pour savoir si le profil existe
        title = await page.title()
        if "Page not found" in title or "Instagram" == title.strip():
            result["found"] = False
            return result

        # Essaie d'extraire les followers depuis le meta
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

# ─────────────────────────────────────────────
# TIKTOK
# ─────────────────────────────────────────────

async def check_tiktok(page, company_name: str) -> dict:
    result = empty_result("TikTok")
    slug = clean_name(company_name)
    url = f"https://www.tiktok.com/@{slug}"

    try:
        await page.goto(url, timeout=15000)
        await page.wait_for_timeout(3000)

        title = await page.title()
        content = await page.content()

        # TikTok retourne "TikTok - Make Your Day" ou le nom du profil
        if "couldn't find" in content.lower() or "not found" in title.lower():
            result["found"] = False
            return result

        # Cherche les followers dans le contenu JSON embarqué
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

# ─────────────────────────────────────────────
# FACEBOOK
# ─────────────────────────────────────────────

async def check_facebook(page, company_name: str) -> dict:
    result = empty_result("Facebook")
    slug = clean_name(company_name)
    url = f"https://www.facebook.com/{slug}"

    try:
        await page.goto(url, timeout=15000)
        await page.wait_for_timeout(3000)

        current_url = page.url
        content = await page.content()
        title = await page.title()

        # Facebook redirige vers login si la page n'existe pas
        if "login" in current_url and slug not in current_url:
            result["found"] = False
            return result

        # Vérifie si la page a été trouvée
        if "page not found" in content.lower() or "ce contenu n'est pas disponible" in content.lower():
            result["found"] = False
            return result

        # Cherche les mentions "J'aime" ou "followers"
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

# ─────────────────────────────────────────────
# LINKEDIN
# ─────────────────────────────────────────────

async def check_linkedin(page, company_name: str) -> dict:
    result = empty_result("LinkedIn")
    slug = clean_name(company_name)
    url = f"https://www.linkedin.com/company/{slug}"

    try:
        await page.goto(url, timeout=15000)
        await page.wait_for_timeout(3000)

        current_url = page.url
        content = await page.content()

        # LinkedIn redirige vers login si non connecté — mais la page existe quand même
        if "authwall" in current_url or "login" in current_url:
            # On vérifie si la company existe dans l'URL de redirection
            if slug in current_url or slug in content:
                result["found"] = True
                result["url"] = url
                result["active"] = True
            else:
                result["found"] = False
            return result

        # Cherche le nombre de followers
        followers_match = re.search(r'([\d,]+)\s*(followers|abonnés)', content.lower())
        if followers_match:
            result["followers"] = parse_number(followers_match.group(1))

        if "page introuvable" not in content.lower() and "page not found" not in content.lower():
            result["found"] = True
            result["url"] = url
            result["active"] = True

    except PlaywrightTimeout:
        result["error"] = "Timeout"
    except Exception as e:
        result["error"] = str(e)[:80]

    return result

# ─────────────────────────────────────────────
# MOTEUR PRINCIPAL
# ─────────────────────────────────────────────

async def analyze_company(company_name: str, progress_callback=None) -> dict:
    """
    Lance l'analyse complète d'une entreprise sur les 4 réseaux.
    Retourne un dict avec les résultats par plateforme + le score global.
    """
    results = {}

    async with async_playwright() as p:
        # Lance un navigateur Chromium sans interface graphique
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        # Bloque les ressources inutiles pour aller plus vite
        async def block_resources(route):
            if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
                await route.abort()
            else:
                await route.continue_()

        page = await context.new_page()
        await page.route("**/*", block_resources)

        # --- Instagram ---
        if progress_callback:
            progress_callback("🔍 Vérification Instagram...")
        results["instagram"] = await check_instagram(page, company_name)

        # --- TikTok ---
        if progress_callback:
            progress_callback("🔍 Vérification TikTok...")
        results["tiktok"] = await check_tiktok(page, company_name)

        # --- Facebook ---
        if progress_callback:
            progress_callback("🔍 Vérification Facebook...")
        results["facebook"] = await check_facebook(page, company_name)

        # --- LinkedIn ---
        if progress_callback:
            progress_callback("🔍 Vérification LinkedIn...")
        results["linkedin"] = await check_linkedin(page, company_name)

        await browser.close()

    # Calcul du score
    results["score"] = calculate_score(results)
    results["company_name"] = company_name

    return results

# ─────────────────────────────────────────────
# CALCUL DU SCORE
# ─────────────────────────────────────────────

def calculate_score(results: dict) -> dict:
    """
    Calcule le score de présence digitale sur 100 points.
    Instagram: 40 pts max | TikTok: 20 pts | Facebook: 20 pts | LinkedIn: 20 pts
    """
    score = 0
    details = {}

    # Instagram (40 pts)
    ig = results.get("instagram", {})
    ig_score = 0
    if ig.get("found"):
        ig_score += 20  # Présence de base
        if ig.get("active"):
            ig_score += 10  # Compte actif
        followers = ig.get("followers") or 0
        if followers > 10000:
            ig_score += 10
        elif followers > 1000:
            ig_score += 5
        elif followers > 0:
            ig_score += 2
    details["instagram"] = ig_score
    score += ig_score

    # TikTok (20 pts)
    tt = results.get("tiktok", {})
    tt_score = 0
    if tt.get("found"):
        tt_score = 15
        if tt.get("followers") and tt["followers"] > 0:
            tt_score = 20
    details["tiktok"] = tt_score
    score += tt_score

    # Facebook (20 pts)
    fb = results.get("facebook", {})
    fb_score = 0
    if fb.get("found"):
        fb_score = 15
        if fb.get("active"):
            fb_score = 20
    details["facebook"] = fb_score
    score += fb_score

    # LinkedIn (20 pts)
    li = results.get("linkedin", {})
    li_score = 0
    if li.get("found"):
        li_score = 15
        if li.get("active"):
            li_score = 20
    details["linkedin"] = li_score
    score += li_score

    return {
        "total": score,
        "max": 100,
        "details": details,
        "label": score_label(score),
    }

def score_label(score: int) -> str:
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
