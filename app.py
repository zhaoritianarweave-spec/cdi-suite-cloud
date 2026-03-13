import streamlit as st

st.set_page_config(
    page_title="CDI Suite — Civil Design Intelligence",
    page_icon="\U0001f3d7\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.ui_components import inject_css
from utils.auth import render_auth_page

inject_css()

# ---------------------------------------------------------------------------
# Auth gate — show login page if not authenticated
# ---------------------------------------------------------------------------
if not render_auth_page():
    st.stop()

# ---------------------------------------------------------------------------
# Main app — only runs when authenticated
# ---------------------------------------------------------------------------
from utils.ui_components import render_header, render_sidebar
from tabs import tab1_site_design, tab2_drawing_analyser, tab4_contract_guard

render_sidebar()
render_header()

tab1, tab2, tab3 = st.tabs([
    "Site Renderer",
    "Drawing Analyser",
    "ContractGuard",
])

with tab1:
    tab1_site_design.render()

with tab2:
    tab2_drawing_analyser.render()

with tab3:
    tab4_contract_guard.render()
