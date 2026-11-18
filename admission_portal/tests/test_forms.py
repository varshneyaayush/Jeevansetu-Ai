"""
admission_portal/tests/test_forms.py
--------------------------------------
Tests: form submission, validation, document save/list.
"""
from __future__ import annotations

import pytest

import admission_portal.db as db


VALID_FORM = {
    "patient_name":           "Aarav Sharma",
    "patient_dob":            "15/08/1990",
    "patient_gender":         "Male",
    "attendant_name":         "Meera Sharma",
    "attendant_relation":     "Mother",
    "attendant_phone":        "+91 9876543210",
    "attendant_email":        "meera@example.com",
    "insurance_provider":     "Star Health",
    "insurance_policy_no":    "POL-12345",
    "emergency_contact_name": "Rohan Sharma",
    "emergency_contact_phone":"9876540000",
    "consent_given":          True,
}


class TestFormSubmission:
    def test_save_and_retrieve_form(self, tmp_db, sample_request_id):
        form_id = db.save_form(sample_request_id, VALID_FORM)
        assert isinstance(form_id, int)
        assert form_id > 0
        form = db.get_form(sample_request_id)
        assert form is not None
        assert form["patient_name"] == "Aarav Sharma"
        assert form["attendant_name"] == "Meera Sharma"
        assert bool(form["consent_given"]) is True

    def test_form_stores_all_fields(self, tmp_db, sample_request_id):
        db.save_form(sample_request_id, VALID_FORM)
        form = db.get_form(sample_request_id)
        assert form["patient_dob"] == "15/08/1990"
        assert form["attendant_relation"] == "Mother"
        assert form["insurance_provider"] == "Star Health"
        assert form["emergency_contact_phone"] == "9876540000"

    def test_no_form_returns_none(self, tmp_db, sample_request_id):
        form = db.get_form(sample_request_id)
        assert form is None

    def test_consent_false_stored_correctly(self, tmp_db, sample_request_id):
        data = {**VALID_FORM, "consent_given": False}
        db.save_form(sample_request_id, data)
        form = db.get_form(sample_request_id)
        assert bool(form["consent_given"]) is False

    def test_latest_form_returned_for_multiple_submissions(self, tmp_db, sample_request_id):
        db.save_form(sample_request_id, VALID_FORM)
        updated = {**VALID_FORM, "attendant_name": "Rohan Sharma Updated"}
        db.save_form(sample_request_id, updated)
        form = db.get_form(sample_request_id)
        assert form["attendant_name"] == "Rohan Sharma Updated"


class TestRequestStatusFlow:
    def test_initial_status_is_pending(self, tmp_db, sample_request_id):
        req = db.get_request(sample_request_id)
        assert req["status"] == "pending"

    def test_update_status(self, tmp_db, sample_request_id):
        db.update_request_status(sample_request_id, "submitted")
        req = db.get_request(sample_request_id)
        assert req["status"] == "submitted"

    def test_all_valid_statuses(self, tmp_db, sample_request_id):
        for s in ["pending", "submitted", "under_review", "confirmed", "payment_pending", "paid"]:
            db.update_request_status(sample_request_id, s)
            req = db.get_request(sample_request_id)
            assert req["status"] == s

    def test_invalid_status_raises(self, tmp_db, sample_request_id):
        with pytest.raises(ValueError):
            db.update_request_status(sample_request_id, "flying_unicorn")

    def test_set_deposit_amount(self, tmp_db, sample_request_id):
        db.set_deposit_amount(sample_request_id, 50000)
        req = db.get_request(sample_request_id)
        assert req["deposit_amount_paise"] == 50000

    def test_list_requests(self, tmp_db):
        id1 = db.create_request("hospital_a", "REF1", "Patient A")
        id2 = db.create_request("hospital_b", "REF2", "Patient B")
        reqs = db.list_requests()
        ids = [r["id"] for r in reqs]
        assert id1 in ids
        assert id2 in ids


class TestDocumentStorage:
    def test_save_and_list_documents(self, tmp_db, sample_request_id):
        db.save_document(sample_request_id, "id_proof", "abc123.jpg", "jpg", 102400)
        docs = db.list_documents(sample_request_id)
        assert len(docs) == 1
        assert docs[0]["doc_type"] == "id_proof"
        assert docs[0]["filename_stored"] == "abc123.jpg"
        assert docs[0]["file_size_bytes"] == 102400

    def test_multiple_documents(self, tmp_db, sample_request_id):
        db.save_document(sample_request_id, "id_proof", "id.jpg", "jpg", 100000)
        db.save_document(sample_request_id, "insurance_card", "ins.pdf", "pdf", 200000)
        docs = db.list_documents(sample_request_id)
        assert len(docs) == 2
        types = {d["doc_type"] for d in docs}
        assert types == {"id_proof", "insurance_card"}

    def test_no_documents_returns_empty(self, tmp_db, sample_request_id):
        docs = db.list_documents(sample_request_id)
        assert docs == []


class TestAuditLog:
    def test_audit_log_saved(self, tmp_db, sample_request_id):
        db.audit_log(sample_request_id, "family", "form_submitted", "test detail")
        logs = db.list_audit(sample_request_id)
        assert len(logs) >= 1
        assert logs[0]["action"] == "form_submitted"
        assert logs[0]["actor"] == "family"

    def test_no_medical_data_in_detail(self, tmp_db, sample_request_id):
        # detail should only contain non-sensitive metadata
        db.audit_log(sample_request_id, "family", "document_uploaded", "doc_type=id_proof size_bytes=1024")
        logs = db.list_audit(sample_request_id)
        # Ensure we can retrieve without error
        assert logs[0]["detail"] == "doc_type=id_proof size_bytes=1024"

    def test_global_audit_list(self, tmp_db):
        rid = db.create_request("h1", "ref1", "Patient X")
        db.audit_log(rid, "staff", "status_updated", "new_status=confirmed")
        logs = db.list_audit(limit=10)
        assert any(l["action"] == "status_updated" for l in logs)
