-- ============================================================
-- JeevanSetu AI — Emergency Pre-Admission Portal
-- Schema: ALL tables prefixed with adm_
-- Run once: python -m admission_portal.db --init-schema
-- Compatible with PostgreSQL AND SQLite (see db.py for dialect)
-- ============================================================

-- Access tokens for family portal links
CREATE TABLE IF NOT EXISTS adm_access_tokens (
    token_hash      TEXT        NOT NULL PRIMARY KEY,
    request_id      INTEGER     NOT NULL,
    created_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at      TIMESTAMP   NOT NULL,
    revoked         BOOLEAN     NOT NULL DEFAULT FALSE,
    used_count      INTEGER     NOT NULL DEFAULT 0
);

-- Top-level admission request (created by staff)
CREATE TABLE IF NOT EXISTS adm_requests (
    id                      INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
    hospital_id             TEXT        NOT NULL,
    incident_ref            TEXT,
    patient_name            TEXT,
    status                  TEXT        NOT NULL DEFAULT 'pending',
    -- status values: pending | submitted | under_review | confirmed | payment_pending | paid
    deposit_amount_paise    INTEGER,    -- set by staff; NULL = not yet set
    created_at              TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Admission form filled by family
CREATE TABLE IF NOT EXISTS adm_forms (
    id                          INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
    request_id                  INTEGER     NOT NULL,
    patient_name                TEXT        NOT NULL,
    patient_dob                 TEXT,
    patient_gender              TEXT,
    attendant_name              TEXT        NOT NULL,
    attendant_relation          TEXT        NOT NULL,
    attendant_phone             TEXT        NOT NULL,
    attendant_email             TEXT,
    insurance_provider          TEXT,
    insurance_policy_no         TEXT,
    emergency_contact_name      TEXT,
    emergency_contact_phone     TEXT,
    consent_given               BOOLEAN     NOT NULL DEFAULT FALSE,
    consent_timestamp           TIMESTAMP,
    submitted_at                TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Uploaded ID/insurance documents
CREATE TABLE IF NOT EXISTS adm_documents (
    id                  INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
    request_id          INTEGER     NOT NULL,
    doc_type            TEXT        NOT NULL,   -- id_proof | insurance_card
    filename_stored     TEXT        NOT NULL,   -- UUID-based, safe
    original_ext        TEXT        NOT NULL,   -- jpg | png | pdf
    file_size_bytes     INTEGER     NOT NULL,
    uploaded_at         TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Payment records (Razorpay Payment Links)
CREATE TABLE IF NOT EXISTS adm_payments (
    id                      INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
    request_id              INTEGER     NOT NULL UNIQUE,  -- one active link per request
    razorpay_link_id        TEXT        UNIQUE,
    razorpay_payment_id     TEXT,
    amount_paise            INTEGER     NOT NULL,
    currency                TEXT        NOT NULL DEFAULT 'INR',
    status                  TEXT        NOT NULL DEFAULT 'created',
    -- status values: created | pending | paid | failed | cancelled
    pay_later               BOOLEAN     NOT NULL DEFAULT FALSE,
    short_url               TEXT,
    created_at              TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_at             TIMESTAMP
);

-- Audit log for all actions
CREATE TABLE IF NOT EXISTS adm_audit_log (
    id              INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
    request_id      INTEGER,
    actor           TEXT        NOT NULL,   -- 'family' | 'staff' | 'system'
    action          TEXT        NOT NULL,
    detail          TEXT,                  -- non-sensitive metadata only
    ip_hash         TEXT,                  -- SHA-256 of IP (privacy-safe)
    created_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common lookups
CREATE INDEX IF NOT EXISTS idx_adm_tokens_request  ON adm_access_tokens(request_id);
CREATE INDEX IF NOT EXISTS idx_adm_forms_request   ON adm_forms(request_id);
CREATE INDEX IF NOT EXISTS idx_adm_docs_request    ON adm_documents(request_id);
CREATE INDEX IF NOT EXISTS idx_adm_payments_req    ON adm_payments(request_id);
CREATE INDEX IF NOT EXISTS idx_adm_audit_request   ON adm_audit_log(request_id);
CREATE INDEX IF NOT EXISTS idx_adm_audit_created   ON adm_audit_log(created_at);
