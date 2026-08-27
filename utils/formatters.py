"""
HazeCrop Malaysia — Formatting utilities.
"""

from __future__ import annotations

import math


def fmt_aod(value: float | None, decimals: int = 3) -> str:
    """Format an AOD float value, returning '—' for None/NaN."""
    if value is None:
        return "—"
    if isinstance(value, float) and math.isnan(value):
        return "—"
    return f"{value:.{decimals}f}"


def fmt_pct(value: float | None, decimals: int = 0) -> str:
    """Format a fraction (0–1) as a percentage string."""
    if value is None:
        return "—"
    if isinstance(value, float) and math.isnan(value):
        return "—"
    return f"{value * 100:.{decimals}f}%"


def risk_css_class(risk_level: str) -> str:
    """Map a risk level string to the corresponding CSS class."""
    mapping = {
        "Low":       "risk-low",
        "Moderate":  "risk-moderate",
        "High":      "risk-high",
        "Very High": "risk-severe",
    }
    return mapping.get(risk_level, "risk-moderate")


def risk_colour(risk_level: str) -> str:
    """Map a risk level string to the corresponding hex colour."""
    mapping = {
        "Low":       "#4ade80",
        "Moderate":  "#fb923c",
        "High":      "#f87171",
        "Very High": "#a78bfa",
    }
    return mapping.get(risk_level, "#fb923c")


def agent_status_html(statuses: dict[str, str]) -> str:
    """
    Build the HTML pill row for agent pipeline status.

    statuses: {"Agent Name": "ok" | "warn" | "off"}
    """
    icons = {"ok": "✓", "warn": "⚠", "off": "·"}
    pills = "".join(
        f'<span class="hc-agent-pill agent-{v}">{icons.get(v, "·")} {k}</span>'
        for k, v in statuses.items()
    )
    return f'<div class="hc-agent-row">{pills}</div>'
