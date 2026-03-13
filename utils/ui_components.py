import streamlit as st

# ---------------------------------------------------------------------------
# Custom CSS — dark theme with blueprint / civil-tech aesthetic
# ---------------------------------------------------------------------------
GLOBAL_CSS = """
<style>
/* --- Blueprint grid overlay on main area --- */
[data-testid="stMainBlockContainer"] {
    background-image:
        linear-gradient(rgba(10,124,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(10,124,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
}

/* --- Header banner --- */
.hero-banner {
    text-align: center;
    padding: 2rem 1rem 1rem 1rem;
    border-bottom: 2px solid rgba(10,124,255,0.3);
    margin-bottom: 1.5rem;
}
.hero-banner h1 {
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 0.3rem;
    background: linear-gradient(135deg, #0A7CFF 0%, #00D4AA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-banner .subtitle {
    color: #8B949E;
    font-size: 1rem;
    letter-spacing: 1px;
}
.hero-banner .tech-badge {
    display: inline-block;
    margin-top: 0.6rem;
    padding: 4px 14px;
    border: 1px solid rgba(10,124,255,0.4);
    border-radius: 20px;
    font-size: 0.75rem;
    color: #58A6FF;
    letter-spacing: 1px;
}

/* --- Sidebar --- */
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(10,124,255,0.15);
}
.sidebar-brand {
    text-align: center;
    padding: 1rem 0;
}
.sidebar-brand .logo-text {
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 1px;
    background: linear-gradient(135deg, #0A7CFF, #00D4AA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sidebar-brand .logo-sub {
    color: #8B949E;
    font-size: 0.75rem;
    margin-top: 2px;
    letter-spacing: 0.5px;
}
.sidebar-footer {
    text-align: center;
    color: #484F58;
    font-size: 0.72rem;
    padding-top: 0.5rem;
    border-top: 1px solid rgba(255,255,255,0.06);
}

/* --- Tab styling --- */
[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* --- Section headers inside tabs --- */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.5rem;
}
.section-header .icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    background: rgba(10,124,255,0.12);
    border: 1px solid rgba(10,124,255,0.25);
}
.section-header h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #E6EDF3;
}

/* --- Result cards --- */
.render-card {
    border: 1px solid rgba(10,124,255,0.2);
    border-radius: 12px;
    overflow: hidden;
    background: #161B22;
    margin-bottom: 1rem;
}
.render-card img {
    border-radius: 12px 12px 0 0;
}
.render-card .label {
    padding: 0.6rem 1rem;
    font-size: 0.85rem;
    font-weight: 600;
    color: #58A6FF;
    letter-spacing: 0.5px;
}

/* --- Buttons --- */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0A7CFF 0%, #0062CC 100%);
    border: none;
    font-weight: 600;
    letter-spacing: 0.5px;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2E90FF 0%, #0A7CFF 100%);
}
</style>
"""


def inject_css():
    """Inject the global CSS into the page. Call once at the top of app.py."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_header():
    """Render the hero banner."""
    st.markdown(
        """
        <div class="hero-banner">
            <h1>CIVIL DESIGN INTELLIGENCE</h1>
            <div class="subtitle">Architecture &middot; Engineering &middot; Visualisation</div>
            <div class="tech-badge">POWERED BY GENERATIVE ARCHITECTURE ENGINE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Render the sidebar with user info, model selector, and usage stats."""
    from utils.auth import get_user, logout
    from utils.usage import get_monthly_usage, FREE_MONTHLY_LIMIT

    user = get_user()

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="logo-text">CDI SUITE</div>
                <div class="logo-sub">Civil Design Intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # User info
        if user:
            st.markdown(f"**{user['email']}**")
            used = get_monthly_usage(user["id"])
            remaining = max(0, FREE_MONTHLY_LIMIT - used)
            st.caption(f"Usage: {used} / {FREE_MONTHLY_LIMIT} this month")
            st.progress(min(used / FREE_MONTHLY_LIMIT, 1.0))
            if remaining == 0:
                st.warning("Quota reached", icon="\U0001f512")
            if st.button("Log Out", use_container_width=True):
                logout()
                st.rerun()

        st.markdown("---")
        st.markdown(
            """
            <div class="sidebar-footer">
                Civil Design Intelligence Suite v1.0<br>
                Generative Architecture Engine
            </div>
            """,
            unsafe_allow_html=True,
        )


def section_header(icon: str, title: str):
    """Render a styled section header with an icon badge."""
    st.markdown(
        f"""
        <div class="section-header">
            <div class="icon">{icon}</div>
            <h3>{title}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def result_card(title: str, content: str):
    """Render a styled result container."""
    st.markdown(
        f"""
        <div style="
            background: #161B22;
            border-left: 3px solid #0A7CFF;
            border-radius: 0 8px 8px 0;
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
        ">
            <h4 style="color:#58A6FF; margin-top:0;">{title}</h4>
            <div style="color:#C9D1D9;">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_row(metrics: list[dict]):
    """Render a row of metric cards."""
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        col.metric(label=m["label"], value=m["value"], delta=m.get("delta"))
