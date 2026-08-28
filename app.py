"""
HazeCrop Malaysia
=================
NASA MODIS Satellite Intelligence for Pre-Season Crop Planning

Entry point.  Run with:
    streamlit run app.py

Architecture
------------
app.py (this file)
├── config/settings.py          — all constants and tuning parameters
├── services/
│   ├── earth_engine.py         — EE initialisation
│   ├── aod_service.py          — MODIS MAIAC AOD data queries
│   └── malaysia_regions.py     — state boundaries and centroids
├── analysis/
│   ├── pattern_detection.py    — monthly stats + seasonal scoring
│   ├── seasonal_prediction.py  — outlook generation + timeline
│   └── confidence.py           — data-driven confidence calculation
├── agents/
│   ├── data_analyst.py         — Agent 1: data fetch & validation
│   ├── pattern_analyst.py      — Agent 2: pattern detection
│   ├── outlook_agent.py        — Agent 3: seasonal outlook
│   └── preparedness_agent.py   — Agent 4: crop preparedness plan
├── ui/
│   ├── styles.py               — global CSS injection
│   ├── overview.py             — overview cards
│   ├── map_view.py             — satellite map
│   ├── patterns.py             — historical pattern charts
│   └── ai_insights.py         — AI insights + preparedness plan
└── utils/
    ├── formatters.py           — number / HTML formatters
    └── dates.py                — calendar helpers
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="HazeCrop Malaysia",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Styles (inject before anything else renders) ──────────────────────────────
from ui.styles import inject_styles
inject_styles()

# ── Earth Engine init ─────────────────────────────────────────────────────────
from services.earth_engine import initialize_earth_engine

ee_ready = initialize_earth_engine()

if not ee_ready:
    st.markdown(
        '<div class="hc-ee-error">'
        '<div style="font-size:40px;margin-bottom:16px;">🛰️</div>'
        '<div style="font-family:Fraunces,Georgia,serif;font-size:20px;font-weight:600;color:#1E2A1C;margin-bottom:10px;">Satellite connection unavailable</div>'
        '<div style="font-size:14px;color:#5C6858;line-height:1.7;margin-bottom:16px;">'
        'HazeCrop could not connect to Google Earth Engine.<br><br>'
        'Please check authentication and project configuration.<br><br>'
        'Run <code style="background:#F6F4EE;padding:2px 6px;border-radius:4px;border:1px solid #E4E1D6;color:#1E2A1C;">earthengine authenticate</code> in your terminal, '
        'then restart the app with your project ID set as the '
        '<code style="background:#F6F4EE;padding:2px 6px;border-radius:4px;border:1px solid #E4E1D6;color:#1E2A1C;">EARTHENGINE_PROJECT</code> environment variable.'
        '</div></div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── Remaining imports (after EE is confirmed ready) ───────────────────────────
from services.aod_service import get_historical_aod as _get_historical_aod


@st.cache_data(show_spinner=False, ttl=3600)
def _fetch_aod_cached(_region_fao_name: str,
                      start_year: int,
                      end_year: int,
                      state_name: str):
    """Cached wrapper around get_historical_aod for app-level reuse."""
    return _get_historical_aod(_region_fao_name, start_year, end_year, state_name)


from services.malaysia_regions import MALAYSIA_STATES
from config.settings import (
    DEFAULT_STATE,
    DEFAULT_TARGET_YEAR,
    DEFAULT_HISTORICAL_YEARS,
)
from utils.dates import current_year
from utils.formatters import agent_status_html

from ui.overview    import render_overview_idle, render_overview_results, render_settings_changed_banner
from ui.map_view    import render_map_idle, render_map_results
from ui.patterns    import render_patterns_idle, render_patterns_results
from ui.ai_insights import render_ai_insights_idle, render_ai_insights_results


# ══════════════════════════════════════════════════════════════════════════════
# NAVBAR
# ══════════════════════════════════════════════════════════════════════════════

import streamlit.components.v1 as components

st.markdown("""
<div class="hc-navbar">
    <div class="hc-logo">🌾&nbsp;<span>HazeCrop</span></div>
    <div style="flex:1"></div>
    <button class="hc-nav-pill" id="nav-0">Overview</button>
    <button class="hc-nav-pill" id="nav-1">Map</button>
    <button class="hc-nav-pill" id="nav-2">Patterns</button>
    <button class="hc-nav-pill" id="nav-3">AI Insights</button>
</div>
""", unsafe_allow_html=True)

components.html("""
<script>
(function() {
    function switchTab(index) {
        var tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
        if (tabs && tabs[index]) {
            tabs[index].click();
            setTimeout(function() {
                var tabList = window.parent.document.querySelector('[data-baseweb="tab-list"]');
                if (tabList) {
                    tabList.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 100);
        }
    }
    // Attach to buttons in the parent document
    function attachListeners() {
        var parent = window.parent.document;
        for (var i = 0; i < 4; i++) {
            var btn = parent.getElementById('nav-' + i);
            if (btn) {
                (function(idx) {
                    btn.addEventListener('click', function() { switchTab(idx); });
                })(i);
            }
        }
    }
    // Wait for parent DOM to be ready
    if (window.parent.document.readyState === 'complete') {
        attachListeners();
    } else {
        window.parent.document.addEventListener('DOMContentLoaded', attachListeners);
    }
    // Retry after a short delay in case Streamlit re-renders
    setTimeout(attachListeners, 800);
})();
</script>
""", height=0)


# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    '<div class="hc-hero">'
    '<div class="hc-hero-content">'
    '<div class="hc-hero-tag">🛰 NASA MODIS &middot; Multi-Year Aerosol Analysis</div>'
    '<div class="hc-hero-title">Seasonal Haze Outlook<br><span>for Malaysian Agriculture</span></div>'
    '<div class="hc-hero-sub">Multi-year NASA MODIS satellite aerosol data, analysed by a four-agent AI system to identify recurring haze seasons and generate pre-season crop preparedness plans for Malaysian farmers.</div>'
    '</div></div>',
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALISATION
# ══════════════════════════════════════════════════════════════════════════════

def _init_session_state() -> None:
    defaults = {
        "analysis_completed":    False,
        "analysis_results":      None,
        "last_state":            None,
        "last_year":             None,
        "last_historical_years": None,
        "settings_changed":      False,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


_init_session_state()


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS PANEL
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="hc-settings">', unsafe_allow_html=True)
st.markdown(
    '<div class="hc-settings-title">⚙ &nbsp;Analysis Settings</div>',
    unsafe_allow_html=True,
)

_this_year = current_year()

# historical_years is fixed internally — not exposed to the user
historical_years = DEFAULT_HISTORICAL_YEARS

col_state, col_year, col_btn = st.columns([2, 1, 1])

with col_state:
    default_idx = MALAYSIA_STATES.index(DEFAULT_STATE) if DEFAULT_STATE in MALAYSIA_STATES else 0
    state = st.selectbox(
        "📍 State / Territory",
        MALAYSIA_STATES,
        index=default_idx,
        key="widget_state",
    )

with col_year:
    target_year = st.selectbox(
        "📅 Target Year",
        list(range(_this_year, _this_year + 6)),
        index=1 if DEFAULT_TARGET_YEAR - _this_year >= 1 else 0,
        key="widget_year",
    )

with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    run_analysis = st.button("🚀 Analyse Haze Pattern", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# ── Detect settings change after a completed analysis ─────────────────────────
if st.session_state.analysis_completed:
    changed = (
        state          != st.session_state.last_state
        or target_year != st.session_state.last_year
    )
    st.session_state.settings_changed = changed
else:
    st.session_state.settings_changed = False


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS PIPELINE
# When run_analysis is clicked:
#   1. Run the four-agent pipeline
#   2. Store results in session state
#   3. Render the reactive dashboard
# ══════════════════════════════════════════════════════════════════════════════

if run_analysis:
    import time
    from agents.data_analyst       import run_data_analyst
    from agents.pattern_analyst    import run_pattern_analyst
    from agents.outlook_agent      import run_outlook_agent
    from agents.preparedness_agent import run_preparedness_agent

    _t_start = time.time()

    agent_statuses = {
        "🔬 Data Analyst":       "off",
        "📊 Pattern Analyst":    "off",
        "🌫 Outlook Agent":      "off",
        "🌱 Preparedness Agent": "off",
    }
    status_placeholder = st.empty()
    status_placeholder.markdown(
        agent_status_html(agent_statuses), unsafe_allow_html=True
    )

    # ── Agent 1: Data Analyst ─────────────────────────────────────────────────
    with st.spinner(f"Analysing {historical_years} years of NASA MODIS data for {state}…"):
        data_result = run_data_analyst(state, target_year, historical_years)

    if data_result["status"] == "error":
        agent_statuses["🔬 Data Analyst"] = "warn"
        status_placeholder.markdown(agent_status_html(agent_statuses), unsafe_allow_html=True)
        st.markdown(
            f'<div class="hc-card" style="border-left:4px solid #9B3330;">'
            f'<div class="hc-card-header">'
            f'<div class="hc-card-icon icon-risk">⚠️</div>'
            f'<div><div class="hc-card-title">Satellite Data Unavailable</div>'
            f'<div class="hc-card-meta">Analysis could not be completed</div></div>'
            f'</div>'
            f'<div class="hc-card-body">{data_result["message"]}</div>'
            f'<div style="font-size:12px;color:#8FA688;">Try a different state or adjust the historical data period.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.stop()

    agent_statuses["🔬 Data Analyst"] = "ok" if data_result["status"] == "ok" else "warn"
    status_placeholder.markdown(agent_status_html(agent_statuses), unsafe_allow_html=True)

    # ── Agent 2: Pattern Analyst ──────────────────────────────────────────────
    with st.spinner("Detecting seasonal aerosol patterns…"):
        pattern_result = run_pattern_analyst(data_result)

    agent_statuses["📊 Pattern Analyst"] = (
        "ok" if pattern_result["status"] == "ok" else "warn"
    )
    status_placeholder.markdown(agent_status_html(agent_statuses), unsafe_allow_html=True)

    # ── Agent 3: Outlook Agent ────────────────────────────────────────────────
    with st.spinner("Generating seasonal haze outlook…"):
        outlook_result = run_outlook_agent(data_result, pattern_result, state, target_year)

    agent_statuses["🌫 Outlook Agent"] = (
        "ok" if outlook_result["status"] == "ok" else "warn"
    )
    status_placeholder.markdown(agent_status_html(agent_statuses), unsafe_allow_html=True)

    # ── Agent 4: Preparedness Agent ───────────────────────────────────────────
    preparedness_result = run_preparedness_agent(outlook_result)

    agent_statuses["🌱 Preparedness Agent"] = (
        "ok" if preparedness_result["status"] == "ok" else "warn"
    )
    status_placeholder.markdown(agent_status_html(agent_statuses), unsafe_allow_html=True)

    # ── Store results in session state ────────────────────────────────────────
    _elapsed = time.time() - _t_start
    st.session_state.analysis_completed    = True
    st.session_state.settings_changed      = False
    st.session_state.last_state            = state
    st.session_state.last_year             = target_year
    st.session_state.last_historical_years = historical_years
    st.session_state.last_load_time        = _elapsed
    st.session_state.analysis_results      = {
        "data_result":         data_result,
        "pattern_result":      pattern_result,
        "outlook_result":      outlook_result,
        "preparedness_result": preparedness_result,
    }
    status_placeholder.markdown(
        agent_status_html(agent_statuses)
        + f'<div style="font-size:11px;color:#8FA688;margin-top:6px;">⏱ Analysis completed in {_elapsed:.1f}s</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# REACTIVE DASHBOARD RENDERING
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.analysis_completed and st.session_state.analysis_results:
    results = st.session_state.analysis_results

    if st.session_state.settings_changed:
        render_settings_changed_banner()

    data_result         = results["data_result"]
    pattern_result      = results["pattern_result"]
    outlook_result      = results["outlook_result"]
    preparedness_result = results["preparedness_result"]

    tab_overview, tab_map, tab_patterns, tab_insights = st.tabs(
        ["📡 Overview", "🗺 Map", "📈 Patterns", "🧠 AI Insights"]
    )

    with tab_overview:
        render_overview_results(outlook_result, preparedness_result)

    with tab_map:
        render_map_results(
            st.session_state.last_state,
            st.session_state.last_year,
            st.session_state.last_historical_years,
            outlook_result,
            data_result,
        )

    with tab_patterns:
        render_patterns_results(
            pattern_result,
            outlook_result,
            st.session_state.last_historical_years,
        )

    with tab_insights:
        render_ai_insights_results(
            outlook_result,
            preparedness_result,
            data_result,
            pattern_result,
        )

else:
    tab_overview, tab_map, tab_patterns, tab_insights = st.tabs(
        ["📡 Overview", "🗺 Map", "📈 Patterns", "🧠 AI Insights"]
    )

    with tab_overview:
        render_overview_idle(state, target_year)

    with tab_map:
        render_map_idle(state)

    with tab_patterns:
        render_patterns_idle()

    with tab_insights:
        render_ai_insights_idle()