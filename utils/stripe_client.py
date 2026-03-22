"""Stripe payment integration for CDI Suite Cloud.

Uses Stripe Checkout Sessions for subscription management.
Since Streamlit Cloud cannot host webhook endpoints, we verify
payment status by polling Stripe on each page load.
"""

import streamlit as st
import stripe


# Plan configuration
PLANS = {
    "free": {"name": "Free", "price": 0, "limit": 3, "price_id": None},
    "beta": {"name": "Beta", "price": 0, "limit": 50, "price_id": None},
    "pro": {"name": "Pro", "price": 99, "price_annual": 49, "limit": 50, "currency": "AUD", "price_id": None},
    "max": {"name": "Max", "price": 199, "price_annual": 99, "limit": 200, "currency": "AUD", "price_id": None},
    "enterprise": {"name": "Enterprise", "price": None, "limit": 999999, "price_id": None},
}


def _get_stripe_key() -> str:
    """Return Stripe secret key from Streamlit secrets."""
    try:
        return st.secrets["STRIPE_SECRET_KEY"]
    except (KeyError, FileNotFoundError):
        return ""


def _get_price_ids() -> dict:
    """Return Stripe Price IDs from secrets."""
    ids = {}
    try:
        ids["pro_monthly"] = st.secrets["STRIPE_PRO_MONTHLY_PRICE_ID"]
    except (KeyError, FileNotFoundError):
        pass
    try:
        ids["pro_annual"] = st.secrets["STRIPE_PRO_ANNUAL_PRICE_ID"]
    except (KeyError, FileNotFoundError):
        pass
    try:
        ids["max_monthly"] = st.secrets["STRIPE_MAX_MONTHLY_PRICE_ID"]
    except (KeyError, FileNotFoundError):
        pass
    try:
        ids["max_annual"] = st.secrets["STRIPE_MAX_ANNUAL_PRICE_ID"]
    except (KeyError, FileNotFoundError):
        pass
    return ids


def is_stripe_configured() -> bool:
    """Check if Stripe is properly configured."""
    price_ids = _get_price_ids()
    return bool(_get_stripe_key()) and bool(price_ids)


def get_plan_limit(plan: str) -> int:
    """Return the monthly usage limit for a plan."""
    return PLANS.get(plan, PLANS["free"])["limit"]


def get_plan_name(plan: str) -> str:
    """Return the display name for a plan."""
    return PLANS.get(plan, PLANS["free"])["name"]


def create_checkout_session(
    user_id: str,
    user_email: str,
    plan: str = "pro",
    interval: str = "monthly",
) -> str | None:
    """Create a Stripe Checkout Session and return the URL.

    Args:
        interval: "monthly" or "annual"

    Returns the checkout URL or None on error.
    """
    secret_key = _get_stripe_key()
    if not secret_key:
        st.error("Stripe is not configured. Contact admin.")
        return None

    price_ids = _get_price_ids()
    price_key = f"{plan}_{interval}"
    price_id = price_ids.get(price_key)
    if not price_id:
        st.error(f"No price configured for: {price_key}")
        return None

    stripe.api_key = secret_key

    try:
        # Get or create Stripe customer
        customer_id = _get_or_create_customer(user_id, user_email)
        if not customer_id:
            return None

        # App URL for redirect
        app_url = st.secrets.get(
            "APP_URL",
            "https://cdi-suite-cloud-f3svb9i29ma9kpwxgtdc6l.streamlit.app",
        )

        session = stripe.checkout.Session.create(
            customer=customer_id,
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{app_url}?payment=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{app_url}?payment=canceled",
            metadata={"user_id": user_id, "plan": plan},
        )

        return session.url

    except stripe.StripeError as e:
        st.error(f"Payment error: {e.user_message or str(e)}")
        return None
    except Exception as e:
        st.error(f"Payment error: {e}")
        return None


def _get_or_create_customer(user_id: str, email: str) -> str | None:
    """Find existing Stripe customer by email or create a new one."""
    try:
        # Check if user already has a Stripe customer via Supabase
        sb = st.session_state.get("supabase_client")
        if sb:
            try:
                res = (
                    sb.table("subscriptions")
                    .select("stripe_customer_id")
                    .eq("user_id", user_id)
                    .execute()
                )
                if res.data and len(res.data) > 0:
                    cid = res.data[0].get("stripe_customer_id")
                    if cid:
                        return cid
            except Exception:
                pass  # Table may not exist yet or RLS blocks — continue

        # Search Stripe by email
        customers = stripe.Customer.list(email=email, limit=1)
        if customers.data:
            return customers.data[0].id

        # Create new customer
        customer = stripe.Customer.create(
            email=email,
            metadata={"supabase_user_id": user_id},
        )
        return customer.id

    except Exception as e:
        st.error(f"Customer creation error: {e}")
        return None


def sync_subscription_status(user_id: str) -> dict:
    """Check Stripe for current subscription status and sync to Supabase.

    Returns dict with: plan, status, current_period_end
    """
    default = {"plan": "free", "status": "active", "current_period_end": None}

    sb = st.session_state.get("supabase_client")
    if not sb:
        return default

    try:
        # Read current subscription from Supabase
        res = (
            sb.table("subscriptions")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        if not res.data or len(res.data) == 0:
            return default

        sub_data = res.data[0]

        # If free plan, no need to check Stripe
        if sub_data.get("plan") == "free" or not sub_data.get("stripe_subscription_id"):
            return {
                "plan": sub_data.get("plan", "free"),
                "status": sub_data.get("status", "active"),
                "current_period_end": sub_data.get("current_period_end"),
            }

        # Check Stripe for latest status
        secret_key = _get_stripe_key()
        if not secret_key:
            return {
                "plan": sub_data.get("plan", "free"),
                "status": sub_data.get("status", "active"),
                "current_period_end": sub_data.get("current_period_end"),
            }

        stripe.api_key = secret_key
        stripe_sub = stripe.Subscription.retrieve(sub_data["stripe_subscription_id"])

        # Map Stripe status
        new_status = "active"
        new_plan = sub_data.get("plan", "free")

        if stripe_sub.status in ("active", "trialing"):
            new_status = "active"
        elif stripe_sub.status == "past_due":
            new_status = "past_due"
        elif stripe_sub.status in ("canceled", "unpaid", "incomplete_expired"):
            new_status = "canceled"
            new_plan = "free"  # Downgrade to free
        else:
            new_status = "incomplete"

        # Update Supabase if changed
        from datetime import datetime, timezone
        period_end = datetime.fromtimestamp(
            stripe_sub.current_period_end, tz=timezone.utc
        ).isoformat()

        if (
            new_status != sub_data.get("status")
            or new_plan != sub_data.get("plan")
            or period_end != sub_data.get("current_period_end")
        ):
            sb.table("subscriptions").update({
                "plan": new_plan,
                "status": new_status,
                "current_period_end": period_end,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).eq("user_id", user_id).execute()

        return {
            "plan": new_plan,
            "status": new_status,
            "current_period_end": period_end,
        }

    except Exception:
        # On any error, return what we have in Supabase
        try:
            if sub_data:
                return {
                    "plan": sub_data.get("plan", "free"),
                    "status": sub_data.get("status", "active"),
                    "current_period_end": sub_data.get("current_period_end"),
                }
        except NameError:
            pass
        return default


def handle_checkout_success(session_id: str, user_id: str) -> bool:
    """Handle successful Stripe Checkout redirect.

    Retrieves the Checkout Session, extracts subscription info,
    and upserts the subscription record in Supabase.
    """
    secret_key = _get_stripe_key()
    if not secret_key:
        return False

    stripe.api_key = secret_key

    try:
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status != "paid":
            return False

        plan = session.metadata.get("plan", "pro")
        customer_id = session.customer if isinstance(session.customer, str) else session.customer.id

        # Get subscription ID
        sub_id = session.subscription
        if hasattr(sub_id, "id"):
            sub_id = sub_id.id

        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()

        # Build upsert data
        upsert_data = {
            "user_id": user_id,
            "plan": plan,
            "stripe_customer_id": customer_id,
            "stripe_subscription_id": sub_id or "",
            "status": "active",
            "updated_at": now_iso,
        }

        # Try to get period end from Stripe subscription
        if sub_id:
            try:
                sub_obj = stripe.Subscription.retrieve(sub_id)
                period_end_ts = getattr(sub_obj, "current_period_end", None)
                if period_end_ts:
                    upsert_data["current_period_end"] = datetime.fromtimestamp(
                        period_end_ts, tz=timezone.utc
                    ).isoformat()
            except Exception:
                pass  # period_end is optional

        sb = st.session_state.get("supabase_client")
        if not sb:
            return False

        # Upsert subscription record
        sb.table("subscriptions").upsert(
            upsert_data, on_conflict="user_id"
        ).execute()

        return True

    except Exception as e:
        st.error(f"Payment verification error: {type(e).__name__}: {e}")
        return False


def create_customer_portal_url(user_id: str) -> str | None:
    """Create a Stripe Customer Portal session for managing subscriptions."""
    secret_key = _get_stripe_key()
    if not secret_key:
        return None

    stripe.api_key = secret_key

    sb = st.session_state.get("supabase_client")
    if not sb:
        return None

    try:
        res = (
            sb.table("subscriptions")
            .select("stripe_customer_id")
            .eq("user_id", user_id)
            .execute()
        )

        if not res.data or len(res.data) == 0:
            return None

        customer_id = res.data[0].get("stripe_customer_id")
        if not customer_id:
            return None

        app_url = st.secrets.get(
            "APP_URL",
            "https://cdi-suite-cloud-f3svb9i29ma9kpwxgtdc6l.streamlit.app",
        )

        portal = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=app_url,
        )

        return portal.url

    except Exception:
        return None
