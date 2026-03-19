"""API usage tracking and rate limiting for CDI Suite Cloud."""

import streamlit as st
from datetime import datetime, timezone


# Plan limits (monthly API calls)
PLAN_LIMITS = {
    "free": 3,
    "pro": 25,
    "enterprise": 999999,  # effectively unlimited
}

# Keep backward compatibility
FREE_MONTHLY_LIMIT = PLAN_LIMITS["free"]


def _get_supabase():
    """Get the Supabase client from session state."""
    return st.session_state.get("supabase_client")


def get_user_plan(user_id: str) -> str:
    """Get the current plan for a user. Returns 'free' if no subscription."""
    # Cache in session state to avoid repeated DB calls
    cache_key = f"_plan_{user_id}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    sb = _get_supabase()
    if sb is None:
        return "free"

    try:
        res = (
            sb.table("subscriptions")
            .select("plan, status")
            .eq("user_id", user_id)
            .execute()
        )
        if res.data and len(res.data) > 0 and res.data[0].get("status") == "active":
            plan = res.data[0].get("plan", "free")
            st.session_state[cache_key] = plan
            return plan
    except Exception:
        pass

    st.session_state[cache_key] = "free"
    return "free"


def get_plan_limit(user_id: str) -> int:
    """Get the monthly limit for a user based on their plan."""
    plan = get_user_plan(user_id)
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])


def record_usage(user_id: str, tab: str, model: str = ""):
    """Record an API call for the given user."""
    sb = _get_supabase()
    if sb is None:
        return
    try:
        sb.table("usage_logs").insert({
            "user_id": user_id,
            "tab": tab,
            "model": model,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        # Invalidate cached usage count
        st.session_state.pop(f"_usage_{user_id}", None)

        # Check if we should send a usage warning email
        try:
            from utils.email_service import check_and_send_usage_warning
            from utils.auth import get_user
            user = get_user()
            if user:
                used = get_monthly_usage(user_id)
                limit = get_plan_limit(user_id)
                check_and_send_usage_warning(user_id, user["email"], used, limit)
        except Exception:
            pass
    except Exception:
        pass  # Don't block the user if logging fails


def get_monthly_usage(user_id: str) -> int:
    """Get the number of API calls this month for the user."""
    # Cache to avoid repeated DB calls within same page render
    cache_key = f"_usage_{user_id}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    sb = _get_supabase()
    if sb is None:
        return 0
    try:
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        res = (
            sb.table("usage_logs")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .gte("created_at", month_start)
            .execute()
        )
        count = res.count or 0
        st.session_state[cache_key] = count
        return count
    except Exception:
        return 0


def check_quota(user_id: str) -> tuple[bool, int, int]:
    """Check if user has remaining quota.

    Returns:
        (allowed, used, limit)
    """
    used = get_monthly_usage(user_id)
    limit = get_plan_limit(user_id)
    return used < limit, used, limit


def render_quota_exceeded():
    """Show a quota exceeded message with upgrade prompt."""
    st.warning(
        "You've reached your plan's monthly analysis limit. "
        "Upgrade to Pro for 100 analyses/month.",
        icon="\U0001f512",
    )
