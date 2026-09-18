# =============================================================================
# EcoGuard AI - Module 1: Flood Risk Prediction Assistant
# =============================================================================

def assess_flood_risk(location: str, rainfall_mm: float, proximity: str) -> dict:
    risk_score = 0
    if rainfall_mm < 20:
        risk_score += 10
    elif rainfall_mm < 80:
        risk_score += 30
    else:
        risk_score += 60

    proximity_scores = {
        "Far (> 5 km)": 5,
        "Moderate (1–5 km)": 20,
        "Close (< 1 km)": 40,
    }
    risk_score += proximity_scores.get(proximity, 0)

    if risk_score < 30:
        risk_level = "Low"
        recommendation = (
            "No immediate flood risk detected. Stay informed about weather forecasts "
            "and keep an emergency kit ready."
        )
    elif risk_score < 65:
        risk_level = "Moderate"
        recommendation = (
            "Moderate flood risk. Avoid low-lying areas, monitor local alerts, "
            "and prepare an evacuation plan."
        )
    else:
        risk_level = "High"
        recommendation = (
            "High flood risk. Move to higher ground immediately, follow official "
            "evacuation instructions, and avoid flooded roads."
        )

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "recommendation": recommendation,
    }


def get_safety_tips() -> list:
    return [
        "Keep an emergency kit with water, food, and first-aid supplies.",
        "Know your local evacuation routes in advance.",
        "Avoid walking or driving through floodwaters.",
        "Move important documents and valuables to higher floors.",
        "Sign up for local weather and flood alert notifications.",
        "Keep drains and gutters clear of debris.",
    ]
