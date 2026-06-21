"""
SentinelX — Search Page
Search for threat indicators across local database and OTX API.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

st.set_page_config(page_title="SentinelX — Search", page_icon="🔍", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from frontend.components.sidebar import render_sidebar
from frontend.utils.helpers import (
    page_header, severity_badge, source_badge, indicator_display
)
from frontend.utils import api_client

render_sidebar()

st.markdown(
    page_header("Threat Search", "Search for indicators across OTX and local threat database", "🔍"),
    unsafe_allow_html=True,
)


# ── Helper: Render search result card ────────────────────────────
def _render_search_result(result: dict):
    """Render a single search result as a styled card."""
    severity = result.get("severity", "Medium")
    border_color = {
        "Critical": "#DC2626", "High": "#EA580C", "Medium": "#D97706",
        "Low": "#2563EB", "Info": "#6B7280",
    }.get(severity, "#CBD5E1")

    badges = f'{severity_badge(severity)} {source_badge(result.get("source", "Unknown"))}'
    ind = indicator_display(result.get("indicator", "N/A"), result.get("indicator_type", ""))

    description = result.get("description", "")
    if len(description) > 300:
        description = description[:300] + "..."

    ref_html = ""
    ref = result.get("reference_url")
    if ref:
        ref_html = (
            f'<a href="{ref}" target="_blank" style="color:#0A84FF;font-size:0.8rem;'
            f'text-decoration:none">🔗 Reference</a>'
        )

    html = f'''
    <div style="background:white;border:1px solid #E2E8F0;border-radius:12px;
        padding:1.25rem;margin-bottom:0.75rem;box-shadow:0 1px 2px rgba(0,0,0,0.05);
        border-left:4px solid {border_color}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;
            flex-wrap:wrap;gap:8px">
            <h4 style="margin:0;font-size:0.95rem;font-weight:700;color:#1B2A4A;flex:1">
                {result.get("title", "Search Result")}</h4>
            <div>{badges}</div>
        </div>
        <div style="margin-top:8px">{ind}</div>
        <p style="margin:8px 0 0 0;font-size:0.85rem;color:#64748B;line-height:1.5">
            {description}</p>
        <div style="display:flex;justify-content:space-between;align-items:center;
            margin-top:10px;padding-top:8px;border-top:1px solid #F0F2F6">
            {ref_html}
            <span style="font-size:0.75rem;color:#94A3B8">
                Risk: <strong>{result.get("risk_score", 5.0):.1f}/10</strong>
            </span>
        </div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


# ── Search Form ──────────────────────────────────────────────────
col_search, col_type = st.columns([4, 1.5])

with col_search:
    search_query = st.text_input(
        "Search Indicator",
        placeholder="Enter IP address, domain, URL, or file hash...",
        label_visibility="collapsed",
    )

with col_type:
    indicator_type = st.selectbox(
        "Type",
        ["Auto-Detect", "IPv4", "IPv6", "Domain", "URL",
         "FileHash-MD5", "FileHash-SHA1", "FileHash-SHA256", "Email"],
        label_visibility="collapsed",
    )

search_btn = st.button("🔍 Search", use_container_width=False, type="primary")

# Example queries
st.markdown(
    '<div style="margin-top:0.5rem;margin-bottom:1.5rem">'
    '<span style="color:#94A3B8;font-size:0.8rem">Try: </span>'
    '<code style="font-size:0.75rem;background:#F0F2F6;padding:2px 8px;'
    'border-radius:4px;margin:0 4px">185.141.63.120</code>'
    '<code style="font-size:0.75rem;background:#F0F2F6;padding:2px 8px;'
    'border-radius:4px;margin:0 4px">avsvmcloud.com</code>'
    '<code style="font-size:0.75rem;background:#F0F2F6;padding:2px 8px;'
    'border-radius:4px;margin:0 4px">a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6</code>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Search Results ───────────────────────────────────────────────
if search_btn and search_query:
    # Track search history
    if "search_history" not in st.session_state:
        st.session_state["search_history"] = []
    if search_query not in st.session_state["search_history"]:
        st.session_state["search_history"].insert(0, search_query)
        st.session_state["search_history"] = st.session_state["search_history"][:10]

    with st.spinner("Searching across local database and OTX..."):
        type_param = None if indicator_type == "Auto-Detect" else indicator_type
        results = api_client.search_indicators(search_query, type_param)

    if results.get("error"):
        st.error(f"Search failed: {results.get('detail', 'Unknown error')}")
    else:
        total = results.get("total_results", 0)
        detected_type = results.get("query_type", "Unknown")

        # Result summary bar
        st.markdown(
            f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;'
            f'padding:1rem 1.5rem;margin-bottom:1.5rem">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<div>'
            f'<span style="font-size:0.85rem;color:#64748B">Searching for </span>'
            f'<code style="font-family:JetBrains Mono,monospace;font-size:0.9rem;color:#1B2A4A;'
            f'background:#E2E8F0;padding:2px 8px;border-radius:4px;font-weight:600">'
            f'{search_query}</code>'
            f'<span style="font-size:0.85rem;color:#64748B"> as </span>'
            f'<span style="font-weight:600;color:#0A84FF">{detected_type}</span>'
            f'</div>'
            f'<div style="font-size:0.9rem;font-weight:700;color:#1B2A4A">'
            f'{total} result{"s" if total != 1 else ""}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        local_results = results.get("local_results", [])
        otx_results = results.get("otx_results", [])

        tab_local, tab_otx = st.tabs([
            f"🗄️ Local Database ({len(local_results)})",
            f"🛡️ OTX Results ({len(otx_results)})",
        ])

        with tab_local:
            if local_results:
                for r in local_results:
                    _render_search_result(r)
            else:
                st.info("No matching indicators found in the local database.")

        with tab_otx:
            if otx_results:
                for r in otx_results:
                    _render_search_result(r)
            else:
                st.info("No matching indicators found in OTX.")

elif search_btn:
    st.warning("Please enter a search query.")

# ── Search History in Sidebar ────────────────────────────────────
if st.session_state.get("search_history"):
    with st.sidebar:
        st.markdown("---")
        st.markdown("#### 🕐 Recent Searches")
        for q in st.session_state["search_history"][:5]:
            st.markdown(
                f'<code style="font-size:0.75rem;color:#94A3B8">{q}</code>',
                unsafe_allow_html=True,
            )
