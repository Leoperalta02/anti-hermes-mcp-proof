"""
Tests for gated provision executor.
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from apex_core.provision_executor import (
    evaluate_brief_provision_gate,
    execute_gated_provision,
    execute_gated_provision_from_file,
    slugify,
)


class TestProvisionExecutor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="apex_provision_"))
        self.tenants_dir = self.temp_dir / "tenants"
        self.briefs_dir = self.temp_dir / "briefs"
        self.briefs_dir.mkdir()
        self._a4_backup = os.environ.pop("APEX_A4_WATCH_COMPLETE", None)
        os.environ["APEX_OPERATOR_GATES_FILE"] = str(self.temp_dir / "operator_gates.json")
        (self.temp_dir / "operator_gates.json").write_text(
            json.dumps({"version": 1, "gates": {"a4_watch_complete": False}, "history": []}),
            encoding="utf-8",
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if self._a4_backup is None:
            os.environ.pop("APEX_A4_WATCH_COMPLETE", None)
        else:
            os.environ["APEX_A4_WATCH_COMPLETE"] = self._a4_backup
        os.environ.pop("APEX_OPERATOR_GATES_FILE", None)

    def _sample_brief(self, leo_decision=None):
        return {
            "kind": "apex_realtor_onboarding_brief",
            "status": "staged",
            "answers": {
                "full_name": "DRYRUN Rosie Test",
                "brokerage": "Apex Staging Brokerage",
                "market": "Estero, FL",
                "email": "dryrun.rosie@apexstaging.local",
                "needs": ["intake", "follow_up", "copy"],
            },
            "hermes_stage": "STAGE:READY",
            "leo_decision": leo_decision,
        }

    def test_blocked_without_leo_decision(self):
        with self.assertRaises(PermissionError):
            execute_gated_provision(self._sample_brief(), tenants_dir=self.tenants_dir)

    def test_dryrun_provisions_skeleton(self):
        brief = self._sample_brief("APPROVE PROVISION DRYRUN")
        brief_path = self.briefs_dir / "dryrun.json"
        brief_path.write_text(json.dumps(brief), encoding="utf-8")

        result = execute_gated_provision(brief, brief_path=brief_path, tenants_dir=self.tenants_dir)
        self.assertEqual(result["status"], "PROVISIONED")
        self.assertEqual(result["provision_gate"]["gate_mode"], "DRYRUN")
        self.assertTrue((Path(result["tenant_dir"]) / "TENANT_MANIFEST.json").exists())
        for path in result["drafts_generated"].values():
            self.assertTrue(Path(path).exists())

        updated = json.loads(brief_path.read_text(encoding="utf-8"))
        self.assertEqual(updated["assigned_tenant_slug"], "dryrun-rosie-test")

    def test_live_blocked_without_a4(self):
        brief = self._sample_brief("APPROVE PROVISION")
        with self.assertRaises(PermissionError):
            execute_gated_provision(brief, tenants_dir=self.tenants_dir)

    def test_from_file_helper(self):
        brief = self._sample_brief("APPROVE PROVISION DRYRUN")
        brief_path = self.briefs_dir / "from-file.json"
        brief_path.write_text(json.dumps(brief), encoding="utf-8")
        result = execute_gated_provision_from_file(brief_path, tenants_dir=self.tenants_dir)
        self.assertEqual(result["status"], "PROVISIONED")

    def test_evaluate_brief_provision_gate(self):
        gate = evaluate_brief_provision_gate(self._sample_brief())
        self.assertFalse(gate["provision_allowed"])

    def test_slugify(self):
        self.assertEqual(slugify("DRYRUN Rosie Test"), "dryrun-rosie-test")


if __name__ == "__main__":
    unittest.main()
