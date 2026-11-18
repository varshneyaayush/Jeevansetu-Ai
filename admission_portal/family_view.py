"""
admission_portal/family_view.py
--------------------------------
Family-facing portal: token-gated, mobile-friendly.
Steps: form → document upload → payment → status → receipt download.
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone

import streamlit as st

_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    from admission_portal import config, db, payments, receipts, security
except ImportError:
    import config, db, payments, receipts, security

# ---------------------------------------------------------------------------
# CSS — mobile-first, independent of main app
# ---------------------------------------------------------------------------
PORTAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap');
body, .stApp { background: #F5EFE6; font-family: 'Lato', sans-serif; }
.adm-header {
    background: #1F3D2B; color: #F5EFE6; border-radius: 14px;
    padding: 1.1rem 1.4rem; margin-bottom: 1.2rem;
    border-bottom: 4px solid #8B5CF6;
}
.adm-header h2 { color: #F5EFE6 !important; margin: 0; font-size: 1.35rem; }
.adm-header p  { color: #D3C29E; margin: 0.2rem 0 0; font-size: 0.85rem; }
.adm-step {
    background: #fff; border: 1.5px solid rgba(31,61,43,0.25);
    border-radius: 12px; padding: 1.1rem 1.3rem; margin-bottom: 1rem;
}
.adm-step h3 { color: #1F3D2B; margin-top: 0; }
.adm-disclaimer {
    background: #FFF8E1; border-left: 6px solid #F59E0B;
    border-radius: 8px; padding: 0.8rem 1rem; margin: 0.8rem 0;
    font-size: 0.9rem; color: #78350F;
}
.adm-status-badge {
    display: inline-block; padding: 0.35rem 1rem; border-radius: 999px;
    font-weight: 700; font-size: 0.88rem; margin: 0.5rem 0;
}
.status-pending        { background:#FEF3C7; color:#92400E; }
.status-submitted      { background:#DBEAFE; color:#1E3A8A; }
.status-under_review   { background:#EDE9FE; color:#4C1D95; }
.status-confirmed      { background:#D1FAE5; color:#065F46; }
.status-payment_pending{ background:#FEE2E2; color:#991B1B; }
.status-paid           { background:#D1FAE5; color:#065F46; }
.adm-success { background:#ECF6EF; border:1.5px solid #2F7A55; border-radius:10px; padding:0.9rem 1.1rem; color:#1F3D2B; }
.adm-error   { background:#FEF2F2; border:1.5px solid #DC2626; border-radius:10px; padding:0.9rem 1.1rem; color:#7F1D1D; }
</style>
"""

STATUS_LABELS = {
    "pending":         "⏳ Submitted — Pending Review",
    "submitted":       "📋 Form Submitted",
    "under_review":    "🔍 Under Review by Hospital",
    "confirmed":       "✅ Admission Confirmed",
    "payment_pending": "💳 Payment Pending",
    "paid":            "✅ Payment Received",
}

# ---------------------------------------------------------------------------
# Main render entry point
# ---------------------------------------------------------------------------

def render(token: str) -> None:
    st.markdown(PORTAL_CSS, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="adm-header">
      <h2>🏥 JeevanSetu — Emergency Admission Portal</h2>
      <p>Surakshit Online Admission Form &amp; Payment | Secure Family Link</p>
    </div>
    """, unsafe_allow_html=True)

    # Rate limit check (IP not available in Streamlit easily; use session key as proxy)
    ip_proxy = st.session_state.get("_adm_session_id", "unknown")
    if not ip_proxy or ip_proxy == "unknown":
        import secrets as _s
        ip_proxy = _s.token_hex(8)
        st.session_state["_adm_session_id"] = ip_proxy
    ip_hash = security.hash_ip(ip_proxy)

    blocked, wait_secs = security.check_rate_limit(ip_hash)
    if blocked:
        st.error(f"⛔ Bahut zyada galat attempts. {wait_secs // 60 + 1} minute baad try karein.")
        return

    # Validate token
    is_valid, err_msg, token_rec = db.validate_token(token)
    if not is_valid:
        security.check_rate_limit(ip_hash)  # count as bad attempt
        st.markdown(f'<div class="adm-error">❌ {err_msg}</div>', unsafe_allow_html=True)
        st.info("Agar aapko lagta hai yeh galat hai, hospital se sampark karein.")
        return

    # Token valid — reset rate limit
    security.reset_rate_limit(ip_hash)

    request_id = int(token_rec["request_id"])
    req = db.get_request(request_id)
    if not req:
        st.error("Admission request nahi mili. Hospital se sampark karein.")
        return

    db.audit_log(request_id, "family", "portal_opened", f"session_hash={ip_hash[:8]}")

    current_status = req.get("status", "pending")

    # Status banner (always visible)
    _render_status_banner(current_status, request_id)

    # Disclaimer — always visible
    st.markdown("""
    <div class="adm-disclaimer">
      <b>⚠️ Zaroori Soochna:</b> Emergency treatment payment ka wait NAHI karega.
      Yeh form sirf <b>admission formalities / deposit</b> ke liye hai.<br>
      <i>"Treatment has already started / will start regardless of payment."</i>
    </div>
    """, unsafe_allow_html=True)

    # Tabs: Form | Documents | Payment | Status
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Admission Form", "📎 Documents", "💳 Payment", "📄 Receipt"])

    with tab1:
        _render_form_tab(request_id, current_status)

    with tab2:
        _render_documents_tab(request_id, current_status)

    with tab3:
        _render_payment_tab(request_id, req, current_status)

    with tab4:
        _render_receipt_tab(request_id, req, current_status)


# ---------------------------------------------------------------------------
# Status banner
# ---------------------------------------------------------------------------

def _render_status_banner(status: str, request_id: int) -> None:
    label = STATUS_LABELS.get(status, status.replace("_", " ").title())
    css_class = f"status-{status}"
    st.markdown(f"""
    <div style="margin-bottom:0.5rem">
      <span style="font-size:0.8rem;color:#5C6B61">Request #{request_id} &nbsp;|&nbsp; Current Status:</span><br>
      <span class="adm-status-badge {css_class}">{label}</span>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tab 1 — Admission Form
# ---------------------------------------------------------------------------

def _render_form_tab(request_id: int, current_status: str) -> None:
    st.markdown('<div class="adm-step"><h3>📋 Admission Form</h3>', unsafe_allow_html=True)

    existing_form = db.get_form(request_id)
    show_form = True
    if existing_form:
        st.markdown('<div class="adm-success">✅ Form already submitted. Aap neeche submitted details dekh sakte hain ya edit kar sakte hain.</div>', unsafe_allow_html=True)
        with st.expander("👁️ Submitted Details Dekhen", expanded=False):
            st.json({
                "Patient": existing_form.get("patient_name"),
                "Attendant": existing_form.get("attendant_name"),
                "Phone": existing_form.get("attendant_phone"),
                "Relation": existing_form.get("attendant_relation"),
                "Insurance": existing_form.get("insurance_provider"),
                "Submitted At": str(existing_form.get("submitted_at", "")),
            })
        st.markdown("<br>", unsafe_allow_html=True)

    ef = existing_form or {}

    with st.form("adm_family_form"):
        st.markdown("#### 🧑‍⚕️ Patient Details")
        patient_name   = st.text_input("Patient ka Naam (Full Name) *", value=ef.get("patient_name", ""), placeholder="Aarav Sharma")
        patient_dob    = st.text_input("Date of Birth (DD/MM/YYYY)", value=ef.get("patient_dob", ""), placeholder="15/08/1990")
        gender_options = ["", "Male", "Female", "Other"]
        g_idx = gender_options.index(ef.get("patient_gender", "")) if ef.get("patient_gender") in gender_options else 0
        patient_gender = st.selectbox("Gender", gender_options, index=g_idx)

        st.markdown("#### 👤 Attendant / Family Member Details")
        attendant_name     = st.text_input("Aapka Naam (Attendant) *", value=ef.get("attendant_name", ""), placeholder="Meera Sharma")
        attendant_relation = st.text_input("Relation with Patient *", value=ef.get("attendant_relation", ""), placeholder="e.g. Mother, Spouse")
        attendant_phone    = st.text_input("Mobile Number *", value=ef.get("attendant_phone", ""), placeholder="+91 98765 43210")
        attendant_email    = st.text_input("Email (optional)", value=ef.get("attendant_email", ""), placeholder="meera@example.com")

        st.markdown("#### 🏥 Insurance Information (optional)")
        insurance_provider  = st.text_input("Insurance Company Name", value=ef.get("insurance_provider", ""), placeholder="Star Health / Religare")
        insurance_policy_no = st.text_input("Policy Number", value=ef.get("insurance_policy_no", ""), placeholder="Policy No.")

        st.markdown("#### 🆘 Emergency Contact (different from attendant)")
        ec_name  = st.text_input("Emergency Contact Name", value=ef.get("emergency_contact_name", ""), placeholder="Rohan Sharma")
        ec_phone = st.text_input("Emergency Contact Phone", value=ef.get("emergency_contact_phone", ""), placeholder="+91 97654 32100")

        st.markdown("---")
        consent = st.checkbox(
            "✅ Main samajhta/samajhti hoon ki meri dī gayi jaankāri hospital ke saath share ki jayegi. "
            "Maine is baat ki sehmat de di hai. (I consent to sharing this information with the hospital.)",
            value=bool(ef.get("consent_given", False)),
        )

        btn_label = "💾 Update Form" if existing_form else "📤 Form Submit Karen"
        submitted = st.form_submit_button(btn_label, type="primary")

    if submitted:
        # Validation
        errors = []
        if not patient_name.strip():
            errors.append("Patient ka naam zaroori hai.")
        if not attendant_name.strip():
            errors.append("Attendant ka naam zaroori hai.")
        if not attendant_relation.strip():
            errors.append("Relation with patient zaroori hai.")
        if not attendant_phone.strip():
            errors.append("Mobile number zaroori hai.")
        elif not security.validate_phone(attendant_phone):
            errors.append("Mobile number sahi format mein nahi hai.")
        if attendant_email and not security.validate_email(attendant_email):
            errors.append("Email address sahi format mein nahi hai.")
        if ec_phone and not security.validate_phone(ec_phone):
            errors.append("Emergency contact phone number sahi format mein nahi hai.")
        if not consent:
            errors.append("Form submit karne ke liye consent (checkbox) zaroori hai.")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            form_data = {
                "patient_name": patient_name.strip(),
                "patient_dob": patient_dob.strip(),
                "patient_gender": patient_gender,
                "attendant_name": attendant_name.strip(),
                "attendant_relation": attendant_relation.strip(),
                "attendant_phone": attendant_phone.strip(),
                "attendant_email": attendant_email.strip(),
                "insurance_provider": insurance_provider.strip(),
                "insurance_policy_no": insurance_policy_no.strip(),
                "emergency_contact_name": ec_name.strip(),
                "emergency_contact_phone": ec_phone.strip(),
                "consent_given": True,
            }
            try:
                db.save_form(request_id, form_data)
                db.update_request_status(request_id, "submitted")
                db.audit_log(request_id, "family", "form_submitted",
                             f"attendant_phone_hash={security.sha256_hex(attendant_phone)[:8]}")
                st.success("✅ Form successfully submit ho gaya! Hospital review karega.")
                time.sleep(1)
                st.rerun()
            except Exception as ex:
                st.error(f"Form save karne mein error: {ex}")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tab 2 — Document Upload
# ---------------------------------------------------------------------------

def _render_documents_tab(request_id: int, current_status: str) -> None:
    st.markdown('<div class="adm-step"><h3>📎 Document Upload</h3>', unsafe_allow_html=True)
    st.caption("Sirf JPG, PNG, PDF — max 5 MB. Documents private folder mein store honge, public access nahi.")

    existing_docs = db.list_documents(request_id)
    if existing_docs:
        st.markdown("**Already Uploaded Documents:**")
        for doc in existing_docs:
            st.markdown(f"- 📄 `{doc['doc_type']}` — {doc['original_ext'].upper()}, "
                        f"{doc['file_size_bytes'] // 1024} KB — {doc['uploaded_at']}")
        st.markdown("---")

    max_mb = config.get_max_file_mb()
    doc_type = st.selectbox("Document Type *", ["id_proof", "insurance_card"], key="doc_type_sel")
    uploaded_file = st.file_uploader(
        f"File Choose Karen ({max_mb}MB max — JPG/PNG/PDF)",
        type=["jpg", "jpeg", "png", "pdf"],
        key="doc_uploader",
    )

    if uploaded_file is not None:
        if st.button("📤 Document Upload Karen", key="upload_btn"):
            file_bytes = uploaded_file.read()
            original_name = uploaded_file.name
            try:
                safe_name = security.validate_upload(file_bytes, original_name, max_mb)
                _, ext = os.path.splitext(safe_name)
                security.save_upload(file_bytes, safe_name)
                db.save_document(
                    request_id=request_id,
                    doc_type=doc_type,
                    filename_stored=safe_name,
                    original_ext=ext.lstrip("."),
                    file_size=len(file_bytes),
                )
                db.audit_log(request_id, "family", "document_uploaded",
                             f"doc_type={doc_type} size_bytes={len(file_bytes)}")
                st.success(f"✅ Document upload ho gaya! ({doc_type})")
                time.sleep(1)
                st.rerun()
            except security.FileValidationError as fve:
                st.error(f"❌ File validation failed: {fve}")
            except Exception as ex:
                st.error(f"Upload error: {ex}")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tab 3 — Payment
# ---------------------------------------------------------------------------

def _render_payment_tab(request_id: int, req: dict, current_status: str) -> None:
    st.markdown('<div class="adm-step"><h3>💳 Online Payment</h3>', unsafe_allow_html=True)

    # Disclaimer — mandatory, always first
    st.markdown("""
    <div class="adm-disclaimer">
      <b>⚠️ Emergency Treatment Payment ka Wait NAHI Karega.</b><br>
      Yeh sirf admission deposit / formalities ke liye hai.<br>
      Aap hospital mein aake bhi pay kar sakte hain.
    </div>
    """, unsafe_allow_html=True)

    deposit_paise = req.get("deposit_amount_paise")
    if not deposit_paise:
        st.info("💡 Hospital staff ne abhi deposit amount set nahi kiya. Thodi der baad check karein ya hospital se sampark karein.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    amount_rupees = deposit_paise / 100.0
    st.markdown(f"**Admission Deposit Amount: ₹{amount_rupees:,.2f}**")
    st.caption("Amount hospital staff ne set kiya hai — yeh badla nahi ja sakta.")

    if current_status == "paid":
        st.markdown('<div class="adm-success">✅ Payment already received. Receipt tab mein download karein.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    existing_payment = db.get_payment(request_id)
    if existing_payment and existing_payment.get("pay_later"):
        st.info("ℹ️ Aapne 'Pay Later' choose kiya tha. Online pay karne ke liye neeche button use karein.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💳 Online Pay Karen (Razorpay)", type="primary", key="pay_online_btn"):
            _handle_online_payment(request_id, deposit_paise, req)

    with col2:
        if st.button("🏥 Hospital Mein Jakar Pay Karunga/Karungi", key="pay_later_btn"):
            try:
                db.mark_pay_later(request_id)
                db.audit_log(request_id, "family", "pay_later_chosen")
                st.info("✅ Noted. Aap hospital counter par payment kar sakte hain.")
            except Exception as ex:
                st.error(f"Error: {ex}")

    # Show existing payment link if exists
    if existing_payment and existing_payment.get("short_url") and existing_payment.get("status") not in ("paid", "failed", "cancelled"):
        st.markdown("---")
        st.markdown(f"**Payment Link:** [{existing_payment['short_url']}]({existing_payment['short_url']})")
        st.caption("QR code ya link se pay karen. Razorpay ka secure page hai.")
        if st.button("🔄 Payment Status Check Karen", key="check_status_btn"):
            _check_payment_status(request_id)

    st.markdown('</div>', unsafe_allow_html=True)


def _handle_online_payment(request_id: int, deposit_paise: int, req: dict) -> None:
    with st.spinner("Payment link create ho raha hai..."):
        try:
            result = payments.get_or_create_payment_link(
                request_id=request_id,
                description=f"Admission Deposit — {req.get('patient_name', 'Patient')}",
            )
            if result.get("already_existed"):
                st.success("✅ Aapka payment link already exist karta hai.")
            else:
                st.success("✅ Payment link create ho gaya!")
            url = result.get("short_url", "")
            if url:
                st.markdown(f"**[👉 Yahan Click Karen Payment Ke Liye]({url})**")
                st.caption("Razorpay secure page par UPI / Card / NetBanking se pay karein.")
            db.audit_log(request_id, "family", "payment_link_accessed",
                         f"link_id={result.get('link_id','')[:8]}")
        except payments.PaymentError as pe:
            st.error(f"❌ Payment Error: {pe}")
        except Exception as ex:
            st.error(f"❌ Unexpected error: {ex}")


def _check_payment_status(request_id: int) -> None:
    with st.spinner("Status verify ho raha hai Razorpay se..."):
        try:
            result = payments.verify_payment_status(request_id)
            status = result.get("status", "")
            if status == "paid":
                st.success("✅ Payment confirmed! Receipt tab mein download karein.")
                time.sleep(1)
                st.rerun()
            elif status == "pay_later":
                st.info("ℹ️ 'Pay Later' select kiya gaya hai.")
            elif status in ("expired", "cancelled"):
                st.warning(f"⚠️ Payment link {status} ho gaya. 'Online Pay Karen' button se nayi link banayein.")
            else:
                st.info(f"⏳ Payment status: {status}. Pay karne ke baad yahan check karein.")
        except payments.PaymentError as pe:
            st.error(f"❌ Status check error: {pe}")


# ---------------------------------------------------------------------------
# Tab 4 — Receipt
# ---------------------------------------------------------------------------

def _render_receipt_tab(request_id: int, req: dict, current_status: str) -> None:
    st.markdown('<div class="adm-step"><h3>📄 Payment Receipt</h3>', unsafe_allow_html=True)

    if current_status != "paid":
        st.info("💡 Receipt sirf payment complete hone ke baad available hogi.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    payment = db.get_payment(request_id)
    if not payment:
        st.warning("Payment record nahi mila. Hospital se sampark karein.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    patient_name = req.get("patient_name", "—")
    hospital_id  = req.get("hospital_id", "—")
    amount_paise = payment.get("amount_paise", 0)
    rz_pay_id    = payment.get("razorpay_payment_id", "—")
    paid_at      = str(payment.get("verified_at", ""))

    st.markdown(f"""
    **Patient:** {patient_name}  
    **Amount Paid:** ₹{amount_paise/100:,.2f}  
    **Payment ID:** {rz_pay_id}  
    **Paid At:** {paid_at}
    """)

    if st.button("📥 Receipt PDF Download Karen", type="primary"):
        try:
            pdf_bytes = receipts.generate_receipt_pdf(
                request_id=request_id,
                patient_name=patient_name,
                hospital_id=hospital_id,
                amount_paise=amount_paise,
                razorpay_payment_id=rz_pay_id,
                paid_at=paid_at,
            )
            st.download_button(
                label="⬇️ Download Receipt PDF",
                data=pdf_bytes,
                file_name=f"JeevanSetu_Receipt_{request_id}.pdf",
                mime="application/pdf",
            )
            db.audit_log(request_id, "family", "receipt_downloaded")
        except Exception as ex:
            st.error(f"Receipt generate karne mein error: {ex}")

    st.markdown('</div>', unsafe_allow_html=True)
