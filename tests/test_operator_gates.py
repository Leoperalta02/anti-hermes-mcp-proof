"""
Tests for operator gate registry.
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from apex_core.operator_gates import (
    is_a4_watch_complete,
    is_gate_open,
    is_telegram_live_enabled,
    lift_provision_gates,
    load_operator_gates,
    record_gate_lift,
)


class TestOperatorGates(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="apex_gates_"))
        self.gates_file = self.temp_dir / "operator_gates.json"
        os.environ["APEX_OPERATOR_GATES_FILE"] = str(self.gates_file)
        self.gates_file.write_text(
            json.dumps({"version": 1, "gates": {"a4_watch_complete": False}, "history": []}),
            encoding="utf-8",
        )

    def tearDown(self):
        os.environ.pop("APEX_OPERATOR_GATES_FILE", None)
        os.environ.pop("APEX_A4_WATCH_COMPLETE", None)
        os.environ.pop("APEX_TELEGRAM_LIVE", None)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_env_overrides_evidence(self):
        os.environ["APEX_A4_WATCH_COMPLETE"] = "1"
        self.assertTrue(is_a4_watch_complete())

    def test_lift_provision_gates(self):
        result = lift_provision_gates(notes="test lift")
        self.assertTrue(result["gates"]["a4_watch_complete"])
        self.assertTrue(result["gates"]["live_provision_enabled"])
        self.assertTrue(is_a4_watch_complete())

    def test_telegram_gate_from_evidence(self):
        record_gate_lift(telegram_live_enabled=True, notes="tg")
        self.assertTrue(is_telegram_live_enabled())

    def test_hq_hold_defaults_closed(self):
        self.assertTrue(is_gate_open("alienware_hq_hold_active"))


if __name__ == "__main__":
    unittest.main()
