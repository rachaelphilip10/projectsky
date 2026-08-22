"""
HazeCrop Malaysia — Google Earth Engine initialisation.

Tries, in order:
  1. EARTHENGINE_PROJECT environment variable
  2. Streamlit secrets key  'earthengine_project'
  3. Default ee.Initialize() (uses previously-authenticated credentials)
"""

import os
import streamlit as st
import ee


@st.cache_resource(show_spinner=False)
def initialize_earth_engine() -> bool:
    """
    Initialise the Earth Engine Python API.

    Returns True on success, False on failure.
    Never raises — the caller should check the return value and
    show a user-friendly message if False.
    """
    project = _resolve_project()
    try:
        _try_init(project)
        return True
    except Exception:
        # Attempt interactive authentication then re-initialise.
        try:
            ee.Authenticate(quiet=True)
            _try_init(project)
            return True
        except Exception:
            return False


def _resolve_project() -> str | None:
    """Return the GEE project ID from env or Streamlit secrets."""
    project = os.environ.get("EARTHENGINE_PROJECT")
    if not project:
        try:
            project = st.secrets.get("earthengine_project", None)
        except Exception:
            project = None
    return project or None


def _try_init(project: str | None) -> None:
    """Call ee.Initialize with or without an explicit project."""
    if project:
        ee.Initialize(project=project)
    else:
        ee.Initialize()
