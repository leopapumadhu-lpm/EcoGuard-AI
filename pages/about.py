# =============================================================================
# EcoGuard AI - About Page
# =============================================================================

import streamlit as st
from utils.ui_components import page_header, section_divider, info_card, footer


def show():
    page_header("ℹ️", "About EcoGuard AI", "Climate Intelligence & Sustainability Platform")

    st.markdown(
        """
        **EcoGuard AI** is an educational climate intelligence and sustainability platform
        designed to help users understand environmental risks, explore climate trends,
        estimate their carbon footprint, and learn practical actions for climate resilience.

        Built for the **1M1B AI for Sustainability Virtual Internship** in collaboration
        with **IBM SkillsBuild** and **AICTE**.
        """
    )

    section_divider("🌐 UN SUSTAINABLE DEVELOPMENT GOALS")
    sdg_cols = st.columns(4)
    sdgs = [
        ("🎯", "SDG 13", "Climate Action",        "Core focus — climate risk awareness, resilience, and individual action."),
        ("🏙️", "SDG 11", "Sustainable Cities",    "Flood risk assessment and climate-risk tools for urban communities."),
        ("♻️", "SDG 12", "Responsible Consumption","Carbon footprint estimation and practical waste-reduction guidance."),
        ("🌿", "SDG 15", "Life on Land",           "Climate awareness on deforestation, biodiversity, and ecosystems."),
    ]
    for col, (icon, sdg, title, desc) in zip(sdg_cols, sdgs):
        with col:
            st.markdown(
                f'<div class="eco-card" style="text-align:center;">'
                f'<div style="font-size:2rem;">{icon}</div>'
                f'<h4 style="color:#059669;">{sdg}</h4>'
                f'<strong>{title}</strong><p style="margin-top:6px;">{desc}</p></div>',
                unsafe_allow_html=True,
            )

    section_divider("🗺️ CORE MODULES")
    modules = [
        ("🌡️", "Heatwave Risk",          "Assess extreme heat conditions based on temperature and humidity."),
        ("🌧️", "Heavy Rain & Flood Risk", "Real-time rainfall data via Open-Meteo + indicative flood risk scoring."),
        ("💧", "Drought Risk",            "Indicative water-scarcity assessment based on precipitation and temperature."),
        ("🔥", "Wildfire Risk",           "Fire-spread risk assessment from temperature, humidity and dryness."),
        ("🌍", "Climate Monitor",         "Long-term climate trend visualisations — temperature, ice, sea level, ecosystems."),
        ("🌱", "Carbon Footprint",        "Estimate personal annual CO₂e from transport, energy, and diet."),
        ("♻️", "Waste & Recycling",       "Practical guidance on responsible disposal and recycling of everyday items."),
        ("🤖", "Climate Assistant",       "Keyword-based Q&A chatbot. IBM watsonx.ai integration planned for Phase 4."),
    ]
    mc1, mc2 = st.columns(2)
    for i, (icon, title, desc) in enumerate(modules):
        with (mc1 if i % 2 == 0 else mc2):
            info_card(f"{icon} {title}", desc)

    section_divider("🛠️ TECHNOLOGY")
    tech_cols = st.columns(3)
    tech = [
        ("🐍", "Python",         "Core programming language"),
        ("📊", "Streamlit",      "Web application framework"),
        ("🌐", "Open-Meteo API", "Live rainfall & weather data"),
        ("📈", "Pandas / Charts","Data handling and visualisation"),
        ("🤖", "IBM watsonx.ai", "AI assistant (planned — Phase 4)"),
        ("🔍", "RAG / Vector DB","Knowledge retrieval (planned — Phase 4)"),
    ]
    for i, (icon, name, role) in enumerate(tech):
        with tech_cols[i % 3]:
            st.markdown(f'<div class="eco-card"><h4>{icon} {name}</h4><p>{role}</p></div>',
                        unsafe_allow_html=True)

    section_divider("🗓️ DEVELOPMENT ROADMAP")
    phases = [
        ("✅", "Phase 1", "UI/UX Foundation — complete navigation, all page layouts, placeholder data"),
        ("🔧", "Phase 2", "Live Climate Data — Open-Meteo weather API for all risk modules"),
        ("🔧", "Phase 3", "Carbon & Sustainability — full calculation engine and progress tracking"),
        ("🔧", "Phase 4", "IBM watsonx.ai Integration — Granite-powered Climate Assistant with RAG"),
        ("🔧", "Phase 5", "Live Global Datasets — NASA, NOAA, news APIs, real climate indicators"),
    ]
    for status, phase, description in phases:
        color = "#065f46" if status == "✅" else "#374151"
        st.markdown(
            f"<div style='padding:8px 0;border-bottom:1px solid #f3f4f6;'>"
            f"<span style='font-size:1.1rem;'>{status}</span> "
            f"<strong style='color:{color};'>{phase}:</strong> "
            f"<span style='color:#6b7280;font-size:0.9rem;'>{description}</span></div>",
            unsafe_allow_html=True,
        )

    section_divider("⚠️ DISCLAIMER")
    st.warning(
        "**EcoGuard AI is an educational project.** Climate-risk results are indicative "
        "assessments and should not be treated as official emergency warnings or professional "
        "environmental forecasts. Always follow guidance from official authorities."
    )
    footer()
