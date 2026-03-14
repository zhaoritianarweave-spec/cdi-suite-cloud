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
    """Render the sidebar with user info, plan, usage stats, and upgrade option."""
    from utils.auth import get_user, logout
    from utils.usage import get_monthly_usage, get_user_plan, get_plan_limit, PLAN_LIMITS
    from utils.stripe_client import (
        is_stripe_configured,
        create_checkout_session,
        create_customer_portal_url,
        get_plan_name,
    )

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

        # User info & usage
        if user:
            plan = get_user_plan(user["id"])
            plan_name = get_plan_name(plan)
            limit = get_plan_limit(user["id"])
            used = get_monthly_usage(user["id"])
            remaining = max(0, limit - used)

            st.markdown(f"[{user['email']}](mailto:{user['email']})")

            # Plan badge
            badge_color = {"free": "#8B949E", "pro": "#0A7CFF", "enterprise": "#00D4AA"}.get(plan, "#8B949E")
            st.markdown(
                f"<span style='background:{badge_color}22;color:{badge_color};"
                f"padding:2px 10px;border-radius:10px;font-size:0.75rem;"
                f"font-weight:600;border:1px solid {badge_color}44;'>"
                f"{plan_name} Plan</span>",
                unsafe_allow_html=True,
            )

            # Usage display
            display_limit = limit if limit < 999999 else "\u221e"
            st.caption(f"Usage: {used} / {display_limit} this month")
            if limit < 999999:
                st.progress(min(used / limit, 1.0))

            if remaining == 0 and plan == "free":
                st.warning("Free quota reached", icon="\U0001f512")

            # Upgrade / Manage buttons
            if is_stripe_configured():
                if plan == "free":
                    billing = st.radio(
                        "Billing",
                        ["Monthly — A$99/mo", "Annual — A$69/mo (save 30%)"],
                        index=1,
                        key="billing_interval",
                        label_visibility="collapsed",
                    )
                    interval = "annual" if "Annual" in billing else "monthly"
                    price_label = "A$69/mo" if interval == "annual" else "A$99/mo"

                    if st.button(f"\u26a1 Upgrade to Pro — {price_label}", use_container_width=True, type="primary"):
                        url = create_checkout_session(user["id"], user["email"], "pro", interval)
                        if url:
                            st.markdown(
                                f'<meta http-equiv="refresh" content="0;url={url}">',
                                unsafe_allow_html=True,
                            )
                            st.info("Redirecting to checkout...")
                            st.stop()
                else:
                    portal_url = create_customer_portal_url(user["id"])
                    if portal_url:
                        st.markdown(
                            f"<a href='{portal_url}' target='_blank' style='"
                            f"display:block;text-align:center;padding:8px;border-radius:6px;"
                            f"border:1px solid #30363D;color:#E6EDF3;text-decoration:none;"
                            f"font-size:0.85rem;'>Manage Subscription</a>",
                            unsafe_allow_html=True,
                        )

            st.markdown("")
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
