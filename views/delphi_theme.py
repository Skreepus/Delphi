"""
Shared global CSS for Streamlit pages — typography, safe areas, overflow.
Inject once from app.py so all routes inherit consistent text rendering.
"""
from __future__ import annotations

import streamlit as st

GLOBAL_LAYOUT_CSS = """
<style>
/* ── Delphi global layout & typography (all pages) ───────────────────── */
html {
  overflow-x: hidden;
  scroll-behavior: smooth;
}
section[data-testid="stAppViewContainer"] > div {
  overflow-x: hidden;
}

.block-container {
  max-width: min(1200px, 100%) !important;
  padding-left: max(1rem, env(safe-area-inset-left)) !important;
  padding-right: max(1rem, env(safe-area-inset-right)) !important;
  padding-bottom: 2.5rem !important;
}

/* Default Streamlit text: match site body */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaption"] {
  font-family: "Merriweather", Georgia, serif !important;
  font-weight: 300 !important;
  color: #e8e2d9 !important;
  line-height: 1.75 !important;
  overflow-wrap: anywhere;
  word-wrap: break-word;
  hyphens: auto;
}

[data-testid="stMarkdownContainer"] strong {
  font-weight: 500 !important;
  color: #c9a96e !important;
}

[data-testid="stMarkdownContainer"] a {
  color: #c9a96e !important;
  text-decoration: underline;
  text-underline-offset: 3px;
}
[data-testid="stMarkdownContainer"] a:hover {
  color: #dcc598 !important;
}

/* Widget labels */
label[data-testid],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
  font-family: "Merriweather", Georgia, serif !important;
  font-weight: 300 !important;
  color: #6b6560 !important;
  font-size: 0.9rem !important;
  letter-spacing: 0.04em !important;
}

/* Inputs — readable, on-theme */
.stTextInput input,
[data-testid="stTextInput"] input {
  font-family: "Merriweather", Georgia, serif !important;
  font-weight: 300 !important;
  color: #e8e2d9 !important;
  background: #161616 !important;
  border-color: #2a2a2a !important;
}

/* ── Select / multiselect: closed control (dark, no white flash) ───────── */
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  font-family: "Merriweather", Georgia, serif !important;
  font-weight: 300 !important;
  color: #e8e2d9 !important;
  background-color: #161616 !important;
  background: #161616 !important;
  border: 1px solid #2a2a2a !important;
  border-radius: 6px !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] input,
[data-testid="stMultiSelect"] [data-baseweb="select"] input {
  color: #e8e2d9 !important;
  background: transparent !important;
  font-family: "Merriweather", Georgia, serif !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] svg,
[data-testid="stMultiSelect"] [data-baseweb="select"] svg {
  fill: #c9a96e !important;
}

/* Dropdown panel (Base Web portal — may render as body-level sibling to #root) */
.stApp [data-baseweb="popover"],
.stApp div[data-baseweb="popover"],
body > [data-baseweb="popover"],
body [data-baseweb="popover"] {
  background-color: #161616 !important;
  background: #161616 !important;
  color: #e8e2d9 !important;
  border: 1px solid #2a2a2a !important;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.55) !important;
}

[data-baseweb="popover"] > div,
[data-baseweb="popover"] [data-baseweb="scroll"] {
  background-color: #161616 !important;
  background: #161616 !important;
}

.stApp [data-baseweb="popover"] ul,
.stApp ul[role="listbox"],
.stApp [data-baseweb="menu"],
body [data-baseweb="popover"] ul,
body ul[role="listbox"],
body [data-baseweb="menu"] {
  background-color: #161616 !important;
  background: #161616 !important;
  border: none !important;
}

.stApp li[role="option"],
.stApp [data-baseweb="menu"] li,
body li[role="option"],
body [data-baseweb="menu"] li {
  background-color: #161616 !important;
  color: #e8e2d9 !important;
  font-family: "Merriweather", Georgia, serif !important;
  font-weight: 300 !important;
  font-size: 0.95rem !important;
}

.stApp li[role="option"]:hover,
.stApp [data-baseweb="menu"] li:hover,
.stApp [data-baseweb="menu"] li:focus,
body li[role="option"]:hover,
body [data-baseweb="menu"] li:hover,
body [data-baseweb="menu"] li:focus {
  background-color: #1f1f1f !important;
  color: #c9a96e !important;
}

.stApp li[aria-selected="true"][role="option"],
body li[aria-selected="true"][role="option"] {
  background-color: rgba(201, 169, 110, 0.14) !important;
  color: #e8e2d9 !important;
}

/* Multiselect selected tags (chips) */
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
  background: #1f1f1f !important;
  border-color: #2a2a2a !important;
  color: #e8e2d9 !important;
}

[data-testid="stMultiSelect"] [data-baseweb="tag"] span {
  color: #e8e2d9 !important;
}

/* Nav row: avoid float clipping on small screens */
[data-testid="stMain"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"] {
  float: none !important;
  max-width: 100%;
}
[data-testid="stMain"] [data-testid="stHorizontalBlock"]:first-of-type {
  flex-wrap: wrap !important;
  row-gap: 0.35rem;
}

/* Error / warning boxes */
[data-testid="stAlert"] {
  font-family: "Merriweather", Georgia, serif !important;
}

/* Iframe (Explorer) — fill width cleanly */
iframe[title] {
  max-width: 100%;
}
</style>
"""


def inject_global_layout() -> None:
    st.markdown(GLOBAL_LAYOUT_CSS, unsafe_allow_html=True)
