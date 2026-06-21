"""
SentinelX — Threat Feed Page
Unified feed of all threats from OTX and Community sources.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

st.set_page_config(page_title="SentinelX — Threat Feed", page_icon="📡", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from frontend.components.sidebar import render_sidebar
from frontend.components.threat_card import render_threat_card
from frontend.utils.helpers import (
    page_header, severity_badge, source_badge, indicator_display,
    format_relative_time
)
from frontend.utils import api_client

render_sidebar()

st.markdown(
    page_header("Threat Feed", "Unified threat intelligence from OTX and Community sources", "📡"),
    unsafe_allow_html=True,
)

# ── Filter Bar ───────────────────────────────────────────────────
col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1.5, 1.5, 1.5])

with col_f1:
    search_query = st.text_input(
        "🔍 Search threats",
        placeholder="Search by title, indicator, or description...",
        label_visibility="collapsed",
    )

with col_f2:
    source_filter = st.selectbox(
        "Source", ["All Sources", "OTX", "Community"], label_visibility="collapsed"
    )

with col_f3:
    severity_filter = st.selectbox(
        "Severity",
        ["All Severities", "Critical", "High", "Medium", "Low", "Info"],
        label_visibility="collapsed",
    )

with col_f4:
    type_filter = st.selectbox(
        "Type",
        ["All Types", "IPv4", "IPv6", "Domain", "URL",
         "FileHash-MD5", "FileHash-SHA1", "FileHash-SHA256", "Email", "Hostname"],
        label_visibility="collapsed",
    )

# Pagination state
if "feed_page" not in st.session_state:
    st.session_state["feed_page"] = 1

# Build query params
params = {
    "page": st.session_state["feed_page"],
    "limit": 15,
}
if source_filter != "All Sources":
    params["source"] = source_filter
if severity_filter != "All Severities":
    params["severity"] = severity_filter
if type_filter != "All Types":
    params["indicator_type"] = type_filter
if search_query:
    params["search"] = search_query

# Fetch data
data = api_client.get_threats(**params)

if data.get("error"):
    st.warning("⚠️ Unable to connect to backend API.")
    st.stop()

threats = data.get("threats", [])
total = data.get("total", 0)
pages = data.get("pages", 1)

# Results count
st.markdown(
    f'<div style="display:flex;justify-content:space-between;align-items:center;'
    f'margin-bottom:1rem">'
    f'<span style="color:#64748B;font-size:0.85rem">'
    f'Showing <strong>{len(threats)}</strong> of <strong>{total}</strong> threats</span>'
    f'<span style="color:#94A3B8;font-size:0.8rem">'
    f'Page {st.session_state["feed_page"]} of {pages}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Threat Cards ─────────────────────────────────────────────────
if threats:
    for threat in threats:
        render_threat_card(threat)
else:
    st.info("No threats match your current filters. Try adjusting the search criteria.")

# ── Pagination Controls ──────────────────────────────────────────
if pages > 1:
    st.markdown("---")
    col_prev, col_info, col_next = st.columns([1, 2, 1])

    with col_prev:
        if st.session_state["feed_page"] > 1:
            if st.button("← Previous", key="prev_page", use_container_width=True):
                st.session_state["feed_page"] -= 1
                st.rerun()

    with col_info:
        st.markdown(
            f'<p style="text-align:center;color:#94A3B8;font-size:0.85rem;'
            f'margin-top:0.5rem">'
            f'Page {st.session_state["feed_page"]} of {pages}</p>',
            unsafe_allow_html=True,
        )

    with col_next:
        if st.session_state["feed_page"] < pages:
            if st.button("Next →", key="next_page", use_container_width=True):
                st.session_state["feed_page"] += 1
                st.rerun()
