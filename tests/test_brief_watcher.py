"""
Automated Test Suite for Hermes Brief Watcher & Triage Hook (W1 & W2)
Verifies triage classification, security validation, and Telegram alert formatting (§6 & §12 SOP).
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path

# Ensure root on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apex_core.brief_watcher import BriefWatcher, SECRET_RE, TELEGRAM_TARGET


class TestBriefWatcher(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="apex_brief_test_"))
        self.briefs_dir = self.temp_dir / "briefs"
        self.evidence_dir = self.temp_dir / "evidence"
        self.briefs_dir.mkdir(parents=True)
        self.evidence_dir.mkdir(parents=True)
        self.watcher = BriefWatcher(briefs_dir=self.briefs_dir, evidence_dir=self.evidence_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_triage_ready_brief(self):
        """Verify complete brief evaluates to STAGE:READY and produces SOP-compliant Telegram alert."""
        sample_brief = {
            "kind": "apex_realtor_onboarding_brief",
            "status": "staged",
            "answers": {
                "full_name": "Rosie Rivera",
                "brokerage": "Rosie Rivera Luxury Real Estate",
                "market": "Estero & Naples, FL",
                "email": "rosie@rosieriveraluxury.com",
                "needs": ["intake", "cma_model", "follow_up"]
            }
        }
        brief_file = self.briefs_dir / "20260904-rosie-ready.json"
        brief_file.write_text(json.dumps(sample_brief), encoding="utf-8")

        result = self.watcher.triage_brief(brief_file)

        self.assertEqual(result["classification"], "STAGE:READY")
        self.assertEqual(result["channel"], TELEGRAM_TARGET)
        self.assertFalse(result["claims"]["agent_deployed"])
        self.assertFalse(result["claims"]["portal_created"])
        self.assertFalse(result["claims"]["mls_connected"])

        # SOP §12 verification: explicit zero false claims
        msg = result["message"]
        self.assertIn("STAGED ONLY", msg)
        self.assertIn("Agent deployed: NO", msg)
        self.assertIn("Public portal live: NO", msg)
        self.assertIn("MLS connected: NO", msg)
        self.assertIn("Rosie Rivera", msg)

        # Verify alert written to evidence directory
        self.assertTrue(self.watcher.alert_file.exists())
        alert_data = json.loads(self.watcher.alert_file.read_text(encoding="utf-8"))
        self.assertEqual(alert_data["classification"], "STAGE:READY")

    def test_triage_discovery_brief(self):
        """Verify incomplete brief evaluates to STAGE:DISCOVERY."""
        discovery_brief = {
            "kind": "apex_realtor_onboarding_brief",
            "status": "staged",
            "answers": {
                "brokerage": "Anonymous Realty",
                "market": "Miami, FL"
            }
        }
        brief_file = self.briefs_dir / "20260904-anon-discovery.json"
        brief_file.write_text(json.dumps(discovery_brief), encoding="utf-8")

        result = self.watcher.triage_brief(brief_file)
        self.assertEqual(result["classification"], "STAGE:DISCOVERY")
        self.assertIn("STAGE:DISCOVERY", result["message"])

    def test_triage_rejects_credentials(self):
        """Verify brief with credential keys is flagged STAGE:REJECTED_CREDENTIALS."""
        leaky_brief = {
            "kind": "apex_realtor_onboarding_brief",
            "answers": {
                "full_name": "Malicious User",
                "api_key": "sk-secret-12345678"
            }
        }
        brief_file = self.briefs_dir / "20260904-leaky.json"
        brief_file.write_text(json.dumps(leaky_brief), encoding="utf-8")

        result = self.watcher.triage_brief(brief_file)
        self.assertEqual(result["classification"], "STAGE:REJECTED_CREDENTIALS")
        self.assertIn("CREDENTIALS REJECTED", result["message"])

    def test_scan_once_and_idempotence(self):
        """Verify scan_once finds new briefs and avoids duplicate processing."""
        b1 = {
            "answers": {
                "full_name": "Test Agent One",
                "needs": ["intake"]
            }
        }
        (self.briefs_dir / "brief-1.json").write_text(json.dumps(b1), encoding="utf-8")

        found = self.watcher.scan_once()
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["brief_id"], "brief-1")

        # Second scan should be empty
        found_again = self.watcher.scan_once()
        self.assertEqual(len(found_again), 0)

    def test_triage_defer_brief(self):
        """Verify brief flagged for deferral evaluates to STAGE:DEFER."""
        defer_brief = {
            "kind": "apex_realtor_onboarding_brief",
            "leo_decision": "DEFER",
            "answers": {
                "full_name": "Deferred Agent",
                "needs": ["intake"]
            }
        }
        brief_file = self.briefs_dir / "20260904-defer.json"
        brief_file.write_text(json.dumps(defer_brief), encoding="utf-8")

        result = self.watcher.triage_brief(brief_file)
        self.assertEqual(result["classification"], "STAGE:DEFER")
        self.assertIn("STAGE:DEFER", result["message"])
        self.assertIn("Brief is deferred", result["message"])

    def test_telegram_target_configuration(self):
        """Verify telegram target can be customized via env var or constructor."""
        # Constructor override
        custom_watcher = BriefWatcher(
            briefs_dir=self.briefs_dir,
            evidence_dir=self.evidence_dir,
            telegram_target="telegram:custom_chat_999"
        )
        self.assertEqual(custom_watcher.telegram_target, "telegram:custom_chat_999")

        # Env var override
        os.environ["APEX_TELEGRAM_TARGET"] = "telegram:env_chat_123"
        try:
            env_watcher = BriefWatcher(
                briefs_dir=self.briefs_dir,
                evidence_dir=self.evidence_dir
            )
            self.assertEqual(env_watcher.telegram_target, "telegram:env_chat_123")
        finally:
            del os.environ["APEX_TELEGRAM_TARGET"]


    def test_triage_brief_with_mentor_team(self):
        """Verify brief with team and mentor group details formats cleanly in alert."""
        sample_brief = {
            "kind": "apex_realtor_onboarding_brief",
            "status": "staged",
            "answers": {
                "full_name": "Rosie Rivera",
                "brokerage": "eXp Realty",
                "team_name": "Gulf Pointe Properties",
                "team_leader": "Bradley Dohack",
                "office_address": "9480 Corkscrew Palms Cir, Suite 4, Estero, FL 33928",
                "market": "Estero & Naples, FL",
                "email": "rosie@gulfpointe.com",
                "needs": ["intake", "cma_model"]
            }
        }
        brief_file = self.briefs_dir / "20260904-rosie-gulfpointe.json"
        brief_file.write_text(json.dumps(sample_brief), encoding="utf-8")

        result = self.watcher.triage_brief(brief_file)
        self.assertEqual(result["classification"], "STAGE:READY")
        self.assertIn("Team: Gulf Pointe Properties", result["message"])
        self.assertIn("Mentor: Bradley Dohack", result["message"])
        self.assertIn("eXp Realty", result["message"])
        self.assertFalse(result["claims"]["agent_deployed"])


if __name__ == "__main__":
    unittest.main()


