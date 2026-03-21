"""Email notification service for ArchiMind Pro using Resend."""

import streamlit as st
import requests


def _get_resend_key() -> str | None:
    """Get the Resend API key from secrets."""
    try:
        return st.secrets.get("RESEND_API_KEY")
    except Exception:
        return None


def _get_from_address() -> str:
    """Get the sender email address."""
    try:
        return st.secrets.get("EMAIL_FROM", "ArchiMind Pro <onboarding@resend.dev>")
    except Exception:
        return "ArchiMind Pro <onboarding@resend.dev>"


def _send_email(to: str, subject: str, html: str) -> bool:
    """Send an email via Resend API."""
    api_key = _get_resend_key()
    if not api_key:
        return False

    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "from": _get_from_address(),
                "to": [to],
                "subject": subject,
                "html": html,
            },
            timeout=10,
        )
        return resp.status_code == 200
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Email templates
# ---------------------------------------------------------------------------

def send_welcome_email(email: str) -> bool:
    """Send a welcome email to a newly registered user."""
    subject = "Welcome to ArchiMind Pro"
    html = """
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#0D1117;color:#E6EDF3;padding:2rem;border-radius:12px;">
        <div style="text-align:center;margin-bottom:1.5rem;">
            <h1 style="background:linear-gradient(135deg,#0A7CFF,#00D4AA);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:1.8rem;margin:0;">
                ARCHIMIND PRO
            </h1>
            <p style="color:#8B949E;font-size:0.9rem;margin-top:4px;">Architecture & Engineering Intelligence</p>
        </div>

        <h2 style="color:#E6EDF3;font-size:1.3rem;">Welcome aboard! 🎉</h2>

        <p style="color:#C9D1D9;line-height:1.6;">
            Thank you for joining ArchiMind Pro. You now have access to our intelligent tools for architecture and civil engineering:
        </p>

        <ul style="color:#C9D1D9;line-height:1.8;">
            <li><strong style="color:#58A6FF;">Site Renderer</strong> — Generate photorealistic renderings from site photos</li>
            <li><strong style="color:#58A6FF;">Drawing Analyser</strong> — Intelligent quantity takeoff and compliance checks</li>
            <li><strong style="color:#58A6FF;">ContractGuard</strong> — Instant contract risk analysis</li>
        </ul>

        <p style="color:#C9D1D9;line-height:1.6;">
            Your free plan includes <strong>3 analyses per month</strong>. Upgrade to Pro for 50 analyses/month or Max for 200 analyses/month.
        </p>

        <div style="text-align:center;margin:2rem 0;">
            <a href="https://cdi-suite-cloud-f3svb9i29ma9kpwxgtdc6l.streamlit.app"
               style="background:linear-gradient(135deg,#0A7CFF,#0062CC);color:#fff;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600;font-size:0.95rem;">
                Open ArchiMind Pro →
            </a>
        </div>

        <hr style="border:none;border-top:1px solid #30363D;margin:1.5rem 0;">
        <p style="color:#484F58;font-size:0.75rem;text-align:center;">
            ArchiMind Pro v1.0
        </p>
    </div>
    """
    return _send_email(email, subject, html)


def send_usage_warning_email(email: str, used: int, limit: int) -> bool:
    """Send a warning when user reaches 80% of their quota."""
    remaining = limit - used
    subject = f"ArchiMind Pro — You have {remaining} analysis left this month"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#0D1117;color:#E6EDF3;padding:2rem;border-radius:12px;">
        <div style="text-align:center;margin-bottom:1.5rem;">
            <h1 style="background:linear-gradient(135deg,#0A7CFF,#00D4AA);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:1.8rem;margin:0;">
                ARCHIMIND PRO
            </h1>
        </div>

        <h2 style="color:#FF6B35;font-size:1.3rem;">⚠️ Usage Alert</h2>

        <p style="color:#C9D1D9;line-height:1.6;">
            You've used <strong>{used} of {limit}</strong> analyses this month.
            You have <strong style="color:#FF6B35;">{remaining}</strong> remaining.
        </p>

        <div style="background:#21262D;border-radius:8px;padding:4px;margin:1rem 0;">
            <div style="width:{used/limit*100:.0f}%;height:8px;border-radius:6px;background:linear-gradient(90deg,#FF6B35,#FF4500);"></div>
        </div>

        {"<p style='color:#C9D1D9;line-height:1.6;'>Upgrade to <strong style=\"color:#0A7CFF;\">Pro (A$99/mo)</strong> for 50 analyses/month or <strong style=\"color:#FFB800;\">Max (A$199/mo)</strong> for 200 analyses/month.</p>" if limit <= 3 else "<p style='color:#C9D1D9;line-height:1.6;'>Your quota resets on the 1st of next month." + (" Consider upgrading to <strong style=\"color:#FFB800;\">Max (A$199/mo)</strong> for 200 analyses/month.</p>" if limit <= 50 else "</p>")}

        <div style="text-align:center;margin:2rem 0;">
            <a href="https://cdi-suite-cloud-f3svb9i29ma9kpwxgtdc6l.streamlit.app"
               style="background:linear-gradient(135deg,#0A7CFF,#0062CC);color:#fff;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600;font-size:0.95rem;">
                Open ArchiMind Pro →
            </a>
        </div>

        <hr style="border:none;border-top:1px solid #30363D;margin:1.5rem 0;">
        <p style="color:#484F58;font-size:0.75rem;text-align:center;">
            ArchiMind Pro v1.0
        </p>
    </div>
    """
    return _send_email(email, subject, html)


def check_and_send_usage_warning(user_id: str, email: str, used: int, limit: int):
    """Check if we should send a usage warning (at 80% usage), send only once per month."""
    if limit >= 999999:
        return  # Enterprise, no warning needed

    threshold = max(int(limit * 0.8), limit - 1)  # 80% or 1 remaining
    if used < threshold:
        return

    # Only send once per month — use session state flag
    warning_key = f"_usage_warning_sent_{user_id}"
    if st.session_state.get(warning_key):
        return

    if send_usage_warning_email(email, used, limit):
        st.session_state[warning_key] = True
