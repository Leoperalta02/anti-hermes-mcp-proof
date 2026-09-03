"""
apex_core/client_workspace_factory.py
Apex Luxury AI — Autonomous Client Workspace & Agent Factory Engine.
Implements the "AI-Operated Business Deployment Platform" Architecture:

Pipeline:
Lead Capture -> Landing Page Onboard -> Client Workspace Factory -> JIT Agent Assembly -> Operational Execution

Core Principles:
1. Workspace is the Container (Obsidian Vault + Supabase); Agents are Disposable Workers.
2. 6-10 Core Agent Archetypes instantiated on-demand per industry vertical.
3. Human-in-the-Loop (HITL) Founder Approval Card before live agent deployment.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
VAULT_DIR = BASE_DIR / "local_vault" / "obsidian_memory" / "clients"

# 6 Core Disposable Agent Archetypes
AGENT_ARCHETYPES = {
    "lead_intake": {
        "title": "Lead Intake & Triage Specialist",
        "description": "Qualifies incoming leads 24/7, screens urgency, and enforces statutory rules.",
        "model": "gpt-4o"
    },
    "appointment_scheduler": {
        "title": "Appointment & Showing Coordinator",
        "description": "Integrates with Google Calendar / ShowingTime to book private viewings and clinic consultations.",
        "model": "gpt-4-turbo"
    },
    "omnichannel_followup": {
        "title": "Omnichannel SMS & Email Follow-Up Specialist",
        "description": "Nurtures unresponsive leads with personalized value touches.",
        "model": "gemini-2.0-flash"
    },
    "reputation_reviews": {
        "title": "Client Review & Referral Specialist",
        "description": "Automates 5-star Google review collection from satisfied customers post-service.",
        "model": "gemini-2.0-flash"
    },
    "analytics_cro": {
        "title": "Analytics & Conversion Rate Optimizer",
        "description": "Monitors cost-per-lead, conversion rates, and recommends landing page copy tweaks.",
        "model": "grok-2-latest"
    },
    "technical_web_builder": {
        "title": "Fast Web & Landing Page Specialist",
        "description": "Deploys and updates client subdomains, landing page banners, and tracking tags.",
        "model": "gpt-4o"
    }
}

class ClientWorkspaceFactory:
    def __init__(self):
        self.vault_dir = VAULT_DIR
        self.vault_dir.mkdir(parents=True, exist_ok=True)

    def provision_client_workspace(
        self,
        company_name: str,
        vertical: str, # "FL_NO_FAULT_ACCIDENT", "LUXURY_REAL_ESTATE", "HOME_SERVICES", "CUSTOM"
        contact_name: str,
        contact_phone: str,
        contact_email: str
    ) -> Dict[str, Any]:
        """
        Assembles a customized client workspace container and determines the JIT agent team.
        """
        slug = company_name.lower().replace(" ", "_").replace("-", "_")
        channel_name = f"client-{slug}"
        
        # 1. Create Isolated Client Container in Obsidian Vault
        client_dir = self.vault_dir / slug
        client_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Determine Just-In-Time (JIT) Specialist Agent Team based on Vertical
        proposed_agents = self._select_agent_team(vertical, company_name)
        
        # 3. Create Client Dossier & State Manifest (Container owns the state, NOT the agents)
        manifest = {
            "company_name": company_name,
            "slug": slug,
            "channel_name": channel_name,
            "vertical": vertical,
            "contact": {
                "name": contact_name,
                "phone": contact_phone,
                "email": contact_email
            },
            "status": "AWAITING_FOUNDER_APPROVAL",
            "proposed_agent_team": proposed_agents,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        
        manifest_path = client_dir / "workspace_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # 4. Generate the Founder Approval Card
        approval_card = {
            "status": "STAGED_FOR_APPROVAL",
            "channel_name": f"#{channel_name}",
            "client": company_name,
            "vertical": vertical,
            "proposed_agents_count": len(proposed_agents),
            "proposed_agents": [a["name"] for a in proposed_agents],
            "manifest_location": str(manifest_path),
            "approval_prompt": f"Leo, '{company_name}' workspace staged with {len(proposed_agents)} specialist agents. Reply 'Approve' to deploy Buzz channel #{channel_name} and activate workforce."
        }

        return approval_card

    def _select_agent_team(self, vertical: str, company_name: str) -> List[Dict[str, Any]]:
        """Dynamically assembles specialized agent instances from core archetypes."""
        if "ACCIDENT" in vertical.upper() or "PIP" in vertical.upper() or "CLAIM" in vertical.upper():
            return [
                {"name": f"{company_name} 24/7 Triage Coordinator", "archetype": "lead_intake", "model": "gpt-4o"},
                {"name": f"{company_name} Medical Clinic Scheduler", "archetype": "appointment_scheduler", "model": "gpt-4-turbo"},
                {"name": f"{company_name} 14-Day PIP Compliance Monitor", "archetype": "omnichannel_followup", "model": "gemini-2.0-flash"},
                {"name": f"{company_name} Lead Intelligence Analyst", "archetype": "analytics_cro", "model": "grok-2-latest"}
            ]
        elif "REAL_ESTATE" in vertical.upper() or "LUXURY" in vertical.upper():
            return [
                {"name": f"{company_name} Luxury Showing Concierge", "archetype": "lead_intake", "model": "gpt-4o"},
                {"name": f"{company_name} ShowingTime & MLS Scheduler", "archetype": "appointment_scheduler", "model": "gpt-4-turbo"},
                {"name": f"{company_name} VIP Buyer Follow-Up Specialist", "archetype": "omnichannel_followup", "model": "gemini-2.0-flash"},
                {"name": f"{company_name} Luxury Architectural Copywriter", "archetype": "technical_web_builder", "model": "gemini-2.0-flash"}
            ]
        else: # Universal Home Services / Commercial Business
            return [
                {"name": f"{company_name} Lead Intake Agent", "archetype": "lead_intake", "model": "gpt-4o"},
                {"name": f"{company_name} Estimate Booking Coordinator", "archetype": "appointment_scheduler", "model": "gpt-4-turbo"},
                {"name": f"{company_name} Follow-Up & Review Agent", "archetype": "reputation_reviews", "model": "gemini-2.0-flash"},
                {"name": f"{company_name} CRO & Performance Analyst", "archetype": "analytics_cro", "model": "grok-2-latest"}
            ]

workspace_factory = ClientWorkspaceFactory()

if __name__ == "__main__":
    print("🚀 Testing Apex Client Workspace & Agent Factory...")
    
    # Simulate a new commercial roofing client onboarding
    res_roofing = workspace_factory.provision_client_workspace(
        company_name="Acme Roofing Pro",
        vertical="HOME_SERVICES",
        contact_name="Carlos Mendez",
        contact_phone="+13055558822",
        contact_email="carlos@acmeroofing.com"
    )
    print("\n[Acme Roofing Staging Card]:")
    print(json.dumps(res_roofing, indent=2))
