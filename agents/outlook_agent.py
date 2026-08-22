"""
HazeCrop Malaysia — Agent 3: Outlook Agent

Responsibility:
  • Convert pattern analysis into a seasonal risk outlook
  • Calculate pattern confidence
  • Explain uncertainty
  • Return a structured outlook payload

Public API
----------
  run_outlook_agent(data_result, pattern_result, state, target_year) → dict
"""

from __future__ import annotations

import pandas as pd

from analysis.confidence import calculate_prediction_confidence
from analysis.seasonal_prediction import generate_haze_outlook, generate_preparation_timeline


def run_outlook_agent(data_result: dict,
                      pattern_result: dict,
                      state: str,
                      target_year: int) -> dict:
    """
    Generate the full seasonal haze outlook from pattern analysis outputs.

    Parameters
    ----------
    data_result    : output of agents/data_analyst.run_data_analyst()
    pattern_result : output of agents/pattern_analyst.run_pattern_analyst()
    state          : display name of the state
    target_year    : the year for which the outlook applies

    Returns
    -------
    dict with keys:
      status              : "ok" | "warn" | "error"
      message             : str
      outlook             : dict  (from generate_haze_outlook)
      confidence          : dict  (from calculate_prediction_confidence)
      timeline            : list[dict]  (preparation phases)
      ai_input_summary    : dict  (structured input for the AI layer)
    """
    if pattern_result["status"] == "error":
        return _error_result("Outlook generation skipped — pattern analysis failed.")

    historical_df = data_result["historical_df"]
    monthly_stats = pattern_result["monthly_stats"]
    scored_df     = pattern_result["scored_df"]
    haze_season   = pattern_result["haze_season"]

    # ── Confidence calculation ────────────────────────────────────────────────
    confidence = calculate_prediction_confidence(historical_df, monthly_stats, haze_season)

    # ── Seasonal outlook ──────────────────────────────────────────────────────
    outlook = generate_haze_outlook(
        scored_df, haze_season, confidence, state, target_year
    )

    # ── Preparation timeline ──────────────────────────────────────────────────
    timeline = generate_preparation_timeline(haze_season, target_year)

    # ── Structured summary for the AI insights layer ─────────────────────────
    # This is what gets passed to Agent 4 and the AI insights UI.
    # It contains only deterministic statistics — no invented values.
    ai_input_summary = {
        "location":            state,
        "target_year":         target_year,
        "historical_years":    data_result["n_years"],
        "peak_month":          haze_season["peak_month_name"],
        "high_risk_months":    haze_season["high_risk_month_names"],
        "primary_season":      outlook["primary_season_label"],
        "secondary_season":    outlook["secondary_season_label"],
        "mean_peak_aod":       round(outlook["mean_peak_aod"], 3)
                               if outlook["mean_peak_aod"] is not None else None,
        "overall_mean_aod":    round(outlook["overall_mean_aod"], 3),
        "pattern_consistency": round(pattern_result["peak_month_agreement"], 2),
        "recent_trend":        outlook["recent_trend"],
        "confidence":          confidence["confidence_pct"],
        "confidence_label":    confidence["confidence_label"],
        "risk_level":          outlook["risk_level"],
        "valid_obs":           data_result["valid_obs"],
        "completeness_pct":    round(data_result["completeness"] * 100, 0),
    }

    status = "ok" if data_result["status"] == "ok" and pattern_result["status"] == "ok" else "warn"

    return {
        "status":           status,
        "message":          outlook["outlook_summary"],
        "outlook":          outlook,
        "confidence":       confidence,
        "timeline":         timeline,
        "ai_input_summary": ai_input_summary,
    }


def _error_result(message: str) -> dict:
    return {
        "status":           "error",
        "message":          message,
        "outlook":          {},
        "confidence":       {"confidence_pct": 0, "confidence_label": "Low",
                             "explanation": message, "factors": []},
        "timeline":         [],
        "ai_input_summary": {},
    }
