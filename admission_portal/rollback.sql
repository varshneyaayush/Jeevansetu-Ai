-- ============================================================
-- JeevanSetu AI — Emergency Pre-Admission Portal
-- ROLLBACK: Drop ONLY adm_* tables and indexes
-- WARNING: This permanently deletes all admission portal data.
-- Run: psql $DATABASE_URL -f admission_portal/rollback.sql
--  OR: python -m admission_portal.db --rollback
-- ============================================================

-- Drop indexes first
DROP INDEX IF EXISTS idx_adm_audit_created;
DROP INDEX IF EXISTS idx_adm_audit_request;
DROP INDEX IF EXISTS idx_adm_payments_req;
DROP INDEX IF EXISTS idx_adm_docs_request;
DROP INDEX IF EXISTS idx_adm_forms_request;
DROP INDEX IF EXISTS idx_adm_tokens_request;

-- Drop tables (reverse dependency order)
DROP TABLE IF EXISTS adm_audit_log;
DROP TABLE IF EXISTS adm_payments;
DROP TABLE IF EXISTS adm_documents;
DROP TABLE IF EXISTS adm_forms;
DROP TABLE IF EXISTS adm_access_tokens;
DROP TABLE IF EXISTS adm_requests;
