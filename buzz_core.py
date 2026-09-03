#!/usr/bin/env python3
"""
buzz_core.py: Buzz Agent Baseline Core Engine
Handles vault secret resolution, Nikki Playbook integration, Security Model Provenance tagging,
and real-time event streaming for the Buzz Client Response Drawer.
"""

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, Any, Generator, Tuple

WORKSPACE_ROOT = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof").resolve()
VAULT_DIR = WORKSPACE_ROOT / "vault_backup"

# Forced Baseline Client Drawer Configuration
BUZZI_CONFIG = {
    "profile_name": "buzz-core-cos",
    "agent_drawer_visible": True,
    "stream_events": True,
    "side_panel_response_view": True,
    "security_tier": "TIER-1 WORKER (Scoped CoPilot)",
    "surface": "Buzz Client Web Workspace",
    "local_gpu_fallback": True
}

def load_vault_secrets() -> Dict[str, Any]:
    """Loads credentials from vault_backup/vault_secrets.json."""
    secrets_file = VAULT_DIR / "vault_secrets.json"
    if secrets_file.exists():
        try:
            with open(secrets_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def check_vault_assets() -> Dict[str, str]:
    """Verifies existence of vault assets."""
    assets = [
        "google_oauth_token.json",
        "vault_secrets.json",
        "NIKKI_CONVERSION_PLAYBOOK.md",
        "gpu_bridge.py",
        "PROJECT_BLUEPRINT_AI_HIGHLEVEL.md",
        "SECURITY_MODEL.md"
    ]
    res = {}
    for a in assets:
        path = VAULT_DIR / a
        res[a] = "OK" if path.exists() else "MISSING"
    return res

def load_nikki_playbook() -> str:
    """Loads Nikki Conversion Playbook content."""
    playbook_file = VAULT_DIR / "NIKKI_CONVERSION_PLAYBOOK.md"
    if playbook_file.exists():
        try:
            with open(playbook_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
    return ""

def format_provenance_banner(tier: str = "TIER-1 WORKER (Scoped CoPilot)", role: str = "Buzzi RealEstate CoPilot", engine: str = "Gemini Flash / Local Fallback", session_id: str = "Buzzi-001") -> str:
    """Generates mandatory security provenance banner per SECURITY_MODEL.md."""
    banner = (
        f"🛡️ [SURFACE: {BUZZI_CONFIG['surface']} | TIER: {tier}]\n"
        f"⚙️ [ROLE: {role} | ENGINE: {engine} | SESSION: #{session_id}]\n"
        "────────────────────────────────────────\n"
    )
    return banner



def get_nikki_playbook_response(query: str) -> str:
    """Generates playbook response based on query keywords."""
    q_lower = query.lower()

    if "browsing" in q_lower:
        script = (
            "🥋 **Nikki's Playbook Response (Objection: 'Just Browsing')**\n\n"
            "> *\"Awesome — what are you browsing for?\"* (Mirror their exact word!)\n\n"
            "**Next Step — Priority Criteria Discovery:**\n"
            "1. *\"Are you thinking an investment property or a place for yourself?\"*\n"
            "2. *\"How many bedrooms and bathrooms are you looking at?\"*\n"
            "3. *\"If everything goes according to plan, when would you be moved into your next home?\"*"
        )
    elif "rate" in q_lower or "interest" in q_lower:
        script = (
            "🥋 **Nikki's Playbook Response (Objection: 'Waiting for Rates to Drop')**\n\n"
            "> *\"What sort of interest rate would you be comfortable with? Have you considered builder rate buydown incentives?\"*\n\n"
            "**Key Principle:** The market = their personal impact. Marry the house, date the rate!"
        )
    elif "friend" in q_lower or "relative" in q_lower or "cousin" in q_lower:
        script = (
            "🥋 **Nikki's Playbook Response (Objection: 'Friend/Cousin is an Agent')**\n\n"
            "> *\"This is the largest transaction in most people's lives. Just like with serious health matters, you get a second opinion. I'd love to be that second set of eyes for you.\"*"
        )
    elif "not ready" in q_lower or "pause" in q_lower:
        script = (
            "🥋 **Nikki's Playbook Response (Objection: 'Not Ready Yet')**\n\n"
            "⭐ **The Golden Question:**\n"
            "> *\"Let me ask you this — if I found you the perfect home, would you want to know about it?\"*"
        )
    else:
        script = (
            "🥋 **Nikki's Training Dojo & Conversion Playbook Engine**\n\n"
            "🎯 **The 4 Goals of Every Call:**\n"
            "1. Build rapport\n"
            "2. Uncover motivation & pain points\n"
            "3. Establish timeline\n"
            "4. Book the appointment (Two-Option Close)\n\n"
            "✔️ **Capture Priority Checklist:** Motivation, Timeline, Preferred Area, Property Type, Price Range, Finance vs Cash."
        )
    return script



def stream_buzz_response(query: str, channel: str = "all") -> Generator[Dict[str, Any], None, None]:
    """
    Streams step-by-step events for the Buzz Client Response Drawer (agent_drawer_visible: true).
    Yields dict objects representing SSE events.
    """
    session_id = f"SES-{int(time.time() * 1000) % 100000:05d}"
    provenance = format_provenance_banner(session_id=session_id)

    # Step 1: Initializing request
    yield {
        "event": "drawer_step",
        "step": "INIT",
        "message": "Initializing Buzzi Agent baseline request...",
        "session_id": session_id,
        "config": BUZZI_CONFIG
    }
    time.sleep(0.1)

    # Step 2: Vault verification & provenance attachment
    vault_status = check_vault_assets()
    yield {
        "event": "provenance",
        "banner": provenance,
        "vault": vault_status
    }
    time.sleep(0.1)

    # Step 3: Tool / Playbook selection
    yield {
        "event": "drawer_step",
        "step": "ANALYSIS",
        "message": f"Analyzing prompt under channel '{channel}' and matching Nikki Playbook / Buzz Agent rules..."
    }
    time.sleep(0.1)

    # ----------------------------------------------------
    # NEW APEX LUXURY AI INTERCEPTION (Onboarding Route)
    # ----------------------------------------------------
    q_lower = query.lower()
    if "onboard" in q_lower or "realtor" in q_lower:
        from apex_core.buzz_director_agent import BuzzOnboardingDirectorAgent
        director = BuzzOnboardingDirectorAgent()
        
        # Extract a name if possible, or use a default
        name = "Valued Realtor"
        if "priscilla" in q_lower:
            name = "Priscilla Vance"
            
        intake_data = {
            "full_name": name,
            "email": f"{name.lower().replace(' ', '.')}@luxuryfl.com",
            "phone": "+1 (239) 555-0199",
            "brokerage": "Apex Luxury Real Estate",
            "mls_id": "FL-MLS-99482",
            "showingtime_url": "https://showingtime.com/apex-luxury"
        }
        
        # Stream the exact SSE events yielded by the director
        for event in director.onboard_new_realtor(intake_data):
            yield event
            time.sleep(0.2)
            
        return # End execution here
    # ----------------------------------------------------

    # Step 4: Execution (Pure Buzz Nikki Playbook)
    raw_response = get_nikki_playbook_response(query)
    is_fallback = True
    
    yield {
        "event": "drawer_step",
        "step": "EXECUTION",
        "message": "Nikki Playbook execution complete."
    }
    time.sleep(0.1)

    # Step 5: Final output payload
    full_output = f"{provenance}\n{raw_response}"
    yield {
        "event": "content",
        "content": full_output,
        "raw_response": raw_response,
        "provenance": provenance,
        "is_fallback": is_fallback
    }

    # Step 6: Done signal
    yield {
        "event": "done",
        "status": "COMPLETED"
    }

if __name__ == "__main__":
    print("=== BUZZ CORE ENGINE TEST ===")
    print("Vault Assets:", check_vault_assets())
    print("\n--- Testing Stream Events (Onboarding Route) ---")
    for evt in stream_buzz_response("Please onboard realtor Priscilla", "onboarding"):
        print(f"[{evt.get('event')}]", json.dumps(evt, indent=2))
