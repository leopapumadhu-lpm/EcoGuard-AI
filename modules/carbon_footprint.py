# =============================================================================
# EcoGuard AI - Module 2: Carbon Footprint Estimation Tool
# =============================================================================
# Sources: IPCC, UK DESNZ, EPA (US), IEA

TRANSPORT_EMISSION_FACTORS = {
    "Car (Petrol)":      0.192,
    "Car (Diesel)":      0.171,
    "Car (Electric)":    0.053,
    "Public Transport":  0.089,
    "Bicycle / Walk":    0.0,
}

ELECTRICITY_EMISSION_FACTOR = 0.475

DIET_EMISSION_FACTORS = {
    "Meat-heavy":             160.0,
    "Balanced (Meat + Veg)":  100.0,
    "Vegetarian":              60.0,
    "Vegan":                   40.0,
}


def estimate_carbon_footprint(
    transport_type: str,
    km_per_month: float,
    electricity_kwh: float,
    diet_type: str,
) -> dict:
    transport_kg  = round(TRANSPORT_EMISSION_FACTORS.get(transport_type, 0.0) * km_per_month, 2)
    electricity_kg = round(ELECTRICITY_EMISSION_FACTOR * electricity_kwh, 2)
    diet_kg       = round(DIET_EMISSION_FACTORS.get(diet_type, 100.0), 2)
    total_kg      = round(transport_kg + electricity_kg + diet_kg, 2)
    annual_kg     = round(total_kg * 12, 2)

    global_avg = 416.0
    if total_kg < global_avg * 0.5:
        comparison = "✅ Well below the global average — great job!"
    elif total_kg < global_avg:
        comparison = "🟡 Below the global average — room for improvement."
    elif total_kg < global_avg * 1.5:
        comparison = "🟠 Above the global average — consider reducing key areas."
    else:
        comparison = "🔴 Significantly above the global average — action recommended."

    return {
        "transport_kg":   transport_kg,
        "electricity_kg": electricity_kg,
        "diet_kg":        diet_kg,
        "total_kg":       total_kg,
        "annual_kg":      annual_kg,
        "comparison":     comparison,
    }


def get_reduction_tips(transport_type: str, diet_type: str) -> list:
    tips = [
        "Switch to LED lighting and unplug devices when not in use.",
        "Use cold water for laundry to save energy.",
        "Reduce single-use plastics and prefer reusable alternatives.",
        "Support local and seasonal produce to cut food-miles emissions.",
    ]
    if transport_type in ("Car (Petrol)", "Car (Diesel)"):
        tips.append("Consider carpooling or switching to public transport for regular commutes.")
        tips.append("Transitioning to an electric vehicle could cut your transport emissions by ~70%.")
    elif transport_type == "Car (Electric)":
        tips.append("Charge your EV using renewable energy (solar or green tariff) if possible.")
    if diet_type == "Meat-heavy":
        tips.append("Replacing one meat meal per day with a plant-based option can save ~50 kg CO₂e/month.")
    elif diet_type == "Balanced (Meat + Veg)":
        tips.append("Moving toward a vegetarian diet could halve your food-related emissions.")
    return tips
