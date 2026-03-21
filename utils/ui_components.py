import streamlit as st
from utils.i18n import t, t_fmt

# ---------------------------------------------------------------------------
# Custom CSS — dark theme with blueprint / civil-tech aesthetic
# ---------------------------------------------------------------------------
GLOBAL_CSS = """
<style>
/* --- Premium fonts --- */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
    font-family: 'Plus Jakarta Sans', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', 'Noto Sans SC', sans-serif !important;
    letter-spacing: 0.3px;
}

/* --- Hide Streamlit Cloud UI elements --- */
[data-testid="stToolbar"] {display: none !important;}

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
    transition: all 0.25s ease;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2E90FF 0%, #0A7CFF 100%);
    box-shadow: 0 4px 15px rgba(10,124,255,0.3);
    transform: translateY(-1px);
}

/* --- File uploader --- */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(10,124,255,0.25);
    border-radius: 12px;
    padding: 0.5rem;
    transition: border-color 0.3s ease, background 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(10,124,255,0.5);
    background: rgba(10,124,255,0.03);
}

/* --- Images --- */
[data-testid="stImage"] img {
    border-radius: 10px;
    border: 1px solid rgba(10,124,255,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
[data-testid="stImage"] img:hover {
    transform: scale(1.01);
    box-shadow: 0 6px 20px rgba(10,124,255,0.15);
}

/* --- Metrics --- */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #161B22, #1C2333);
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 1rem;
    transition: border-color 0.3s ease;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(10,124,255,0.3);
}

/* --- Progress bar glow --- */
[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg, #0A7CFF, #00D4AA) !important;
    border-radius: 10px;
    box-shadow: 0 0 8px rgba(10,124,255,0.3);
}

/* --- Expanders --- */
[data-testid="stExpander"] {
    border: 1px solid #30363D;
    border-radius: 10px;
    background: #161B22;
    overflow: hidden;
    transition: border-color 0.3s ease;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(10,124,255,0.25);
}

/* --- Download buttons --- */
[data-testid="stDownloadButton"] button {
    border: 1px solid #30363D;
    border-radius: 8px;
    font-weight: 600;
    letter-spacing: 0.3px;
    transition: all 0.25s ease;
}
[data-testid="stDownloadButton"] button:hover {
    border-color: #0A7CFF;
    background: rgba(10,124,255,0.08);
    box-shadow: 0 2px 10px rgba(10,124,255,0.15);
}

/* --- Selectbox & Multiselect --- */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    border-radius: 8px !important;
    border-color: #30363D !important;
    transition: border-color 0.3s ease;
}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stMultiSelect"] > div > div:focus-within {
    border-color: #0A7CFF !important;
    box-shadow: 0 0 0 1px rgba(10,124,255,0.3);
}

/* --- Text inputs --- */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    border-radius: 8px !important;
    border-color: #30363D !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #0A7CFF !important;
    box-shadow: 0 0 0 1px rgba(10,124,255,0.3);
}

/* --- Dividers --- */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(10,124,255,0.2), transparent);
    margin: 1.5rem 0;
}

/* --- Scrollbar --- */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0D1117; }
::-webkit-scrollbar-thumb { background: #30363D; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #484F58; }

/* --- Render result card --- */
.result-frame {
    border: 1px solid rgba(10,124,255,0.15);
    border-radius: 12px;
    overflow: hidden;
    background: linear-gradient(145deg, #161B22, #1A1F2B);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    margin-bottom: 1rem;
}
.result-frame:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(10,124,255,0.12);
    border-color: rgba(10,124,255,0.3);
}
.result-frame .frame-label {
    padding: 0.6rem 1rem;
    font-size: 0.85rem;
    font-weight: 600;
    color: #58A6FF;
    letter-spacing: 0.5px;
    border-top: 1px solid rgba(10,124,255,0.1);
    background: rgba(10,124,255,0.04);
}
</style>
"""


def inject_css():
    """Inject the global CSS into the page. Call once at the top of app.py."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_header():
    """Render a compact greeting bar with date on the right."""
    from utils.auth import get_user
    import datetime, zoneinfo

    user = get_user()
    if not user:
        return

    is_zh = t("log_in") == "登录"
    now = datetime.datetime.now(zoneinfo.ZoneInfo("Australia/Sydney"))
    hour = now.hour

    if hour < 12:
        greeting = "早上好" if is_zh else "Good morning"
    elif hour < 18:
        greeting = "下午好" if is_zh else "Good afternoon"
    else:
        greeting = "晚上好" if is_zh else "Good evening"

    email_name = user["email"].split("@")[0]

    # Date display
    if is_zh:
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        date_str = f"{now.month}月{now.day}日 {weekdays[now.weekday()]}"
    else:
        date_str = now.strftime("%b %d, %A")

    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
            padding:0.6rem 0; margin-bottom:0.5rem;">
            <div style="font-size:1.1rem; color:#E6EDF3; font-weight:600;">
                {greeting}, {email_name} 👋
            </div>
            <div style="display:flex; align-items:center; gap:6px;
                color:#8B949E; font-size:0.85rem;">
                <span>🗓️</span>
                <span>{date_str}</span>
            </div>
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
            f"""
            <div class="sidebar-brand">
                <div class="logo-text">{t("sidebar_brand")}</div>
                <div class="logo-sub">{t("sidebar_brand_sub")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Language toggle
        langs = ["English", "中文"]
        cur = 1 if st.session_state.get("lang") == "zh" else 0
        choice = st.selectbox("🌐", langs, index=cur, key="lang_select_sidebar", label_visibility="collapsed")
        st.session_state["lang"] = "zh" if choice == "中文" else "en"

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
                f"{t_fmt('plan_label', name=plan_name)}</span>",
                unsafe_allow_html=True,
            )

            # Usage display
            display_limit = str(limit) if limit < 999999 else "\u221e"
            st.caption(t_fmt("usage_label", used=used, limit=display_limit))
            if limit < 999999:
                _pct = int(min(used / limit, 1.0) * 100)
                st.markdown(
                    f"<div style='width:100%;height:8px;background:rgba(255,255,255,0.06);"
                    f"border-radius:4px;overflow:hidden;margin:4px 0 8px 0;'>"
                    f"<div style='width:{_pct}%;height:100%;"
                    f"background:linear-gradient(90deg,#0A7CFF,#00D4AA);"
                    f"border-radius:4px;'></div></div>",
                    unsafe_allow_html=True,
                )

            if remaining == 0 and plan == "free":
                st.warning(t("free_quota_reached"), icon="\U0001f512")

            # Upgrade / Manage buttons
            if is_stripe_configured():
                if plan == "free":
                    billing = st.radio(
                        "Billing",
                        [t("billing_monthly"), t("billing_annual")],
                        index=1,
                        key="billing_interval",
                        label_visibility="collapsed",
                    )
                    interval = "annual" if "69" in billing else "monthly"
                    price_label = "A$69/mo" if interval == "annual" else "A$99/mo"

                    if st.button(t_fmt("upgrade_btn", price=price_label), use_container_width=True, type="primary"):
                        url = create_checkout_session(user["id"], user["email"], "pro", interval)
                        if url:
                            st.markdown(
                                f'<meta http-equiv="refresh" content="0;url={url}">',
                                unsafe_allow_html=True,
                            )
                            st.info(t("redirecting_checkout"))
                            st.stop()
                else:
                    portal_url = create_customer_portal_url(user["id"])
                    if portal_url:
                        st.markdown(
                            f"<a href='{portal_url}' target='_blank' style='"
                            f"display:block;text-align:center;padding:8px;border-radius:6px;"
                            f"border:1px solid #30363D;color:#E6EDF3;text-decoration:none;"
                            f"font-size:0.85rem;'>{t('manage_subscription')}</a>",
                            unsafe_allow_html=True,
                        )

            # History section
            st.markdown("---")
            from utils.history import get_history
            history = get_history(user["id"], limit=10)
            if history:
                history_label = "📋 History" if t("log_in") != "登录" else "📋 历史记录"
                with st.expander(history_label, expanded=False):
                    tab_icons = {
                        "site_renderer": "🖼️",
                        "drawing_analyser": "📐",
                        "contract_guard": "📜",
                    }
                    for h in history:
                        icon = tab_icons.get(h["tab"], "📄")
                        date = h["created_at"][:10] if h.get("created_at") else ""
                        title = h.get("title", "Analysis")
                        st.markdown(
                            f"<div style='padding:4px 0;border-bottom:1px solid #21262D;'>"
                            f"<span style='font-size:0.8rem;'>{icon} {title}</span><br>"
                            f"<span style='color:#8B949E;font-size:0.7rem;'>{date}</span>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

            st.markdown("")
            if st.button(t("log_out"), use_container_width=True):
                logout()
                st.rerun()

            st.markdown("---")

            with st.expander(t("support_button"), expanded=False):
                st.markdown(
                    f"<div style='text-align:center;color:#8B949E;font-size:0.82rem;padding:4px 0;'>"
                    f"{t('support_email_label')}: hsy8260@proton.me</div>",
                    unsafe_allow_html=True,
                )

        st.markdown(
            f"""
            <div class="sidebar-footer">
                {t("sidebar_footer_line1")}<br>
                {t("sidebar_footer_line2")}
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
