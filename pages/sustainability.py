# =============================================================================
# EcoGuard AI - Sustainability Page
# =============================================================================

import streamlit as st
import pandas as pd

from utils.ui_components import (
    page_header, metric_card, risk_metric_card, recommendation_card,
    section_divider, demo_notice, info_card, footer,
)
from modules.carbon_footprint import estimate_carbon_footprint, get_reduction_tips

WASTE_GUIDANCE = {
    "🍌 Food Waste": {
        "disposal": "Compost organic waste at home or use municipal green-waste bins.",
        "avoid":    "Do not put food waste in general recycling or landfill bins.",
        "eco_tip":  "Meal planning reduces food waste by ~30%.",
    },
    "📦 Cardboard": {
        "disposal": "Flatten boxes and place in the paper/cardboard recycling bin.",
        "avoid":    "Do not recycle wet, greasy, or food-contaminated cardboard.",
        "eco_tip":  "Reuse boxes for storage before recycling.",
    },
    "🥤 Plastic": {
        "disposal": "Rinse containers and recycle plastics labelled #1 (PET) and #2 (HDPE).",
        "avoid":    "Do not put plastic bags or polystyrene in kerbside recycling.",
        "eco_tip":  "Choose products with less packaging and carry a reusable bag.",
    },
    "🔋 Batteries": {
        "disposal": "Take batteries to a designated collection point. Never put in general waste.",
        "avoid":    "Do not throw batteries in household waste — they leach toxic chemicals.",
        "eco_tip":  "Switch to rechargeable batteries.",
    },
    "💻 Electronics": {
        "disposal": "Take e-waste to an authorised recycling centre.",
        "avoid":    "Do not discard electronics in general waste — hazardous materials.",
        "eco_tip":  "Extend device life through repair before replacing.",
    },
    "👕 Clothes": {
        "disposal": "Donate wearable clothing to charity. Recycle worn items at brand take-back schemes.",
        "avoid":    "Avoid sending clothing to landfill.",
        "eco_tip":  "Buy second-hand and choose quality over quantity.",
    },
    "🍾 Glass": {
        "disposal": "Rinse and place in a glass recycling bin or bottle bank.",
        "avoid":    "Do not mix glass with general recycling unless your council permits it.",
        "eco_tip":  "Glass is infinitely recyclable — always recycle rather than landfill.",
    },
}


def show_landing(nav_callback=None):
    page_header("🌱", "Sustainability",
                "Tools and guidance to help you live and act more sustainably.")
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            '<div class="risk-overview-card"><div class="risk-icon">🌱</div>'
            '<h4>Carbon Footprint Calculator</h4>'
            '<p>Estimate your annual carbon footprint across transportation, energy, '
            'food, and consumption. Get personalised reduction tips.</p><br></div>',
            unsafe_allow_html=True,
        )
        if st.button("Open Carbon Calculator →", key="sus_carbon", width="stretch"):
            if nav_callback:
                nav_callback("carbon")
    with col2:
        st.markdown(
            '<div class="risk-overview-card"><div class="risk-icon">♻️</div>'
            '<h4>Waste &amp; Recycling Assistant</h4>'
            '<p>Find out how to correctly dispose of and recycle everyday items. '
            'Get practical tips to reduce household waste.</p><br></div>',
            unsafe_allow_html=True,
        )
        if st.button("Open Waste & Recycling →", key="sus_waste", width="stretch"):
            if nav_callback:
                nav_callback("waste")
    footer()


def show_carbon():
    page_header("🌱", "Carbon Footprint Calculator",
                "Estimate your annual carbon emissions and find ways to reduce them.")

    with st.form("carbon_calc_form"):
        section_divider("🚗 TRANSPORTATION")
        tc1, tc2 = st.columns(2)
        with tc1:
            transport = st.selectbox(
                "Primary Mode of Transport",
                ["Car (Petrol)", "Car (Diesel)", "Car (Electric)", "Public Transport", "Bicycle / Walk"],
            )
        with tc2:
            km_per_month = st.number_input("Distance Travelled per Month (km)",
                                           min_value=0, max_value=10000, value=500, step=50)
        section_divider("⚡ ENERGY")
        ec1, ec2 = st.columns(2)
        with ec1:
            electricity_kwh = st.number_input("Monthly Electricity Usage (kWh)",
                                              min_value=0, max_value=5000, value=200, step=10)
        with ec2:
            st.markdown("<small style='color:#6b7280;'>Global average: ~200 kWh/month</small>",
                        unsafe_allow_html=True)
        section_divider("🍽️ FOOD & LIFESTYLE")
        fc1, _ = st.columns(2)
        with fc1:
            diet = st.selectbox("Diet Type",
                                ["Meat-heavy", "Balanced (Meat + Veg)", "Vegetarian", "Vegan"])
        section_divider("🛍️ CONSUMPTION")
        st.markdown("<small style='color:#9ca3af;'>Detailed consumption inputs will be added in Phase 3.</small>",
                    unsafe_allow_html=True)
        submitted = st.form_submit_button("🌱 Calculate My Carbon Footprint", width="stretch")

    if submitted:
        result = estimate_carbon_footprint(transport, km_per_month, electricity_kwh, diet)
        annual_t = round(result["annual_kg"] / 1000, 2)

        section_divider("📊 YOUR CARBON FOOTPRINT")
        rc = st.columns(4)
        with rc[0]: metric_card("🚗", "Transport",    f"{result['transport_kg']} kg",  "CO₂e / month")
        with rc[1]: metric_card("⚡", "Electricity",  f"{result['electricity_kg']} kg","CO₂e / month")
        with rc[2]: metric_card("🍽️", "Diet",         f"{result['diet_kg']} kg",       "CO₂e / month")
        with rc[3]: metric_card("🌱", "Annual Total", f"{annual_t} tCO₂e",            "per year")
        st.markdown(f"**{result['comparison']}**")
        st.caption("Global average: ~5 tCO₂e/year per person.")

        section_divider("📊 EMISSIONS BY CATEGORY")
        st.bar_chart(
            pd.DataFrame(
                {"Emissions (kg CO₂e/month)": [result["transport_kg"], result["electricity_kg"], result["diet_kg"]]},
                index=["🚗 Transport", "⚡ Electricity", "🍽️ Diet"],
            ),
            height=200,
        )

        section_divider("💡 PERSONALISED REDUCTION TIPS")
        for tip in get_reduction_tips(transport, diet):
            recommendation_card("✅", "", tip)

    footer()


def show_waste():
    page_header("♻️", "Waste & Recycling Assistant",
                "Find out how to correctly dispose of everyday items.")
    st.markdown("Select an item below to see the recommended disposal method, what to avoid, and an eco tip.")

    item = st.selectbox("🗑️ Select an item", list(WASTE_GUIDANCE.keys()), key="waste_item_select")
    guidance = WASTE_GUIDANCE[item]
    section_divider(f"♻️ GUIDANCE FOR: {item}")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="eco-card"><h4>✅ Recommended Disposal</h4><p>{guidance["disposal"]}</p></div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="eco-card" style="border-color:#fecaca;"><h4>🚫 What to Avoid</h4><p>{guidance["avoid"]}</p></div>',
                    unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="eco-card" style="border-color:#bbf7d0;"><h4>🌿 Eco Tip</h4><p>{guidance["eco_tip"]}</p></div>',
                    unsafe_allow_html=True)

    section_divider("🌍 GENERAL WASTE REDUCTION TIPS")
    tips = [
        ("🛍️", "Reduce",  "Buy only what you need and choose products with minimal packaging."),
        ("♻️", "Reuse",   "Repair, repurpose, or donate items before discarding them."),
        ("🌿", "Recycle", "Know your local recycling rules — contamination reduces recycling rates."),
        ("🍃", "Compost", "Composting food and garden waste cuts methane from landfill."),
    ]
    tc = st.columns(2)
    for i, (icon, title, body) in enumerate(tips):
        with tc[i % 2]: recommendation_card(icon, title, body)
    footer()
