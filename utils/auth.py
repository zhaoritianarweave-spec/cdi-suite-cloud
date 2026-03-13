"""Supabase authentication for CDI Suite Cloud."""

import streamlit as st
from supabase import create_client, Client


def _get_supabase() -> Client:
    """Get or create a Supabase client from Streamlit secrets."""
    if "supabase_client" not in st.session_state:
        st.session_state["supabase_client"] = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"],
        )
    return st.session_state["supabase_client"]


def get_user() -> dict | None:
    """Return the current logged-in user dict, or None."""
    return st.session_state.get("user")


def _do_login(email: str, password: str) -> bool:
    """Attempt login. Returns True on success."""
    try:
        sb = _get_supabase()
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state["user"] = {
            "id": res.user.id,
            "email": res.user.email,
            "created_at": str(res.user.created_at),
        }
        st.session_state["access_token"] = res.session.access_token
        return True
    except Exception as e:
        err = str(e)
        if "Invalid login" in err or "invalid" in err.lower():
            st.error("Invalid email or password.")
        else:
            st.error(f"Login failed: {err}")
        return False


def _do_signup(email: str, password: str) -> bool:
    """Attempt signup. Returns True on success."""
    try:
        sb = _get_supabase()
        res = sb.auth.sign_up({"email": email, "password": password})
        if res.user and res.user.id:
            st.success("Account created! Please check your email to confirm, then log in.")
            return True
        st.error("Signup failed. Please try again.")
        return False
    except Exception as e:
        err = str(e)
        if "already registered" in err.lower():
            st.error("This email is already registered. Please log in.")
        else:
            st.error(f"Signup failed: {err}")
        return False


def logout():
    """Clear session and log out."""
    for key in ["user", "access_token", "supabase_client"]:
        st.session_state.pop(key, None)


def render_auth_page():
    """Render the login/signup page. Returns True if user is authenticated."""
    user = get_user()
    if user:
        return True

    st.markdown(
        """
        <div style="text-align:center; padding:3rem 0 1rem 0;">
            <h1 style="font-size:2.4rem; font-weight:700; letter-spacing:2px;
                background:linear-gradient(135deg,#0A7CFF,#00D4AA);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                CDI SUITE
            </h1>
            <p style="color:#8B949E; font-size:1rem; letter-spacing:1px;">
                Civil Design Intelligence Platform
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_form, col_right = st.columns([1, 2, 1])

    with col_form:
        login_tab, signup_tab = st.tabs(["Log In", "Sign Up"])

        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@company.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log In", use_container_width=True, type="primary")
                if submitted:
                    if email and password:
                        if _do_login(email, password):
                            st.rerun()
                    else:
                        st.warning("Please enter email and password.")

        with signup_tab:
            with st.form("signup_form"):
                new_email = st.text_input("Email", placeholder="you@company.com", key="signup_email")
                new_password = st.text_input("Password", type="password", key="signup_pw",
                                             help="At least 6 characters")
                confirm_pw = st.text_input("Confirm Password", type="password", key="signup_pw2")
                signed_up = st.form_submit_button("Create Account", use_container_width=True, type="primary")
                if signed_up:
                    if not new_email or not new_password:
                        st.warning("Please fill in all fields.")
                    elif len(new_password) < 6:
                        st.warning("Password must be at least 6 characters.")
                    elif new_password != confirm_pw:
                        st.warning("Passwords do not match.")
                    else:
                        _do_signup(new_email, new_password)

        st.markdown(
            "<p style='text-align:center; color:#484F58; font-size:0.75rem; margin-top:2rem;'>"
            "CDI Suite v1.0 Cloud &middot; Powered by Generative Architecture Engine</p>",
            unsafe_allow_html=True,
        )

    return False
