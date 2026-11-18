"""
admission_portal/payments.py
-----------------------------
Razorpay Payment Links API integration.
Keys loaded ONLY from env/secrets — never hardcoded, logged, or shown in UI.
Amount always comes from server DB — never from client input.
"""
from __future__ import annotations

import os
import sys
import time
from typing import Any

_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    from admission_portal import config, db
except ImportError:
    import config, db


class PaymentError(Exception):
    pass


def _get_razorpay_client():
    """Lazily initialize Razorpay client."""
    key_id = config.get_razorpay_key_id()
    key_secret = config.get_razorpay_key_secret()
    if not key_id or not key_secret:
        raise PaymentError(
            "Razorpay keys not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET "
            "in environment variables or Streamlit secrets."
        )
    try:
        import razorpay
    except ImportError:
        raise PaymentError("razorpay library not installed. Run: pip install razorpay")
    client = razorpay.Client(auth=(key_id, key_secret))
    return client


def get_or_create_payment_link(request_id: int, description: str = "") -> dict:
    """
    Idempotent: if an active payment link already exists for this request, return it.
    Otherwise create a new one via Razorpay Payment Links API.

    Amount is ALWAYS read from adm_requests.deposit_amount_paise (server DB).
    Returns dict with keys: short_url, link_id, amount_paise, status
    """
    # 1. Check for existing payment record
    existing = db.get_payment(request_id)
    if existing and existing.get("razorpay_link_id") and existing.get("status") not in ("failed", "cancelled"):
        return {
            "short_url": existing.get("short_url", ""),
            "link_id": existing.get("razorpay_link_id", ""),
            "amount_paise": existing.get("amount_paise", 0),
            "status": existing.get("status", "created"),
            "already_existed": True,
        }

    # 2. Get amount from DB (never from client)
    req = db.get_request(request_id)
    if not req:
        raise PaymentError(f"Admission request #{request_id} not found.")
    amount_paise = req.get("deposit_amount_paise")
    if not amount_paise or amount_paise < 100:
        raise PaymentError(
            "Deposit amount not set or invalid. Please ask hospital staff to set the deposit amount first."
        )

    # 3. Create Razorpay Payment Link
    client = _get_razorpay_client()
    desc = description or f"Admission Deposit — Request #{request_id}"
    # Truncate desc to Razorpay limit
    if len(desc) > 255:
        desc = desc[:252] + "..."

    payload = {
        "amount": amount_paise,
        "currency": "INR",
        "accept_partial": False,
        "description": desc,
        "reference_id": f"ADM-{request_id}-{int(time.time())}",
        "notify": {"sms": False, "email": False},  # Family gets link directly in portal
        "reminder_enable": False,
        "callback_method": "get",
    }

    try:
        response = client.payment_link.create(payload)
    except Exception as e:
        raise PaymentError(f"Razorpay API error: {e}") from e

    link_id = response.get("id", "")
    short_url = response.get("short_url", "")

    # 4. Store in DB
    db.create_payment_record(request_id, amount_paise, link_id, short_url)
    db.update_request_status(request_id, "payment_pending")
    db.audit_log(request_id, "system", "payment_link_created", f"link_id={link_id} amount_paise={amount_paise}")

    return {
        "short_url": short_url,
        "link_id": link_id,
        "amount_paise": amount_paise,
        "status": "created",
        "already_existed": False,
    }


def verify_payment_status(request_id: int) -> dict:
    """
    Server-side Razorpay API call to verify payment status.
    NEVER trusts client-side callbacks.
    Returns dict with keys: status, razorpay_payment_id, amount_paise
    """
    payment = db.get_payment(request_id)
    if not payment:
        return {"status": "no_payment_record", "razorpay_payment_id": "", "amount_paise": 0}

    if payment.get("pay_later"):
        return {"status": "pay_later", "razorpay_payment_id": "", "amount_paise": 0}

    link_id = payment.get("razorpay_link_id")
    if not link_id:
        return {"status": payment.get("status", "unknown"), "razorpay_payment_id": "", "amount_paise": 0}

    client = _get_razorpay_client()
    try:
        response = client.payment_link.fetch(link_id)
    except Exception as e:
        raise PaymentError(f"Razorpay status fetch error: {e}") from e

    rz_status = response.get("status", "")
    # Razorpay statuses: created, partially_paid, paid, expired, cancelled
    payment_id = ""

    if rz_status == "paid":
        # Get payment_id from payments array
        payments_arr = response.get("payments", [])
        if payments_arr:
            payment_id = payments_arr[-1].get("payment_id", "")
        db.update_payment_status(request_id, "paid", payment_id)
        db.update_request_status(request_id, "paid")
        db.audit_log(request_id, "system", "payment_verified_paid", f"razorpay_payment_id={payment_id}")
    elif rz_status in ("expired", "cancelled"):
        db.update_payment_status(request_id, rz_status)
        db.audit_log(request_id, "system", f"payment_{rz_status}", f"link_id={link_id}")
    # else: still pending — no DB update needed

    return {
        "status": rz_status,
        "razorpay_payment_id": payment_id,
        "amount_paise": payment.get("amount_paise", 0),
    }


def paise_to_rupees(paise: int) -> float:
    return paise / 100.0


def rupees_to_paise(rupees: float) -> int:
    return int(round(rupees * 100 + 1e-9))
