"""
admission_portal/staff_view.py
-------------------------------
Hospital staff dashboard — password-protected.
Features: view submissions, update status, set deposit, generate family links.
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
    from admission_portal import config, db, payments, security
except ImportError:
    import config, db, payments, security

STAFF_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap');
body, .stApp { background: #F0F4F8; font-family: 'Lato', sans-serif; }
.staff-header {
    background: #1F3D2B; color: #F5EFE6; border-radius: 14px;
    padding: 1.1rem 1.4rem; margin-bottom: 1.2rem;
    border-bottom: 4px solid #8B5CF6;
}
.staff-header h2 { color: #F5EFE6 !important; margin: 0; }
.staff-header p  { color: #D3C29E; margin: 0.2rem 0 0; font-size: 0.85rem; }
.staff-card {
    background: #fff; border: 1.5px solid rgba(31,61,43,0.2);
    border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.9rem;
}
.staff-badge {
    display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px;
    font-weight: 700; font-size: 0.8rem;
}
.s-pending        { background:#FEF3C7; color:#92400E; }
.s-submitted      { background:#DBEAFE; color:#1E3A8A; }
.s-under_review   { background:#EDE9FE; color:#4C1D95; }
.s-confirmed      { background:#D1FAE5; color:#065F46; }
.s-payment_pending{ background:#FEE2E2; color:#991B1B; }
.s-paid           { background:#D1FAE5; color:#065F46; }
</style>
"""

VALID_STATUSES = ["pending", "submitted", "under_review", "confirmed", "payment_pending", "paid"]

STATUS_DISPLAY = {
    "pending":         "⏳ Pending",
    "submitted":       "📋 Submitted",
    "under_review":    "🔍 Under Review",
    "confirmed":       "✅ Confirmed",
    "payment_pending": "💳 Payment Pending",
    "paid":            "✅ Paid",
}


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def render() -> None:
    st.markdown(STAFF_CSS, unsafe_allow_html=True)
    st.markdown("""
    <div class="staff-header">
      <h2>🏥 JeevanSetu — Staff Dashboard</h2>
      <p>Emergency Pre-Admission Management Portal | Hospital Staff Only</p>
    </div>
    """, unsafe_allow_html=True)

    if not config.is_staff_view_enabled():
        st.error("🚫 Staff view is currently disabled. Set ENABLE_STAFF_VIEW=true to enable.")
        return

    # Session auth check
    if not _is_authenticated():
        _render_login()
        return

    _render_dashboard()


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def _is_authenticated() -> bool:
    login_time = st.session_state.get("_staff_login_time")
    return security.is_staff_session_valid(login_time)


def _render_login() -> None:
    st.subheader("🔐 Staff Login")
    st.caption("Sirf authorized hospital staff ke liye.")

    # Rate limiting using a session-based key
    ip_key = st.session_state.get("_staff_ip_key", "staff_anon")
    if not st.session_state.get("_staff_ip_key"):
        import secrets as _s
        ip_key = _s.token_hex(6)
        st.session_state["_staff_ip_key"] = ip_key
    ip_hash = security.hash_ip(ip_key)

    blocked, wait_secs = security.check_rate_limit(ip_hash)
    if blocked:
        st.error(f"⛔ Bahut zyada galat attempts. {wait_secs // 60 + 1} minute baad try karein.")
        return

    with st.form("staff_login_form"):
        password = st.text_input("Password", type="password", placeholder="Staff password")
        login_btn = st.form_submit_button("Login", type="primary")

    if login_btn:
        if not password:
            st.error("Password zaroori hai.")
            return
        if not config.get_staff_password():
            st.error("ADM_STAFF_PASSWORD environment variable set nahi hai. Admin se sampark karein.")
            return
        if security.verify_staff_password(password):
            security.reset_rate_limit(ip_hash)
            st.session_state["_staff_login_time"] = time.time()
            db.audit_log(None, "staff", "staff_login", "Staff dashboard access granted")
            st.success("✅ Login successful!")
            time.sleep(0.5)
            st.rerun()
        else:
            security.check_rate_limit(ip_hash)  # count failed attempt
            st.error("❌ Galat password. Phir try karein.")


# ---------------------------------------------------------------------------
# Main dashboard
# ---------------------------------------------------------------------------

def _render_dashboard() -> None:
    timeout_min = config.get_session_timeout_minutes()
    login_time = st.session_state.get("_staff_login_time", time.time())
    remaining = int(timeout_min * 60 - (time.time() - login_time))

    col1, col2 = st.columns([5, 1])
    with col1:
        st.caption(f"Session expires in ~{remaining // 60} min. Auto logout after {timeout_min} min inactivity.")
    with col2:
        if st.button("Logout", key="staff_logout"):
            db.audit_log(None, "staff", "staff_logout")
            st.session_state.pop("_staff_login_time", None)
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["📋 Requests", "➕ Generate Link", "📊 Audit Log"])

    with tab1:
        _render_requests_tab()
    with tab2:
        _render_generate_link_tab()
    with tab3:
        _render_audit_tab()


# ---------------------------------------------------------------------------
# Tab 1 — Request list
# ---------------------------------------------------------------------------

def _render_requests_tab() -> None:
    st.subheader("All Admission Requests")

    filter_status = st.selectbox(
        "Filter by Status", ["All"] + VALID_STATUSES, key="staff_status_filter"
    )

    requests = db.list_requests(limit=200)
    if filter_status != "All":
        requests = [r for r in requests if r.get("status") == filter_status]

    if not requests:
        st.info("Koi requests nahi mili.")
        return

    st.caption(f"Total: {len(requests)} request(s)")

    for req in requests:
        _render_request_card(req)


def _render_request_card(req: dict) -> None:
    rid = req["id"]
    status = req.get("status", "pending")
    badge_cls = f"s-{status}"
    status_label = STATUS_DISPLAY.get(status, status)

    with st.expander(f"Request #{rid} — {req.get('patient_name', 'N/A')} | {status_label}", expanded=False):
        st.markdown(f"""
        <div class="staff-card">
          <b>Hospital ID:</b> {req.get('hospital_id','—')} &nbsp;|&nbsp;
          <b>Incident Ref:</b> {req.get('incident_ref','—')}<br>
          <b>Patient:</b> {req.get('patient_name','—')}<br>
          <b>Created:</b> {req.get('created_at','—')} &nbsp;|&nbsp;
          <b>Updated:</b> {req.get('updated_at','—')}<br>
          <span class="staff-badge {badge_cls}">{status_label}</span>
        </div>
        """, unsafe_allow_html=True)

        # Form details
        form = db.get_form(rid)
        if form:
            with st.expander("📋 Submitted Form Details"):
                st.markdown(f"""
                **Patient:** {form.get('patient_name','—')} | DOB: {form.get('patient_dob','—')} | Gender: {form.get('patient_gender','—')}  
                **Attendant:** {form.get('attendant_name','—')} ({form.get('attendant_relation','—')})  
                **Phone:** {form.get('attendant_phone','—')} | Email: {form.get('attendant_email','—')}  
                **Insurance:** {form.get('insurance_provider','—')} / {form.get('insurance_policy_no','—')}  
                **Emergency Contact:** {form.get('emergency_contact_name','—')} — {form.get('emergency_contact_phone','—')}  
                **Consent:** {'✅ Yes' if form.get('consent_given') else '❌ No'} | Submitted: {form.get('submitted_at','—')}
                """)
        else:
            st.caption("⏳ Family ne abhi form submit nahi kiya.")

        # Documents
        docs = db.list_documents(rid)
        if docs:
            with st.expander(f"📎 Documents ({len(docs)})"):
                for doc in docs:
                    st.markdown(f"- `{doc['doc_type']}` — {doc['original_ext'].upper()}, "
                                f"{doc['file_size_bytes']//1024} KB — {doc['uploaded_at']}")
                    # Staff can read file from uploads dir
                    uploads_dir = config.get_uploads_dir()
                    file_path = os.path.join(uploads_dir, doc["filename_stored"])
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            file_bytes = f.read()
                        ext = doc["original_ext"].lower()
                        mime = "application/pdf" if ext == "pdf" else f"image/{ext}"
                        st.download_button(
                            f"⬇️ Download {doc['doc_type']}",
                            data=file_bytes,
                            file_name=f"{doc['doc_type']}.{doc['original_ext']}",
                            mime=mime,
                            key=f"dl_doc_{doc['id']}",
                        )

        st.markdown("---")
        # Controls
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Update Status**")
            new_status = st.selectbox(
                "Status", VALID_STATUSES,
                index=VALID_STATUSES.index(status) if status in VALID_STATUSES else 0,
                key=f"status_sel_{rid}",
                label_visibility="collapsed",
            )
            if st.button(f"✅ Status Update Karen", key=f"update_status_{rid}"):
                try:
                    db.update_request_status(rid, new_status)
                    db.audit_log(rid, "staff", "status_updated", f"new_status={new_status}")
                    st.success(f"Status updated to '{new_status}'")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")

        with col_b:
            st.markdown("**Deposit Amount Set Karen (₹)**")
            current_deposit = req.get("deposit_amount_paise")
            current_rupees = (current_deposit / 100.0) if current_deposit else 0.0
            deposit_rupees = st.number_input(
                "Amount (₹)",
                min_value=0.0, max_value=1000000.0,
                value=current_rupees, step=100.0,
                key=f"deposit_inp_{rid}",
                label_visibility="collapsed",
            )
            if st.button("💰 Deposit Set Karen", key=f"set_deposit_{rid}"):
                paise = int(round(deposit_rupees * 100))
                if paise < 100:
                    st.error("Minimum ₹1 (100 paise) chahiye.")
                else:
                    try:
                        db.set_deposit_amount(rid, paise)
                        db.audit_log(rid, "staff", "deposit_amount_set", f"amount_paise={paise}")
                        st.success(f"Deposit set: ₹{deposit_rupees:,.2f}")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error: {ex}")

        # Payment status
        payment = db.get_payment(rid)
        if payment:
            st.markdown("**Payment Status:**")
            pay_status = payment.get("status", "—")
            st.markdown(f"Status: `{pay_status}` | Link ID: `{payment.get('razorpay_link_id','—')[:16]}...`")
            if payment.get("razorpay_link_id") and pay_status not in ("paid", "cancelled"):
                if st.button("🔄 Payment Verify Karen (Razorpay)", key=f"verify_pay_{rid}"):
                    try:
                        result = payments.verify_payment_status(rid)
                        st.info(f"Razorpay status: {result.get('status')}")
                        time.sleep(0.5)
                        st.rerun()
                    except payments.PaymentError as pe:
                        st.error(f"Payment verify error: {pe}")


# ---------------------------------------------------------------------------
# Tab 2 — Generate family link
# ---------------------------------------------------------------------------

def _render_generate_link_tab() -> None:
    st.subheader("➕ Nayi Admission Request + Family Link Generate Karen")
    st.caption("Staff yahan se ek nayi admission request create karke family ko secure link bhej sakta hai.")

    with st.form("gen_link_form"):
        hospital_id    = st.text_input("Hospital ID *", placeholder="manipal_dwarka / aiims")
        incident_ref   = st.text_input("Incident / SOS Reference (optional)", placeholder="SOS-123456")
        patient_name   = st.text_input("Patient Name (if known)", placeholder="Aarav Sharma")
        base_url       = st.text_input(
            "Portal Base URL *",
            placeholder="https://your-portal.streamlit.app",
            help="Yeh URL family ko bheja jayega. Apna deployed URL enter karein.",
        )
        generate_btn = st.form_submit_button("🔗 Link Generate Karen", type="primary")

    if generate_btn:
        if not hospital_id.strip():
            st.error("Hospital ID zaroori hai.")
            return
        if not base_url.strip():
            st.error("Portal Base URL zaroori hai.")
            return

        try:
            # Create request
            rid = db.create_request(
                hospital_id=hospital_id.strip(),
                incident_ref=incident_ref.strip(),
                patient_name=patient_name.strip(),
            )

            # Generate token
            token_payload = security.generate_token()
            db.save_token(
                token_hash=token_payload.token_hash,
                request_id=rid,
                expires_at=token_payload.expires_at,
            )

            # Build URL
            family_url = security.build_family_url(base_url.strip(), token_payload.raw_token)

            db.audit_log(rid, "staff", "family_link_generated",
                         f"hospital_id={hospital_id.strip()} incident_ref={incident_ref.strip()[:20]}")

            st.success(f"✅ Admission Request #{rid} create ho gaya!")
            st.markdown("**Family Portal Link:**")
            st.code(family_url, language=None)
            st.caption(
                f"⚠️ Yeh link sirf ek baar dikhaya ja raha hai. Copy karke WhatsApp/SMS se family ko bhejein.\n"
                f"Link 48 ghante tak valid rahega (expires: {token_payload.expires_at.strftime('%d %b %Y %H:%M')} UTC)."
            )

            # WhatsApp copy helper
            wa_msg = (
                f"JeevanSetu Hospital Admission Portal\n"
                f"Request #{rid} — {patient_name or 'Patient'}\n"
                f"Yeh link use karke admission form bharen aur payment karein:\n{family_url}\n"
                f"(Link 48 hrs mein expire hoga)"
            )
            st.markdown("**WhatsApp/SMS ke liye copy karein:**")
            st.text_area("Message", wa_msg, height=120, key="wa_msg_box")

        except Exception as ex:
            st.error(f"Link generate karne mein error: {ex}")


# ---------------------------------------------------------------------------
# Tab 3 — Audit log
# ---------------------------------------------------------------------------

def _render_audit_tab() -> None:
    st.subheader("📊 Audit Log")
    st.caption("Recent 50 actions. Medical/ID data kabhi log nahi hota.")

    rid_filter = st.number_input("Request ID se filter (0 = sab)", min_value=0, value=0, key="audit_rid_filter")
    logs = db.list_audit(request_id=int(rid_filter) if rid_filter else None, limit=50)

    if not logs:
        st.info("Koi audit entries nahi mili.")
        return

    for entry in logs:
        st.markdown(
            f"`{entry.get('created_at','')}` — "
            f"**{entry.get('actor','')}** → `{entry.get('action','')}` "
            f"| req #{entry.get('request_id','—')} | {entry.get('detail','')}"
        )


# ---------------------------------------------------------------------------
# os import needed for file download
# ---------------------------------------------------------------------------
import os
