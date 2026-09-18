# =============================================================================
# EcoGuard AI - Weather Data Utilities
# Provides location geocoding and real-time / historical weather retrieval
# via the Open-Meteo free API (no API key required).
#
# Used by: Climate Risks (heatwave, drought, wildfire sections)
# The Flood Risk section has its own inline implementation — do not touch it.
# =============================================================================

import requests


# ---------------------------------------------------------------------------
# Geocoding
# ---------------------------------------------------------------------------

def geocode_location(location: str) -> dict | None:
    """
    Resolve a place name to coordinates using the Open-Meteo Geocoding API.

    Returns a dict with keys:
        name      (str)   – resolved place name
        country   (str)   – country name
        latitude  (float) – decimal latitude
        longitude (float) – decimal longitude

    Returns None if the location is not found or on network error.
    """
    try:
        resp = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": location, "count": 1, "language": "en", "format": "json"},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        if "results" not in data or not data["results"]:
            return None
        place = data["results"][0]
        return {
            "name":      place.get("name", location),
            "country":   place.get("country", ""),
            "latitude":  place["latitude"],
            "longitude": place["longitude"],
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Current weather conditions
# ---------------------------------------------------------------------------

def get_current_weather(lat: float, lon: float) -> dict | None:
    """
    Fetch current weather observations for the given coordinates.

    Returns a dict with keys:
        temperature       (float) – air temperature in °C
        apparent_temp     (float) – feels-like temperature in °C
        humidity          (int)   – relative humidity in %
        precipitation     (float) – precipitation in mm (last hour)
        wind_speed        (float) – wind speed in km/h

    Returns None on any network or parse error.
    """
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude":  lat,
                "longitude": lon,
                "current":   (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "precipitation,"
                    "wind_speed_10m"
                ),
                "timezone": "auto",
            },
            timeout=20,
        )
        resp.raise_for_status()
        c = resp.json().get("current", {})
        return {
            "temperature":   c.get("temperature_2m"),
            "apparent_temp": c.get("apparent_temperature"),
            "humidity":      c.get("relative_humidity_2m"),
            "precipitation": c.get("precipitation"),
            "wind_speed":    c.get("wind_speed_10m"),
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Recent daily weather (past N days)
# ---------------------------------------------------------------------------

def get_recent_daily_weather(lat: float, lon: float, past_days: int = 90) -> dict | None:
    """
    Fetch daily weather summaries for the past `past_days` days.

    Returns a dict with keys (all lists of equal length):
        dates             (list[str])   – ISO-8601 date strings
        precipitation_sum (list[float]) – daily precipitation total in mm
        temp_max          (list[float]) – daily maximum temperature in °C
        humidity_max      (list[float]) – daily maximum relative humidity in %
        wind_speed_max    (list[float]) – daily maximum wind speed in km/h

    Returns None on any network or parse error.
    """
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude":  lat,
                "longitude": lon,
                "daily": (
                    "precipitation_sum,"
                    "temperature_2m_max,"
                    "relative_humidity_2m_max,"
                    "wind_speed_10m_max"
                ),
                "past_days":      past_days,
                "forecast_days":  1,
                "timezone":       "auto",
            },
            timeout=20,
        )
        resp.raise_for_status()
        d = resp.json().get("daily", {})
        return {
            "dates":             d.get("time", []),
            "precipitation_sum": d.get("precipitation_sum", []),
            "temp_max":          d.get("temperature_2m_max", []),
            "humidity_max":      d.get("relative_humidity_2m_max", []),
            "wind_speed_max":    d.get("wind_speed_10m_max", []),
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Risk scoring helpers (shared by home.py and climate_risks.py)
# ---------------------------------------------------------------------------

def flood_risk_score(rainfall_24h: float) -> tuple[int, str]:
    """
    Derive a flood risk score from 24-hour accumulated precipitation.

    Returns (score 0–100, risk level string).
    Mirrors the inline logic in show_flood() in pages/climate_risks.py.
    """
    if rainfall_24h < 25:
        return 15, "LOW"
    elif rainfall_24h < 50:
        return 35, "MODERATE"
    elif rainfall_24h < 100:
        return 60, "HIGH"
    else:
        return 85, "VERY HIGH"


def heatwave_risk_score(temp_c: float, humidity_pct: float) -> tuple[int, str]:
    """
    Simple Heat Index–inspired scoring.
    Returns (score 0–100, risk level string).
    Mirrors _heatwave_score() in pages/climate_risks.py.
    """
    humidity_factor = max(0, (humidity_pct - 40) / 60)
    base = (temp_c - 20) / 25
    score = int(min(100, max(0, (base * 0.7 + humidity_factor * 0.3) * 100)))
    if score >= 75:
        level = "VERY HIGH"
    elif score >= 55:
        level = "HIGH"
    elif score >= 35:
        level = "MODERATE"
    else:
        level = "LOW"
    return score, level


def drought_risk_score(precip_30d: float, avg_max_temp: float) -> tuple[int, str]:
    """
    Returns (score 0–100, risk level string).
    Mirrors _drought_score() in pages/climate_risks.py.
    """
    precip_factor = max(0, 1 - precip_30d / 150)
    temp_factor   = max(0, min(1, (avg_max_temp - 15) / 30))
    score = int(min(100, max(0, (precip_factor * 0.65 + temp_factor * 0.35) * 100)))
    if score >= 70:
        level = "VERY HIGH"
    elif score >= 50:
        level = "HIGH"
    elif score >= 30:
        level = "MODERATE"
    else:
        level = "LOW"
    return score, level


def wildfire_risk_score(
    avg_max_temp: float, avg_humidity: float, precip_30d: float
) -> tuple[int, str]:
    """
    Returns (score 0–100, risk level string).
    Mirrors _wildfire_score() in pages/climate_risks.py.
    """
    temp_factor     = max(0, min(1, (avg_max_temp - 15) / 30))
    humidity_factor = max(0, 1 - avg_humidity / 80)
    precip_factor   = max(0, 1 - precip_30d / 100)
    score = int(min(100, max(0, (
        temp_factor * 0.35 + humidity_factor * 0.40 + precip_factor * 0.25
    ) * 100)))
    if score >= 70:
        level = "VERY HIGH"
    elif score >= 50:
        level = "HIGH"
    elif score >= 30:
        level = "MODERATE"
    else:
        level = "LOW"
    return score, level
