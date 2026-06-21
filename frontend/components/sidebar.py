"""
SentinelX Sidebar Component
Light-themed branded sidebar with navigation, user info, and OTX status.
"""
import streamlit as st


def render_sidebar():
    """Render the light-themed branded sidebar."""
    with st.sidebar:
        # Branding
        st.markdown(
            '''
            <div style="text-align:center;padding:1rem 0 0.5rem 0">
                <div style="font-size:2rem;margin-bottom:4px">🛡️</div>
                <h1 style="color:#1B2A4A!important;font-size:1.4rem!important;margin:0!important;
                    font-weight:800!important;letter-spacing:-0.02em">SentinelX</h1>
                <p style="color:#94A3B8!important;font-size:0.7rem!important;margin:4px 0 0 0!important;
                    text-transform:uppercase;letter-spacing:0.1em">
                    Threat Intelligence Platform
                </p>
            </div>
            ''',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # User info
        if st.session_state.get("user"):
            user = st.session_state["user"]
            role_color = "#F59E0B" if user.get("role") == "admin" else "#0A84FF"
            role_badge = "🔑 Admin" if user.get("role") == "admin" else "👤 Analyst"

            st.markdown(
                f'''
                <div style="background:#F0F2F6;border:1px solid #E2E8F0;border-radius:10px;
                    padding:0.75rem;margin-bottom:0.5rem">
                    <div style="color:#1B2A4A;font-weight:600;font-size:0.9rem">
                        {user.get("username", "User")}
                    </div>
                    <div style="color:{role_color};font-size:0.75rem;font-weight:500;margin-top:2px">
                        {role_badge}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

            if st.button("🚪 Logout", key="sidebar_logout", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        else:
            st.markdown(
                '<p style="color:#94A3B8!important;font-size:0.8rem!important;text-align:center">'
                'Login to submit threats</p>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # OTX Status
        st.markdown(
            '''
            <div style="background:#F0F2F6;border:1px solid #E2E8F0;border-radius:8px;
                padding:0.6rem;margin-top:0.5rem">
                <div style="font-size:0.7rem;color:#94A3B8;text-transform:uppercase;
                    letter-spacing:0.05em;margin-bottom:4px">OTX Integration</div>
                <div style="color:#10B981;font-size:0.8rem;font-weight:500">
                    <span style="display:inline-block;width:6px;height:6px;border-radius:50%;
                        background:#10B981;margin-right:6px"></span>
                    Connected
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

        # Footer
        st.markdown(
            '''
            <div style="text-align:center;padding:2rem 0 0.5rem 0">
                <p style="color:#CBD5E1!important;font-size:0.65rem!important;margin:0!important">
                    SentinelX v1.0.0 • Powered by AlienVault OTX
                </p>
            </div>
            ''',
            unsafe_allow_html=True,
        )
