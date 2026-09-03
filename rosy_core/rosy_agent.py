"""
rosy_agent.py
Core execution logic for Rosy AI Real Estate Copilot.
Handles property valuation estimation, MLS copy generation, and lead qualification.
"""

import json
from typing import Dict, Any, List
from rosy_prompts import ROSY_SYSTEM_PROMPT

class RosyRealEstateAgent:
    def __init__(self, agent_name: str = "Rosy", brokerage_name: str = "Gulf Point Real Estate"):
        self.agent_name = agent_name
        self.brokerage_name = brokerage_name

    def analyze_property(self, property_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes property details and generates comparative valuation estimates,
        pricing strategy tiers, and key selling highlights.
        """
        address = property_details.get("address", "Property Location")
        beds = property_details.get("beds", 3)
        baths = property_details.get("baths", 2)
        sqft = property_details.get("sqft", 2000)
        prop_type = property_details.get("type", "Single Family Home")
        features = property_details.get("features", [])

        # Strategic Valuation Logic (Estero / FL Market Base)
        base_rate_min = 285
        base_rate_max = 365
        
        base_val_min = sqft * base_rate_min
        base_val_max = sqft * base_rate_max

        # Premium feature adjustments
        feature_adjustments = 0
        feat_str_list = [f.lower() for f in features]

        if any("pool" in f for f in feat_str_list):
            feature_adjustments += 35000
        if any("lake" in f or "water" in f for f in feat_str_list):
            feature_adjustments += 25000
        if any("roof" in f for f in feat_str_list):
            feature_adjustments += 15000
        if any("gated" in f or "golf" in f for f in feat_str_list):
            feature_adjustments += 20000

        final_min = base_val_min + feature_adjustments
        final_max = base_val_max + feature_adjustments

        pricing_tiers = {
            "conservative": {
                "range": f"${final_min:,.0f} - ${(final_min + final_max)/2 * 0.95:,.0f}",
                "strategy": "Quick sale, competitive positioning for motivated sellers."
            },
            "market_realistic": {
                "range": f"${(final_min + final_max)/2 * 0.95:,.0f} - ${(final_min + final_max)/2 * 1.05:,.0f}",
                "strategy": "Balanced offer target, optimal value matching recent comps."
            },
            "premium": {
                "range": f"${(final_min + final_max)/2 * 1.05:,.0f} - ${final_max:,.0f}",
                "strategy": "High-end positioning highlighting unique amenities & key updates."
            }
        }

        return {
            "property_summary": {
                "address": address,
                "beds": beds,
                "baths": baths,
                "sqft": sqft,
                "type": prop_type,
                "features": features
            },
            "valuation_estimate": {
                "estimated_range": f"${final_min:,.0f} - ${final_max:,.0f}",
                "price_per_sqft_range": f"${base_rate_min} - ${base_rate_max} /sqft",
                "feature_premium_added": f"${feature_adjustments:,.0f}"
            },
            "pricing_tiers": pricing_tiers
        }

    def generate_mls_description(self, property_details: Dict[str, Any]) -> str:
        """
        Generates a polished, ready-to-publish MLS public description.
        """
        address = property_details.get("address", "Prime Real Estate")
        beds = property_details.get("beds", 3)
        baths = property_details.get("baths", 2)
        sqft = property_details.get("sqft", 2000)
        features = property_details.get("features", [])

        feat_bullets = "\n".join([f"• {feat}" for feat in features]) if features else "• Beautiful layout & prime location"

        description = f"""[LUXURY LIVING] — BEAUTIFUL HOME AT {address.upper()}!

Welcome to this exquisite {beds} bedroom, {baths} bathroom property featuring over {sqft:,} sq ft of elegant living space presented by {self.brokerage_name}.

KEY UPDATES & HIGHLIGHTS:
{feat_bullets}

PROPERTY OVERVIEW:
• Open-concept floor plan designed for comfort & modern entertaining
• Prime location close to top-rated schools, dining, and shopping
• Schedule your private viewing today before this gem is off the market!
"""
        return description

    def qualify_lead(self, lead_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Qualifies incoming lead details into structured CRM data.
        """
        name = lead_info.get("name", "Interested Prospect")
        budget = lead_info.get("budget", "Unspecified")
        timeframe = lead_info.get("timeframe", "Flexible")
        pre_approved = lead_info.get("pre_approved", False)

        lead_score = "WARM"
        if pre_approved and budget != "Unspecified":
            lead_score = "HOT 🔥"
        elif not pre_approved and timeframe == "Immediate":
            lead_score = "VERY WARM ☀️"

        return {
            "lead_name": name,
            "qualification_status": lead_score,
            "budget": budget,
            "timeframe": timeframe,
            "pre_approved": pre_approved,
            "recommended_next_step": "Schedule 15-min discovery call & send property match portfolio."
        }


if __name__ == "__main__":
    rosy = RosyRealEstateAgent()
    sample_property = {
        "address": "10450 Stoneybrook Golf Dr, Estero, FL 33928",
        "beds": 3,
        "baths": 2,
        "sqft": 2150,
        "type": "Single Family Home",
        "features": ["Screened lanai + heated pool", "Lake view", "Updated kitchen (quartz)", "New 2024 roof", "Gated community"]
    }

    print("=== ROSY REAL ESTATE AGENT TEST ===")
    analysis = rosy.analyze_property(sample_property)
    print("\nVALUATION ANALYSIS:")
    print(json.dumps(analysis, indent=2))

    print("\nMLS DESCRIPTION:")
    print(rosy.generate_mls_description(sample_property))
