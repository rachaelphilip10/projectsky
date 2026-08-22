"""
HazeCrop Malaysia — Agent 4: Crop Preparedness Agent

Responsibility:
  • Generate pre-season preparation suggestions based on the predicted haze window
  • Return a structured preparedness plan

The agent does NOT fabricate satellite values.  All its output is
based on the structured ai_input_summary from the Outlook Agent.

Public API
----------
  run_preparedness_agent(outlook_result) → dict
"""

from __future__ import annotations

from config.settings import MONTH_FULL_NAMES


def run_preparedness_agent(outlook_result: dict) -> dict:
    """
    Generate the Pre-Haze Season Preparation Plan.

    Parameters
    ----------
    outlook_result : output of agents/outlook_agent.run_outlook_agent()

    Returns
    -------
    dict with keys:
      status           : "ok" | "warn" | "error"
      message          : str
      recommendations  : list[dict]
      timeline         : list[dict]  (passed through from outlook_result)
      disclaimer       : str
    """
    if outlook_result["status"] == "error":
        return _error_result("Preparedness plan skipped — outlook generation failed.")

    ai_summary = outlook_result["ai_input_summary"]
    timeline   = outlook_result["timeline"]
    peak_month = ai_summary.get("peak_month", "October")
    primary    = ai_summary.get("primary_season", "August – October")
    risk_level = ai_summary.get("risk_level", "Moderate")

    # ── Four core recommendations (spec section 17) ───────────────────────────

    # Timing helper
    peak_idx   = _month_index(peak_month)
    prep_start = MONTH_FULL_NAMES[max(0, peak_idx - 4)]

    recommendations = [
        {
            "icon":     "💡",
            "title":    "Artificial Lighting",
            "priority": "Medium",
            "when":     f"Before the next planting cycle (by {prep_start})",
            "why": (
                "Reduced sunlight during prolonged haze may affect photosynthetically "
                "active radiation for high-value protected crops. Lighting requirements "
                "should be assessed during farm planning, not during a haze event."
            ),
            "detail": (
                "Evaluate supplemental lighting before the predicted haze season. "
                "For suitable protected or high-value cropping systems, assess "
                "lighting requirements during farm planning rather than waiting "
                "until haze conditions occur."
            ),
        },
        {
            "icon":     "💧",
            "title":    "Leaf Surface Management",
            "priority": _priority(risk_level, "Moderate", "High"),
            "when":     f"Develop strategy before {primary} window",
            "why": (
                "Particulate deposition on leaf surfaces reduces photosynthetic "
                "efficiency. A crop-appropriate management strategy should be "
                "developed in advance rather than reactively."
            ),
            "detail": (
                "Review leaf-cleaning and irrigation strategies before the haze season. "
                "Where appropriate for the crop and production system, develop a "
                "suitable approach for managing particulate deposition on leaf surfaces."
            ),
        },
        {
            "icon":     "💨",
            "title":    "Humidity Monitoring",
            "priority": "High",
            "when":     f"Establish baselines at least 2 months before {primary}",
            "why": (
                "Elevated humidity combined with haze can promote fungal disease. "
                "Baseline data collected before the haze window allows unusual "
                "conditions to be identified quickly."
            ),
            "detail": (
                "Establish humidity monitoring before the predicted haze period. "
                "Use baseline environmental data to identify unusual conditions "
                "during prolonged haze events."
            ),
        },
        {
            "icon":     "🌱",
            "title":    "Plant and Row Spacing",
            "priority": "Medium",
            "when":     "Before the next planting cycle",
            "why": (
                "Structural decisions such as crop spacing require advance planning "
                "and cannot be easily changed once crops are established. "
                "Adequate spacing improves light penetration and airflow during haze."
            ),
            "detail": (
                "Review planting density and row spacing during the next crop "
                "planning cycle. Optimise spacing according to crop-specific "
                "agronomic requirements and allow adequate light penetration "
                "and airflow."
            ),
        },
    ]

    disclaimer = (
        "This is a seasonal outlook based on historical satellite-observed "
        "aerosol patterns. It is not a guaranteed real-time haze forecast. "
        "Recommendations are general agricultural guidance and should be "
        "adapted to specific crop types, farm conditions, and local advice."
    )

    return {
        "status":          "ok",
        "message":         f"Pre-haze preparation plan generated for {primary} window.",
        "recommendations": recommendations,
        "timeline":        timeline,
        "disclaimer":      disclaimer,
    }


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _month_index(month_name: str) -> int:
    """Return 0-based index of a month name."""
    try:
        return MONTH_FULL_NAMES.index(month_name)
    except ValueError:
        return 8  # default September


def _priority(risk_level: str, moderate_priority: str, high_priority: str) -> str:
    if risk_level in ("High", "Very High"):
        return high_priority
    return moderate_priority


def _error_result(message: str) -> dict:
    return {
        "status":          "error",
        "message":         message,
        "recommendations": [],
        "timeline":        [],
        "disclaimer":      "",
    }
