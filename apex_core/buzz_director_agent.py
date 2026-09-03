"""
buzz_director_agent.py
Main Onboarding Director Agent (Buzz Leader) for Apex Luxury AI.
Coordinates the specialist agent workforce (@Buzz-MLS, @Buzz-Scheduler, @Buzz-Deployer)
to autonomously onboard new Realtors.
"""

import json
import uuid
from typing import Dict, Any, List
from apex_core.supabase_agent import SupabaseAutonomousAgent
from apex_core.vapi_agent import VapiAutonomousAgent
try:
    from apex_core.apex_models import RealtorProfile
    from apex_core.buzz_specialists import (
        MLSIdxSpecialistAgent,
        SchedulingSpecialistAgent,
        SiteDeploymentSpecialistAgent
    )
except ModuleNotFoundError:
    from apex_models import RealtorProfile
    from buzz_specialists import (
        MLSIdxSpecialistAgent,
        SchedulingSpecialistAgent,
        SiteDeploymentSpecialistAgent
    )

class BuzzOnboardingDirectorAgent:
    """
    Main Director Agent that greets new Realtors and dispatches tasks to specialist agents.
    """

    def __init__(self, director_name: str = "Buzz Director"):
        self.director_name = director_name
        self.mls_agent = MLSIdxSpecialistAgent()
        self.scheduler_agent = SchedulingSpecialistAgent()
        self.deployer_agent = SiteDeploymentSpecialistAgent()
        
        # Initialize Core Backend Agents
        self.db_agent = SupabaseAutonomousAgent()
        self.voice_agent = VapiAutonomousAgent()
        
        self.realtors: Dict[str, Dict[str, Any]] = {}

    def onboard_new_realtor(self, intake_data: Dict[str, Any]):
        realtor_id = f"realtor_{uuid.uuid4().hex[:8]}"
        full_name = intake_data.get("full_name", "Valued Realtor")
        email = intake_data.get("email", "")
        phone = intake_data.get("phone", "")
        brokerage = intake_data.get("brokerage", "Apex Luxury Real Estate")
        mls_id = intake_data.get("mls_id", "")
        showingtime_url = intake_data.get("showingtime_url", "")

        yield {
            "event": "drawer_step",
            "step": "INIT_ONBOARDING",
            "message": f"[{self.director_name}] New Realtor onboarding initiated for: {full_name}"
        }

        # Core Task: Provision Database Record in Supabase
        yield {
            "event": "drawer_step",
            "step": "PROVISION_DB",
            "message": f"[{self.director_name}] Provisioning Supabase Database Record..."
        }
        self.db_agent.provision_tables()
        db_result = self.db_agent.provision_realtor_data({
            "name": full_name,
            "email": email,
            "phone": phone,
            "brokerage": brokerage
        })

        # Core Task: Provision Vapi Voice Assistant
        yield {
            "event": "drawer_step",
            "step": "PROVISION_VOICE",
            "message": f"[{self.director_name}] Provisioning Vapi Voice Assistant..."
        }
        voice_result = self.voice_agent.provision_voice_assistant(full_name, phone)

        # Task 1: Dispatch MLS Specialist
        yield {
            "event": "drawer_step",
            "step": "DISPATCH_MLS",
            "message": f"[{self.director_name}] Dispatching @Buzz-MLS-Specialist..."
        }
        mls_result = self.mls_agent.verify_mls_credentials(mls_id, brokerage)

        # Task 2: Dispatch Scheduler Specialist
        yield {
            "event": "drawer_step",
            "step": "DISPATCH_SCHEDULER",
            "message": f"[{self.director_name}] Dispatching @Buzz-Scheduler-Specialist..."
        }
        scheduler_result = self.scheduler_agent.configure_showingtime(showingtime_url)

        # Task 3: Dispatch Site Deployment Specialist
        yield {
            "event": "drawer_step",
            "step": "DISPATCH_DEPLOYER",
            "message": f"[{self.director_name}] Dispatching @Buzz-Deployer-Specialist..."
        }
        deploy_result = self.deployer_agent.deploy_luxury_site(full_name, "ULTRA_LUXURY")

        # Compile Complete Onboarding Report
        onboarding_record = {
            "realtor_id": realtor_id,
            "full_name": full_name,
            "brokerage": brokerage,
            "email": email,
            "phone": phone,
            "db_provisioning": db_result,
            "voice_assistant": voice_result,
            "mls_verification": mls_result,
            "scheduler_integration": scheduler_result,
            "site_deployment": deploy_result,
            "status": "ONBOARDING_COMPLETE"
        }

        self.realtors[realtor_id] = onboarding_record

        yield {
            "event": "content",
            "content": f"Autonomous Onboarding Complete! Welcome to Apex Luxury AI, {full_name}.\n\n```json\n{json.dumps(onboarding_record, indent=2)}\n```",
            "raw_response": onboarding_record,
            "provenance": "Apex Luxury AI - Buzz Core",
            "is_fallback": False
        }
        
        yield {
            "event": "done",
            "status": "COMPLETED"
        }


if __name__ == "__main__":
    buzz_director = BuzzOnboardingDirectorAgent()

    print("=== BUZZ AUTONOMOUS ONBOARDING WORKFORCE TEST ===")
    sample_signup = {
        "full_name": "Priscilla Vance",
        "email": "priscilla@luxuryfl.com",
        "phone": "+1 (239) 555-0199",
        "brokerage": "Vance Luxury Properties",
        "mls_id": "FL-MLS-99482",
        "showingtime_url": "https://showingtime.com/vance-luxury"
    }

    result = buzz_director.onboard_new_realtor(sample_signup)
    print("\nFINAL ONBOARDING REPORT:")
    print(json.dumps(result, indent=2))
