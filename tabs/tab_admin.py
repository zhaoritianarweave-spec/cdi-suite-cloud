"""Admin panel — visible only to the admin user."""

import streamlit as st
from datetime import datetime, timezone
from utils.i18n import t
from utils.ui_components import section_header

ADMIN_EMAIL = "hsy8260@proton.me"


def _get_service_client():
    """Create a Supabase client with service_role key for admin operations."""
    try:
        from supabase import create_client
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY")
        if not key:
            return None
        return create_client(url, key)
    except Exception:
        return None


def _get_all_users(admin_client):
    """Fetch all users from auth.users via service_role client."""
    try:
        # Use admin API to list users
        users_response = admin_client.auth.admin.list_users()
        return users_response
    except Exception as e:
        st.error(f"Failed to fetch users: {e}")
        return []


def _get_subscriptions(admin_client):
    """Fetch all subscriptions."""
    try:
        res = admin_client.table("subscriptions").select("*").execute()
        return {row["user_id"]: row for row in (res.data or [])}
    except Exception:
        return {}


def _get_all_usage(admin_client):
    """Fetch usage counts for current month."""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    try:
        res = (
            admin_client.table("usage_logs")
            .select("user_id")
            .gte("created_at", month_start)
            .execute()
        )
        counts = {}
        for row in (res.data or []):
            uid = row["user_id"]
            counts[uid] = counts.get(uid, 0) + 1
        return counts
    except Exception:
        return {}


def _get_feedback_stats(admin_client):
    """Fetch feedback counts grouped by tab and rating."""
    try:
        res = admin_client.table("feedback").select("tab, rating").execute()
        stats = {}
        for row in (res.data or []):
            tab = row["tab"]
            rating = row["rating"]
            if tab not in stats:
                stats[tab] = {"up": 0, "down": 0}
            stats[tab][rating] = stats[tab].get(rating, 0) + 1
        return stats
    except Exception:
        return {}


def _set_user_plan(admin_client, user_id: str, plan: str):
    """Upsert subscription for a user."""
    try:
        if plan == "free":
            # Downgrade: delete the subscription row so user falls back to free
            admin_client.table("subscriptions").delete().eq("user_id", user_id).execute()
        else:
            period_end = "2026-12-31T00:00:00Z"
            admin_client.table("subscriptions").upsert(
                {
                    "user_id": user_id,
                    "plan": plan,
                    "status": "active",
                    "current_period_end": period_end,
                },
                on_conflict="user_id",
            ).execute()
        # Clear cached plan
        st.session_state.pop(f"_plan_{user_id}", None)
        return True
    except Exception as e:
        st.error(f"Failed to update plan: {e}")
        return False


def is_admin(user: dict) -> bool:
    """Check if the current user is admin."""
    return user and user.get("email") == ADMIN_EMAIL


def render():
    """Render the admin panel."""
    section_header("⚙️", t("admin_title"))

    admin_client = _get_service_client()
    if not admin_client:
        st.warning(t("admin_no_key"))
        st.code("SUPABASE_SERVICE_ROLE_KEY = \"your-service-role-key\"", language="toml")
        return

    # Fetch data
    users = _get_all_users(admin_client)
    subs = _get_subscriptions(admin_client)
    usage = _get_all_usage(admin_client)
    feedback_stats = _get_feedback_stats(admin_client)

    if not users:
        st.info(t("admin_no_users"))
        return

    # Stats
    total = len(users)
    pro_count = sum(1 for s in subs.values() if s.get("plan") == "pro")
    st.markdown(f"**{t_fmt('admin_stats', total=total, pro=pro_count)}**")

    # Feedback summary
    if feedback_stats:
        fb_cols = st.columns(len(feedback_stats))
        for i, (tab_name, stats) in enumerate(feedback_stats.items()):
            with fb_cols[i]:
                up = stats.get("up", 0)
                down = stats.get("down", 0)
                total_fb = up + down
                rate = f"{up / total_fb * 100:.0f}%" if total_fb > 0 else "—"
                st.metric(tab_name, f"👍 {up}  👎 {down}", f"{rate} positive")

    st.markdown("---")

    # User table
    for u in users:
        uid = u.id
        email = u.email or "—"
        created = str(u.created_at)[:10] if u.created_at else "—"
        sub = subs.get(uid, {})
        plan = sub.get("plan", "free")
        used = usage.get(uid, 0)
        plan_limit = 50 if plan == "pro" else 3

        col_email, col_date, col_plan, col_usage, col_action = st.columns([3, 2, 1.5, 1.5, 2])

        with col_email:
            st.markdown(f"**{email}**")
        with col_date:
            st.caption(created)
        with col_plan:
            color = "#0A7CFF" if plan == "pro" else "#8B949E"
            st.markdown(
                f"<span style='color:{color};font-weight:600;'>{plan.upper()}</span>",
                unsafe_allow_html=True,
            )
        with col_usage:
            st.caption(f"{used}/{plan_limit}")
        with col_action:
            if plan == "pro":
                if st.button(t("admin_downgrade"), key=f"down_{uid}"):
                    if _set_user_plan(admin_client, uid, "free"):
                        st.rerun()
            else:
                if st.button(t("admin_upgrade"), key=f"up_{uid}"):
                    if _set_user_plan(admin_client, uid, "pro"):
                        st.rerun()


# Need t_fmt imported
from utils.i18n import t_fmt
