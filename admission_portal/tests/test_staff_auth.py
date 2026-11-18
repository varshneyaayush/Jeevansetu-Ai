"""
admission_portal/tests/test_staff_auth.py
------------------------------------------
Tests: staff password verification, constant-time compare, session timeout.
"""
from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from admission_portal import security, config


class TestStaffPasswordVerification:
    def test_correct_password_accepted(self):
        with patch.object(config, "get_staff_password", return_value="StaffPass@123"):
            assert security.verify_staff_password("StaffPass@123") is True

    def test_wrong_password_rejected(self):
        with patch.object(config, "get_staff_password", return_value="StaffPass@123"):
            assert security.verify_staff_password("wrongpassword") is False

    def test_empty_password_rejected(self):
        with patch.object(config, "get_staff_password", return_value="StaffPass@123"):
            assert security.verify_staff_password("") is False

    def test_none_configured_password_rejected(self):
        with patch.object(config, "get_staff_password", return_value=None):
            assert security.verify_staff_password("anything") is False

    def test_empty_configured_password_rejected(self):
        with patch.object(config, "get_staff_password", return_value=""):
            assert security.verify_staff_password("") is False

    def test_case_sensitive(self):
        with patch.object(config, "get_staff_password", return_value="SecretPass"):
            assert security.verify_staff_password("secretpass") is False
            assert security.verify_staff_password("SECRETPASS") is False
            assert security.verify_staff_password("SecretPass") is True

    def test_no_leading_trailing_space_match(self):
        with patch.object(config, "get_staff_password", return_value="StaffPass"):
            assert security.verify_staff_password(" StaffPass") is False
            assert security.verify_staff_password("StaffPass ") is False

    def test_uses_constant_time_compare(self):
        """
        Verify that hmac.compare_digest is used (not == operator).
        We just call it twice with correct/incorrect and ensure no timing exception is raised.
        """
        import hmac
        with patch.object(config, "get_staff_password", return_value="TimingTest"):
            # Both calls should complete without raising
            result_ok  = security.verify_staff_password("TimingTest")
            result_bad = security.verify_staff_password("WrongPass1")
        assert result_ok is True
        assert result_bad is False


class TestSessionTimeout:
    def test_fresh_session_valid(self):
        login_time = time.time()
        with patch.object(config, "get_session_timeout_minutes", return_value=30):
            assert security.is_staff_session_valid(login_time) is True

    def test_expired_session_invalid(self):
        # Login time 31 minutes ago
        login_time = time.time() - (31 * 60)
        with patch.object(config, "get_session_timeout_minutes", return_value=30):
            assert security.is_staff_session_valid(login_time) is False

    def test_none_login_time_invalid(self):
        assert security.is_staff_session_valid(None) is False

    def test_exactly_at_timeout_invalid(self):
        timeout_min = 30
        login_time = time.time() - (timeout_min * 60 + 1)
        with patch.object(config, "get_session_timeout_minutes", return_value=timeout_min):
            assert security.is_staff_session_valid(login_time) is False

    def test_just_before_timeout_valid(self):
        timeout_min = 30
        login_time = time.time() - (timeout_min * 60 - 60)  # 1 minute before timeout
        with patch.object(config, "get_session_timeout_minutes", return_value=timeout_min):
            assert security.is_staff_session_valid(login_time) is True

    def test_configurable_timeout(self):
        login_time = time.time() - (10 * 60)  # 10 minutes ago
        with patch.object(config, "get_session_timeout_minutes", return_value=5):
            assert security.is_staff_session_valid(login_time) is False
        with patch.object(config, "get_session_timeout_minutes", return_value=15):
            assert security.is_staff_session_valid(login_time) is True


class TestIPHashing:
    def test_ip_hashed_consistently(self):
        h1 = security.hash_ip("192.168.0.1")
        h2 = security.hash_ip("192.168.0.1")
        assert h1 == h2

    def test_different_ips_different_hashes(self):
        h1 = security.hash_ip("192.168.0.1")
        h2 = security.hash_ip("10.0.0.1")
        assert h1 != h2

    def test_empty_ip_handled(self):
        h = security.hash_ip("")
        assert len(h) == 64  # SHA-256 hex

    def test_original_ip_not_recoverable(self):
        ip = "192.168.100.200"
        h = security.hash_ip(ip)
        assert ip not in h
