"""
admission_portal/security.py
-----------------------------
Token generation/validation, rate limiting, file validation,
staff session management, OTP hook, constant-time comparisons.
Medical/ID data is NEVER logged here.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import time
import uuid
import sys
from datetime import datetime, timedelta, timezone
from typing import NamedTuple

_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    from admission_portal import config
except ImportError:
    import config

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
# Magic bytes for file type verification
MAGIC_BYTES: dict[bytes, str] = {
    b"\xff\xd8\xff": "jpg",
    b"\x89PNG": "png",
    b"%PDF": "pdf",
}

RATE_LIMIT_MAX_ATTEMPTS = 5
RATE_LIMIT_WINDOW_SECONDS = 15 * 60   # 15 minutes
RATE_LIMIT_LOCKOUT_SECONDS = 15 * 60  # 15 minutes lockout

# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------

def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_ip(ip: str) -> str:
    """Privacy-safe: store IP as SHA-256 hash only."""
    return sha256_hex(ip or "unknown")


# ---------------------------------------------------------------------------
# Family access token
# ---------------------------------------------------------------------------

class TokenPayload(NamedTuple):
    raw_token: str    # Only returned at creation; never stored
    token_hash: str   # What goes into DB
    expires_at: datetime


def generate_token() -> TokenPayload:
    """Create a new URL-safe token. Returns raw token (send to family) + hash (store in DB)."""
    raw = secrets.token_urlsafe(32)
    h = sha256_hex(raw)
    expiry_hours = config.get_token_expiry_hours()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
    return TokenPayload(raw_token=raw, token_hash=h, expires_at=expires_at)


def hash_token(raw_token: str) -> str:
    """Hash a raw token to look up in DB."""
    return sha256_hex(raw_token.strip())


def build_family_url(base_url: str, raw_token: str) -> str:
    """Build the family portal URL with the token."""
    base = base_url.rstrip("/")
    return f"{base}/?t={raw_token}"


# ---------------------------------------------------------------------------
# Rate limiting (in-memory; suitable for single-process Streamlit)
# ---------------------------------------------------------------------------
# Maps ip_hash -> list of attempt timestamps
_rate_limit_store: dict[str, list[float]] = {}


def check_rate_limit(ip_hash: str) -> tuple[bool, int]:
    """
    Returns (is_blocked, seconds_until_reset).
    Records an attempt. If >RATE_LIMIT_MAX_ATTEMPTS in window → blocked.
    """
    now = time.monotonic()
    attempts = _rate_limit_store.get(ip_hash, [])
    # Purge old entries
    attempts = [t for t in attempts if now - t < RATE_LIMIT_WINDOW_SECONDS]
    attempts.append(now)
    _rate_limit_store[ip_hash] = attempts

    if len(attempts) > RATE_LIMIT_MAX_ATTEMPTS:
        # Lockout until the oldest attempt expires
        oldest = attempts[0]
        reset_in = int(RATE_LIMIT_LOCKOUT_SECONDS - (now - oldest))
        return True, max(0, reset_in)
    return False, 0


def reset_rate_limit(ip_hash: str) -> None:
    """Clear rate limit on successful auth."""
    _rate_limit_store.pop(ip_hash, None)


# ---------------------------------------------------------------------------
# Staff password authentication
# ---------------------------------------------------------------------------

def verify_staff_password(entered: str) -> bool:
    """Constant-time comparison to prevent timing attacks."""
    expected = config.get_staff_password()
    if not expected:
        return False
    # hmac.compare_digest requires same type
    return hmac.compare_digest(
        entered.encode("utf-8"),
        expected.encode("utf-8"),
    )


def is_staff_session_valid(login_time: float | None) -> bool:
    """Check if staff session has not timed out."""
    if login_time is None:
        return False
    timeout_min = config.get_session_timeout_minutes()
    elapsed = time.time() - login_time
    return elapsed < timeout_min * 60


# ---------------------------------------------------------------------------
# File validation
# ---------------------------------------------------------------------------

class FileValidationError(Exception):
    pass


def validate_upload(
    file_bytes: bytes,
    original_filename: str,
    max_mb: int | None = None,
) -> str:
    """
    Validates uploaded file. Returns a safe UUID-based filename (without path).
    Raises FileValidationError on failure.
    """
    if max_mb is None:
        max_mb = config.get_max_file_mb()

    # 1. Size check
    max_bytes = max_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise FileValidationError(f"File size exceeds {max_mb} MB limit.")

    if len(file_bytes) == 0:
        raise FileValidationError("Uploaded file is empty.")

    # 2. Extension check
    _, ext = os.path.splitext(original_filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"File type '{ext}' not allowed. Only JPG, PNG, PDF accepted."
        )
    if ext == ".jpeg":
        ext = ".jpg"

    # 3. Magic bytes check (prevent extension spoofing)
    detected = _detect_magic(file_bytes)
    if detected is None:
        raise FileValidationError("File content does not match an allowed format (JPG/PNG/PDF).")

    # Map detected type to canonical ext
    canonical_ext_map = {"jpg": ".jpg", "png": ".png", "pdf": ".pdf"}
    canonical_ext = canonical_ext_map[detected]
    if ext not in (canonical_ext, ".jpeg"):
        raise FileValidationError(
            f"File extension '{ext}' does not match detected content type '{canonical_ext}'."
        )

    # 4. Generate safe UUID filename
    safe_name = f"{uuid.uuid4().hex}{canonical_ext}"
    return safe_name


def _detect_magic(data: bytes) -> str | None:
    for magic, kind in MAGIC_BYTES.items():
        if data[:len(magic)] == magic:
            return kind
    return None


def save_upload(file_bytes: bytes, safe_filename: str) -> str:
    """Save file bytes to uploads directory. Returns absolute path."""
    uploads_dir = config.get_uploads_dir()
    dest = os.path.join(uploads_dir, safe_filename)
    with open(dest, "wb") as f:
        f.write(file_bytes)
    return dest


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

PHONE_RE = re.compile(r"^\+?[0-9\s\-()]{7,15}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_phone(phone: str) -> bool:
    return bool(PHONE_RE.match(phone.strip()))


def validate_email(email: str) -> bool:
    if not email or not email.strip():
        return True   # email is optional
    return bool(EMAIL_RE.match(email.strip()))


def validate_amount_paise(amount_paise: int | None) -> bool:
    """Deposit amount must be a positive integer (paise). Minimum ₹1 = 100 paise."""
    if amount_paise is None:
        return False
    return isinstance(amount_paise, int) and amount_paise >= 100


# ---------------------------------------------------------------------------
# OTP hook (dev = mock; prod = pluggable SMS provider)
# ---------------------------------------------------------------------------

def send_otp(phone: str) -> str:
    """
    Returns the OTP (for mock mode in dev).
    In prod with ENABLE_OTP_HOOK=true, integrate your SMS provider here.
    """
    if not config.is_otp_enabled():
        return ""
    # Mock OTP: 6-digit, deterministic per session for demo
    otp = str(secrets.randbelow(900000) + 100000)
    # TODO: replace with real SMS API (e.g. Twilio, MSG91)
    # sms_provider.send(phone, f"JeevanSetu OTP: {otp}")
    return otp  # Only returned in mock/dev; in prod, return "" and send via SMS
