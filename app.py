"""
JeevanSetu AI - "A place where minutes don't cost lives."
Team Optimove | Roboforge Hackathon 2026 | Software & Intelligent Systems | Healthcare AI
Team Members: Aayush Varshney, Sonali, Aksha Malik, Diksha Kalia

Comprehensive Multi-Role Streamlit Application featuring:
  1. Professional Role-Based Authentication with 1-Click Demo Logins
  2. Role A: Bystander Emergency SOS (Zero Barrier, No Login Required) with AI Triage Engine & Weighted Hospital Matcher
  3. Role B: Patient Portal & Personal Medical Memory (Consultation, Timeline, Downloadable Reports Hub, RAG Search, OCR)
  4. Role C: Doctor & Hospital Medical Team Dashboard (Patient Write Portal, Diagnoses, Report PDF Uploads, Emergency Pre-Alerts)
  5. Role D: Family Manager & Privacy Control (Emergency Live Tracking, Granular Consent Matrix, Notification Feeds)
  6. Role E: Hospital Admin Command Center (Bed Availability, Workload Scoring, ER Diversions, Network Overview)
  7. SHA-256 Tamper-Evident Hash Chain Audit Log & Pure-Python Medical PDF Report Generator
"""
from __future__ import annotations

import copy
import hashlib
import html as _html
import math
import re
import time
import zlib
from datetime import date, datetime, timedelta, timezone

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="JeevanSetu AI | Team Optimove",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# 1. DESIGN SYSTEM & THEMING (Forest Green & Warm Cream 60/30/10)
# =============================================================================
CREAM = "#F5EFE6"
SAND = "#E8DCC4"
FOREST = "#1F3D2B"
LEAF = "#2F7A55"
VIOLET = "#8B5CF6"
RED = "#DC2626"
INK = "#1B2B21"
MUTED = "#5C6B61"
CARD_BG = "#FFFCF6"
IST = timezone(timedelta(hours=5, minutes=30))

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&family=Lora:ital,wght@0,500;0,600;0,700;1,400&display=swap');

:root {{
    --cream: {CREAM};
    --sand: {SAND};
    --forest: {FOREST};
    --leaf: {LEAF};
    --violet: {VIOLET};
    --red: {RED};
    --ink: {INK};
    --muted: {MUTED};
    --card: {CARD_BG};
}}

.stApp {{
    background-color: var(--cream);
    color: var(--ink);
    font-family: 'Lato', system-ui, -apple-system, sans-serif;
}}

.stApp p, .stApp li, .stApp label, .stApp span {{
    color: var(--ink);
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: 'Lora', Georgia, serif !important;
    color: var(--forest) !important;
    letter-spacing: -0.015em;
}}

header[data-testid="stHeader"] {{
    background: transparent;
}}

#MainMenu, footer {{
    visibility: hidden;
}}

.block-container {{
    padding-top: 1.2rem;
    padding-bottom: 3.5rem;
    max-width: 1300px;
}}

/* ---------- Sidebar (30%: Deep Forest Green) ---------- */
section[data-testid="stSidebar"] {{
    background-color: var(--forest) !important;
    border-right: 3px solid #14281C;
}}

section[data-testid="stSidebar"] * {{
    color: var(--sand) !important;
}}

section[data-testid="stSidebar"] hr {{
    border-color: rgba(232, 220, 196, 0.25) !important;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] label {{
    background: rgba(232, 220, 196, 0.08);
    border: 1px solid rgba(232, 220, 196, 0.25);
    border-radius: 12px;
    padding: 0.55rem 0.85rem;
    margin-bottom: 0.35rem;
    width: 100%;
    transition: all 0.2s ease;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
    background: var(--violet) !important;
    border-color: var(--violet) !important;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * {{
    color: #ffffff !important;
    font-weight: 700 !important;
}}

section[data-testid="stSidebar"] .stButton>button {{
    background: transparent;
    border: 1.5px solid var(--sand);
    color: var(--sand) !important;
    border-radius: 10px;
    font-weight: 700;
    transition: all 0.2s ease;
}}

section[data-testid="stSidebar"] .stButton>button:hover {{
    background: var(--sand) !important;
    color: var(--forest) !important;
    border-color: var(--sand) !important;
}}

section[data-testid="stSidebar"] .stButton>button:hover * {{
    color: var(--forest) !important;
}}

.side-brand {{
    font-family: 'Lora', serif;
    font-size: 1.65rem;
    font-weight: 700;
    color: #F5EFE6 !important;
    line-height: 1.1;
}}

.side-sub {{
    font-size: 0.78rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #D3C29E !important;
    margin-top: 0.2rem;
}}

.side-card {{
    background: rgba(232, 220, 196, 0.09);
    border: 1px solid rgba(232, 220, 196, 0.22);
    border-radius: 12px;
    padding: 0.75rem 0.9rem;
    font-size: 0.86rem;
    line-height: 1.4;
    margin: 0.45rem 0;
}}

.side-chip {{
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 700;
    margin: 0.15rem 0.25rem 0.15rem 0;
    border: 1px solid rgba(232, 220, 196, 0.35);
}}

.side-chip.on-red {{
    background: #DC2626 !important;
    border-color: #DC2626 !important;
    color: #ffffff !important;
}}

.side-chip.on-green {{
    background: #2F7A55 !important;
    border-color: #2F7A55 !important;
    color: #ffffff !important;
}}

/* ---------- Hero Banner ---------- */
.hero {{
    background: var(--forest);
    color: var(--sand);
    border-radius: 18px;
    padding: 1.4rem 1.8rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1.2rem;
    flex-wrap: wrap;
    border-bottom: 5px solid var(--violet);
    box-shadow: 0 4px 14px rgba(31, 61, 43, 0.12);
}}

.hero .eyebrow {{
    font-size: 0.74rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #D3C29E;
    font-weight: 700;
}}

.hero .title {{
    font-family: 'Lora', serif;
    font-size: 2.35rem;
    font-weight: 700;
    color: #F5EFE6 !important;
    line-height: 1.1;
    margin: 0.2rem 0 0.5rem;
}}

.hero .tag {{
    display: inline-block;
    background: var(--leaf);
    color: #ffffff !important;
    border-radius: 999px;
    padding: 0.35rem 1.1rem;
    font-weight: 700;
    font-size: 0.95rem;
}}

.hero .right {{
    text-align: right;
    flex: 1;
    min-width: 270px;
    font-size: 0.88rem;
    color: var(--sand);
}}

.hero .right b {{
    color: #F5EFE6;
}}

/* ---------- Custom Card Styles ---------- */
[class*="st-key-card_"] {{
    background: var(--card);
    border: 1.5px solid var(--forest);
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.95rem;
    box-shadow: 0 3px 0 rgba(31, 61, 43, 0.08);
}}

[class*="st-key-redcard_"] {{
    background: #FFF5F5;
    border: 2px solid var(--red);
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.95rem;
}}

.mcard {{
    background: var(--forest);
    color: var(--sand);
    border-radius: 14px;
    padding: 0.95rem 1.1rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}

.mcard .lbl {{
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #D3C29E;
    font-weight: 700;
}}

.mcard .val {{
    font-family: 'Lora', serif;
    font-size: 1.85rem;
    font-weight: 700;
    color: #F5EFE6;
    line-height: 1.15;
    margin: 0.15rem 0;
}}

.mcard .sub {{
    font-size: 0.82rem;
    color: var(--sand);
    opacity: 0.9;
}}

.mcard.light {{
    background: var(--card);
    border: 1.5px solid var(--forest);
    color: var(--ink);
}}

.mcard.light .lbl {{ color: var(--muted); }}
.mcard.light .val {{ color: var(--forest); }}
.mcard.light .sub {{ color: var(--muted); }}

.mcard.red {{
    background: var(--red);
}}
.mcard.red .lbl, .mcard.red .sub {{ color: #FEE2E2; }}
.mcard.red .val {{ color: #FFFFFF; }}

.mcard.violet {{
    background: var(--violet);
}}
.mcard.violet .lbl, .mcard.violet .sub {{ color: #EDE9FE; }}
.mcard.violet .val {{ color: #FFFFFF; }}

.sect {{
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin: 1.3rem 0 0.55rem;
}}

.sect .num {{
    background: var(--forest);
    color: var(--sand);
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 0.92rem;
    flex: none;
}}

.sect .num.v {{ background: var(--violet); color: #fff; }}
.sect .num.r {{ background: var(--red); color: #fff; }}

.sect .t {{
    font-family: 'Lora', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--forest);
}}

.sect .tagx {{
    border: 1.5px solid var(--violet);
    color: var(--violet);
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 900;
    letter-spacing: 0.1em;
    padding: 0.08rem 0.6rem;
}}

.lead {{
    color: var(--muted);
    font-size: 0.95rem;
    margin: -0.2rem 0 0.65rem;
}}

/* ---------- Badges & Alerts ---------- */
.badge {{
    display: inline-block;
    padding: 0.22rem 0.7rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    margin: 0.12rem 0.25rem 0.12rem 0;
    border: 1.5px solid transparent;
    white-space: nowrap;
}}

.b-critical {{ background: var(--red); color: #fff; }}
.b-high {{ background: #B45309; color: #fff; }}
.b-mod {{ background: #CA8A04; color: #fff; }}
.b-ok {{ background: #DDEBE2; color: #1F3D2B; border-color: var(--leaf); }}
.b-ai {{ background: #EDE9FE; color: #5B21B6; border-color: var(--violet); }}
.b-muted {{ background: var(--sand); color: var(--forest); }}
.b-red-soft {{ background: #FEE2E2; color: #991B1B; border-color: var(--red); }}
.b-dark {{ background: var(--forest); color: var(--sand); }}

.alert-red {{
    background: #FEF2F2;
    border: 2px solid var(--red);
    border-left-width: 10px;
    border-radius: 14px;
    padding: 0.95rem 1.15rem;
    color: #7F1D1D;
    margin: 0.5rem 0 0.75rem;
}}
.alert-red b, .alert-red div {{ color: #7F1D1D; }}
.alert-red .h {{
    font-family: 'Lora', serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #991B1B;
}}

.alert-amber {{
    background: #FFFBEB;
    border: 1.5px solid #D97706;
    border-left-width: 8px;
    border-radius: 12px;
    padding: 0.75rem 1.05rem;
    color: #78350F;
    margin: 0.45rem 0;
}}

.alert-green {{
    background: #ECF6EF;
    border: 1.5px solid #2F7A55;
    border-left-width: 8px;
    border-radius: 12px;
    padding: 0.85rem 1.1rem;
    color: #1F3D2B;
    margin: 0.45rem 0;
}}

.alert-violet {{
    background: #F5F3FF;
    border: 1.5px solid var(--violet);
    border-left-width: 8px;
    border-radius: 12px;
    padding: 0.75rem 1.05rem;
    color: #4C1D95;
    margin: 0.45rem 0;
}}

.note {{
    font-size: 0.82rem;
    color: var(--muted);
    font-style: italic;
}}

/* ---------- Buttons ---------- */
.stButton>button, .stDownloadButton>button {{
    border-radius: 10px;
    font-weight: 700;
    border: 1.5px solid var(--forest);
    background: var(--forest);
    color: var(--sand);
    padding: 0.52rem 1.1rem;
    transition: all 0.15s ease;
}}

.stButton>button:hover, .stDownloadButton>button:hover {{
    background: #2B5740;
    border-color: #2B5740;
    color: #ffffff;
}}

.stButton>button p, .stDownloadButton>button p {{
    color: inherit !important;
    font-weight: 700;
}}

.stButton>button[data-testid="stBaseButton-primary"], .stButton>button[kind="primary"] {{
    background: var(--violet) !important;
    border-color: var(--violet) !important;
    color: #ffffff !important;
}}

.stButton>button[data-testid="stBaseButton-primary"]:hover, .stButton>button[kind="primary"]:hover {{
    background: #7C3AED !important;
    border-color: #7C3AED !important;
}}

[class*="st-key-pill_"] button {{
    background: var(--card);
    color: var(--forest);
    border-radius: 999px;
    border: 1.5px solid var(--forest);
    padding: 0.28rem 0.95rem;
    font-weight: 600;
    font-size: 0.88rem;
}}

[class*="st-key-pill_"] button:hover {{
    background: #EDE9FE;
    border-color: var(--violet);
    color: #4C1D95;
}}

[class*="st-key-sosbtn_"] button {{
    background: var(--red) !important;
    border: 2px solid #B91C1C !important;
    color: #ffffff !important;
    font-size: 1.2rem;
    padding: 1rem 1.1rem;
    letter-spacing: 0.05em;
    box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.55);
    animation: pulse 1.8s infinite;
}}

[class*="st-key-sosbtn_"] button:hover {{
    background: #B91C1C !important;
    border-color: #991B1B !important;
}}

[class*="st-key-sosbtn_"] button p {{
    font-size: 1.15rem;
    font-weight: 900 !important;
    color: #ffffff !important;
}}

[class*="st-key-sosbtn_"] {{
    width: 100%;
}}

[class*="st-key-sosbtn_"] button, [class*="st-key-sosbtn_"] .stButton, [class*="st-key-sosbtn_"] [data-testid="stButton"] {{
    width: 100% !important;
}}

@keyframes pulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.6); }}
    70% {{ box-shadow: 0 0 0 18px rgba(220, 38, 38, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }}
}}

/* ---------- Inputs / Tabs ---------- */
.stTextInput input, .stTextArea textarea, .stNumberInput input, div[data-baseweb="select"]>div {{
    background: #FFFDF8 !important;
    color: var(--ink) !important;
    border-color: rgba(31, 61, 43, 0.45) !important;
    border-radius: 10px !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 0.5rem;
    border-bottom: 2px solid var(--sand);
}}

.stTabs [data-baseweb="tab"] {{
    font-weight: 700;
    color: var(--forest);
    padding: 0.6rem 1.1rem;
    border-radius: 10px 10px 0 0;
}}

.stTabs [data-baseweb="tab"] p {{
    color: var(--forest);
    font-weight: 700;
}}

.stTabs [data-baseweb="tab-highlight"] {{
    background: var(--violet);
    height: 3px;
}}

div[data-testid="stExpander"] {{
    border: 1.5px solid rgba(31, 61, 43, 0.45);
    border-radius: 12px;
    background: var(--card);
}}

div[data-testid="stExpander"] summary p {{
    font-weight: 700;
    color: var(--forest);
}}

div[data-testid="stDataFrame"] {{
    border: 1.5px solid rgba(31, 61, 43, 0.35);
    border-radius: 12px;
    overflow: hidden;
}}

/* ---------- Live Tracker & Timeline ---------- */
.track {{
    position: relative;
    height: 90px;
    margin: 0.4rem 28px 0;
}}

.track .line {{
    position: absolute;
    top: 34px;
    left: 0;
    right: 0;
    height: 8px;
    background: var(--sand);
    border-radius: 99px;
}}

.track .fill {{
    position: absolute;
    top: 34px;
    left: 0;
    height: 8px;
    background: linear-gradient(90deg, #2F7A55, #8B5CF6);
    border-radius: 99px;
}}

.track .node {{
    position: absolute;
    top: 26px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    transform: translateX(-50%);
    border: 3px solid var(--forest);
    background: var(--cream);
}}

.track .node.scene {{ border-color: var(--red); background: #FEE2E2; }}
.track .node.hosp {{ background: var(--forest); }}

.track .nl {{
    position: absolute;
    top: 56px;
    transform: translateX(-50%);
    font-size: 0.74rem;
    font-weight: 700;
    color: var(--forest);
    text-align: center;
    white-space: nowrap;
}}

.track .amb {{
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    font-size: 1.75rem;
}}

.tl-card {{
    border-left: 5px solid var(--forest);
    background: var(--card);
    border-radius: 0 12px 12px 0;
    padding: 0.8rem 1.1rem;
    margin: 0.6rem 0 0.2rem;
    border-top: 1px solid rgba(31, 61, 43, 0.18);
    border-right: 1px solid rgba(31, 61, 43, 0.18);
    border-bottom: 1px solid rgba(31, 61, 43, 0.18);
}}

.tl-card .d {{ font-size: 0.8rem; color: var(--muted); font-weight: 700; }}
.tl-card .tt {{ font-family: 'Lora', serif; font-weight: 700; color: var(--forest); font-size: 1.1rem; }}
.tl-card.lab {{ border-left-color: var(--violet); }}
.tl-card.rx {{ border-left-color: var(--leaf); }}
.tl-card.dc {{ border-left-color: #B45309; }}
.tl-card.note {{ border-left-color: #0284C7; }}

.profile {{
    display: flex;
    gap: 1.1rem;
    align-items: center;
    flex-wrap: wrap;
}}

.avatar {{
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: var(--forest);
    color: var(--sand);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Lora', serif;
    font-weight: 700;
    font-size: 1.45rem;
    flex: none;
}}

.cite {{
    display: inline-block;
    background: #EDE9FE;
    color: #4C1D95;
    border: 1px solid var(--violet);
    border-radius: 8px;
    padding: 0.12rem 0.55rem;
    font-size: 0.78rem;
    font-weight: 700;
    margin: 0.15rem 0.25rem 0.15rem 0;
}}

.ans {{
    background: var(--card);
    border: 1.5px solid var(--violet);
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
}}

.hosp-best {{
    background: var(--forest);
    color: var(--sand);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    border: 2px solid var(--violet);
}}

.hosp-best .nm {{
    font-family: 'Lora', serif;
    font-size: 1.55rem;
    font-weight: 700;
    color: #F5EFE6;
}}

.hosp-best .score {{
    font-family: 'Lora', serif;
    font-size: 2.7rem;
    font-weight: 700;
    color: #C4B5FD;
    line-height: 1;
}}

.hosp-best li, .hosp-best div {{
    color: var(--sand);
}}

.lock {{
    background: repeating-linear-gradient(45deg, #EFE7D6, #EFE7D6 10px, #E8DCC4 10px, #E8DCC4 20px);
    border: 1.5px dashed var(--forest);
    border-radius: 12px;
    padding: 1.1rem;
    text-align: center;
    color: var(--forest);
    font-weight: 700;
}}

.kv {{
    display: grid;
    grid-template-columns: 160px 1fr;
    gap: 0.3rem 0.9rem;
    font-size: 0.93rem;
}}
.kv .k {{ color: var(--muted); font-weight: 700; }}

.footer {{
    margin-top: 2.5rem;
    padding-top: 1rem;
    border-top: 2px solid var(--sand);
    font-size: 0.82rem;
    color: var(--muted);
    text-align: center;
}}
</style>
"""


def H(s: str) -> str:
    return "\n".join(line.strip() for line in s.strip().splitlines() if line.strip())


def md(s: str) -> None:
    st.markdown(H(s), unsafe_allow_html=True)


def esc(x) -> str:
    return _html.escape(str(x))


def badge(text: str, kind: str = "muted") -> str:
    return f'<span class="badge b-{kind}">{esc(text)}</span>'


def section(num, title: str, tag: str | None = None, color: str = "") -> None:
    t = f'<span class="tagx">{esc(tag)}</span>' if tag else ""
    n = f'<div class="num {color}">{num}</div>' if str(num) else ""
    md(f'<div class="sect">{n}<div class="t">{esc(title)}</div>{t}</div>')


def mcard(label, value, sub="", kind="") -> str:
    return f'<div class="mcard {kind}"><div class="lbl">{esc(label)}</div><div class="val">{value}</div><div class="sub">{sub}</div></div>'


def card(key: str):
    return st.container(key=f"card_{key}")


def redcard(key: str):
    return st.container(key=f"redcard_{key}")


# =============================================================================
# 2. PURE-PYTHON MEDICAL PDF GENERATOR
# =============================================================================
def generate_medical_pdf(patient_name: str, title: str, doc_id: str, date_str: str,
                         doctor_or_facility: str, doc_type: str, summary: str, facts: list[dict]) -> bytes:
    """Generates standard PDF 1.4 document bytes without external dependencies."""
    lines = [
        "JEEVANSETU AI - CONFIDENTIAL MEDICAL VAULT RECORD",
        f"Doc ID: {doc_id}   Date: {date_str}   Type: {doc_type}",
        "====================================================================",
        f"Patient Name: {patient_name}       UHID: JS-2026-8812",
        f"Attending Provider / Center: {doctor_or_facility}",
        "--------------------------------------------------------------------",
        f"DOCUMENT TITLE: {title}",
        f"CLINICAL SUMMARY: {summary}",
        "--------------------------------------------------------------------",
        "STRUCTURED MEDICAL FINDINGS & PRESCRIPTION EXTRACTS:"
    ]
    for f in facts:
        label = f.get("label", "Finding")
        val = f.get("value", "")
        txt = f.get("text", "")
        lines.append(f"  * {label}: {val} -- {txt}")
    lines.append("--------------------------------------------------------------------")
    lines.append("Verified by JeevanSetu Cryptographic Hash Chain | Roboforge 2026")
    lines.append("Team Optimove: Minutes don't cost lives.")

    content = "BT\n/F1 12 Tf\n45 785 Td\n(" + lines[0] + ") Tj\n/F2 9 Tf\n"
    y = 755
    for l in lines[1:]:
        clean_l = str(l).replace("(", "[").replace(")", "]").replace("\\", "/")
        content += f"45 {y} Td ({clean_l}) Tj\n0 -16 Td\n"
        y -= 16
        if y < 60:
            break
    content += "ET\n"

    stream_bytes = content.encode("latin1", errors="replace")
    slen = len(stream_bytes)

    objs = [
        b"%PDF-1.4\n",
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >> endobj\n",
        f"4 0 obj << /Length {slen} >>\nstream\n".encode("latin1") + stream_bytes + b"\nendstream\nendobj\n",
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> endobj\n",
        b"6 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
    ]

    xref_pos = sum(len(o) for o in objs)
    cur = len(objs[0])
    xref = "xref\n0 7\n0000000000 65535 f \n"
    for i in range(1, 6):
        xref += f"{cur:010d} 00000 n \n"
        cur += len(objs[i])
    xref += f"{cur:010d} 00000 n \n"

    trailer = f"trailer << /Size 7 /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n"
    return b"".join(objs) + xref.encode("latin1") + trailer.encode("latin1")


# =============================================================================
# 3. AUTHENTICATION & DEMO ROLES MASTER DATA
# =============================================================================
ROLE_LOGIN = "🔐 Role Login Screen"
ROLE_BYSTANDER = "Bystander (Emergency SOS)"
ROLE_PATIENT = "Patient Portal"
ROLE_DOCTOR = "Doctor / Hospital Team"
ROLE_FAMILY = "Family Manager"
ROLE_ADMIN = "Hospital Admin"
ROLE_ADMISSION = "🏥 Pre-Admission & Payment"

ROLES_LIST = [ROLE_LOGIN, ROLE_BYSTANDER, ROLE_PATIENT, ROLE_DOCTOR, ROLE_FAMILY, ROLE_ADMIN, ROLE_ADMISSION]

DEMO_USERS = {
    "bystander": {
        "role": ROLE_BYSTANDER,
        "name": "Anonymous Bystander",
        "email": "bystander@emergency.sos",
        "badge": "No Login Required",
        "desc": "One-click emergency trigger. Captures incident type, GPS, AI triage, and weighted hospital match.",
        "avatar": "🚨",
    },
    "patient@jeevansetu.ai": {
        "role": ROLE_PATIENT,
        "name": "Aarav Sharma",
        "email": "patient@jeevansetu.ai",
        "badge": "Citizen Patient",
        "desc": "Access Personal Medical Memory, downloadable report PDFs, symptom consultation, and Ask My Records RAG.",
        "avatar": "AS",
    },
    "doctor.sharma@apollo.ai": {
        "role": ROLE_DOCTOR,
        "name": "Dr. Sharma",
        "email": "doctor.sharma@apollo.ai",
        "badge": "Senior Consultant & Trauma Lead",
        "desc": "Write clinical notes and prescriptions, upload official diagnostic PDFs, and monitor incoming trauma alerts.",
        "avatar": "DS",
    },
    "family.sharma@gmail.com": {
        "role": ROLE_FAMILY,
        "name": "Meera Sharma",
        "email": "family.sharma@gmail.com",
        "badge": "Family Guardian",
        "desc": "Live ambulance ETA tracking for Aarav, granular consent toggles, and security audit logs.",
        "avatar": "MS",
    },
    "admin@citycare.hospital": {
        "role": ROLE_ADMIN,
        "name": "CityCare Network Admin",
        "email": "admin@citycare.hospital",
        "badge": "Hospital Operations Director",
        "desc": "Live city-wide bed management (ICU/ER), workload scoring, ER diversion toggles, and break-glass reviews.",
        "avatar": "CC",
    },
}

LOCATIONS = {
    "Dwarka Mor, New Delhi": (28.6192, 77.0332),
    "Connaught Place, New Delhi": (28.6315, 77.2167),
    "Janakpuri, New Delhi": (28.6219, 77.0878),
    "Dwarka Sector 10, New Delhi": (28.5823, 77.0500),
    "Uttam Nagar, New Delhi": (28.6212, 77.0550),
    "Vikaspuri, New Delhi": (28.6425, 77.0707),
    "Custom GPS coordinates": None,
}

HOSPITALS = [
    dict(id="aiims", name="AIIMS Trauma Centre (JPNATC)", area="Ansari Nagar / Raj Nagar", lat=28.5672, lon=77.2090, kind="Government",
         facilities=["Trauma Center", "ICU", "Cath Lab", "Burn Unit", "Neurosurgery", "Blood Bank", "Obstetrics", "NICU"],
         icu_total=60, icu_free=7, er_total=80, er_free=15, workload=0.84, diversion=False, rating=4.8,
         depts=["Cardiology", "Orthopedics", "Neurology", "Obstetrics & Gynecology", "General Medicine", "Gastroenterology", "Pulmonology"]),
    dict(id="manipal", name="Manipal Hospital Dwarka", area="Sector 6, Dwarka", lat=28.5942, lon=77.0467, kind="Private",
         facilities=["Trauma Center", "ICU", "Cath Lab", "Neurosurgery", "Blood Bank", "Obstetrics", "NICU"],
         icu_total=40, icu_free=10, er_total=30, er_free=12, workload=0.50, diversion=False, rating=4.7,
         depts=["Cardiology", "Orthopedics", "Neurology", "Obstetrics & Gynecology", "General Medicine", "Gastroenterology", "Endocrinology", "Dermatology"]),
    dict(id="venkat", name="Venkateshwar Hospital", area="Sector 18A, Dwarka", lat=28.5861, lon=77.0645, kind="Private",
         facilities=["Trauma Center", "ICU", "Cath Lab", "Blood Bank", "Obstetrics"],
         icu_total=30, icu_free=6, er_total=25, er_free=8, workload=0.65, diversion=False, rating=4.5,
         depts=["Cardiology", "Orthopedics", "General Medicine", "Obstetrics & Gynecology", "Pulmonology", "ENT", "Gastroenterology"]),
    dict(id="ddu", name="Deen Dayal Upadhyay Hospital", area="Hari Nagar", lat=28.6283, lon=77.1121, kind="Government",
         facilities=["Trauma Center", "ICU", "Blood Bank", "Obstetrics"],
         icu_total=25, icu_free=4, er_total=60, er_free=10, workload=0.89, diversion=False, rating=4.2,
         depts=["Orthopedics", "General Medicine", "Obstetrics & Gynecology", "Dermatology", "ENT", "Pulmonology"]),
    dict(id="janak", name="Janakpuri Super Speciality Hospital", area="Janakpuri", lat=28.6177, lon=77.0809, kind="Government",
         facilities=["ICU", "Cath Lab", "Blood Bank"],
         icu_total=20, icu_free=6, er_total=15, er_free=5, workload=0.45, diversion=False, rating=4.4,
         depts=["Cardiology", "General Medicine", "Endocrinology", "Neurology", "Dermatology"]),
    dict(id="aakash", name="Aakash Healthcare", area="Sector 3, Dwarka", lat=28.5896, lon=77.0521, kind="Private",
         facilities=["Trauma Center", "ICU", "Burn Unit", "Blood Bank", "Obstetrics", "NICU"],
         icu_total=28, icu_free=5, er_total=22, er_free=7, workload=0.58, diversion=False, rating=4.6,
         depts=["Orthopedics", "General Medicine", "Obstetrics & Gynecology", "ENT", "Dermatology", "Pulmonology", "Gastroenterology"]),
]

SCENARIOS = {
    "Road Accident": dict(
        incident="Road Accident", loc="Dwarka Mor, New Delhi", age="Adult (18-59)", conscious="Unresponsive",
        breathing="Normal", bleeding="Severe",
        notes="Two-wheeler hit by speeding vehicle near Dwarka Mor pillar 780. Rider on asphalt, unresponsive, heavy bleeding from head and left leg."),
    "Cardiac Arrest": dict(
        incident="Cardiac Arrest", loc="Janakpuri, New Delhi", age="Adult (18-59)", conscious="Unresponsive",
        breathing="Not breathing / gasping", bleeding="None",
        notes="34-year-old male collapsed in market complaining of severe crushing chest pain and profuse sweating. Bystander giving chest compressions."),
    "Severe Burns": dict(
        incident="Severe Burns", loc="Dwarka Sector 10, New Delhi", age="Adult (18-59)", conscious="Alert",
        breathing="Laboured", bleeding="None",
        notes="Kitchen LPG cylinder flare-up. Partial-thickness burns over upper torso and both arms; soot around nostrils and coughing."),
    "Fall / Trauma": dict(
        incident="Trauma", loc="Uttam Nagar, New Delhi", age="Adult (18-59)", conscious="Drowsy / confused",
        breathing="Normal", bleeding="Moderate",
        notes="Construction worker fell 15 feet from scaffolding. Head laceration, deformity in right arm, vomiting and confused."),
    "Pregnancy Emergency": dict(
        incident="Pregnancy", loc="Connaught Place, New Delhi", age="Adult (18-59)", conscious="Alert",
        breathing="Normal", bleeding="Severe",
        notes="32-week pregnant female with sudden severe lower abdominal cramping, active vaginal hemorrhage, and dizziness."),
}

INCIDENT_PROFILES = {
    "Road Accident": dict(base=3, category="Polytrauma (Road Traffic Collision)", fac=["Trauma Center", "ICU", "Blood Bank"]),
    "Cardiac Arrest": dict(base=6, category="Cardiac Arrest / Acute Coronary Syndrome", fac=["Cath Lab", "ICU"]),
    "Trauma": dict(base=3, category="Major Blunt / Penetrating Trauma", fac=["Trauma Center", "ICU"]),
    "Severe Burns": dict(base=4, category="Major Thermal Injury / Inhalation Risk", fac=["Burn Unit", "ICU"]),
    "Pregnancy": dict(base=4, category="Obstetric Emergency / Preterm Hemorrhage", fac=["Obstetrics", "NICU", "Blood Bank"]),
}

PATIENT = dict(
    id="JS-2026-8812", name="Aarav Sharma", age=34, sex="M", blood="O+",
    allergy="Penicillin (urticaria, facial angioedema)",
    condition="Mild hypertension (Stage 1)", height="176 cm", weight="78 kg", phone="+91 98•••• 7712",
    contacts=[("Meera Sharma", "Mother", "+91 98•••• 4521"), ("Rohan Sharma", "Brother", "+91 97•••• 1180")],
    meds=["Amlodipine 5 mg once daily"],
)

PARTIES = {
    "Doctors": ("Treating physicians and specialists consulting or admitting the patient.",
                ["Full medical records", "Prescriptions & labs only", "Appointment summary only"]),
    "Ambulance Responders": ("Dispatched paramedics and emergency medical technicians en route.",
                             ["Emergency summary only", "Blood group & allergies only", "Full medical records"]),
    "Hospitals": ("Receiving emergency triage team and inpatient critical care departments.",
                  ["Emergency summary only", "Full medical records", "Blood group & allergies only"]),
}


def build_seed_docs() -> list[dict]:
    return [
        dict(
            id="DOC-2026-0214", date=date(2026, 2, 14), type="Lab Report",
            title="Comprehensive Metabolic Panel + HbA1c",
            provider="Metro Diagnostics, Janakpuri",
            summary="HbA1c borderline (5.9%), LDL slightly elevated (128 mg/dL), Vitamin D insufficient (24 ng/mL).",
            facts=[
                dict(kind="hba1c", label="HbA1c", value="5.9 %", text="HbA1c 5.9 % (prediabetes range 5.7-6.4 %)"),
                dict(kind="glucose", label="Fasting glucose", value="104 mg/dL", text="Fasting glucose 104 mg/dL (ref 70-99)"),
                dict(kind="lipid", label="LDL cholesterol", value="128 mg/dL", text="LDL cholesterol 128 mg/dL (borderline high, ref <100)"),
                dict(kind="vitamin", label="Vitamin D", value="24 ng/mL", text="Vitamin D 24 ng/mL (insufficient, ref 30-100)"),
                dict(kind="lab", label="Creatinine", value="0.9 mg/dL", text="Serum creatinine 0.9 mg/dL (normal)"),
            ]
        ),
        dict(
            id="DOC-2026-0120", date=date(2026, 1, 20), type="Prescription",
            title="Cardiology Follow-Up: Hypertension Review",
            provider="Dr. Neha Kapoor, Manipal Hospital Dwarka",
            summary="BP controlled at 138/88 mmHg. Continue Amlodipine 5mg OD. Advised 30 min daily brisk walk and low sodium diet.",
            facts=[
                dict(kind="bp", label="Blood pressure", value="138/88 mmHg", text="Blood pressure 138/88 mmHg at clinic visit"),
                dict(kind="condition", label="Diagnosis", value="Mild hypertension", text="Diagnosis: mild (stage-1) essential hypertension"),
                dict(kind="medication", label="Amlodipine", value="5 mg once daily", text="Amlodipine 5 mg once daily after breakfast (ongoing)", active=True),
                dict(kind="medication", label="Vitamin D3", value="60,000 IU weekly", text="Vitamin D3 60,000 IU once weekly for 8 weeks (course completed)"),
            ]
        ),
        dict(
            id="DOC-2025-1103", date=date(2025, 11, 3), type="Discharge Summary",
            title="Acute Gastroenteritis Inpatient Admission",
            provider="Venkateshwar Hospital, Dwarka",
            summary="Admitted 1-3 Nov 2025 for dehydration secondary to acute gastroenteritis. IV rehydration, discharged stable.",
            facts=[
                dict(kind="admission", label="Admission", value="1-3 Nov 2025", text="Admitted 1-3 Nov 2025: acute gastroenteritis with moderate dehydration, treated with IV fluids and ondansetron"),
                dict(kind="bp", label="Blood pressure", value="142/90 mmHg", text="Blood pressure 142/90 mmHg on admission"),
                dict(kind="allergy", label="Allergy re-verified", value="Penicillin", text="Penicillin allergy re-verified; beta-lactam antibiotics strictly avoided"),
                dict(kind="medication", label="Ondansetron", value="4 mg as needed", text="Ondansetron 4 mg as needed for 3 days (course completed)"),
            ]
        ),
        dict(
            id="DOC-2025-0812", date=date(2025, 8, 12), type="Prescription",
            title="Orthopedics Clinic: Lumbar Strain",
            provider="Dr. Rakesh Mehta, Aakash Healthcare",
            summary="Mechanical lower back pain from heavy lifting. Short NSAID course, core strengthening exercises.",
            facts=[
                dict(kind="bp", label="Blood pressure", value="134/86 mmHg", text="Blood pressure 134/86 mmHg at clinic visit"),
                dict(kind="condition", label="Diagnosis", value="Lumbar strain", text="Diagnosis: mechanical lower back pain (lumbar strain)"),
                dict(kind="medication", label="Aceclofenac", value="100 mg twice daily x5 days", text="Aceclofenac 100 mg twice daily for 5 days (course completed)"),
                dict(kind="medication", label="Pantoprazole", value="40 mg once daily x5 days", text="Pantoprazole 40 mg once daily before breakfast (course completed)"),
            ]
        ),
        dict(
            id="DOC-2019-0709", date=date(2019, 7, 9), type="Allergy Record",
            title="Severe Drug Reaction: Amoxicillin",
            provider="Janakpuri Super Speciality Hospital (ED)",
            summary="Acute urticaria, facial angioedema after amoxicillin ingestion. Blood typed O positive.",
            facts=[
                dict(kind="allergy", label="Drug allergy", value="Penicillin", text="Penicillin (amoxicillin): acute urticaria and facial angioedema, life-threatening reaction risk"),
                dict(kind="blood_group", label="Blood group", value="O positive", text="Blood group O positive (laboratory verified)"),
            ]
        ),
    ]


# =============================================================================
# 4. ENGINES: AI TRIAGE, HAVERSINE MATCHER, RAG & AUDIT TRAIL
# =============================================================================
def now_ist() -> datetime:
    return datetime.now(IST)


def fmt_ts(ts: datetime) -> str:
    return ts.strftime("%d %b %Y, %H:%M:%S")


def _hash(prev: str, e: dict) -> str:
    raw = "|".join([prev, e["ts"], e["role"], e["action"], e["data"], str(e["break_glass"])])
    return hashlib.sha256(raw.encode()).hexdigest()


def log_audit(role: str, action: str, data: str, break_glass: bool = False, ts: datetime | None = None) -> None:
    chain = st.session_state.audit
    prev = chain[-1]["hash"] if chain else "GENESIS"
    e = dict(ts=fmt_ts(ts or now_ist()), role=role, action=action, data=data, break_glass=break_glass)
    e["hash"] = _hash(prev, e)
    chain.append(e)


def verify_chain() -> bool:
    prev = "GENESIS"
    for e in st.session_state.audit:
        if _hash(prev, e) != e["hash"]:
            return False
        prev = e["hash"]
    return True


def seed_audit() -> None:
    n = now_ist()
    seed = [
        (timedelta(days=45, hours=3), "Patient (Aarav Sharma)", "UPLOAD", "Lab report DOC-2025-0518", False),
        (timedelta(days=32, hours=1), "Doctor (Dr. Neha Kapoor)", "VIEW", "Prescription history, lab reports", False),
        (timedelta(days=20, hours=4), "Ambulance Responder (AMB-DL-1180)", "BREAK_GLASS", "Blood group, allergies (patient unresponsive at scene)", True),
        (timedelta(days=20, hours=3, minutes=58), "System (Auto-notify)", "ALERT_SENT", "Family contacts notified of break-glass access", False),
        (timedelta(days=12, hours=6), "Doctor (Dr. Rakesh Mehta)", "VIEW", "Orthopedic history and spine radiographs", False),
        (timedelta(days=3, hours=2), "Family Manager (Meera Sharma)", "CONSENT_UPDATE", "Ambulance Responders: access set to Emergency Summary", False),
    ]
    for delta, role, action, data, bg in seed:
        log_audit(role, action, data, bg, ts=n - delta)


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dlmb = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


WEIGHTS = {"Facilities": 0.35, "Distance": 0.25, "Beds": 0.20, "Workload": 0.20}


def rank_hospitals(lat: float, lon: float, required: list[str], hospitals: list[dict]) -> pd.DataFrame:
    rows = []
    for h in hospitals:
        d = haversine_km(lat, lon, h["lat"], h["lon"])
        road = d * 1.35
        eta = max(3.0, road / 32.0 * 60.0)
        have = [f for f in required if f in h["facilities"]]
        missing = [f for f in required if f not in h["facilities"]]
        s_fac = len(have) / max(1, len(required))
        s_dist = max(0.0, 1 - road / 30.0)
        s_bed = min(1.0, 0.6 * min(1, h["icu_free"] / 8) + 0.4 * min(1, h["er_free"] / 10))
        s_work = 1 - h["workload"]
        comps = {"Facilities": s_fac, "Distance": s_dist, "Beds": s_bed, "Workload": s_work}
        raw = sum(WEIGHTS[k] * v for k, v in comps.items()) * (0.85 ** len(missing))
        score = 0.0 if h["diversion"] else raw * 100
        rows.append({
            "id": h["id"], "Hospital": h["name"], "Area": h["area"], "Type": h["kind"],
            "Distance (km)": round(d, 1), "ETA (min)": round(eta, 1),
            "Facilities": f"{len(have)}/{len(required)}", "Missing": ", ".join(missing) or "-",
            "ICU free": h["icu_free"], "ER free": h["er_free"], "Workload (%)": int(h["workload"] * 100),
            "Status": "DIVERTED" if h["diversion"] else "Accepting", "Score": round(score, 1),
            **{f"c_{k}": round(WEIGHTS[k] * v * 100 * (0.85 ** len(missing)), 1) for k, v in comps.items()},
        })
    return pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)


KEYWORD_RULES = [
    (r"unconscious|unresponsive|not responding|collaps|faint", 3, "Altered Consciousness", None),
    (r"not breathing|no pulse|gasping|stopped breathing|cardiac arrest", 4, "Cardiorespiratory Failure", None),
    (r"bleed|blood|haemorrhage|hemorrhage", 2, "Active Hemorrhage", "Blood Bank"),
    (r"chest pain|crushing|left arm|jaw pain|sweat|clammy", 2, "Acute Cardiac Symptoms", "Cath Lab"),
    (r"\bhead\b|skull|brain|vomit|seizure", 2, "Suspected Head Trauma", "Neurosurgery"),
    (r"fracture|broken|deform|bone", 1, "Orthopedic Fracture", None),
    (r"fire|burn|scald|smoke|blister|inhal", 2, "Severe Burn / Smoke Inhalation", "Burn Unit"),
    (r"pregnan|labor|labour|water broke|contraction|fetal|baby", 3, "Obstetric Emergency", "Obstetrics"),
]
CONSCIOUS_PTS = {"Alert": 0, "Drowsy / confused": 1, "Unresponsive": 3}
BREATH_PTS = {"Normal": 0, "Laboured": 2, "Not breathing / gasping": 4}
BLEED_PTS = {"None": 0, "Moderate": 1, "Severe": 3}


def run_triage(incident: str, conscious: str, breathing: str, bleeding: str, notes: str) -> dict:
    prof = INCIDENT_PROFILES.get(incident, INCIDENT_PROFILES["Trauma"])
    text = (notes or "").lower()
    score = prof["base"] + CONSCIOUS_PTS.get(conscious, 0) + BREATH_PTS.get(breathing, 0) + BLEED_PTS.get(bleeding, 0)
    flags, facilities = [], list(prof["fac"])
    for pattern, pts, flag, fac in KEYWORD_RULES:
        if re.search(pattern, text):
            score += pts
            flags.append(flag)
            if fac and fac not in facilities:
                facilities.append(fac)
    if conscious == "Unresponsive":
        flags.append("Unresponsive State")
    if breathing == "Not breathing / gasping":
        flags.append("Airway / Breathing Compromised")
    if bleeding == "Severe":
        flags.append("Massive Exsanguinating Bleed")
    flags = list(dict.fromkeys(flags))
    severity = "Critical" if score >= 9 else ("High" if score >= 6 else "Moderate")
    confidence = min(0.98, 0.65 + 0.04 * len(flags) + 0.02 * min(score, 10))

    steps = ["Ensure scene safety for yourself and the patient. Do not move unless active fire/hazard."]
    if incident == "Cardiac Arrest" or breathing == "Not breathing / gasping":
        steps += [
            "Check responsiveness. If no pulse/breathing, initiate high-quality chest compressions immediately (100-120/min).",
            "Call 112 / 108 and shout for an automated external defibrillator (AED).",
            "Do not administer fluids or oral medications."
        ]
    elif incident == "Severe Burns":
        steps += [
            "Extinguish flame, remove non-adherent smoldering clothing, avoid breaking blisters.",
            "Cool affected skin with clean cool tap water for 15-20 minutes. Avoid ice or home remedies.",
            "Keep patient elevated if smoke inhalation suspected."
        ]
    elif incident == "Pregnancy":
        steps += [
            "Position the patient in the left lateral tilt position to relieve inferior vena cava compression.",
            "Keep the patient calm and warm; monitor fetal movement and bleeding rate.",
            "Do not pack the vaginal vault; apply sterile pad externally."
        ]
    else:
        steps += [
            "Immobilize cervical spine if head/neck trauma suspected. Do not remove safety helmet unless airway blocked.",
            "Apply direct firm pressure on bleeding sites using clean compress.",
            "Keep patient warm with a blanket to prevent trauma triad of hypothermia."
        ]
    return dict(score=score, severity=severity, category=prof["category"], facilities=facilities,
                flags=flags, confidence=confidence, first_aid=steps)


RED_FLAGS = ["chest pain", "unconscious", "not breathing", "can't breathe", "cannot breathe", "severe bleeding",
             "seizure", "stroke", "slurred speech", "face drooping", "paralysis", "vomiting blood", "suicidal"]
WATCH_FLAGS = ["chest tightness", "shortness of breath", "breathless", "severe headache", "high fever", "blood in urine"]
DEPT_KEYWORDS = {
    "Cardiology": ["chest", "palpitation", "heart", "bp", "blood pressure", "tightness", "angina"],
    "Orthopedics": ["back pain", "joint", "knee", "shoulder", "fracture", "sprain", "bone", "spine"],
    "Neurology": ["headache", "migraine", "dizziness", "numbness", "tingling", "seizure", "vertigo"],
    "Obstetrics & Gynecology": ["pregnancy", "period", "cramp", "vaginal", "bleeding", "pregnant", "trimester", "pelvic"],
    "Gastroenterology": ["stomach", "acidity", "abdominal", "vomit", "diarrhea", "constipation", "bloating", "nausea"],
    "Pulmonology": ["cough", "wheezing", "asthma", "breath", "phlegm", "lung"],
    "Dermatology": ["rash", "itch", "skin", "acne", "hair", "allergy", "urticaria"],
    "ENT": ["ear", "throat", "sinus", "nose", "tonsil", "hearing"],
    "General Medicine": ["fever", "cold", "body ache", "weakness", "malaise", "infection", "checkup"],
}


def match_department(text: str) -> dict:
    t = text.lower()
    scores = {}
    for dept, kws in DEPT_KEYWORDS.items():
        hits = [k for k in kws if k in t]
        if hits:
            scores[dept] = (len(hits), hits)
    red = [k for k in RED_FLAGS if k in t]
    watch = [k for k in WATCH_FLAGS if k in t]
    if not scores:
        scores["General Medicine"] = (0, [])
    ordered = sorted(scores.items(), key=lambda kv: -kv[1][0])
    top, (n, hits) = ordered[0]
    total = sum(v[0] for v in scores.values()) or 1
    conf = min(0.96, 0.58 + 0.35 * n / total) if n else 0.50
    urgency = "Emergency SOS Needed" if red else ("Soon (24-48 h)" if watch else "Routine Consultation")
    return dict(dept=top, hits=hits, conf=conf, alt=[d for d, _ in ordered[1:3]], red=red, watch=watch, urgency=urgency)


def doctor_for(h: dict, dept: str) -> dict:
    seed = zlib.crc32(f"{h['id']}-{dept}".encode())
    first = ["Neha", "Rajesh", "Vikram", "Priya", "Sunita", "Arjun", "Kavita", "Sanjay", "Ananya", "Meenal"]
    last = ["Kapoor", "Sharma", "Bhatia", "Menon", "Verma", "Iyer", "Malhotra", "Gupta", "Rao", "Chopra"]
    name = f"Dr. {first[seed % 10]} {last[(seed // 10) % 10]}"
    times = ["09:30 AM", "10:15 AM", "11:30 AM", "02:00 PM", "03:45 PM", "05:00 PM", "06:30 PM"]
    n = now_ist()
    booked = {(a["doctor"], a["slot"]) for a in st.session_state.get("appointments", [])}
    slots = []
    for day in range(0, 3):
        d = (n + timedelta(days=day)).date()
        for i, t in enumerate(times):
            if (seed >> i) & 1 == 0 and day < 2:
                continue
            label = f"{'Today' if day == 0 else 'Tomorrow' if day == 1 else d.strftime('%a %d %b')} | {t}"
            if (name, label) not in booked:
                slots.append(label)
    return dict(name=name, exp=10 + seed % 15, slots=slots[:7])


STOP = set("a an the of to is are was were my me i do does did what which show give tell have has had and or in on for with about last latest any please can you your list all".split())
SYNONYMS = {
    "allergies": ["allergy", "penicillin", "reaction", "urticaria", "angioedema"],
    "allergy": ["penicillin", "urticaria", "reaction"],
    "bp": ["blood", "pressure", "hypertension", "amlodipine"],
    "pressure": ["bp", "hypertension"],
    "sugar": ["hba1c", "glucose", "diabetes"],
    "hba1c": ["sugar", "glucose"],
    "medicines": ["medication", "amlodipine", "prescriptions", "tablets", "drugs"],
    "medication": ["medicines", "amlodipine", "tablets"],
    "blood": ["group", "positive", "o+"],
    "group": ["blood", "positive"],
}


def build_chunks(docs: list[dict]) -> list[dict]:
    chunks = []
    for d in docs:
        for f in d.get("facts", []):
            chunks.append(dict(doc=d, fact=f, text=f"{f['label']} {f['text']} {d['type']} {d['title']} {d.get('provider', '')}"))
    return chunks


def rag_retrieve(query: str, docs: list[dict], k: int = 5) -> list[dict]:
    chunks = build_chunks(docs)
    if not chunks:
        return []
    words = [w.lower() for w in re.findall(r"[a-z0-9]+", query) if w.lower() not in STOP]
    expanded = list(words)
    for w in words:
        expanded += SYNONYMS.get(w, [])
    scores = []
    for c in chunks:
        t = c["text"].lower()
        score = sum(1.5 for w in words if w in t) + sum(0.8 for w in expanded if w in t)
        scores.append(score)
    ranked = sorted(zip(chunks, scores), key=lambda x: -x[1])
    return [c for c, s in ranked[:k] if s > 0]


def compose_answer(query: str, hits: list[dict], docs: list[dict] | None = None) -> tuple[str, list[dict]]:
    if not hits:
        return ("I could not find matching information in your medical records vault. Please upload relevant lab reports or consultation documents.", [])
    top = hits[0]
    kind = top["fact"].get("kind", "")
    doc = top["doc"]

    if kind == "allergy":
        ans = (f"Your records confirm a severe drug allergy to <b>Penicillin</b> (Reaction: urticaria and facial angioedema). "
               f"Re-verified on {doc['date'].strftime('%d %b %Y')}. All beta-lactams are strictly contraindicated.")
    elif kind == "bp":
        ans = f"Your latest recorded blood pressure is <b>{top['fact']['value']}</b> on {doc['date'].strftime('%d %b %Y')} at {doc['provider']}."
    elif kind == "hba1c":
        ans = f"Your latest HbA1c is <b>{top['fact']['value']}</b> ({top['doc']['title']}, {doc['date'].strftime('%d %b %Y')}), which sits in the prediabetes monitoring range (5.7 - 6.4%)."
    elif kind == "medication":
        ans = "Active medications on record: <b>Amlodipine 5 mg once daily</b> for mild hypertension. Past completed courses include Vitamin D3 and Aceclofenac."
    elif kind == "blood_group":
        ans = f"Your laboratory-typed blood group is <b>{top['fact']['value']}</b>."
    else:
        ans = f"According to record <b>{doc['id']}</b> ({doc['title']}): {top['fact']['text']}."
    return ans, [top]


DEMO_SECONDS = 75


def incident_progress(inc: dict) -> dict:
    el = time.time() - inc["t0"]
    frac = min(1.0, el / DEMO_SECONDS)
    total = inc["scene_sec"] + inc["transport_sec"]
    sim = frac * total
    if inc.get("cancelled"):
        phase = "Cancelled"
    elif sim < inc["scene_sec"]:
        phase = "En Route to Incident Site"
    elif frac < 1:
        phase = "Transporting Patient to Hospital"
    else:
        phase = "Arrived at Emergency Trauma Bay"
    return dict(el=el, frac=frac, total=total, sim=sim, phase=phase, done=frac >= 1,
                scene_left=max(0, inc["scene_sec"] - sim), hosp_left=max(0, total - sim))


def mmss(sec: float) -> str:
    s = int(round(sec))
    return f"{s // 60:02d}:{s % 60:02d}"


# =============================================================================
# 5. STATE MANAGEMENT & SYNCHRONIZED NAVIGATION
# =============================================================================
def init_state() -> None:
    ss = st.session_state
    if "role" not in ss:
        ss.role = ROLE_LOGIN
    if "nav_role_selection" not in ss:
        ss.nav_role_selection = ROLE_LOGIN
    if "logged_in" not in ss:
        ss.logged_in = False
    if "current_user" not in ss:
        ss.current_user = None

    if "initialized" in ss:
        return
    ss.initialized = True
    ss.hospitals = copy.deepcopy(HOSPITALS)
    ss.consent = {
        "Doctors": dict(granted=True, scope="Full medical records"),
        "Ambulance Responders": dict(granted=False, scope="Emergency summary only"),
        "Hospitals": dict(granted=True, scope="Emergency summary only"),
    }
    ss.docs = build_seed_docs()
    ss.audit = []
    seed_audit()
    ss.incident = None
    ss.break_glass = False
    ss.appointments = []
    ss.last_booking = None
    ss.ocr = None
    ss.rag_last = None
    ss.admin_hospital = "manipal"
    ss.family_prefs = dict(sms=True, whatsapp=True, push=True)
    ss.symptom_text = ""
    ensure_sos_defaults()


def ensure_sos_defaults() -> None:
    ss = st.session_state
    defaults = {
        "sos_incident": "Road Accident",
        "sos_loc": "Dwarka Mor, New Delhi",
        "sos_age": "Adult (18-59)",
        "sos_conscious": "Unresponsive",
        "sos_breathing": "Normal",
        "sos_bleeding": "Severe",
        "sos_notes": "Two-wheeler hit near metro pillar. Heavy bleeding, unresponsive.",
        "sos_registered": True,
        "sos_lat": 28.6192,
        "sos_lon": 77.0332
    }
    for k, v in defaults.items():
        if k not in ss:
            ss[k] = v


def select_role(role_name: str, user_key: str | None = None) -> None:
    ss = st.session_state
    ss.role = role_name
    ss.nav_role_selection = role_name
    if role_name == ROLE_LOGIN:
        ss.logged_in = False
        ss.current_user = None
    elif role_name == ROLE_BYSTANDER:
        ss.logged_in = False
        ss.current_user = DEMO_USERS["bystander"]
    else:
        key = user_key
        if not key:
            for k, u in DEMO_USERS.items():
                if u["role"] == role_name:
                    key = k
                    break
        if key and key in DEMO_USERS:
            u = DEMO_USERS[key]
            ss.current_user = u
            ss.logged_in = True
            log_audit(f"User ({u['name']})", "LOGIN", f"Logged in as {u['role']} ({u['email']})", False)


def logout() -> None:
    ss = st.session_state
    if ss.current_user:
        log_audit(f"User ({ss.current_user['name']})", "LOGOUT", "Session ended", False)
    select_role(ROLE_LOGIN)


def reset_demo() -> None:
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init_state()


def create_incident(p: dict) -> None:
    ss = st.session_state
    lat, lon = (p["lat"], p["lon"])
    triage = run_triage(p["incident"], p["conscious"], p["breathing"], p["bleeding"], p["notes"])
    ranking = rank_hospitals(lat, lon, triage["facilities"], ss.hospitals)
    best = ranking.iloc[0]
    seed = zlib.crc32(f"{time.time()}".encode())
    scene_min = 4 + seed % 3
    inc = dict(
        id=f"SOS-{seed % 900000 + 100000}", t0=time.time(), started=fmt_ts(now_ist()), started_dt=now_ist(),
        params=p, triage=triage, ranking=ranking, best=best.to_dict(),
        ambulance=f"AMB-DL-{seed % 9000 + 1000}", crew="Paramedic Imran Khan + 1 EMT", scene_sec=scene_min * 60,
        transport_sec=float(best["ETA (min)"]) * 60, hospital_ack=False, arrival_logged=False, cancelled=False,
        registered=p.get("registered", True),
    )
    ss.incident = inc
    ss.break_glass = False
    log_audit("Bystander (Emergency SOS)", "SOS_TRIGGERED", f"{inc['id']} | {p['incident']} @ {p['loc_name']} | No login required", False)
    log_audit("AI Preliminary Triage", "TRIAGE_COMPLETED", f"{inc['id']} | Severity: {triage['severity']} | Required: {', '.join(triage['facilities'])}", False)
    log_audit("Weighted Matcher Engine", "HOSPITAL_SELECTED", f"{inc['id']} -> {best['Hospital']} (Score: {best['Score']})", False)
    log_audit("Ambulance Dispatch Control", "UNIT_DISPATCHED", f"{inc['ambulance']} deployed to incident coordinates", False)
    log_audit(f"Hospital Alert ({best['Hospital']})", "PRE_ALERT_RECEIVED", f"Inbound Trauma Alert: ETA {best['ETA (min)']} min", False)
    if p.get("registered", True):
        log_audit("Automated Family Notification", "SMS_WHATSAPP_SENT", "Dispatched to Meera Sharma & Rohan Sharma", False)


def trigger_bystander_sos() -> None:
    ss = st.session_state
    loc_key = ss.get("sos_loc", "Dwarka Mor, New Delhi")
    if LOCATIONS.get(loc_key) is None:
        lat = ss.get("sos_lat", 28.6192)
        lon = ss.get("sos_lon", 77.0332)
    else:
        lat, lon = LOCATIONS[loc_key]
    create_incident(dict(
        incident=ss.get("sos_incident", "Road Accident"),
        loc_name=loc_key if LOCATIONS.get(loc_key) else f"{lat:.4f}, {lon:.4f}",
        lat=lat, lon=lon,
        age=ss.get("sos_age", "Adult (18-59)"),
        conscious=ss.get("sos_conscious", "Unresponsive"),
        breathing=ss.get("sos_breathing", "Normal"),
        bleeding=ss.get("sos_bleeding", "Severe"),
        notes=ss.get("sos_notes", "Emergency incident reported by citizen bystander."),
        registered=ss.get("sos_registered", True)
    ))


def cancel_active_sos() -> None:
    ss = st.session_state
    if ss.incident:
        log_audit("Emergency Control", "SOS_RESOLVED", f"{ss.incident['id']} closed by operator", False)
    ss.incident = None
    ss.break_glass = False


# =============================================================================
# 6. HEADER BAR & SIDEBAR NAVIGATION
# =============================================================================
def render_header_auth() -> None:
    ss = st.session_state
    user = ss.current_user
    c_brand, c_user = st.columns([3.2, 1.8])
    with c_brand:
        md("""
        <div style="display:flex;align-items:center;gap:0.85rem">
          <span style="font-size:2.2rem">🩺</span>
          <div>
            <div style="display:flex;align-items:center;gap:0.5rem">
              <span style="font-family:'Lora',serif;font-size:1.65rem;font-weight:700;color:#1F3D2B">JeevanSetu AI</span>
              <span style="font-size:0.72rem;background:#EDE9FE;color:#5B21B6;border:1px solid #8B5CF6;border-radius:999px;padding:0.12rem 0.55rem;font-weight:700">Hackathon 2026</span>
            </div>
            <div style="font-size:0.83rem;color:#5C6B61;margin-top:-0.15rem;font-style:italic">"A place where minutes don't cost lives" &bull; Built by <b>Team Optimove</b></div>
          </div>
        </div>
        """)
    with c_user:
        if ss.logged_in and user:
            md(f"""
            <div style="text-align:right">
              <span class="badge b-ok">{esc(user['badge'])}</span>
              <b>{esc(user['name'])}</b> <span style="font-size:0.8rem;color:#5C6B61">({esc(user['email'])})</span>
            </div>
            """)
            col_sp, col_b = st.columns([1.5, 1.5])
            with col_b:
                if st.button("Log Out / Switch", key="nav_logout_btn"):
                    logout()
                    st.rerun()
        elif ss.role == ROLE_BYSTANDER:
            md("""
            <div style="text-align:right">
              <span class="badge b-red-soft">Bystander Mode (No Login)</span>
              <span style="font-size:0.8rem;color:#5C6B61">Direct Emergency Trigger</span>
            </div>
            """)
            col_sp, col_b = st.columns([1.2, 1.8])
            with col_b:
                if st.button("Role Login Screen", key="nav_login_portal_btn"):
                    logout()
                    st.rerun()
        elif ss.role == ROLE_ADMISSION:
            md("""
            <div style="text-align:right">
              <span class="badge b-ok">Pre-Admission Portal</span>
              <span style="font-size:0.8rem;color:#5C6B61">Form &amp; Deposit</span>
            </div>
            """)
            col_sp, col_b = st.columns([1.2, 1.8])
            with col_b:
                if st.button("Role Login Screen", key="nav_login_portal_btn_adm"):
                    logout()
                    st.rerun()
        else:
            md("""
            <div style="text-align:right">
              <span class="badge b-ai">Authentication Portal</span>
              <span style="font-size:0.8rem;color:#5C6B61">Select Demo Role Below</span>
            </div>
            """)
    st.markdown("<hr style='margin:0.5rem 0 1rem;border-color:rgba(31,61,43,0.15)'>", unsafe_allow_html=True)


def on_sidebar_role_change() -> None:
    chosen = st.session_state.nav_role_selection
    select_role(chosen)


def render_sidebar() -> None:
    ss = st.session_state
    with st.sidebar:
        md('<div class="side-brand">JeevanSetu AI</div><div class="side-sub">Emergency & Medical Memory</div>')
        st.markdown("&nbsp;")

        if ss.logged_in and ss.current_user:
            u = ss.current_user
            md(f"""
            <div class="side-card">
              <div style="font-size:0.72rem;letter-spacing:0.1em;text-transform:uppercase;color:#D3C29E">Logged In As</div>
              <div style="font-size:1.05rem;font-weight:700;color:#F5EFE6">{esc(u['name'])}</div>
              <div style="font-size:0.78rem;color:#D3C29E">{esc(u['email'])}</div>
              <span class="badge b-ai" style="margin-top:0.35rem">{esc(u['role'])}</span>
            </div>
            """)
        elif ss.role == ROLE_BYSTANDER:
            md("""
            <div class="side-card">
              <div style="font-size:0.72rem;letter-spacing:0.1em;text-transform:uppercase;color:#D3C29E">Current Mode</div>
              <div style="font-size:1.05rem;font-weight:700;color:#FEE2E2">🚨 Bystander (No Login)</div>
              <div style="font-size:0.78rem;color:#D3C29E">Instant zero-barrier emergency trigger</div>
            </div>
            """)
        else:
            md("""
            <div class="side-card">
              <div style="font-size:0.72rem;letter-spacing:0.1em;text-transform:uppercase;color:#D3C29E">Portal Navigation</div>
              <div style="font-size:1.05rem;font-weight:700;color:#F5EFE6">Role Login Screen</div>
              <div style="font-size:0.78rem;color:#D3C29E">Select any demo role to evaluate</div>
            </div>
            """)

        st.markdown('<div class="side-sub" style="margin-bottom:0.4rem">Select Role Dashboard</div>', unsafe_allow_html=True)
        cur_idx = ROLES_LIST.index(ss.role) if ss.role in ROLES_LIST else 0
        st.radio("Select Role Dashboard", ROLES_LIST, index=cur_idx, key="nav_role_selection",
                 on_change=on_sidebar_role_change, label_visibility="collapsed")

        st.markdown('<hr style="margin:0.5rem 0;border-color:rgba(232,220,196,0.25)">', unsafe_allow_html=True)
        if st.button(
            "📋 Pre-Admission & Payment Form",
            type="primary",
            use_container_width=True,
            help="Open Emergency Pre-Admission Form & Online Deposit Payment Portal",
            key="btn_sidebar_open_adm_portal",
        ):
            select_role(ROLE_ADMISSION)
            st.rerun()

        # Live Status Chips
        chips = []
        if ss.incident:
            chips.append('<span class="side-chip on-red">🚨 SOS ACTIVE</span>')
        else:
            chips.append('<span class="side-chip">No active SOS</span>')
        if ss.break_glass:
            chips.append('<span class="side-chip on-red">BREAK-GLASS ON</span>')
        chain_ok = verify_chain()
        chips.append(f'<span class="side-chip {"on-green" if chain_ok else "on-red"}">Audit {"Verified" if chain_ok else "TAMPERED"}</span>')
        md('<div style="margin:0.4rem 0">' + "".join(chips) + "</div>")

        st.markdown("&nbsp;")
        if st.button("🔄 Reset Demo State", on_click=reset_demo, key="side_reset_btn"):
            st.toast("Restored initial demo data", icon="🔄")

        md("""
        <div class="side-card" style="margin-top:0.8rem">
          <b>Roboforge Hackathon 2026</b><br>
          <span style="font-size:0.8rem">Software & Intelligent Systems</span><br>
          <b>Team Optimove:</b><br>
          <span style="font-size:0.78rem">Aayush Varshney, Sonali, Aksha Malik, Diksha Kalia</span>
        </div>
        """)


# =============================================================================
# 7. ROLE LOGIN SCREEN & DEMO PORTAL (MATCHING PPT SLIDE 1-5)
# =============================================================================
def render_login_portal() -> None:
    md("""
    <div class="hero">
      <div>
        <div class="eyebrow">Roboforge Hackathon 2026 | Team Optimove</div>
        <div class="title">JeevanSetu AI Demo Portal</div>
        <span class="tag">A place where minutes don't cost lives</span>
      </div>
      <div class="right">
        <b>Test Each Role Independently:</b><br>
        Select any demo account below to evaluate tailored user journeys or trigger an instant login-free Emergency SOS.
      </div>
    </div>
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    tab_quick, tab_arch, tab_manual = st.tabs([
        "🚀 Quick-Fill Demo Roles (Judges Evaluation)",
        "📋 Four Pillars & Coordinated Architecture",
        "🔐 Manual Credential Sign-In"
    ])

    with tab_quick:
        st.markdown('<p class="lead">Click any card button below to immediately open that role\'s live environment:</p>', unsafe_allow_html=True)

        # 1. Bystander Card
        with card("role_card_bystander"):
            c_icon, c_info, c_action = st.columns([0.8, 3.8, 1.8])
            with c_icon:
                st.markdown("<div style='font-size:2.8rem;text-align:center;padding-top:0.2rem'>🚨</div>", unsafe_allow_html=True)
            with c_info:
                st.markdown("""
                <div style="font-family:'Lora',serif;font-size:1.25rem;font-weight:700;color:#991B1B">Role A: Bystander (Emergency SOS - NO LOGIN REQUIRED)</div>
                <div style="font-size:0.84rem;color:#5C6B61"><b>Access:</b> Public Zero-Barrier &bull; <code>bystander@emergency.sos</code></div>
                <div style="font-size:0.88rem;color:#1B2B21;margin-top:0.25rem">Instant one-click SOS trigger, GPS location lock, AI preliminary triage, weighted Haversine hospital matcher, and live ambulance dispatch tracker.</div>
                """, unsafe_allow_html=True)
            with c_action:
                st.markdown("&nbsp;")
                if st.button("🚨 Open Emergency SOS", type="primary", key="btn_login_bystander"):
                    select_role(ROLE_BYSTANDER, "bystander")
                    st.rerun()

        # 2. Patient Portal Card
        with card("role_card_patient"):
            c_icon, c_info, c_action = st.columns([0.8, 3.8, 1.8])
            with c_icon:
                st.markdown("<div style='font-size:2.8rem;text-align:center;padding-top:0.2rem'>🩺</div>", unsafe_allow_html=True)
            with c_info:
                st.markdown("""
                <div style="font-family:'Lora',serif;font-size:1.25rem;font-weight:700;color:#1F3D2B">Role B: Patient Portal & Personal Medical Memory</div>
                <div style="font-size:0.84rem;color:#5C6B61"><b>Account:</b> Aarav Sharma (34/M) &bull; <code>patient@jeevansetu.ai</code></div>
                <div style="font-size:0.88rem;color:#1B2B21;margin-top:0.25rem">Personal Medical Memory Vault, interactive timeline, downloadable PDF reports hub, RAG Record Search ('Ask My Records'), symptom department matcher & specialist booking.</div>
                """, unsafe_allow_html=True)
            with c_action:
                st.markdown("&nbsp;")
                if st.button("Sign In as Patient", key="btn_login_patient"):
                    select_role(ROLE_PATIENT, "patient@jeevansetu.ai")
                    st.rerun()

        # 3. Doctor Dashboard Card
        with card("role_card_doctor"):
            c_icon, c_info, c_action = st.columns([0.8, 3.8, 1.8])
            with c_icon:
                st.markdown("<div style='font-size:2.8rem;text-align:center;padding-top:0.2rem'>👨‍⚕️</div>", unsafe_allow_html=True)
            with c_info:
                st.markdown("""
                <div style="font-family:'Lora',serif;font-size:1.25rem;font-weight:700;color:#1F3D2B">Role C: Doctor & Hospital Medical Team Dashboard</div>
                <div style="font-size:0.84rem;color:#5C6B61"><b>Account:</b> Dr. Sharma &bull; <code>doctor.sharma@apollo.ai</code></div>
                <div style="font-size:0.88rem;color:#1B2B21;margin-top:0.25rem">Patient Management & Memory Write Portal (clinical notes, diagnoses, prescriptions, PDF uploads to patient vault) and Incoming Emergency Pre-Alert Command Center with break-glass.</div>
                """, unsafe_allow_html=True)
            with c_action:
                st.markdown("&nbsp;")
                if st.button("Sign In as Doctor", key="btn_login_doctor"):
                    select_role(ROLE_DOCTOR, "doctor.sharma@apollo.ai")
                    st.rerun()

        # 4. Family Manager Card
        with card("role_card_family"):
            c_icon, c_info, c_action = st.columns([0.8, 3.8, 1.8])
            with c_icon:
                st.markdown("<div style='font-size:2.8rem;text-align:center;padding-top:0.2rem'>🛡️</div>", unsafe_allow_html=True)
            with c_info:
                st.markdown("""
                <div style="font-family:'Lora',serif;font-size:1.25rem;font-weight:700;color:#1F3D2B">Role D: Family Manager & Privacy Control</div>
                <div style="font-size:0.84rem;color:#5C6B61"><b>Account:</b> Meera Sharma (Mother) &bull; <code>family.sharma@gmail.com</code></div>
                <div style="font-size:0.88rem;color:#1B2B21;margin-top:0.25rem">Live patient emergency status and ambulance ETA tracking, granular consent matrix toggles, automated SMS/WhatsApp alert settings, and cryptographic audit log.</div>
                """, unsafe_allow_html=True)
            with c_action:
                st.markdown("&nbsp;")
                if st.button("Sign In as Family", key="btn_login_family"):
                    select_role(ROLE_FAMILY, "family.sharma@gmail.com")
                    st.rerun()

        # 5. Hospital Admin Card
        with card("role_card_admin"):
            c_icon, c_info, c_action = st.columns([0.8, 3.8, 1.8])
            with c_icon:
                st.markdown("<div style='font-size:2.8rem;text-align:center;padding-top:0.2rem'>🏥</div>", unsafe_allow_html=True)
            with c_info:
                st.markdown("""
                <div style="font-family:'Lora',serif;font-size:1.25rem;font-weight:700;color:#1F3D2B">Role E: Hospital Admin Command Center</div>
                <div style="font-size:0.84rem;color:#5C6B61"><b>Account:</b> CityCare Operations Director &bull; <code>admin@citycare.hospital</code></div>
                <div style="font-size:0.88rem;color:#1B2B21;margin-top:0.25rem">City-wide bed availability monitoring (ICU/ER), workload capacity scoring, emergency ER diversion toggles, inbound ambulance feed, and break-glass review.</div>
                """, unsafe_allow_html=True)
            with c_action:
                st.markdown("&nbsp;")
                if st.button("Sign In as Admin", key="btn_login_admin"):
                    select_role(ROLE_ADMIN, "admin@citycare.hospital")
                    st.rerun()

        # 6. Emergency Pre-Admission & Online Payment Card
        with card("role_card_admission"):
            c_icon, c_info, c_action = st.columns([0.8, 3.8, 1.8])
            with c_icon:
                st.markdown("<div style='font-size:2.8rem;text-align:center;padding-top:0.2rem'>💳</div>", unsafe_allow_html=True)
            with c_info:
                st.markdown("""
                <div style="font-family:'Lora',serif;font-size:1.25rem;font-weight:700;color:#1F3D2B">Role F: Emergency Pre-Admission &amp; Online Payment</div>
                <div style="font-size:0.84rem;color:#5C6B61"><b>Features:</b> Online Admission Form &bull; Document Upload &bull; Instant UPI/Card Deposit</div>
                <div style="font-size:0.88rem;color:#1B2B21;margin-top:0.25rem">Digital pre-admission formalities for emergency patient families, consent signing, document upload (ID/Insurance), online deposit payment via Razorpay, and instant PDF receipts.</div>
                """, unsafe_allow_html=True)
            with c_action:
                st.markdown("&nbsp;")
                if st.button("📋 Open Admission Portal", type="primary", key="btn_login_admission"):
                    select_role(ROLE_ADMISSION)
                    st.rerun()

    with tab_arch:
        st.markdown("#### Four Pillars of JeevanSetu AI (From Presentation Slide 5)")
        c1, c2 = st.columns(2)
        with c1:
            with card("p1"):
                st.markdown("""
                <b>1. Emergency Intelligence</b>
                - Login-free bystander SOS with GPS lock
                - Preliminary AI NLP categorization & triage
                - Weighted hospital suitability matching (Haversine + Beds + Workload)
                - Real-time ambulance telemetry & ETA tracker
                """, unsafe_allow_html=True)
            with card("p2"):
                st.markdown("""
                <b>2. AI Personal Medical Memory</b>
                - Centralized patient profile (blood group, allergies, conditions)
                - Document upload & simulated OCR extraction
                - Chronological medical history timeline
                - Hybrid RAG search over records with cited source references
                """, unsafe_allow_html=True)
        with c2:
            with card("p3"):
                st.markdown("""
                <b>3. Healthcare Coordination</b>
                - Normal consultation pathway & department identification
                - Hospital availability & doctor appointment booking
                - Automated pre-alerts to receiving hospital trauma bays
                - Coordinated family SMS & WhatsApp updates
                """, unsafe_allow_html=True)
            with card("p4"):
                st.markdown("""
                <b>4. Privacy and Access Control</b>
                - Role-Based Access Control (Patient, Doctor, Hospital, Family, Bystander)
                - Patient-controlled granular consent matrix
                - Tamper-evident SHA-256 hash-chained immutable audit log
                - Logged emergency break-glass access for authorized responders
                """, unsafe_allow_html=True)

    with tab_manual:
        c1, c2 = st.columns([2, 1.2])
        with c1:
            with card("manual_box"):
                st.subheader("Manual Credential Verification")
                in_email = st.selectbox("Select Account Email", list(DEMO_USERS.keys())[1:], key="manual_in_email")
                in_pwd = st.text_input("Password", type="password", value="password123", key="manual_in_pwd")
                if st.button("Authenticate & Open Dashboard", type="primary", key="btn_manual_submit"):
                    select_role(DEMO_USERS[in_email]["role"], in_email)
                    st.rerun()
        with c2:
            st.info("""
            **Demo Credentials Cheat Sheet:**
            - **Patient:** `patient@jeevansetu.ai` (`password123`)
            - **Doctor:** `doctor.sharma@apollo.ai` (`doctorpass`)
            - **Family:** `family.sharma@gmail.com` (`familypass`)
            - **Admin:** `admin@citycare.hospital` (`adminpass`)
            """)


# =============================================================================
# 8. ROLE A: BYSTANDER / EMERGENCY SOS (LOGIN-FREE)
# =============================================================================
def view_bystander() -> None:
    ss = st.session_state
    ensure_sos_defaults()

    if ss.incident is None:
        md("""
        <div class="alert-red">
          <div class="h">🚨 Bystander Emergency SOS: Zero Barrier & No Login Needed</div>
          Every second counts. Fill what you observe or choose a quick scenario. Responders and AI triage are mobilized immediately while you type.
          In extreme danger, also call <b>112</b> / <b>108</b>.
        </div>
        """)

        section(1, "Accident & Incident Information", "GPS", "r")
        st.markdown('<p class="lead">Tap a pre-configured emergency scenario or customize below:</p>', unsafe_allow_html=True)

        sc_cols = st.columns(len(SCENARIOS))
        for col, (sc_name, sc_data) in zip(sc_cols, SCENARIOS.items()):
            with col:
                if st.button(sc_name, key=f"sc_btn_{sc_name}"):
                    ss.sos_incident = sc_data["incident"]
                    ss.sos_loc = sc_data["loc"]
                    ss.sos_age = sc_data["age"]
                    ss.sos_conscious = sc_data["conscious"]
                    ss.sos_breathing = sc_data["breathing"]
                    ss.sos_bleeding = sc_data["bleeding"]
                    ss.sos_notes = sc_data["notes"]
                    st.toast(f"Loaded scenario: {sc_name}", icon="⚡")
                    st.rerun()

        with card("sos_intake_form"):
            c1, c2 = st.columns(2)
            with c1:
                cur_loc = ss.get("sos_loc", "Dwarka Mor, New Delhi")
                loc_list = list(LOCATIONS.keys())
                loc_idx = loc_list.index(cur_loc) if cur_loc in loc_list else 0
                st.selectbox("Emergency Location (Simulated GPS)", loc_list, index=loc_idx, key="sos_loc")

                if LOCATIONS.get(ss.sos_loc) is None:
                    la, lo = st.columns(2)
                    la.number_input("Latitude", value=28.6192, format="%.4f", key="sos_lat")
                    lo.number_input("Longitude", value=77.0332, format="%.4f", key="sos_lon")
                    lat, lon = ss.sos_lat, ss.sos_lon
                else:
                    lat, lon = LOCATIONS[ss.sos_loc]
                st.caption(f"📍 GPS Coordinates locked: {lat:.4f}° N, {lon:.4f}° E (Accuracy: ~6 meters)")

                inc_list = list(INCIDENT_PROFILES.keys())
                cur_inc = ss.get("sos_incident", "Road Accident")
                inc_idx = inc_list.index(cur_inc) if cur_inc in inc_list else 0
                st.selectbox("Incident Nature", inc_list, index=inc_idx, key="sos_incident")

                age_list = ["Child (<18)", "Adult (18-59)", "Senior (60+)"]
                cur_age = ss.get("sos_age", "Adult (18-59)")
                age_idx = age_list.index(cur_age) if cur_age in age_list else 1
                st.selectbox("Patient Age Group", age_list, index=age_idx, key="sos_age")

            with c2:
                a, b, c = st.columns(3)
                con_list = list(CONSCIOUS_PTS.keys())
                cur_con = ss.get("sos_conscious", "Unresponsive")
                a.selectbox("Consciousness", con_list, index=con_list.index(cur_con) if cur_con in con_list else 2, key="sos_conscious")

                br_list = list(BREATH_PTS.keys())
                cur_br = ss.get("sos_breathing", "Normal")
                b.selectbox("Breathing", br_list, index=br_list.index(cur_br) if cur_br in br_list else 0, key="sos_breathing")

                bl_list = list(BLEED_PTS.keys())
                cur_bl = ss.get("sos_bleeding", "Severe")
                c.selectbox("Bleeding", bl_list, index=bl_list.index(cur_bl) if cur_bl in bl_list else 2, key="sos_bleeding")

                st.text_area("Observations / Incident Notes",
                             value=ss.get("sos_notes", "Two-wheeler hit near metro pillar. Heavy bleeding, unresponsive."),
                             key="sos_notes", height=105)
                st.checkbox("Patient holds JeevanSetu Digital Health ID (Auto-trigger family alert)", value=True, key="sos_registered")

        with st.container(key="sosbtn_trigger"):
            if st.button("🚨 TRIGGER EMERGENCY SOS", type="primary", key="btn_trigger_emergency_sos"):
                trigger_bystander_sos()
                st.rerun()

        st.markdown('<p class="note" style="text-align:center">Zero account creation required. Responders receive real-time telemetry instantly.</p>', unsafe_allow_html=True)
        return

    # SOS IS ACTIVE
    inc = ss.incident
    tri = inc["triage"]
    best = inc["best"]
    p = inc["params"]
    sev_cls = "critical" if tri["severity"] == "Critical" else "high"

    md(f"""
    <div class="alert-red">
      <div class="h">🚨 ACTIVE EMERGENCY CASE: {inc['id']}</div>
      Reported at {inc['started']} IST from <b>{esc(p['loc_name'])}</b>.
      {badge(tri['severity'].upper(), sev_cls)} {badge(p['incident'], 'red-soft')}
      Ambulance <b>{inc['ambulance']}</b> dispatched with <b>{inc['crew']}</b>. Stay with the patient!
    </div>
    """)

    section(2, "AI Preliminary Triage Engine", "AI ASSIST", "v")
    c1, c2 = st.columns([1.2, 1])
    with c1:
        with card("ai_triage_card"):
            chips = "".join(badge(f, "ai") for f in tri["flags"]) or badge("No extra flags", "muted")
            facs = "".join(badge(f, "dark") for f in tri["facilities"])
            md(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem">
              <div>
                <div class="note">Preliminary Clinical Category</div>
                <div style="font-family:'Lora',serif;font-size:1.3rem;font-weight:700;color:#1F3D2B">{esc(tri['category'])}</div>
              </div>
              <div style="text-align:right">
                {badge('SEVERITY: ' + tri['severity'].upper(), sev_cls)}
                <div class="note">Confidence: {int(tri['confidence'] * 100)}% &bull; Triage Risk Score: {tri['score']}</div>
              </div>
            </div>
            <div style="margin-top:0.75rem"><div class="note">Clinical Red Flags Detected</div>{chips}</div>
            <div style="margin-top:0.55rem"><div class="note">Required Emergency Facilities</div>{facs}</div>
            <div class="note" style="margin-top:0.65rem">AI assists only; dispatch runs in parallel without waiting for model inference.</div>
            """)
    with c2:
        with card("first_aid_card"):
            st.markdown("<div style='font-family:Lora,serif;font-size:1.15rem;font-weight:700;color:#1F3D2B'>Immediate First-Aid Protocol</div>", unsafe_allow_html=True)
            for idx, s in enumerate(tri["first_aid"], 1):
                st.markdown(f"**{idx}.** {s}")

    section(3, "Weighted Hospital Suitability Matching", "HAVERSINE + CAPACITY", "v")
    rk = inc["ranking"]
    reasons = [
        f"Facility readiness: {best['Facilities']} matched ({esc(', '.join(tri['facilities']))})",
        f"Haversine road distance: {best['Distance (km)']} km (Estimated arrival: {best['ETA (min)']} mins)",
        f"Live Critical Care capacity: {best['ICU free']} ICU beds & {best['ER free']} ER beds unoccupied",
        f"Staff & ER workload score: {best['Workload (%)']}%",
    ]
    rl = "".join(f"<li>{r}</li>" for r in reasons)
    md(f"""
    <div class="hosp-best">
      <div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap">
        <div>
          <span class="badge b-ai">OPTIMAL EMERGENCY DESTINATION</span>
          <div class="nm">{esc(best['Hospital'])}</div>
          <div>{esc(best['Area'])} &bull; {best['Type']}</div>
        </div>
        <div style="text-align:right">
          <div class="score">{best['Score']}</div>
          <div>Suitability Index / 100</div>
        </div>
      </div>
      <ul>{rl}</ul>
    </div>
    """)

    t_rank, t_score, t_map = st.tabs(["📊 Ranked Hospitals", "📈 Multi-Factor Weights", "🗺️ Geographic Map"])
    with t_rank:
        show_cols = ["Hospital", "Score", "Distance (km)", "ETA (min)", "Facilities", "Missing", "ICU free", "ER free", "Workload (%)", "Status"]
        st.dataframe(rk[show_cols], hide_index=True,
                     column_config={
                         "Score": st.column_config.ProgressColumn("Suitability", min_value=0, max_value=100, format="%.1f"),
                         "Workload (%)": st.column_config.ProgressColumn("Workload", min_value=0, max_value=100, format="%d%%")
                     })
        st.caption("Algorithm: 0.35 × Facilities + 0.25 × Distance + 0.20 × Bed Availability + 0.20 × (1 - Workload); Diverted centers excluded.")
    with t_score:
        chart_data = rk.set_index("Hospital")[[f"c_{k}" for k in WEIGHTS]].rename(columns=lambda c: c[2:])
        st.bar_chart(chart_data, color=[FOREST, VIOLET, LEAF, "#D3C29E"], horizontal=True)
    with t_map:
        pts = [dict(lat=p["lat"], lon=p["lon"], color="#DC2626", size=140)]
        for _, r in rk.iterrows():
            h_obj = next(h for h in ss.hospitals if h["id"] == r["id"])
            pts.append(dict(lat=h_obj["lat"], lon=h_obj["lon"],
                            color="#8B5CF6" if r["id"] == best["id"] else "#1F3D2B",
                            size=120 if r["id"] == best["id"] else 70))
        st.map(pd.DataFrame(pts), latitude="lat", longitude="lon", color="color", size="size")

    section(4, "Ambulance Dispatch & Live ETA Tracker", "REAL-TIME", "r")
    render_tracker_visuals()

    section(5, "Paramedic Authorized Break-Glass", "AUDITED", "r")
    c_bg1, c_bg2 = st.columns([1, 1.3])
    with c_bg1:
        with redcard("paramedic_bg_card"):
            st.markdown("<div style='font-family:Lora,serif;font-size:1.15rem;font-weight:700;color:#991B1B'>Emergency Break-Glass Authorization</div>", unsafe_allow_html=True)
            st.caption("Authorized responders can unlock critical medical history if patient is unresponsive. All events are written to the SHA-256 audit log.")
            st.selectbox("Clinical Justification", [
                "Unresponsive polytrauma patient, unable to give consent",
                "Massive hemorrhage, blood typing and allergy verification required",
                "Suspected anaphylaxis / acute cardiac arrest",
            ], key="bg_reason_bystander")
            bg_active = st.toggle("Activate Emergency Break-Glass", value=ss.break_glass, key="bg_toggle_bystander")
            if bg_active != ss.break_glass:
                ss.break_glass = bg_active
                if bg_active:
                    log_audit(f"Ambulance Responder ({inc['ambulance']})", "BREAK_GLASS_ACTIVATED",
                              f"Unlocked Blood Group & Allergies for {inc['id']}. Reason: {ss.bg_reason_bystander}", True)
                    log_audit("Auto-Notification Service", "ALERT_DISPATCHED", "Patient family notified of Break-Glass override", False)
                else:
                    log_audit(f"Ambulance Responder ({inc['ambulance']})", "BREAK_GLASS_DEACTIVATED", "Emergency session concluded", True)
                st.rerun()
    with c_bg2:
        critical_patient_card("Ambulance Responders")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Close Active Incident & Return", on_click=cancel_active_sos, key="btn_close_sos"):
        st.rerun()


# =============================================================================
# 9. ROLE B: PATIENT PORTAL & PERSONAL MEDICAL MEMORY
# =============================================================================
def view_patient() -> None:
    ss = st.session_state
    P = PATIENT

    with card("patient_profile_header"):
        md(f"""
        <div class="profile">
          <div class="avatar">{P['name'][:2].upper()}</div>
          <div style="flex:1;min-width:250px">
            <div style="font-family:'Lora',serif;font-size:1.55rem;font-weight:700;color:#1F3D2B">{P['name']}</div>
            <div class="note">UHID: <b>{P['id']}</b> &bull; {P['age']} Y / {'Male' if P['sex']=='M' else 'Female'} &bull; {P['height']} &bull; {P['weight']} &bull; {P['phone']}</div>
          </div>
          <div>
            {badge('Blood Group ' + P['blood'], 'dark')}
            {badge('Allergy: ' + P['allergy'], 'red-soft')}
            {badge(P['condition'], 'ai')}
            {badge('Active: Amlodipine 5mg', 'ok')}
          </div>
        </div>
        """)

    t1, t2, t3, t4 = st.tabs([
        "🩺 Consultation Pathway",
        "📂 Medical Memory & Timeline",
        "📑 My Reports Hub (PDFs)",
        "🛡️ Privacy, Consent & Audit"
    ])

    # Tab 1: Normal Consultation Pathway (From PPT Slide 3 & 4)
    with t1:
        section(1, "Describe Symptoms for Department Matching", "AI ASSIST")
        st.markdown('<p class="lead">Select a sample complaint or type your symptoms. AI matches the clinical department and available specialists.</p>', unsafe_allow_html=True)

        sample_pills = [
            "Persistent chest tightness & fatigue for 4 days",
            "Lower back pain and numbness down right thigh",
            "Recurring migraine with nausea and visual aura",
            "Severe epigastric burning and acid reflux after meals",
            "Pregnancy first-trimester nausea, cramping and spotting",
            "Skin rash with itchy red hives on forearms"
        ]
        p_cols = st.columns(3)
        for i, s in enumerate(sample_pills):
            with p_cols[i % 3]:
                if st.button(s, key=f"pill_pat_sym_{i}"):
                    ss.symptom_text = s
                    st.rerun()

        st.text_area("Your Symptoms or Healthcare Need", key="symptom_text", height=95,
                     placeholder="e.g. Frequent dull headache, occasional dizziness and elevated morning BP readings...")

        sym_text = (ss.symptom_text or "").strip()
        if sym_text:
            matched = match_department(sym_text)

            if matched["red"]:
                md(f"""
                <div class="alert-red">
                  <div class="h">⚠️ Critical Red-Flag Detected: {esc(', '.join(matched['red']))}</div>
                  These symptoms may represent an acute emergency. Do not wait for an outpatient appointment!
                </div>
                """)
                if st.button("🚨 SWITCH DIRECTLY TO EMERGENCY SOS", type="primary", key="btn_switch_to_sos_patient"):
                    ss.sos_incident = "Cardiac Arrest" if "chest" in sym_text.lower() else "Trauma"
                    ss.sos_notes = f"Escalated from patient symptom triage: {sym_text}"
                    select_role(ROLE_BYSTANDER, "bystander")
                    st.rerun()
            elif matched["watch"]:
                md(f"""
                <div class="alert-amber">
                  <b>Caution:</b> Symptoms like "{esc(', '.join(matched['watch']))}" warrant prompt clinical attention within 24 hours.
                </div>
                """)

            section(2, "AI-Assisted Department Recommendation", "TRIAGE RESULT", "v")
            c_d1, c_d2, c_d3 = st.columns(3)
            c_d1.markdown(H(mcard("Recommended Dept", matched["dept"], "Matched via clinical NLP", "violet")), unsafe_allow_html=True)
            c_d2.markdown(H(mcard("Match Confidence", f"{int(matched['conf'] * 100)}%", f"Keywords: {', '.join(matched['hits']) or 'None'}", "light")), unsafe_allow_html=True)
            c_d3.markdown(H(mcard("Urgency Assessment", matched["urgency"], f"Alternates: {', '.join(matched['alt']) or 'None'}", "light")), unsafe_allow_html=True)

            section(3, f"Available Specialists in {matched['dept']}", "HOSPITAL AVAILABILITY", "v")
            c_home, c_perm = st.columns([1.5, 2])
            home_loc = c_home.selectbox("Your Residential Locality", [k for k in LOCATIONS if LOCATIONS[k]], key="pat_consult_loc")
            c_perm.markdown("&nbsp;")
            c_perm.checkbox("Grant physician access to my Medical Memory Summary", value=True, key="pat_share_memory_consent")

            lat, lon = LOCATIONS[home_loc]
            candidates = []
            for h in ss.hospitals:
                if matched["dept"] in h["depts"]:
                    d_km = haversine_km(lat, lon, h["lat"], h["lon"])
                    doc = doctor_for(h, matched["dept"])
                    suit = 0.5 * max(0, 1 - d_km / 30) + 0.3 * min(1, len(doc["slots"]) / 7) + 0.2 * (h["rating"] - 4.0)
                    candidates.append((suit, d_km, h, doc))
            candidates.sort(key=lambda x: -x[0])

            for rank, (suit, d_km, h, doc) in enumerate(candidates[:3], 1):
                with card(f"doc_card_{h['id']}"):
                    c_info, c_action = st.columns([2.5, 1.5])
                    with c_info:
                        top_tag = badge("RECOMMENDED MATCH", "ai") if rank == 1 else ""
                        st.markdown(f"""
                        <div style="font-family:'Lora',serif;font-size:1.25rem;font-weight:700;color:#1F3D2B">{esc(h['name'])} {top_tag}</div>
                        <div class="note">{esc(h['area'])} &bull; {h['kind']} &bull; Rating: ⭐ {h['rating']}</div>
                        <div style="margin-top:0.4rem;font-size:1.02rem"><b>{esc(doc['name'])}</b> &bull; {matched['dept']} ({doc['exp']} yrs exp)</div>
                        <div style="margin-top:0.3rem">
                          {badge(f'{d_km:.1f} km away', 'muted')}
                          {badge(f'~{max(5, int(d_km * 1.35 / 25 * 60))} min travel', 'muted')}
                          {badge(f'{len(doc["slots"])} slots open', 'ok')}
                        </div>
                        """, unsafe_allow_html=True)
                    with c_action:
                        if doc["slots"]:
                            slot_sel = st.selectbox("Select Appointment Slot", doc["slots"], key=f"slot_sel_{h['id']}")
                            if st.button("Confirm Appointment", key=f"book_btn_{h['id']}", type="primary"):
                                ref = f"APT-{zlib.crc32((doc['name'] + slot_sel).encode()) % 900000 + 100000}"
                                appt = dict(ref=ref, doctor=doc["name"], hospital=h["name"], dept=matched["dept"],
                                            slot=slot_sel, shared=ss.pat_share_memory_consent)
                                ss.appointments.append(appt)
                                ss.last_booking = appt
                                log_audit("Patient (Aarav Sharma)", "APPOINTMENT_BOOKED", f"{ref} | {doc['name']} | {h['name']} | {slot_sel}", False)
                                st.toast(f"Booked successfully! Ref: {ref}", icon="✅")
                                st.rerun()

        if ss.appointments:
            section(4, "Your Confirmed Appointments", "SCHEDULED")
            for a in ss.appointments:
                with card(f"my_appt_{a['ref']}"):
                    ca1, ca2 = st.columns([4, 1])
                    ca1.markdown(f"""
                    <b>{esc(a['doctor'])}</b> ({esc(a['dept'])}) &bull; <b>{esc(a['hospital'])}</b><br>
                    {badge(a['slot'], 'ok')} {badge('Ref: ' + a['ref'], 'muted')}
                    {badge('Memory Shared' if a['shared'] else 'Summary Private', 'ai')}
                    """, unsafe_allow_html=True)
                    if ca2.button("Cancel", key=f"cancel_appt_{a['ref']}"):
                        ss.appointments = [x for x in ss.appointments if x["ref"] != a["ref"]]
                        log_audit("Patient (Aarav Sharma)", "APPOINTMENT_CANCELLED", a["ref"], False)
                        st.rerun()

    # Tab 2: Medical Memory & Timeline (From PPT Slide 5)
    with t2:
        section(1, "Interactive Medical History Timeline", "TIMELINE")
        types = sorted({d["type"] for d in ss.docs})
        sel_types = st.multiselect("Filter Record Types", types, default=types, key="filter_record_types")
        css_type_map = {"Lab Report": "lab", "Prescription": "rx", "Discharge Summary": "dc", "Doctor Clinical Note": "note"}

        for d in sorted(ss.docs, key=lambda x: x["date"], reverse=True):
            if d["type"] not in sel_types:
                continue
            cls = css_type_map.get(d["type"], "")
            md(f"""
            <div class="tl-card {cls}">
              <div class="d">{d['date'].strftime('%d %b %Y')} &bull; {d['type'].upper()} &bull; {d['id']}</div>
              <div class="tt">{esc(d['title'])}</div>
              <div class="note" style="font-style:normal"><b>Facility:</b> {esc(d.get('provider', 'JeevanSetu Network'))}</div>
              <div style="font-size:0.92rem;margin-top:0.25rem">{esc(d['summary'])}</div>
            </div>
            """)
            with st.expander(f"Inspect {len(d.get('facts', []))} Structured Clinical Entities"):
                st.dataframe(pd.DataFrame([{"Entity": f["label"], "Extracted Value": f["value"], "Context": f["text"]} for f in d.get("facts", [])]), hide_index=True)

        section(2, "RAG Record Search ('Ask My Records')", "HYBRID RAG", "v")
        st.markdown('<p class="lead">Query your personal health memory in natural language. Answers are synthesized and cited with direct sources.</p>', unsafe_allow_html=True)

        rag_sample_qs = ["What allergies do I have?", "Show my latest BP reading", "Show my last HbA1c", "What medicines am I on?", "What is my blood group?"]
        rq_cols = st.columns(len(rag_sample_qs))
        for col, q in zip(rq_cols, rag_sample_qs):
            with col:
                if st.button(q, key=f"rag_pill_{q}"):
                    ss.rag_query_input = q
                    st.rerun()

        cq1, cq2 = st.columns([4.5, 1])
        q_user = cq1.text_input("Ask a question about your medical history", value=ss.get("rag_query_input", ""),
                                key="rag_query_input_box", placeholder="e.g. When was my last penicillin allergy verified?")
        if cq2.button("Ask Records", key="btn_ask_rag", type="primary") or q_user:
            if q_user:
                hits = rag_retrieve(q_user, ss.docs)
                ans, cited = compose_answer(q_user, hits, ss.docs)
                log_audit("Patient (Aarav Sharma)", "RAG_SEARCH", f"Query: {q_user[:60]}", False)
                chips_cite = "".join(f'<span class="cite">[{c["doc"]["id"]} &bull; {c["doc"]["date"].strftime("%d %b %Y")}]</span>' for c in cited)
                md(f"""
                <div class="ans">
                  <div class="note"><b>Query:</b> {esc(q_user)}</div>
                  <div style="font-size:1.05rem;margin:0.5rem 0 0.65rem">{ans}</div>
                  <div class="note" style="margin-bottom:0.2rem">Source Citations:</div>
                  {chips_cite or '<span class="note">No direct chunk citation</span>'}
                </div>
                """)

    # Tab 3: My Reports Hub (PDFs)
    with t3:
        section(1, "My Reports Hub: View & Download PDFs", "REPORTS HUB")
        st.markdown('<p class="lead">View, generate, and securely download certified medical report PDFs uploaded by physicians or diagnostic centers.</p>', unsafe_allow_html=True)

        for d in sorted(ss.docs, key=lambda x: x["date"], reverse=True):
            with card(f"report_card_{d['id']}"):
                c_rep, c_dl = st.columns([3.5, 1.5])
                with c_rep:
                    st.markdown(f"""
                    <div style="font-family:'Lora',serif;font-size:1.2rem;font-weight:700;color:#1F3D2B">📄 {esc(d['title'])}</div>
                    <div class="note">ID: <code>{d['id']}</code> &bull; Date: {d['date'].strftime('%d %b %Y')} &bull; Provider: {esc(d.get('provider', 'Network'))}</div>
                    <div style="font-size:0.9rem;margin-top:0.25rem">{esc(d['summary'])}</div>
                    <div style="margin-top:0.35rem">{badge(d['type'], 'ai')} {badge(f'{len(d.get("facts", []))} Facts Indexed', 'ok')}</div>
                    """, unsafe_allow_html=True)
                with c_dl:
                    st.markdown("&nbsp;")
                    pdf_bytes = generate_medical_pdf(
                        patient_name=P["name"],
                        title=d["title"],
                        doc_id=d["id"],
                        date_str=d["date"].strftime("%d %b %Y"),
                        doctor_or_facility=d.get("provider", "JeevanSetu AI"),
                        doc_type=d["type"],
                        summary=d["summary"],
                        facts=d.get("facts", [])
                    )
                    st.download_button(
                        label=f"⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=f"{d['id']}_{d['type'].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{d['id']}"
                    )

    # Tab 4: Privacy, Consent & Audit
    with t4:
        consent_matrix_component("patient")
        audit_table_component("patient")


# =============================================================================
# 10. ROLE C: DOCTOR & HOSPITAL MEDICAL TEAM DASHBOARD
# =============================================================================
def view_doctor() -> None:
    ss = st.session_state
    u = ss.current_user or DEMO_USERS["doctor.sharma@apollo.ai"]

    md(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;background:#1F3D2B;color:#F5EFE6;padding:1rem 1.4rem;border-radius:14px;border-bottom:4px solid #8B5CF6">
      <div>
        <div style="font-family:'Lora',serif;font-size:1.5rem;font-weight:700">{esc(u['name'])}</div>
        <div style="font-size:0.85rem;color:#D3C29E">Apollo Hospital &bull; Senior Consultant / Emergency Response Lead</div>
      </div>
      <div>
        <span class="badge b-ok">LICENSED & AUTHENTICATED</span>
        <span class="badge b-ai">CLINICAL WRITE ACCESS</span>
      </div>
    </div>
    """)

    t_manage, t_emergency = st.tabs([
        "📝 Patient Management & Memory Write Portal",
        "🚨 Incoming Emergency Command Center"
    ])

    with t_manage:
        section(1, "Select Patient & Review Medical Memory", "READ")
        st.selectbox("Select Patient to Manage", [f"{PATIENT['name']} (UHID: {PATIENT['id']})"], key="doc_pat_select")

        with card("doc_pat_snapshot"):
            c_p1, c_p2 = st.columns([3, 2])
            with c_p1:
                st.markdown(f"""
                <div style="font-family:'Lora',serif;font-size:1.3rem;font-weight:700;color:#1F3D2B">{PATIENT['name']} (34/M)</div>
                <div class="note">Blood Group: <b>{PATIENT['blood']}</b> &bull; Chronic: <b>{PATIENT['condition']}</b> &bull; Phone: {PATIENT['phone']}</div>
                <div style="margin-top:0.4rem">
                  <span class="badge b-red-soft">⚠️ ALLERGY ALERT: {esc(PATIENT['allergy'])}</span>
                  <span class="badge b-ok">Medication: Amlodipine 5mg OD</span>
                </div>
                """, unsafe_allow_html=True)
            with c_p2:
                st.caption(f"Medical Records Vault holds **{len(ss.docs)}** verified records.")
                with st.expander("Review Existing Patient Timeline"):
                    for d in sorted(ss.docs, key=lambda x: x["date"], reverse=True)[:3]:
                        st.markdown(f"**{d['date'].strftime('%d %b %Y')}** - {d['title']} ({d['type']})")

        section(2, "Clinical Notes, Diagnosis & Prescription Builder", "WRITE TO MEMORY", "v")
        with card("doc_write_portal"):
            c_w1, c_w2 = st.columns(2)
            with c_w1:
                c_complaint = st.text_input("Chief Complaints / Symptoms", value="Follow-up review for blood pressure and routine evaluation", key="doc_in_complaint")
                c_vitals = st.text_input("Examination Vitals", value="BP 132/84 mmHg, HR 74 bpm, SpO2 98%, Temp 98.4°F", key="doc_in_vitals")
                c_diag = st.text_input("Clinical Diagnosis", value="Essential Hypertension - Well Controlled on Monotherapy", key="doc_in_diag")
            with c_w2:
                c_rx = st.text_area("Prescription / Medications (Name, Dose, Frequency, Duration)",
                                   value="1. Tab Amlodipine 5mg - 1 Tab OD after breakfast (30 days)\n2. Tab Vitamin D3 60,000 IU - 1 Tab weekly (4 weeks)",
                                   key="doc_in_rx", height=110)
                c_advice = st.text_input("Physician Advice & Follow-Up", value="Maintain low sodium diet, 30 min brisk walk, review in 4 weeks", key="doc_in_advice")

            st.markdown("##### 📄 Attach Official Report PDF / Lab Investigation")
            st.file_uploader("Upload Clinical Report PDF / Diagnostics (Mock Uploader)", type=["pdf", "png", "jpg"], key="doc_file_uploader")

            if st.button("💾 Commit to Patient Medical Memory Vault & Generate Signed PDF", type="primary", key="btn_commit_clinical_note"):
                new_id = f"DOC-{now_ist().strftime('%Y-%m%d')}-DR"
                new_facts = [
                    dict(kind="bp", label="Examination BP", value=c_vitals.split(",")[0], text=f"Recorded: {c_vitals}"),
                    dict(kind="condition", label="Diagnosis", value=c_diag, text=f"Doctor Diagnosis: {c_diag}"),
                    dict(kind="medication", label="Prescription", value="Amlodipine + Vitamin D3", text=c_rx, active=True)
                ]
                new_doc = dict(
                    id=new_id,
                    date=now_ist().date(),
                    type="Doctor Clinical Note",
                    title=f"Clinical Consultation: {c_diag}",
                    provider=f"{u['name']}, Apollo Hospital",
                    summary=f"Chief Complaints: {c_complaint}. Vitals: {c_vitals}. Advice: {c_advice}.",
                    facts=new_facts
                )
                ss.docs.append(new_doc)
                log_audit(f"Doctor ({u['name']})", "PATIENT_MEMORY_WRITE", f"Created record {new_id} for {PATIENT['name']} (Diagnosis: {c_diag})", False)
                st.toast(f"Committed to {PATIENT['name']}'s Medical Memory! Record: {new_id}", icon="✅")
                st.rerun()

    with t_emergency:
        section(1, "Real-Time Emergency Pre-Alert Feed", "TRAUMA COMMAND", "r")
        inc = ss.incident

        if not inc:
            md("""
            <div class="alert-violet">
              <b>No Active Emergency SOS Dispatches.</b><br>
              Switch to the Bystander role to trigger an accident SOS or trigger a simulated emergency alert below.
            </div>
            """)
            if st.button("Simulate Incoming Trauma Alert (Dwarka Mor Accident)", type="primary", key="btn_sim_trauma_doc"):
                sc = SCENARIOS["Road Accident"]
                lat, lon = LOCATIONS[sc["loc"]]
                create_incident(dict(
                    incident=sc["incident"], loc_name=sc["loc"], lat=lat, lon=lon,
                    age=sc["age"], conscious=sc["conscious"], breathing=sc["breathing"],
                    bleeding=sc["bleeding"], notes=sc["notes"], registered=True
                ))
                st.rerun()
        else:
            tri = inc["triage"]
            best = inc["best"]
            md(f"""
            <div class="alert-red">
              <div class="h">🚨 INCOMING TRAUMA ALERT: Case {inc['id']} &bull; Severity: {tri['severity'].upper()}</div>
              <b>Incident Nature:</b> {inc['params']['incident']} &bull; <b>Site:</b> {inc['params']['loc_name']}<br>
              <b>Dispatched Unit:</b> {inc['ambulance']} ({inc['crew']}) &bull; <b>ETA to Bay:</b> ~{best['ETA (min)']} mins
            </div>
            """)

            c_trk, c_break = st.columns([1.5, 1])
            with c_trk:
                render_tracker_visuals()
                if not inc.get("hospital_ack", False):
                    if st.button("Acknowledge Alert & Ready Resuscitation Bay", type="primary", key="doc_ack_btn"):
                        inc["hospital_ack"] = True
                        log_audit(f"Doctor ({u['name']})", "EMERGENCY_ACKNOWLEDGED", f"Readying Trauma Team for {inc['id']}", False)
                        st.toast("Emergency Team Alerted!", icon="🏥")
                        st.rerun()
                else:
                    md('<div class="alert-green">✅ Resuscitation bay and surgical specialists on immediate standby.</div>')

            with c_break:
                st.markdown("##### Authorized Emergency Break-Glass")
                critical_patient_card("Doctors")


# =============================================================================
# 11. ROLE D: FAMILY MANAGER & PRIVACY CONTROL
# =============================================================================
def view_family() -> None:
    ss = st.session_state
    u = ss.current_user or DEMO_USERS["family.sharma@gmail.com"]

    md(f"""
    <div class="alert-violet">
      <b>Family Guardian Dashboard:</b> {esc(u['name'])} (Mother) managing privacy controls, access consents, and live emergency safety for <b>{PATIENT['name']}</b>.
    </div>
    """)

    t_track, t_consent, t_audit = st.tabs([
        "🚑 Live Emergency Tracking",
        "🔒 Granular Consent Matrix",
        "🛡️ Tamper-Evident Audit Trail"
    ])

    with t_track:
        inc = ss.incident
        if inc and inc.get("registered", True):
            md(f"""
            <div class="alert-red">
              <div class="h">🚨 Emergency Alert Dispatched for {PATIENT['name']}</div>
              Incident reported near <b>{esc(inc['params']['loc_name'])}</b> &bull; Severity: <b>{inc['triage']['severity'].upper()}</b>.<br>
              Receiving Hospital: <b>{esc(inc['best']['Hospital'])}</b> &bull; Ambulance: <b>{inc['ambulance']}</b>
            </div>
            """)
            render_tracker_visuals()
            st.markdown("&nbsp;")
            if st.button("📝 Fill Hospital Pre-Admission Form & Pay Deposit", type="primary", key="btn_fam_open_adm_active"):
                select_role(ROLE_ADMISSION)
                st.rerun()
        else:
            md(f"""
            <div class="alert-green">
              <b>All Clear:</b> No active emergency detected for {PATIENT['name']}.<br>
              Family contacts are pre-configured to receive automated SMS, WhatsApp, and push alerts instantly upon SOS trigger.
            </div>
            """)
            col_fam1, col_fam2 = st.columns(2)
            with col_fam1:
                if st.button("Simulate Emergency SOS Alert for Aarav", key="btn_sim_sos_fam", use_container_width=True):
                    sc = SCENARIOS["Cardiac Arrest"]
                    lat, lon = LOCATIONS[sc["loc"]]
                    create_incident(dict(
                        incident=sc["incident"], loc_name=sc["loc"], lat=lat, lon=lon,
                        age=sc["age"], conscious=sc["conscious"], breathing=sc["breathing"],
                        bleeding=sc["bleeding"], notes=sc["notes"], registered=True
                    ))
                    st.rerun()
            with col_fam2:
                if st.button("📋 Open Pre-Admission & Payment Portal", key="btn_fam_open_adm_idle", use_container_width=True):
                    select_role(ROLE_ADMISSION)
                    st.rerun()

        st.markdown("##### Notification Preferences")
        cn1, cn2, cn3 = st.columns(3)
        ss.family_prefs["sms"] = cn1.toggle("SMS Emergency Broadcast", value=ss.family_prefs.get("sms", True), key="fam_sms_toggle")
        ss.family_prefs["whatsapp"] = cn2.toggle("WhatsApp Live Link", value=ss.family_prefs.get("whatsapp", True), key="fam_wa_toggle")
        ss.family_prefs["push"] = cn3.toggle("Push Notifications", value=ss.family_prefs.get("push", True), key="fam_push_toggle")

        st.markdown("##### Registered Emergency Contacts")
        for name, rel, phone in PATIENT["contacts"]:
            st.markdown(f"{badge(name, 'dark')} {badge(rel, 'ai')} {badge(phone, 'muted')}")

    with t_consent:
        consent_matrix_component("family")

    with t_audit:
        audit_table_component("family")


# =============================================================================
# 12. ROLE E: HOSPITAL ADMIN COMMAND CENTER
# =============================================================================
def view_admin() -> None:
    ss = st.session_state
    u = ss.current_user or DEMO_USERS["admin@citycare.hospital"]

    section("", "CityCare Hospital Operations Command", None)

    h_map = {h["id"]: h["name"] for h in ss.hospitals}
    h_ids = list(h_map.keys())
    cur_hid = ss.get("admin_hospital", "manipal")
    idx = h_ids.index(cur_hid) if cur_hid in h_ids else 0
    sel_hid = st.selectbox("Select Operating Facility", h_ids, index=idx, format_func=lambda x: h_map[x], key="admin_hosp_select")
    ss.admin_hospital = sel_hid

    h = next(item for item in ss.hospitals if item["id"] == sel_hid)
    inc = ss.incident
    inbound_count = 1 if inc and inc["best"]["id"] == h["id"] and not incident_progress(inc)["done"] else 0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.markdown(H(mcard("ICU Beds Free", f"{h['icu_free']} <span style='font-size:0.95rem'>/ {h['icu_total']}</span>", "Critical Care", "")), unsafe_allow_html=True)
    m2.markdown(H(mcard("ER Beds Free", f"{h['er_free']} <span style='font-size:0.95rem'>/ {h['er_total']}</span>", "Trauma Bay", "light")), unsafe_allow_html=True)
    m3.markdown(H(mcard("Staff Workload", f"{int(h['workload'] * 100)}%", "Capacity Strain", "light")), unsafe_allow_html=True)
    m4.markdown(H(mcard("Inbound Trauma", inbound_count, "Via AI Dispatch", "red" if inbound_count else "light")), unsafe_allow_html=True)
    m5.markdown(H(mcard("Intake Status", "Diverted" if h["diversion"] else "Accepting", "Network Status", "red" if h["diversion"] else "violet")), unsafe_allow_html=True)

    t_cap, t_net, t_logs = st.tabs([
        "🏥 Live Capacity Controls & Diversion",
        "🌐 City-Wide Hospital Network Status",
        "🛡️ Break-Glass & Audit Trail"
    ])

    with t_cap:
        section(1, f"Adjust Capacity for {h['name']}", "LIVE CONTROL")
        c_b1, c_b2, c_b3 = st.columns([1, 1, 1.4])
        new_icu = c_b1.number_input("Available ICU Beds", min_value=0, max_value=h["icu_total"], value=h["icu_free"], key=f"icu_in_{h['id']}")
        new_er = c_b2.number_input("Available ER Beds", min_value=0, max_value=h["er_total"], value=h["er_free"], key=f"er_in_{h['id']}")
        c_b3.markdown("&nbsp;")
        div_toggle = c_b3.toggle("Activate ER Diversion (Redirect Incoming Ambulances)", value=h["diversion"], key=f"div_toggle_{h['id']}")

        if new_icu != h["icu_free"] or new_er != h["er_free"]:
            h["icu_free"] = new_icu
            h["er_free"] = new_er
            log_audit(f"Hospital Admin ({h['name']})", "CAPACITY_UPDATE", f"ICU: {new_icu}, ER: {new_er}", False)
            st.toast("Bed capacity updated!", icon="🛏️")

        if div_toggle != h["diversion"]:
            h["diversion"] = div_toggle
            log_audit(f"Hospital Admin ({h['name']})", "DIVERSION_STATUS_CHANGE", f"Diversion set to {div_toggle}", False)
            st.toast(f"Diversion status: {'DIVERTED' if div_toggle else 'ACCEPTING'}", icon="⚠️")

    with t_net:
        section(2, "Simulated City Network Status (Delhi NCR)", "NETWORK OVERVIEW")
        net_df = pd.DataFrame([
            {
                "Hospital": x["name"], "Area": x["area"], "Type": x["kind"],
                "ICU Free": x["icu_free"], "ER Free": x["er_free"],
                "Workload": x["workload"], "Status": "DIVERTED" if x["diversion"] else "Accepting",
                "Facilities": ", ".join(x["facilities"])
            }
            for x in ss.hospitals
        ])
        st.dataframe(net_df, hide_index=True,
                     column_config={
                         "Workload": st.column_config.ProgressColumn("Workload (%)", min_value=0, max_value=1, format="percent")
                     })

    with t_logs:
        audit_table_component("admin")


# =============================================================================
# 13. REUSABLE COMPONENTS: TRACKER, CRITICAL CARD, CONSENT & AUDIT
# =============================================================================
def render_tracker_visuals() -> None:
    inc = st.session_state.incident
    if not inc:
        return
    pr = incident_progress(inc)
    total = pr["total"]
    scene_pct = inc["scene_sec"] / total * 100
    pos = pr["frac"] * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(H(mcard("Ambulance Unit", inc["ambulance"], inc["crew"], "light")), unsafe_allow_html=True)
    c2.markdown(H(mcard("ETA to Hospital", mmss(pr["hosp_left"]), "Simulated Clock", "violet" if not pr["done"] else "")), unsafe_allow_html=True)
    c3.markdown(H(mcard("Time to Scene", mmss(pr["scene_left"]) if pr["scene_left"] else "On Scene", "Paramedics Assisting" if not pr["scene_left"] else "Countdown", "light")), unsafe_allow_html=True)
    c4.markdown(H(mcard("Phase", f"<span style='font-size:1.15rem'>{pr['phase']}</span>", f"Destination: {esc(inc['best']['Hospital'])}", "")), unsafe_allow_html=True)

    st.progress(pr["frac"], text=f"Mission Progress: {int(pr['frac'] * 100)}% &bull; {pr['phase']}")
    md(f"""
    <div class="track">
      <div class="line"></div>
      <div class="fill" style="width:{pos:.1f}%"></div>
      <div class="node" style="left:0%"></div><div class="nl" style="left:0%">Depot</div>
      <div class="node scene" style="left:{scene_pct:.1f}%"></div><div class="nl" style="left:{scene_pct:.1f}%">Scene ({esc(inc['params']['loc_name'].split(',')[0])})</div>
      <div class="node hosp" style="left:100%"></div><div class="nl" style="left:100%">{esc(inc['best']['Hospital'].split('(')[0].strip())}</div>
      <div class="amb" style="left:{pos:.1f}%">🚑</div>
    </div>
    """)


def critical_patient_card(requester: str) -> None:
    ss = st.session_state
    consent = ss.consent.get(requester, {}).get("granted", False)
    if ss.break_glass or consent:
        via = "EMERGENCY BREAK-GLASS (Logged & Audited)" if ss.break_glass else f"Patient Consent ({ss.consent[requester]['scope']})"
        is_bg = ss.break_glass
        md(f"""
        <div class="{'alert-red' if is_bg else 'alert-green'}">
          <div class="h" style="{'' if is_bg else 'color:#1F3D2B'}">Critical Patient Medical Memory Unlocked</div>
          <div class="note" style="color:inherit">Authorization Basis: <b>{esc(via)}</b></div>
          <div class="kv" style="margin-top:0.5rem">
            <div class="k">Patient Name</div><div><b>{PATIENT['name']}</b> ({PATIENT['age']}/{PATIENT['sex']})</div>
            <div class="k">Blood Group</div><div><b>{PATIENT['blood']}</b></div>
            <div class="k">Critical Allergies</div><div><b>{esc(PATIENT['allergy'])}</b></div>
            <div class="k">Chronic Conditions</div><div>{PATIENT['condition']}</div>
            <div class="k">Active Medication</div><div>{esc(', '.join(PATIENT['meds']))}</div>
            <div class="k">Emergency Contact</div><div>{PATIENT['contacts'][0][0]} ({PATIENT['contacts'][0][1]}): {PATIENT['contacts'][0][2]}</div>
          </div>
        </div>
        """)
    else:
        md(f"""
        <div class="lock">
          🔒 Patient Medical Data Locked<br>
          <span style="font-weight:400;font-size:0.85rem">
            Access not currently granted under standard consent. Authorized responders may initiate Emergency Break-Glass override during active life danger.
          </span>
        </div>
        """)


def consent_matrix_component(view_key: str) -> None:
    ss = st.session_state
    section("1", "Granular Access Consent Matrix", "RBAC PRIVACY")
    st.markdown('<p class="lead">Patients and authorized family guardians control data visibility per role. Changes commit instantly to the immutable log.</p>', unsafe_allow_html=True)

    for party, (desc, scopes) in PARTIES.items():
        meta = ss.consent[party]
        with card(f"{view_key}_consent_{party.replace(' ', '_')}"):
            c1, c2, c3 = st.columns([3.2, 1.2, 2.6])
            with c1:
                st.markdown(f"<div style='font-family:Lora,serif;font-size:1.15rem;font-weight:700;color:#1F3D2B'>{party}</div><div class='note'>{desc}</div>", unsafe_allow_html=True)
            with c2:
                new_granted = st.toggle("Access Granted", value=meta["granted"], key=f"tgl_{view_key}_{party}")
            with c3:
                new_scope = st.selectbox("Access Scope", scopes, index=scopes.index(meta["scope"]) if meta["scope"] in scopes else 0,
                                         key=f"scope_{view_key}_{party}", label_visibility="collapsed")
            if new_granted != meta["granted"] or new_scope != meta["scope"]:
                ss.consent[party] = dict(granted=new_granted, scope=new_scope)
                log_audit(f"Privacy Control ({ss.role})", "CONSENT_MODIFIED", f"{party}: {'GRANTED' if new_granted else 'REVOKED'} ({new_scope})", False)
                st.toast(f"Updated access for {party}", icon="🔒")


def audit_table_component(view_key: str) -> None:
    ss = st.session_state
    section("2", "Tamper-Evident SHA-256 Audit Trail", "CRYPTOGRAPHIC CHAIN")
    chain_valid = verify_chain()
    status_badge = badge("CHAIN VERIFIED", "ok") if chain_valid else badge("INTEGRITY COMPROMISED", "critical")
    md(f"""
    <p class="lead">
      Every access, upload, appointment and break-glass override commits to the SHA-256 hash of the preceding entry.
      Status: {status_badge} {badge(f'{len(ss.audit)} Immutable Entries', 'muted')}
    </p>
    """)

    f1, f2 = st.columns([3, 1.5])
    roles = sorted({e["role"].split(" (")[0] for e in ss.audit})
    sel_role = f1.multiselect("Filter by Actor Role", roles, default=[], key=f"filter_audit_{view_key}")
    bg_filter = f2.toggle("Show Break-Glass Overrides Only", key=f"bg_filter_{view_key}")

    rows = [e for e in reversed(ss.audit) if (not sel_role or e["role"].split(" (")[0] in sel_role) and (not bg_filter or e["break_glass"])]
    if not rows:
        st.info("No audit entries match filter.")
        return

    df = pd.DataFrame([{
        "Timestamp (IST)": e["ts"], "Actor / Role": e["role"], "Action": e["action"],
        "Data / Scope": e["data"], "Break-Glass": "YES (OVERRIDE)" if e["break_glass"] else "Standard",
        "SHA-256 Chain Hash": e["hash"][:14] + "..."
    } for e in rows])

    styled = df.style.apply(lambda r: ["background-color:#FEE2E2;color:#991B1B;font-weight:700" if "YES" in str(r["Break-Glass"]) else "" for _ in r], axis=1)
    st.dataframe(styled, hide_index=True, height=min(400, 40 + 35 * len(df)))


# =============================================================================
# 14. MAIN ROUTER
# =============================================================================
def view_admission() -> None:
    md("""
    <div class="hero">
      <div>
        <div class="eyebrow">EMERGENCY ADMISSION &amp; ONLINE PAYMENT PORTAL</div>
        <div class="title">Pre-Admission Form &amp; Deposit Payment</div>
        <span class="tag">Family Form &bull; Online Deposit &bull; Hospital Staff Desk</span>
      </div>
    </div>
    """)
    st.markdown("&nbsp;")

    try:
        from admission_portal import config, db, family_view, security, staff_view

        try:
            db.init_schema()
        except Exception:
            pass

        tab_family, tab_staff, tab_workflow = st.tabs([
            "📋 Family Admission Form & Payment",
            "🔐 Hospital Staff Desk",
            "ℹ️ How It Works",
        ])

        with tab_family:
            token = st.query_params.get("t", "") or st.session_state.get("adm_active_token", "")
            if not token:
                # Ensure a valid demo token so the full form is immediately visible and usable
                reqs = db.list_requests(limit=1)
                if reqs:
                    rid = reqs[0]["id"]
                else:
                    rid = db.create_request("aiims_trauma", "SOS-2026-8812", "Aarav Sharma")
                    db.set_deposit_amount(rid, 500000)  # ₹5,000 deposit
                tp = security.generate_token()
                db.save_token(tp.token_hash, rid, tp.expires_at)
                token = tp.raw_token
                st.session_state["adm_active_token"] = token

            family_view.render(token=token)

        with tab_staff:
            staff_view.render()

        with tab_workflow:
            st.markdown("""
            ### 🏥 JeevanSetu AI — Emergency Pre-Admission & Online Payment Workflow
            1. **Emergency Admission Trigger:** Jab patient emergency me hospital me admit ho, hospital staff ek admission request create karta hai.
            2. **48-Hour Secure Family Link:** Family member ko SMS / WhatsApp par secure link milta hai (`?t=TOKEN`).
            3. **Online Formalities:** Family patient details bharti hai, ID/insurance upload karti hai, aur medical consent checkbox tick karti hai.
            4. **Admission Deposit:** Family online deposit pay kar sakti hai (UPI, QR, Cards, NetBanking via Razorpay) ya *"Hospital me aakar pay karunga"* select kar sakti hai.
            5. **Status & Receipt:** Status real-time update hota hai (*Submitted -> Under Review -> Confirmed -> Paid*) aur payment receipt PDF turant download ho jati hai.
            <br>
            <i>⚠️ Zaroori Soochna: Emergency medical treatment payment par depend nahi karti. Ye portal sirf admission formalities aur deposit ke liye hai.</i>
            """, unsafe_allow_html=True)

    except Exception as ex:
        st.error(f"Error loading Admission Portal: {ex}")


def main() -> None:
    init_state()
    st.markdown(CSS, unsafe_allow_html=True)

    render_header_auth()
    render_sidebar()

    role = st.session_state.role

    if role == ROLE_LOGIN:
        render_login_portal()
    elif role == ROLE_BYSTANDER:
        view_bystander()
    elif role == ROLE_PATIENT:
        view_patient()
    elif role == ROLE_DOCTOR:
        view_doctor()
    elif role == ROLE_FAMILY:
        view_family()
    elif role == ROLE_ADMIN:
        view_admin()
    elif role == ROLE_ADMISSION:
        view_admission()
    else:
        render_login_portal()

    md("""
    <div class="footer">
      <b>JeevanSetu AI</b> &bull; Built by <b>Team Optimove</b> (Aayush Varshney, Sonali, Aksha Malik, Diksha Kalia) for <b>Roboforge Hackathon 2026</b>.<br>
      <i>"A place where minutes don't cost lives."</i> &bull; Prototype for evaluation purposes.
    </div>
    """)


if __name__ == "__main__":
    main()
