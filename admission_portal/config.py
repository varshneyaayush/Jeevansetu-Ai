"""
admission_portal/config.py
--------------------------
Reads env variables / Streamlit secrets safely.
Never exposes secret values in logs or UI.
"""
from __future__ import annotations

import os
from functools import lru_cache

try:
    import streamlit as st
    _HAS_ST = True
except ImportError:
    _HAS_ST = False


def _get(key: str, default: str | None = None) -> str | None:
    """Read from st.secrets first (Streamlit Cloud), then os.environ."""
    if _HAS_ST:
        try:
            return str(st.secrets[key])
        except (KeyError, AttributeError, Exception):
            pass
    return os.environ.get(key, default)


@lru_cache(maxsize=None)
def get_database_url() -> str | None:
    return _get("DATABASE_URL")


@lru_cache(maxsize=None)
def get_razorpay_key_id() -> str | None:
    return _get("RAZORPAY_KEY_ID")


@lru_cache(maxsize=None)
def get_razorpay_key_secret() -> str | None:
    return _get("RAZORPAY_KEY_SECRET")


@lru_cache(maxsize=None)
def get_staff_password() -> str | None:
    return _get("ADM_STAFF_PASSWORD")


@lru_cache(maxsize=None)
def is_portal_enabled() -> bool:
    return _get("ENABLE_ADMISSION_PORTAL", "true").lower() not in ("false", "0", "no")


@lru_cache(maxsize=None)
def is_staff_view_enabled() -> bool:
    return _get("ENABLE_STAFF_VIEW", "true").lower() not in ("false", "0", "no")


@lru_cache(maxsize=None)
def is_otp_enabled() -> bool:
    return _get("ENABLE_OTP_HOOK", "false").lower() in ("true", "1", "yes")


@lru_cache(maxsize=None)
def get_token_expiry_hours() -> int:
    try:
        return int(_get("ADM_TOKEN_EXPIRY_HOURS", "48"))
    except (ValueError, TypeError):
        return 48


@lru_cache(maxsize=None)
def get_max_file_mb() -> int:
    try:
        return int(_get("ADM_MAX_FILE_MB", "5"))
    except (ValueError, TypeError):
        return 5


@lru_cache(maxsize=None)
def get_sqlite_path() -> str:
    """Default SQLite path for local dev (not used if DATABASE_URL is set)."""
    here = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(here, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "portal.db")


@lru_cache(maxsize=None)
def get_uploads_dir() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    uploads = os.path.join(here, "uploads")
    os.makedirs(uploads, exist_ok=True)
    return uploads


@lru_cache(maxsize=None)
def get_session_timeout_minutes() -> int:
    try:
        return int(_get("ADM_SESSION_TIMEOUT_MINUTES", "30"))
    except (ValueError, TypeError):
        return 30
