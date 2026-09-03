"""
Apex Luxury AI — Zero-Friction SMS / iMessage Text Onboarding Router
Handles incoming MMS photos, client chat prompts, and automatic landing page generation triggers.
"""

import os
import shutil
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from apex_core.tenant_manager import tenant_manager, Tenant

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
INCOMING_MESSAGES_LOG = os.path.join(DATA_DIR, "sms_onboarding_log.json")

class TextOnboardingRouter:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def process_incoming_mms(
        self,
        sender_phone: str,
        message_text: str,
        media_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Processes an incoming text message from a client (e.g. Sofia or Toki)
        containing text instructions and/or photo attachments (headshots, flyers).
        """
        timestamp = datetime.utcnow().isoformat()
        
        # 1. Match or create tenant
        matched_tenant = None
        for t in tenant_manager.list_tenants():
            if t.phone_number.replace("-", "").replace(" ", "") in sender_phone.replace("-", "").replace(" ", ""):
                matched_tenant = t
                break

        # 2. Process attached media files
        saved_assets = []
        if media_paths:
            client_asset_dir = os.path.join(
                os.path.dirname(__file__), "..", "assets", "clients", 
                matched_tenant.subdomain_slug if matched_tenant else "new_client"
            )
            os.makedirs(client_asset_dir, exist_ok=True)
            
            for idx, p in enumerate(media_paths):
                if os.path.exists(p):
                    filename = os.path.basename(p)
                    dest_file = os.path.join(client_asset_dir, f"received_{int(datetime.utcnow().timestamp())}_{filename}")
                    shutil.copyfile(p, dest_file)
                    saved_assets.append(dest_file)
                    print(f"[TextRouter] Ingested MMS media from {sender_phone}: {dest_file}")

        # 3. Log event
        log_entry = {
            "timestamp": timestamp,
            "sender_phone": sender_phone,
            "tenant_id": matched_tenant.id if matched_tenant else None,
            "tenant_name": matched_tenant.name if matched_tenant else "New Lead",
            "message_text": message_text,
            "saved_assets": saved_assets,
            "status": "PROCESSED_BY_HERMES"
        }

        # Append to log
        logs = []
        if os.path.exists(INCOMING_MESSAGES_LOG):
            try:
                with open(INCOMING_MESSAGES_LOG, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append(log_entry)
        with open(INCOMING_MESSAGES_LOG, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)

        # 4. Generate Hermes response to the client
        reply_message = self._generate_hermes_reply(matched_tenant, message_text, len(saved_assets))
        return {
            "success": True,
            "log_entry": log_entry,
            "hermes_reply": reply_message
        }

    def _generate_hermes_reply(self, tenant: Optional[Tenant], text: str, asset_count: int) -> str:
        name = tenant.name if tenant else "there"
        if asset_count > 0:
            return (
                f"Got your {asset_count} image(s), {name}! 📸✨ "
                f"Fizz is adding them to your custom landing page right now. "
                f"We'll have your live preview ready in 2 minutes!"
            )
        else:
            return (
                f"Understood, {name}! Hermes and the team have recorded your request: '{text}'. "
                f"Updating your system now."
            )

text_router = TextOnboardingRouter()

if __name__ == "__main__":
    test_res = text_router.process_incoming_mms(
        sender_phone="786-461-0049",
        message_text="Here is my headshot and flyer! Make the headline in gold for Florida accidents.",
        media_paths=["assets/clients/sofia_headshot.png", "assets/clients/sofia_flyer.png"]
    )
    print("Router Test Result:")
    print(json.dumps(test_res, indent=2))
