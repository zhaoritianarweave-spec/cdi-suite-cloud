"""Analysis history storage and retrieval for CDI Suite Cloud."""

import json
import streamlit as st
from datetime import datetime, timezone


def _get_supabase():
    """Get the Supabase client from session state."""
    return st.session_state.get("supabase_client")


def save_history(user_id: str, tab: str, title: str, result_summary: str, result_data=None):
    """Save an analysis result to history."""
    sb = _get_supabase()
    if sb is None:
        return False
    try:
        # Convert result_data to string for text column
        data_str = None
        if result_data is not None:
            if isinstance(result_data, str):
                data_str = result_data
            else:
                data_str = json.dumps(result_data, ensure_ascii=False)
        row = {
            "user_id": user_id,
            "tab": tab,
            "title": title,
            "result_summary": result_summary[:500] if result_summary else "",
            "result_data": data_str,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        sb.table("analysis_history").insert(row).execute()
        # Invalidate cache
        st.session_state.pop(f"_history_{user_id}", None)
        return True
    except Exception:
        return False


def get_history(user_id: str, limit: int = 20) -> list[dict]:
    """Get recent analysis history for a user."""
    cache_key = f"_history_{user_id}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    sb = _get_supabase()
    if sb is None:
        return []
    try:
        res = (
            sb.table("analysis_history")
            .select("id, tab, title, result_summary, result_data, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        history = res.data or []
        st.session_state[cache_key] = history
        return history
    except Exception:
        return []


def get_history_detail(history_id: str) -> dict | None:
    """Get full detail of a specific history entry."""
    sb = _get_supabase()
    if sb is None:
        return None
    try:
        res = (
            sb.table("analysis_history")
            .select("*")
            .eq("id", history_id)
            .execute()
        )
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None
    except Exception:
        return None
