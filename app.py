from __future__ import annotations

import streamlit as st


# =============================================================================
# ECOGUARD AI
# Main Application
# =============================================================================


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="EcoGuard AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# GLOBAL UI STYLE
# =============================================================================

st.markdown(
    """
    <style>
        /* Main application */
        .main {
            background-color: #ffffff;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #f8fafc;
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1rem;
        }

        /* Sidebar buttons */
        section[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            border: none;
            background: transparent;
            text-align: left;
            padding: 0.45rem 0.75rem;
            border-radius: 8px;
            font-size: 0.95rem;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            background-color: #e8f5e9;
        }

        /* Sidebar divider */
        .sidebar-divider {
            margin: 0.8rem 0;
            border-top: 1px solid #d1d5db;
        }

        /* Sidebar title */
        .sidebar-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #111827;
            margin-bottom: 0.1rem;
        }

        .sidebar-subtitle {
            font-size: 0.78rem;
            color: #6b7280;
            margin-bottom: 0.9rem;
        }

        /* Sidebar section headings */
        .sidebar-section {
            font-size: 0.95rem;
            font-weight: 700;
            color: #111827;
            margin-top: 0.55rem;
            margin-bottom: 0.15rem;
        }

        .sidebar-child {
            font-size: 0.82rem;
            color: #6b7280;
            padding-left: 0.55rem;
            margin-top: 0.05rem;
            margin-bottom: 0.05rem;
        }

        /* Footer */
        .sidebar-footer {
            text-align: center;
            color: #6b7280;
            font-size: 0.78rem;
            padding-top: 0.6rem;
        }

        /* Remove excessive top spacing */
        .block-container {
            padding-top: 1.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# IMPORT PROJECT PAGES
# =============================================================================

from pages import home as pg_home
from pages import climate_risks as pg_risks
from pages import climate_monitor as pg_monitor
from pages import sustainability as pg_sus
from pages import climate_news as pg_news
from pages import climate_assistant as pg_assistant
from pages import about as pg_about

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "climate_risk_section" not in st.session_state:
    st.session_state.climate_risk_section = "landing"

if "climate_monitor_section" not in st.session_state:
    st.session_state.climate_monitor_section = "temperature"

if "sustainability_section" not in st.session_state:
    st.session_state.sustainability_section = "landing"

if "ecoguard_selected_country" not in st.session_state:
    st.session_state.ecoguard_selected_country = None

if "ecoguard_selected_region" not in st.session_state:
    st.session_state.ecoguard_selected_region = None


# =============================================================================
# VALID MAIN PAGES
# =============================================================================

VALID_PAGES = {
    "home",
    "climate_risks",
    "climate_monitor",
    "sustainability",
    "climate_news",
    "climate_assistant",
    "about",
}


# =============================================================================
# NAVIGATION FUNCTION
# =============================================================================

def navigate(page_key: str):
    """
    Navigate between the main EcoGuard AI pages.
    """

    if page_key not in VALID_PAGES:
        page_key = "home"

    st.session_state.page = page_key

    # When leaving Home, clear the selected map location.
    if page_key != "home":
        st.session_state.ecoguard_selected_country = None
        st.session_state.ecoguard_selected_region = None

    st.rerun()


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:

    # -------------------------------------------------------------------------
    # BRAND
    # -------------------------------------------------------------------------

    st.markdown(
        '<div class="sidebar-title">🌍 EcoGuard AI</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Climate Intelligence &amp; Sustainability'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # HOME
    # -------------------------------------------------------------------------

    if st.button(
        "Home",
        key="nav_home",
        use_container_width=True,
    ):
        navigate("home")

    # -------------------------------------------------------------------------
    # CLIMATE RISKS
    # -------------------------------------------------------------------------

    st.markdown(
        '<div class="sidebar-section">Climate Risks</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "Heatwave",
        key="nav_heatwave",
        use_container_width=True,
    ):
        st.session_state.climate_risk_section = "heatwave"
        navigate("climate_risks")

    if st.button(
        "Heavy Rain & Flood",
        key="nav_flood",
        use_container_width=True,
    ):
        st.session_state.climate_risk_section = "flood"
        navigate("climate_risks")

    if st.button(
        "Drought",
        key="nav_drought",
        use_container_width=True,
    ):
        st.session_state.climate_risk_section = "drought"
        navigate("climate_risks")

    if st.button(
        "Wildfire",
        key="nav_wildfire",
        use_container_width=True,
    ):
        st.session_state.climate_risk_section = "wildfire"
        navigate("climate_risks")

    # -------------------------------------------------------------------------
    # CLIMATE MONITOR
    # -------------------------------------------------------------------------

    st.markdown(
        '<div class="sidebar-section">Climate Monitor</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "Temperature Trends",
        key="nav_temperature_trends",
        use_container_width=True,
    ):
        st.session_state.climate_monitor_section = "temperature"
        navigate("climate_monitor")

    if st.button(
        "Ice & Glaciers",
        key="nav_ice_glaciers",
        use_container_width=True,
    ):
        st.session_state.climate_monitor_section = "ice"
        navigate("climate_monitor")

    if st.button(
        "Sea Level",
        key="nav_sea_level",
        use_container_width=True,
    ):
        st.session_state.climate_monitor_section = "sea"
        navigate("climate_monitor")

    if st.button(
        "Ecosystems",
        key="nav_ecosystems",
        use_container_width=True,
    ):
        st.session_state.climate_monitor_section = "ecosystems"
        navigate("climate_monitor")

    # -------------------------------------------------------------------------
    # SUSTAINABILITY
    # -------------------------------------------------------------------------

    st.markdown(
        '<div class="sidebar-section">Sustainability</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "Carbon Footprint",
        key="nav_carbon",
        use_container_width=True,
    ):
        st.session_state.sustainability_section = "carbon"
        navigate("sustainability")

    if st.button(
        "Waste & Recycling",
        key="nav_waste",
        use_container_width=True,
    ):
        st.session_state.sustainability_section = "waste"
        navigate("sustainability")

    # -------------------------------------------------------------------------
    # CLIMATE NEWS
    # -------------------------------------------------------------------------

    if st.button(
        "Climate News",
        key="nav_climate_news",
        use_container_width=True,
    ):
        navigate("climate_news")

    # -------------------------------------------------------------------------
    # CLIMATE ASSISTANT
    # -------------------------------------------------------------------------

    if st.button(
        "Climate Assistant",
        key="nav_climate_assistant",
        use_container_width=True,
    ):
        navigate("climate_assistant")

    # -------------------------------------------------------------------------
    # ABOUT
    # -------------------------------------------------------------------------

    if st.button(
        "About EcoGuard",
        key="nav_about",
        use_container_width=True,
    ):
        navigate("about")

    # -------------------------------------------------------------------------
    # FOOTER
    # -------------------------------------------------------------------------

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-footer">Made by V.Madhuvanthi</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# CURRENT PAGE
# =============================================================================

current_page = st.session_state.page


# =============================================================================
# PAGE ROUTING
# =============================================================================

# -----------------------------------------------------------------------------
# HOME
# -----------------------------------------------------------------------------

if current_page == "home":

    pg_home.show()
       


# -----------------------------------------------------------------------------
# CLIMATE RISKS
# -----------------------------------------------------------------------------

elif current_page == "climate_risks":

    risk_section = st.session_state.get(
        "climate_risk_section",
        "landing",
    )

    if risk_section == "heatwave":

        pg_risks.show_heatwave()

    elif risk_section == "flood":

        pg_risks.show_flood()

    elif risk_section == "drought":

        pg_risks.show_drought()

    elif risk_section == "wildfire":

        pg_risks.show_wildfire()

    else:

        pg_risks.show_landing(
            nav_callback=navigate
        )


# -----------------------------------------------------------------------------
# CLIMATE MONITOR
# -----------------------------------------------------------------------------

elif current_page == "climate_monitor":

    pg_monitor.show()


# -----------------------------------------------------------------------------
# SUSTAINABILITY
# -----------------------------------------------------------------------------

elif current_page == "sustainability":

    sustainability_section = st.session_state.get(
        "sustainability_section",
        "landing",
    )

    if sustainability_section == "carbon":

        pg_sus.show_carbon()

    elif sustainability_section == "waste":

        pg_sus.show_waste()

    else:

        pg_sus.show_landing(
            nav_callback=navigate
        )


# -----------------------------------------------------------------------------
# CLIMATE NEWS
# -----------------------------------------------------------------------------

elif current_page == "climate_news":

    pg_news.show()


# -----------------------------------------------------------------------------
# CLIMATE ASSISTANT
# -----------------------------------------------------------------------------

elif current_page == "climate_assistant":

    pg_assistant.show()


# -----------------------------------------------------------------------------
# ABOUT ECOGUARD
# -----------------------------------------------------------------------------

elif current_page == "about":

    pg_about.show()


# =============================================================================
# FALLBACK
# =============================================================================

else:

    st.session_state.page = "home"
    st.session_state.ecoguard_selected_country = None
    st.session_state.ecoguard_selected_region = None

