"""
HazeCrop Malaysia — Global CSS styles.

Design system:
  FOREST  #1E2A1C  near-black forest green (headings, nav text)
  MOSS    #4C6B45  primary accent (buttons, active states)
  SAGE    #8FA688  muted secondary
  CREAM   #F6F4EE  main page background
  CARD    #FFFFFF  card/panel background
  LINE    #E4E1D6  borders

Typography:
  Fraunces — headings, hero, section titles
  Inter    — body, labels, controls, metrics

Call inject_styles() once at the top of app.py.
"""

import streamlit as st


def inject_styles() -> None:
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,600;9..144,700&family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Tokens ── */
:root {
    --forest: #1E2A1C;
    --moss:   #4C6B45;
    --moss-d: #3A5535;
    --sage:   #8FA688;
    --cream:  #F6F4EE;
    --card:   #FFFFFF;
    --line:   #E4E1D6;
    --line-d: #CFC9BC;
    --text:   #1E2A1C;
    --muted:  #5C6858;
    --soft:   #8FA688;
    --amber:  #A06C2A;
    --red:    #9B3330;
    --shadow: 0 2px 16px rgba(30,42,28,0.07);
    --shadow-lg: 0 8px 32px rgba(30,42,28,0.11);
    --radius: 16px;
    --radius-sm: 10px;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}
.stApp {
    background-color: var(--cream) !important;
    color: var(--text) !important;
    min-height: 100vh;
    overflow-x: hidden; /* prevent horizontal scrollbar from negative-margin bleed */
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 60px !important;
    max-width: 1200px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    overflow-x: visible !important; /* allow hero to bleed without clipping */
}
/* Streamlit wraps each st.markdown() in these — must not clip or add gap */
[data-testid="stMarkdownContainer"],
div.element-container {
    overflow: visible !important;
}

/* ── Navbar ── */
.hc-navbar {
    position: sticky; top: 0; z-index: 1000;
    isolation: isolate;
    background: rgba(246,244,238,0.95);
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--line);
    display: flex; align-items: center; gap: 10px;
    padding: 14px calc(2rem + 18px) 14px calc(2rem + 14px);
    /* bleed out of the container padding on both sides */
    margin-left: -2rem;
    margin-right: -2rem;
}
.hc-logo {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 20px; font-weight: 600; color: var(--forest);
    letter-spacing: -0.3px; display: flex; align-items: center; gap: 8px;
}
.hc-logo span { color: var(--moss); -webkit-text-fill-color: var(--moss); }
.hc-nav-pill {
    display: inline-flex; align-items: center;
    padding: 5px 14px; border-radius: 999px; font-size: 13px; font-weight: 500;
    color: var(--muted); cursor: pointer; transition: all 0.2s;
    border: 1px solid var(--line); text-decoration: none;
    background: var(--card);
}
.hc-nav-pill:hover {
    color: var(--forest); background: var(--cream);
    border-color: var(--moss); text-decoration: none;
}

/* ── Hero (farm background with dark gradient overlay) ── */
.hc-hero {
    position: relative;
    z-index: 0;
    min-height: 440px;
    /*
     * Full-bleed technique: negative margins pull the element to the viewport
     * edge without changing the element's own width (avoids overflow/scrollbar).
     * calc(50% - 50vw) moves left edge to viewport left; matching right margin
     * pulls the right edge to the viewport right.
     */
    margin-left:  calc(50% - 50vw);
    margin-right: calc(50% - 50vw);
    margin-bottom: 40px;
    padding: 90px calc(50vw - 50% + 8%) 72px;
    display: flex; align-items: flex-end;
    overflow: hidden;
    background:
        linear-gradient(
            to right,
            rgba(20,31,18,0.88) 0%,
            rgba(20,31,18,0.60) 55%,
            rgba(20,31,18,0.22) 100%
        ),
        url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=2400&q=80")
        center / cover no-repeat;
}
.hc-hero::after {
    content: "";
    position: absolute; inset: 0;
    background: linear-gradient(0deg, rgba(20,31,18,0.50) 0%, transparent 50%);
    pointer-events: none;
    z-index: 1;
}
.hc-hero-content { position: relative; z-index: 2; max-width: 720px; }
.hc-hero-tag {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 13px; border-radius: 999px;
    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.28);
    color: #E8F0E5; font-size: 11px; font-weight: 700;
    letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 20px;
    backdrop-filter: blur(6px);
}
.hc-hero-title {
    font-family: 'Fraunces', Georgia, serif;
    font-size: clamp(36px, 5.5vw, 62px); font-weight: 600;
    color: #FFFFFF !important; line-height: 1.02;
    letter-spacing: -0.5px; margin-bottom: 16px;
}
.hc-hero-title span { color: #C8DDB8 !important; -webkit-text-fill-color: #C8DDB8 !important; }
.hc-hero-sub {
    font-size: 15px; color: rgba(255,255,255,0.80);
    max-width: 560px; margin: 0 0 0; line-height: 1.65;
}

/* ── Section label ── */
.hc-section-label {
    font-size: 10px; font-weight: 700; letter-spacing: 1.4px;
    text-transform: uppercase; color: var(--sage); padding: 24px 0 10px;
    display: flex; align-items: center; gap: 10px;
}
.hc-section-label::after {
    content: ""; height: 1px; flex: 1; background: var(--line);
}

/* ── Cards ── */
.hc-card {
    background: var(--card); border: 1px solid var(--line);
    border-radius: var(--radius); padding: 22px 26px; margin-bottom: 14px;
    box-shadow: var(--shadow);
    transition: border-color 0.22s, transform 0.22s, box-shadow 0.22s;
}
.hc-card:hover {
    border-color: var(--line-d); transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}
.hc-card-header { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 14px; }
.hc-card-icon {
    width: 40px; height: 40px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}
.icon-haze  { background: #FEF3E2; border: 1px solid #EDD9B0; }
.icon-veg   { background: #EBF2E8; border: 1px solid #C5D9BE; }
.icon-risk  { background: #FAEAEA; border: 1px solid #E8C5C5; }
.icon-map   { background: #E8F4F6; border: 1px solid #B8D9DF; }
.icon-trend { background: #EEF0F8; border: 1px solid #C6CCDF; }
.icon-data  { background: #F7F3E3; border: 1px solid #DDD4B0; }
.icon-ai    { background: #F0EBF7; border: 1px solid #CCBCE0; }
.icon-plan  { background: #EBF2E8; border: 1px solid #C5D9BE; }

.hc-card-title {
    font-size: 14px; font-weight: 700; color: var(--forest);
    line-height: 1.3; margin-bottom: 3px;
}
.hc-card-meta  { font-size: 11px; color: var(--soft); }
.hc-card-body  { font-size: 14px; color: var(--muted); line-height: 1.7; margin-bottom: 12px; }

/* ── Stat pills ── */
.hc-stat-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.hc-stat-pill {
    display: inline-flex; flex-direction: column; padding: 10px 16px;
    border-radius: var(--radius-sm); background: var(--cream);
    border: 1px solid var(--line); min-width: 100px;
}
.hc-stat-label {
    font-size: 9px; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; color: var(--soft); margin-bottom: 4px;
}
.hc-stat-value {
    font-size: 20px; font-weight: 700; color: var(--forest); letter-spacing: -0.5px;
}
.hc-stat-value.green  { color: var(--moss); }
.hc-stat-value.orange { color: var(--amber); }
.hc-stat-value.red    { color: var(--red); }
.hc-stat-value.blue   { color: var(--moss); }
.hc-stat-value.purple { color: #5C3D8F; }

/* ── Risk badges ── */
.hc-risk-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 5px 13px; border-radius: 999px; font-size: 12px;
    font-weight: 700; letter-spacing: 0.2px;
}
.risk-low      { background: #EAF3E7; color: #3A5A33; border: 1px solid #BDD4B6; }
.risk-moderate { background: #F9EFE1; color: #8C5A1A; border: 1px solid #DEC48A; }
.risk-high     { background: #FAEAEA; color: #852424; border: 1px solid #DEB0B0; }
.risk-severe   { background: #F3EBF9; color: #5C2D91; border: 1px solid #C9A8E8; }

/* ── Misc ── */
.hc-divider { height: 1px; background: var(--line); margin: 10px 0 16px; }

/* ── Settings panel ── */
.hc-settings {
    background: var(--card); border: 1px solid var(--line);
    border-radius: var(--radius); padding: 20px 24px; margin-bottom: 24px;
    box-shadow: var(--shadow);
}
.hc-settings-title {
    font-size: 10px; font-weight: 700; color: var(--sage);
    letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 16px;
}

/* ── Agent pills ── */
.hc-agent-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
.hc-agent-pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 12px; border-radius: 999px; font-size: 11px; font-weight: 600;
}
.agent-ok   { background: #EAF3E7; color: #3A5A33; border: 1px solid #BDD4B6; }
.agent-warn { background: #F9EFE1; color: #8C5A1A; border: 1px solid #DEC48A; }
.agent-off  { background: var(--cream); color: var(--soft); border: 1px solid var(--line); }

/* ── Action cards ── */
.hc-action-card {
    background: var(--cream); border: 1px solid var(--line);
    border-radius: var(--radius-sm); padding: 16px 20px; margin-bottom: 10px;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.hc-action-card:hover { border-color: var(--line-d); box-shadow: var(--shadow); }
.hc-action-priority {
    font-size: 9px; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; margin-bottom: 5px;
}
.priority-high   { color: var(--red); }
.priority-medium { color: var(--amber); }
.priority-low    { color: var(--moss); }
.hc-action-title { font-size: 14px; font-weight: 700; color: var(--forest); margin-bottom: 4px; }
.hc-action-why   { font-size: 13px; color: var(--muted); line-height: 1.65; }

/* ── Disclaimer ── */
.hc-disclaimer {
    font-size: 11px; color: var(--soft); text-align: center;
    padding: 14px 18px; border: 1px solid var(--line);
    border-radius: var(--radius-sm); margin-top: 14px; line-height: 1.65;
    background: var(--cream);
}

/* ── Timeline ── */
.hc-timeline-phase {
    border-left: 2px solid var(--moss); padding-left: 18px; margin-bottom: 20px;
}
.hc-timeline-phase-label { font-size: 12px; font-weight: 700; color: var(--moss); margin-bottom: 2px; }
.hc-timeline-phase-title { font-size: 13px; font-weight: 700; color: var(--forest); margin-bottom: 2px; }
.hc-timeline-phase-months {
    font-size: 10px; color: var(--soft);
    text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 7px;
}
.hc-timeline-phase-items { font-size: 13px; color: var(--muted); line-height: 1.8; }
.hc-timeline-months {
    font-size: 10px; color: var(--soft);
    text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 7px;
}
.hc-timeline-item { font-size: 13px; color: var(--muted); padding: 3px 0; line-height: 1.6; }

/* ── AI insight box ── */
.hc-ai-box {
    background: #F0F4EE; border: 1px solid #D0DCCB;
    border-radius: var(--radius-sm); padding: 16px 20px; margin-bottom: 10px;
}
.hc-ai-box-label {
    font-size: 9px; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; color: var(--moss); margin-bottom: 8px;
}
.hc-ai-box-text { font-size: 13px; color: var(--muted); line-height: 1.7; }

/* ── Settings changed banner ── */
.hc-stale-banner {
    background: #FAF3E6; border: 1px solid #DEC48A;
    border-radius: var(--radius-sm); padding: 10px 16px; margin-bottom: 14px;
    font-size: 12px; color: var(--amber); font-weight: 600;
    display: flex; align-items: center; gap: 8px;
}

/* ── EE error card ── */
.hc-ee-error {
    background: var(--card); border: 1px solid #DEB0B0;
    border-radius: var(--radius); padding: 48px 36px; margin: 60px auto;
    max-width: 560px; text-align: center; box-shadow: var(--shadow);
}

/* ── Streamlit widget overrides ── */
div[data-testid="stSelectbox"] > label,
div[data-testid="stSlider"] > label {
    color: var(--muted) !important; font-size: 11px !important;
    font-weight: 700 !important; letter-spacing: 0.6px !important;
    text-transform: uppercase !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: var(--cream) !important;
    border: 1px solid var(--line) !important; color: var(--forest) !important;
    border-radius: var(--radius-sm) !important;
}
div[data-testid="stButton"] > button {
    background: var(--moss) !important;
    color: #FFFFFF !important; font-weight: 700 !important; font-size: 13px !important;
    border: none !important; padding: 11px 22px !important;
    border-radius: 999px !important; width: 100% !important;
    transition: background 0.2s, transform 0.15s, box-shadow 0.2s !important;
    letter-spacing: 0.2px !important;
}
div[data-testid="stButton"] > button:hover {
    background: var(--moss-d) !important; transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(76,107,69,0.22) !important;
}
div[data-testid="stExpander"] {
    background: var(--card) !important;
    border: 1px solid var(--line) !important; border-radius: var(--radius-sm) !important;
}
div[data-testid="stExpander"] summary {
    color: var(--forest) !important; font-weight: 600 !important; font-size: 13px !important;
}
div[data-testid="stDataFrame"] {
    background: var(--card) !important;
    border-radius: var(--radius-sm) !important; border: 1px solid var(--line) !important;
}
div[data-testid="stMetric"] {
    background: var(--card); border: 1px solid var(--line);
    border-radius: var(--radius-sm); padding: 14px 18px; box-shadow: var(--shadow);
}
div[data-testid="stMetric"] label {
    color: var(--soft) !important;
    font-size: 10px !important; font-weight: 700 !important;
    text-transform: uppercase; letter-spacing: 0.7px;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: var(--forest) !important;
    font-family: 'Fraunces', Georgia, serif !important;
}
div[data-testid="stAlert"] { border-radius: var(--radius-sm) !important; }
button[data-baseweb="tab"] {
    color: var(--soft) !important; font-weight: 600 !important;
    font-size: 13px !important; background: transparent !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--forest) !important; border-bottom-color: var(--moss) !important;
}
div[data-baseweb="tab-list"] {
    background: transparent !important; border-bottom: 1px solid var(--line) !important; gap: 4px;
}
div[data-testid="stDownloadButton"] > button {
    background: var(--card) !important; color: var(--forest) !important;
    border: 1px solid var(--line) !important; border-radius: 999px !important;
    font-weight: 600 !important; font-size: 12px !important;
    transition: border-color 0.2s, color 0.2s !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    border-color: var(--moss) !important; color: var(--moss) !important;
}
div[data-testid="stSpinner"] > div { border-top-color: var(--moss) !important; }
div[data-testid="stRadio"] label { color: var(--muted) !important; font-size: 13px !important; }
</style>
""", unsafe_allow_html=True)
