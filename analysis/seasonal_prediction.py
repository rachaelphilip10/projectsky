"""
HazeCrop Malaysia — Seasonal Prediction module.

Converts pattern detection outputs into a structured seasonal haze
outlook including a human-readable description and timeline.

Public API
----------
  generate_haze_outlook(scored_df, haze_season, confidence_result,
                        state_name, target_year) → dict
  generate_preparation_timeline(haze_season, target_year) → list[dict]
"""

from __future__ import annotations

import pandas as pd
from config.settings import MONTH_FULL_NAMES, MONTH_LABELS


def generate_haze_outlook(scored_df: pd.DataFrame,
                          haze_season: dict,
                          confidence_result: dict,
                          state_name: str,
                          target_year: int) -> dict:
    """
    Build a complete seasonal haze outlook dict.

    Returns
    -------
    dict with keys:
      state, target_year,
      primary_season_label, secondary_season_label,
      peak_month_name, high_risk_month_names,
      mean_peak_aod, overall_mean_aod,
      risk_level,           # "Low" | "Moderate" | "High" | "Very High"
      confidence_pct,       # int 0–100
      confidence_label,     # "Low" | "Medium" | "High"
      recent_trend,         # "increasing" | "stable" | "decreasing"
      outlook_summary,      # plain-English sentence
      scored_df             # full month-level DataFrame
    """
    primary   = haze_season["primary"]
    secondary = haze_season.get("secondary")
    peak_m    = haze_season["peak_month"]

    # Primary season label
    if primary["start_month"] == primary["end_month"]:
        primary_label = primary["start_name"]
    else:
        primary_label = f"{primary['start_name']} – {primary['end_name']}"

    secondary_label = None
    if secondary:
        if secondary["start_month"] == secondary["end_month"]:
            secondary_label = secondary["start_name"]
        else:
            secondary_label = f"{secondary['start_name']} – {secondary['end_name']}"

    # Peak-month AOD stats
    peak_row      = scored_df[scored_df["Month"] == peak_m]
    mean_peak_aod = float(peak_row["Mean_AOD"].iloc[0]) if not peak_row.empty else None
    overall_mean  = float(scored_df["Mean_AOD"].dropna().mean())

    # Overall risk level: based on peak-month Risk_Category
    if not peak_row.empty:
        risk_level = str(peak_row["Risk_Category"].iloc[0])
    else:
        risk_level = "Moderate"

    # Trend direction from slope of peak month
    trend_slope = float(peak_row["Trend_Slope"].iloc[0]) if not peak_row.empty else 0.0
    if trend_slope > 0.005:
        recent_trend = "increasing"
    elif trend_slope < -0.005:
        recent_trend = "decreasing"
    else:
        recent_trend = "stable"

    # Outlook sentence
    months_str = ", ".join(haze_season["high_risk_month_names"])
    outlook_summary = (
        f"Historical satellite data for {state_name} shows recurring elevated aerosol "
        f"loading during {primary_label}. "
        f"The peak month is {haze_season['peak_month_name']}. "
        f"AOD levels are {recent_trend} over the observed period. "
        f"The predicted high-risk window for {target_year} is "
        f"{primary_label}"
        + (f" with a secondary period in {secondary_label}" if secondary_label else "")
        + "."
    )

    return {
        "state":                 state_name,
        "target_year":           target_year,
        "primary_season_label":  primary_label,
        "secondary_season_label": secondary_label,
        "peak_month_name":       haze_season["peak_month_name"],
        "peak_month":            peak_m,
        "high_risk_months":      haze_season["high_risk_months"],
        "high_risk_month_names": haze_season["high_risk_month_names"],
        "mean_peak_aod":         mean_peak_aod,
        "overall_mean_aod":      overall_mean,
        "risk_level":            risk_level,
        "confidence_pct":        confidence_result["confidence_pct"],
        "confidence_label":      confidence_result["confidence_label"],
        "recent_trend":          recent_trend,
        "outlook_summary":       outlook_summary,
        "scored_df":             scored_df,
    }


def generate_preparation_timeline(haze_season: dict,
                                  target_year: int) -> list[dict]:
    """
    Generate a month-by-month preparation timeline that is dynamically
    derived from the predicted haze season.

    Returns a list of phase dicts:
    [
      {"phase": str, "months": str, "items": [str, ...]},
      ...
    ]
    """
    primary    = haze_season["primary"]
    season_start = primary["start_month"]
    season_end   = primary["end_month"]
    peak_month   = haze_season["peak_month"]

    # Compute preparation phases relative to season start
    plan_end      = season_start - 1 if season_start > 1 else 12
    plan_start    = max(1, season_start - 6)
    prep_start    = max(1, season_start - 3)
    prep_end      = season_start - 1 if season_start > 1 else 12
    pre_month     = season_start - 1 if season_start > 1 else 12

    def _month_range_label(start: int, end: int) -> str:
        if start > end:
            return f"{MONTH_LABELS[start-1]} – {MONTH_LABELS[end-1]}"
        if start == end:
            return MONTH_LABELS[start - 1]
        return f"{MONTH_LABELS[start-1]} – {MONTH_LABELS[end-1]}"

    planning_label  = _month_range_label(plan_start, prep_start - 1 if prep_start > 1 else 1)
    prep_label      = _month_range_label(prep_start, pre_month)
    pre_label       = MONTH_LABELS[pre_month - 1]
    season_label    = _month_range_label(season_start, season_end)

    return [
        {
            "phase":  "🗓 Planning Phase",
            "months": planning_label,
            "items": [
                "Review planting calendar for the upcoming cycle",
                "Assess row spacing and planting density for affected crops",
                "Evaluate supplemental lighting requirements for high-value protected crops",
                "Identify which crops are most exposed during the predicted haze window",
            ],
        },
        {
            "phase":  "🔧 Preparation Phase",
            "months": prep_label,
            "items": [
                "Install or test environmental monitoring equipment",
                "Review irrigation and leaf-management strategies",
                "Establish humidity and temperature baselines",
                "Train farm staff on haze-period protocols",
            ],
        },
        {
            "phase":  "✅ Pre-Season Readiness",
            "months": pre_label,
            "items": [
                "Confirm monitoring systems are operational",
                "Review condition of most vulnerable crops",
                "Prepare response procedures and contact lists",
                "Verify irrigation system functionality",
            ],
        },
        {
            "phase":  f"⚠ Predicted High-Risk Window",
            "months": season_label,
            "items": [
                "Monitor satellite aerosol data and local haze reports",
                "Track crop condition and NDVI indicators",
                "Monitor humidity and adjust irrigation as required",
                "Implement leaf-surface management where appropriate",
            ],
        },
    ]
