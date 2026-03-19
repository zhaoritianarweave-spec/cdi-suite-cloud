import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="CDI Suite — Civil Design Intelligence",
    page_icon="\U0001f3d7\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.ui_components import inject_css
from utils.auth import render_auth_page
from utils.i18n import t

inject_css()

# ---------------------------------------------------------------------------
# Auth gate — show login page if not authenticated
# ---------------------------------------------------------------------------
if not render_auth_page():
    st.stop()

# ---------------------------------------------------------------------------
# Handle Stripe payment redirect (must run before sidebar renders)
# ---------------------------------------------------------------------------
from utils.auth import get_user

_params = st.query_params
if _params.get("payment") == "success" and _params.get("session_id"):
    _current_user = get_user()
    if _current_user:
        from utils.stripe_client import handle_checkout_success
        if handle_checkout_success(_params["session_id"], _current_user["id"]):
            st.session_state.pop(f"_plan_{_current_user['id']}", None)
            st.success(t("payment_success"))
        else:
            st.warning(t("payment_fail"))
    st.query_params.clear()

# ---------------------------------------------------------------------------
# Main app — only runs when authenticated
# ---------------------------------------------------------------------------
from utils.ui_components import render_header, render_sidebar
from tabs import tab1_site_design, tab2_drawing_analyser, tab4_contract_guard

render_sidebar()
render_header()

_ASSETS_UI = Path(__file__).resolve().parent / "assets" / "ui"

# Check if current user is admin — admin goes in sidebar
_user = get_user()
_is_admin = _user and _user.get("email") == "hsy8260@proton.me"

# ---------------------------------------------------------------------------
# 3 feature cards + workspace below
# ---------------------------------------------------------------------------
_MODULES = [
    ("site_renderer", "feat_renderer_title", "feat_renderer_desc", "site_renderer.png"),
    ("drawing_analyser", "feat_analyser_title", "feat_analyser_desc", "drawing_analyser.png"),
    ("contract_guard", "feat_contract_title", "feat_contract_desc", "contract_guard.png"),
]

# Default to first module
if "active_module" not in st.session_state:
    st.session_state["active_module"] = "site_renderer"

active = st.session_state["active_module"]

# ── Feature cards row ──
cols = st.columns(3, gap="medium")
for col, (key, title_key, desc_key, img_file) in zip(cols, _MODULES):
    with col:
        is_active = (key == active)
        border_color = "#0A7CFF" if is_active else "rgba(48,54,61,0.6)"
        bg = "rgba(10,124,255,0.06)" if is_active else "transparent"

        img_path = _ASSETS_UI / img_file
        if img_path.exists():
            st.image(str(img_path), use_container_width=True)

        st.markdown(
            f"<div style='text-align:center; padding:0.3rem 0;'>"
            f"<h4 style='color:{'#58A6FF' if is_active else '#8B949E'}; "
            f"margin:0 0 0.3rem 0; font-size:0.95rem; font-weight:600;'>{t(title_key)}</h4>"
            f"<p style='color:#8B949E; font-size:0.8rem; line-height:1.4; "
            f"min-height:2.5rem;'>{t(desc_key)}</p></div>",
            unsafe_allow_html=True,
        )

        if st.button(
            t(title_key),
            key=f"btn_{key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state["active_module"] = key
            st.rerun()

st.markdown("---")

# ── Workspace ──
if active == "site_renderer":
    tab1_site_design.render()
elif active == "drawing_analyser":
    tab2_drawing_analyser.render()
elif active == "contract_guard":
    tab4_contract_guard.render()

# ---------------------------------------------------------------------------
# Admin panel in sidebar (admin only)
# ---------------------------------------------------------------------------
if _is_admin:
    with st.sidebar:
        with st.expander(f"⚙️ {t('tab_admin')}", expanded=False):
            from tabs import tab_admin
            tab_admin.render()
