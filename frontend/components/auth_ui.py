"""
SentinelX Auth UI Component
Login and registration forms for the Streamlit frontend.
"""
import streamlit as st
from frontend.utils import api_client


def render_login_form():
    """Render the login form in the main content area."""
    st.markdown(
        '''
        <div style="text-align:center;padding:2rem 0">
            <div style="font-size:3rem;margin-bottom:0.5rem">🛡️</div>
            <h2 style="color:#1B2A4A!important;font-weight:800!important;margin:0!important">
                Welcome to SentinelX
            </h2>
            <p style="color:#64748B;font-size:0.95rem;margin-top:0.5rem">
                Sign in to access threat intelligence features
            </p>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Register"])

    with tab1:
        with st.form("login_form"):
            st.markdown("#### Sign In")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            col1, col2 = st.columns([1, 1])
            with col1:
                submit = st.form_submit_button("Sign In", use_container_width=True)

            if submit:
                if not username or not password:
                    st.error("Please fill in all fields")
                else:
                    result = api_client.login(username, password)
                    if result.get("error"):
                        st.error(f"Login failed: {result.get('detail', 'Unknown error')}")
                    else:
                        st.session_state["token"] = result["access_token"]
                        st.session_state["user"] = result["user"]
                        st.success("Login successful!")
                        st.rerun()

        st.markdown(
            '<p style="color:#94A3B8;font-size:0.8rem;text-align:center;margin-top:1rem">'
            'Demo credentials: <strong>admin / SentinelX@2024</strong> or '
            '<strong>analyst / analyst123</strong></p>',
            unsafe_allow_html=True,
        )

    with tab2:
        with st.form("register_form"):
            st.markdown("#### Create Account")
            reg_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
            reg_email = st.text_input("Email", key="reg_email", placeholder="your@email.com")
            reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Min 6 characters")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Re-enter password")

            register_btn = st.form_submit_button("Create Account", use_container_width=True)

            if register_btn:
                if not all([reg_username, reg_email, reg_password, reg_confirm]):
                    st.error("Please fill in all fields")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    result = api_client.register(reg_username, reg_email, reg_password)
                    if result.get("error"):
                        st.error(f"Registration failed: {result.get('detail', 'Unknown error')}")
                    else:
                        st.session_state["token"] = result["access_token"]
                        st.session_state["user"] = result["user"]
                        st.success("Account created successfully!")
                        st.rerun()


def is_authenticated() -> bool:
    """Check if user is currently authenticated."""
    return bool(st.session_state.get("token"))


def is_admin() -> bool:
    """Check if current user has admin role."""
    user = st.session_state.get("user", {})
    return user.get("role") == "admin"


def require_login():
    """Show login form if not authenticated. Returns True if authenticated."""
    if not is_authenticated():
        render_login_form()
        return False
    return True
