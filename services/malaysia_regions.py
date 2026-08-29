from __future__ import annotations

"""
HazeCrop Malaysia — State boundary helpers.

Provides:
  get_malaysia_states()  — cached EE FeatureCollection
  get_selected_region()  — single-state Feature
  MALAYSIA_STATES        — ordered list of display names
  FAO_NAME_MAP           — display name → FAO/GAUL ADM1_NAME
  STATE_CENTROIDS        — approximate lat/lon for map centring
"""

import streamlit as st
import ee
from config.settings import FAO_GAUL_L1, FAO_GAUL_COUNTRY
from services.earth_engine import initialize_earth_engine


# ── Display-name list (shown in the UI selectbox) ────────────────────────────
MALAYSIA_STATES = [
    "Johor",
    "Kedah",
    "Kelantan",
    "Kuala Lumpur",
    "Labuan",
    "Melaka",
    "Negeri Sembilan",
    "Pahang",
    "Penang",
    "Perak",
    "Perlis",
    "Putrajaya",
    "Sabah",
    "Sarawak",
    "Selangor",
    "Terengganu",
]

# ── FAO/GAUL ADM1_NAME values differ for some states ─────────────────────────
FAO_NAME_MAP = {
    "Penang":       "Pulau Pinang",
    "Kuala Lumpur": "Wilayah Persekutuan Kuala Lumpur",
    "Putrajaya":    "Wilayah Persekutuan Putrajaya",
    "Labuan":       "Wilayah Persekutuan Labuan",
}

# ── Approximate centroids (lat, lon) for map auto-zoom ───────────────────────
STATE_CENTROIDS = {
    "Johor":            (1.86,  103.77),
    "Kedah":            (6.12,  100.37),
    "Kelantan":         (5.53,  102.11),
    "Kuala Lumpur":     (3.14,  101.69),
    "Labuan":           (5.28,  115.24),
    "Melaka":           (2.19,  102.24),
    "Negeri Sembilan":  (2.73,  102.00),
    "Pahang":           (3.81,  103.33),
    "Penang":           (5.42,  100.34),
    "Perak":            (4.59,  101.09),
    "Perlis":           (6.44,  100.19),
    "Putrajaya":        (2.92,  101.69),
    "Sabah":            (5.97,  116.07),
    "Sarawak":          (1.55,  110.34),
    "Selangor":         (3.07,  101.52),
    "Terengganu":       (5.31,  103.14),
}


@st.cache_resource(show_spinner=False)
def get_malaysia_states() -> ee.FeatureCollection:
    """Return the full FAO/GAUL Level-1 FeatureCollection for Malaysia."""
    return (
        ee.FeatureCollection(FAO_GAUL_L1)
        .filter(ee.Filter.eq("ADM0_NAME", FAO_GAUL_COUNTRY))
    )


def get_selected_region(state_display_name: str) -> ee.FeatureCollection:
    """
    Return the EE FeatureCollection for a single Malaysian state.

    Parameters
    ----------
    state_display_name : str
        One of the values in MALAYSIA_STATES (UI display name).

    Returns
    -------
    ee.FeatureCollection
        Filtered to the single state/territory.
    """
    fao_name = FAO_NAME_MAP.get(state_display_name, state_display_name)
    initialize_earth_engine()
    return (
        ee.FeatureCollection(FAO_GAUL_L1)
        .filter(ee.Filter.eq("ADM1_NAME", fao_name))
    )


def get_state_centroid(state_display_name: str) -> tuple[float, float]:
    """Return (lat, lon) centroid for the given state (for map auto-zoom)."""
    return STATE_CENTROIDS.get(state_display_name, (4.0, 109.5))