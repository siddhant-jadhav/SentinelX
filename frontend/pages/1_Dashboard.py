"""
SentinelX — Dashboard Page
Real-time cyber threat intelligence overview with metrics, charts, and recent feed.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

st.set_page_config(page_title="SentinelX — Dashboard", page_icon="📊", layout="wide")

# Load CSS
css_path = Path(__file__).parent.parent / "assets" / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from frontend.components.sidebar import render_sidebar
from frontend.components.metric_card import render_metric_cards
from frontend.components.threat_card import render_threat_card
from frontend.components.charts import threat_trend_chart, top_categories_chart, threats_by_severity_chart
from frontend.utils.helpers import page_header
from frontend.utils import api_client

render_sidebar()

# Page header
st.markdown(
    page_header("Dashboard", "Real-time cyber threat intelligence overview", "📊"),
    unsafe_allow_html=True,
)

# Fetch data
overview = api_client.get_analytics_overview()
if overview.get("error"):
    st.warning(
        "⚠️ Unable to connect to backend. Start the API server:\n\n"
        "```bash\nuvicorn backend.main:app --reload --port 8003\n```"
    )
    st.stop()

# Metric cards
render_metric_cards([
    {"label": "Total Threats", "value": overview.get("total_threats", 0), "icon": "🎯", "color": "#0A84FF"},
    {"label": "OTX Threats", "value": overview.get("otx_count", 0), "icon": "🛡️", "color": "#00D4AA"},
    {"label": "Community Threats", "value": overview.get("community_count", 0), "icon": "👥", "color": "#8B5CF6"},
    {"label": "Critical Threats", "value": overview.get("critical_count", 0), "icon": "🔴", "color": "#DC2626"},
])

st.markdown("<br>", unsafe_allow_html=True)

# Charts
col1, col2 = st.columns([3, 2])

with col1:
    trends = api_client.get_analytics_trends(30)
    if not trends.get("error") and trends.get("daily_volume"):
        fig = threat_trend_chart(trends["daily_volume"])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No trend data available")

with col2:
    severity_data = overview.get("threats_by_severity", {})
    if severity_data:
        fig = threats_by_severity_chart(severity_data)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No severity data available")

# Top Categories
type_data = overview.get("threats_by_type", {})
if type_data:
    st.markdown("### 📂 Top Threat Categories")
    fig = top_categories_chart(type_data, height=300)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# Recent threats
st.markdown("### 🔄 Recent Threat Feed")
recent = api_client.get_threats(limit=6)
if not recent.get("error") and recent.get("threats"):
    for threat in recent["threats"]:
        render_threat_card(threat)
else:
    st.info("No threats yet")
