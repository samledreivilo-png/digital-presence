import streamlit as st
from scraper import analyze_company

st.set_page_config(page_title="DMXPulse", layout="centered")

st.markdown("""
<style>
    .stApp { background: #ffffff; }
    .stButton > button { background: #cc0000 !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 700 !important; }
    .stTextInput > div > div > input { background: #ffffff !important; border: 1px solid #cccccc !important; color: #111111 !important; border-radius: 8px !important; }
    .score-box { background: #f9f9f9; border: 2px solid #cc0000; border-radius: 12px; padding: 2rem; text-align: center; margin: 1.5rem 0; }
    .score-number { font-size: 4rem; font-weight: 900; color: #cc0000; line-height: 1; }
    .network-card { background: #f9f9f9; border: 1px solid #dddddd; border-radius: 10px; padding: 1rem 1.5rem; margin-bottom: 0.8rem; }
    .found { border-left: 4px solid #cc0000; }
    .missing { border-left: 4px solid #cccccc; opacity: 0.6; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2rem; max-width: 720px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1><span style="color:#111111;">DMX</span><span style="color:#cc0000;">Pulse</span></h1>', unsafe_allow_html=True)
st.markdown('<h2 style="color:#cc0000;font-size:1.8rem;font-weight:900;letter-spacing:4px;">MALTA</h2>', unsafe_allow_html=True)
st.markdown("Analyse the digital presence of a business across social media platforms.")
st.divider()

company_name = st.text_input("Business name", placeholder="e.g. Cafe Jubilee, Wembley Store...")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("Analyse", use_container_width=True)

if analyze_button and company_name.strip():
    st.divider()
    st.markdown(f"### Analysing: {company_name.strip()} — Malta")

    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    steps = [0.1, 0.35, 0.60, 0.85, 1.0]
    counter = [0]

    def update_progress(message):
        status_placeholder.markdown(f"*{message}*")
        idx = min(counter[0], len(steps) - 1)
        progress_bar.progress(steps[idx])
        counter[0] += 1

    try:
        results = analyze_company(company_name.strip(), country="Malta", progress_callback=update_progress)
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

    progress_bar.empty()
    status_placeholder.empty()

    if not results or "score" not in results:
        st.error("No results returned. Please try again.")
        st.stop()

    score = results["score"]
    total = score["total"]
    label = score["label"]

    st.markdown(f"""
    <div class="score-box">
        <div class="score-number">{total}<span style="font-size:1.5rem;color:#111111">/100</span></div>
        <div style="color:#cc0000;font-size:1.1rem;margin-top:0.5rem;font-weight:700">{label}</div>
        <div style="color:#555555;font-size:0.85rem;margin-top:0.3rem">Digital Presence Score</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Social Media Platforms")

    platforms = [
        {"key": "instagram", "name": "Instagram", "max_pts": 40},
        {"key": "tiktok", "name": "TikTok", "max_pts": 20},
        {"key": "facebook", "name": "Facebook", "max_pts": 20},
        {"key": "linkedin", "name": "LinkedIn", "max_pts": 20},
    ]

    for p in platforms:
        data = results.get(p["key"]) or {}
        found = data.get("found", False)
        pts = score["details"].get(p["key"], 0)
        url = data.get("url") or ""
        url_html = f'<a href="{url}" target="_blank" style="color:#cc0000;font-size:0.8rem;">View profile</a>' if url else ""

        st.markdown(f"""
        <div class="network-card {'found' if found else 'missing'}">
            <div style="display:flex;align-items:center;gap:1rem">
                <div style="flex:1">
                    <div style="font-weight:700;color:#111111">{p['name']} — {"Found" if found else "Not found"}</div>
                    <div style="font-size:0.82rem;color:#555555;margin-top:0.2rem">{"Account detected" if found else "No account found"} {url_html}</div>
                </div>
                <div style="text-align:right;min-width:80px">
                    <div style="font-weight:800;font-size:1.2rem;color:{'#cc0000' if pts > 0 else '#cccccc'}">{pts}/{p['max_pts']}</div>
                    <div style="font-size:0.72rem;color:#888888">points</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    recommendations = []
    if not (results.get("instagram") or {}).get("found"):
        recommendations.append("Instagram — Create a professional account to boost your visibility (+40 pts)")
    if not (results.get("tiktok") or {}).get("found"):
        recommendations.append("TikTok — The fastest growing platform for local businesses (+20 pts)")
    if not (results.get("facebook") or {}).get("found"):
        recommendations.append("Facebook — Essential for local SEO and community engagement (+20 pts)")
    if not (results.get("linkedin") or {}).get("found"):
        recommendations.append("LinkedIn — Key for professional credibility and B2B visibility (+20 pts)")

    if recommendations:
        st.markdown("#### Recommendations")
        for rec in recommendations:
            st.markdown(f"- {rec}")

    st.success(f"Analysis complete — Score: {total}/100")

elif analyze_button and not company_name.strip():
    st.warning("Please enter a business name to begin the analysis.")

st.divider()
st.markdown('<p style="color:#888888;font-size:0.78rem;text-align:center;">Analysis based on publicly available data — Results may vary depending on the platform</p>', unsafe_allow_html=True)
