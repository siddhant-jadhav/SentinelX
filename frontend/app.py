"""
SentinelX — Cyber Threat Intelligence Sharing Platform
Main Streamlit Application Entry Point

Run with: streamlit run frontend/app.py --server.port 8503
"""
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

# ── Page Configuration ───────────────────────────────────────────
st.set_page_config(
    page_title="SentinelX — Threat Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load Custom CSS ──────────────────────────────────────────────
css_path = Path(__file__).parent / "assets" / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Initialize Session State ─────────────────────────────────────
if "token" not in st.session_state:
    st.session_state["token"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None

# ── Sidebar ──────────────────────────────────────────────────────
from frontend.components.sidebar import render_sidebar
render_sidebar()

# ── Landing Content ──────────────────────────────────────────────
from frontend.utils.helpers import page_header, metric_card_html
from frontend.utils import api_client
from frontend.components.metric_card import render_metric_cards
from frontend.components.threat_card import render_threat_card
from frontend.components.charts import threat_trend_chart, threats_by_severity_chart

# Page header
st.markdown(
    page_header(
        "Dashboard",
        "Real-time cyber threat intelligence overview",
        "📊"
    ),
    unsafe_allow_html=True,
)

# Check backend connectivity
overview = api_client.get_analytics_overview()

if overview.get("error"):
    st.markdown(
        '<div style="background:white;border:1px solid #E2E8F0;border-radius:16px;'
        'padding:2rem;text-align:center;margin:2rem 0;box-shadow:0 4px 6px rgba(0,0,0,0.05)">'
        '<div style="font-size:3rem;margin-bottom:1rem">🛡️</div>'
        '<h2 style="color:#1B2A4A!important;margin:0 0 0.5rem 0!important">Welcome to SentinelX</h2>'
        '<p style="color:#64748B;font-size:0.95rem;margin-bottom:1.5rem">'
        'Cyber Threat Intelligence Sharing Platform</p>'
        '<div style="background:#FEF3C7;border:1px solid #FDE68A;border-radius:10px;'
        'padding:1rem;text-align:left;max-width:500px;margin:0 auto">'
        '<p style="color:#92400E;font-size:0.85rem;margin:0">'
        '⚠️ <strong>Backend not connected.</strong> Start the API server:</p>'
        '<code style="display:block;margin-top:0.5rem;padding:0.5rem;'
        'background:#FFFBEB;border-radius:6px;font-size:0.8rem;color:#78350F">'
        'uvicorn backend.main:app --reload --port 8003</code>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── Metric Cards ─────────────────────────────────────────────────
render_metric_cards([
    {
        "label": "Total Threats",
        "value": overview.get("total_threats", 0),
        "icon": "🎯",
        "color": "#0A84FF",
    },
    {
        "label": "OTX Threats",
        "value": overview.get("otx_count", 0),
        "icon": "🛡️",
        "color": "#00D4AA",
    },
    {
        "label": "Community Threats",
        "value": overview.get("community_count", 0),
        "icon": "👥",
        "color": "#8B5CF6",
    },
    {
        "label": "Critical Threats",
        "value": overview.get("critical_count", 0),
        "icon": "🔴",
        "color": "#DC2626",
    },
])

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row ───────────────────────────────────────────────────
col_chart1, col_chart2 = st.columns([3, 2])

with col_chart1:
    trends = api_client.get_analytics_trends(30)
    if not trends.get("error") and trends.get("daily_volume"):
        fig = threat_trend_chart(trends["daily_volume"])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No trend data available yet")

with col_chart2:
    severity_data = overview.get("threats_by_severity", {})
    if severity_data:
        fig = threats_by_severity_chart(severity_data)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No severity data available yet")

# ── Recent Threat Feed ───────────────────────────────────────────
st.markdown("### 🔄 Recent Threat Feed")

recent = api_client.get_threats(limit=6)
if not recent.get("error") and recent.get("threats"):
    for threat in recent["threats"]:
        render_threat_card(threat)
else:
    st.info("No threats in the feed yet. Submit your first threat or sync from OTX!")
