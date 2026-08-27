"""
HazeCrop Malaysia — UI: Overview Tab

Renders the seasonal outlook and preparedness preview cards.

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
    """Show placeholder before any analysis has been run."""
    st.markdown('<div id="overview"></div>', unsafe_allow_html=True)
    st.markdown('<div class="hc-section-label">🌫 &nbsp;Haze Outlook</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hc-card" style="text-align:center;padding:48px 28px;">'
        f'<div style="font-size:36px;margin-bottom:16px;">🌾</div>'
        f'<div style="font-family:Fraunces,Georgia,serif;font-size:22px;font-weight:600;color:#1E2A1C;margin-bottom:10px;">Ready for seasonal analysis</div>'
        f'<div style="font-size:14px;color:#5C6858;max-width:420px;margin:0 auto 20px;line-height:1.7;">'
        f'Select <strong style="color:#1E2A1C;">{state}</strong> and target year '
        f'<strong style="color:#1E2A1C;">{target_year}</strong>, then click '
        f'<strong style="color:#4C6B45;">Analyse Haze Pattern</strong> to identify recurring haze periods.'
        f'</div>'
        f'<div style="font-size:11px;color:#8FA688;letter-spacing:0.8px;text-transform:uppercase;">NASA MODIS · Multi-Year AOD Analysis</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_settings_changed_banner() -> None:
    """Show a subtle warning that settings have changed since last analysis."""
    st.markdown(
        '<div class="hc-stale-banner">&#8635; Settings changed — run analysis again to refresh results.</div>',
        unsafe_allow_html=True,
    )


def render_overview_results(outlook_result: dict, preparedness_result: dict) -> None:
    """Render the seasonal outlook and preparedness preview after a successful analysis."""
    st.markdown('<div id="overview"></div>', unsafe_allow_html=True)
    st.markdown('<div class="hc-section-label">🌫 &nbsp;Seasonal Haze Outlook</div>', unsafe_allow_html=True)

    outlook    = outlook_result["outlook"]
    confidence = outlook_result["confidence"]

    risk_level = outlook["risk_level"]
    risk_css   = risk_css_class(risk_level)
    peak_month = outlook["peak_month_name"]
    season_lbl = outlook["primary_season_label"]
    mean_aod   = outlook["mean_peak_aod"]
    conf_pct   = confidence["confidence_pct"]
    conf_lbl   = confidence["confidence_label"]
    n_years    = confidence.get("n_years", "?")
    state      = outlook["state"]
    target_yr  = outlook["target_year"]
    aod_display = fmt_aod(mean_aod) if mean_aod is not None else "—"

    # ── Secondary period ──────────────────────────────────────────────────────
    sec_lbl = outlook.get("secondary_season_label")
    secondary_html = (
        f'<div style="display:inline-flex;align-items:center;gap:8px;'
        f'margin-top:12px;padding:6px 12px;border-radius:8px;'
        f'background:#F6F4EE;border:1px solid #E4E1D6;">'
        f'<span style="font-size:10px;font-weight:700;letter-spacing:0.8px;text-transform:uppercase;color:#8FA688;">Secondary period</span>'
        f'<span style="font-size:13px;font-weight:600;color:#1E2A1C;">{sec_lbl}</span>'
        f'</div>'
    ) if sec_lbl else ""

    # ── Hero outlook card ─────────────────────────────────────────────────────
    st.markdown(
        f'<div class="hc-card" style="border-left:4px solid #4C6B45;">'
        f'<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:16px;">'
        f'<div>'
        f'<div style="font-size:10px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:#8FA688;margin-bottom:6px;">HISTORICAL PATTERN &middot; {str(state).upper()}</div>'
        f'<div style="font-family:Fraunces,Georgia,serif;font-size:28px;font-weight:600;color:#1E2A1C;line-height:1.1;margin-bottom:4px;">{season_lbl}</div>'
        f'<div style="font-size:13px;color:#5C6858;">Predicted high-risk period &middot; {n_years}-year AOD record &middot; Target {target_yr}</div>'
        f'</div>'
        f'<span class="hc-risk-badge {risk_css}">{risk_level}</span>'
        f'</div>'
        f'{secondary_html}'
        f'<div class="hc-divider"></div>'
        f'<div style="display:flex;flex-wrap:wrap;gap:24px;">'
        f'<div><div style="font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#8FA688;margin-bottom:3px;">PEAK MONTH</div>'
        f'<div style="font-size:15px;font-weight:700;color:#1E2A1C;">{peak_month}</div></div>'
        f'<div><div style="font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#8FA688;margin-bottom:3px;">PATTERN CONFIDENCE</div>'
        f'<div style="font-size:15px;font-weight:700;color:#1E2A1C;">{conf_pct}% &middot; {conf_lbl}</div></div>'
        f'<div><div style="font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#8FA688;margin-bottom:3px;">PEAK AOD</div>'
        f'<div style="font-size:15px;font-weight:700;color:#1E2A1C;">{aod_display}</div></div>'
        f'<div><div style="font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#8FA688;margin-bottom:3px;">DATA SOURCE</div>'
        f'<div style="font-size:15px;font-weight:700;color:#1E2A1C;">NASA MODIS AOD</div></div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Four metric cards ─────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    conf_colour = "green" if conf_lbl == "High" else ("orange" if conf_lbl == "Medium" else "red")

    with c1:
        st.markdown(
            f'<div class="hc-card" style="text-align:center;padding:20px 14px;">'
            f'<div class="hc-stat-label" style="text-align:center;margin-bottom:8px;">RISK LEVEL</div>'
            f'<div class="hc-stat-value {_risk_colour(risk_level)}" style="font-size:17px;">{risk_level}</div>'
            f'<div style="font-size:11px;color:#8FA688;margin-top:5px;">{season_lbl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="hc-card" style="text-align:center;padding:20px 14px;">'
            f'<div class="hc-stat-label" style="text-align:center;margin-bottom:8px;">PEAK MONTH</div>'
            f'<div class="hc-stat-value" style="font-size:17px;">{peak_month}</div>'
            f'<div style="font-size:11px;color:#8FA688;margin-top:5px;">Highest recurring AOD</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="hc-card" style="text-align:center;padding:20px 14px;">'
            f'<div class="hc-stat-label" style="text-align:center;margin-bottom:8px;">HISTORICAL AOD</div>'
            f'<div class="hc-stat-value green" style="font-size:20px;">{aod_display}</div>'
            f'<div style="font-size:11px;color:#8FA688;margin-top:5px;">Multi-year peak-month mean</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="hc-card" style="text-align:center;padding:20px 14px;">'
            f'<div class="hc-stat-label" style="text-align:center;margin-bottom:8px;">CONFIDENCE</div>'
            f'<div class="hc-stat-value {conf_colour}" style="font-size:20px;">{conf_pct}%</div>'
            f'<div style="font-size:11px;color:#8FA688;margin-top:5px;">{conf_lbl} pattern consistency</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Preparedness preview ──────────────────────────────────────────────────
    recommendations = preparedness_result.get("recommendations", [])
    if recommendations:
        st.markdown('<div class="hc-section-label">🌱 &nbsp;Pre-Season Preparedness</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(recommendations[:4]), 2))
        for i, rec in enumerate(recommendations[:4]):
            priority_css = f"priority-{rec['priority'].lower()}"
            with cols[i % 2]:
                st.markdown(
                    f'<div class="hc-action-card">'
                    f'<div class="hc-action-priority {priority_css}">{rec["priority"].upper()} PRIORITY</div>'
                    f'<div class="hc-action-title">{rec.get("icon", "")} {rec["title"]}</div>'
                    f'<div class="hc-action-why">{rec["why"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="hc-disclaimer">This is a historical seasonal outlook based on recurring satellite-observed aerosol patterns. It does not guarantee the timing, location, or severity of a future haze event and should not be treated as a real-time atmospheric forecast.</div>',
        unsafe_allow_html=True,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _risk_colour(risk_level: str) -> str:
    mapping = {
        "Low":       "green",
        "Moderate":  "orange",
        "High":      "red",
        "Very High": "purple",
    }
    return mapping.get(risk_level, "orange")
