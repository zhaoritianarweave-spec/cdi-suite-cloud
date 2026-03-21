"""Supabase authentication for CDI Suite Cloud."""

import streamlit as st
from pathlib import Path
from supabase import create_client, Client
from utils.i18n import t, t_fmt, get_region

_ASSETS_UI = Path(__file__).resolve().parent.parent / "assets" / "ui"


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
            st.error(t("err_invalid_login"))
        else:
            st.error(f"Login failed: {err}")
        return False


def _do_signup(email: str, password: str) -> bool:
    """Attempt signup. Returns True on success."""
    try:
        sb = _get_supabase()
        res = sb.auth.sign_up({"email": email, "password": password})
        if res.user and res.user.id:
            st.success(t("msg_account_created"))
            # Send welcome email (non-blocking)
            try:
                from utils.email_service import send_welcome_email
                send_welcome_email(email)
            except Exception:
                pass
            return True
        st.error("Signup failed. Please try again.")
        return False
    except Exception as e:
        err = str(e)
        if "already registered" in err.lower():
            st.error(t("err_already_registered"))
        else:
            st.error(f"Signup failed: {err}")
        return False


def logout():
    """Clear session and log out."""
    for key in ["user", "access_token", "supabase_client"]:
        st.session_state.pop(key, None)


def _do_reset_password(email: str) -> bool:
    """Send password reset email."""
    try:
        sb = _get_supabase()
        sb.auth.reset_password_email(email)
        return True
    except Exception as e:
        st.error(f"Failed to send reset email: {e}")
        return False


def _render_lang_toggle():
    """Render a compact language + region toggle at the top-right of the page."""
    _, region_col, lang_col = st.columns([5, 1, 1])
    with region_col:
        regions = ["Australia", "China"]
        cur_r = 1 if st.session_state.get("region") == "cn" else 0
        region_choice = st.selectbox("🌏", regions, index=cur_r, key="region_select_auth", label_visibility="collapsed")
        st.session_state["region"] = "cn" if region_choice == "China" else "au"
    with lang_col:
        langs = ["English", "中文"]
        cur = 1 if st.session_state.get("lang") == "zh" else 0
        choice = st.selectbox("🌐", langs, index=cur, key="lang_select_auth", label_visibility="collapsed")
        st.session_state["lang"] = "zh" if choice == "中文" else "en"


def render_auth_page():
    """Render the landing page with product intro + login/signup. Returns True if user is authenticated."""
    user = get_user()
    if user:
        return True

    _render_lang_toggle()

    # --- Hero Image + Title ---
    st.image(str(_ASSETS_UI / "hero.png"), use_container_width=True)

    st.markdown(
        f"""
        <div style="text-align:center; padding:1rem 0 0.5rem 0;">
            <h1 style="font-size:2.6rem; font-weight:700; letter-spacing:2px;
                background:linear-gradient(135deg,#0A7CFF,#00D4AA);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                margin-bottom:0.3rem;">
                {t("hero_title")}
            </h1>
            <p style="color:#C9D1D9; font-size:1.15rem; letter-spacing:1px; margin-bottom:0.2rem;">
                {t("hero_subtitle")}
            </p>
            <p style="color:#8B949E; font-size:0.9rem;">
                {t("hero_caption")}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Feature Cards with Images ---
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)

    with f1:
        st.image(str(_ASSETS_UI / "site_renderer.png"), use_container_width=True)
        st.markdown(
            f"<div style='text-align:center; padding:0.5rem 0;'>"
            f"<h4 style='color:#58A6FF; margin:0 0 0.3rem 0; font-size:0.95rem;'>{t('feat_renderer_title')}</h4>"
            f"<p style='color:#8B949E; font-size:0.8rem; line-height:1.4;'>{t('feat_renderer_desc')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with f2:
        st.image(str(_ASSETS_UI / "drawing_analyser.png"), use_container_width=True)
        st.markdown(
            f"<div style='text-align:center; padding:0.5rem 0;'>"
            f"<h4 style='color:#58A6FF; margin:0 0 0.3rem 0; font-size:0.95rem;'>{t('feat_analyser_title')}</h4>"
            f"<p style='color:#8B949E; font-size:0.8rem; line-height:1.4;'>{t('feat_analyser_desc')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with f3:
        _cg_img = "contract_guard_cn.png" if get_region() == "cn" else "contract_guard.png"
        _cg_path = _ASSETS_UI / _cg_img
        if not _cg_path.exists():
            _cg_path = _ASSETS_UI / "contract_guard.png"
        st.image(str(_cg_path), use_container_width=True)
        st.markdown(
            f"<div style='text-align:center; padding:0.5rem 0;'>"
            f"<h4 style='color:#58A6FF; margin:0 0 0.3rem 0; font-size:0.95rem;'>{t('feat_contract_title')}</h4>"
            f"<p style='color:#8B949E; font-size:0.8rem; line-height:1.4;'>{t('feat_contract_desc')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # --- Beta Badge ---
    st.markdown(
        f"""
        <div style="text-align:center; padding:1.2rem 0 0.3rem 0;">
            <span style="background:linear-gradient(135deg,#0A7CFF,#00D4AA); color:#fff;
                padding:0.35rem 1rem; border-radius:20px; font-size:0.8rem; font-weight:600;">
                {t("pricing_badge")}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # --- Login / Signup Form ---
    col_left, col_form, col_right = st.columns([1, 2, 1])

    with col_form:
        login_tab, signup_tab = st.tabs([t("log_in"), t("sign_up")])

        with login_tab:
            with st.form("login_form"):
                email = st.text_input(t("email"), placeholder=t("email_placeholder"))
                password = st.text_input(t("password"), type="password")
                submitted = st.form_submit_button(t("log_in"), use_container_width=True, type="primary")
                if submitted:
                    if email and password:
                        if _do_login(email, password):
                            st.rerun()
                    else:
                        st.warning(t("err_enter_email_pw"))

            # Forgot Password
            if "show_reset" not in st.session_state:
                st.session_state["show_reset"] = False

            if st.button(t("forgot_password"), type="tertiary"):
                st.session_state["show_reset"] = not st.session_state["show_reset"]

            if st.session_state["show_reset"]:
                with st.form("reset_form"):
                    reset_email = st.text_input(t("enter_your_email"), placeholder=t("email_placeholder"),
                                                key="reset_email")
                    reset_submitted = st.form_submit_button(t("send_reset_link"), use_container_width=True)
                    if reset_submitted:
                        if reset_email:
                            if _do_reset_password(reset_email):
                                st.success(t("msg_reset_sent"))
                                st.session_state["show_reset"] = False
                        else:
                            st.warning(t("err_enter_email"))

        with signup_tab:
            with st.form("signup_form"):
                new_email = st.text_input(t("email"), placeholder=t("email_placeholder"), key="signup_email")
                new_password = st.text_input(t("password"), type="password", key="signup_pw",
                                             help=t("pw_help"))
                confirm_pw = st.text_input(t("confirm_password"), type="password", key="signup_pw2")
                signed_up = st.form_submit_button(t("create_account"), use_container_width=True, type="primary")
                if signed_up:
                    if not new_email or not new_password:
                        st.warning(t("err_fill_all"))
                    elif len(new_password) < 6:
                        st.warning(t("err_pw_length"))
                    elif new_password != confirm_pw:
                        st.warning(t("err_pw_mismatch"))
                    else:
                        _do_signup(new_email, new_password)

        st.markdown(
            f"<p style='text-align:center; color:#484F58; font-size:0.75rem; margin-top:2rem;'>"
            f"{t('auth_footer')}</p>",
            unsafe_allow_html=True,
        )

    return False
