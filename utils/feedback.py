"""User feedback collection for CDI Suite Cloud."""

import streamlit as st


def _get_supabase():
    """Get the Supabase client from session state."""
    return st.session_state.get("supabase_client")


def record_feedback(user_id: str, tab: str, rating: str, comment: str = ""):
    """Record a feedback entry (rating='up' or 'down')."""
    try:
        sb = _get_supabase()
        if sb is None:
            return False
        sb.table("feedback").insert({
            "user_id": user_id,
            "tab": tab,
            "rating": rating,
            "comment": comment,
        }).execute()
        return True
    except Exception:
        return False


def render_feedback(tab_name: str, result_key: str):
    """Render 👍/👎 feedback buttons after analysis completion.

    Args:
        tab_name: Tab identifier (e.g. 'site_renderer', 'drawing_analyser', 'contract_guard')
        result_key: Session state key for the results (to check if analysis was done)
    """
    from utils.auth import get_user
    from utils.i18n import t

    if result_key not in st.session_state or not st.session_state[result_key]:
        return

    user = get_user()
    if not user:
        return

    feedback_key = f"_feedback_{tab_name}_{id(st.session_state.get(result_key, ''))}"

    # Already submitted this session
    if st.session_state.get(feedback_key):
        st.markdown(
            f"<div style='text-align:center;color:#8B949E;font-size:0.85rem;padding:0.5rem 0;'>"
            f"{'谢谢反馈！' if t('log_in') == '登录' else 'Thanks for your feedback!'}</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"<div style='text-align:center;color:#8B949E;font-size:0.85rem;padding:0.5rem 0;'>"
        f"{'这个结果对你有帮助吗？' if t('log_in') == '登录' else 'Was this result helpful?'}</div>",
        unsafe_allow_html=True,
    )

    col_l, col_up, col_down, col_r = st.columns([3, 1, 1, 3])

    with col_up:
        if st.button("👍", key=f"fb_up_{tab_name}", use_container_width=True):
            if record_feedback(user["id"], tab_name, "up"):
                st.session_state[feedback_key] = True
                st.rerun()

    with col_down:
        if st.button("👎", key=f"fb_down_{tab_name}", use_container_width=True):
            if record_feedback(user["id"], tab_name, "down"):
                st.session_state[feedback_key] = True
                st.rerun()
