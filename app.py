import streamlit as st
from scraper import analyze_company

st.set_page_config(
    page_title="Presence Digitale",
    page_icon="",
    layout="centered",
)

st.markdown("""
<style>
    .stApp { background: #ffffff; }
    h1 { color: #cc0000; font-size: 2.2rem !important; font-weight: 800 !important; }
    h3 { color: #111111; }
    h4 { color: #cc0000; }
    .score-box { background: #f9f9f9; border: 2px solid #cc0000; border-radius: 12px; padding: 2rem; text-align: center; margin: 1.5rem 0; }
    .score-number { font-size: 4rem; font-weight: 900; color: #cc0000; line-height: 1; }
    .network-card { background: #f9f9f9; border: 1px solid #dddddd; border-radius: 10px; padding: 1rem 1.5rem; margin-bottom: 0.8rem; }
    .found { border-left: 4px solid #cc0000; }
    .missing { border-left: 4px solid #cccccc; opacity: 0.6; }
    #MainMenu, footer, header { visibility: hidden; }
    .stButton > button { background: #cc0000 !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 700 !important; width: 100%; }
    .stButton > button:hover { background: #aa0000 !important; }
    .stTextInput > div > div > input { background: #ffffff !important; border: 1px solid #cccccc !important; color: #111111 !important; border-radius: 8px !important; }
    .stTextInput label { color: #111111 !important; font-weight: 600; }
    .stSuccess { background: #fff0f0 !important; color: #cc0000 !important; }
    .stWarning { background: #fff8f8 !important; }
    .block-container { padding-top: 2rem; max-width: 720px; }
    p, div { color: #111111; }
    .stDivider { border-color: #eeeeee; }
</style>
""", unsafe_allow_html=True)

st.markdown("# Presence Digitale")
st.markdown("Analysez la visibilite d'une entreprise sur les reseaux sociaux.")
st.divider()

company_name = st.text_input("Nom de l'entreprise", placeholder="ex: Nike, Zara, Apple...")
country = st.text_input("Pays (optionnel)", placeholder="ex: Malte, France, Belgique...")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("Analyser", use_container_width=True)

st.markdown("**Exemples rapides :**")
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
    st.markdown(f"### Analyse de {company_name.strip()}{label_pays}")

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
        <div class="score-number">{total}<span style="font-size:1.5rem;color:#111111">/100</span></div>
        <div style="color:#cc0000;font-size:1.1rem;margin-top:0.5rem;font-weight:700">{label}</div>
        <div style="color:#555555;font-size:0.85rem;margin-top:0.3rem">Score de presence digitale</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Reseaux sociaux analyses")

    platforms = [
        {"key": "instagram", "name": "Instagram", "max_pts": 40},
        {"key": "tiktok", "name": "TikTok", "max_pts": 20},
        {"key": "facebook", "name": "Facebook", "max_pts": 20},
        {"key": "linkedin", "name": "LinkedIn", "max_pts": 20},
    ]

    for p in platforms:
        data = results.get(p["key"], {})
        found = data.get("found", False)
        pts = score["details"].get(p["key"], 0)
        card_class = "found" if found else "missing"
        status_text_val = "Trouve" if found else "Non trouve"
        url = data.get("url", "")
        url_html = f'<a href="{url}" target="_blank" style="color:#cc0000;font-size:0.8rem;text-decoration:none;">Voir le profil</a>' if url else ""

        st.markdown(f"""
        <div class="network-card {card_class}">
            <div style="display:flex;align-items:center;gap:1rem">
                <div style="flex:1">
                    <div style="font-weight:700;color:#111111;font-size:1rem">
                        {p['name']} — {"Present" if found else "Absent"}
                    </div>
                    <div style="font-size:0.82rem;color:#555555;margin-top:0.2rem">
                        {status_text_val} {url_html}
                    </div>
                </div>
                <div style="text-align:right;min-width:70px">
                    <div style="font-weight:800;font-size:1.2rem;color:{'#cc0000' if pts > 0 else '#cccccc'}">{pts}/{p['max_pts']}</div>
                    <div style="font-size:0.72rem;color:#888888">points</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    recommendations = []
    if not results.get("instagram", {}).get("found"):
        recommendations.append("Instagram — Creez un compte professionnel (+20 pts minimum)")
    if not results.get("tiktok", {}).get("found"):
        recommendations.append("TikTok — Le reseau a la croissance la plus rapide (+20 pts)")
    if not results.get("facebook", {}).get("found"):
        recommendations.append("Facebook — Page indispensable pour le SEO local (+20 pts)")
    if not results.get("linkedin", {}).get("found"):
        recommendations.append("LinkedIn — Vital pour la credibilite professionnelle (+20 pts)")

    if recommendations:
        st.markdown("#### Recommandations")
        for rec in recommendations:
            st.markdown(f"- {rec}")

    st.success(f"Analyse terminee — Score : {total}/100")

elif analyze_button and not company_name.strip():
    st.warning("Entrez le nom d'une entreprise pour lancer l'analyse.")

st.divider()
st.markdown('<p style="color:#888888;font-size:0.78rem;text-align:center;">Analyse basee sur les profils publics — Les donnees peuvent varier selon les plateformes</p>', unsafe_allow_html=True)
