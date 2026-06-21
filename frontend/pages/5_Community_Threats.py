"""
SentinelX — Community Threats Page
Browse all approved community-submitted threat intelligence.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

st.set_page_config(page_title="SentinelX — Community", page_icon="👥", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from frontend.components.sidebar import render_sidebar
from frontend.components.threat_card import render_threat_card
from frontend.components.metric_card import render_metric_cards
from frontend.utils.helpers import page_header
from frontend.utils import api_client

render_sidebar()

st.markdown(
    page_header(
        "Community Threats",
        "Approved threat intelligence contributed by the SentinelX community",
        "👥"
    ),
    unsafe_allow_html=True,
)

# ── Community Stats ──────────────────────────────────────────────
community_stats = api_client.get_community_stats()
if not community_stats.get("error"):
    render_metric_cards([
        {
            "label": "Total Submissions",
            "value": community_stats.get("total_submissions", 0),
            "icon": "📝",
            "color": "#8B5CF6",
        },
        {
            "label": "Approved",
            "value": community_stats.get("approved_count", 0),
            "icon": "✅",
            "color": "#10B981",
        },
        {
            "label": "Approval Rate",
            "value": f"{community_stats.get('approval_rate', 0)}%",
            "icon": "📊",
            "color": "#0A84FF",
        },
        {
            "label": "Pending Review",
            "value": community_stats.get("pending_count", 0),
            "icon": "⏳",
            "color": "#F59E0B",
        },
    ])

st.markdown("<br>", unsafe_allow_html=True)

# ── Filters ──────────────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns([3, 1.5, 1.5])

with col_f1:
    search = st.text_input(
        "Search", placeholder="Search community threats...",
        label_visibility="collapsed",
    )

with col_f2:
    severity = st.selectbox(
        "Severity",
        ["All Severities", "Critical", "High", "Medium", "Low", "Info"],
        label_visibility="collapsed",
    )

with col_f3:
    ind_type = st.selectbox(
        "Type",
        ["All Types", "IPv4", "IPv6", "Domain", "URL",
         "FileHash-MD5", "FileHash-SHA1", "FileHash-SHA256", "Email"],
        label_visibility="collapsed",
    )

# Build query
params = {
    "source": "Community",
    "limit": 30,
}
if search:
    params["search"] = search
if severity != "All Severities":
    params["severity"] = severity
if ind_type != "All Types":
    params["indicator_type"] = ind_type

# Fetch
data = api_client.get_threats(**params)

if data.get("error"):
    st.warning("⚠️ Unable to connect to backend API.")
    st.stop()

threats = data.get("threats", [])

# Results count
st.markdown(
    f'<p style="color:#64748B;font-size:0.85rem;margin-bottom:1rem">'
    f'Showing <strong>{len(threats)}</strong> approved community threats</p>',
    unsafe_allow_html=True,
)

# ── Threat Cards ─────────────────────────────────────────────────
if threats:
    for threat in threats:
        render_threat_card(threat)
else:
    st.info(
        "No community threats match your filters. "
        "Be the first to contribute — go to the **Submit Threat** page!"
    )

# ── Top Contributors ─────────────────────────────────────────────
if not community_stats.get("error"):
    contributors = community_stats.get("top_contributors", [])
    if contributors:
        st.markdown("---")
        st.markdown("### 🏆 Top Contributors")
        for i, c in enumerate(contributors[:5], 1):
            medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i - 1]
            progress = min(c.get("count", 0) * 10, 100)
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0">'
                f'<span style="font-size:1.2rem">{medal}</span>'
                f'<span style="font-weight:600;color:#1B2A4A;min-width:120px">'
                f'{c.get("username", "")}</span>'
                f'<div style="flex:1;background:#E2E8F0;border-radius:4px;'
                f'height:8px;overflow:hidden">'
                f'<div style="width:{progress}%;background:linear-gradient(90deg,#0A84FF,#00D4AA);'
                f'height:100%;border-radius:4px"></div></div>'
                f'<span style="font-weight:700;color:#1B2A4A;min-width:30px">'
                f'{c.get("count", 0)}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
