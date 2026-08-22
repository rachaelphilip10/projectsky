"""
HazeCrop Malaysia — UI: Overview Tab

Renders the four summary cards and the haze outlook section.

Public API
----------
  render_overview_idle(state, target_year)
  render_overview_results(outlook_result, preparedness_result)
  render_settings_changed_banner()
"""

from __future__ import annotations

import streamlit as st
from utils.formatters import fmt_aod, risk_css_class


def render_overview_idle(state: str, target_year: int) -> None:
    """Show placeholder cards before any analysis has been run."""
    st.markdown('<div id="overview"></div>', unsafe_allow_html=True)
    st.markdown('<div class="hc-section-label">🌫️ &nbsp;Haze Outlook</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="hc-card" style="text-align:center;padding:40px 28px;">
        <div style="font-size:32px;margin-bottom:14px;">🌫️</div>
        <div class="hc-card-title" style="font-size:17px;margin-bottom:10px;">Haze Outlook</div>
        <div class="hc-card-body" style="max-width:440px;margin:0 auto;">
            Select a location and run the analysis to identify recurring haze periods
            for <strong style="color:#ffffff;">{state}</strong>,
            targeting <strong style="color:#ffffff;">{target_year}</strong>.
        </div>
        <div style="margin-top:20px;font-size:12px;color:rgba(255,255,255,0.25);">
            Click <strong>🚀 Analyse Haze Pattern</strong> above to begin.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_settings_changed_banner() -> None:
    """Show a subtle warning that settings have changed since last analysis."""
    st.markdown("""
    <div class="hc-stale-banner">
        ⚠ Settings changed — run analysis to refresh results.
    </div>
    """, unsafe_allow_html=True)


def render_overview_results(outlook_result: dict, preparedness_result: dict) -> None:
    """
    Render the four reactive summary cards after a successful analysis.
    """
    st.markdown('<div id="overview"></div>', unsafe_allow_html=True)
    st.markdown('<div class="hc-section-label">🌫️ &nbsp;Seasonal Haze Outlook</div>', unsafe_allow_html=True)

    outlook    = outlook_result["outlook"]
    confidence = outlook_result["confidence"]

    risk_level  = outlook["risk_level"]
    risk_css    = risk_css_class(risk_level)
    peak_month  = outlook["peak_month_name"]
    season_lbl  = outlook["primary_season_label"]
    mean_aod    = outlook["mean_peak_aod"]
    conf_pct    = confidence["confidence_pct"]
    conf_lbl    = confidence["confidence_label"]

    # ── Haze outlook banner card ──────────────────────────────────────────────
    sec_lbl = outlook.get("secondary_season_label")
    secondary_html = (
        f'<div style="margin-top:10px;font-size:12px;color:rgba(255,255,255,0.4);">'
        f'Secondary elevated period: {sec_lbl}</div>'
    ) if sec_lbl else ""

    st.markdown(f"""
    <div class="hc-card" style="border-color:rgba(251,146,60,0.2);background:rgba(251,146,60,0.03);">
        <div class="hc-card-header">
            <div class="hc-card-icon icon-haze">🌫️</div>
            <div>
                <div class="hc-card-title" style="font-size:17px;">HAZE OUTLOOK</div>
                <div class="hc-card-meta">Historical seasonal pattern · {outlook['state']} · {outlook['target_year']}</div>
            </div>
            <div style="margin-left:auto;">
                <span class="hc-risk-badge {risk_css}">{risk_level}</span>
            </div>
        </div>
        <div style="font-size:26px;font-weight:800;color:#ffffff;margin-bottom:4px;">
            {season_lbl}
        </div>
        <div style="font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:14px;">
            Predicted high-risk period based on {confidence.get('n_years', '?')}-year AOD record
        </div>
        {secondary_html}
        <div class="hc-divider"></div>
        <div style="font-size:12px;color:rgba(255,255,255,0.3);font-style:italic;">
            This is a historical seasonal outlook based on recurring satellite-observed
            aerosol patterns. It is not a guaranteed real-time haze forecast.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Four metric cards ─────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="hc-card" style="text-align:center;padding:20px 16px;">
            <div style="font-size:24px;margin-bottom:8px;">🌫️</div>
            <div class="hc-stat-label" style="text-align:center;margin-bottom:6px;">HAZE OUTLOOK</div>
            <div class="hc-stat-value {_risk_colour(risk_level)}" style="font-size:18px;text-align:center;">{risk_level}</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.35);margin-top:6px;">{season_lbl}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="hc-card" style="text-align:center;padding:20px 16px;">
            <div style="font-size:24px;margin-bottom:8px;">📈</div>
            <div class="hc-stat-label" style="text-align:center;margin-bottom:6px;">PEAK MONTH</div>
            <div class="hc-stat-value orange" style="font-size:18px;text-align:center;">{peak_month}</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.35);margin-top:6px;">Highest recurring AOD</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        aod_display = fmt_aod(mean_aod) if mean_aod is not None else "—"
        st.markdown(f"""
        <div class="hc-card" style="text-align:center;padding:20px 16px;">
            <div style="font-size:24px;margin-bottom:8px;">🛰️</div>
            <div class="hc-stat-label" style="text-align:center;margin-bottom:6px;">HISTORICAL AOD</div>
            <div class="hc-stat-value blue" style="font-size:22px;text-align:center;">{aod_display}</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.35);margin-top:6px;">Multi-year peak-month mean</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        conf_colour = "green" if conf_lbl == "High" else "orange" if conf_lbl == "Medium" else "red"
        st.markdown(f"""
        <div class="hc-card" style="text-align:center;padding:20px 16px;">
            <div style="font-size:24px;margin-bottom:8px;">🧠</div>
            <div class="hc-stat-label" style="text-align:center;margin-bottom:6px;">PATTERN CONFIDENCE</div>
            <div class="hc-stat-value {conf_colour}" style="font-size:22px;text-align:center;">{conf_pct}%</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.35);margin-top:6px;">{conf_lbl} consistency</div>
        </div>
        """, unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _risk_colour(risk_level: str) -> str:
    mapping = {
        "Low":       "green",
        "Moderate":  "orange",
        "High":      "red",
        "Very High": "purple",
    }
    return mapping.get(risk_level, "orange")
