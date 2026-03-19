import streamlit as st

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
            # Clear cached plan so sidebar shows updated info
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

tab1, tab2, tab3 = st.tabs([
    t("tab_site_renderer"),
    t("tab_drawing_analyser"),
    t("tab_contract_guard"),
])

with tab1:
    tab1_site_design.render()

with tab2:
    tab2_drawing_analyser.render()

with tab3:
    tab4_contract_guard.render()
