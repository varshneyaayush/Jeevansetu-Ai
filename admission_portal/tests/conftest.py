"""
admission_portal/tests/conftest.py
-----------------------------------
Shared pytest fixtures.
Uses an in-memory SQLite DB so tests never touch the real portal.db.
"""
from __future__ import annotations

import os
import sys
import sqlite3
import tempfile
from unittest.mock import patch

import pytest

# Make sure admission_portal is importable from the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture(autouse=True)
def mock_streamlit_secrets(monkeypatch):
    """Prevent any st.secrets access during tests."""
    monkeypatch.setenv("RAZORPAY_KEY_ID", "rzp_test_TESTKEY")
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", "test_secret_TESTKEY")
    monkeypatch.setenv("ADM_STAFF_PASSWORD", "StaffPass@123")
    monkeypatch.setenv("ENABLE_ADMISSION_PORTAL", "true")
    monkeypatch.setenv("ENABLE_STAFF_VIEW", "true")
    monkeypatch.setenv("ADM_TOKEN_EXPIRY_HOURS", "48")
    monkeypatch.setenv("ADM_MAX_FILE_MB", "5")
    # Clear lru_cache on config so env vars are picked up fresh
    import admission_portal.config as cfg
    cfg.get_razorpay_key_id.cache_clear()
    cfg.get_razorpay_key_secret.cache_clear()
    cfg.get_staff_password.cache_clear()
    cfg.get_token_expiry_hours.cache_clear()
    cfg.get_max_file_mb.cache_clear()
    cfg.get_database_url.cache_clear()


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    """
    Provides a fresh SQLite DB for each test.
    Patches config.get_sqlite_path() and config.get_database_url() so db.py uses it.
    """
    db_file = str(tmp_path / "test_portal.db")

    import admission_portal.config as cfg
    monkeypatch.setattr(cfg, "get_sqlite_path", lambda: db_file)
    # Ensure PostgreSQL path is NOT taken
    cfg.get_database_url.cache_clear()
    monkeypatch.setenv("DATABASE_URL", "")

    # Init schema
    import admission_portal.db as db_module
    db_module.init_schema()

    yield db_file


@pytest.fixture()
def sample_request_id(tmp_db):
    """Create a sample admission request and return its ID."""
    import admission_portal.db as db_module
    return db_module.create_request(
        hospital_id="test_hospital",
        incident_ref="SOS-TEST-001",
        patient_name="Test Patient",
    )
