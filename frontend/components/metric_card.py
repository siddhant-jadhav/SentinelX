"""
SentinelX Metric Card Component
Dashboard metric card with icon, value, and optional delta.
"""
import streamlit as st
from frontend.utils.helpers import metric_card_html


def render_metric_cards(metrics: list[dict]):
    """
    Render a row of metric cards.

    Args:
        metrics: List of dicts with keys: label, value, icon, color, delta (optional).
    """
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            html = metric_card_html(
                label=metric.get("label", ""),
                value=metric.get("value", 0),
                icon=metric.get("icon", "📊"),
                color=metric.get("color", "#0A84FF"),
                delta=metric.get("delta", ""),
            )
            st.markdown(html, unsafe_allow_html=True)


def render_stat_row(stats: dict):
    """
    Render a quick stat row from a dictionary.

    Args:
        stats: Dictionary of label -> value pairs.
    """
    cols = st.columns(len(stats))
    for col, (label, value) in zip(cols, stats.items()):
        with col:
            st.metric(label=label, value=value)
