"""
Rideshare Profit Copilot - Core Parsing & Scoring Engine
Supports: Uber Driver, Lyft Driver, Walmart Spark
Extracts offer pay, mileage, duration, and returns audio/visual verdicts.
"""

import re
from typing import Dict, Any, Optional

DEFAULT_CONFIG = {
    "min_per_mile": 1.75,      # Minimum acceptable rate per total mile ($)
    "min_per_hour": 28.00,     # Minimum acceptable rate per hour ($)
    "max_pickup_miles": 5.0,   # Warn if pickup distance exceeds this (miles)
    "max_pickup_mins": 12.0,   # Warn if pickup duration exceeds this (minutes)
}

def detect_app_signature(text: str) -> str:
    """
    Identifies whether the screen belongs to Uber, Lyft, or Walmart Spark.
    """
    text_lower = text.lower()
    
    # Walmart Spark indicators
    if any(k in text_lower for k in ["spark", "walmart", "delivery offer", "orders (", "batch"]):
        return "Spark"
        
    # DoorDash indicators
    if any(k in text_lower for k in ["doordash", "dasher", "accept by", "subtotal", "red card", "items ("]):
        return "DoorDash"

    # Uber Eats vs Uber Rides
    if "eats" in text_lower or "restaurant" in text_lower or "deliver" in text_lower or "dropoff order" in text_lower:
        return "Uber Eats"
        
    # Lyft indicators
    if any(k in text_lower for k in ["lyft", "arrive in", "ride challenge", "bonus zone", "scheduled pickup"]):
        return "Lyft"
        
    # Uber Rides indicators
    if any(k in text_lower for k in ["trip radar", "uber", "exclusive", "match", "upfront fare", "comfort", "uberx", "points"]):
        return "Uber"
        
    # Fallback heuristics
    if "radar" in text_lower or "exclusive" in text_lower:
        return "Uber"
        
    return "Unknown"

def extract_offer_metrics(app: str, text: str) -> Dict[str, Optional[float]]:
    """
    Extracts pay ($), miles, and duration (minutes) from OCR text based on app patterns.
    """
    metrics = {
        "pay": None,
        "total_miles": None,
        "pickup_miles": None,
        "trip_miles": None,
        "duration_mins": None,
    }
    
    # 1. Extract Dollar Pay ($XX.XX or $XX)
    pay_matches = re.findall(r"\$\s*(\d+(?:\.\d{2})?)", text)
    if pay_matches:
        # Take the most prominent or largest reasonable fare
        fares = [float(p) for p in pay_matches]
        # Avoid zero or tiny amounts if larger fare exists
        valid_fares = [f for f in fares if 2.0 <= f <= 500.0]
        if valid_fares:
            metrics["pay"] = max(valid_fares)
        else:
            metrics["pay"] = fares[0]

    # 2. Extract Miles (e.g., '3.4 mi', '12.5 miles', '15 mi')
    mile_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:mi|miles|mile)", text, re.IGNORECASE)
    if mile_matches:
        miles_floats = [float(m) for m in mile_matches]
        # In Uber / Lyft, multiple distances might be shown (pickup miles and trip miles)
        # Or a single total distance like '4.2 mi total'
        if "total" in text.lower():
            # If explicit total mentioned
            metrics["total_miles"] = max(miles_floats)
        elif len(miles_floats) == 1:
            metrics["total_miles"] = miles_floats[0]
        else:
            # Often first is pickup, second is trip or vice versa.
            # Total is typically the sum if both are short, or the largest if one is total.
            metrics["total_miles"] = max(miles_floats)

    # 3. Extract Duration (e.g., '14 min', '25 mins', '1 hr 10 min')
    hour_match = re.search(r"(\d+)\s*(?:hr|hour|hours)", text, re.IGNORECASE)
    min_match = re.search(r"(\d+)\s*(?:min|mins|minute|minutes)", text, re.IGNORECASE)
    
    total_mins = 0.0
    if hour_match:
        total_mins += float(hour_match.group(1)) * 60.0
    if min_match:
        total_mins += float(min_match.group(1))
        
    if total_mins > 0:
        metrics["duration_mins"] = total_mins

    return metrics

def evaluate_offer(metrics: Dict[str, Optional[float]], config: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Evaluates profitability against configured rules.
    """
    cfg = config or DEFAULT_CONFIG
    pay = metrics.get("pay")
    miles = metrics.get("total_miles")
    duration = metrics.get("duration_mins")
    
    if not pay or not miles or miles <= 0:
        return {
            "verdict": "UNKNOWN",
            "color": "gray",
            "per_mile": 0.0,
            "per_hour": 0.0,
            "reason": "Could not extract complete pay or distance data.",
            "speech": "Offer details unclear. Check screen."
        }
        
    per_mile = pay / miles
    per_hour = (pay / (duration / 60.0)) if (duration and duration > 0) else (per_mile * 20.0) # default assumption ~20mph
    
    min_mile = cfg.get("min_per_mile", 1.75)
    min_hour = cfg.get("min_per_hour", 28.00)
    
    is_good_mile = per_mile >= min_mile
    is_good_hour = per_hour >= min_hour
    
    if is_good_mile and is_good_hour:
        verdict = "GREEN"
        color = "#00E676" # Neon green
        action = "TAKE IT"
    elif is_good_mile or (per_mile >= min_mile * 0.9):
        verdict = "YELLOW"
        color = "#FFD600" # Yellow
        action = "BORDERLINE"
    else:
        verdict = "RED"
        color = "#FF1744" # Red
        action = "PASS"
        
    return {
        "verdict": verdict,
        "color": color,
        "action": action,
        "per_mile": round(per_mile, 2),
        "per_hour": round(per_hour, 2),
        "pay": round(pay, 2),
        "miles": round(miles, 1),
        "duration_mins": round(duration, 0) if duration else None
    }

def generate_voice_announcement(app: str, evaluation: Dict[str, Any]) -> str:
    """
    Generates concise, natural speech optimized for car speakers.
    Example: 'Uber Green. $2.40 a mile, 4 miles total.'
    """
    verdict = evaluation["verdict"]
    if verdict == "UNKNOWN":
        return f"{app} offer detected. Check screen."
        
    per_mile = evaluation["per_mile"]
    miles = evaluation["miles"]
    pay = evaluation["pay"]
    
    # Format dollars and cents naturally
    rate_str = f"{per_mile:.2f}"
    
    if verdict == "GREEN":
        return f"{app} Green. {rate_str} dollars a mile. {miles} miles total."
    elif verdict == "YELLOW":
        return f"{app} Yellow. {rate_str} dollars a mile. Pass or take quick."
    else:
        return f"{app} Red. {rate_str} a mile. Pass."

def process_screen_text(raw_text: str, config: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Full pipeline: text in -> verdict + audio announcement out.
    """
    app = detect_app_signature(raw_text)
    metrics = extract_offer_metrics(app, raw_text)
    evaluation = evaluate_offer(metrics, config)
    speech = generate_voice_announcement(app, evaluation)
    
    return {
        "app": app,
        "metrics": metrics,
        "evaluation": evaluation,
        "speech": speech
    }
