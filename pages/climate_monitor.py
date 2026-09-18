# =============================================================================
# EcoGuard AI - Climate Monitor Page
# =============================================================================
# All sections use real official datasets loaded from utils/climate_data.py.
# No demo arrays remain.
#
# Data sources:
#   Temperature : NASA GISS GISTEMP v4 — annual anomalies 1880–present
#   Sea Ice     : NSIDC Sea Ice Index v4 — September extent 1979–present
#   Sea Level   : NOAA Laboratory for Satellite Altimetry — multi-mission
#                 GMSL (TOPEX/Poseidon → Sentinel-6MF) 1993–present
#   Forest Area : FAOSTAT Land Use bulk dataset — global forest land 1990–present
#
# session_state.climate_monitor_section is initialised in app.py and set
# by sidebar navigation buttons. Sections: temperature | ice | sea | ecosystems
# =============================================================================

import streamlit as st

from utils.ui_components import (
    page_header, section_divider, info_card, footer,
)
from utils.climate_data import (
    get_global_temperature_data,
    get_arctic_sea_ice_data,
    get_global_sea_level_data,
    get_global_forest_data,
)


# ---------------------------------------------------------------------------
# Section: Temperature Trends
# ---------------------------------------------------------------------------

def _show_temperature():
    section_divider("🌡️ TEMPERATURE TRENDS")
    info_card(
        "Global Temperature Anomaly — NASA GISS GISTEMP v4",
        "Annual mean surface temperature anomaly relative to the 1951–1980 baseline. "
        "Data from NASA Goddard Institute for Space Studies (GISS) Surface Temperature "
        "Analysis. Earth's average temperature has risen ~1.2 °C above pre-industrial levels.",
    )

    with st.spinner("Loading NASA GISS temperature data…"):
        df = get_global_temperature_data()

    if df is None:
        st.error(
            "❌ Unable to retrieve NASA GISS temperature data. "
            "Check your internet connection and try refreshing."
        )
        return

    chart_df = df.set_index("year")[["anomaly"]]
    chart_df.columns = ["Temperature Anomaly (°C)"]
    st.line_chart(chart_df, height=260, width="stretch")

    # Summary stats
    latest = df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Year",       str(int(latest["year"])))
    col2.metric("Latest Anomaly",    f"{latest['anomaly']:+.2f} °C")
    col3.metric("Records Available", f"{len(df)} years")

    st.caption(
        f"📡 Source: NASA GISS Surface Temperature Analysis (GISTEMP v4). "
        f"Data range: {int(df['year'].min())}–{int(df['year'].max())}. "
        "Anomaly relative to 1951–1980 average. "
        "Retrieved live from data.giss.nasa.gov."
    )
    st.caption(
        "⚠️ **Responsible AI notice:** Temperature data is sourced directly from NASA GISS. "
        "EcoGuard AI does not modify or interpret these measurements. "
        "Always consult official scientific sources for decision-making."
    )


# ---------------------------------------------------------------------------
# Section: Ice & Glaciers
# ---------------------------------------------------------------------------

def _show_ice():
    section_divider("🧊 ICE & GLACIER CHANGES")
    info_card(
        "Arctic Sea Ice September Extent — NSIDC Sea Ice Index v4",
        "September marks the annual Arctic sea ice minimum. This dataset from the "
        "National Snow and Ice Data Center (NSIDC) tracks the extent of sea ice "
        "each September since satellite observations began in 1979.",
    )

    with st.spinner("Loading NSIDC sea ice data…"):
        df = get_arctic_sea_ice_data()

    if df is None:
        st.error(
            "❌ Unable to retrieve NSIDC sea ice data. "
            "Check your internet connection and try refreshing."
        )
    else:
        chart_df = df.set_index("year")[["extent"]]
        chart_df.columns = ["Sea Ice Extent (million km²)"]
        st.line_chart(chart_df, height=260, width="stretch")

        latest = df.iloc[-1]
        col1, col2, col3 = st.columns(3)
        col1.metric("Latest Year",       str(int(latest["year"])))
        col2.metric("Latest Extent",     f"{latest['extent']:.2f} M km²")
        col3.metric("Records Available", f"{len(df)} years")

        st.caption(
            f"📡 Source: NSIDC Sea Ice Index v4 — September Northern Hemisphere extent. "
            f"Data range: {int(df['year'].min())}–{int(df['year'].max())}. "
            "Retrieved live from noaadata.apps.nsidc.org."
        )
        st.caption(
            "⚠️ **Responsible AI notice:** Sea ice data is sourced directly from NSIDC. "
            "EcoGuard AI does not modify these measurements. "
            "Always consult official scientific sources for decision-making."
        )

    # Contextual info cards (text — not fake data)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        info_card(
            "🧊 Greenland Ice Sheet",
            "Greenland is losing approximately 280 billion tonnes of ice per year, "
            "contributing measurably to global sea level rise. "
            "<em>(Source: IPCC AR6, 2021)</em>",
        )
    with c2:
        info_card(
            "🏔️ Mountain Glaciers",
            "Glaciers in the Himalayas, Alps, and Andes have lost significant mass "
            "since the 1990s. Many are projected to disappear within decades under "
            "current emissions trajectories. "
            "<em>(Source: IPCC AR6, 2021)</em>",
        )


# ---------------------------------------------------------------------------
# Section: Sea Level — NOAA Laboratory for Satellite Altimetry
# ---------------------------------------------------------------------------

def _show_sea():
    section_divider("🌊 SEA LEVEL CHANGES")
    info_card(
        "Global Mean Sea Level — NOAA Laboratory for Satellite Altimetry",
        "Merged multi-mission satellite altimetry (TOPEX/Poseidon, Jason-1/2/3, "
        "Sentinel-6MF) from the NOAA Laboratory for Satellite Altimetry. "
        "Values are sea level anomaly in mm above the 1993 baseline mean. "
        "Annual tidal signals are retained.",
    )

    with st.spinner("Loading NOAA sea level data…"):
        df = get_global_sea_level_data()

    if df is None:
        st.error(
            "❌ **Global Mean Sea Level data is currently unavailable.**\n\n"
            "The NOAA LSA data file could not be retrieved. "
            "EcoGuard AI does not display fabricated data — no fallback is shown.\n\n"
            "📡 **Direct sources you can visit:**\n"
            "- [NOAA Sea Level Rise](https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/)\n"
            "- [NASA Sea Level Change Portal](https://sealevel.nasa.gov/)\n"
            "- [IPCC AR6 Chapter 9 (Ocean)](https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-9/)"
        )
        st.caption(
            "⚠️ **Responsible AI notice:** EcoGuard AI only displays real official data. "
            "When a source is unavailable, this section shows an error message rather "
            "than a synthetic substitute."
        )
        return

    # The dataset has ~1 557 sub-monthly observations. Resample to annual mean
    # for a legible chart (annual average of decimal-year values).
    df_annual = (
        df.assign(year_int=df["year"].astype(int))
        .groupby("year_int", as_index=True)["sea_level_mm"]
        .mean()
        .reset_index()
        .rename(columns={"year_int": "year"})
    )

    chart_df = df_annual.set_index("year")[["sea_level_mm"]]
    chart_df.columns = ["Sea Level Anomaly (mm)"]
    st.line_chart(chart_df, height=260, width="stretch")

    latest_row  = df.iloc[-1]
    latest_year = int(latest_row["year"])
    latest_val  = latest_row["sea_level_mm"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Source",         "NOAA LSA")
    col2.metric("Latest Year",    str(latest_year))
    col3.metric("Latest Value",   f"{latest_val:.1f} mm")
    col4.metric("Observations",   f"{len(df):,}")

    st.caption(
        f"📡 **Source:** NOAA Laboratory for Satellite Altimetry (LSA). "
        f"**Dataset:** Mean Sea Level Anomaly, Global Ocean 66°S–66°N, annual signals retained. "
        f"**Latest available official data:** year {latest_year}. "
        f"**Unit:** mm above 1993 baseline. "
        f"**Missions:** TOPEX/Poseidon → Jason-1 → Jason-2 → Jason-3 → Sentinel-6MF. "
        "This dataset is periodically updated by NOAA — it is not a real-time feed."
    )
    st.caption(
        "⚠️ **Responsible AI notice:** Sea level data is sourced directly from NOAA. "
        "EcoGuard AI does not modify these measurements. "
        "Always consult official scientific sources for decision-making."
    )


# ---------------------------------------------------------------------------
# Section: Ecosystems — FAOSTAT Land Use (FAO)
# ---------------------------------------------------------------------------

def _show_ecosystems():
    section_divider("🌳 ECOSYSTEM CHANGES")
    info_card(
        "Global Forest Area — FAO FAOSTAT Land Use Dataset",
        "World aggregate forest land area from the FAO FAOSTAT Land Use bulk dataset "
        "(Item: Forest land, code 6646). Values are converted from the source unit "
        "(1 000 ha) to million hectares. Data covers 1990 to the latest FAO "
        "assessment year.",
    )

    with st.spinner("Loading FAO forest area data…"):
        df = get_global_forest_data()

    if df is None:
        st.error(
            "❌ **Global Forest Area data is currently unavailable.**\n\n"
            "The FAOSTAT bulk dataset could not be retrieved or parsed. "
            "EcoGuard AI does not display fabricated data — no fallback is shown.\n\n"
            "📡 **Direct sources you can visit:**\n"
            "- [FAO Global Forest Resources Assessment](https://www.fao.org/forest-resources-assessment/)\n"
            "- [FAOSTAT Land Use](https://www.fao.org/faostat/en/#data/RL)\n"
            "- [Global Forest Watch](https://www.globalforestwatch.org/)"
        )
        st.caption(
            "⚠️ **Responsible AI notice:** EcoGuard AI only displays real official data. "
            "When a source is unavailable, this section shows an error message rather "
            "than a synthetic substitute."
        )
    else:
        chart_df = df.set_index("year")[["forest_area"]]
        chart_df.columns = ["Forest Area (million ha)"]
        st.area_chart(chart_df, height=260, width="stretch")

        latest = df.iloc[-1]
        first  = df.iloc[0]
        change = latest["forest_area"] - first["forest_area"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Source",             "FAO FAOSTAT")
        col2.metric("Latest Year",        str(int(latest["year"])))
        col3.metric("Latest Forest Area", f"{latest['forest_area']:.1f} M ha")
        col4.metric(
            f"Change since {int(first['year'])}",
            f"{change:+.1f} M ha",
            delta_color="inverse",
        )

        st.caption(
            f"📡 **Source:** Food and Agriculture Organization of the United Nations (FAO). "
            f"**Dataset:** FAOSTAT — Inputs: Land Use, Item: Forest land (code 6646), "
            f"World aggregate (area code 5000). "
            f"**Latest available official data:** {int(latest['year'])}. "
            f"**Unit:** million hectares (converted from source unit of 1 000 ha). "
            f"**Data range:** {int(first['year'])}–{int(latest['year'])}. "
            "This dataset is periodically updated by FAO — it is not a real-time feed."
        )
        st.caption(
            "⚠️ **Responsible AI notice:** Forest area data is sourced directly from FAO FAOSTAT. "
            "EcoGuard AI does not modify these measurements. "
            "Always consult official scientific sources for decision-making."
        )

    # Contextual info cards — educational text, clearly distinguished from data
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        info_card(
            "🐾 Biodiversity Loss",
            "Climate change and habitat loss are driving species extinction rates "
            "100–1 000× above natural background rates. Over 1 million species are "
            "currently threatened with extinction. "
            "<em>(Educational context — Source: IPBES Global Assessment, 2019)</em>",
        )
    with c2:
        info_card(
            "🪸 Ocean Ecosystems",
            "Coral reefs support approximately 25 % of all marine species but face "
            "widespread bleaching from ocean warming and acidification. "
            "50 % of the world's coral reefs have been lost since the 1950s. "
            "<em>(Educational context — Source: IPCC SROCC, 2019)</em>",
        )


# ---------------------------------------------------------------------------
# Main render function
# ---------------------------------------------------------------------------

def show():
    """
    Render the Climate Monitor page.

    Reads st.session_state.climate_monitor_section (set by the sidebar
    navigation buttons in app.py) to decide which section to display.

    Sections:
        "temperature" → Temperature Trends  (NASA GISS GISTEMP v4)
        "ice"         → Ice & Glaciers      (NSIDC Sea Ice Index v4)
        "sea"         → Sea Level           (NOAA LSA multi-mission GMSL)
        "ecosystems"  → Ecosystems          (FAO FAOSTAT Land Use)
    """
    page_header(
        "🌍", "Climate Monitor",
        "Long-term environmental changes from official scientific datasets.",
    )

    # Read the section key — default to "temperature" if somehow not set
    section = st.session_state.get("climate_monitor_section", "temperature")

    # In-page tab buttons (user can navigate without the sidebar too)
    tab_labels = {
        "temperature": "🌡️ Temperature",
        "ice":         "🧊 Ice & Glaciers",
        "sea":         "🌊 Sea Level",
        "ecosystems":  "🌳 Ecosystems",
    }

    tab_cols = st.columns(4)
    for i, (key, label) in enumerate(tab_labels.items()):
        with tab_cols[i]:
            button_type = "primary" if section == key else "secondary"
            if st.button(
                label, key=f"cm_tab_{key}",
                width="stretch", type=button_type,
            ):
                st.session_state.climate_monitor_section = key
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Dispatch to the selected section
    if section == "temperature":
        _show_temperature()
    elif section == "ice":
        _show_ice()
    elif section == "sea":
        _show_sea()
    elif section == "ecosystems":
        _show_ecosystems()
    else:
        _show_temperature()

    footer()
