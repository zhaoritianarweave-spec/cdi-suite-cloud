"""API usage tracking and rate limiting for CDI Suite Cloud."""

import streamlit as st
from datetime import datetime, timezone


# Free tier limits
FREE_MONTHLY_LIMIT = 5


def _get_supabase():
    """Get the Supabase client from session state."""
    return st.session_state.get("supabase_client")


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
    except Exception:
        pass  # Don't block the user if logging fails


def get_monthly_usage(user_id: str) -> int:
    """Get the number of API calls this month for the user."""
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
        return res.count or 0
    except Exception:
        return 0


def check_quota(user_id: str) -> tuple[bool, int, int]:
    """Check if user has remaining quota.

    Returns:
        (allowed, used, limit)
    """
    used = get_monthly_usage(user_id)
    limit = FREE_MONTHLY_LIMIT
    return used < limit, used, limit


def render_quota_exceeded():
    """Show a quota exceeded message."""
    st.warning(
        f"You've reached your free plan limit of {FREE_MONTHLY_LIMIT} analyses per month. "
        "Upgrade to Pro for unlimited access.",
        icon="🔒",
    )
