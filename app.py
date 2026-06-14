"""
app.py — Interface web Streamlit pour l'analyseur de présence digitale
Lance avec : streamlit run app.py
"""

import streamlit as st
import asyncio
import time
from src.scraper import analyze_company

# ─────────────────────────────────────────────
# CONFIGURATION DE LA PAGE
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Présence Digitale",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CSS PERSONNALISÉ
# ─────────────────────────────────────────────

st.markdown("""
<style>
    /* Fond global */
    .stApp { background: #0f0f1a; }

    /* Titre principal */
    h1 { 
        background: linear-gradient(135deg, #6c63ff, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }

    /* Sous-titre */
    .subtitle {
        color: #8b8fa8;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Carte de résultat par réseau */
    .network-card {
        background: #1a1a2e;
        border: 1px solid #2a2a42;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .network-found { border-left: 4px solid #6c63ff; }
    .network-missing { border-left: 4px solid #3a3a5c; opacity: 0.6; }

    /* Score principal */
    .score-circle {
        background: linear-gradient(135deg, #1a1a2e, #0f0f1a);
        border: 2px solid #6c63ff;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1.5rem 0;
    }
    .score-number {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #6c63ff, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    .score-label {
        color: #a78bfa;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 600;
    }

    /* Métriques */
    .metric-pill {
        background: #252540;
        border-radius: 20px;
        padding: 0.3rem 0.8rem;
        font-size: 0.8rem;
        color: #a78bfa;
        display: inline-block;
        margin-left: 0.5rem;
    }

    /* Bouton */
    .stButton > button {
        background: linear-gradient(135deg, #6c63ff, #a78bfa) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        width: 100%;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }

    /* Input */
    .stTextInput > div > div > input {
        background: #1a1a2e !important;
        border: 1px solid #2a2a42 !important;
        color: white !important;
        border-radius: 10px !important;
        font-size: 1rem !important;
        padding: 0.8rem 1rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6c63ff !important;
        box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.15) !important;
    }

    /* Barre de progression */
    .stProgress > div > div > div { background: #6c63ff !important; }

    /* Masquer les éléments Streamlit par défaut */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2rem; max-width: 720px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# EN-TÊTE
# ─────────────────────────────────────────────

st.markdown("# 📊 Présence Digitale")
st.markdown(
    '<p class="subtitle">Analysez la visibilité d\'une entreprise sur les réseaux sociaux en quelques secondes.</p>',
    unsafe_allow_html=True
)

st.divider()

# ─────────────────────────────────────────────
# FORMULAIRE DE RECHERCHE
# ─────────────────────────────────────────────

company_name = st.text_input(
    "Nom de l'entreprise ou boutique",
    placeholder="ex: Nike, Zara, BoulangeriePaul...",
    label_visibility="visible",
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("🔍 Analyser maintenant", use_container_width=True)

# ─────────────────────────────────────────────
# EXEMPLES RAPIDES
# ─────────────────────────────────────────────

st.markdown("**Tester avec :**")
ex_cols = st.columns(4)
examples = ["Nike", "Zara", "Apple", "Decathlon"]
for i, ex in enumerate(examples):
    with ex_cols[i]:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            company_name = ex
            analyze_button = True

# ─────────────────────────────────────────────
# LANCEMENT DE L'ANALYSE
# ─────────────────────────────────────────────

if analyze_button and company_name.strip():
    st.divider()
    st.markdown(f"### Analyse de **{company_name.strip()}**")

    # Zone de statut en temps réel
    status_text = st.empty()
    progress_bar = st.progress(0)
    progress_steps = [0.1, 0.35, 0.60, 0.85, 1.0]
    step_counter = [0]  # liste pour contourner la closure Python

    def update_progress(message: str):
        status_text.markdown(f"*{message}*")
        idx = min(step_counter[0], len(progress_steps) - 1)
        progress_bar.progress(progress_steps[idx])
        step_counter[0] += 1

    # Lance l'analyse asynchrone depuis Streamlit (synchrone)
    with st.spinner(""):
        try:
            results = asyncio.run(
                analyze_company(company_name.strip(), progress_callback=update_progress)
            )
        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {e}")
            st.stop()

    # Nettoie la barre de progression
    progress_bar.empty()
    status_text.empty()

    # ─────────────────────────────────────────
    # AFFICHAGE DU SCORE GLOBAL
    # ─────────────────────────────────────────

    score = results["score"]
    total = score["total"]
    label = score["label"]

    st.markdown(f"""
    <div class="score-circle">
        <div class="score-number">{total}<span style="font-size:1.5rem;color:#a78bfa">/100</span></div>
        <div class="score-label">{label}</div>
        <div style="color:#8b8fa8; font-size:0.85rem; margin-top:0.3rem">Score de présence digitale</div>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────
    # DÉTAILS PAR RÉSEAU SOCIAL
    # ─────────────────────────────────────────

    st.markdown("#### Réseaux sociaux analysés")

    platforms = [
        {
            "key": "instagram",
            "emoji": "📸",
            "name": "Instagram",
            "max_pts": 40,
        },
        {
            "key": "tiktok",
            "emoji": "🎵",
            "name": "TikTok",
            "max_pts": 20,
        },
        {
            "key": "facebook",
            "emoji": "👥",
            "name": "Facebook",
            "max_pts": 20,
        },
        {
            "key": "linkedin",
            "emoji": "💼",
            "name": "LinkedIn",
            "max_pts": 20,
        },
    ]

    for p in platforms:
        data = results.get(p["key"], {})
        found = data.get("found", False)
        followers = data.get("followers")
        pts = score["details"].get(p["key"], 0)
        card_class = "network-found" if found else "network-missing"
        status_icon = "✅" if found else "❌"
        status_text_val = "Trouvé" if found else "Non trouvé"

        # Construction de l'affichage des followers
        followers_html = ""
        if followers and followers > 0:
            if followers >= 1_000_000:
                followers_display = f"{followers/1_000_000:.1f}M"
            elif followers >= 1_000:
                followers_display = f"{followers/1_000:.1f}K"
            else:
                followers_display = str(followers)
            followers_html = f'<span class="metric-pill">👁 {followers_display} followers</span>'

        url = data.get("url", "")
        url_html = f'<a href="{url}" target="_blank" style="color:#6c63ff;font-size:0.8rem;text-decoration:none;">🔗 Voir le profil</a>' if url else ""

        error = data.get("error")
        error_html = f'<span style="color:#ff6b6b;font-size:0.75rem;"> ⚠ {error}</span>' if error else ""

        st.markdown(f"""
        <div class="network-card {card_class}">
            <div style="font-size:1.8rem">{p['emoji']}</div>
            <div style="flex:1">
                <div style="font-weight:700;color:{'#e2e8f0' if found else '#555'}">
                    {p['name']} {status_icon}
                    {followers_html}
                </div>
                <div style="font-size:0.82rem;color:#8b8fa8;margin-top:0.2rem">
                    {status_text_val} {url_html} {error_html}
                </div>
            </div>
            <div style="text-align:right;min-width:70px">
                <div style="font-weight:800;font-size:1.2rem;color:{'#a78bfa' if pts > 0 else '#3a3a5c'}">
                    {pts}/{p['max_pts']}
                </div>
                <div style="font-size:0.72rem;color:#8b8fa8">points</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ─────────────────────────────────────────
    # DÉCOMPOSITION DU SCORE
    # ─────────────────────────────────────────

    st.divider()
    st.markdown("#### Répartition des points")

    bar_cols = st.columns(4)
    bar_data = [
        ("Instagram", score["details"].get("instagram", 0), 40, "📸"),
        ("TikTok", score["details"].get("tiktok", 0), 20, "🎵"),
        ("Facebook", score["details"].get("facebook", 0), 20, "👥"),
        ("LinkedIn", score["details"].get("linkedin", 0), 20, "💼"),
    ]
    for col, (name, pts, max_pts, emoji) in zip(bar_cols, bar_data):
        pct = int((pts / max_pts) * 100) if max_pts else 0
        col.metric(f"{emoji} {name}", f"{pts}/{max_pts}", f"{pct}%")

    # ─────────────────────────────────────────
    # RECOMMANDATIONS
    # ─────────────────────────────────────────

    recommendations = []
    if not results.get("instagram", {}).get("found"):
        recommendations.append("📸 **Instagram** — Créez un compte professionnel pour +20 pts minimum")
    if not results.get("tiktok", {}).get("found"):
        recommendations.append("🎵 **TikTok** — Le réseau à la croissance la plus rapide (+20 pts potentiels)")
    if not results.get("facebook", {}).get("found"):
        recommendations.append("👥 **Facebook** — Page d'entreprise indispensable pour le SEO local (+20 pts)")
    if not results.get("linkedin", {}).get("found"):
        recommendations.append("💼 **LinkedIn** — Vital pour la crédibilité B2B (+20 pts)")

    if recommendations:
        st.markdown("#### 💡 Recommandations")
        for rec in recommendations:
            st.markdown(f"- {rec}")

    st.success(f"✅ Analyse terminée pour **{company_name}** — Score : **{total}/100**")

elif analyze_button and not company_name.strip():
    st.warning("⚠️ Entrez le nom d'une entreprise pour lancer l'analyse.")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.divider()
st.markdown(
    '<p style="color:#555;font-size:0.78rem;text-align:center;">'
    "Analyse basée sur les profils publics • Certaines données peuvent être limitées par les plateformes"
    "</p>",
    unsafe_allow_html=True,
)
