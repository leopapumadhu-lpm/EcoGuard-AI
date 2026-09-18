# =============================================================================
# EcoGuard AI - Climate Risks Page
# =============================================================================
# Flood Risk: preserves the original Open-Meteo geocoding + rainfall
#             implementation completely unchanged.
# Heatwave / Drought / Wildfire: real Open-Meteo current + historical data
#             via utils/weather_data.py.
# Landing page: no pre-assessment risk badges — users must run an assessment.
#
# Risk scoring functions live in utils/weather_data.py so that home.py and
# this page always produce identical results for the same inputs.
# =============================================================================

import streamlit as st
import requests

from utils.ui_components import (
    page_header, metric_card, risk_metric_card,
    recommendation_card, section_divider, footer,
)
from utils.weather_data import (
    geocode_location,
    get_current_weather,
    get_recent_daily_weather,
    flood_risk_score,
    heatwave_risk_score,
    drought_risk_score,
    wildfire_risk_score,
)


# ---------------------------------------------------------------------------
# Landing page — no fake pre-assessment risk levels
# ---------------------------------------------------------------------------

def show_landing(nav_callback=None):
    page_header("🌦️", "Climate Risk Center",
                "Understand environmental risks affecting your location.")
    st.markdown("<br>", unsafe_allow_html=True)

    cards = [
        ("🌡️", "Heatwave Risk",      "heatwave",
         "Assess extreme heat conditions based on real temperature and humidity data."),
        ("🌧️", "Heavy Rain & Flood", "flood",
         "Evaluate flood risk from recent real rainfall data via Open-Meteo."),
        ("💧", "Drought Risk",       "drought",
         "Understand water-scarcity risk from real precipitation data."),
        ("🔥", "Wildfire Risk",      "wildfire",
         "Gauge fire-spread risk from real temperature, humidity and dryness data."),
    ]

    row1 = st.columns(2)
    row2 = st.columns(2)
    grid = [row1[0], row1[1], row2[0], row2[1]]

    for col, (icon, title, key, desc) in zip(grid, cards):
        with col:
            st.markdown(
                f'<div class="risk-overview-card">'
                f'<div class="risk-icon">{icon}</div>'
                f'<h4>{title}</h4><p>{desc}</p>'
                f'<p style="color:#57606a;font-size:0.82em;font-style:italic;">'
                f'Enter a location to get your risk assessment.</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button(f"Explore {title} →", key=f"risk_{key}", width="stretch"):
                if nav_callback:
                    nav_callback(key)

    footer()


# ---------------------------------------------------------------------------
# Local aliases — keep old call-site names working; logic lives in
# utils/weather_data.py so home.py and this page are always consistent.
# ---------------------------------------------------------------------------

def _heatwave_score(temp_c, humidity_pct):
    return heatwave_risk_score(temp_c, humidity_pct)

def _drought_score(precip_30d, avg_max_temp):
    return drought_risk_score(precip_30d, avg_max_temp)

def _wildfire_score(avg_max_temp, avg_min_humidity, precip_30d):
    return wildfire_risk_score(avg_max_temp, avg_min_humidity, precip_30d)


# ---------------------------------------------------------------------------
# Heatwave Risk
# ---------------------------------------------------------------------------

def show_heatwave():
    page_header("🌡️", "Heatwave Risk Assessment",
                "Real-time heat conditions powered by Open-Meteo.")
    st.markdown(
        "Enter a city or region and EcoGuard AI will retrieve current "
        "temperature and humidity to assess heatwave risk.\n\n"
        "⚠️ This is an educational decision-support tool — not an official heat warning."
    )

    location = st.text_input(
        "📍 Enter your location",
        placeholder="Example: Delhi, India",
        key="heatwave_location_input",
    )
    assess = st.button("🔍 Get Conditions & Assess Risk", key="heatwave_assess_btn")

    if assess:
        if not location.strip():
            st.error("Please enter a location.")
            return

        with st.spinner("Locating and fetching weather data…"):
            place = geocode_location(location.strip())

        if place is None:
            st.error("❌ Location not found. Try a city name such as Delhi, India.")
            return

        lat, lon = place["latitude"], place["longitude"]
        city_label = f"{place['name']}, {place['country']}".strip(", ")

        with st.spinner("Loading current conditions…"):
            current = get_current_weather(lat, lon)

        if current is None:
            st.error("❌ Unable to retrieve weather data. Check your internet connection.")
            return

        temp      = current["temperature"]
        feels     = current["apparent_temp"]
        humidity  = current["humidity"]
        wind      = current["wind_speed"]

        if temp is None or humidity is None:
            st.error("❌ Incomplete weather data returned. Please try again.")
            return

        score, level = _heatwave_score(temp, humidity)

        section_divider("📊 CURRENT CONDITIONS")
        c1, c2, c3 = st.columns(3)
        with c1: metric_card("📍", "Location",    city_label)
        with c2: metric_card("🌡️", "Temperature", f"{temp:.1f} °C",
                              f"Feels like {feels:.1f} °C" if feels is not None else "")
        with c3: metric_card("💧", "Humidity",    f"{humidity} %")

        c4, c5, c6 = st.columns(3)
        with c4: metric_card("🌬️", "Wind Speed",      f"{wind:.1f} km/h" if wind is not None else "N/A")
        with c5: metric_card("📊", "Heat Risk Score", f"{score}/100")
        with c6: risk_metric_card("🌡️", "Heat Risk Level", level)

        section_divider("⚠️ RECOMMENDATIONS")
        recs = [
            ("💧", "Hydration",     "Drink at least 2–3 litres of water per day. Avoid alcohol and caffeine."),
            ("🏠", "Stay Indoors",  "Avoid outdoor activity between 11 am and 4 pm on high-heat days."),
            ("👕", "Light Clothing","Wear loose, light-coloured, breathable clothing."),
            ("🏥", "Heat Illness",  "Recognise symptoms: heavy sweating, weakness, dizziness. Seek shade immediately."),
            ("🌬️", "Ventilation",   "Use fans or air conditioning. Keep curtains closed during the day."),
            ("🌳", "Green Spaces",  "Spend time in shaded parks or near water bodies to cool down."),
        ]
        rc = st.columns(2)
        for i, (icon, title, body) in enumerate(recs):
            with rc[i % 2]:
                recommendation_card(icon, title, body)

        st.caption(
            f"📡 Source: Open-Meteo (open-meteo.com) — real-time conditions for {city_label}."
        )
        st.caption(
            "⚠️ **Responsible AI notice:** Risk score is a simplified heat-stress indicator "
            "based on temperature and relative humidity. It is not a medical or official "
            "meteorological warning. Always follow advice from local health authorities."
        )

    footer()


# ---------------------------------------------------------------------------
# Flood Risk — UNCHANGED (original Open-Meteo implementation)
# ---------------------------------------------------------------------------

def show_flood():
    """
    Flood Risk Assistant — preserves the original Open-Meteo
    geocoding + rainfall implementation unchanged.
    """
    page_header("🌧️", "Heavy Rain & Flood Risk",
                "Real-time rainfall data powered by Open-Meteo.")
    st.markdown(
        "Enter a city or region and EcoGuard AI will automatically retrieve "
        "location coordinates and recent rainfall information.\n\n"
        "⚠️ This is an educational decision-support tool."
    )

    location = st.text_input("📍 Enter your location",
                              placeholder="Example: Chennai, India",
                              key="flood_location_input")
    assess = st.button("🔍 Get Rainfall & Assess Risk", key="flood_assess_btn")

    if assess:
        if not location.strip():
            st.error("Please enter a location.")
        else:
            try:
                geo_resp = requests.get(
                    "https://geocoding-api.open-meteo.com/v1/search",
                    params={"name": location, "count": 1, "language": "en", "format": "json"},
                    timeout=10,
                )
                geo_resp.raise_for_status()
                geo_data = geo_resp.json()

                if "results" not in geo_data or not geo_data["results"]:
                    st.error("❌ Location not found. Try a city name such as Chennai, India.")
                else:
                    place     = geo_data["results"][0]
                    latitude  = place["latitude"]
                    longitude = place["longitude"]
                    city_name = place.get("name", location)
                    country   = place.get("country", "")

                    wx_resp = requests.get(
                        "https://api.open-meteo.com/v1/forecast",
                        params={
                            "latitude": latitude, "longitude": longitude,
                            "hourly": "precipitation,rain",
                            "past_days": 1, "forecast_days": 1, "timezone": "auto",
                        },
                        timeout=10,
                    )
                    wx_resp.raise_for_status()
                    wx_data = wx_resp.json()

                    precip      = wx_data["hourly"]["precipitation"]
                    rainfall_24h = sum(v for v in precip[-24:] if v is not None)

                    section_divider("📍 LOCATION INFORMATION")
                    c1, c2, c3 = st.columns(3)
                    with c1: metric_card("📍", "Location",  f"{city_name}, {country}".strip(", "))
                    with c2: metric_card("🌐", "Latitude",  f"{latitude:.4f}")
                    with c3: metric_card("🌐", "Longitude", f"{longitude:.4f}")

                    section_divider("🌧️ RAINFALL DATA")
                    metric_card("🌧️", "Rainfall – Last 24 Hours", f"{rainfall_24h:.1f} mm",
                                "Retrieved from Open-Meteo")
                    st.caption("Rainfall retrieved automatically from Open-Meteo (open-meteo.com).")

                    risk_score, risk_level = flood_risk_score(rainfall_24h)

                    section_divider("🌊 FLOOD RISK ASSESSMENT")
                    rc = st.columns(2)
                    with rc[0]: metric_card("📊", "Flood Risk Score", f"{risk_score}/100")
                    with rc[1]: risk_metric_card("🌊", "Flood Risk Level", risk_level)

                    section_divider("⚠️ RECOMMENDATIONS")
                    if risk_score >= 80:
                        st.error("🔴 **Very high rainfall.**\n\n• Monitor official flood alerts\n• Avoid flooded areas\n• Do not drive through floodwater\n• Keep emergency supplies ready")
                    elif risk_score >= 60:
                        st.warning("🟠 **High rainfall.**\n\n• Monitor local conditions\n• Avoid travel near waterways\n• Be cautious in low-lying areas")
                    elif risk_score >= 35:
                        st.warning("🟡 **Moderate rainfall.**\n\n• Monitor weather conditions\n• Be cautious around drainage channels")
                    else:
                        st.success("🟢 **Current rainfall is relatively low.**\n\n• Continue monitoring local weather")

                    st.caption("EcoGuard AI provides an indicative rainfall-based assessment. Not an official flood warning.")

            except requests.exceptions.RequestException:
                st.error("❌ Unable to retrieve weather data. Check your internet connection.")
            except Exception as error:
                st.error(f"❌ Something went wrong: {error}")

    footer()


# ---------------------------------------------------------------------------
# Drought Risk — real Open-Meteo 30-day data
# ---------------------------------------------------------------------------

def show_drought():
    page_header("💧", "Drought Risk Assessment",
                "Real precipitation data powered by Open-Meteo.")
    st.markdown(
        "Enter a city or region. EcoGuard AI will retrieve 30 days of rainfall "
        "and temperature data to assess drought risk.\n\n"
        "⚠️ This is an educational decision-support tool — not an official drought warning."
    )

    location = st.text_input(
        "📍 Enter your location",
        placeholder="Example: Rajasthan, India",
        key="drought_location_input",
    )
    assess = st.button("🔍 Get Data & Assess Risk", key="drought_assess_btn")

    if assess:
        if not location.strip():
            st.error("Please enter a location.")
            return

        with st.spinner("Locating and fetching weather data…"):
            place = geocode_location(location.strip())

        if place is None:
            st.error("❌ Location not found. Try a city name such as Rajasthan, India.")
            return

        lat, lon = place["latitude"], place["longitude"]
        city_label = f"{place['name']}, {place['country']}".strip(", ")

        with st.spinner("Loading 30-day historical data…"):
            history = get_recent_daily_weather(lat, lon, past_days=30)

        if history is None:
            st.error("❌ Unable to retrieve weather data. Check your internet connection.")
            return

        precip_list = [v for v in history["precipitation_sum"] if v is not None]
        temp_list   = [v for v in history["temp_max"]          if v is not None]

        if not precip_list or not temp_list:
            st.error("❌ Insufficient data returned for this location. Please try again.")
            return

        precip_30d    = sum(precip_list)
        avg_max_temp  = sum(temp_list) / len(temp_list)
        dry_days      = sum(1 for v in precip_list if v < 1.0)

        score, level = _drought_score(precip_30d, avg_max_temp)

        section_divider("📊 30-DAY CONDITIONS")
        c1, c2, c3 = st.columns(3)
        with c1: metric_card("📍", "Location",            city_label)
        with c2: metric_card("🌧️", "30-Day Rainfall",    f"{precip_30d:.1f} mm")
        with c3: metric_card("🌡️", "Avg Max Temperature", f"{avg_max_temp:.1f} °C")

        c4, c5, c6 = st.columns(3)
        with c4: metric_card("☀️", "Dry Days (< 1 mm)", f"{dry_days} / {len(precip_list)} days")
        with c5: metric_card("📊", "Water Risk Score",   f"{score}/100")
        with c6: risk_metric_card("💧", "Drought Risk Level", level)

        section_divider("⚠️ RECOMMENDATIONS")
        recs = [
            ("💧", "Water Conservation",      "Fix leaks and use water-efficient appliances."),
            ("🌱", "Rainwater Harvesting",     "Install rainwater collection systems."),
            ("🌾", "Drought-Resistant Plants", "Choose native or drought-tolerant plants."),
            ("🚿", "Reduce Usage",             "Take shorter showers and reuse grey water."),
        ]
        rc = st.columns(2)
        for i, (icon, title, body) in enumerate(recs):
            with rc[i % 2]:
                recommendation_card(icon, title, body)

        st.caption(
            f"📡 Source: Open-Meteo (open-meteo.com) — 30-day historical data for {city_label}."
        )
        st.caption(
            "⚠️ **Responsible AI notice:** Drought risk score is based on total precipitation "
            "and maximum temperature over 30 days. It is a simplified indicator, not an "
            "official drought classification. Consult local water authorities for formal guidance."
        )

    footer()


# ---------------------------------------------------------------------------
# Wildfire Risk — real Open-Meteo 30-day data
# ---------------------------------------------------------------------------

def show_wildfire():
    page_header("🔥", "Wildfire Risk Assessment",
                "Real weather data powered by Open-Meteo.")
    st.markdown(
        "Enter a city or region. EcoGuard AI will retrieve 30 days of temperature, "
        "humidity, and precipitation to assess wildfire risk.\n\n"
        "⚠️ This is an educational decision-support tool — not an official fire warning."
    )

    location = st.text_input(
        "📍 Enter your location",
        placeholder="Example: Sydney, Australia",
        key="wildfire_location_input",
    )
    assess = st.button("🔍 Get Data & Assess Risk", key="wildfire_assess_btn")

    if assess:
        if not location.strip():
            st.error("Please enter a location.")
            return

        with st.spinner("Locating and fetching weather data…"):
            place = geocode_location(location.strip())

        if place is None:
            st.error("❌ Location not found. Try a city name such as Sydney, Australia.")
            return

        lat, lon = place["latitude"], place["longitude"]
        city_label = f"{place['name']}, {place['country']}".strip(", ")

        with st.spinner("Loading 30-day historical data…"):
            history = get_recent_daily_weather(lat, lon, past_days=30)

        if history is None:
            st.error("❌ Unable to retrieve weather data. Check your internet connection.")
            return

        precip_list   = [v for v in history["precipitation_sum"] if v is not None]
        temp_list     = [v for v in history["temp_max"]          if v is not None]
        humidity_list = [v for v in history["humidity_max"]      if v is not None]

        if not precip_list or not temp_list or not humidity_list:
            st.error("❌ Insufficient data returned for this location. Please try again.")
            return

        precip_30d       = sum(precip_list)
        avg_max_temp     = sum(temp_list)    / len(temp_list)
        avg_min_humidity = sum(humidity_list) / len(humidity_list)

        score, level = _wildfire_score(avg_max_temp, avg_min_humidity, precip_30d)

        section_divider("📊 30-DAY CONDITIONS")
        c1, c2, c3 = st.columns(3)
        with c1: metric_card("📍", "Location",            city_label)
        with c2: metric_card("🌡️", "Avg Max Temperature", f"{avg_max_temp:.1f} °C")
        with c3: metric_card("💧", "Avg Humidity",        f"{avg_min_humidity:.0f} %")

        c4, c5, c6 = st.columns(3)
        with c4: metric_card("🌧️", "30-Day Rainfall",    f"{precip_30d:.1f} mm")
        with c5: metric_card("📊", "Fire Risk Score",     f"{score}/100")
        with c6: risk_metric_card("🔥", "Wildfire Risk Level", level)

        section_divider("⚠️ RECOMMENDATIONS")
        recs = [
            ("🚫", "No Open Burning",        "Avoid lighting fires outdoors during dry conditions."),
            ("🌲", "Clear Defensible Space",  "Keep dry materials away from buildings."),
            ("📻", "Stay Informed",           "Monitor local fire authority alerts."),
            ("💧", "Maintain Firebreaks",     "Ensure water access around forest-edge properties."),
        ]
        rc = st.columns(2)
        for i, (icon, title, body) in enumerate(recs):
            with rc[i % 2]:
                recommendation_card(icon, title, body)

        st.caption(
            f"📡 Source: Open-Meteo (open-meteo.com) — 30-day historical data for {city_label}."
        )
        st.caption(
            "⚠️ **Responsible AI notice:** Wildfire risk score uses temperature, humidity, "
            "and rainfall as simplified fire-weather proxies. It is not an official fire "
            "danger rating. Always follow advice from local fire authorities."
        )

    footer()
