"""
apex_core/vapi_agent.py
Autonomous Voice AI Provisioning Agent for Apex Luxury AI.
Provisions and updates live Vapi Voice Assistants:
1. Celeste ✨ (Luxury Real Estate Voice Concierge)
2. Luna 🌙 (24/7 Florida Accident & No-Fault PIP Bilingual Triage Specialist)
"""

import os
import sys
import json
import requests
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding='utf-8')

class VapiAutonomousAgent:
    def __init__(self):
        self.api_key = ""
        self.base_url = "https://api.vapi.ai"
        self._load_credentials()

    def _load_credentials(self):
        vault_path = os.path.join(os.path.dirname(__file__), "..", "vault_backup", "vault_secrets.json")
        try:
            with open(vault_path, "r") as f:
                secrets = json.load(f)
                self.api_key = secrets.get("vapi_api_key", "")
        except Exception as e:
            print(f"[Vapi Agent] Error loading credentials: {e}")

    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def list_assistants(self) -> List[Dict[str, Any]]:
        try:
            res = requests.get(f"{self.base_url}/assistant", headers=self.get_headers())
            if res.status_code == 200:
                return res.json()
            return []
        except Exception as e:
            print("Error listing assistants:", e)
            return []

    def list_phone_numbers(self) -> List[Dict[str, Any]]:
        try:
            res = requests.get(f"{self.base_url}/phone-number", headers=self.get_headers())
            if res.status_code == 200:
                return res.json()
            return []
        except Exception as e:
            print("Error listing phone numbers:", e)
            return []

    def provision_celeste_real_estate(self) -> Dict[str, Any]:
        """
        Provisions or updates Celeste (Luxury Real Estate Voice Concierge).
        """
        payload = {
            "name": "Celeste ✨ Luxury Real Estate Concierge",
            "firstMessage": "Hello, thank you for calling. My name is Celeste with Apex Luxury Estates. Are you inquiring about one of our private listings, or scheduling a private viewing?",
            "voice": {
                "provider": "11labs",
                "voiceId": "21m00Tcm4TlvDq8ikWAM", # Rachel / Elegant
                "stability": 0.7,
                "similarityBoost": 0.8
            },
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are Celeste, the ultra-luxury private real estate concierge for Apex Luxury Estates. "
                            "Tone: Sophisticated, polite, discreet, warm, and highly polished. "
                            "Mission: Qualify high-net-worth buyers, answer questions regarding private architectural estates ($2M to $50M+), "
                            "and coordinate private showings. Always confirm buyer name, preferred viewing timeframe, and contact details."
                        )
                    }
                ]
            },
            "recordingEnabled": True,
            "endCallMessage": "Thank you for contacting Apex Luxury Estates. Have a wonderful day."
        }

        return self._create_or_update_assistant("Celeste", payload)

    def provision_luna_accident_pip(self) -> Dict[str, Any]:
        """
        Provisions or updates Luna (24/7 Bilingual Florida Accident & PIP Specialist).
        """
        payload = {
            "name": "Luna 🌙 Florida No-Fault & PIP Triage",
            "firstMessage": "Hola, gracias por llamar a la línea de asistencia de accidentes de Florida. Mi nombre es Luna. ¿Se encuentra usted y sus acompañantes en un lugar seguro? / Hello, thank you for calling Florida Accident Care. Are you in a safe location?",
            "voice": {
                "provider": "11labs",
                "voiceId": "EXAVITQu4vr4xnSDxMaL", # Bella / Friendly & Empathetic
                "stability": 0.65,
                "similarityBoost": 0.8
            },
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are Luna, the 24/7 bilingual emergency accident triage coordinator for Florida No-Fault Claims. "
                            "Language Standard: 100% fluent in both Spanish and English. Seamlessly match the caller's language. "
                            "Tone: Calm, empathetic, urgent yet reassuring. "
                            "Key Mandate: Florida law grants accident victims 14 days from the date of the accident to complete an initial medical evaluation to preserve their $10,000 PIP insurance benefits. "
                            "Intake Protocol: 1. Confirm safety. 2. Collect caller name & phone. 3. Collect location & date of accident. 4. Inquire about neck/back pain or injuries. 5. Reassure that immediate medical scheduling and attorney coordination are being prepared."
                        )
                    }
                ]
            },
            "recordingEnabled": True,
            "endCallMessage": "Gracias por llamar. Nos pondremos en contacto con usted de inmediato para coordinar su atención médica."
        }

        return self._create_or_update_assistant("Luna", payload)

    def _create_or_update_assistant(self, name_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        assistants = self.list_assistants()
        existing_id = None
        for a in assistants:
            if name_key.lower() in a.get("name", "").lower():
                existing_id = a.get("id")
                break

        try:
            if existing_id:
                url = f"{self.base_url}/assistant/{existing_id}"
                res = requests.patch(url, headers=self.get_headers(), json=payload)
                print(f"[Vapi Agent] Updated existing assistant '{name_key}' (ID: {existing_id})")
                return {"status": "UPDATED", "assistant_id": existing_id, "data": res.json()}
            else:
                url = f"{self.base_url}/assistant"
                res = requests.post(url, headers=self.get_headers(), json=payload)
                data = res.json()
                new_id = data.get("id")
                print(f"[Vapi Agent] Created new assistant '{name_key}' (ID: {new_id})")
                return {"status": "CREATED", "assistant_id": new_id, "data": data}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

if __name__ == "__main__":
    agent = VapiAutonomousAgent()
    print("🚀 Registering Live Voice Assistants on Vapi AI...")
    
    print("\n1. Provisioning Celeste ✨ (Luxury Real Estate Concierge)...")
    res_celeste = agent.provision_celeste_real_estate()
    print(json.dumps(res_celeste, indent=2))
    
    print("\n2. Provisioning Luna 🌙 (Florida No-Fault 24/7 Bilingual Triage)...")
    res_luna = agent.provision_luna_accident_pip()
    print(json.dumps(res_luna, indent=2))

    print("\n3. Checking Phone Numbers registered on Vapi Account...")
    numbers = agent.list_phone_numbers()
    print(f"Total Phone Numbers: {len(numbers)}")
    for n in numbers:
        print(f" - {n.get('number')} (ID: {n.get('id')}) -> Linked Assistant: {n.get('assistantId')}")
