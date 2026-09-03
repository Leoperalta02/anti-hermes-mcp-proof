"""
realtor_api.py
Headless API service for Rosy AI Realtor Copilot.
Exposes endpoints for property valuation, MLS copy generation, and lead qualification.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from rosy_core.rosy_agent import RosyRealEstateAgent

app = FastAPI(
    title="Rosy Real Estate AI Copilot API",
    description="Headless AI engine empowering Realtors with valuation analysis, MLS listing copy generation, and lead qualification.",
    version="1.0.0"
)

rosy = RosyRealEstateAgent()

class PropertyRequest(BaseModel):
    address: str
    beds: int = 3
    baths: int = 2
    sqft: int = 2000
    type: str = "Single Family Home"
    features: List[str] = []

class LeadRequest(BaseModel):
    name: str
    budget: Optional[str] = "Unspecified"
    timeframe: Optional[str] = "Flexible"
    pre_approved: Optional[bool] = False

@app.get("/")
def root():
    return {
        "status": "ONLINE",
        "service": "Rosy Real Estate AI Copilot API",
        "version": "1.0.0",
        "endpoints": [
            "POST /api/valuation",
            "POST /api/mls-description",
            "POST /api/qualify-lead"
        ]
    }

@app.post("/api/valuation")
def analyze_property_valuation(property_data: PropertyRequest):
    try:
        result = rosy.analyze_property(property_data.dict())
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mls-description")
def generate_mls_copy(property_data: PropertyRequest):
    try:
        mls_copy = rosy.generate_mls_description(property_data.dict())
        return {"success": True, "mls_description": mls_copy}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/qualify-lead")
def qualify_lead_entry(lead_data: LeadRequest):
    try:
        qualification = rosy.qualify_lead(lead_data.dict())
        return {"success": True, "qualification": qualification}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
