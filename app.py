import streamlit as st
from scraper import analyze_company

st.set_page_config(
    page_title="Présence Digitale",
    page_icon="📊",
    layout="centered",
)

st.markdown("""
<style>
    .stApp { background: #0f0f1a; }
    h1 { color: #a78bfa; font-size: 2.4rem !important; font-weight: 800 !important; }
    .score-box { background: #1a1a2e; border: 2px solid #6c63ff; border-radius: 16px; padding: 2rem; text-align: center; margin: 1.5rem 0; }
    .score-number { font-size: 4rem; font-weight: 900; color: #a78bfa; line-height: 1; }
    .network-card { background: #1a1a2e; border: 1px solid #2a2a42; border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 0.8rem; }
    .found { border-left: 4px solid #6c63ff; }
    .missing { border-left: 4px solid #3a3a5c; opacity: 0.6; }
    #MainMenu, footer, header { visibility: hidden; }
    .stButton > button { background: linear-gradient(135deg, #6c63ff, #a78bfa) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 700 !important; width: 100%; }
    .stTextInput > div > div > input { background: #1a1a2e !important; border: 1px solid #2a2a42 !important; color: white !important; border-radius: 10px !important; }
    .block-container { padding-top: 2rem; max-width: 720px; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📊 Présence Digitale")
st.markdown("Analysez la visibilité d'une entreprise sur les réseaux sociaux.")
st.divider()

company_name = st.text_input("Nom de l'entreprise", placeholder="ex: Nike, Zara, Apple...")
country = st.text_input("Pays (optionnel)", placeholder="ex: Malte, France, Belgique...")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("🔍 Analyser", use_container_width=True)

st.markdown("**Tester avec :**")
ex_cols = st.columns(4)
examples = ["Nike", "Zara", "Apple", "Decathlon"]
for i, ex in enumerate(examples):
    with ex_cols[i]:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            company_name = ex
            analyze_button = True

if analyze_button and company_name.strip():
    st.divider()
    label_pays = f" ({country.strip()})" if country.strip() else ""
    st.markdown(f"### Analyse de **{company_name.strip()}{label_pays}**")

    status_text = st.empty()
    progress_bar = st.progress(0)
    steps = [0.1, 0.35, 0.60, 0.85, 1.0]
    counter = [0]

    def update_progress(message):
        status_text.markdown(f"*{message}*")
        idx = min(counter[0], len(steps) - 1)
        progress_bar.progress(steps[idx])
        counter[0] += 1

    try:
        results = analyze_company(company_name.strip(), progress_callback=update_progress)
    except Exception as e:
        st.error(f"Erreur lors de l'analyse : {e}")
        st.stop()

    progress_bar.empty()
    status_text.empty()

    score = results["score"]
    total = score["total"]
    label = score["label"]

    st.markdown(f"""
    <div class="score-box">
        <div class="score-number">{total}<span style="font-size:1.5rem;color:#6c63ff">/100</span></div>
        <div style="color:#a78bfa;font-size:1.1rem;margin-top:0.5rem;font-weight:600">{label}</div>
        <div style="color:#8b8fa8;font-size:0.85rem">Score de présence digitale</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Réseaux sociaux analysés")

    platforms = [
        {"key": "instagram", "emoji": "📸", "name": "Instagram", "max_pts": 40},
        {"key": "tiktok", "emoji": "🎵", "name": "TikTok", "max_pts": 20},
        {"key": "facebook", "emoji": "👥", "name": "Facebook", "max_pts": 20},
        {"key": "linkedin", "emoji": "💼", "name": "LinkedIn", "max_pts": 20},
    ]

    for p in platforms:
        data = results.get(p["key"], {})
        found = data.get("found", False)
        followers = data.get("followers")
        pts = score["details"].get(p["key"], 0)
        card_class = "found" if found else "missing"
        status_icon = "✅" if found else "❌"

        followers_html = ""
        if followers and followers > 0:
            if followers >= 1_000_000:
                f_display = f"{followers/1_000_000:.1f}M"
            elif followers >= 1_000:
                f_display = f"{followers/1_000:.1f}K"
            else:
                f_display = str(followers)
            followers_html = f'<span style="background:#252540;border-radius:20px;padding:0.3rem 0.8rem;font-size:0.8rem;color:#a78bfa;margin-left:0.5rem">👁 {f_display} followers</span>'

        url = data.get("url", "")
        url_html = f'<a href="{url}" target="_blank" style="color:#6c63ff;font-size:0.8rem;">🔗 Voir</a>' if url else ""

        st.markdown(f"""
        <div class="network-card {card_class}">
            <div style="display:flex;align-items:center;gap:1rem">
                <div style="font-size:1.8rem">{p['emoji']}</div>
                <div style="flex:1">
                    <div style="font-weight:700;color:{'#e2e8f0' if found else '#555'}">
                        {p['name']} {status_icon} {followers_html}
                    </div>
                    <div style="font-size:0.82rem;color:#8b8fa8">
                        {'Trouvé' if found else 'Non trouvé'} {url_html}
                    </div>
                </div>
                <div style="text-align:right">
                    <div style="font-weight:800;font-size:1.2rem;color:{'#a78bfa' if pts > 0 else '#3a3a5c'}">{pts}/{p['max_pts']}</div>
                    <div style="font-size:0.72rem;color:#8b8fa8">points</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    recommendations = []
    if not results.get("instagram", {}).get("found"):
        recommendations.append("📸 **Instagram** — Créez un compte professionnel (+20 pts minimum)")
    if not results.get("tiktok", {}).get("found"):
        recommendations.append("🎵 **TikTok** — Le réseau à la croissance la plus rapide (+20 pts)")
    if not results.get("facebook", {}).get("found"):
        recommendations.append("👥 **Facebook** — Page indispensable pour le SEO local (+20 pts)")
    if not results.get("linkedin", {}).get("found"):
        recommendations.append("💼 **LinkedIn** — Vital pour la crédibilité B2B (+20 pts)")

    if recommendations:
        st.markdown("#### 💡 Recommandations")
        for rec in recommendations:
            st.markdown(f"- {rec}")

    st.success(f"✅ Analyse terminée — Score : **{total}/100**")

elif analyze_button and not company_name.strip():
    st.warning("⚠️ Entre le nom d'une entreprise pour lancer l'analyse.")

st.divider()
st.markdown('<p style="color:#555;font-size:0.78rem;text-align:center;">Analyse basée sur les profils publics</p>', unsafe_allow_html=True)
