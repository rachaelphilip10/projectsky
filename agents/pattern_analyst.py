"""
HazeCrop Malaysia — Agent 2: Pattern Analyst

Responsibility:
  • Compare AOD patterns across years
  • Identify recurring peak months
  • Detect seasonal windows
  • Evaluate inter-annual consistency
  • Return a structured pattern analysis payload

Public API
----------
  run_pattern_analyst(data_result) → dict
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from analysis.pattern_detection import (
    build_monthly_stats,
    calculate_seasonal_scores,
    detect_haze_season,
)


def run_pattern_analyst(data_result: dict) -> dict:
    """
    Analyse the historical AOD data to identify recurring seasonal patterns.

    Parameters
    ----------
    data_result : dict
        Output from agents/data_analyst.run_data_analyst()

    Returns
    -------
    dict with keys:
      status         : "ok" | "warn" | "error"
      message        : str
      monthly_stats  : pd.DataFrame   (per-month statistics)
      scored_df      : pd.DataFrame   (monthly stats + seasonal risk scores)
      haze_season    : dict           (from detect_haze_season)
      yearly_pivot   : pd.DataFrame   (year × month AOD pivot for charting)
    """
    if data_result["status"] == "error":
        return _error_result(
            "Pattern analysis skipped — data retrieval failed.",
            data_result
        )

    historical_df = data_result["historical_df"]

    if historical_df.empty or data_result["valid_obs"] == 0:
        return _error_result("No valid AOD data to analyse.", data_result)

    # ── Monthly statistics ────────────────────────────────────────────────────
    monthly_stats = build_monthly_stats(historical_df)

    # ── Seasonal risk scores ──────────────────────────────────────────────────
    scored_df = calculate_seasonal_scores(monthly_stats)

    # ── Haze season detection ─────────────────────────────────────────────────
    haze_season = detect_haze_season(scored_df)

    # ── Year × Month pivot (for per-year chart) ───────────────────────────────
    try:
        yearly_pivot = historical_df.pivot_table(
            index="Year", columns="Month", values="Mean_AOD", aggfunc="mean"
        )
    except Exception:
        yearly_pivot = pd.DataFrame()

    # ── Consistency summary ───────────────────────────────────────────────────
    # For each year, identify its peak month
    year_peaks = (
        historical_df.dropna(subset=["Mean_AOD"])
        .groupby("Year")
        .apply(lambda g: int(g.loc[g["Mean_AOD"].idxmax(), "Month"]))
    )
    peak_month          = haze_season["peak_month"]
    peak_month_agreement = float((year_peaks == peak_month).mean()) if len(year_peaks) > 0 else 0.0

    # Recurring pattern description
    n_years       = data_result["n_years"]
    high_risk_names = haze_season["high_risk_month_names"]
    pattern_summary = (
        f"Analysis of {n_years} years of MODIS AOD data shows recurring elevated "
        f"aerosol loading in {', '.join(high_risk_names)}. "
        f"The peak month ({haze_season['peak_month_name']}) appears consistently "
        f"across {peak_month_agreement * 100:.0f}% of observed years."
    )

    status = "ok" if data_result["status"] == "ok" else "warn"

    return {
        "status":               status,
        "message":              pattern_summary,
        "monthly_stats":        monthly_stats,
        "scored_df":            scored_df,
        "haze_season":          haze_season,
        "yearly_pivot":         yearly_pivot,
        "peak_month_agreement": peak_month_agreement,
        "n_years":              n_years,
    }


def _error_result(message: str, data_result: dict) -> dict:
    empty = pd.DataFrame()
    return {
        "status":               "error",
        "message":              message,
        "monthly_stats":        empty,
        "scored_df":            empty,
        "haze_season":          {
            "primary":               {"start_month": 9, "end_month": 10,
                                      "start_name": "September", "end_name": "October",
                                      "months": [9, 10]},
            "secondary":             None,
            "peak_month":            10,
            "peak_month_name":       "October",
            "high_risk_months":      [9, 10],
            "high_risk_month_names": ["September", "October"],
        },
        "yearly_pivot":         empty,
        "peak_month_agreement": 0.0,
        "n_years":              data_result.get("n_years", 0),
    }
