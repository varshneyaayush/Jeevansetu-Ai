# Emergency Pre-Admission & Online Payment Portal
## JeevanSetu AI — `admission_portal/`

> **Standalone** Streamlit app — completely independent of `app.py`.  
> Family: online admission form + deposit payment via Razorpay Payment Links.  
> Staff: manage requests, set deposit, generate secure family links.

---

## Table of Contents
1. [Quick Start (Local Dev)](#1-quick-start-local-dev)
2. [Environment Variables](#2-environment-variables)
3. [Database Setup](#3-database-setup)
4. [Run Commands](#4-run-commands)
5. [Deploy to Streamlit Cloud (PostgreSQL)](#5-deploy-to-streamlit-cloud-postgresql)
6. [Persistent Storage for Uploads](#6-persistent-storage-for-uploads)
7. [Staff Workflow](#7-staff-workflow)
8. [Family Workflow](#8-family-workflow)
9. [Rollback](#9-rollback)
10. [Security Notes](#10-security-notes)

---

## 1. Quick Start (Local Dev)

```bash
# 1. Go to project root
cd JeevanSetu-AI-main

# 2. Install portal dependencies (separate from main app)
pip install -r admission_portal/requirements-admission.txt

# 3. Set env vars (PowerShell)
$env:ADM_STAFF_PASSWORD = "YourSecurePassword123"
# Razorpay test keys (get from dashboard.razorpay.com)
$env:RAZORPAY_KEY_ID     = "rzp_test_XXXXXXXXXXXXXXXX"
$env:RAZORPAY_KEY_SECRET = "your_razorpay_test_secret"

# 4. Init database (SQLite — auto-created at admission_portal/data/portal.db)
python -m admission_portal.db --init-schema

# 5. Run portal (separate port from main app)
streamlit run admission_portal/portal_app.py --server.port 8502
```

**Main app remains unchanged on its own port:**
```bash
streamlit run app.py --server.port 8501
```

---

## 2. Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | No | — | PostgreSQL DSN (e.g. `postgresql://user:pass@host/db`). If not set → SQLite at `admission_portal/data/portal.db` |
| `RAZORPAY_KEY_ID` | Yes* | — | Razorpay API Key ID (`rzp_test_...` for test mode) |
| `RAZORPAY_KEY_SECRET` | Yes* | — | Razorpay API Key Secret |
| `ADM_STAFF_PASSWORD` | Yes | — | Staff dashboard login password |
| `ENABLE_ADMISSION_PORTAL` | No | `true` | Master on/off flag |
| `ENABLE_STAFF_VIEW` | No | `true` | Disable staff view independently |
| `ENABLE_OTP_HOOK` | No | `false` | Phone OTP verification (mock in dev) |
| `ADM_TOKEN_EXPIRY_HOURS` | No | `48` | Family link expiry |
| `ADM_MAX_FILE_MB` | No | `5` | Max upload file size in MB |
| `ADM_SESSION_TIMEOUT_MINUTES` | No | `30` | Staff session timeout |

> **\* Required** only when payment feature is used. Without Razorpay keys, payment links cannot be created (error shown to user).

> ⚠️ **Never** hardcode keys. Use `.env` file (local) or `st.secrets` / Streamlit Cloud secrets (prod).

### Streamlit Secrets Format (`.streamlit/secrets.toml` — gitignored)
```toml
RAZORPAY_KEY_ID     = "rzp_test_XXXXXXXXXXXXXXXX"
RAZORPAY_KEY_SECRET = "your_secret"
ADM_STAFF_PASSWORD  = "YourSecurePassword"
DATABASE_URL        = "postgresql://user:pass@host:5432/dbname"
```

---

## 3. Database Setup

### Schema (run once — creates all `adm_*` tables)
```bash
# SQLite (dev)
python -m admission_portal.db --init-schema

# PostgreSQL (prod)
DATABASE_URL="postgresql://..." python -m admission_portal.db --init-schema
# OR directly:
psql $DATABASE_URL -f admission_portal/schema.sql
```

> **Important:** Schema only creates `adm_*` tables. Existing tables in your DB are **never touched**.

### Supported Databases
| Environment | DB | Notes |
|---|---|---|
| Local Dev | **SQLite** | Auto-created at `admission_portal/data/portal.db` (gitignored) |
| Staging / Prod | **PostgreSQL** | Set `DATABASE_URL` env var |

---

## 4. Run Commands

```bash
# Portal (family + staff, port 8502)
streamlit run admission_portal/portal_app.py --server.port 8502

# URLs:
#   Landing page:  http://localhost:8502/
#   Staff view:    http://localhost:8502/?view=staff
#   Family view:   http://localhost:8502/?t=<raw_token>

# Run tests
cd JeevanSetu-AI-main
pytest admission_portal/tests/ -v

# Run tests with coverage
pytest admission_portal/tests/ -v --tb=short
```

---

## 5. Deploy to Streamlit Cloud (PostgreSQL)

Streamlit Cloud ka disk **ephemeral** hai — SQLite data restarts ke baad delete ho jata hai.  
**Live deploy ke liye PostgreSQL zaroori hai.**

### Free PostgreSQL Options
| Service | Free Tier | Notes |
|---|---|---|
| [Neon](https://neon.tech) | 0.5 GB free | Serverless PostgreSQL, easy setup |
| [Supabase](https://supabase.com) | 500 MB free | PostgreSQL + dashboard |
| [ElephantSQL](https://www.elephantsql.com) | 20 MB free | Simple, no frills |

### Setup Steps
1. Create a PostgreSQL DB on Neon/Supabase
2. Copy the connection string (DSN format: `postgresql://user:pass@host/db`)
3. In Streamlit Cloud app settings → **Secrets**:
   ```toml
   DATABASE_URL        = "postgresql://user:pass@neon-host/dbname?sslmode=require"
   RAZORPAY_KEY_ID     = "rzp_live_XXXXXXXXXXXXXXXX"
   RAZORPAY_KEY_SECRET = "your_live_secret"
   ADM_STAFF_PASSWORD  = "YourStrongPassword"
   ```
4. Run schema init (from local machine, with `DATABASE_URL` set):
   ```bash
   DATABASE_URL="postgresql://..." python -m admission_portal.db --init-schema
   ```
5. Deploy:
   - Set **Main file path** to `admission_portal/portal_app.py`
   - Set **Python version** to 3.14 (or latest available)

### Razorpay Live Mode
- Replace `rzp_test_*` keys with `rzp_live_*` keys from [Razorpay Dashboard](https://dashboard.razorpay.com)
- Test thoroughly on test mode before switching to live

---

## 6. Persistent Storage for Uploads

Uploaded ID documents are stored in `admission_portal/uploads/` (private, gitignored).

| Environment | Storage Solution |
|---|---|
| Local Dev | Local filesystem (`admission_portal/uploads/`) |
| Streamlit Cloud | ⚠️ Ephemeral disk — files lost on restart |

### Streamlit Cloud Upload Solution
For persistent uploads on Streamlit Cloud, integrate an object storage service:

**Option A — Supabase Storage** (if using Supabase DB):
```python
# In security.save_upload(), replace local write with:
supabase.storage.from_("admission-docs").upload(safe_filename, file_bytes)
```

**Option B — AWS S3 / Google Cloud Storage:**
```python
import boto3
s3 = boto3.client("s3")
s3.put_object(Bucket="your-bucket", Key=safe_filename, Body=file_bytes)
```

**Option C — Cloudflare R2** (free tier, S3-compatible)

> Until cloud storage is integrated, `save_upload()` works locally. For cloud deploy, modify `security.save_upload()` and `staff_view.py` download logic to use your chosen object store.

---

## 7. Staff Workflow

1. Open portal at `https://<your-portal-url>/?view=staff`
2. Enter `ADM_STAFF_PASSWORD`
3. Go to **"Generate Link"** tab:
   - Enter Hospital ID, Incident Reference, Patient Name
   - Enter Portal Base URL (your Streamlit Cloud URL)
   - Click **"Generate Link"** → Copy the family URL
4. Send URL via WhatsApp/SMS to family member
5. In **"Requests"** tab: monitor submitted forms, set deposit amount, update status
6. Use **"Payment Verify Karen"** to server-side check Razorpay payment status
7. Session auto-expires after 30 minutes (configurable)

---

## 8. Family Workflow

1. Family receives a secure link: `https://<portal-url>/?t=TOKEN`
2. Opens link on mobile browser
3. **Tab 1 — Admission Form:** Fills patient + attendant details, insurance info, emergency contact; checks consent checkbox → Submit
4. **Tab 2 — Documents:** Uploads ID proof / insurance card (JPG/PNG/PDF, max 5 MB)
5. **Tab 3 — Payment:** 
   - Views deposit amount (set by staff)
   - Clicks **"Online Pay Karen"** → Razorpay Payment Link opens (UPI/Card/NetBanking)
   - OR clicks **"Hospital Mein Jakar Pay Karunga"** (pay later)
   - **"Check Payment Status"** button verifies payment server-side
6. **Tab 4 — Receipt:** Downloads PDF receipt after payment confirmed

> ⚠️ Disclaimer always visible: *"Emergency treatment payment ka wait nahi karega."*

---

## 9. Rollback

To completely remove all admission portal tables:

```bash
# Interactive (confirms before dropping)
python -m admission_portal.db --rollback

# Direct SQL (PostgreSQL)
psql $DATABASE_URL -f admission_portal/rollback.sql

# SQLite: simply delete the file
rm admission_portal/data/portal.db
```

> **Rollback only drops `adm_*` tables.** No other tables are touched. Main `app.py` is unaffected.

---

## 10. Security Notes

| Concern | Implementation |
|---|---|
| Family token | `secrets.token_urlsafe(32)` → SHA-256 hash in DB; raw token only in URL once |
| Token expiry | 48 hours (configurable via `ADM_TOKEN_EXPIRY_HOURS`) |
| Rate limiting | 5 wrong attempts → 15 min lockout (IP hash based) |
| Staff auth | `hmac.compare_digest()` constant-time compare; session timeout 30 min |
| File validation | Extension whitelist + magic bytes check; UUID filename; private folder |
| Payment amount | Always from DB (`adm_requests.deposit_amount_paise`), never from client |
| Idempotency | One active Razorpay Payment Link per request |
| Client callbacks | Never trusted — status verified via server-side Razorpay API only |
| Data logging | Medical/ID data never logged — only non-sensitive metadata in `adm_audit_log` |
| Card/UPI data | Never stored — only `link_id` / `payment_id` / `status` |
| Consent | Mandatory checkbox before form submission |
| Public URLs | Uploaded files have no public URL — served only to authenticated staff |

---

## File Structure

```
admission_portal/
├── __init__.py
├── portal_app.py              ← Entry point
├── config.py                  ← Env/secrets
├── db.py                      ← DB layer (SQLite/PostgreSQL)
├── family_view.py             ← Family portal UI
├── staff_view.py              ← Staff dashboard UI
├── payments.py                ← Razorpay Payment Links API
├── receipts.py                ← PDF receipt (fpdf2 + fallback)
├── security.py                ← Token, rate-limit, file validation
├── schema.sql                 ← CREATE TABLE IF NOT EXISTS
├── rollback.sql               ← DROP TABLE (adm_* only)
├── requirements-admission.txt ← razorpay, fpdf2, psycopg2-binary
├── README_ADMISSION.md        ← This file
├── data/                      ← SQLite DB (gitignored)
│   └── portal.db
├── uploads/                   ← Private document storage (gitignored)
│   └── .gitkeep
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_security.py
    ├── test_forms.py
    ├── test_payments.py
    └── test_staff_auth.py
```

---

*JeevanSetu AI — "A place where minutes don't cost lives." | Team Optimove | Roboforge 2026*
