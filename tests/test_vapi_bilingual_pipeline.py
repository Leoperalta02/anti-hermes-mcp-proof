"""
Offline Verification Test Suite for apex_core/vapi_bilingual_pipeline.py
Ensures prompt schema integrity, variable injection, legal disclaimers, and zero external API calls.
"""

import sys
import unittest
from apex_core.vapi_bilingual_pipeline import VapiBilingualPipeline, vapi_pipeline

class TestVapiBilingualPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = VapiBilingualPipeline()
        self.test_agent = "Sofia Lanz"
        self.test_company = "Final Claim Legal & Medical Triage"
        self.test_phone = "786-461-0049"

    def test_accident_pip_prompt_structure(self):
        config = self.pipeline.get_accident_pip_prompt(
            self.test_agent, self.test_company, self.test_phone
        )
        
        # Verify mandatory schema keys
        required_keys = ["name", "voice", "first_message", "system_prompt", "max_duration_seconds", "end_call_message"]
        for key in required_keys:
            self.assertIn(key, config, f"Missing required key: {key}")

        # Verify parameter injection
        self.assertIn(self.test_company, config["name"])
        self.assertIn(self.test_company, config["first_message"])
        self.assertIn(self.test_agent, config["first_message"])
        self.assertIn(self.test_phone, config["system_prompt"])
        self.assertIn(self.test_agent, config["system_prompt"])

        # Verify Florida 14-Day PIP compliance & safety check rules
        prompt = config["system_prompt"]
        self.assertIn("14 días", prompt)
        self.assertIn("$10,000", prompt)
        self.assertIn("PIP", prompt)
        self.assertIn("SAFETY CHECK", prompt)
        self.assertIn("IMPORTANT LEGAL DISCLAIMER", prompt)

        # Verify Bilingual instructions
        self.assertIn("LANGUAGE DETECTION", prompt)
        self.assertIn("Spanish", prompt)
        self.assertIn("English", prompt)

    def test_luxury_real_estate_prompt_structure(self):
        config = self.pipeline.get_luxury_real_estate_prompt(
            "Elena Rostova", "Apex Luxury Estates", "305-555-0199"
        )
        
        # Verify mandatory schema keys
        required_keys = ["name", "voice", "first_message", "system_prompt", "max_duration_seconds", "end_call_message"]
        for key in required_keys:
            self.assertIn(key, config, f"Missing required key: {key}")

        # Verify parameter injection
        self.assertIn("Apex Luxury Estates", config["name"])
        self.assertIn("Apex Luxury Estates", config["first_message"])
        self.assertIn("Elena Rostova", config["first_message"])
        self.assertIn("305-555-0199", config["system_prompt"])

        # Verify qualification metrics & language switching rules
        prompt = config["system_prompt"]
        self.assertIn("$2M", prompt)
        self.assertIn("ShowingTime", prompt)
        self.assertIn("INTAKE PROTOCOL", prompt)
        self.assertIn("LANGUAGE DETECTION", prompt)
        self.assertIn("Spanish", prompt)

    def test_input_validation_empty_arguments(self):
        with self.assertRaises(ValueError):
            self.pipeline.get_accident_pip_prompt("", "Company", "123")
        with self.assertRaises(ValueError):
            self.pipeline.get_accident_pip_prompt("Agent", "   ", "123")
        with self.assertRaises(ValueError):
            self.pipeline.get_luxury_real_estate_prompt("Agent", "Company", "")

    def test_module_singleton_instance(self):
        self.assertIsInstance(vapi_pipeline, VapiBilingualPipeline)

    def test_bilingual_compliance_constants(self):
        from apex_core.vapi_bilingual_pipeline import PIP_DISCLAIMER_EN, PIP_DISCLAIMER_ES
        config = self.pipeline.get_accident_pip_prompt("Sofia Lanz", "Final Claim", "786-461-0049")
        self.assertIn(PIP_DISCLAIMER_EN, config["system_prompt"])
        self.assertIn(PIP_DISCLAIMER_ES, config["system_prompt"])
        self.assertEqual(config["pip_disclaimer_en"], PIP_DISCLAIMER_EN)
        self.assertEqual(config["pip_disclaimer_es"], PIP_DISCLAIMER_ES)
        self.assertIn("Thank you for calling", config["first_message"])
        self.assertIn("Gracias por llamar", config["first_message"])

    def test_language_context_retention_rule(self):
        config = self.pipeline.get_accident_pip_prompt("Sofia Lanz", "Final Claim", "786-461-0049")
        self.assertIn("Never restart intake from step 1", config["system_prompt"])
        self.assertIn("LANGUAGE SWITCHING & CONTEXT RETENTION", config["system_prompt"])

if __name__ == "__main__":
    unittest.main()

