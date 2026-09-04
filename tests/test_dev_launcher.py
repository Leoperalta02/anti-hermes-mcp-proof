"""
Tests for unified dev launcher (preview + intake + brief receiver).
"""

import shutil
import socket
import tempfile
import unittest
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
import sys
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from apex_core.dev_launcher import (
    launch_dev_stack,
    port_available,
    shutdown_servers,
    wait_for_health,
)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class TestDevLauncher(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="apex_dev_launcher_"))
        self.preview_port = _free_port()
        self.intake_port = _free_port()
        self.brief_port = _free_port()
        self.servers = []

    def tearDown(self):
        shutdown_servers(self.servers)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_launch_all_services_health_checks(self):
        self.servers = launch_dev_stack(
            host="127.0.0.1",
            preview_port=self.preview_port,
            intake_port=self.intake_port,
            brief_port=self.brief_port,
            brief_dir=self.temp_dir / "onboarding-briefs",
        )
        self.assertEqual(len(self.servers), 3)
        for managed in self.servers:
            self.assertTrue(managed.ready)
            self.assertTrue(wait_for_health(managed.url, timeout_sec=3.0))

    def test_port_available_helper(self):
        self.assertTrue(port_available("127.0.0.1", _free_port()))


if __name__ == "__main__":
    unittest.main()
