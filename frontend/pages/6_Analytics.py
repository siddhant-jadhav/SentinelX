"""
SentinelX — Analytics Page
Threat intelligence analytics and statistics dashboard.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

st.set_page_config(page_title="SentinelX — Analytics", page_icon="📈", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from frontend.components.sidebar import render_sidebar
from frontend.components.metric_card import render_metric_cards
from frontend.components.charts import (
    threats_by_type_chart, threats_by_severity_chart,
    daily_volume_chart, community_pie_chart
)
from frontend.utils.helpers import page_header
from frontend.utils import api_client

render_sidebar()

st.markdown(
    page_header("Analytics", "Threat intelligence statistics and trend analysis", "📈"),
    unsafe_allow_html=True,
)

# Fetch data
overview = api_client.get_analytics_overview()
trends = api_client.get_analytics_trends(30)
community = api_client.get_community_stats()

if overview.get("error"):
    st.warning("⚠️ Unable to connect to backend API.")
    st.stop()

# ── Overview Metrics ─────────────────────────────────────────────
render_metric_cards([
    {"label": "Total Threats", "value": overview.get("total_threats", 0), "icon": "🎯", "color": "#0A84FF"},
    {"label": "Pending Review", "value": overview.get("pending_count", 0), "icon": "⏳", "color": "#F59E0B"},
    {"label": "Approved", "value": overview.get("approved_count", 0), "icon": "✅", "color": "#10B981"},
    {"label": "Rejected", "value": overview.get("rejected_count", 0), "icon": "❌", "color": "#EF4444"},
])

st.markdown("<br>", unsafe_allow_html=True)

# ── Chart Row 1: Type + Severity ─────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    type_data = overview.get("threats_by_type", {})
    if type_data:
        fig = threats_by_type_chart(type_data)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No type data available")

with col2:
    severity_data = overview.get("threats_by_severity", {})
    if severity_data:
        fig = threats_by_severity_chart(severity_data)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No severity data available")

# ── Chart Row 2: Daily Volume ────────────────────────────────────
st.markdown("---")

if not trends.get("error") and trends.get("daily_volume"):
    # Period selector
    period = st.selectbox(
        "Time Period",
        ["Last 30 Days", "Last 14 Days", "Last 7 Days"],
        label_visibility="collapsed",
    )

    period_map = {"Last 30 Days": 30, "Last 14 Days": 14, "Last 7 Days": 7}
    days = period_map.get(period, 30)

    # Re-fetch if needed
    if days != 30:
        trends = api_client.get_analytics_trends(days)

    if not trends.get("error") and trends.get("daily_volume"):
        fig = daily_volume_chart(trends["daily_volume"])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
else:
    st.info("No daily volume data available")

# ── Community Stats ──────────────────────────────────────────────
st.markdown("---")
st.markdown("### 👥 Community Contribution Statistics")

if not community.get("error"):
    col1, col2 = st.columns([1, 1])

    with col1:
        render_metric_cards([
            {
                "label": "Total Submissions",
                "value": community.get("total_submissions", 0),
                "icon": "📝",
                "color": "#8B5CF6",
            },
            {
                "label": "Approval Rate",
                "value": f"{community.get('approval_rate', 0)}%",
                "icon": "📊",
                "color": "#10B981",
            },
        ])

    with col2:
        fig = community_pie_chart(community, height=280)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Top contributors
    contributors = community.get("top_contributors", [])
    if contributors:
        st.markdown("#### 🏆 Top Contributors")
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
else:
    st.info("Community stats unavailable")
