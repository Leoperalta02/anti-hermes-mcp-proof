"""
apex_models.py
Data models and schemas for Apex Luxury AI Realtors, Properties, and Leads.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RealtorProfile(BaseModel):
    realtor_id: str
    full_name: str
    brokerage: str
    email: str
    phone: str
    mls_id: Optional[str] = None
    showingtime_url: Optional[str] = None
    zipforms_url: Optional[str] = None
    brand_tier: str = "ULTRA_LUXURY"  # ULTRA_LUXURY, HIGH_END, STANDARD
    active: bool = True

class PropertyListing(BaseModel):
    listing_id: str
    address: str
    price: float
    beds: int
    baths: float
    sqft: int
    property_type: str = "Luxury Estate"
    features: List[str] = []
    images: List[str] = []

class BuyerLead(BaseModel):
    lead_id: str
    name: str
    email: str
    phone: str
    budget: float
    timeframe: str
    pre_approved: bool = False
    preferred_locations: List[str] = []
    notes: Optional[str] = None

class ModelFailoverCascade(BaseModel):
    paid_subscriptions_only: bool = True
    primary_model: str = "gpt-5.6-luna"  # Paid ChatGPT/Codex Subscription
    fallback_models: List[str] = Field(
        default_factory=lambda: ["grok-2-latest", "claude-3.7-sonnet", "gpt-4o"]
    )
    max_retries_per_model: int = 2
    retry_delay_seconds: float = 0.5
    circuit_breaker_enabled: bool = True

    def get_failover_sequence(self) -> List[str]:
        # Filter out free tier endpoints
        free_tier_keywords = ["free_tier", "gemini-3.6-flash-free", "generativelanguage"]
        raw_sequence = [self.primary_model] + self.fallback_models
        sequence = []
        for model in raw_sequence:
            if model not in sequence and not any(kw in model.lower() for kw in free_tier_keywords):
                sequence.append(model)
        return sequence

class AgentModelConfig(BaseModel):
    agent_name: str
    role: str
    model_cascade: ModelFailoverCascade = Field(default_factory=ModelFailoverCascade)


