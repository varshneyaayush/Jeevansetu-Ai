"""
admission_portal/portal_app.py
-------------------------------
Standalone Streamlit entry point.

Run:
    streamlit run admission_portal/portal_app.py --server.port 8502

Routing:
    ?view=staff   → Staff dashboard (password protected)
    ?t=<token>    → Family portal (token gated)
    (none)        → Landing page with 1-click demo access to form & staff views
"""
from __future__ import annotations

import os
import sys

# Ensure parent directory is in sys.path so 'admission_portal' can always be imported
_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

import streamlit as st

# Page config MUST be the very first Streamlit call
st.set_page_config(
    page_title="JeevanSetu — Emergency Admission Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

from admission_portal import config, db, family_view, security, staff_view

# Ensure schema is ready on startup (idempotent, safe)
try:
    db.init_schema()
except Exception:
    pass

LANDING_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap');
body, .stApp { background: #F5EFE6; font-family: 'Lato', sans-serif; }
.land-hero {
    background: #1F3D2B; color: #F5EFE6; border-radius: 18px;
    padding: 1.8rem 2.2rem; text-align: center; margin-bottom: 1.5rem;
    border-bottom: 5px solid #8B5CF6;
}
.land-hero h1 { color: #F5EFE6 !important; margin-bottom: 0.3rem; }
.land-hero p  { color: #D3C29E; font-size: 1rem; }
.land-card {
    background:#fff; border:1.5px solid rgba(31,61,43,0.2);
    border-radius:14px; padding:1.2rem 1.4rem; margin-bottom:1rem;
    height: 100%;
}
.land-card h3 { color:#1F3D2B; margin-top:0; }
.land-disc {
    background:#FFF8E1; border-left:6px solid #F59E0B;
    border-radius:8px; padding:0.8rem 1rem; margin:1rem 0;
    font-size:0.9rem; color:#78350F;
}
.demo-banner {
    background: #EDE9FE; border: 1.5px solid #8B5CF6;
    border-radius: 12px; padding: 1rem 1.2rem; margin: 1rem 0;
    text-align: center;
}
</style>
"""


def _get_or_create_demo_token() -> str:
    """Creates a sample demo admission request & token so the user can see the form immediately."""
    reqs = db.list_requests(limit=1)
    if reqs:
        rid = reqs[0]["id"]
    else:
        rid = db.create_request("aiims_trauma", "SOS-2026-8812", "Aarav Sharma")
        db.set_deposit_amount(rid, 500000)  # ₹5,000 deposit

    tp = security.generate_token()
    db.save_token(tp.token_hash, rid, tp.expires_at)
    return tp.raw_token


def render_landing() -> None:
    st.markdown(LANDING_CSS, unsafe_allow_html=True)
    st.markdown("""
    <div class="land-hero">
      <h1>🏥 JeevanSetu AI</h1>
      <h2 style="color:#D3C29E;font-size:1.25rem;font-weight:400;margin:0.2rem 0">
        Emergency Pre-Admission &amp; Online Payment Portal
      </h2>
      <p>Secure Online Admission Form | Instant UPI/Card Deposit | Hospital Staff Management</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="land-disc">
      <b>⚠️ Emergency Treatment Disclaimer:</b> Emergency medical treatment payment par depend nahi karti.
      Yeh portal sirf <b>admission formalities / deposit</b> ke liye hai.<br>
      <i>Treatment has already started / will start regardless of payment status.</i>
    </div>
    """, unsafe_allow_html=True)

    # Quick 1-Click Action Card
    st.markdown("""
    <div class="demo-banner">
      <h3 style="color:#4C1D95;margin:0 0 0.3rem">🚀 Fast Access / Quick Demo</h3>
      <p style="color:#5C6B61;font-size:0.9rem;margin-bottom:0.8rem">
        Neeche diye gaye buttons se seedha <b>Admission Form</b> ya <b>Staff Dashboard</b> open karein:
      </p>
    </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📝 Open Family Admission Form (1-Click Demo)", type="primary", use_container_width=True):
            token = _get_or_create_demo_token()
            st.query_params["t"] = token
            st.rerun()

    with col_btn2:
        if st.button("🔐 Open Hospital Staff View", use_container_width=True):
            st.query_params["view"] = "staff"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Two Main Cards: Family vs Staff
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="land-card">
          <h3>👨‍👩‍👧 Family Member / Attendant</h3>
          <p>Agar hospital ne aapko <b>SMS ya WhatsApp</b> par link bheja hai, to wahi link click karein, ya apna token yahan enter karein:</p>
        """, unsafe_allow_html=True)

        user_token = st.text_input("Enter Token (from URL):", placeholder="e.g. jx9A...32", key="manual_token_inp")
        if st.button("👉 Open My Admission Form", key="open_token_btn"):
            if user_token.strip():
                st.query_params["t"] = user_token.strip()
                st.rerun()
            else:
                st.warning("Pehle token enter karein ya upar '1-Click Demo' button dabayein.")

        st.markdown("""
          <hr style="margin:1rem 0;border-color:rgba(31,61,43,0.15)">
          <b>Family Portal me kya hai:</b>
          <ul style="font-size:0.88rem;color:#1B2B21;margin-top:0.3rem">
            <li>Patient & Attendant details form</li>
            <li>ID proof & Insurance card upload (JPG/PNG/PDF)</li>
            <li>Online Deposit Payment (Razorpay UPI / Card)</li>
            <li>"Pay Later at Hospital" option</li>
            <li>Downloadable Payment Receipt PDF</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="land-card">
          <h3>🏥 Hospital Staff Portal</h3>
          <p>Hospital reception/admission desk ke liye jahan se nayi requests banti hain aur status update hota hai.</p>
          <ul style="font-size:0.88rem;color:#1B2B21;margin-top:0.3rem">
            <li>Generate 48-hour secure family link</li>
            <li>View submitted forms & download documents</li>
            <li>Set deposit amount (₹)</li>
            <li>Server-side Razorpay payment verification</li>
            <li>Tamper-evident audit log</li>
          </ul>
          <hr style="margin:1.4rem 0 1rem;border-color:rgba(31,61,43,0.15)">
        """, unsafe_allow_html=True)
        if st.button("Go to Staff Login", key="staff_login_redirect", use_container_width=True):
            st.query_params["view"] = "staff"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;color:#5C6B61;font-size:0.82rem">
      JeevanSetu AI &bull; Emergency Pre-Admission &amp; Payment Portal &bull; Team Optimove 2026<br>
      <i>"A place where minutes don't cost lives."</i>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar Navigation (Always accessible)
# ---------------------------------------------------------------------------

def render_sidebar(current_view: str, current_token: str) -> None:
    with st.sidebar:
        st.markdown("### 🏥 Admission Portal")
        options = ["🏠 Portal Home", "📝 Family Admission Form", "🔐 Hospital Staff Dashboard"]

        if current_view == "staff":
            default_idx = 2
        elif current_token:
            default_idx = 1
        else:
            default_idx = 0

        choice = st.radio(
            "Navigation:",
            options,
            index=default_idx,
            key="portal_nav_radio",
            label_visibility="collapsed",
        )

        st.markdown("---")
        if choice == "🏠 Portal Home" and (current_view or current_token):
            if st.button("⬅️ Back to Home", use_container_width=True):
                st.query_params.clear()
                st.rerun()
        elif choice == "📝 Family Admission Form" and not current_token:
            if st.button("🚀 Load Admission Form", type="primary", use_container_width=True):
                token = _get_or_create_demo_token()
                st.query_params["t"] = token
                if "view" in st.query_params:
                    del st.query_params["view"]
                st.rerun()
        elif choice == "🔐 Hospital Staff Dashboard" and current_view != "staff":
            if st.button("🔑 Switch to Staff View", use_container_width=True):
                st.query_params["view"] = "staff"
                if "t" in st.query_params:
                    del st.query_params["t"]
                st.rerun()

        st.markdown("---")
        st.caption("🔒 **Security:** Tokens expire in 48 hours. Medical/ID data is private.")


# ---------------------------------------------------------------------------
# Main Router
# ---------------------------------------------------------------------------

def main() -> None:
    if not config.is_portal_enabled():
        st.error("🚫 Admission Portal is currently disabled (ENABLE_ADMISSION_PORTAL=false).")
        return

    params = st.query_params
    view = params.get("view", "")
    token = params.get("t", "")

    render_sidebar(view, token)

    if view == "staff":
        staff_view.render()
    elif token:
        family_view.render(token=token)
    else:
        render_landing()


if __name__ == "__main__":
    main()
