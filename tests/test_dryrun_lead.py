import json
import unittest
from pathlib import Path

from apex_core.execute_dryrun_lead import run_dryrun_lead


class TestDryrunLead(unittest.TestCase):
    def test_dryrun_lead_execution_passes(self):
        res = run_dryrun_lead()
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["external_sends_performed"], 0)
        self.assertTrue(res["false_claims_clean"])

        brief_path = Path(res["brief_json"])
        self.assertTrue(brief_path.exists())

        with open(brief_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["answers"]["full_name"], "DRYRUN Rosie Test")
        self.assertEqual(data["hermes_stage"], "STAGE:READY")
        self.assertEqual(data["leo_decision"], "APPROVE PROVISION DRYRUN")
        self.assertEqual(res["provision_gate"]["gate_mode"], "DRYRUN")

        # Verify all 3 specialist draft outputs exist on disk
        for agent, path_str in res["drafts_generated"].items():
            self.assertTrue(Path(path_str).exists(), f"Draft for {agent} missing at {path_str}")


if __name__ == "__main__":
    unittest.main()
