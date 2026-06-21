"""
SentinelX Threat Card Component
Renders individual threat entries as styled cards.
"""
import streamlit as st
from frontend.utils.helpers import (
    severity_badge, source_badge, status_badge, indicator_display,
    format_date, format_relative_time, risk_score_bar
)


def render_threat_card(threat: dict, show_status: bool = False, show_actions: bool = False, key_prefix: str = ""):
    """
    Render a threat as a styled card.

    Args:
        threat: Threat data dictionary.
        show_status: Whether to show the status badge.
        show_actions: Whether to show action buttons (for admin).
        key_prefix: Prefix for unique widget keys.
    """
    severity = threat.get("severity", "Medium")
    severity_lower = severity.lower()
    border_color = {
        "critical": "#DC2626",
        "high": "#EA580C",
        "medium": "#D97706",
        "low": "#2563EB",
        "info": "#6B7280",
    }.get(severity_lower, "#CBD5E1")

    # Build card HTML
    badges_html = f'{severity_badge(severity)} {source_badge(threat.get("source", "Unknown"))}'
    if show_status:
        badges_html += f' {status_badge(threat.get("status", "Pending"))}'

    indicator_html = indicator_display(
        threat.get("indicator", "N/A"),
        threat.get("indicator_type", "")
    )

    tags = threat.get("tags", [])
    tags_html = ""
    if tags and isinstance(tags, list):
        tags_items = " ".join(
            f'<span style="display:inline-block;padding:1px 8px;border-radius:12px;'
            f'font-size:0.65rem;background:#F0F2F6;color:#475569;font-weight:500;'
            f'margin-right:4px">{tag}</span>'
            for tag in tags[:5]
        )
        tags_html = f'<div style="margin-top:8px">{tags_items}</div>'

    description = threat.get("description", "")
    if len(description) > 200:
        description = description[:200] + "..."

    card_html = f'''
    <div style="background:white;border:1px solid #E2E8F0;border-radius:12px;
        padding:1.25rem;margin-bottom:0.75rem;box-shadow:0 1px 2px rgba(0,0,0,0.05);
        border-left:4px solid {border_color};transition:all 0.25s ease">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
            <h4 style="margin:0;font-size:1rem;font-weight:700;color:#1B2A4A;flex:1">
                {threat.get("title", "Untitled Threat")}
            </h4>
            <div>{badges_html}</div>
        </div>
        <div style="margin-top:10px">{indicator_html}</div>
        <p style="margin:10px 0 0 0;font-size:0.85rem;color:#64748B;line-height:1.5">
            {description}
        </p>
        {tags_html}
        <div style="display:flex;justify-content:space-between;align-items:center;
            margin-top:12px;padding-top:10px;border-top:1px solid #F0F2F6">
            <span style="font-size:0.75rem;color:#94A3B8">
                {format_relative_time(threat.get("created_at"))}
            </span>
            <span style="font-size:0.75rem;color:#94A3B8">
                Risk: <strong style="color:{_risk_color(threat.get("risk_score", 5.0))}">
                {threat.get("risk_score", 5.0):.1f}/10</strong>
            </span>
        </div>
    </div>
    '''

    st.markdown(card_html, unsafe_allow_html=True)


def render_threat_detail(threat: dict):
    """Render a detailed view of a threat."""
    severity = threat.get("severity", "Medium")

    # Header
    st.markdown(
        f'<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:1rem">'
        f'{severity_badge(severity)} {source_badge(threat.get("source", "Unknown"))} '
        f'{status_badge(threat.get("status", "Approved"))}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Metadata grid
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Indicator Type**")
        st.markdown(f'`{threat.get("indicator_type", "Unknown")}`')
    with col2:
        st.markdown("**Created**")
        st.markdown(format_date(threat.get("created_at")))
    with col3:
        st.markdown("**Risk Score**")
        st.markdown(
            risk_score_bar(threat.get("risk_score", 5.0)),
            unsafe_allow_html=True,
        )

    # Indicator
    st.markdown("---")
    st.markdown("**Indicator**")
    st.markdown(
        indicator_display(threat.get("indicator", "N/A"), threat.get("indicator_type", "")),
        unsafe_allow_html=True,
    )

    # Description
    if threat.get("description"):
        st.markdown("---")
        st.markdown("**Description**")
        st.markdown(threat["description"])

    # Tags
    tags = threat.get("tags", [])
    if tags:
        st.markdown("---")
        st.markdown("**Tags**")
        tags_html = " ".join(
            f'<span style="display:inline-block;padding:3px 12px;border-radius:20px;'
            f'font-size:0.75rem;background:#F0F2F6;color:#475569;font-weight:500;'
            f'margin:2px">{tag}</span>'
            for tag in tags
        )
        st.markdown(tags_html, unsafe_allow_html=True)

    # Reference
    ref = threat.get("reference_url")
    if ref:
        st.markdown("---")
        st.markdown(f"**Reference**: [{ref}]({ref})")


def _risk_color(score: float) -> str:
    """Get color for risk score."""
    if score >= 9.0:
        return "#DC2626"
    elif score >= 7.0:
        return "#EA580C"
    elif score >= 4.0:
        return "#D97706"
    elif score >= 2.0:
        return "#2563EB"
    return "#6B7280"
