"""
admission_portal/tests/test_payments.py
-----------------------------------------
Tests: payment record creation, idempotency, server-side status verify (mocked Razorpay),
pay-later flow, amount-from-server enforcement.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import admission_portal.db as db
from admission_portal import payments


def _setup_request_with_deposit(tmp_db, paise: int = 50000) -> int:
    """Helper: create a request and set deposit amount."""
    rid = db.create_request("test_hospital", "SOS-PAY-001", "Pay Patient")
    db.set_deposit_amount(rid, paise)
    return rid


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

class TestPaymentIdempotency:
    def test_second_call_returns_existing_link(self, tmp_db):
        rid = _setup_request_with_deposit(tmp_db)

        mock_response = {
            "id": "plink_TEST123",
            "short_url": "https://rzp.io/l/test123",
        }
        mock_rzp = MagicMock()
        mock_rzp.payment_link.create.return_value = mock_response
        with patch("admission_portal.payments._get_razorpay_client", return_value=mock_rzp):
            payments.get_or_create_payment_link(rid)

        # Second call — should NOT hit Razorpay API again
        mock_rzp2 = MagicMock()
        with patch("admission_portal.payments._get_razorpay_client", return_value=mock_rzp2):
            result2 = payments.get_or_create_payment_link(rid)
            mock_rzp2.payment_link.create.assert_not_called()

        assert result2["already_existed"] is True
        assert result2["link_id"] == "plink_TEST123"

    def test_first_call_creates_link(self, tmp_db):
        rid = _setup_request_with_deposit(tmp_db)
        mock_response = {"id": "plink_NEW123", "short_url": "https://rzp.io/l/new123"}

        mock_rzp = MagicMock()
        mock_rzp.payment_link.create.return_value = mock_response
        with patch("admission_portal.payments._get_razorpay_client", return_value=mock_rzp):
            result = payments.get_or_create_payment_link(rid)

        assert result["already_existed"] is False
        assert result["link_id"] == "plink_NEW123"
        assert result["short_url"] == "https://rzp.io/l/new123"

    def test_link_stored_in_db(self, tmp_db):
        rid = _setup_request_with_deposit(tmp_db)
        mock_response = {"id": "plink_DB456", "short_url": "https://rzp.io/l/db456"}

        mock_rzp = MagicMock()
        mock_rzp.payment_link.create.return_value = mock_response
        with patch("admission_portal.payments._get_razorpay_client", return_value=mock_rzp):
            payments.get_or_create_payment_link(rid)

        payment_rec = db.get_payment(rid)
        assert payment_rec is not None
        assert payment_rec["razorpay_link_id"] == "plink_DB456"


# ---------------------------------------------------------------------------
# Amount from server, never client
# ---------------------------------------------------------------------------

class TestAmountFromServer:
    def test_amount_read_from_db(self, tmp_db):
        rid = _setup_request_with_deposit(tmp_db, paise=75000)
        captured = {}

        def fake_create(payload):
            captured["amount"] = payload["amount"]
            return {"id": "plink_AMT", "short_url": "https://rzp.io/l/amt"}

        mock_rzp = MagicMock()
        mock_rzp.payment_link.create.side_effect = fake_create
        with patch("admission_portal.payments._get_razorpay_client", return_value=mock_rzp):
            payments.get_or_create_payment_link(rid)

        assert captured["amount"] == 75000  # from DB, not client

    def test_raises_if_no_deposit_set(self, tmp_db):
        rid = db.create_request("h1", "ref", "Patient")
        # No deposit set
        with pytest.raises(payments.PaymentError, match="Deposit amount not set"):
            payments.get_or_create_payment_link(rid)

    def test_raises_if_deposit_too_small(self, tmp_db):
        rid = db.create_request("h1", "ref", "Patient")
        db.set_deposit_amount(rid, 50)  # < 100 paise = < ₹1
        with pytest.raises(payments.PaymentError, match="Deposit amount not set or invalid"):
            payments.get_or_create_payment_link(rid)


# ---------------------------------------------------------------------------
# Server-side payment status verification
# ---------------------------------------------------------------------------

class TestPaymentStatusVerification:
    def test_paid_status_updates_db(self, tmp_db):
        rid = _setup_request_with_deposit(tmp_db)
        # Create link record first
        db.create_payment_record(rid, 50000, "plink_PAID", "https://rzp.io/l/paid")

        fake_fetch = {
            "status": "paid",
            "payments": [{"payment_id": "pay_ABC123"}],
        }
        mock_rzp = MagicMock()
        mock_rzp.payment_link.fetch.return_value = fake_fetch
        with patch("admission_portal.payments._get_razorpay_client", return_value=mock_rzp):
            result = payments.verify_payment_status(rid)

        assert result["status"] == "paid"
        assert result["razorpay_payment_id"] == "pay_ABC123"
        # DB updated
        payment_rec = db.get_payment(rid)
        assert payment_rec["status"] == "paid"
        req = db.get_request(rid)
        assert req["status"] == "paid"

    def test_pending_status_no_db_change(self, tmp_db):
        rid = _setup_request_with_deposit(tmp_db)
        db.create_payment_record(rid, 50000, "plink_PEND", "https://rzp.io/l/pend")
        db.update_request_status(rid, "payment_pending")

        fake_fetch = {"status": "created", "payments": []}
        mock_rzp = MagicMock()
        mock_rzp.payment_link.fetch.return_value = fake_fetch
        with patch("admission_portal.payments._get_razorpay_client", return_value=mock_rzp):
            result = payments.verify_payment_status(rid)

        assert result["status"] == "created"
        req = db.get_request(rid)
        assert req["status"] == "payment_pending"  # unchanged

    def test_no_payment_record_returns_no_record(self, tmp_db):
        rid = db.create_request("h1", "ref", "Patient")
        result = payments.verify_payment_status(rid)
        assert result["status"] == "no_payment_record"

    def test_client_callback_not_trusted(self, tmp_db):
        """
        Proves amount/status always comes from server-side Razorpay API, not client.
        No client input can change payment status directly.
        """
        rid = _setup_request_with_deposit(tmp_db)
        db.create_payment_record(rid, 50000, "plink_SAFE", "https://rzp.io/l/safe")

        # Simulate a "paid" API response — only valid if Razorpay confirms it
        fake_fetch = {"status": "paid", "payments": [{"payment_id": "pay_SERVER"}]}
        mock_rzp = MagicMock()
        mock_rzp.payment_link.fetch.return_value = fake_fetch
        with patch("admission_portal.payments._get_razorpay_client", return_value=mock_rzp):
            result = payments.verify_payment_status(rid)

        # Must go through server-side verification
        assert result["status"] == "paid"
        assert result["razorpay_payment_id"] == "pay_SERVER"


# ---------------------------------------------------------------------------
# Pay Later
# ---------------------------------------------------------------------------

class TestPayLater:
    def test_mark_pay_later(self, tmp_db, sample_request_id):
        db.mark_pay_later(sample_request_id)
        payment = db.get_payment(sample_request_id)
        assert payment is not None
        assert bool(payment["pay_later"]) is True

    def test_pay_later_idempotent(self, tmp_db, sample_request_id):
        db.mark_pay_later(sample_request_id)
        db.mark_pay_later(sample_request_id)  # second call — no error, no duplicate
        payment = db.get_payment(sample_request_id)
        assert bool(payment["pay_later"]) is True

    def test_verify_pay_later_returns_pay_later_status(self, tmp_db, sample_request_id):
        db.mark_pay_later(sample_request_id)
        result = payments.verify_payment_status(sample_request_id)
        assert result["status"] == "pay_later"


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

class TestPaymentUtils:
    def test_paise_to_rupees(self):
        assert payments.paise_to_rupees(50000) == 500.0
        assert payments.paise_to_rupees(100) == 1.0

    def test_rupees_to_paise(self):
        assert payments.rupees_to_paise(500.0) == 50000
        assert payments.rupees_to_paise(1.0) == 100
        assert payments.rupees_to_paise(1.005) == 101  # rounded
