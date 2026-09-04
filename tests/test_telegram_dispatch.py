"""
Tests for gated Telegram dispatch (W2 live path).
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
import sys
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from apex_core.telegram_dispatch import (
    TelegramDispatcher,
    dispatch_telegram_alert,
    is_live_dispatch_enabled,
    parse_chat_id,
)


class TestTelegramDispatch(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="apex_tg_dispatch_"))
        self.gates_file = self.temp_dir / "operator_gates.json"
        self.gates_file.write_text(
            json.dumps({"version": 1, "gates": {"telegram_live_enabled": False}, "history": []}),
            encoding="utf-8",
        )
        os.environ["APEX_OPERATOR_GATES_FILE"] = str(self.gates_file)
        self.alert = {
            "channel": "telegram:8349762599",
            "brief_id": "20260904-rosie",
            "message": "📥 [HERMES TRIAGE: NEW ONBOARDING BRIEF]\n\nTest alert",
            "claims": {
                "agent_deployed": False,
                "portal_created": False,
                "mls_connected": False,
            },
        }
        self._env_backup = {
            "APEX_TELEGRAM_LIVE": os.environ.pop("APEX_TELEGRAM_LIVE", None),
            "APEX_TELEGRAM_BOT_TOKEN": os.environ.pop("APEX_TELEGRAM_BOT_TOKEN", None),
            "APEX_OPERATOR_GATES_FILE": os.environ.get("APEX_OPERATOR_GATES_FILE"),
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        for key, val in self._env_backup.items():
            if val is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = val

    def test_default_staged_only(self):
        result = dispatch_telegram_alert(self.alert, evidence_dir=self.temp_dir)
        self.assertEqual(result["dispatch_status"], "STAGED_ONLY")
        self.assertFalse(result["live_sent"])
        for val in result["claims"].values():
            self.assertFalse(val)
        self.assertTrue((self.temp_dir / "telegram_dispatch_latest.json").exists())

    def test_live_blocked_without_token(self):
        self.gates_file.write_text(
            json.dumps({"version": 1, "gates": {"telegram_live_enabled": True}, "history": []}),
            encoding="utf-8",
        )
        os.environ["APEX_TELEGRAM_LIVE"] = "1"
        result = dispatch_telegram_alert(self.alert, evidence_dir=self.temp_dir)
        self.assertEqual(result["dispatch_status"], "LIVE_BLOCKED_NO_TOKEN")
        self.assertFalse(result["live_sent"])

    def test_live_send_when_gated(self):
        self.gates_file.write_text(
            json.dumps({"version": 1, "gates": {"telegram_live_enabled": True}, "history": []}),
            encoding="utf-8",
        )
        os.environ["APEX_TELEGRAM_LIVE"] = "1"
        os.environ["APEX_TELEGRAM_BOT_TOKEN"] = "test-token"

        def mock_send(token, chat_id, message):
            self.assertEqual(token, "test-token")
            self.assertEqual(chat_id, "8349762599")
            self.assertIn("HERMES TRIAGE", message)
            return {"ok": True, "result": {"message_id": 42}}

        dispatcher = TelegramDispatcher(evidence_dir=self.temp_dir, send_fn=mock_send)
        result = dispatcher.dispatch(self.alert)
        self.assertEqual(result["dispatch_status"], "LIVE_SENT")
        self.assertTrue(result["live_sent"])
        self.assertEqual(result["telegram_message_id"], 42)
        for val in result["claims"].values():
            self.assertFalse(val)

    def test_parse_chat_id(self):
        self.assertEqual(parse_chat_id("telegram:8349762599"), "8349762599")
        self.assertEqual(parse_chat_id("8349762599"), "8349762599")

    def test_is_live_dispatch_enabled(self):
        os.environ["APEX_TELEGRAM_LIVE"] = "true"
        self.assertTrue(is_live_dispatch_enabled())


class TestBriefWatcherDispatchIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="apex_brief_tg_"))
        self.briefs_dir = self.temp_dir / "briefs"
        self.evidence_dir = self.temp_dir / "evidence"
        self.briefs_dir.mkdir()
        self.evidence_dir.mkdir()
        self._gates_backup = os.environ.get("APEX_OPERATOR_GATES_FILE")
        gates_file = self.temp_dir / "operator_gates.json"
        gates_file.write_text(
            json.dumps({"version": 1, "gates": {"telegram_live_enabled": False}, "history": []}),
            encoding="utf-8",
        )
        os.environ["APEX_OPERATOR_GATES_FILE"] = str(gates_file)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if self._gates_backup is None:
            os.environ.pop("APEX_OPERATOR_GATES_FILE", None)
        else:
            os.environ["APEX_OPERATOR_GATES_FILE"] = self._gates_backup

    def test_triage_includes_dispatch_record(self):
        from apex_core.brief_watcher import BriefWatcher

        watcher = BriefWatcher(briefs_dir=self.briefs_dir, evidence_dir=self.evidence_dir)
        brief = {
            "answers": {
                "full_name": "Rosie Rivera",
                "brokerage": "eXp Realty",
                "market": "Estero, FL",
                "needs": ["intake"],
            }
        }
        brief_file = self.briefs_dir / "20260904-rosie-dispatch.json"
        brief_file.write_text(json.dumps(brief), encoding="utf-8")

        result = watcher.triage_brief(brief_file)
        self.assertIn("dispatch", result)
        self.assertEqual(result["dispatch"]["dispatch_status"], "STAGED_ONLY")
        self.assertFalse(result["dispatch"]["live_sent"])


if __name__ == "__main__":
    unittest.main()
