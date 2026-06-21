"""
SentinelX — Admin Panel Page
Admin-only interface for reviewing, approving, and managing threats.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

st.set_page_config(page_title="SentinelX — Admin", page_icon="⚙️", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from frontend.components.sidebar import render_sidebar
from frontend.components.auth_ui import require_login, is_admin
from frontend.components.threat_card import render_threat_card
from frontend.utils.helpers import page_header, severity_badge, source_badge, status_badge, indicator_display
from frontend.utils import api_client

render_sidebar()

st.markdown(
    page_header("Admin Panel", "Manage threats, review submissions, and moderate content", "⚙️"),
    unsafe_allow_html=True,
)

# Auth check
if not require_login():
    st.stop()

if not is_admin():
    st.error("🔒 **Access Denied** — This page requires admin privileges.")
    st.markdown(
        "You are logged in as a regular user. Admin credentials: **admin / SentinelX@2024**"
    )
    st.stop()

# ── Admin Stats ──────────────────────────────────────────────────
from frontend.components.metric_card import render_metric_cards

overview = api_client.get_analytics_overview()
if not overview.get("error"):
    render_metric_cards([
        {"label": "Pending", "value": overview.get("pending_count", 0), "icon": "⏳", "color": "#F59E0B"},
        {"label": "Approved", "value": overview.get("approved_count", 0), "icon": "✅", "color": "#10B981"},
        {"label": "Rejected", "value": overview.get("rejected_count", 0), "icon": "❌", "color": "#EF4444"},
        {"label": "Total", "value": overview.get("total_threats", 0), "icon": "📊", "color": "#0A84FF"},
    ])

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────
tab_pending, tab_all, tab_sync = st.tabs([
    "⏳ Pending Review",
    "📋 All Threats",
    "🔄 OTX Sync"
])

# ── Pending Review Tab ───────────────────────────────────────────
with tab_pending:
    st.markdown("### Pending Community Submissions")

    pending_data = api_client.get_threats(status="Pending", source="Community", limit=50)

    if pending_data.get("error"):
        st.warning("Unable to fetch pending threats")
    else:
        pending = pending_data.get("threats", [])

        if not pending:
            st.success("🎉 No pending submissions! All caught up.")
        else:
            st.markdown(
                f'<p style="color:#64748B;font-size:0.85rem">'
                f'<strong>{len(pending)}</strong> submission(s) awaiting review</p>',
                unsafe_allow_html=True,
            )

            for threat in pending:
                threat_id = threat.get("id")

                with st.expander(
                    f"{'🔴' if threat.get('severity') == 'Critical' else '🟠' if threat.get('severity') == 'High' else '🟡'} "
                    f"{threat.get('title', 'Untitled')} — {threat.get('indicator', '')}",
                    expanded=True,
                ):
                    # Display threat info
                    st.markdown(
                        f'{severity_badge(threat.get("severity", "Medium"))} '
                        f'{source_badge(threat.get("source", "Community"))} '
                        f'{status_badge(threat.get("status", "Pending"))}',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        indicator_display(threat.get("indicator", ""), threat.get("indicator_type", "")),
                        unsafe_allow_html=True,
                    )
                    st.markdown(f'**Type:** {threat.get("indicator_type", "Unknown")}')
                    st.markdown(f'**Description:** {threat.get("description", "No description")}')

                    if threat.get("reference_url"):
                        st.markdown(f'**Reference:** [{threat["reference_url"]}]({threat["reference_url"]})')

                    tags = threat.get("tags", [])
                    if tags:
                        st.markdown(f'**Tags:** {", ".join(tags)}')

                    # Action buttons
                    col_a, col_r, col_d = st.columns(3)

                    with col_a:
                        if st.button("✅ Approve", key=f"approve_{threat_id}", use_container_width=True):
                            result = api_client.update_threat(threat_id, {"status": "Approved"})
                            if result.get("error"):
                                st.error(f"Failed: {result.get('detail')}")
                            else:
                                st.success("Threat approved!")
                                st.rerun()

                    with col_r:
                        if st.button("❌ Reject", key=f"reject_{threat_id}", use_container_width=True):
                            result = api_client.update_threat(threat_id, {"status": "Rejected"})
                            if result.get("error"):
                                st.error(f"Failed: {result.get('detail')}")
                            else:
                                st.warning("Threat rejected.")
                                st.rerun()

                    with col_d:
                        if st.button("🗑️ Delete", key=f"delete_pending_{threat_id}", use_container_width=True):
                            result = api_client.delete_threat(threat_id)
                            if result.get("error"):
                                st.error(f"Failed: {result.get('detail')}")
                            else:
                                st.info("Threat deleted.")
                                st.rerun()

# ── All Threats Tab ──────────────────────────────────────────────
with tab_all:
    st.markdown("### All Threats Management")

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        status_filter = st.selectbox("Status", ["All", "Approved", "Pending", "Rejected"], key="admin_status")
    with col_f2:
        source_filter = st.selectbox("Source", ["All", "OTX", "Community"], key="admin_source")
    with col_f3:
        severity_filter = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low", "Info"], key="admin_severity")

    params = {"limit": 50}
    if status_filter != "All":
        params["status"] = status_filter
    if source_filter != "All":
        params["source"] = source_filter
    if severity_filter != "All":
        params["severity"] = severity_filter

    all_data = api_client.get_threats(**params)

    if all_data.get("error"):
        st.warning("Unable to fetch threats")
    else:
        all_threats = all_data.get("threats", [])

        if all_threats:
            st.markdown(
                f'<p style="color:#64748B;font-size:0.85rem">'
                f'Showing <strong>{len(all_threats)}</strong> threats</p>',
                unsafe_allow_html=True,
            )

            for threat in all_threats:
                threat_id = threat.get("id")

                with st.expander(
                    f"{threat.get('title', 'Untitled')} — [{threat.get('status', '')}]",
                    expanded=False,
                ):
                    # Display badges
                    st.markdown(
                        f'{severity_badge(threat.get("severity", "Medium"))} '
                        f'{source_badge(threat.get("source", ""))} '
                        f'{status_badge(threat.get("status", ""))}',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        indicator_display(threat.get("indicator", ""), threat.get("indicator_type", "")),
                        unsafe_allow_html=True,
                    )

                    # Editable fields
                    st.markdown("---")
                    st.markdown("**Edit Threat:**")

                    new_title = st.text_input("Title", value=threat.get("title", ""), key=f"edit_title_{threat_id}")
                    new_severity = st.selectbox(
                        "Severity",
                        ["Critical", "High", "Medium", "Low", "Info"],
                        index=["Critical", "High", "Medium", "Low", "Info"].index(threat.get("severity", "Medium")),
                        key=f"edit_sev_{threat_id}",
                    )
                    new_status = st.selectbox(
                        "Status",
                        ["Pending", "Approved", "Rejected"],
                        index=["Pending", "Approved", "Rejected"].index(threat.get("status", "Pending")),
                        key=f"edit_status_{threat_id}",
                    )
                    new_desc = st.text_area(
                        "Description",
                        value=threat.get("description", ""),
                        key=f"edit_desc_{threat_id}",
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save Changes", key=f"save_{threat_id}", use_container_width=True):
                            update_data = {
                                "title": new_title,
                                "severity": new_severity,
                                "status": new_status,
                                "description": new_desc,
                            }
                            result = api_client.update_threat(threat_id, update_data)
                            if result.get("error"):
                                st.error(f"Update failed: {result.get('detail')}")
                            else:
                                st.success("Threat updated!")
                                st.rerun()

                    with col2:
                        if st.button("🗑️ Delete", key=f"del_{threat_id}", use_container_width=True):
                            result = api_client.delete_threat(threat_id)
                            if result.get("error"):
                                st.error(f"Delete failed: {result.get('detail')}")
                            else:
                                st.info("Threat deleted.")
                                st.rerun()
        else:
            st.info("No threats match the current filters.")

# ── OTX Sync Tab ─────────────────────────────────────────────────
with tab_sync:
    st.markdown("### 🔄 Sync from AlienVault OTX")

    # OTX Status
    otx_status = api_client.get_otx_status()
    if not otx_status.get("error"):
        mode = otx_status.get("mode", "demo")
        mode_color = "#10B981" if mode == "live" else "#F59E0B"
        st.markdown(
            f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;'
            f'padding:1rem 1.5rem;margin-bottom:1rem">'
            f'<div style="display:flex;align-items:center;gap:8px">'
            f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
            f'background:{mode_color}"></span>'
            f'<span style="font-weight:600;color:#1B2A4A">{otx_status.get("message", "")}</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    sync_limit = st.slider("Number of pulses to sync", 5, 50, 20)

    if st.button("🔄 Sync Now", use_container_width=True, type="primary"):
        with st.spinner("Syncing from OTX..."):
            result = api_client.sync_otx(sync_limit)

        if result.get("error"):
            st.error(f"Sync failed: {result.get('detail')}")
        else:
            st.success(
                f"✅ {result.get('message', 'Sync complete')} "
                f"({result.get('skipped', 0)} duplicates skipped)"
            )
            st.rerun()

    # Show latest OTX pulses
    st.markdown("---")
    st.markdown("#### Latest OTX Pulses (Preview)")

    otx_latest = api_client.get_otx_latest(10)
    if not otx_latest.get("error"):
        pulses = otx_latest.get("pulses", [])
        source_mode = otx_latest.get("source", "demo")

        st.markdown(
            f'<p style="color:#94A3B8;font-size:0.8rem">Source: <strong>{source_mode}</strong></p>',
            unsafe_allow_html=True,
        )

        for pulse in pulses:
            render_threat_card(pulse)
    else:
        st.info("Unable to fetch OTX pulses")
