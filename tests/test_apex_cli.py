"""
Tests for Apex unified CLI.
"""

import json
import os
import unittest
from io import StringIO
from unittest.mock import patch

from apex_core.apex_cli import cmd_host, cmd_status, detect_host, main


class TestApexCli(unittest.TestCase):
    def test_detect_host_returns_dict(self):
        info = detect_host()
        self.assertIn("host_label", info)
        self.assertIn("workspace", info)

    def test_host_command_json(self):
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = cmd_host(type("A", (), {})())
        self.assertEqual(code, 0)
        data = json.loads(buf.getvalue().split("\n\n")[0])
        self.assertIn("host_label", data)

    def test_status_command_runs(self):
        code = cmd_status(type("A", (), {})())
        self.assertEqual(code, 0)

    def test_main_help(self):
        code = main([])
        self.assertEqual(code, 0)

    def test_gates_show(self):
        os.environ.pop("APEX_OPERATOR_GATES_FILE", None)
        code = main(["gates", "show"])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
