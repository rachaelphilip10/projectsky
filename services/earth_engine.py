from __future__ import annotations

"""
HazeCrop Malaysia — Google Earth Engine initialisation.

Tries, in order:
  1. Service account JSON from Streamlit secrets  (cloud deployment)
  2. EARTHENGINE_PROJECT environment variable     (local with env var)
  3. Streamlit secrets key 'earthengine_project'  (local with secrets.toml)
  4. Default ee.Initialize()                      (local interactive credentials)
"""

import json
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
    # ── Try service account first (required on Streamlit Cloud) ──────────────
    if _try_service_account():
        return True

    # ── Fall back to interactive / env-var credentials (local) ───────────────
    project = _resolve_project()
    try:
        _try_init(project)
        return True
    except Exception:
        try:
            ee.Authenticate(quiet=True)
            _try_init(project)
            return True
        except Exception:
            return False


def _try_service_account() -> bool:
    """
    Initialise using a service account JSON stored in Streamlit secrets.

    In secrets.toml (or Streamlit Cloud secret manager) add:

        [gee]
        service_account = "name@project.iam.gserviceaccount.com"
        private_key     = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"

    Returns True on success, False if the secret is absent or invalid.
    """
    try:
        gee_secrets = st.secrets.get("gee", {})
        service_account = gee_secrets.get("service_account", "")
        private_key     = gee_secrets.get("private_key", "")
        if not service_account or not private_key:
            return False
        key_data = json.dumps({
            "type":                        "service_account",
            "private_key":                 private_key,
            "client_email":                service_account,
            "token_uri":                   "https://oauth2.googleapis.com/token",
        })
        credentials = ee.ServiceAccountCredentials(service_account, key_data=key_data)
        project = _resolve_project()
        if project:
            ee.Initialize(credentials, project=project)
        else:
            ee.Initialize(credentials)
        return True
    except Exception:
        return False


def _resolve_project() -> str | None:
    """Return the GEE project ID from env or Streamlit secrets."""
    project = os.environ.get("EARTHENGINE_PROJECT")
    if not project:
        try:
            project = (
                st.secrets.get("EARTHENGINE_PROJECT", None)
                or st.secrets.get("earthengine_project", None)
            )
        except Exception:
            project = None
    return project or None


def _try_init(project: str | None) -> None:
    """Call ee.Initialize with or without an explicit project."""
    if project:
        ee.Initialize(project=project)
    else:
        ee.Initialize()
