# =============================================================================
# EcoGuard AI - IBM watsonx.ai Client Utility
# =============================================================================
# Provides a single, lazily-initialised ModelInference client backed by
# IBM watsonx.ai.  Credentials are read ONLY from Streamlit secrets:
#
#   st.secrets["WATSONX_APIKEY"]       — IBM Cloud API key
#   st.secrets["WATSONX_PROJECT_ID"]   — watsonx.ai project ID
#   st.secrets["WATSONX_URL"]          — regional endpoint
#                                        e.g. https://eu-de.ml.cloud.ibm.com
#
# Model : ibm/granite-4-h-small
#
# Public API (used by modules/climate_chatbot.py):
#   get_model()          → ModelInference | None
#   test_connection()    → (success: bool, message: str)
#   chat(messages)       → (text: str | None, error: str | None)
#
# SECURITY:
#   - No credential values are ever printed, logged, or surfaced in the UI.
#   - The module stores a module-level _model cache so Streamlit reruns reuse
#     the same initialised client without re-authenticating every time.
# =============================================================================

from __future__ import annotations

import logging
from typing import Optional

import streamlit as st

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_MODEL_ID = "ibm/granite-4-h-small"

_CHAT_PARAMS = {
    "max_completion_tokens": 512,
    "temperature": 0.7,
    "top_p": 0.9,
}

# ---------------------------------------------------------------------------
# Module-level cache
# ---------------------------------------------------------------------------
# _model_cache holds the ModelInference instance once successfully built.
# None means "not yet successfully built" — a failed attempt does NOT set
# this, so the next Streamlit rerun will retry (important because Streamlit
# may import this module before secrets are fully available on first load).
_model_cache: Optional[object] = None


# ---------------------------------------------------------------------------
# Credential reader
# ---------------------------------------------------------------------------

def _read_secrets() -> tuple[str, str, str] | None:
    """
    Read watsonx credentials from Streamlit secrets.

    Returns (api_key, project_id, url) or None if any required key is missing.
    Never logs or exposes the actual values.
    """
    try:
        api_key    = st.secrets["WATSONX_APIKEY"]
        project_id = st.secrets["WATSONX_PROJECT_ID"]
        url        = st.secrets["WATSONX_URL"]
        if not api_key or not project_id or not url:
            return None
        return api_key, project_id, url
    except Exception:
        # Catches KeyError, FileNotFoundError, and any Streamlit secrets error
        return None


# ---------------------------------------------------------------------------
# Model factory
# ---------------------------------------------------------------------------

def get_model():
    """
    Return a cached ModelInference instance.

    - On the first successful build the instance is cached and reused.
    - If credentials are unavailable OR initialisation fails, None is returned
      and the cache is NOT updated — the next call will retry.  This handles
      the case where Streamlit imports the module before secrets.toml is
      readable (which can happen on the very first startup rerun).
    """
    global _model_cache
    if _model_cache is not None:
        return _model_cache

    creds = _read_secrets()
    if creds is None:
        logger.warning(
            "EcoGuard AI: IBM watsonx credentials not found in Streamlit secrets. "
            "Expected keys: WATSONX_APIKEY, WATSONX_PROJECT_ID, WATSONX_URL"
        )
        return None   # do NOT cache — retry on next call

    api_key, project_id, url = creds
    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        credentials = Credentials(url=url, api_key=api_key)
        model = ModelInference(
            model_id=_MODEL_ID,
            credentials=credentials,
            project_id=project_id,
            params=_CHAT_PARAMS,
        )
        _model_cache = model   # only cache on success
        logger.info(
            "EcoGuard AI: IBM watsonx.ai ModelInference initialised (model=%s)", _MODEL_ID
        )
        return model

    except Exception as exc:
        logger.warning(
            "EcoGuard AI: Failed to initialise IBM watsonx.ai client. "
            "Error type: %s", type(exc).__name__
        )
        return None   # do NOT cache — retry on next call


# ---------------------------------------------------------------------------
# Connection test — sends a minimal real request to verify the service works
# ---------------------------------------------------------------------------

def test_connection() -> tuple[bool, str]:
    """
    Send a tiny test message to IBM Granite to verify the connection works.

    Returns:
        (True,  "Connected to IBM watsonx.ai · Granite")   on success
        (False, "<safe error description>")                  on failure

    Never exposes credential values in the returned message.
    """
    model = get_model()
    if model is None:
        return False, (
            "Credentials not found. Add WATSONX_APIKEY, WATSONX_PROJECT_ID, "
            "and WATSONX_URL to .streamlit/secrets.toml."
        )

    try:
        test_messages = [
            {"role": "user", "content": "Reply with exactly: EcoGuard AI connection successful."},
        ]
        response = model.chat(messages=test_messages)
        text = response["choices"][0]["message"]["content"].strip()
        logger.info("EcoGuard AI: Connection test succeeded. Response length: %d chars", len(text))
        return True, f"Connected to IBM watsonx.ai · {_MODEL_ID}"

    except Exception as exc:
        err_type = type(exc).__name__
        err_str  = str(exc).lower()
        if any(kw in err_str for kw in ["unauthorized", "forbidden", "401", "403", "invalid apikey", "apikey"]):
            msg = "Authentication failed — check WATSONX_APIKEY and WATSONX_PROJECT_ID."
        elif any(kw in err_str for kw in ["timeout", "connection", "network", "unreachable"]):
            msg = "Network error — IBM watsonx.ai service could not be reached."
        else:
            msg = f"Service error ({err_type}). IBM watsonx.ai may be temporarily unavailable."
        logger.warning("EcoGuard AI: Connection test failed. Error type: %s", err_type)
        return False, msg


# ---------------------------------------------------------------------------
# Chat — send a full message list and return the generated text
# ---------------------------------------------------------------------------

def chat(messages: list[dict]) -> tuple[str | None, str | None]:
    """
    Send *messages* to IBM Granite and return (text, None) on success,
    or (None, error_message) on failure.

    Args:
        messages: list of {"role": "system"|"user"|"assistant", "content": str}

    Returns:
        (text, None)   — generated assistant reply
        (None, error)  — safe error string (no credentials exposed)
    """
    model = get_model()
    if model is None:
        return None, (
            "⚠️ EcoGuard AI could not connect to IBM watsonx.ai. "
            "Please check the WATSONX_APIKEY, WATSONX_PROJECT_ID, and WATSONX_URL "
            "in .streamlit/secrets.toml."
        )

    try:
        response = model.chat(messages=messages)
        text = response["choices"][0]["message"]["content"].strip()
        return text, None

    except Exception as exc:
        err_type = type(exc).__name__
        err_str  = str(exc).lower()
        logger.warning("EcoGuard AI: chat() failed. Error type: %s", err_type)

        if any(kw in err_str for kw in ["unauthorized", "forbidden", "401", "403", "apikey"]):
            return None, (
                "⚠️ EcoGuard AI could not connect to IBM watsonx.ai. "
                "Please check the WATSONX_APIKEY, WATSONX_PROJECT_ID, and WATSONX_URL "
                "in .streamlit/secrets.toml."
            )
        if any(kw in err_str for kw in ["timeout", "connection", "network"]):
            return None, (
                "⚠️ EcoGuard AI is temporarily unable to reach IBM watsonx.ai. "
                "Please try again in a moment."
            )
        return None, (
            "⚠️ EcoGuard AI is temporarily unable to reach IBM watsonx.ai. "
            "Please try again in a moment."
        )
