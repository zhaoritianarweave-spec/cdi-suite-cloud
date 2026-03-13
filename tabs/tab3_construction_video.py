"""Tab 3: Construction Video Intelligence."""

import streamlit as st
from utils.ui_components import section_header


def render():
    section_header("🎬", "Construction Sequence Visualiser")
    st.caption("Generate intelligent construction staging animations from site data and project schedules.")
    st.markdown("---")
    st.info("Module under development. Coming soon.", icon="🔧")
