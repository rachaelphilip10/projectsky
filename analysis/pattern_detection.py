"""
HazeCrop Malaysia — Pattern Detection Engine.

This is the core analytical module.

For each month (1–12) it computes:
  1. Mean historical AOD
  2. Median historical AOD
  3. Maximum historical AOD
  4. Standard deviation
  5. High-frequency score (fraction of years where month is in top tercile)
  6. AOD anomaly relative to the overall multi-year monthly mean
  7. Long-term linear trend

Then it produces a normalised Seasonal Risk Score (0–100) using
the configurable weights in config/settings.py, and classifies each
month into Low / Moderate / High / Very High.

Public API
----------
  build_monthly_stats(historical_df)        → pd.DataFrame (12 rows)
  calculate_seasonal_scores(monthly_stats)  → pd.DataFrame
  classify_month_risk(score)                → str
  detect_haze_season(scored_df)             → dict
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

from config.settings import (
    WEIGHT_HISTORICAL_MEAN,
    WEIGHT_HIGH_FREQ,
    WEIGHT_RECENT_TREND,
    WEIGHT_CONSISTENCY,
    RISK_LOW_MAX,
    RISK_MODERATE_MAX,
    RISK_HIGH_MAX,
    HIGH_RISK_SCORE_THRESHOLD,
    MIN_SEASON_LENGTH,
    MONTH_FULL_NAMES,
)


# ─── Step 1: per-month statistics ────────────────────────────────────────────

def build_monthly_stats(historical_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-month statistics across all historical years.

    Parameters
    ----------
    historical_df : pd.DataFrame
        Columns required: Month (1–12), Year, Mean_AOD

    Returns
    -------
    pd.DataFrame  (12 rows, one per month)
        Month, Mean_AOD, Median_AOD, Max_AOD, Std_AOD,
        High_Freq, Trend_Slope, Obs_Count, Year_Count
    """
    df = historical_df.dropna(subset=["Mean_AOD"]).copy()
    if df.empty:
        # Return a skeleton with NaN values so downstream code never crashes.
        return pd.DataFrame({
            "Month":      range(1, 13),
            "Mean_AOD":   np.nan,
            "Median_AOD": np.nan,
            "Max_AOD":    np.nan,
            "Std_AOD":    np.nan,
            "High_Freq":  np.nan,
            "Trend_Slope": np.nan,
            "Obs_Count":  0,
            "Year_Count": 0,
        })

    # Mark high-AOD months: top tercile within each year
    df["Year_Tercile"] = df.groupby("Year")["Mean_AOD"].transform(
        lambda x: x >= x.quantile(0.67)
    )

    rows = []
    for month in range(1, 13):
        m = df[df["Month"] == month]
        if m.empty:
            rows.append({
                "Month":       month,
                "Mean_AOD":    np.nan,
                "Median_AOD":  np.nan,
                "Max_AOD":     np.nan,
                "Std_AOD":     np.nan,
                "High_Freq":   np.nan,
                "Trend_Slope": np.nan,
                "Obs_Count":   0,
                "Year_Count":  0,
            })
            continue

        mean_aod   = float(m["Mean_AOD"].mean())
        median_aod = float(m["Mean_AOD"].median())
        max_aod    = float(m["Mean_AOD"].max())
        std_aod    = float(m["Mean_AOD"].std(ddof=1)) if len(m) > 1 else 0.0
        high_freq  = float(m["Year_Tercile"].mean())  # fraction of years in top tercile
        obs_count  = int(m.shape[0])
        year_count = int(m["Year"].nunique())

        # Linear trend: slope of AOD ~ year
        if year_count >= 3:
            slope, _, _, _, _ = scipy_stats.linregress(m["Year"], m["Mean_AOD"])
            trend_slope = float(slope)
        else:
            trend_slope = 0.0

        rows.append({
            "Month":       month,
            "Mean_AOD":    mean_aod,
            "Median_AOD":  median_aod,
            "Max_AOD":     max_aod,
            "Std_AOD":     std_aod,
            "High_Freq":   high_freq,
            "Trend_Slope": trend_slope,
            "Obs_Count":   obs_count,
            "Year_Count":  year_count,
        })

    return pd.DataFrame(rows)


# ─── Step 2: Seasonal Risk Score ─────────────────────────────────────────────

def calculate_seasonal_scores(monthly_stats: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a 0–100 Seasonal Risk Score for each month.

    Formula (configurable weights in config/settings.py):
      Score = 40% * norm(Mean_AOD)
             + 25% * High_Freq
             + 20% * norm(positive Trend_Slope)
             + 15% * (1 - norm(Std_AOD))     # lower variance → more consistent

    Normalise each component to [0, 1] before applying weights.

    Returns the input DataFrame with added columns:
      Component_Mean, Component_Freq, Component_Trend, Component_Consistency,
      Seasonal_Risk_Score, Risk_Category, Month_Name
    """
    df = monthly_stats.copy()

    def _norm(series: pd.Series) -> pd.Series:
        """Min-max normalise, handling all-NaN or zero-range gracefully."""
        mn, mx = series.min(), series.max()
        if pd.isna(mn) or mn == mx:
            return series.fillna(0.0) * 0.0
        return (series - mn) / (mx - mn)

    df["Component_Mean"]  = _norm(df["Mean_AOD"].fillna(0))
    df["Component_Freq"]  = df["High_Freq"].fillna(0)
    # Trend: only positive slope contributes to risk
    df["Component_Trend"] = _norm(df["Trend_Slope"].clip(lower=0).fillna(0))
    # Consistency: lower Std_AOD means more consistent → higher component
    df["Component_Consistency"] = 1 - _norm(df["Std_AOD"].fillna(0))

    df["Seasonal_Risk_Score"] = (
        WEIGHT_HISTORICAL_MEAN   * df["Component_Mean"]
        + WEIGHT_HIGH_FREQ       * df["Component_Freq"]
        + WEIGHT_RECENT_TREND    * df["Component_Trend"]
        + WEIGHT_CONSISTENCY     * df["Component_Consistency"]
    ) * 100

    df["Risk_Category"] = df["Seasonal_Risk_Score"].apply(classify_month_risk)
    df["Month_Name"]    = df["Month"].apply(lambda m: MONTH_FULL_NAMES[m - 1])

    return df


# ─── Step 3: Risk classification ─────────────────────────────────────────────

def classify_month_risk(score: float) -> str:
    """Map a 0–100 score to a risk category label."""
    if pd.isna(score):
        return "Low"
    if score <= RISK_LOW_MAX:
        return "Low"
    if score <= RISK_MODERATE_MAX:
        return "Moderate"
    if score <= RISK_HIGH_MAX:
        return "High"
    return "Very High"


# ─── Step 4: Haze season detection ───────────────────────────────────────────

def detect_haze_season(scored_df: pd.DataFrame) -> dict:
    """
    Identify the primary (and optional secondary) haze season(s) from
    the monthly Seasonal Risk Score.

    Returns a dict:
    {
      "primary":   {"start_month": int, "end_month": int,
                    "start_name": str,  "end_name": str,
                    "months": [int, ...]},
      "secondary": {...} | None,
      "peak_month": int,
      "peak_month_name": str,
      "high_risk_months": [int, ...],
      "high_risk_month_names": [str, ...],
    }
    """
    df = scored_df.sort_values("Month").reset_index(drop=True)
    high_risk = df[df["Seasonal_Risk_Score"] >= HIGH_RISK_SCORE_THRESHOLD]
    high_months = sorted(high_risk["Month"].tolist())

    if not high_months:
        # Fallback: top 2 months by score
        top = df.nlargest(2, "Seasonal_Risk_Score")
        high_months = sorted(top["Month"].tolist())

    # Find consecutive runs
    seasons = _find_consecutive_runs(high_months)

    # Sort runs by total score
    def _run_score(run):
        return df[df["Month"].isin(run)]["Seasonal_Risk_Score"].sum()

    seasons = sorted(seasons, key=_run_score, reverse=True)

    # Peak month = highest individual score
    peak_row = df.loc[df["Seasonal_Risk_Score"].idxmax()]
    peak_month      = int(peak_row["Month"])
    peak_month_name = MONTH_FULL_NAMES[peak_month - 1]

    primary   = _season_dict(seasons[0]) if len(seasons) > 0 else _season_dict([peak_month])
    secondary = _season_dict(seasons[1]) if len(seasons) > 1 else None

    return {
        "primary":               primary,
        "secondary":             secondary,
        "peak_month":            peak_month,
        "peak_month_name":       peak_month_name,
        "high_risk_months":      high_months,
        "high_risk_month_names": [MONTH_FULL_NAMES[m - 1] for m in high_months],
    }


def _find_consecutive_runs(months: list[int]) -> list[list[int]]:
    """Split a sorted list of months into consecutive groups."""
    if not months:
        return []
    runs, current = [], [months[0]]
    for m in months[1:]:
        if m == current[-1] + 1:
            current.append(m)
        else:
            runs.append(current)
            current = [m]
    runs.append(current)
    return [r for r in runs if len(r) >= MIN_SEASON_LENGTH]


def _season_dict(months: list[int]) -> dict:
    return {
        "start_month": months[0],
        "end_month":   months[-1],
        "start_name":  MONTH_FULL_NAMES[months[0] - 1],
        "end_name":    MONTH_FULL_NAMES[months[-1] - 1],
        "months":      months,
    }
