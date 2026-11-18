"""
admission_portal/tests/test_security.py
----------------------------------------
Tests: token generation/hash, expiry, rate limiting, file validation, input validation.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone

import pytest

from admission_portal import security


# ---------------------------------------------------------------------------
# Token generation & hashing
# ---------------------------------------------------------------------------

class TestTokenGeneration:
    def test_generates_different_tokens(self):
        t1 = security.generate_token()
        t2 = security.generate_token()
        assert t1.raw_token != t2.raw_token
        assert t1.token_hash != t2.token_hash

    def test_hash_is_sha256_hex(self):
        t = security.generate_token()
        assert len(t.token_hash) == 64
        assert all(c in "0123456789abcdef" for c in t.token_hash)

    def test_raw_token_not_in_hash(self):
        t = security.generate_token()
        assert t.raw_token not in t.token_hash

    def test_hash_deterministic(self):
        t = security.generate_token()
        assert security.hash_token(t.raw_token) == t.token_hash

    def test_expiry_is_48h_by_default(self):
        before = datetime.now(timezone.utc)
        t = security.generate_token()
        after = datetime.now(timezone.utc)
        expected_min = before + timedelta(hours=47, minutes=59)
        expected_max = after + timedelta(hours=48, minutes=1)
        assert expected_min <= t.expires_at <= expected_max

    def test_different_raw_produces_different_hash(self):
        h1 = security.hash_token("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        h2 = security.hash_token("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        assert h1 != h2

    def test_whitespace_stripped_from_token(self):
        t = security.generate_token()
        # hash_token strips whitespace
        assert security.hash_token(f"  {t.raw_token}  ") == t.token_hash


# ---------------------------------------------------------------------------
# Token validation via DB
# ---------------------------------------------------------------------------

class TestTokenDBValidation:
    def test_valid_token_accepted(self, tmp_db, sample_request_id):
        import admission_portal.db as db
        t = security.generate_token()
        db.save_token(t.token_hash, sample_request_id, t.expires_at)
        valid, msg, rec = db.validate_token(t.raw_token)
        assert valid is True
        assert msg == ""
        assert rec["request_id"] == sample_request_id

    def test_invalid_token_rejected(self, tmp_db):
        import admission_portal.db as db
        valid, msg, rec = db.validate_token("completely_wrong_token_xyz")
        assert valid is False
        assert rec is None

    def test_expired_token_rejected(self, tmp_db, sample_request_id):
        import admission_portal.db as db
        t = security.generate_token()
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        db.save_token(t.token_hash, sample_request_id, past)
        valid, msg, rec = db.validate_token(t.raw_token)
        assert valid is False
        assert "expired" in msg.lower()

    def test_revoked_token_rejected(self, tmp_db, sample_request_id):
        import admission_portal.db as db
        t = security.generate_token()
        db.save_token(t.token_hash, sample_request_id, t.expires_at)
        db.revoke_token(t.token_hash)
        valid, msg, rec = db.validate_token(t.raw_token)
        assert valid is False
        assert "revoked" in msg.lower()

    def test_used_count_increments(self, tmp_db, sample_request_id):
        import admission_portal.db as db
        t = security.generate_token()
        db.save_token(t.token_hash, sample_request_id, t.expires_at)
        db.validate_token(t.raw_token)
        db.validate_token(t.raw_token)
        rec = db.get_token_record(t.token_hash)
        assert rec["used_count"] == 2


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

class TestRateLimit:
    def test_first_attempts_not_blocked(self):
        ip = security.hash_ip("192.168.1.1_test_rl1")
        # Reset first
        security.reset_rate_limit(ip)
        for _ in range(security.RATE_LIMIT_MAX_ATTEMPTS):
            blocked, _ = security.check_rate_limit(ip)
            assert blocked is False

    def test_blocked_after_max_attempts(self):
        ip = security.hash_ip("192.168.1.2_test_rl2")
        security.reset_rate_limit(ip)
        # Exhaust limit
        for _ in range(security.RATE_LIMIT_MAX_ATTEMPTS):
            security.check_rate_limit(ip)
        blocked, wait = security.check_rate_limit(ip)
        assert blocked is True
        assert wait > 0

    def test_reset_clears_limit(self):
        ip = security.hash_ip("192.168.1.3_test_rl3")
        security.reset_rate_limit(ip)
        for _ in range(security.RATE_LIMIT_MAX_ATTEMPTS + 2):
            security.check_rate_limit(ip)
        security.reset_rate_limit(ip)
        blocked, _ = security.check_rate_limit(ip)
        assert blocked is False


# ---------------------------------------------------------------------------
# File validation
# ---------------------------------------------------------------------------

JPEG_MAGIC = b"\xff\xd8\xff\xe0" + b"\x00" * 100
PNG_MAGIC  = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
PDF_MAGIC  = b"%PDF-1.4\n" + b"\x00" * 100


class TestFileValidation:
    def test_valid_jpeg(self):
        name = security.validate_upload(JPEG_MAGIC, "photo.jpg")
        assert name.endswith(".jpg")

    def test_valid_png(self):
        name = security.validate_upload(PNG_MAGIC, "scan.png")
        assert name.endswith(".png")

    def test_valid_pdf(self):
        name = security.validate_upload(PDF_MAGIC, "insurance.pdf")
        assert name.endswith(".pdf")

    def test_safe_uuid_filename(self):
        name = security.validate_upload(JPEG_MAGIC, "../../etc/passwd.jpg")
        assert "/" not in name
        assert "\\" not in name
        assert name.endswith(".jpg")
        assert len(name) > 10

    def test_rejects_exe(self):
        with pytest.raises(security.FileValidationError, match="not allowed"):
            security.validate_upload(b"MZ\x90\x00", "virus.exe")

    def test_rejects_oversized(self):
        big = b"\xff\xd8\xff" + b"A" * (6 * 1024 * 1024)
        with pytest.raises(security.FileValidationError, match="exceeds"):
            security.validate_upload(big, "big.jpg", max_mb=5)

    def test_rejects_empty(self):
        with pytest.raises(security.FileValidationError, match="empty"):
            security.validate_upload(b"", "empty.pdf")

    def test_rejects_magic_mismatch(self):
        # PDF magic but .jpg extension
        with pytest.raises(security.FileValidationError):
            security.validate_upload(PDF_MAGIC, "fake.jpg")

    def test_jpeg_ext_normalized_to_jpg(self):
        name = security.validate_upload(JPEG_MAGIC, "photo.jpeg")
        assert name.endswith(".jpg")


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

class TestInputValidation:
    def test_valid_phones(self):
        valid = ["+91 98765 43210", "9876543210", "+919876543210", "98-765-43210"]
        for p in valid:
            assert security.validate_phone(p), f"Should be valid: {p}"

    def test_invalid_phones(self):
        invalid = ["abc", "123", ""]
        for p in invalid:
            assert not security.validate_phone(p), f"Should be invalid: {p}"

    def test_valid_emails(self):
        assert security.validate_email("user@example.com")
        assert security.validate_email("")   # optional field
        assert security.validate_email("   ")  # blank = optional

    def test_invalid_emails(self):
        assert not security.validate_email("notanemail")
        assert not security.validate_email("@nouser.com")

    def test_valid_amount(self):
        assert security.validate_amount_paise(100)
        assert security.validate_amount_paise(50000)

    def test_invalid_amounts(self):
        assert not security.validate_amount_paise(0)
        assert not security.validate_amount_paise(-100)
        assert not security.validate_amount_paise(None)
        assert not security.validate_amount_paise(99)   # < ₹1
