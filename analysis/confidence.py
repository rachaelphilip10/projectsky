"""
HazeCrop Malaysia — Confidence Calculator.

Computes a statistically grounded confidence score from the
quality and consistency of the historical AOD record.

No fake or hardcoded confidence values.

Public API
----------
  calculate_prediction_confidence(historical_df, monthly_stats, haze_season)
    → dict with keys: confidence_pct, confidence_label, explanation, factors
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import (
    MIN_YEARS_HIGH_CONFIDENCE,
    MIN_YEARS_MEDIUM_CONFIDENCE,
    CONSISTENCY_HIGH_THRESHOLD,
    CONSISTENCY_MEDIUM_THRESHOLD,
)


def calculate_prediction_confidence(historical_df: pd.DataFrame,
                                    monthly_stats: pd.DataFrame,
                                    haze_season: dict) -> dict:
    """
    Calculate a data-driven confidence score for the seasonal outlook.

    Four components contribute equally:
      1. Year coverage  (how many years of data)
      2. Data completeness  (fraction of months with valid AOD)
      3. Peak-month consistency  (same peak month appearing across years)
      4. Pattern stability  (low coefficient of variation in high-risk months)

    Returns
    -------
    dict:
      confidence_pct   : int   (0–100)
      confidence_label : str   ("Low" | "Medium" | "High")
      explanation      : str
      factors          : list[str]
    """
    factors: list[str] = []

    # ── 1. Year coverage ─────────────────────────────────────────────────────
    n_years = int(historical_df["Year"].nunique())
    if n_years >= MIN_YEARS_HIGH_CONFIDENCE:
        year_score = 1.0
        factors.append(f"{n_years} years of historical data available — strong coverage.")
    elif n_years >= MIN_YEARS_MEDIUM_CONFIDENCE:
        year_score = 0.6
        factors.append(f"{n_years} years of historical data — moderate coverage.")
    else:
        year_score = 0.2
        factors.append(f"Only {n_years} year(s) of data — limited historical record.")

    # ── 2. Data completeness ─────────────────────────────────────────────────
    total_expected = n_years * 12
    valid_obs = int(historical_df["Mean_AOD"].notna().sum())
    completeness = valid_obs / total_expected if total_expected > 0 else 0.0
    completeness_score = min(completeness, 1.0)
    factors.append(
        f"{valid_obs}/{total_expected} monthly observations valid "
        f"({completeness * 100:.0f}% completeness)."
    )

    # ── 3. Peak-month consistency ─────────────────────────────────────────────
    peak_month = haze_season["peak_month"]
    # For each year, find its peak (highest Mean_AOD) month
    year_peaks = (
        historical_df.dropna(subset=["Mean_AOD"])
        .groupby("Year")
        .apply(lambda g: int(g.loc[g["Mean_AOD"].idxmax(), "Month"]))
    )
    if len(year_peaks) > 0:
        agreement = float((year_peaks == peak_month).mean())
    else:
        agreement = 0.0

    if agreement >= CONSISTENCY_HIGH_THRESHOLD:
        consistency_score = 1.0
        factors.append(
            f"Peak month ({pd.Timestamp(2000, peak_month, 1).strftime('%B')}) "
            f"is consistent across {agreement * 100:.0f}% of years."
        )
    elif agreement >= CONSISTENCY_MEDIUM_THRESHOLD:
        consistency_score = 0.55
        factors.append(
            f"Peak month is moderately consistent ({agreement * 100:.0f}% of years)."
        )
    else:
        consistency_score = 0.20
        factors.append(
            f"Peak-month timing varies across years ({agreement * 100:.0f}% agreement)."
        )

    # ── 4. Pattern stability (low CV in high-risk months) ────────────────────
    high_risk_months = haze_season["high_risk_months"]
    hr_data = historical_df[historical_df["Month"].isin(high_risk_months)]["Mean_AOD"].dropna()
    if len(hr_data) >= 3:
        cv = float(hr_data.std() / hr_data.mean()) if hr_data.mean() > 0 else 1.0
        stability_score = max(0.0, 1.0 - cv)
        factors.append(
            f"Coefficient of variation in high-risk months: {cv:.2f} "
            f"({'stable' if cv < 0.3 else 'moderate variability' if cv < 0.6 else 'high variability'})."
        )
    else:
        stability_score = 0.3
        factors.append("Insufficient high-risk month observations to assess stability.")

    # ── Combine ───────────────────────────────────────────────────────────────
    raw_score = (year_score + completeness_score + consistency_score + stability_score) / 4.0
    confidence_pct = int(round(raw_score * 100))

    if confidence_pct >= 65:
        confidence_label = "High"
        explanation = (
            f"Consistent seasonal pattern observed across {n_years} years. "
            "The historical record supports a reliable seasonal outlook."
        )
    elif confidence_pct >= 40:
        confidence_label = "Medium"
        explanation = (
            "Some recurring patterns observed, but peak timing or AOD magnitude "
            "varies between years. Use this outlook as an indicative guide."
        )
    else:
        confidence_label = "Low"
        explanation = (
            "The historical record is short or inconsistent. "
            "This outlook should be interpreted with caution."
        )

    return {
        "confidence_pct":   confidence_pct,
        "confidence_label": confidence_label,
        "explanation":      explanation,
        "factors":          factors,
        "n_years":          n_years,
        "valid_obs":        valid_obs,
        "completeness":     completeness,
        "peak_agreement":   agreement,
    }
