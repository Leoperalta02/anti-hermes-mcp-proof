"""
Automated Test Suite for Hermes CoS Triage Integration & Evaluator (W3)
Verifies:
1. Canonical CoS prompt block installation & verification in CoS SOUL.md.
2. 5-point triage checklist (§6 ROSIE_ONBOARDING_SOP.md): Acknowledge, Validate, Classify, Surface, Gate.
3. False-claims protection (§12 ROSIE_ONBOARDING_SOP.md & §9 COS_PROACTIVE_SOP.md).
4. Staged alert consumption from evidence/brief_telegram_alert.json.
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Ensure workspace root on sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
import sys
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from apex_core.cos_triage_evaluator import (
    COS_TRIAGE_PROMPT_BLOCK,
    CosTriageEvaluator,
    DEFAULT_COS_PROFILE_PATH,
)


class TestCosTriageEvaluator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="apex_cos_triage_test_"))
        self.mock_soul_file = self.temp_dir / "SOUL.md"
        self.mock_soul_file.write_text(
            "# SOUL.md - Persistent Chief of Staff (Anti)\n\n## Identity & Role\nYou are Anti, Leo's Chief of Staff.\n",
            encoding="utf-8"
        )
        self.evaluator = CosTriageEvaluator(cos_soul_path=self.mock_soul_file)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cos_prompt_block_installation_and_verification(self):
        """Verify prompt block installs cleanly into SOUL.md and passes verification."""
        is_valid, missing = self.evaluator.verify_cos_prompt_block()
        self.assertFalse(is_valid)
        self.assertGreater(len(missing), 0)

        # Sync prompt block
        synced = self.evaluator.sync_prompt_block_to_profile()
        self.assertTrue(synced)

        is_valid_after, missing_after = self.evaluator.verify_cos_prompt_block()
        self.assertTrue(is_valid_after)
        self.assertEqual(len(missing_after), 0)

        # Idempotence: syncing again should return True without duplicate blocks
        synced_again = self.evaluator.sync_prompt_block_to_profile()
        self.assertTrue(synced_again)
        content = self.mock_soul_file.read_text(encoding="utf-8")
        self.assertEqual(content.count("Onboarding Brief Triage Protocol"), 1)

    def test_mock_brief_checklist_ready(self):
        """Verify complete mock brief executes full 5-point checklist with STAGE:READY."""
        mock_brief = {
            "answers": {
                "full_name": "Rosie Rivera",
                "brokerage": "Rosie Rivera Luxury Real Estate",
                "market": "Estero & Naples, FL",
                "email": "rosie@rosieriveraluxury.com",
                "needs": ["intake", "cma_model", "follow_up"]
            }
        }

        result = self.evaluator.evaluate_brief(mock_brief, brief_id="mock-brief-rosie")

        # 5-point checklist verification (§6)
        checklist = result.checklist
        self.assertTrue(checklist.acknowledged)
        self.assertTrue(checklist.validated)
        self.assertTrue(checklist.classified)
        self.assertTrue(checklist.surfaced)
        self.assertTrue(checklist.gated)

        # Classification verification
        self.assertEqual(result.classification, "STAGE:READY")
        self.assertEqual(checklist.details["gate"]["gate_status"], "AWAITING_LEO_APPROVE_PROVISION")
        self.assertTrue(checklist.details["gate"]["provision_blocked"])

        # SOP §12 zero false claims
        for claim_key, claim_val in result.claims.items():
            self.assertFalse(claim_val, f"Claim {claim_key} must be false")

        msg = result.alert_message
        self.assertIn("STAGED ONLY", msg)
        self.assertIn("Agent deployed: NO", msg)
        self.assertIn("Public portal live: NO", msg)
        self.assertIn("MLS connected: NO", msg)
        self.assertIn("Rosie Rivera", msg)

    def test_mock_brief_checklist_discovery(self):
        """Verify incomplete mock brief evaluates to STAGE:DISCOVERY and awaits discovery completion."""
        incomplete_brief = {
            "answers": {
                "brokerage": "Incomplete Realty",
                "market": "Naples, FL"
            }
        }

        result = self.evaluator.evaluate_brief(incomplete_brief, brief_id="mock-brief-discovery")

        self.assertEqual(result.classification, "STAGE:DISCOVERY")
        self.assertEqual(result.checklist.details["gate"]["gate_status"], "AWAITING_DISCOVERY_COMPLETION")
        self.assertIn("STAGE:DISCOVERY", result.alert_message)
        self.assertIn("Follow up on required intake fields", result.recommended_action)

    def test_mock_brief_checklist_defer(self):
        """Verify brief with defer flag evaluates to STAGE:DEFER and sets gate to DEFERRED."""
        deferred_brief = {
            "leo_decision": "DEFER",
            "answers": {
                "full_name": "Deferred Realtor",
                "needs": ["intake"]
            }
        }

        result = self.evaluator.evaluate_brief(deferred_brief, brief_id="mock-brief-defer")

        self.assertEqual(result.classification, "STAGE:DEFER")
        self.assertEqual(result.checklist.details["gate"]["gate_status"], "DEFERRED")
        self.assertIn("STAGE:DEFER", result.alert_message)
        self.assertIn("Awaiting Leo re-activation", result.recommended_action)

    def test_mock_brief_checklist_reject_credentials(self):
        """Verify brief containing credential tokens fails security validation and is REJECTED."""
        leaky_brief = {
            "answers": {
                "full_name": "Leaky Realtor",
                "needs": ["intake"],
                "api_key": "sk-1234567890abcdef"
            }
        }

        result = self.evaluator.evaluate_brief(leaky_brief, brief_id="mock-brief-leaky")

        self.assertEqual(result.classification, "STAGE:REJECTED_CREDENTIALS")
        self.assertFalse(result.checklist.validated)
        self.assertEqual(result.checklist.details["gate"]["gate_status"], "REJECTED")
        self.assertIn("CREDENTIALS REJECTED", result.alert_message)

    def test_consume_staged_alert(self):
        """Verify consuming evidence/brief_telegram_alert.json confirms zero false claims."""
        alert_file = self.temp_dir / "brief_telegram_alert.json"
        alert_payload = {
            "channel": "telegram:8349762599",
            "brief_id": "test-alert",
            "classification": "STAGE:READY",
            "claims": {
                "agent_deployed": False,
                "portal_created": False,
                "mls_connected": False
            },
            "message": "📥 [HERMES TRIAGE: NEW ONBOARDING BRIEF]\n• Agent deployed: NO\n• Public portal live: NO"
        }
        alert_file.write_text(json.dumps(alert_payload), encoding="utf-8")

        consumed = self.evaluator.consume_staged_alert(alert_file)
        self.assertEqual(consumed["status"], "CONSUMED_STAGED_ALERT")
        self.assertEqual(consumed["brief_id"], "test-alert")
        self.assertTrue(consumed["claims_verified_clean"])
        self.assertTrue(consumed["awaiting_operator_gate"])

    def test_consume_staged_alert_catches_false_claims(self):
        """Verify ValueError is raised if any false claim is set to True in the staged alert."""
        tainted_file = self.temp_dir / "tainted_alert.json"
        tainted_payload = {
            "channel": "telegram:8349762599",
            "brief_id": "tainted-alert",
            "classification": "STAGE:READY",
            "claims": {
                "agent_deployed": True,  # VIOLATION of SOP §12
                "portal_created": False
            }
        }
        tainted_file.write_text(json.dumps(tainted_payload), encoding="utf-8")

        with self.assertRaises(ValueError) as ctx:
            self.evaluator.consume_staged_alert(tainted_file)
        self.assertIn("SOP §12 violation", str(ctx.exception))

    def test_live_cos_profile_status(self):
        """Verify live Alienware hermes-state anti-cos SOUL.md profile is verified if path exists."""
        if DEFAULT_COS_PROFILE_PATH.exists():
            live_eval = CosTriageEvaluator()
            is_valid, missing = live_eval.verify_cos_prompt_block()
            self.assertTrue(is_valid, f"Live CoS profile missing sections: {missing}")


if __name__ == "__main__":
    unittest.main()
