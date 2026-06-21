"""
SentinelX — Submit Threat Page
Form for submitting community threat intelligence.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

st.set_page_config(page_title="SentinelX — Submit Threat", page_icon="📤", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from frontend.components.sidebar import render_sidebar
from frontend.components.auth_ui import require_login, is_authenticated
from frontend.components.threat_card import render_threat_card
from frontend.utils.helpers import page_header, status_badge
from frontend.utils import api_client

render_sidebar()

st.markdown(
    page_header("Submit Threat", "Contribute threat intelligence to the SentinelX community", "📤"),
    unsafe_allow_html=True,
)

# Require authentication
if not require_login():
    st.stop()

# ── Submission Form ──────────────────────────────────────────────
st.markdown("### 📝 New Threat Submission")

with st.form("submit_threat_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input(
            "Threat Title *",
            placeholder="e.g., Suspicious C2 Domain Activity",
        )
        indicator = st.text_input(
            "Indicator *",
            placeholder="e.g., 192.168.1.100, malicious-domain.com, hash...",
        )
        indicator_type = st.selectbox(
            "Indicator Type *",
            ["IPv4", "IPv6", "Domain", "Hostname", "URL",
             "FileHash-MD5", "FileHash-SHA1", "FileHash-SHA256", "Email", "CIDR"],
        )

    with col2:
        severity = st.selectbox(
            "Severity *",
            ["Medium", "Critical", "High", "Low", "Info"],
        )
        reference_url = st.text_input(
            "Reference URL",
            placeholder="https://... (optional)",
        )
        tags_input = st.text_input(
            "Tags",
            placeholder="malware, phishing, C2 (comma-separated)",
        )

    description = st.text_area(
        "Description *",
        placeholder="Provide details about this threat indicator including context, impact, and any observed behavior...",
        height=150,
    )

    # Submission info
    st.markdown(
        '<div style="background:#F0F2F6;border-radius:8px;padding:0.75rem 1rem;margin:0.5rem 0">'
        '<span style="font-size:0.8rem;color:#64748B">'
        '📌 Submissions start with <strong>Pending</strong> status and require admin approval '
        'before appearing in the public feed.</span></div>',
        unsafe_allow_html=True,
    )

    submitted = st.form_submit_button("🚀 Submit Threat", use_container_width=True)

    if submitted:
        # Validation
        errors = []
        if not title or len(title) < 3:
            errors.append("Title must be at least 3 characters")
        if not indicator:
            errors.append("Indicator is required")
        if not description:
            errors.append("Description is required")

        if errors:
            for err in errors:
                st.error(err)
        else:
            tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []

            result = api_client.create_threat({
                "title": title,
                "indicator": indicator,
                "indicator_type": indicator_type,
                "severity": severity,
                "description": description,
                "reference_url": reference_url or "",
                "tags": tags,
            })

            if result.get("error"):
                st.error(f"Submission failed: {result.get('detail', 'Unknown error')}")
            else:
                st.success("✅ Threat submitted successfully! It will be reviewed by an admin.")
                st.balloons()

# ── My Submissions ───────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 My Recent Submissions")

# Fetch all threats to filter by current user (simplified approach)
if is_authenticated():
    user = st.session_state.get("user", {})
    all_threats = api_client.get_threats(source="Community", limit=50)

    if not all_threats.get("error"):
        my_threats = [
            t for t in all_threats.get("threats", [])
            if t.get("submitted_by") == user.get("id")
        ]

        if my_threats:
            for threat in my_threats:
                render_threat_card(threat, show_status=True)
        else:
            st.info("You haven't submitted any threats yet. Use the form above to contribute!")
