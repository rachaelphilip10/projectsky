"""
HazeCrop Malaysia — NASA MODIS MAIAC AOD data service.

All Earth Engine queries for AOD data live here.  The public API:

  get_monthly_aod(region, year, month)    → float | None
  get_yearly_aod_data(region, year, state_name) → pd.DataFrame
  get_historical_aod(region, start_year, end_year, state_name) → pd.DataFrame
  get_aod_image(region, start_date, end_date) → ee.Image | None

The MODIS MAIAC collection is:  MODIS/061/MCD19A2_GRANULES
AOD band at ~0.55 µm:           Optical_Depth_055

No satellite band names, scale, or QA details are exposed in the UI.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import ee

from config.settings import (
    MODIS_COLLECTION,
    MODIS_AOD_BAND,
    MODIS_SCALE_METRES,
    MODIS_MAX_PIXELS,
)


# ─── Internal helpers ────────────────────────────────────────────────────────

def _safe_getinfo(ee_obj) -> object | None:
    """Call .getInfo() and return None on any EE or network error."""
    try:
        return ee_obj.getInfo()
    except Exception:
        return None


def _aod_collection(region: ee.FeatureCollection,
                    start_date: str,
                    end_date: str) -> ee.ImageCollection:
    """
    Return a filtered MODIS MAIAC collection restricted to the given
    region and date window.  AOD scale factor 0.001 is applied.
    """
    return (
        ee.ImageCollection(MODIS_COLLECTION)
        .select(MODIS_AOD_BAND)
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .map(lambda img: img.multiply(0.001).copyProperties(img, img.propertyNames()))
    )


def _reduce_to_scalar(image: ee.Image,
                      region: ee.FeatureCollection,
                      reducer: ee.Reducer) -> float | None:
    """Reduce an image to a single scalar over the region geometry."""
    try:
        result = image.reduceRegion(
            reducer=reducer,
            geometry=region.geometry(),
            scale=MODIS_SCALE_METRES,
            maxPixels=MODIS_MAX_PIXELS,
            bestEffort=True,
        )
        val = _safe_getinfo(result.get(MODIS_AOD_BAND))
        return float(val) if val is not None else None
    except Exception:
        return None


# ─── Public API ──────────────────────────────────────────────────────────────

def get_monthly_aod(region: ee.FeatureCollection,
                    year: int,
                    month: int) -> tuple[float | None, float | None]:
    """
    Return (mean_aod, max_aod) for a single month.

    Returns (None, None) if the collection is empty or EE is unavailable.
    """
    start = f"{year}-{month:02d}-01"
    if month == 12:
        end = f"{year + 1}-01-01"
    else:
        end = f"{year}-{month + 1:02d}-01"

    col = _aod_collection(region, start, end)
    size = _safe_getinfo(col.size())
    if not size:
        return None, None

    mean_img = col.mean()
    max_img  = col.max()

    mean_val = _reduce_to_scalar(mean_img, region, ee.Reducer.mean())
    max_val  = _reduce_to_scalar(max_img,  region, ee.Reducer.max())
    return mean_val, max_val


@st.cache_data(ttl=3600, show_spinner=False)
def get_yearly_aod_data(_region_fao_name: str,
                        year: int,
                        state_name: str) -> pd.DataFrame:
    """
    Return a 12-row DataFrame of monthly AOD statistics for one year.

    Columns: Date, Year, Month, State, Mean_AOD, Maximum_AOD
    """
    from services.malaysia_regions import FAO_NAME_MAP
    fao_name = FAO_NAME_MAP.get(state_name, state_name)
    region   = (
        ee.FeatureCollection("FAO/GAUL/2015/level1")
        .filter(ee.Filter.eq("ADM1_NAME", fao_name))
    )

    rows = []
    for month in range(1, 13):
        mean_val, max_val = get_monthly_aod(region, year, month)
        rows.append({
            "Date":       pd.Timestamp(f"{year}-{month:02d}-01"),
            "Year":       year,
            "Month":      month,
            "State":      state_name,
            "Mean_AOD":   mean_val if mean_val is not None else np.nan,
            "Maximum_AOD": max_val if max_val is not None else np.nan,
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=7200, show_spinner=False)
def get_historical_aod(_region_fao_name: str,
                       start_year: int,
                       end_year: int,
                       state_name: str) -> pd.DataFrame:
    """
    Return monthly AOD data across multiple years.

    Parameters
    ----------
    start_year : int  (inclusive)
    end_year   : int  (inclusive)

    Returns a DataFrame with Date, Year, Month, State, Mean_AOD, Maximum_AOD.
    """
    from services.malaysia_regions import FAO_NAME_MAP
    fao_name = FAO_NAME_MAP.get(state_name, state_name)
    region   = (
        ee.FeatureCollection("FAO/GAUL/2015/level1")
        .filter(ee.Filter.eq("ADM1_NAME", fao_name))
    )

    rows = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            mean_val, max_val = get_monthly_aod(region, year, month)
            rows.append({
                "Date":        pd.Timestamp(f"{year}-{month:02d}-01"),
                "Year":        year,
                "Month":       month,
                "State":       state_name,
                "Mean_AOD":    mean_val if mean_val is not None else np.nan,
                "Maximum_AOD": max_val  if max_val  is not None else np.nan,
            })
    return pd.DataFrame(rows)


def get_aod_image(region: ee.FeatureCollection,
                  start_date: str,
                  end_date: str) -> ee.Image | None:
    """
    Return a mean AOD image for the given period, or None if empty.
    Used by the map view to display a raster layer.
    """
    col  = _aod_collection(region, start_date, end_date)
    size = _safe_getinfo(col.size())
    if not size:
        return None
    return col.mean()


def calculate_monthly_baseline(historical_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the monthly mean baseline from multi-year historical data.

    Returns a 12-row DataFrame indexed by Month (1–12) with:
      Month, Baseline_Mean_AOD, Baseline_Std_AOD
    """
    grouped = (
        historical_df.dropna(subset=["Mean_AOD"])
        .groupby("Month")["Mean_AOD"]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    grouped.columns = ["Month", "Baseline_Mean_AOD", "Baseline_Std_AOD", "Obs_Count"]
    grouped["Baseline_Std_AOD"] = grouped["Baseline_Std_AOD"].fillna(0.0)
    return grouped


def calculate_aod_anomaly(historical_df: pd.DataFrame,
                          baseline_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute AOD_Anomaly = Mean_AOD − Baseline_Mean_AOD for each row.

    Returns the historical_df with an additional AOD_Anomaly column.
    """
    df = historical_df.merge(baseline_df[["Month", "Baseline_Mean_AOD"]],
                              on="Month", how="left")
    df["AOD_Anomaly"] = df["Mean_AOD"] - df["Baseline_Mean_AOD"]
    return df
