"""
admission_portal/db.py
-----------------------
Database layer supporting both PostgreSQL (prod) and SQLite (dev).
Auto-detected via DATABASE_URL environment variable.

Usage:
    python -m admission_portal.db --init-schema
    python -m admission_portal.db --rollback
"""
from __future__ import annotations

import os
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator

_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    from admission_portal import config
except ImportError:
    import config

# ---------------------------------------------------------------------------
# Connection factory
# ---------------------------------------------------------------------------

def _is_postgres() -> bool:
    return bool(config.get_database_url())


def _get_pg_connection():
    import psycopg2
    import psycopg2.extras
    conn = psycopg2.connect(config.get_database_url())
    conn.autocommit = False
    return conn


def _get_sqlite_connection():
    db_path = config.get_sqlite_path()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_conn() -> Generator[Any, None, None]:
    """Context manager: yields a DB connection, commits on success, rolls back on error."""
    if _is_postgres():
        conn = _get_pg_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        conn = _get_sqlite_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def _fetchall(cursor) -> list[dict]:
    """Normalize rows to list of dicts for both PG and SQLite."""
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def _fetchone(cursor) -> dict | None:
    cols = [d[0] for d in cursor.description]
    row = cursor.fetchone()
    if row is None:
        return None
    return dict(zip(cols, row))


# ---------------------------------------------------------------------------
# Schema management
# ---------------------------------------------------------------------------

def _read_sql_file(filename: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, filename)
    with open(path, encoding="utf-8") as f:
        return f.read()


def _adapt_schema_for_sqlite(sql: str) -> str:
    """SQLite doesn't support SERIAL — replace with INTEGER PRIMARY KEY AUTOINCREMENT."""
    return sql  # schema.sql already uses AUTOINCREMENT for SQLite


def _adapt_schema_for_postgres(sql: str) -> str:
    """PostgreSQL: replace AUTOINCREMENT with SERIAL."""
    sql = sql.replace("INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT", "SERIAL NOT NULL PRIMARY KEY")
    sql = sql.replace("INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT", "SERIAL NOT NULL PRIMARY KEY")
    return sql


def init_schema() -> None:
    """Run schema.sql to create all adm_* tables."""
    raw = _read_sql_file("schema.sql")
    if _is_postgres():
        sql = _adapt_schema_for_postgres(raw)
        with get_conn() as conn:
            cur = conn.cursor()
            # Remove SQLite-only index syntax issues and run statement by statement
            for stmt in _split_statements(sql):
                cur.execute(stmt)
    else:
        sql = _adapt_schema_for_sqlite(raw)
        with get_conn() as conn:
            conn.executescript(sql)
    print("[admission_portal] Schema initialized successfully.")


def rollback_schema() -> None:
    """Run rollback.sql to drop all adm_* tables."""
    raw = _read_sql_file("rollback.sql")
    if _is_postgres():
        with get_conn() as conn:
            cur = conn.cursor()
            for stmt in _split_statements(raw):
                cur.execute(stmt)
    else:
        with get_conn() as conn:
            conn.executescript(raw)
    print("[admission_portal] Rollback complete — all adm_* tables dropped.")


def _split_statements(sql: str) -> list[str]:
    """Split SQL into individual statements (skip comments/empty)."""
    stmts = []
    for s in sql.split(";"):
        s = s.strip()
        # Remove comment lines
        lines = [l for l in s.splitlines() if not l.strip().startswith("--")]
        s = "\n".join(lines).strip()
        if s:
            stmts.append(s)
    return stmts


# ---------------------------------------------------------------------------
# adm_requests
# ---------------------------------------------------------------------------

def create_request(hospital_id: str, incident_ref: str = "", patient_name: str = "") -> int:
    """Create a new admission request. Returns the new request ID."""
    now = _now()
    with get_conn() as conn:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                """
                INSERT INTO adm_requests (hospital_id, incident_ref, patient_name, status, created_at, updated_at)
                VALUES (%s, %s, %s, 'pending', %s, %s) RETURNING id
                """,
                (hospital_id, incident_ref, patient_name, now, now),
            )
            return cur.fetchone()[0]
        else:
            cur.execute(
                """
                INSERT INTO adm_requests (hospital_id, incident_ref, patient_name, status, created_at, updated_at)
                VALUES (?, ?, ?, 'pending', ?, ?)
                """,
                (hospital_id, incident_ref, patient_name, now, now),
            )
            return cur.lastrowid


def get_request(request_id: int) -> dict | None:
    with get_conn() as conn:
        cur = conn.cursor()
        ph = "%s" if _is_postgres() else "?"
        cur.execute(f"SELECT * FROM adm_requests WHERE id = {ph}", (request_id,))
        return _fetchone(cur)


def list_requests(limit: int = 100, offset: int = 0) -> list[dict]:
    with get_conn() as conn:
        cur = conn.cursor()
        ph = "%s" if _is_postgres() else "?"
        cur.execute(
            f"SELECT * FROM adm_requests ORDER BY created_at DESC LIMIT {ph} OFFSET {ph}",
            (limit, offset),
        )
        return _fetchall(cur)


def update_request_status(request_id: int, status: str) -> None:
    _valid_statuses = {"pending", "submitted", "under_review", "confirmed", "payment_pending", "paid"}
    if status not in _valid_statuses:
        raise ValueError(f"Invalid status: {status}")
    now = _now()
    with get_conn() as conn:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                "UPDATE adm_requests SET status = %s, updated_at = %s WHERE id = %s",
                (status, now, request_id),
            )
        else:
            cur.execute(
                "UPDATE adm_requests SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, request_id),
            )


def set_deposit_amount(request_id: int, amount_paise: int) -> None:
    now = _now()
    with get_conn() as conn:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                "UPDATE adm_requests SET deposit_amount_paise = %s, updated_at = %s WHERE id = %s",
                (amount_paise, now, request_id),
            )
        else:
            cur.execute(
                "UPDATE adm_requests SET deposit_amount_paise = ?, updated_at = ? WHERE id = ?",
                (amount_paise, now, request_id),
            )


# ---------------------------------------------------------------------------
# adm_access_tokens
# ---------------------------------------------------------------------------

def save_token(token_hash: str, request_id: int, expires_at: datetime) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                """
                INSERT INTO adm_access_tokens (token_hash, request_id, created_at, expires_at)
                VALUES (%s, %s, %s, %s)
                """,
                (token_hash, request_id, _now(), expires_at),
            )
        else:
            cur.execute(
                """
                INSERT INTO adm_access_tokens (token_hash, request_id, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (token_hash, request_id, _now(), _fmt_dt(expires_at)),
            )


def get_token_record(token_hash: str) -> dict | None:
    with get_conn() as conn:
        cur = conn.cursor()
        ph = "%s" if _is_postgres() else "?"
        cur.execute(f"SELECT * FROM adm_access_tokens WHERE token_hash = {ph}", (token_hash,))
        return _fetchone(cur)


def increment_token_use(token_hash: str) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        ph = "%s" if _is_postgres() else "?"
        cur.execute(
            f"UPDATE adm_access_tokens SET used_count = used_count + 1 WHERE token_hash = {ph}",
            (token_hash,),
        )


def revoke_token(token_hash: str) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        ph = "%s" if _is_postgres() else "?"
        cur.execute(
            f"UPDATE adm_access_tokens SET revoked = TRUE WHERE token_hash = {ph}",
            (token_hash,),
        )


def validate_token(raw_token: str) -> tuple[bool, str, dict | None]:
    """
    Returns (is_valid, error_message, token_record).
    token_record includes request_id on success.
    """
    from admission_portal.security import hash_token
    h = hash_token(raw_token)
    rec = get_token_record(h)
    if rec is None:
        return False, "Invalid or unrecognized link.", None
    if rec.get("revoked"):
        return False, "This link has been revoked. Please contact the hospital.", None
    # Expiry check
    expires_at = rec.get("expires_at")
    if expires_at:
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at)
            except ValueError:
                pass
        now = datetime.now(timezone.utc)
        if isinstance(expires_at, datetime):
            exp = expires_at if expires_at.tzinfo else expires_at.replace(tzinfo=timezone.utc)
            if now > exp:
                return False, "This link has expired (valid for 48 hours). Please contact the hospital.", None
    increment_token_use(h)
    return True, "", rec


# ---------------------------------------------------------------------------
# adm_forms
# ---------------------------------------------------------------------------

def save_form(request_id: int, form_data: dict) -> int:
    """Insert a new form submission. Returns form ID."""
    now = _now()
    with get_conn() as conn:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                """
                INSERT INTO adm_forms
                    (request_id, patient_name, patient_dob, patient_gender,
                     attendant_name, attendant_relation, attendant_phone, attendant_email,
                     insurance_provider, insurance_policy_no,
                     emergency_contact_name, emergency_contact_phone,
                     consent_given, consent_timestamp, submitted_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
                """,
                (
                    request_id,
                    form_data.get("patient_name", ""),
                    form_data.get("patient_dob", ""),
                    form_data.get("patient_gender", ""),
                    form_data.get("attendant_name", ""),
                    form_data.get("attendant_relation", ""),
                    form_data.get("attendant_phone", ""),
                    form_data.get("attendant_email", ""),
                    form_data.get("insurance_provider", ""),
                    form_data.get("insurance_policy_no", ""),
                    form_data.get("emergency_contact_name", ""),
                    form_data.get("emergency_contact_phone", ""),
                    bool(form_data.get("consent_given", False)),
                    now,
                    now,
                ),
            )
            return cur.fetchone()[0]
        else:
            cur.execute(
                """
                INSERT INTO adm_forms
                    (request_id, patient_name, patient_dob, patient_gender,
                     attendant_name, attendant_relation, attendant_phone, attendant_email,
                     insurance_provider, insurance_policy_no,
                     emergency_contact_name, emergency_contact_phone,
                     consent_given, consent_timestamp, submitted_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    request_id,
                    form_data.get("patient_name", ""),
                    form_data.get("patient_dob", ""),
                    form_data.get("patient_gender", ""),
                    form_data.get("attendant_name", ""),
                    form_data.get("attendant_relation", ""),
                    form_data.get("attendant_phone", ""),
                    form_data.get("attendant_email", ""),
                    form_data.get("insurance_provider", ""),
                    form_data.get("insurance_policy_no", ""),
                    form_data.get("emergency_contact_name", ""),
                    form_data.get("emergency_contact_phone", ""),
                    1 if form_data.get("consent_given") else 0,
                    now,
                    now,
                ),
            )
            return cur.lastrowid


def get_form(request_id: int) -> dict | None:
    with get_conn() as conn:
        cur = conn.cursor()
        ph = "%s" if _is_postgres() else "?"
        cur.execute(f"SELECT * FROM adm_forms WHERE request_id = {ph} ORDER BY submitted_at DESC, id DESC LIMIT 1", (request_id,))
        return _fetchone(cur)


# ---------------------------------------------------------------------------
# adm_documents
# ---------------------------------------------------------------------------

def save_document(request_id: int, doc_type: str, filename_stored: str, original_ext: str, file_size: int) -> int:
    now = _now()
    with get_conn() as conn:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                """
                INSERT INTO adm_documents (request_id, doc_type, filename_stored, original_ext, file_size_bytes, uploaded_at)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                """,
                (request_id, doc_type, filename_stored, original_ext, file_size, now),
            )
            return cur.fetchone()[0]
        else:
            cur.execute(
                """
                INSERT INTO adm_documents (request_id, doc_type, filename_stored, original_ext, file_size_bytes, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (request_id, doc_type, filename_stored, original_ext, file_size, now),
            )
            return cur.lastrowid


def list_documents(request_id: int) -> list[dict]:
    with get_conn() as conn:
        cur = conn.cursor()
        ph = "%s" if _is_postgres() else "?"
        cur.execute(f"SELECT * FROM adm_documents WHERE request_id = {ph} ORDER BY uploaded_at", (request_id,))
        return _fetchall(cur)


# ---------------------------------------------------------------------------
# adm_payments
# ---------------------------------------------------------------------------

def get_payment(request_id: int) -> dict | None:
    with get_conn() as conn:
        cur = conn.cursor()
        ph = "%s" if _is_postgres() else "?"
        cur.execute(f"SELECT * FROM adm_payments WHERE request_id = {ph}", (request_id,))
        return _fetchone(cur)


def create_payment_record(request_id: int, amount_paise: int, razorpay_link_id: str, short_url: str) -> int:
    now = _now()
    with get_conn() as conn:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                """
                INSERT INTO adm_payments (request_id, razorpay_link_id, amount_paise, status, short_url, created_at)
                VALUES (%s, %s, %s, 'created', %s, %s) RETURNING id
                """,
                (request_id, razorpay_link_id, amount_paise, short_url, now),
            )
            return cur.fetchone()[0]
        else:
            cur.execute(
                """
                INSERT INTO adm_payments (request_id, razorpay_link_id, amount_paise, status, short_url, created_at)
                VALUES (?, ?, ?, 'created', ?, ?)
                """,
                (request_id, razorpay_link_id, amount_paise, short_url, now),
            )
            return cur.lastrowid


def update_payment_status(request_id: int, status: str, razorpay_payment_id: str = "") -> None:
    now = _now()
    with get_conn() as conn:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                """
                UPDATE adm_payments
                SET status = %s, razorpay_payment_id = %s, verified_at = %s
                WHERE request_id = %s
                """,
                (status, razorpay_payment_id, now, request_id),
            )
        else:
            cur.execute(
                """
                UPDATE adm_payments
                SET status = ?, razorpay_payment_id = ?, verified_at = ?
                WHERE request_id = ?
                """,
                (status, razorpay_payment_id, now, request_id),
            )


def mark_pay_later(request_id: int) -> None:
    now = _now()
    with get_conn() as conn:
        cur = conn.cursor()
        # Only insert if no existing record
        existing = get_payment(request_id)
        if existing:
            return
        if _is_postgres():
            cur.execute(
                "INSERT INTO adm_payments (request_id, amount_paise, status, pay_later, created_at) VALUES (%s, 0, 'cancelled', TRUE, %s)",
                (request_id, now),
            )
        else:
            cur.execute(
                "INSERT INTO adm_payments (request_id, amount_paise, status, pay_later, created_at) VALUES (?, 0, 'cancelled', 1, ?)",
                (request_id, now),
            )


# ---------------------------------------------------------------------------
# adm_audit_log
# ---------------------------------------------------------------------------

def audit_log(request_id: int | None, actor: str, action: str, detail: str = "", ip: str = "") -> None:
    """Log an action. Medical/ID data must NOT appear in detail."""
    from admission_portal.security import hash_ip
    ip_hash = hash_ip(ip) if ip else ""
    now = _now()
    with get_conn() as conn:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                "INSERT INTO adm_audit_log (request_id, actor, action, detail, ip_hash, created_at) VALUES (%s,%s,%s,%s,%s,%s)",
                (request_id, actor, action, detail, ip_hash, now),
            )
        else:
            cur.execute(
                "INSERT INTO adm_audit_log (request_id, actor, action, detail, ip_hash, created_at) VALUES (?,?,?,?,?,?)",
                (request_id, actor, action, detail, ip_hash, now),
            )


def list_audit(request_id: int | None = None, limit: int = 50) -> list[dict]:
    with get_conn() as conn:
        cur = conn.cursor()
        if request_id is not None:
            ph = "%s" if _is_postgres() else "?"
            cur.execute(
                f"SELECT * FROM adm_audit_log WHERE request_id = {ph} ORDER BY created_at DESC LIMIT {ph}",
                (request_id, limit),
            )
        else:
            ph = "%s" if _is_postgres() else "?"
            cur.execute(f"SELECT * FROM adm_audit_log ORDER BY created_at DESC LIMIT {ph}", (limit,))
        return _fetchall(cur)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _fmt_dt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--init-schema" in sys.argv:
        init_schema()
    elif "--rollback" in sys.argv:
        answer = input("WARNING: This will DROP all adm_* tables. Type 'yes' to confirm: ")
        if answer.strip().lower() == "yes":
            rollback_schema()
        else:
            print("Rollback cancelled.")
    else:
        print("Usage: python -m admission_portal.db [--init-schema | --rollback]")
