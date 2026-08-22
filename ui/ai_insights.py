"""
HazeCrop Malaysia — UI: AI Insights Tab

Renders the AI Insights section including:
  • Pattern interpretation
  • Why this matters
  • Preparedness plan with timeline
  • Data transparency expander
  • CSV export

The AI layer receives only pre-computed deterministic statistics —
it never invents satellite values.

Public API
----------
  render_ai_insights_idle()
  render_ai_insights_results(outlook_result, preparedness_result,
                              data_result, pattern_result)
"""

from __future__ import annotations

import io
import json

import pandas as pd
import streamlit as st

from utils.formatters import fmt_aod, risk_css_class
from config.settings import EXPORT_COLUMNS, MONTH_FULL_NAMES


def render_ai_insights_idle() -> None:
    st.markdown('<div id="ai-insights"></div>', unsafe_allow_html=True)
    st.markdown('<div class="hc-section-label">🧠 &nbsp;AI Seasonal Insight</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hc-card" style="text-align:center;padding:40px 28px;">
        <div style="font-size:32px;margin-bottom:14px;">🧠</div>
        <div class="hc-card-title" style="font-size:17px;margin-bottom:10px;">AI Seasonal Insight</div>
        <div class="hc-card-body" style="max-width:440px;margin:0 auto;">
            Run an analysis to receive an AI-generated interpretation of the
            seasonal pattern, along with a pre-haze preparedness plan.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_ai_insights_results(outlook_result: dict,
                                preparedness_result: dict,
                                data_result: dict,
                                pattern_result: dict) -> None:
    """Render the full AI Insights section."""
    st.markdown('<div id="ai-insights"></div>', unsafe_allow_html=True)
    st.markdown('<div class="hc-section-label">🧠 &nbsp;AI Seasonal Insight</div>', unsafe_allow_html=True)

    ai_summary = outlook_result["ai_input_summary"]
    outlook    = outlook_result["outlook"]
    confidence = outlook_result["confidence"]

    # ── Pattern interpretation ────────────────────────────────────────────────
    interpretation = _generate_pattern_interpretation(ai_summary)
    why_matters    = _generate_why_it_matters(ai_summary)

    st.markdown(f"""
    <div class="hc-card">
        <div class="hc-card-header">
            <div class="hc-card-icon icon-ai">🧠</div>
            <div>
                <div class="hc-card-title">AI SEASONAL INSIGHT</div>
                <div class="hc-card-meta">
                    Based on {ai_summary.get('historical_years', '?')}-year MODIS AOD record ·
                    Confidence: {ai_summary.get('confidence', '?')}%
                </div>
            </div>
        </div>
        <div class="hc-ai-box">
            <div class="hc-ai-box-label">📡 Pattern Interpretation</div>
            <div class="hc-ai-box-text">{interpretation}</div>
        </div>
        <div class="hc-ai-box">
            <div class="hc-ai-box-label">🌾 Why This Matters</div>
            <div class="hc-ai-box-text">{why_matters}</div>
        </div>
        <div class="hc-disclaimer">
            This is a seasonal outlook based on historical patterns and does not
            guarantee a future haze event. Satellite data quality and coverage
            affect confidence. Always combine this outlook with local knowledge
            and official meteorological advisories.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Confidence factors ────────────────────────────────────────────────────
    with st.expander("📊 Pattern confidence details"):
        st.markdown(f"""
        <div style="padding:8px 0;">
            <span class="hc-risk-badge {'risk-low' if confidence['confidence_label']=='High' else 'risk-moderate' if confidence['confidence_label']=='Medium' else 'risk-high'}">
                {confidence['confidence_label']} Confidence — {confidence['confidence_pct']}%
            </span>
        </div>
        <div style="font-size:14px;color:rgba(255,255,255,0.65);margin:12px 0 8px;line-height:1.7;">
            {confidence['explanation']}
        </div>
        """, unsafe_allow_html=True)
        for factor in confidence.get("factors", []):
            st.markdown(
                f'<div style="font-size:13px;color:rgba(255,255,255,0.45);'
                f'padding:4px 0 4px 14px;border-left:2px solid rgba(74,222,128,0.3);">'
                f'• {factor}</div>',
                unsafe_allow_html=True,
            )

    # ── Preparedness plan ─────────────────────────────────────────────────────
    st.markdown('<div class="hc-section-label">🌱 &nbsp;Pre-Haze Season Preparation Plan</div>', unsafe_allow_html=True)

    primary_label = outlook.get("primary_season_label", "the predicted period")
    st.markdown(f"""
    <div class="hc-card" style="border-color:rgba(74,222,128,0.15);background:rgba(74,222,128,0.02);">
        <div class="hc-card-header">
            <div class="hc-card-icon icon-plan">🌱</div>
            <div>
                <div class="hc-card-title">PRE-HAZE SEASON PREPARATION PLAN</div>
                <div class="hc-card-meta">
                    Predicted high-risk window: {primary_label} ·
                    Start planning several months before the predicted period
                </div>
            </div>
        </div>
        <div class="hc-divider"></div>
        <div style="font-size:13px;color:rgba(255,255,255,0.45);font-style:italic;margin-bottom:16px;">
            These recommendations are for long-term pre-season planning only.
            They are not an emergency response guide.
        </div>
    """, unsafe_allow_html=True)

    recommendations = preparedness_result.get("recommendations", [])
    for rec in recommendations:
        priority_css = f"priority-{rec['priority'].lower()}"
        st.markdown(f"""
        <div class="hc-action-card">
            <div class="hc-action-priority {priority_css}">{rec['priority'].upper()} PRIORITY</div>
            <div class="hc-action-title">{rec['icon']} {rec['title']}</div>
            <div class="hc-action-why" style="margin-bottom:8px;">{rec['detail']}</div>
            <div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:8px;">
                <div style="font-size:11px;color:rgba(255,255,255,0.4);">
                    <span style="color:#22d3ee;font-weight:700;">WHEN:</span> {rec['when']}
                </div>
                <div style="font-size:11px;color:rgba(255,255,255,0.4);">
                    <span style="color:#4ade80;font-weight:700;">WHY:</span> {rec['why']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Preparation timeline ──────────────────────────────────────────────────
    st.markdown('<div class="hc-section-label">🗓 &nbsp;Preparation Timeline</div>', unsafe_allow_html=True)

    timeline = preparedness_result.get("timeline", [])
    if timeline:
        st.markdown('<div class="hc-card">', unsafe_allow_html=True)
        for phase in timeline:
            items_html = "".join(f"<div>• {item}</div>" for item in phase["items"])
            st.markdown(f"""
            <div class="hc-timeline-phase">
                <div class="hc-timeline-phase-title">{phase['phase']}</div>
                <div class="hc-timeline-phase-months">{phase['months']}</div>
                <div class="hc-timeline-phase-items">{items_html}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Data Transparency expander ────────────────────────────────────────────
    _render_data_transparency(data_result, pattern_result, outlook_result)

    # ── CSV / Report download ─────────────────────────────────────────────────
    _render_downloads(data_result, pattern_result, outlook_result, preparedness_result)


# ─── AI text generators (deterministic, based on structured data) ─────────────

def _generate_pattern_interpretation(ai_summary: dict) -> str:
    location      = ai_summary.get("location", "the selected region")
    n_years       = ai_summary.get("historical_years", "?")
    peak_month    = ai_summary.get("peak_month", "?")
    high_months   = ai_summary.get("high_risk_months", [])
    primary       = ai_summary.get("primary_season", "?")
    mean_aod      = ai_summary.get("mean_peak_aod")
    consistency   = ai_summary.get("pattern_consistency", 0)
    trend         = ai_summary.get("recent_trend", "stable")

    months_str    = ", ".join(high_months) if high_months else primary
    aod_str       = f" (mean AOD: {mean_aod:.3f})" if mean_aod else ""
    consist_str   = f"{consistency * 100:.0f}%"
    trend_str     = {
        "increasing": "an upward trend in peak-period aerosol loading",
        "decreasing": "a declining trend in aerosol loading in recent years",
        "stable":     "stable inter-annual aerosol levels across the historical record",
    }.get(trend, "stable aerosol levels")

    return (
        f"Historical satellite observations for {location} show a recurring increase "
        f"in atmospheric aerosol optical depth (AOD) during {months_str}. "
        f"{peak_month} is the most consistently elevated month across the "
        f"{n_years}-year observation period, appearing as the peak in "
        f"{consist_str} of analysed years{aod_str}. "
        f"The data indicate {trend_str}."
    )


def _generate_why_it_matters(ai_summary: dict) -> str:
    primary   = ai_summary.get("primary_season", "the predicted window")
    risk_level = ai_summary.get("risk_level", "Moderate")
    conf_lbl  = ai_summary.get("confidence_label", "Medium")

    return (
        f"This recurring pattern — with {conf_lbl.lower()} confidence — suggests that "
        f"farmers operating in the affected area should use the months before {primary} "
        f"to review crop preparedness measures. "
        f"The outlook is classified as <strong>{risk_level}</strong> based on historical "
        f"aerosol levels. "
        f"Pre-season preparation — including monitoring, spacing reviews, and leaf-management "
        f"strategies — can reduce the impact of prolonged aerosol loading on crop performance. "
        f"Decisions should also take into account local weather conditions, crop type, "
        f"and current farm situation."
    )


# ─── Data transparency ────────────────────────────────────────────────────────

def _render_data_transparency(data_result: dict,
                               pattern_result: dict,
                               outlook_result: dict) -> None:
    with st.expander("🔬 View Satellite Analysis Details"):
        ai_summary = outlook_result["ai_input_summary"]
        st.markdown(f"""
        <div style="font-size:13px;color:rgba(255,255,255,0.55);line-height:2;">
            <strong style="color:#ffffff;">Dataset:</strong> MODIS/061/MCD19A2_GRANULES (NASA MODIS MAIAC)<br>
            <strong style="color:#ffffff;">AOD Band:</strong> Optical_Depth_055 (~0.55 µm)<br>
            <strong style="color:#ffffff;">State:</strong> {ai_summary.get('location', '—')}<br>
            <strong style="color:#ffffff;">Analysis period:</strong>
                {data_result.get('start_year', '—')} – {data_result.get('end_year', '—')}<br>
            <strong style="color:#ffffff;">Years analysed:</strong> {data_result.get('n_years', '—')}<br>
            <strong style="color:#ffffff;">Valid observations:</strong>
                {data_result.get('valid_obs', '—')} / {data_result.get('total_expected', '—')}
                ({ai_summary.get('completeness_pct', 0):.0f}% completeness)<br>
            <strong style="color:#ffffff;">Pattern confidence:</strong>
                {ai_summary.get('confidence', '—')}% ({ai_summary.get('confidence_label', '—')})<br>
            <strong style="color:#ffffff;">Peak-month agreement:</strong>
                {ai_summary.get('pattern_consistency', 0) * 100:.0f}% of years<br>
        </div>
        """, unsafe_allow_html=True)

        scored_df = pattern_result.get("scored_df")
        if scored_df is not None and not scored_df.empty:
            st.markdown(
                '<div style="font-size:12px;font-weight:700;color:rgba(255,255,255,0.4);'
                'margin:16px 0 8px;letter-spacing:0.8px;text-transform:uppercase;">'
                'Monthly Seasonal Scores</div>',
                unsafe_allow_html=True,
            )
            display_cols = ["Month_Name", "Mean_AOD", "Max_AOD", "Std_AOD",
                            "Seasonal_Risk_Score", "Risk_Category"]
            display_cols = [c for c in display_cols if c in scored_df.columns]
            st.dataframe(
                scored_df[display_cols].rename(columns={"Month_Name": "Month"}),
                use_container_width=True,
                hide_index=True,
            )


# ─── Downloads ────────────────────────────────────────────────────────────────

def _render_downloads(data_result: dict,
                      pattern_result: dict,
                      outlook_result: dict,
                      preparedness_result: dict) -> None:
    st.markdown('<div class="hc-section-label">📥 &nbsp;Export</div>', unsafe_allow_html=True)

    dc1, dc2 = st.columns(2)

    # ── CSV: monthly AOD data ─────────────────────────────────────────────────
    with dc1:
        historical_df = data_result.get("historical_df", pd.DataFrame())
        scored_df     = pattern_result.get("scored_df", pd.DataFrame())

        if not historical_df.empty and not scored_df.empty:
            export_df = historical_df.merge(
                scored_df[["Month", "Seasonal_Risk_Score", "Risk_Category"]],
                on="Month", how="left",
            )
            # Ensure AOD_Anomaly column exists
            if "AOD_Anomaly" not in export_df.columns:
                export_df["AOD_Anomaly"] = None
            for col in EXPORT_COLUMNS:
                if col not in export_df.columns:
                    export_df[col] = None
            csv_bytes = export_df[
                [c for c in EXPORT_COLUMNS if c in export_df.columns]
            ].to_csv(index=False).encode("utf-8")

            state_slug = (
                outlook_result["ai_input_summary"].get("location", "malaysia")
                .lower().replace(" ", "_")
            )
            st.download_button(
                label="⬇ Download Monthly AOD Data (CSV)",
                data=csv_bytes,
                file_name=f"hazecrop_{state_slug}_aod_data.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.button("⬇ Download Monthly AOD Data (CSV)", disabled=True, use_container_width=True)

    # ── TXT: seasonal outlook report ──────────────────────────────────────────
    with dc2:
        report_text = _build_report_text(outlook_result, preparedness_result, data_result)
        state_slug  = (
            outlook_result["ai_input_summary"].get("location", "malaysia")
            .lower().replace(" ", "_")
        )
        st.download_button(
            label="⬇ Download Seasonal Outlook Report",
            data=report_text.encode("utf-8"),
            file_name=f"hazecrop_{state_slug}_outlook_report.txt",
            mime="text/plain",
            use_container_width=True,
        )


def _build_report_text(outlook_result: dict,
                       preparedness_result: dict,
                       data_result: dict) -> str:
    ai_summary = outlook_result["ai_input_summary"]
    outlook    = outlook_result["outlook"]
    confidence = outlook_result["confidence"]
    timeline   = preparedness_result.get("timeline", [])
    recs       = preparedness_result.get("recommendations", [])
    disclaimer = preparedness_result.get("disclaimer", "")

    lines = [
        "=" * 60,
        "  HAZECROP MALAYSIA — SEASONAL HAZE OUTLOOK REPORT",
        "=" * 60,
        "",
        f"Location        : {ai_summary.get('location', '—')}",
        f"Target Year     : {ai_summary.get('target_year', '—')}",
        f"Analysis Period : {data_result.get('start_year', '—')} – {data_result.get('end_year', '—')}",
        f"Years Analysed  : {ai_summary.get('historical_years', '—')}",
        f"Valid Obs       : {data_result.get('valid_obs', '—')} / {data_result.get('total_expected', '—')}",
        "",
        "── SEASONAL HAZE OUTLOOK ──────────────────────────────",
        f"Predicted high-risk period : {outlook.get('primary_season_label', '—')}",
        (f"Secondary elevated period  : {outlook.get('secondary_season_label')}"
         if outlook.get("secondary_season_label") else ""),
        f"Peak month                 : {outlook.get('peak_month_name', '—')}",
        f"Risk level                 : {outlook.get('risk_level', '—')}",
        f"AOD trend                  : {outlook.get('recent_trend', '—')}",
        f"Pattern confidence         : {confidence.get('confidence_pct', '—')}% ({confidence.get('confidence_label', '—')})",
        "",
        "── PATTERN INTERPRETATION ─────────────────────────────",
        outlook.get("outlook_summary", ""),
        "",
        "── CONFIDENCE ─────────────────────────────────────────",
        confidence.get("explanation", ""),
    ]
    for f in confidence.get("factors", []):
        lines.append(f"  • {f}")

    lines += ["", "── PREPARATION TIMELINE ───────────────────────────────"]
    for phase in timeline:
        lines.append(f"\n{phase['phase']}  ({phase['months']})")
        for item in phase["items"]:
            lines.append(f"  • {item}")

    lines += ["", "── RECOMMENDATIONS ────────────────────────────────────"]
    for rec in recs:
        lines.append(f"\n{rec['icon']} {rec['title']}  [{rec['priority']} PRIORITY]")
        lines.append(f"When : {rec['when']}")
        lines.append(f"Why  : {rec['why']}")
        lines.append(rec["detail"])

    lines += [
        "",
        "── DISCLAIMER ─────────────────────────────────────────",
        disclaimer,
        "",
        "Generated by HazeCrop Malaysia · NASA MODIS MAIAC AOD Analysis",
        "=" * 60,
    ]
    return "\n".join(line for line in lines if line is not None)
