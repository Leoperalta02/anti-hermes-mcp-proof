"""
Tests for Leo provision gate (SOP §6.5).
"""

import os
import unittest

from apex_core.provision_gate import (
    assert_provision_allowed,
    classify_leo_decision,
    evaluate_provision_gate,
)


class TestProvisionGate(unittest.TestCase):
    def setUp(self):
        self._a4_backup = os.environ.pop("APEX_A4_WATCH_COMPLETE", None)

    def tearDown(self):
        if self._a4_backup is None:
            os.environ.pop("APEX_A4_WATCH_COMPLETE", None)
        else:
            os.environ["APEX_A4_WATCH_COMPLETE"] = self._a4_backup

    def test_blocked_without_decision(self):
        gate = evaluate_provision_gate(None)
        self.assertFalse(gate["provision_allowed"])
        self.assertEqual(gate["gate_mode"], "BLOCKED")

    def test_dryrun_allowed_without_a4(self):
        gate = evaluate_provision_gate("APPROVE PROVISION DRYRUN")
        self.assertTrue(gate["provision_allowed"])
        self.assertEqual(gate["gate_mode"], "DRYRUN")

    def test_live_blocked_without_a4(self):
        gate = evaluate_provision_gate("APPROVE PROVISION")
        self.assertFalse(gate["provision_allowed"])
        self.assertEqual(gate["gate_mode"], "LIVE_BLOCKED_A4")

    def test_live_allowed_when_a4_complete(self):
        gate = evaluate_provision_gate("APPROVE PROVISION", a4_complete=True)
        self.assertTrue(gate["provision_allowed"])
        self.assertEqual(gate["gate_mode"], "LIVE")

    def test_all_provisions_approved_requires_a4(self):
        gate = evaluate_provision_gate("all provisions are approved", a4_complete=False)
        self.assertFalse(gate["provision_allowed"])
        gate_ok = evaluate_provision_gate("all provisions are approved", a4_complete=True)
        self.assertTrue(gate_ok["provision_allowed"])

    def test_classify_leo_decision(self):
        self.assertEqual(classify_leo_decision("APPROVE PROVISION DRYRUN"), "DRYRUN")
        self.assertEqual(classify_leo_decision("APPROVE PROVISION"), "LIVE")
        self.assertEqual(classify_leo_decision(""), "NONE")

    def test_assert_raises_when_blocked(self):
        with self.assertRaises(PermissionError):
            assert_provision_allowed(None)


if __name__ == "__main__":
    unittest.main()
