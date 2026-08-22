"""
HazeCrop Malaysia — Agent 1: Data Analyst

Responsibility:
  • Fetch MODIS MAIAC AOD data for the selected state and period
  • Identify missing data
  • Calculate per-month statistics
  • Detect anomalies
  • Return a structured satellite statistics payload

This agent does NOT do pattern analysis or outlooks — it only provides
clean, validated data to downstream agents.

Public API
----------
  run_data_analyst(state, target_year, historical_years) → dict
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from services.malaysia_regions import FAO_NAME_MAP
from services.aod_service import (
    get_yearly_aod_data,
    get_historical_aod,
    calculate_monthly_baseline,
    calculate_aod_anomaly,
)


def run_data_analyst(state: str,
                     target_year: int,
                     historical_years: int) -> dict:
    """
    Fetch and validate MODIS AOD data for the analysis.

    Parameters
    ----------
    state            : display name of the Malaysian state
    target_year      : year for which the outlook is being generated
    historical_years : number of past years to include in the historical record

    Returns
    -------
    dict with keys:
      status          : "ok" | "warn" | "error"
      message         : human-readable status string
      historical_df   : pd.DataFrame  (multi-year monthly AOD)
      baseline_df     : pd.DataFrame  (monthly mean baseline)
      historical_with_anomaly : pd.DataFrame
      missing_months  : list[str]  — months with no valid AOD observation
      valid_obs       : int
      total_expected  : int
      completeness    : float  (0–1)
      n_years         : int
    """
    fao_name   = FAO_NAME_MAP.get(state, state)
    start_year = target_year - historical_years
    end_year   = target_year - 1  # historical only; target year is the forecast horizon

    # ── Fetch historical data ─────────────────────────────────────────────────
    try:
        historical_df = get_historical_aod(fao_name, start_year, end_year, state)
    except Exception as exc:
        return _error_result(f"Satellite data retrieval failed: {exc}")

    if historical_df.empty:
        return _error_result("No satellite data returned for the selected location and period.")

    # ── Baseline and anomaly ──────────────────────────────────────────────────
    baseline_df = calculate_monthly_baseline(historical_df)
    historical_with_anomaly = calculate_aod_anomaly(historical_df, baseline_df)

    # ── Data quality assessment ───────────────────────────────────────────────
    valid_obs      = int(historical_df["Mean_AOD"].notna().sum())
    total_expected = int(historical_years * 12)
    completeness   = valid_obs / total_expected if total_expected > 0 else 0.0
    n_years        = int(historical_df["Year"].nunique())

    # Missing months (month-year pairs)
    missing = historical_df[historical_df["Mean_AOD"].isna()].copy()
    missing_months = [
        f"{row['Month']:02d}/{row['Year']}"
        for _, row in missing.iterrows()
    ]

    # ── Anomaly detection: months with AOD > 2 SD above baseline ─────────────
    anomaly_df = historical_with_anomaly.dropna(subset=["AOD_Anomaly"])
    if not anomaly_df.empty:
        sd2 = anomaly_df["AOD_Anomaly"].mean() + 2 * anomaly_df["AOD_Anomaly"].std()
        anomalies = anomaly_df[anomaly_df["AOD_Anomaly"] > sd2]
    else:
        anomalies = pd.DataFrame()

    # ── Status ────────────────────────────────────────────────────────────────
    if completeness >= 0.75:
        status  = "ok"
        message = (
            f"Data retrieved for {state}: {valid_obs}/{total_expected} "
            f"monthly observations valid ({completeness * 100:.0f}%)."
        )
    elif completeness > 0:
        status  = "warn"
        message = (
            f"Partial data for {state}: {valid_obs}/{total_expected} valid observations. "
            "Analysis proceeds but confidence may be lower."
        )
    else:
        return _error_result(
            f"No valid AOD observations found for {state} "
            f"({start_year}–{end_year}). Try a different location or time period."
        )

    return {
        "status":                 status,
        "message":                message,
        "historical_df":          historical_df,
        "baseline_df":            baseline_df,
        "historical_with_anomaly": historical_with_anomaly,
        "missing_months":         missing_months,
        "valid_obs":              valid_obs,
        "total_expected":         total_expected,
        "completeness":           completeness,
        "n_years":                n_years,
        "anomaly_count":          len(anomalies),
        "start_year":             start_year,
        "end_year":               end_year,
    }


def _error_result(message: str) -> dict:
    empty = pd.DataFrame()
    return {
        "status":                 "error",
        "message":                message,
        "historical_df":          empty,
        "baseline_df":            empty,
        "historical_with_anomaly": empty,
        "missing_months":         [],
        "valid_obs":              0,
        "total_expected":         0,
        "completeness":           0.0,
        "n_years":                0,
        "anomaly_count":          0,
        "start_year":             None,
        "end_year":               None,
    }
