"""
HazeCrop Malaysia — UI: Map View

Renders the interactive satellite map using geemap.

Segmented control:
  [ 🌫 AOD ]  [ 📊 Historical Pattern ]

Public API
----------
  render_map_idle(state)
  render_map_results(state, target_year, historical_years,
                     outlook_result, data_result)
"""

from __future__ import annotations

import streamlit as st

try:
    import geemap.foliumap as geemap
    GEEMAP_AVAILABLE = True
except Exception:
    try:
        import geemap
        GEEMAP_AVAILABLE = True
    except Exception:
        GEEMAP_AVAILABLE = False

import ee
from services.malaysia_regions import get_state_centroid, FAO_NAME_MAP
from services.aod_service import get_aod_image


# AOD vis params
_AOD_VIS = {
    "min":     0.0,
    "max":     0.8,
    "palette": ["#001219", "#0a9396", "#94d2bd", "#e9c46a", "#f4a261", "#e76f51", "#9b2226"],
}


def render_map_idle(state: str) -> None:
    st.markdown('<div id="map"></div>', unsafe_allow_html=True)
    st.markdown('<div class="hc-section-label">🗺 &nbsp;Satellite Map</div>', unsafe_allow_html=True)
    lat, lon = get_state_centroid(state)
    _render_base_map(lat, lon, state, zoom=8)


def render_map_results(state: str,
                       target_year: int,
                       historical_years: int,
                       outlook_result: dict,
                       data_result: dict) -> None:
    """Render the map with AOD or Historical Pattern layer."""
    st.markdown('<div id="map"></div>', unsafe_allow_html=True)
    st.markdown('<div class="hc-section-label">🗺 &nbsp;Satellite Map</div>', unsafe_allow_html=True)

    mode = st.radio(
        "Map layer",
        ["🌫 AOD", "📊 Historical Pattern"],
        horizontal=True,
        label_visibility="collapsed",
    )

    lat, lon = get_state_centroid(state)

    if mode == "🌫 AOD":
        _render_aod_layer(state, target_year, historical_years, lat, lon)
    else:
        _render_historical_layer(state, data_result, lat, lon, outlook_result)


# ─── Internal renderers ───────────────────────────────────────────────────────

def _render_base_map(lat: float, lon: float, state: str, zoom: int = 8) -> None:
    """Render a basic map with only the state boundary."""
    if not GEEMAP_AVAILABLE:
        _map_unavailable_card()
        return

    try:
        m = geemap.Map(center=[lat, lon], zoom=zoom)
        m.add_basemap("CartoDB.Positron")

        # State boundary
        fao_name = FAO_NAME_MAP.get(state, state)
        state_fc = (
            ee.FeatureCollection("FAO/GAUL/2015/level1")
            .filter(ee.Filter.eq("ADM1_NAME", fao_name))
        )
        m.addLayer(
            state_fc.style(**{"color": "#22d3ee", "fillColor": "#00000000", "width": 2}),
            {},
            f"{state} boundary",
        )
        m.to_streamlit(height=440, width=-1)
    except Exception as exc:
        _map_error_card(str(exc))


def _render_aod_layer(state: str, target_year: int, historical_years: int,
                      lat: float, lon: float) -> None:
    """Show mean AOD composite for the analysis period."""
    if not GEEMAP_AVAILABLE:
        _map_unavailable_card()
        return

    try:
        fao_name = FAO_NAME_MAP.get(state, state)
        region   = (
            ee.FeatureCollection("FAO/GAUL/2015/level1")
            .filter(ee.Filter.eq("ADM1_NAME", fao_name))
        )
        start_year = target_year - historical_years
        start_date = f"{start_year}-01-01"
        end_date   = f"{target_year}-01-01"

        aod_image = get_aod_image(region, start_date, end_date)

        m = geemap.Map(center=[lat, lon], zoom=8)
        m.add_basemap("CartoDB.Positron")

        if aod_image is not None:
            m.addLayer(aod_image, _AOD_VIS, f"Mean AOD {start_year}–{target_year - 1}")
            m.add_colorbar(
                vis_params=_AOD_VIS,
                label="Mean AOD (MODIS MAIAC ~0.55 µm)",
                layer_name=f"Mean AOD {start_year}–{target_year - 1}",
            )
        else:
            st.warning("AOD raster not available for this period. Showing boundary only.")

        # State outline
        m.addLayer(
            region.style(**{"color": "#22d3ee", "fillColor": "#00000000", "width": 2}),
            {},
            f"{state} boundary",
        )

        # Malaysia outline
        malaysia = (
            ee.FeatureCollection("FAO/GAUL/2015/level1")
            .filter(ee.Filter.eq("ADM0_NAME", "Malaysia"))
        )
        m.addLayer(
            malaysia.style(**{"color": "#AAAAAA", "fillColor": "#00000000", "width": 1}),
            {},
            "Malaysia",
        )

        m.to_streamlit(height=480)

    except Exception as exc:
        _map_error_card(str(exc))


def _render_historical_layer(state: str, data_result: dict,
                              lat: float, lon: float,
                              outlook_result: dict) -> None:
    """Show the AOD anomaly layer for the peak month across historical years."""
    if not GEEMAP_AVAILABLE:
        _map_unavailable_card()
        return

    try:
        fao_name = FAO_NAME_MAP.get(state, state)
        region   = (
            ee.FeatureCollection("FAO/GAUL/2015/level1")
            .filter(ee.Filter.eq("ADM1_NAME", fao_name))
        )

        peak_month = outlook_result["outlook"]["peak_month"]
        start_year = data_result.get("start_year", 2018)
        end_year   = data_result.get("end_year", 2023)

        # Build a mean image of the peak month across all historical years
        images = []
        from config.settings import MODIS_COLLECTION, MODIS_AOD_BAND
        for yr in range(start_year, end_year + 1):
            start = f"{yr}-{peak_month:02d}-01"
            end   = (
                f"{yr + 1}-01-01" if peak_month == 12
                else f"{yr}-{peak_month + 1:02d}-01"
            )
            col = (
                ee.ImageCollection(MODIS_COLLECTION)
                .select(MODIS_AOD_BAND)
                .filterDate(start, end)
                .filterBounds(region)
                .map(lambda img: img.multiply(0.001).copyProperties(img, img.propertyNames()))
            )
            images.append(col.mean())

        if images:
            composite = ee.ImageCollection(images).mean()
            m = geemap.Map(center=[lat, lon], zoom=8)
            m.add_basemap("CartoDB.Positron")
            m.addLayer(composite, _AOD_VIS, f"Historical Pattern — peak month")
            m.add_colorbar(
                vis_params=_AOD_VIS,
                label="Mean AOD (peak month composite)",
                layer_name="Historical Pattern — peak month",
            )
        else:
            m = geemap.Map(center=[lat, lon], zoom=8)
            m.add_basemap("CartoDB.Positron")
            st.warning("Historical pattern composite unavailable. Showing boundary only.")

        m.addLayer(
            region.style(**{"color": "#22d3ee", "fillColor": "#00000000", "width": 2}),
            {},
            f"{state} boundary",
        )
        m.to_streamlit(height=480)

    except Exception as exc:
        _map_error_card(str(exc))


def _map_unavailable_card() -> None:
    st.markdown(
        '<div class="hc-card" style="text-align:center;padding:48px 28px;">'
        '<div style="font-size:36px;margin-bottom:16px;">🗺️</div>'
        '<div style="font-family:Fraunces,Georgia,serif;font-size:18px;font-weight:600;color:#1E2A1C;margin-bottom:8px;">Map unavailable</div>'
        '<div style="font-size:14px;color:#5C6858;">geemap is not installed. Install it with '
        '<code style="background:#F6F4EE;padding:2px 6px;border-radius:4px;border:1px solid #E4E1D6;color:#1E2A1C;">pip install geemap</code> to enable the satellite map view.</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _map_error_card(error: str) -> None:
    st.markdown(
        '<div class="hc-card" style="border-left:4px solid #9B3330;text-align:center;padding:36px 28px;">'
        '<div style="font-size:28px;margin-bottom:12px;">⚠️</div>'
        '<div style="font-family:Fraunces,Georgia,serif;font-size:16px;font-weight:600;color:#1E2A1C;margin-bottom:6px;">Map rendering error</div>'
        '<div style="font-size:13px;color:#5C6858;margin-bottom:10px;">The satellite map could not be displayed for this configuration. The analysis results above are still valid.</div>'
        f'<div style="font-size:11px;color:#9B3330;background:#FAEAEA;border-radius:8px;padding:8px 12px;text-align:left;word-break:break-word;">{error}</div>'
        '</div>',
        unsafe_allow_html=True,
    )
