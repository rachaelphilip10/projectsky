"""
HazeCrop Malaysia — Global CSS styles.

Call inject_styles() once at the top of app.py.
"""

import streamlit as st


def inject_styles() -> None:
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0f1117 0%, #1a1f2e 50%, #0f1117 100%);
    min-height: 100vh;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 1100px; }

/* ── Navbar ── */
.hc-navbar {
    position: sticky; top: 0; z-index: 999;
    background: rgba(15,17,23,0.92);
    backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
    border-bottom: 1px solid rgba(255,255,255,0.07);
    padding: 14px 32px; display: flex; align-items: center; gap: 12px;
}
.hc-logo { font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; }
.hc-logo span {
    background: linear-gradient(90deg, #4ade80, #22d3ee);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hc-nav-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 14px; border-radius: 999px; font-size: 13px; font-weight: 500;
    color: rgba(255,255,255,0.55); cursor: pointer; transition: all 0.2s;
    border: 1px solid transparent; text-decoration: none;
}
.hc-nav-pill:hover { color: #ffffff; background: rgba(255,255,255,0.07); border-color: rgba(255,255,255,0.10); }

/* ── Hero ── */
.hc-hero { padding: 48px 32px 32px; text-align: center; }
.hc-hero-tag {
    display: inline-block; padding: 4px 14px; border-radius: 999px;
    background: rgba(74,222,128,0.12); border: 1px solid rgba(74,222,128,0.25);
    color: #4ade80; font-size: 12px; font-weight: 600; letter-spacing: 0.8px;
    text-transform: uppercase; margin-bottom: 18px;
}
.hc-hero-title {
    font-size: clamp(32px, 5vw, 52px); font-weight: 800; color: #ffffff;
    line-height: 1.1; letter-spacing: -1.5px; margin-bottom: 14px;
}
.hc-hero-title span {
    background: linear-gradient(90deg, #4ade80 0%, #22d3ee 50%, #818cf8 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hc-hero-sub {
    font-size: 16px; color: rgba(255,255,255,0.45);
    max-width: 560px; margin: 0 auto 32px; line-height: 1.6;
}

/* ── Section label ── */
.hc-section-label {
    font-size: 11px; font-weight: 700; letter-spacing: 1.2px;
    text-transform: uppercase; color: rgba(255,255,255,0.28); padding: 28px 0 10px;
}

/* ── Cards ── */
.hc-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 24px 28px; margin-bottom: 16px;
    transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
    animation: fadeUp 0.4s ease both;
}
.hc-card:hover {
    border-color: rgba(255,255,255,0.16); transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.35);
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.hc-card-header { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 14px; }
.hc-card-icon {
    width: 42px; height: 42px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
}
.icon-haze  { background: rgba(251,146,60,0.15);  border: 1px solid rgba(251,146,60,0.25); }
.icon-veg   { background: rgba(74,222,128,0.12);   border: 1px solid rgba(74,222,128,0.22); }
.icon-risk  { background: rgba(248,113,113,0.13);  border: 1px solid rgba(248,113,113,0.23); }
.icon-map   { background: rgba(34,211,238,0.12);   border: 1px solid rgba(34,211,238,0.22); }
.icon-trend { background: rgba(129,140,248,0.13);  border: 1px solid rgba(129,140,248,0.23); }
.icon-data  { background: rgba(250,204,21,0.10);   border: 1px solid rgba(250,204,21,0.20); }
.icon-ai    { background: rgba(167,139,250,0.13);  border: 1px solid rgba(167,139,250,0.23); }
.icon-plan  { background: rgba(34,211,238,0.12);   border: 1px solid rgba(34,211,238,0.22); }

.hc-card-title { font-size: 15px; font-weight: 700; color: #ffffff; line-height: 1.3; margin-bottom: 4px; }
.hc-card-meta  { font-size: 12px; color: rgba(255,255,255,0.35); }
.hc-card-body  { font-size: 14px; color: rgba(255,255,255,0.65); line-height: 1.7; margin-bottom: 14px; }

/* ── Stat pills ── */
.hc-stat-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.hc-stat-pill {
    display: inline-flex; flex-direction: column; padding: 10px 16px;
    border-radius: 12px; background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09); min-width: 100px;
}
.hc-stat-label {
    font-size: 10px; font-weight: 600; letter-spacing: 0.6px;
    text-transform: uppercase; color: rgba(255,255,255,0.35); margin-bottom: 4px;
}
.hc-stat-value { font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; }
.hc-stat-value.green  { color: #4ade80; }
.hc-stat-value.orange { color: #fb923c; }
.hc-stat-value.red    { color: #f87171; }
.hc-stat-value.blue   { color: #22d3ee; }
.hc-stat-value.purple { color: #a78bfa; }

/* ── Risk badges ── */
.hc-risk-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 14px; border-radius: 999px; font-size: 13px;
    font-weight: 700; letter-spacing: 0.3px;
}
.risk-low      { background: rgba(74,222,128,0.15);  color: #4ade80;  border: 1px solid rgba(74,222,128,0.3); }
.risk-moderate { background: rgba(251,146,60,0.15);  color: #fb923c;  border: 1px solid rgba(251,146,60,0.3); }
.risk-high     { background: rgba(248,113,113,0.15); color: #f87171;  border: 1px solid rgba(248,113,113,0.3); }
.risk-severe   { background: rgba(167,139,250,0.15); color: #a78bfa;  border: 1px solid rgba(167,139,250,0.3); }

/* ── Misc ── */
.hc-divider { height: 1px; background: rgba(255,255,255,0.06); margin: 8px 0 16px; }

.hc-settings {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; padding: 24px 28px; margin-bottom: 24px;
}
.hc-settings-title {
    font-size: 13px; font-weight: 700; color: rgba(255,255,255,0.5);
    letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 18px;
}

/* ── Agent pills ── */
.hc-agent-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
.hc-agent-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 12px; border-radius: 999px; font-size: 12px; font-weight: 600;
}
.agent-ok   { background: rgba(74,222,128,0.12); color: #4ade80; border: 1px solid rgba(74,222,128,0.25); }
.agent-warn { background: rgba(251,146,60,0.12); color: #fb923c; border: 1px solid rgba(251,146,60,0.25); }
.agent-off  { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.3); border: 1px solid rgba(255,255,255,0.08); }

/* ── Action cards ── */
.hc-action-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 18px 22px; margin-bottom: 10px;
}
.hc-action-priority {
    font-size: 10px; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; margin-bottom: 6px;
}
.priority-high   { color: #f87171; }
.priority-medium { color: #fb923c; }
.priority-low    { color: #4ade80; }
.hc-action-title { font-size: 14px; font-weight: 700; color: #ffffff; margin-bottom: 4px; }
.hc-action-why   { font-size: 13px; color: rgba(255,255,255,0.55); line-height: 1.6; }

/* ── Disclaimer ── */
.hc-disclaimer {
    font-size: 11px; color: rgba(255,255,255,0.25); text-align: center;
    padding: 16px; border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px; margin-top: 12px; line-height: 1.6;
}

/* ── Timeline ── */
.hc-timeline-phase {
    border-left: 2px solid rgba(74,222,128,0.3);
    padding-left: 18px; margin-bottom: 20px;
}
.hc-timeline-phase-label { font-size: 13px; font-weight: 700; color: #4ade80; margin-bottom: 2px; }
.hc-timeline-phase-title { font-size: 13px; font-weight: 700; color: #ffffff; margin-bottom: 2px; }
.hc-timeline-phase-months {
    font-size: 11px; color: rgba(255,255,255,0.35);
    text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px;
}
.hc-timeline-phase-items { font-size: 13px; color: rgba(255,255,255,0.6); line-height: 1.8; }
.hc-timeline-months {
    font-size: 11px; color: rgba(255,255,255,0.35);
    text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px;
}
.hc-timeline-item {
    font-size: 13px; color: rgba(255,255,255,0.65);
    padding: 3px 0; line-height: 1.6;
}

/* ── AI insight box ── */
.hc-ai-box {
    background: rgba(167,139,250,0.06); border: 1px solid rgba(167,139,250,0.15);
    border-radius: 14px; padding: 18px 22px; margin-bottom: 12px;
}
.hc-ai-box-label {
    font-size: 10px; font-weight: 700; letter-spacing: 0.8px;
    text-transform: uppercase; color: #a78bfa; margin-bottom: 8px;
}
.hc-ai-box-text {
    font-size: 14px; color: rgba(255,255,255,0.72); line-height: 1.7;
}

/* ── Settings changed banner ── */
.hc-stale-banner {
    background: rgba(251,146,60,0.08); border: 1px solid rgba(251,146,60,0.25);
    border-radius: 12px; padding: 10px 16px; margin-bottom: 12px;
    font-size: 12px; color: #fb923c; font-weight: 600;
}

/* ── Streamlit widget overrides ── */
div[data-testid="stSelectbox"] > label,
div[data-testid="stSlider"] > label {
    color: rgba(255,255,255,0.55) !important; font-size: 12px !important;
    font-weight: 600 !important; letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.10) !important; color: #ffffff !important;
}
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #4ade80, #22d3ee) !important;
    color: #0f1117 !important; font-weight: 700 !important; font-size: 14px !important;
    border: none !important; padding: 12px 24px !important;
    border-radius: 14px !important; width: 100% !important;
    transition: opacity 0.2s, transform 0.15s !important;
}
div[data-testid="stButton"] > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 14px !important;
}
div[data-testid="stExpander"] summary { color: rgba(255,255,255,0.7) !important; font-weight: 600 !important; font-size: 13px !important; }
div[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.08) !important;
}
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 14px 18px;
}
div[data-testid="stMetric"] label { color: rgba(255,255,255,0.45) !important; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #ffffff !important; }
div[data-testid="stAlert"] { border-radius: 14px !important; border: none !important; }
button[data-baseweb="tab"] { color: rgba(255,255,255,0.45) !important; font-weight: 600 !important; font-size: 13px !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #ffffff !important; border-bottom-color: #4ade80 !important; }
div[data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid rgba(255,255,255,0.08) !important; gap: 4px; }
div[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.06) !important; color: rgba(255,255,255,0.8) !important;
    border: 1px solid rgba(255,255,255,0.12) !important; border-radius: 12px !important;
    font-weight: 600 !important; font-size: 13px !important;
}
div[data-testid="stSpinner"] > div { border-top-color: #4ade80 !important; }
</style>
""", unsafe_allow_html=True)
