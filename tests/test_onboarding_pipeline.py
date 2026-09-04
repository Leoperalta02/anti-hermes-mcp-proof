"""
tests/test_onboarding_pipeline.py
Unit tests asserting the autonomous end-to-end onboarding pipeline.
"""

import unittest
import os
import json
from apex_core.onboarding_pipeline import onboarding_pipeline

class TestOnboardingPipeline(unittest.TestCase):
    def test_full_onboarding_cycle(self):
        client_payload = {
            "full_name": "Rosie Rivera",
            "subdomain_slug": "rosie",
            "email": "rosie@rosieriveraluxury.com",
            "phone": "239-555-0199",
            "brokerage": "Rosie Rivera Luxury Real Estate",
            "market": "Estero & Naples, FL",
            "package_tier": "pro_realty",
            "monthly_price": 499
        }

        result = onboarding_pipeline.run_onboarding(client_payload)
        
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["tenant_slug"], "rosie")
        self.assertTrue(os.path.exists(result["front_door_url"]))
        self.assertTrue(os.path.exists(result["portal_url"]))
        self.assertIn("Welcome to Your Private AI Office", result["welcome_instructions"])
        self.assertIn("APEX ONBOARDING SUCCESS", result["telegram_alert"])

if __name__ == "__main__":
    unittest.main()
