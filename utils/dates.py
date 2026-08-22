"""
HazeCrop Malaysia — Date and calendar utilities.
"""

from __future__ import annotations

import datetime
from config.settings import MONTH_FULL_NAMES, MONTH_LABELS


def current_year() -> int:
    """Return the current calendar year."""
    return datetime.datetime.now().year


def month_name(month: int) -> str:
    """Return the full month name for month number 1–12."""
    if 1 <= month <= 12:
        return MONTH_FULL_NAMES[month - 1]
    return "Unknown"


def month_abbr(month: int) -> str:
    """Return the 3-character abbreviated month name for month 1–12."""
    if 1 <= month <= 12:
        return MONTH_LABELS[month - 1]
    return "???"


def months_before(month: int, n: int) -> int:
    """
    Return the month number that is n months before the given month.
    Wraps around the calendar year.
    """
    return ((month - 1 - n) % 12) + 1


def month_range_label(start_month: int, end_month: int) -> str:
    """
    Return a human-readable label for a range of months.

    Examples:
      month_range_label(8, 10) → "Aug – Oct"
      month_range_label(9, 9)  → "September"
    """
    if start_month == end_month:
        return MONTH_FULL_NAMES[start_month - 1]
    return f"{MONTH_LABELS[start_month - 1]} – {MONTH_LABELS[end_month - 1]}"
