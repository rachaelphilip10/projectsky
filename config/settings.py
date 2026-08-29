"""
HazeCrop Malaysia — Central configuration.

All tuneable constants live here so no magic numbers are scattered
across the codebase.  Import with:

    from config.settings import *   (or specific names)
"""

# ── NASA MODIS AOD dataset ────────────────────────────────────────────────────
MODIS_COLLECTION    = "MODIS/061/MCD19A2_GRANULES"
MODIS_AOD_BAND      = "Optical_Depth_055"          # ~0.55 µm AOD band
MODIS_SCALE_METRES  = 1000                          # native pixel resolution
MODIS_MAX_PIXELS    = 1e10

# FAO GAUL boundary dataset used for state polygons
FAO_GAUL_L1         = "FAO/GAUL/2015/level1"
FAO_GAUL_COUNTRY    = "Malaysia"

# AOD quality flag band & acceptable QA values
MODIS_QA_BAND       = "AOD_QA"
MODIS_GOOD_QA       = [0, 1]                        # 0 = best, 1 = good

# ── Seasonal pattern scoring weights ─────────────────────────────────────────
# Adjust these to change how the Seasonal Risk Score is computed.
WEIGHT_HISTORICAL_MEAN   = 0.40   # 40% – mean AOD across historical years
WEIGHT_HIGH_FREQ         = 0.25   # 25% – frequency of top-tercile months
WEIGHT_RECENT_TREND      = 0.20   # 20% – recent-year AOD trend direction
WEIGHT_CONSISTENCY       = 0.15   # 15% – inter-annual standard deviation

# ── Risk classification thresholds (seasonal score 0–100) ────────────────────
RISK_LOW_MAX        = 25
RISK_MODERATE_MAX   = 50
RISK_HIGH_MAX       = 75
# Above 75 → Very High

# ── Haze-season detection ─────────────────────────────────────────────────────
HIGH_RISK_SCORE_THRESHOLD = 50    # Months above this are "high-risk"
MIN_SEASON_LENGTH         = 1     # Minimum consecutive months to call it a season

# ── Confidence calculation parameters ────────────────────────────────────────
MIN_YEARS_HIGH_CONFIDENCE   = 6   # ≥ 6 years → eligible for High confidence
MIN_YEARS_MEDIUM_CONFIDENCE = 3   # 3–5 years → Medium
# < 3 years → Low

CONSISTENCY_HIGH_THRESHOLD   = 0.70   # peak-month agreement ≥ 70% → consistent
CONSISTENCY_MEDIUM_THRESHOLD = 0.40

CONFIDENCE_LABELS = {
    "High":   65,   # score ≥ 65 → High confidence
    "Medium": 40,   # score ≥ 40 → Medium confidence
    # below 40 → Low confidence
}

# ── Analysis defaults ─────────────────────────────────────────────────────────
DEFAULT_STATE           = "Selangor"
DEFAULT_TARGET_YEAR     = 2027
DEFAULT_HISTORICAL_YEARS = 3
MIN_HISTORICAL_YEARS    = 3
MAX_HISTORICAL_YEARS    = 10

# ── Data export columns ────────────────────────────────────────────────────────
EXPORT_COLUMNS = [
    "Date", "Year", "Month", "State",
    "Mean_AOD", "Maximum_AOD", "AOD_Anomaly",
    "Seasonal_Risk_Score", "Risk_Category",
]

# ── Plotly light layout (cream/forest design system) ──────────────────────────
DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(246,244,238,0.5)",
    font=dict(color="#5C6858", family="Inter, sans-serif", size=12),
    xaxis=dict(
        gridcolor="rgba(228,225,214,0.8)",
        linecolor="#E4E1D6",
        tickcolor="#8FA688",
        zerolinecolor="#E4E1D6",
    ),
    yaxis=dict(
        gridcolor="rgba(228,225,214,0.8)",
        linecolor="#E4E1D6",
        tickcolor="#8FA688",
        zerolinecolor="#E4E1D6",
    ),
    legend=dict(
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#E4E1D6",
        borderwidth=1,
        font=dict(color="#1E2A1C"),
    ),
    margin=dict(l=12, r=12, t=40, b=12),
)

# ── Risk colour palette (light-mode readable) ─────────────────────────────────
RISK_COLOURS = {
    "Low":       "#4C6B45",
    "Moderate":  "#A06C2A",
    "High":      "#9B3330",
    "Very High": "#5C2D91",
}

RISK_CSS_CLASSES = {
    "Low":       "risk-low",
    "Moderate":  "risk-moderate",
    "High":      "risk-high",
    "Very High": "risk-severe",
}

# ── Month labels ──────────────────────────────────────────────────────────────
MONTH_LABELS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

MONTH_FULL_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]