"""
Automated Test Suite for Internal Delegation Sandbox (W5)
Per ROSIE_ONBOARDING_SOP.md §8, §9 & §10.

Verifies:
1. Sandbox channel configuration and boundary enforcement (#rosie-onboarding-sandbox, #wellington-canary).
2. Fail-closed rejection of #Alienware-hq and #panel-advisors.
3. Multi-agent delegation dispatches to Harbor, Keystone, Quill.
4. Input validation: non-empty target_agent and sanitized content.
5. SOP §12 zero false claims & zero external send verification.
6. Full §9 dry-run multi-agent orchestration.
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

from apex_core.delegation_sandbox import (
    ALLOWED_SPECIALISTS,
    FORBIDDEN_CHANNELS,
    SANDBOX_CHANNELS,
    DelegationSandbox,
)


class TestDelegationSandbox(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="apex_delegation_test_"))
        self.sandbox = DelegationSandbox(tenants_root=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_channel_authorization_whitelist(self):
        """Verify allowed sandbox channels pass authorization check."""
        for ch in ["#rosie-onboarding-sandbox", "rosie-onboarding-sandbox", "#wellington-canary", "wellington-canary"]:
            self.assertTrue(self.sandbox.is_channel_authorized(ch), f"Channel {ch} should be authorized")

    def test_channel_authorization_forbidden(self):
        """Verify production and boardroom channels are strictly forbidden."""
        for ch in ["#Alienware-hq", "Alienware-hq", "#panel-advisors", "panel-advisors", "#client-rosie-rivera"]:
            self.assertFalse(self.sandbox.is_channel_authorized(ch), f"Channel {ch} must be forbidden")

    def test_delegation_fails_closed_on_forbidden_channel(self):
        """Verify attempting to delegate in #Alienware-hq or #panel-advisors raises PermissionError."""
        with self.assertRaises(PermissionError):
            self.sandbox.delegate_task(
                target_agent="harbor",
                task_type="intake",
                content="Test task",
                tenant_slug="rosie",
                channel="#Alienware-hq"
            )

        with self.assertRaises(PermissionError):
            self.sandbox.delegate_task(
                target_agent="keystone",
                task_type="cma",
                content="Test task",
                tenant_slug="rosie",
                channel="#panel-advisors"
            )

    def test_argument_validation(self):
        """Verify empty agent, empty content, or empty slug raise ValueError."""
        # Empty agent
        with self.assertRaises(ValueError):
            self.sandbox.delegate_task(target_agent="", task_type="test", content="content", tenant_slug="rosie")

        # Invalid agent
        with self.assertRaises(ValueError):
            self.sandbox.delegate_task(target_agent="unauthorized_agent", task_type="test", content="content", tenant_slug="rosie")

        # Empty content
        with self.assertRaises(ValueError):
            self.sandbox.delegate_task(target_agent="harbor", task_type="test", content="   ", tenant_slug="rosie")

        # Empty slug
        with self.assertRaises(ValueError):
            self.sandbox.delegate_task(target_agent="harbor", task_type="test", content="valid", tenant_slug="")

    def test_delegate_to_harbor(self):
        """Verify delegation to Harbor produces draft follow_up_queue.json."""
        res = self.sandbox.delegate_task(
            target_agent="harbor",
            task_type="seed_follow_up_queue",
            content="Qualify inbound Estero luxury buyer lead.",
            tenant_slug="rosie_test"
        )
        self.assertEqual(res["status"], "DRAFT_STAGED_CLEAN")
        self.assertEqual(res["target_agent"], "harbor")
        self.assertTrue(res["external_send_blocked"])

        out_path = Path(res["output_file"])
        self.assertTrue(out_path.exists())
        data = json.loads(out_path.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "DRAFT_PENDING_REALTOR_APPROVAL")
        self.assertFalse(data["external_sent"])

    def test_delegate_to_keystone(self):
        """Verify delegation to Keystone produces draft cma_market_consult.md."""
        res = self.sandbox.delegate_task(
            target_agent="keystone",
            task_type="compute_cma_benchmark",
            content="Benchmark Bella Terra Estero comps.",
            tenant_slug="rosie_test"
        )
        self.assertEqual(res["status"], "DRAFT_STAGED_CLEAN")
        self.assertEqual(res["target_agent"], "keystone")

        out_path = Path(res["output_file"])
        self.assertTrue(out_path.exists())
        text = out_path.read_text(encoding="utf-8")
        self.assertIn("Keystone Comparative Market Analysis Draft", text)
        self.assertIn("DRAFT_PENDING_APPROVAL", text)

    def test_delegate_to_quill(self):
        """Verify delegation to Quill produces draft welcome_packet.md."""
        res = self.sandbox.delegate_task(
            target_agent="quill",
            task_type="draft_remarks",
            content="Draft MLS remarks for private estate.",
            tenant_slug="rosie_test"
        )
        self.assertEqual(res["status"], "DRAFT_STAGED_CLEAN")
        self.assertEqual(res["target_agent"], "quill")

        out_path = Path(res["output_file"])
        self.assertTrue(out_path.exists())
        text = out_path.read_text(encoding="utf-8")
        self.assertIn("Quill Marketing & Remarks Draft", text)

    def test_zero_false_claims_enforcement(self):
        """Verify that all claims in dispatch records are strictly False (§12 SOP)."""
        res = self.sandbox.delegate_task(
            target_agent="harbor",
            task_type="check",
            content="Check claims",
            tenant_slug="test_slug"
        )
        claims = res["claims"]
        for k, v in claims.items():
            self.assertFalse(v, f"Claim '{k}' must be false")

    def test_mock_delegation_orchestration(self):
        """Verify full §9 dry-run multi-agent delegation passes completely."""
        summary = self.sandbox.run_mock_delegation(slug="dryrun-test-tenant")
        self.assertEqual(summary["status"], "PASS")
        self.assertEqual(summary["dispatches_count"], 3)
        self.assertTrue(summary["zero_external_sends_verified"])
        self.assertTrue(summary["all_claims_false_verified"])


if __name__ == "__main__":
    unittest.main()
