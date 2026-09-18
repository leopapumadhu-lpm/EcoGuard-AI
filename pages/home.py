from __future__ import annotations

import math
from typing import Any

import pandas as pd
import requests
import streamlit as st

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


# =============================================================================
# EcoGuard AI - HOME PAGE
# =============================================================================

WORLD_GEOJSON_URL = (
    "https://raw.githubusercontent.com/datasets/geo-countries/main/data/countries.geojson"
)

INDIA_GEOJSON_URL = (
    "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/"
    "releaseData/gbOpen/IND/ADM1/"
    "geoBoundaries-IND-ADM1_simplified.geojson"
)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

MAP_CACHE_TTL = 900
REQUEST_TIMEOUT = 20

DEFAULT_COUNTRY_ISO3 = "IND"


# =============================================================================
# INDIA COORDINATES
# =============================================================================

INDIA_STATE_COORDINATES = {
    "Andaman and Nicobar Islands": (11.7401, 92.6586),
    "Andhra Pradesh": (15.9129, 79.7400),
    "Arunachal Pradesh": (28.2180, 94.7278),
    "Assam": (26.2006, 92.9376),
    "Bihar": (25.0961, 85.3131),
    "Chandigarh": (30.7333, 76.7794),
    "Chhattisgarh": (21.2787, 81.8661),
    "Dadra and Nagar Haveli and Daman and Diu": (20.1809, 73.0169),
    "Delhi": (28.7041, 77.1025),
    "Goa": (15.2993, 74.1240),
    "Gujarat": (22.2587, 71.1924),
    "Haryana": (29.0588, 76.0856),
    "Himachal Pradesh": (31.1048, 77.1734),
    "Jammu and Kashmir": (33.7782, 76.5762),
    "Jharkhand": (23.6102, 85.2799),
    "Karnataka": (15.3173, 75.7139),
    "Kerala": (10.8505, 76.2711),
    "Ladakh": (34.1526, 77.5771),
    "Lakshadweep": (10.5667, 72.6417),
    "Madhya Pradesh": (22.9734, 78.6569),
    "Maharashtra": (19.7515, 75.7139),
    "Manipur": (24.6637, 93.9063),
    "Meghalaya": (25.4670, 91.3662),
    "Mizoram": (23.1645, 92.9376),
    "Nagaland": (26.1584, 94.5624),
    "Odisha": (20.9517, 85.0985),
    "Puducherry": (11.9416, 79.8083),
    "Punjab": (31.1471, 75.3412),
    "Rajasthan": (27.0238, 74.2179),
    "Sikkim": (27.5330, 88.5122),
    "Tamil Nadu": (11.1271, 78.6569),
    "Telangana": (18.1124, 79.0193),
    "Tripura": (23.9408, 91.9882),
    "Uttar Pradesh": (26.8467, 80.9462),
    "Uttarakhand": (30.0668, 79.0193),
    "West Bengal": (22.9868, 87.8550),
}


# =============================================================================
# COUNTRY COORDINATES
# =============================================================================

COUNTRY_COORDINATE_FALLBACKS = {
    "IND": (20.5937, 78.9629),
    "USA": (37.0902, -95.7129),
    "CAN": (56.1304, -106.3468),
    "MEX": (23.6345, -102.5528),
    "BRA": (-14.2350, -51.9253),
    "ARG": (-38.4161, -63.6167),
    "CHL": (-35.6751, -71.5430),
    "PER": (-9.1900, -75.0152),
    "COL": (4.5709, -74.2973),
    "GBR": (55.3781, -3.4360),
    "FRA": (46.2276, 2.2137),
    "DEU": (51.1657, 10.4515),
    "ITA": (41.8719, 12.5674),
    "ESP": (40.4637, -3.7492),
    "PRT": (39.3999, -8.2245),
    "NLD": (52.1326, 5.2913),
    "BEL": (50.5039, 4.4699),
    "CHE": (46.8182, 8.2275),
    "AUT": (47.5162, 14.5501),
    "POL": (51.9194, 19.1451),
    "NOR": (60.4720, 8.4689),
    "SWE": (60.1282, 18.6435),
    "FIN": (61.9241, 25.7482),
    "DNK": (56.2639, 9.5017),
    "IRL": (53.1424, -7.6921),
    "ISL": (64.9631, -19.0208),
    "RUS": (61.5240, 105.3188),
    "UKR": (48.3794, 31.1656),
    "ROU": (45.9432, 24.9668),
    "GRC": (39.0742, 21.8243),
    "TUR": (38.9637, 35.2433),
    "SAU": (23.8859, 45.0792),
    "ARE": (23.4241, 53.8478),
    "QAT": (25.3548, 51.1839),
    "ISR": (31.0461, 34.8516),
    "EGY": (26.8206, 30.8025),
    "ZAF": (-30.5595, 22.9375),
    "NGA": (9.0820, 8.6753),
    "KEN": (-0.0236, 37.9062),
    "ETH": (9.1450, 40.4897),
    "GHA": (7.9465, -1.0232),
    "MAR": (31.7917, -7.0926),
    "DZA": (28.0339, 1.6596),
    "CHN": (35.8617, 104.1954),
    "JPN": (36.2048, 138.2529),
    "KOR": (35.9078, 127.7669),
    "PRK": (40.3399, 127.5101),
    "MNG": (46.8625, 103.8467),
    "THA": (15.8700, 100.9925),
    "VNM": (14.0583, 108.2772),
    "MYS": (4.2105, 101.9758),
    "SGP": (1.3521, 103.8198),
    "IDN": (-0.7893, 113.9213),
    "PHL": (12.8797, 121.7740),
    "AUS": (-25.2744, 133.7751),
    "NZL": (-40.9006, 174.8860),
    "PAK": (30.3753, 69.3451),
    "BGD": (23.6850, 90.3563),
    "LKA": (7.8731, 80.7718),
    "NPL": (28.3949, 84.1240),
    "AFG": (33.9391, 67.7100),
    "IRN": (32.4279, 53.6880),
    "IRQ": (33.2232, 43.6793),
    "KAZ": (48.0196, 66.9237),
    "UZB": (41.3775, 64.5853),
    "TKM": (38.9697, 59.5563),
    "GEO": (42.3154, 43.3569),
    "ARM": (40.0691, 45.0382),
    "AZE": (40.1431, 47.5769),
}


# =============================================================================
# HELPERS
# =============================================================================

def _safe_float(
    value: Any,
    default: float | None = None,
) -> float | None:

    try:
        if value is None:
            return default

        number = float(value)

        if math.isnan(number) or math.isinf(number):
            return default

        return number

    except (TypeError, ValueError):
        return default


def _normalise_text(
    value: Any,
) -> str:

    if value is None:
        return ""

    return " ".join(
        str(value).strip().split()
    )


def _normalise_iso3(
    value: Any,
) -> str:

    value = _normalise_text(
        value
    ).upper()

    if value in {
        "",
        "NAN",
        "NONE",
        "NULL",
        "-99",
    }:
        return ""

    if len(value) != 3:
        return ""

    if not value.isalpha():
        return ""

    return value


def _valid_coordinates(
    latitude: Any,
    longitude: Any,
) -> bool:

    lat = _safe_float(latitude)
    lon = _safe_float(longitude)

    if lat is None or lon is None:
        return False

    return (
        -90 <= lat <= 90
        and -180 <= lon <= 180
    )


# =============================================================================
# GEOJSON
# =============================================================================

@st.cache_data(
    ttl=MAP_CACHE_TTL,
    show_spinner=False,
)
def load_world_geojson() -> dict:

    response = requests.get(
        WORLD_GEOJSON_URL,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    return response.json()


@st.cache_data(
    ttl=MAP_CACHE_TTL,
    show_spinner=False,
)
def load_india_geojson() -> dict:

    response = requests.get(
        INDIA_GEOJSON_URL,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    return response.json()


def _find_property(
    properties: dict,
    candidates: list[str],
) -> str | None:

    if not isinstance(
        properties,
        dict,
    ):
        return None

    lower_map = {
        str(key).strip().lower(): key
        for key in properties.keys()
    }

    for candidate in candidates:

        found = lower_map.get(
            candidate.strip().lower()
        )

        if found is not None:
            return found

    return None


def detect_geojson_iso_property(
    geojson: dict,
) -> str | None:

    features = geojson.get(
        "features",
        [],
    )

    if not features:
        return None

    properties = (
        features[0].get(
            "properties",
            {},
        )
        or {}
    )

    candidates = [
        "ISO3166-1-Alpha-3",
        "ISO_A3",
        "ADM0_A3",
        "ISO3",
        "iso_a3",
        "iso3",
    ]

    found = _find_property(
        properties,
        candidates,
    )

    if found:
        return found

    for key in properties.keys():

        key_text = (
            str(key)
            .strip()
            .lower()
        )

        if (
            "iso3166" in key_text
            and "alpha-3" in key_text
        ):
            return key

        if key_text in {
            "iso_a3",
            "adm0_a3",
            "iso3",
        }:
            return key

    return None


# =============================================================================
# COUNTRY EXTRACTION
# =============================================================================

def extract_country_records(
    geojson: dict,
) -> list[dict]:

    features = geojson.get(
        "features",
        [],
    )

    if not features:
        return []

    iso_property = (
        detect_geojson_iso_property(
            geojson
        )
    )

    records = []

    for feature in features:

        properties = (
            feature.get(
                "properties",
                {},
            )
            or {}
        )

        iso3 = ""

        if iso_property:

            iso3 = _normalise_iso3(
                properties.get(
                    iso_property
                )
            )

        if not iso3:

            key = _find_property(
                properties,
                [
                    "ISO3166-1-Alpha-3",
                    "ISO_A3",
                    "ADM0_A3",
                    "ISO3",
                    "iso_a3",
                    "iso3",
                ],
            )

            if key:

                iso3 = _normalise_iso3(
                    properties.get(key)
                )

        if not iso3:
            continue

        name_key = _find_property(
            properties,
            [
                "name",
                "NAME",
                "ADMIN",
                "NAME_EN",
                "name_en",
            ],
        )

        if name_key:

            name = _normalise_text(
                properties.get(
                    name_key
                )
            )

        else:

            name = iso3

        if not name:
            name = iso3

        records.append(
            {
                "iso3": iso3,
                "name": name,
                "feature": feature,
            }
        )

    unique = {}

    for record in records:
        unique[
            record["iso3"]
        ] = record

    return list(
        unique.values()
    )


# =============================================================================
# COORDINATES
# =============================================================================

def _extract_coordinates(
    coords: Any,
) -> list[tuple[float, float]]:

    points = []

    if not isinstance(
        coords,
        (list, tuple),
    ):
        return points

    if (
        len(coords) >= 2
        and isinstance(
            coords[0],
            (int, float),
        )
        and isinstance(
            coords[1],
            (int, float),
        )
    ):

        lon = _safe_float(
            coords[0]
        )

        lat = _safe_float(
            coords[1]
        )

        if (
            lon is not None
            and lat is not None
            and _valid_coordinates(
                lat,
                lon,
            )
        ):

            points.append(
                (lat, lon)
            )

        return points

    for item in coords:

        points.extend(
            _extract_coordinates(
                item
            )
        )

    return points


def _safe_centroid(
    feature: dict,
) -> tuple[float, float] | None:

    geometry = (
        feature.get(
            "geometry",
            {},
        )
        or {}
    )

    coords = geometry.get(
        "coordinates"
    )

    points = _extract_coordinates(
        coords
    )

    if not points:
        return None

    lats = [
        point[0]
        for point in points
    ]

    lons = [
        point[1]
        for point in points
    ]

    return (
        sum(lats) / len(lats),
        sum(lons) / len(lons),
    )


def _bbox_center(
    feature: dict,
) -> tuple[float, float] | None:

    geometry = (
        feature.get(
            "geometry",
            {},
        )
        or {}
    )

    bbox = geometry.get(
        "bbox"
    )

    if (
        isinstance(bbox, list)
        and len(bbox) >= 4
    ):

        min_lon = _safe_float(
            bbox[0]
        )

        min_lat = _safe_float(
            bbox[1]
        )

        max_lon = _safe_float(
            bbox[2]
        )

        max_lat = _safe_float(
            bbox[3]
        )

        if all(
            value is not None
            for value in [
                min_lon,
                min_lat,
                max_lon,
                max_lat,
            ]
        ):

            return (
                (min_lat + max_lat) / 2,
                (min_lon + max_lon) / 2,
            )

    return None


def get_country_coordinates(
    iso3: str,
    feature: dict | None = None,
) -> tuple[float, float] | None:

    if feature:

        centroid = _safe_centroid(
            feature
        )

        if centroid:
            return centroid

        bbox = _bbox_center(
            feature
        )

        if bbox:
            return bbox

    return COUNTRY_COORDINATE_FALLBACKS.get(
        iso3.upper()
    )


# =============================================================================
# WEATHER
# =============================================================================

def _empty_weather_record() -> dict:

    return {
        "temperature": None,
        "rainfall": None,
        "humidity": None,
        "wind_speed": None,
    }


@st.cache_data(
    ttl=900,
    show_spinner=False,
)
def fetch_weather(
    latitude: float,
    longitude: float,
) -> dict:

    if not _valid_coordinates(
        latitude,
        longitude,
    ):
        return _empty_weather_record()

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "rain,"
            "wind_speed_10m"
        ),
        "timezone": "auto",
    }

    try:

        response = requests.get(
            OPEN_METEO_URL,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        current = (
            data.get(
                "current",
                {},
            )
            or {}
        )

        return {
            "temperature": _safe_float(
                current.get(
                    "temperature_2m"
                )
            ),
            "rainfall": _safe_float(
                current.get(
                    "rain"
                )
            ),
            "humidity": _safe_float(
                current.get(
                    "relative_humidity_2m"
                )
            ),
            "wind_speed": _safe_float(
                current.get(
                    "wind_speed_10m"
                )
            ),
        }

    except Exception:
        return _empty_weather_record()


# =============================================================================
# RISKS
# =============================================================================

def calculate_heat_risk(
    temperature: float | None,
) -> str:

    if temperature is None:
        return "Unknown"

    if temperature >= 40:
        return "High"

    if temperature >= 35:
        return "Moderate"

    return "Low"


def calculate_flood_risk(
    rainfall: float | None,
) -> str:

    if rainfall is None:
        return "Unknown"

    if rainfall >= 50:
        return "High"

    if rainfall >= 20:
        return "Moderate"

    return "Low"


def calculate_environmental_status(
    temperature: float | None,
    rainfall: float | None,
) -> str:

    if (
        temperature is None
        and rainfall is None
    ):
        return "Unknown"

    heat = calculate_heat_risk(
        temperature
    )

    flood = calculate_flood_risk(
        rainfall
    )

    if (
        heat == "High"
        or flood == "High"
    ):
        return "At Risk"

    if (
        heat == "Moderate"
        or flood == "Moderate"
    ):
        return "Monitor"

    return "Stable"


def build_alert(
    heat_risk: str,
    flood_risk: str,
) -> str:

    if heat_risk == "High":
        return "Heat alert"

    if flood_risk == "High":
        return "Heavy rain / flood alert"

    if (
        heat_risk == "Moderate"
        or flood_risk == "Moderate"
    ):
        return "Monitor conditions"

    return "No major alert"


# =============================================================================
# GLOBAL DATA
# =============================================================================

@st.cache_data(
    ttl=MAP_CACHE_TTL,
    show_spinner=False,
)
def build_global_dataframe(
    geojson: dict,
) -> pd.DataFrame:

    records = extract_country_records(
        geojson
    )

    rows = []

    for record in records:

        iso3 = record["iso3"]
        name = record["name"]
        feature = record["feature"]

        coordinates = (
            get_country_coordinates(
                iso3,
                feature,
            )
        )

        if coordinates:

            latitude, longitude = coordinates

            weather = fetch_weather(
                latitude,
                longitude,
            )

        else:

            latitude = None
            longitude = None

            weather = (
                _empty_weather_record()
            )

        temperature = weather[
            "temperature"
        ]

        rainfall = weather[
            "rainfall"
        ]

        humidity = weather[
            "humidity"
        ]

        wind_speed = weather[
            "wind_speed"
        ]

        heat_risk = calculate_heat_risk(
            temperature
        )

        flood_risk = calculate_flood_risk(
            rainfall
        )

        environment = (
            calculate_environmental_status(
                temperature,
                rainfall,
            )
        )

        alert = build_alert(
            heat_risk,
            flood_risk,
        )

        rows.append(
            {
                "iso3": iso3,
                "name": name,
                "latitude": latitude,
                "longitude": longitude,
                "temperature": temperature,
                "rainfall": rainfall,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "heat_risk": heat_risk,
                "flood_risk": flood_risk,
                "environmental_status": environment,
                "alert": alert,
            }
        )

    return pd.DataFrame(rows)


# =============================================================================
# INDIA STATE DATA
# =============================================================================

def _normalise_india_state_name(
    name: str,
) -> str:

    mapping = {
        "NCT of Delhi": "Delhi",
        "Orissa": "Odisha",
        "Pondicherry": "Puducherry",
        "Uttaranchal": "Uttarakhand",
        "Jammu & Kashmir": "Jammu and Kashmir",
    }

    return mapping.get(
        name,
        name,
    )


def _extract_india_state_records(
    geojson: dict,
) -> list[dict]:

    features = geojson.get(
        "features",
        [],
    )

    records = []

    for feature in features:

        properties = (
            feature.get(
                "properties",
                {},
            )
            or {}
        )

        name_key = _find_property(
            properties,
            [
                "shapeName",
                "shape_name",
                "name",
                "NAME_1",
                "NAME",
                "admin1Name",
                "state",
            ],
        )

        if not name_key:
            continue

        name = _normalise_text(
            properties.get(
                name_key
            )
        )

        if not name:
            continue

        name = _normalise_india_state_name(
            name
        )

        records.append(
            {
                "state": name,
                "feature": feature,
            }
        )

    unique = {}

    for record in records:
        unique[
            record["state"]
        ] = record

    return list(
        unique.values()
    )


@st.cache_data(
    ttl=MAP_CACHE_TTL,
    show_spinner=False,
)
def build_india_state_dataframe(
    geojson: dict,
) -> pd.DataFrame:

    records = (
        _extract_india_state_records(
            geojson
        )
    )

    rows = []

    for record in records:

        state = record["state"]

        coordinates = (
            INDIA_STATE_COORDINATES.get(
                state
            )
        )

        if coordinates:

            latitude, longitude = coordinates

            weather = fetch_weather(
                latitude,
                longitude,
            )

        else:

            latitude = None
            longitude = None

            weather = (
                _empty_weather_record()
            )

        temperature = weather[
            "temperature"
        ]

        rainfall = weather[
            "rainfall"
        ]

        humidity = weather[
            "humidity"
        ]

        wind_speed = weather[
            "wind_speed"
        ]

        heat_risk = calculate_heat_risk(
            temperature
        )

        flood_risk = calculate_flood_risk(
            rainfall
        )

        environment = (
            calculate_environmental_status(
                temperature,
                rainfall,
            )
        )

        alert = build_alert(
            heat_risk,
            flood_risk,
        )

        rows.append(
            {
                "state": state,
                "latitude": latitude,
                "longitude": longitude,
                "temperature": temperature,
                "rainfall": rainfall,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "heat_risk": heat_risk,
                "flood_risk": flood_risk,
                "environmental_status": environment,
                "alert": alert,
            }
        )

    return pd.DataFrame(rows)


# =============================================================================
# DISPLAY
# =============================================================================

def display_value(
    value: Any,
    suffix: str = "",
) -> str:

    if value is None:
        return "N/A"

    try:

        number = float(value)

        if math.isnan(number):
            return "N/A"

        return f"{number:.1f}{suffix}"

    except (
        TypeError,
        ValueError,
    ):
        return "N/A"


# =============================================================================
# WORLD MAP
# =============================================================================

def render_world_map(
    df: pd.DataFrame,
) -> None:

    if not PLOTLY_AVAILABLE:

        st.error(
            "Plotly is not installed."
        )

        return

    if df.empty:

        st.warning(
            "No country climate data available."
        )

        return

    try:

        geojson = (
            load_world_geojson()
        )

    except Exception as exc:

        st.error(
            f"Unable to load world map: {exc}"
        )

        return

    iso_property = (
        detect_geojson_iso_property(
            geojson
        )
    )

    if not iso_property:

        st.error(
            "Could not detect the country ISO3 property."
        )

        return

    map_df = df.copy()

    map_df["iso3"] = (
        map_df["iso3"]
        .astype(str)
        .str.upper()
    )

    map_df["risk_score"] = (
        map_df["heat_risk"]
        .map(
            {
                "Low": 1,
                "Moderate": 2,
                "High": 3,
            }
        )
        .fillna(0)
    )

    map_df["temperature_display"] = (
        map_df["temperature"].apply(
            lambda x: display_value(
                x,
                " °C",
            )
        )
    )

    map_df["rainfall_display"] = (
        map_df["rainfall"].apply(
            lambda x: display_value(
                x,
                " mm",
            )
        )
    )

    map_df["humidity_display"] = (
        map_df["humidity"].apply(
            lambda x: display_value(
                x,
                " %",
            )
        )
    )

    map_df["wind_display"] = (
        map_df["wind_speed"].apply(
            lambda x: display_value(
                x,
                " km/h",
            )
        )
    )

    map_df["map_iso3"] = map_df[
        "iso3"
    ]

    fig = px.choropleth(
        map_df,
        geojson=geojson,
        locations="map_iso3",
        featureidkey=(
            f"properties.{iso_property}"
        ),
        color="risk_score",
        color_continuous_scale=[
            [0.00, "#E5E7EB"],
            [0.01, "#E5E7EB"],
            [0.33, "#86EFAC"],
            [0.66, "#FCD34D"],
            [1.00, "#EF4444"],
        ],
        range_color=(0, 3),
        custom_data=[
            "iso3",
            "name",
            "temperature_display",
            "rainfall_display",
            "humidity_display",
            "wind_display",
            "flood_risk",
            "heat_risk",
            "environmental_status",
            "alert",
        ],
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[1]}</b><br>"
            "🌡️ Temperature: %{customdata[2]}<br>"
            "🌧️ Rainfall: %{customdata[3]}<br>"
            "💧 Humidity: %{customdata[4]}<br>"
            "💨 Wind: %{customdata[5]}<br>"
            "🌊 Flood Risk: %{customdata[6]}<br>"
            "🔥 Heat Risk: %{customdata[7]}<br>"
            "🌱 Environment: %{customdata[8]}<br>"
            "⚠️ Alert: %{customdata[9]}"
            "<extra></extra>"
        ),
        marker_line_width=0.5,
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
    )

    fig.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0,
        ),
        height=520,
        coloraxis_colorbar=dict(
            title="Risk",
            tickvals=[
                0,
                1,
                2,
                3,
            ],
            ticktext=[
                "No data",
                "Low",
                "Moderate",
                "High",
            ],
        ),
    )

    # IMPORTANT:
    # Unique key prevents DuplicateElementKey.
    event = st.plotly_chart(
        fig,
        width="stretch",
        key=f"ecoguard_world_map_clickable_{id(fig)}",
        on_select="rerun",
        selection_mode="points",
    )

    # -------------------------------------------------------------------------
    # COUNTRY CLICK
    # -------------------------------------------------------------------------

    try:

        points = event.selection.points

        if points:

            point = points[0]

            customdata = point.get(
                "customdata"
            )

            if customdata:

                clicked_iso3 = str(
                    customdata[0]
                ).upper()

                valid_iso3 = set(
                    map_df["iso3"]
                    .astype(str)
                    .str.upper()
                )

                if clicked_iso3 in valid_iso3:

                    st.session_state[
                        "home_selected_country_iso3"
                    ] = clicked_iso3

                    # Do NOT modify the selectbox key here.
                    # We only save the selected country.
                    st.session_state[
                        "home_map_clicked_country"
                    ] = clicked_iso3

                    st.rerun()

    except Exception:
        pass


# =============================================================================
# INDIA MAP
# =============================================================================

def render_india_map(
    df: pd.DataFrame,
) -> None:

    if not PLOTLY_AVAILABLE:

        st.error(
            "Plotly is not installed."
        )

        return

    if df.empty:

        st.warning(
            "No India state climate data available."
        )

        return

    try:

        geojson = (
            load_india_geojson()
        )

    except Exception as exc:

        st.error(
            f"Unable to load India state map: {exc}"
        )

        return

    features = geojson.get(
        "features",
        [],
    )

    if not features:

        st.error(
            "India GeoJSON contains no features."
        )

        return

    properties = (
        features[0].get(
            "properties",
            {},
        )
        or {}
    )

    state_property = _find_property(
        properties,
        [
            "shapeName",
            "shape_name",
            "name",
            "NAME_1",
            "NAME",
            "admin1Name",
            "state",
        ],
    )

    if not state_property:

        st.error(
            "Could not detect the India state property."
        )

        return

    map_df = df.copy()

    map_df["risk_score"] = (
        map_df["heat_risk"]
        .map(
            {
                "Low": 1,
                "Moderate": 2,
                "High": 3,
            }
        )
        .fillna(0)
    )

    map_df["temperature_display"] = (
        map_df["temperature"].apply(
            lambda x: display_value(
                x,
                " °C",
            )
        )
    )

    map_df["rainfall_display"] = (
        map_df["rainfall"].apply(
            lambda x: display_value(
                x,
                " mm",
            )
        )
    )

    map_df["humidity_display"] = (
        map_df["humidity"].apply(
            lambda x: display_value(
                x,
                " %",
            )
        )
    )

    map_df["wind_display"] = (
        map_df["wind_speed"].apply(
            lambda x: display_value(
                x,
                " km/h",
            )
        )
    )

    fig = px.choropleth(
        map_df,
        geojson=geojson,
        locations="state",
        featureidkey=(
            f"properties.{state_property}"
        ),
        color="risk_score",
        color_continuous_scale=[
            [0.00, "#E5E7EB"],
            [0.01, "#E5E7EB"],
            [0.33, "#86EFAC"],
            [0.66, "#FCD34D"],
            [1.00, "#EF4444"],
        ],
        range_color=(0, 3),
        custom_data=[
            "state",
            "temperature_display",
            "rainfall_display",
            "humidity_display",
            "wind_display",
            "heat_risk",
            "flood_risk",
            "environmental_status",
            "alert",
        ],
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "🌡️ Temperature: %{customdata[1]}<br>"
            "🌧️ Rainfall: %{customdata[2]}<br>"
            "💧 Humidity: %{customdata[3]}<br>"
            "💨 Wind: %{customdata[4]}<br>"
            "🔥 Heat Risk: %{customdata[5]}<br>"
            "🌊 Flood Risk: %{customdata[6]}<br>"
            "🌱 Environment: %{customdata[7]}<br>"
            "⚠️ Alert: %{customdata[8]}"
            "<extra></extra>"
        ),
        marker_line_width=0.5,
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
    )

    fig.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0,
        ),
        height=560,
        coloraxis_colorbar=dict(
            title="Risk",
            tickvals=[
                0,
                1,
                2,
                3,
            ],
            ticktext=[
                "No data",
                "Low",
                "Moderate",
                "High",
            ],
        ),
    )

    event = st.plotly_chart(
        fig,
        width="stretch",
        key=f"ecoguard_india_map_clickable_{id(fig)}",
        on_select="rerun",
        selection_mode="points",
    )

    # -------------------------------------------------------------------------
    # STATE CLICK
    # -------------------------------------------------------------------------

    try:

        points = event.selection.points

        if points:

            point = points[0]

            customdata = point.get(
                "customdata"
            )

            if customdata:

                clicked_state = str(
                    customdata[0]
                )

                valid_states = set(
                    map_df["state"]
                    .astype(str)
                )

                if clicked_state in valid_states:

                    st.session_state[
                        "home_selected_state"
                    ] = clicked_state

                    st.session_state[
                        "home_map_clicked_state"
                    ] = clicked_state

                    st.rerun()

    except Exception:
        pass


# =============================================================================
# DETAILS
# =============================================================================

def show_country_details(
    df: pd.DataFrame,
    iso3: str,
) -> None:

    rows = df[
        df["iso3"]
        .astype(str)
        .str.upper()
        == str(iso3).upper()
    ]

    if rows.empty:

        st.info(
            "No climate data available."
        )

        return

    row = rows.iloc[0]

    st.markdown(
        f"### 🌍 {row['name']}"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "🌡️ Temperature",
            display_value(
                row["temperature"],
                " °C",
            ),
        )

    with c2:
        st.metric(
            "🌧️ Rainfall",
            display_value(
                row["rainfall"],
                " mm",
            ),
        )

    with c3:
        st.metric(
            "💧 Humidity",
            display_value(
                row["humidity"],
                " %",
            ),
        )

    with c4:
        st.metric(
            "💨 Wind",
            display_value(
                row["wind_speed"],
                " km/h",
            ),
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.info(
            f"🔥 Heat Risk: {row['heat_risk']}"
        )

    with c2:
        st.info(
            f"🌊 Flood Risk: {row['flood_risk']}"
        )

    with c3:
        st.info(
            f"🌱 Environment: "
            f"{row['environmental_status']}"
        )

    if row["alert"] != "No major alert":

        st.warning(
            f"⚠️ {row['alert']}"
        )

    else:

        st.success(
            "✅ No major climate alert."
        )


def show_state_details(
    df: pd.DataFrame,
    state: str,
) -> None:

    rows = df[
        df["state"] == state
    ]

    if rows.empty:

        st.info(
            "No climate data available."
        )

        return

    row = rows.iloc[0]

    st.markdown(
        f"### 📍 {state}"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "🌡️ Temperature",
            display_value(
                row["temperature"],
                " °C",
            ),
        )

    with c2:
        st.metric(
            "🌧️ Rainfall",
            display_value(
                row["rainfall"],
                " mm",
            ),
        )

    with c3:
        st.metric(
            "💧 Humidity",
            display_value(
                row["humidity"],
                " %",
            ),
        )

    with c4:
        st.metric(
            "💨 Wind",
            display_value(
                row["wind_speed"],
                " km/h",
            ),
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.info(
            f"🔥 Heat Risk: {row['heat_risk']}"
        )

    with c2:
        st.info(
            f"🌊 Flood Risk: {row['flood_risk']}"
        )

    with c3:
        st.info(
            f"🌱 Environment: "
            f"{row['environmental_status']}"
        )

    if row["alert"] != "No major alert":

        st.warning(
            f"⚠️ {row['alert']}"
        )

    else:

        st.success(
            "✅ No major climate alert."
        )


# =============================================================================
# SNAPSHOT
# =============================================================================

def render_snapshot(
    df: pd.DataFrame,
) -> None:

    st.markdown(
        "### 🌎 Climate Snapshot"
    )

    if df.empty:
        return

    temperature = pd.to_numeric(
        df["temperature"],
        errors="coerce",
    )

    rainfall = pd.to_numeric(
        df["rainfall"],
        errors="coerce",
    )

    humidity = pd.to_numeric(
        df["humidity"],
        errors="coerce",
    )

    wind = pd.to_numeric(
        df["wind_speed"],
        errors="coerce",
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        value = (
            temperature.mean()
            if not temperature.dropna().empty
            else None
        )

        st.metric(
            "🌡️ Avg Temperature",
            display_value(
                value,
                " °C",
            ),
        )

    with c2:

        value = (
            rainfall.mean()
            if not rainfall.dropna().empty
            else None
        )

        st.metric(
            "🌧️ Avg Rainfall",
            display_value(
                value,
                " mm",
            ),
        )

    with c3:

        value = (
            humidity.mean()
            if not humidity.dropna().empty
            else None
        )

        st.metric(
            "💧 Avg Humidity",
            display_value(
                value,
                " %",
            ),
        )

    with c4:

        value = (
            wind.mean()
            if not wind.dropna().empty
            else None
        )

        st.metric(
            "💨 Avg Wind",
            display_value(
                value,
                " km/h",
            ),
        )


# =============================================================================
# MAP SECTION
# =============================================================================

def render_global_map_section(
    df: pd.DataFrame,
) -> None:

    if "home_map_view" not in st.session_state:

        st.session_state[
            "home_map_view"
        ] = "world"

    # =========================================================================
    # INDIA MAP
    # =========================================================================

    if (
        st.session_state[
            "home_map_view"
        ]
        == "india"
    ):

        if st.button(
            "← Back to World Map",
            key="home_back_world_button",
        ):

            st.session_state[
                "home_map_view"
            ] = "world"

            st.rerun()

        st.markdown(
            "### 🇮🇳 India State Climate Map"
        )

        try:

            india_geojson = (
                load_india_geojson()
            )

            india_df = (
                build_india_state_dataframe(
                    india_geojson
                )
            )

        except Exception as exc:

            st.error(
                f"Unable to load India state data: {exc}"
            )

            return

        if india_df.empty:

            st.warning(
                "No India state data available."
            )

            return

        render_india_map(
            india_df
        )

        state_options = sorted(
            india_df["state"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if not state_options:
            return

        # ---------------------------------------------------------------------
        # Determine selected state.
        # ---------------------------------------------------------------------

        selected_state = (
            st.session_state.get(
                "home_selected_state"
            )
        )

        if (
            selected_state
            not in state_options
        ):

            selected_state = (
                "Tamil Nadu"
                if "Tamil Nadu"
                in state_options
                else state_options[0]
            )

        selected_state = st.selectbox(
            "Select an Indian state",
            state_options,
            index=state_options.index(
                selected_state
            ),
            key="home_india_state_dropdown",
        )

        st.session_state[
            "home_selected_state"
        ] = selected_state

        show_state_details(
            india_df,
            selected_state,
        )

        return

    # =========================================================================
    # WORLD MAP
    # =========================================================================

    st.markdown(
        "### 🌍 Global Climate Map"
    )

    # Render the map only once.
    render_world_map(df)

    if df.empty:
        return

    iso3_list = sorted(
        df["iso3"]
        .dropna()
        .astype(str)
        .str.upper()
        .unique()
        .tolist()
    )

    if not iso3_list:
        return

    name_by_iso3 = (
        df.drop_duplicates(
            "iso3"
        )
        .set_index("iso3")["name"]
        .to_dict()
    )

    # -------------------------------------------------------------------------
    # Current selected country.
    # -------------------------------------------------------------------------

    selected_iso3 = (
        st.session_state.get(
            "home_selected_country_iso3",
            DEFAULT_COUNTRY_ISO3,
        )
    )

    selected_iso3 = str(
        selected_iso3
    ).upper()

    if selected_iso3 not in iso3_list:

        selected_iso3 = (
            DEFAULT_COUNTRY_ISO3
            if DEFAULT_COUNTRY_ISO3
            in iso3_list
            else iso3_list[0]
        )

    # -------------------------------------------------------------------------
    # IMPORTANT FIX:
    #
    # We DO NOT use:
    #
    # key="home_country_selector"
    #
    # together with Session State changes.
    #
    # Instead, the dropdown uses a unique widget key and the selected
    # country is stored separately.
    # -------------------------------------------------------------------------

    selected_iso3 = st.selectbox(
        "Select a country",
        iso3_list,
        index=iso3_list.index(
            selected_iso3
        ),
        format_func=lambda value: (
            f"{name_by_iso3.get(value, value)} "
            f"({value})"
        ),
        key="home_country_dropdown",
    )

    st.session_state[
        "home_selected_country_iso3"
    ] = selected_iso3

    # =========================================================================
    # INDIA
    # =========================================================================

    if selected_iso3 == "IND":

        st.info(
            "🇮🇳 India selected. "
            "Open the state-level climate map below."
        )

        if st.button(
            "🇮🇳 Open India State Map",
            key="home_open_india_button",
        ):

            st.session_state[
                "home_map_view"
            ] = "india"

            st.rerun()

    else:

        show_country_details(
            df,
            selected_iso3,
        )


# =============================================================================
# TRENDS
# =============================================================================

def render_trends(
    df: pd.DataFrame,
) -> None:

    if df.empty:
        return

    st.markdown(
        "### 📊 Climate Trends"
    )

    chart_df = df.copy()

    chart_df["temperature"] = pd.to_numeric(
        chart_df["temperature"],
        errors="coerce",
    )

    chart_df = (
        chart_df
        .dropna(
            subset=[
                "temperature"
            ]
        )
        .sort_values(
            "temperature",
            ascending=False,
        )
        .head(10)
    )

    if chart_df.empty:
        return

    if PLOTLY_AVAILABLE:

        fig = px.bar(
            chart_df,
            x="name",
            y="temperature",
            title="Top 10 Current Temperatures",
            labels={
                "name": "Country",
                "temperature": "Temperature °C",
            },
        )

        fig.update_layout(
            height=400,
            margin=dict(
                l=20,
                r=20,
                t=50,
                b=20,
            ),
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="ecoguard_temperature_chart",
        )


# =============================================================================
# ALERTS
# =============================================================================

def render_alerts(
    df: pd.DataFrame,
) -> None:

    st.markdown(
        "### ⚠️ Climate Alerts"
    )

    if df.empty:

        st.info(
            "No climate data available."
        )

        return

    alert_df = df[
        df["alert"]
        != "No major alert"
    ]

    if alert_df.empty:

        st.success(
            "No major climate alerts detected."
        )

        return

    for _, row in (
        alert_df.head(10).iterrows()
    ):

        st.warning(
            f"**{row['name']}** — "
            f"{row['alert']}"
        )


# =============================================================================
# RECOMMENDATIONS
# =============================================================================

def render_recommendations() -> None:

    st.markdown(
        "### 🌱 Sustainability Recommendations"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.info(
            "💡 **Reduce Energy Use**\n\n"
            "Use energy-efficient appliances "
            "and switch off unused devices."
        )

    with c2:

        st.info(
            "♻️ **Reduce Waste**\n\n"
            "Reuse, recycle and separate "
            "waste correctly."
        )

    with c3:

        st.info(
            "🌳 **Protect Green Spaces**\n\n"
            "Support trees, biodiversity "
            "and local ecosystems."
        )


# =============================================================================
# MAIN
# =============================================================================

def show() -> None:

    # =========================================================================
    # HEADER
    # =========================================================================

    st.markdown(
        """
        <div style="
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.15rem;
        ">
            🌍 EcoGuard AI
        </div>

        <div style="
            font-size: 0.82rem;
            color: #6b7280;
            margin-bottom: 1rem;
        ">
            Climate Intelligence & Sustainability
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # WORLD DATA
    # =========================================================================

    try:

        world_geojson = (
            load_world_geojson()
        )

        df = build_global_dataframe(
            world_geojson
        )

    except Exception as exc:

        st.error(
            f"Unable to load climate data: {exc}"
        )

        return

    # =========================================================================
    # SNAPSHOT
    # =========================================================================

    render_snapshot(df)

    st.divider()

    # =========================================================================
    # MAP
    # =========================================================================

    render_global_map_section(
        df
    )

    st.divider()

    # =========================================================================
    # TRENDS
    # =========================================================================

    render_trends(df)

    st.divider()

    # =========================================================================
    # ALERTS
    # =========================================================================

    render_alerts(df)

    st.divider()

    # =========================================================================
    # RECOMMENDATIONS
    # =========================================================================

    render_recommendations()

    st.divider()

    # =========================================================================
    # ASK ECOGUARD
    # =========================================================================

    st.markdown(
        "### 🤖 Ask EcoGuard"
    )

    question = st.text_input(
        "Ask a climate or sustainability question",
        placeholder=(
            "Example: How can I reduce my carbon footprint?"
        ),
        key="home_ecoguard_question",
    )

    if question:

        st.info(
            "EcoGuard AI Assistant can help "
            "you explore climate risks, "
            "sustainability and environmental topics."
        )

# =============================================================================
# START
# =============================================================================

if __name__ == "__main__":
    show()
