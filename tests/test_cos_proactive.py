"""
Automated Test Suite for Hermes CoS Proactive Stack (P1–P5)
Per COS_PROACTIVE_SOP.md §2, §4, §9 & §10.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from apex_core.cos_proactive import (
    COS_PROACTIVE_PROMPT_BLOCK,
    CosProactiveEngine,
    GatewayHealth,
    GatewayHealthProbe,
    StandupComposer,
    StatusTelemetry,
    StatusTelemetryReader,
)


SAMPLE_ANTI = """# Anti Status

## Phase A — Engine (Anti)

| Task | Status | Evidence |
| --- | --- | --- |
| A4 72h uptime watch | **IN PROGRESS** | 12h+ clean |

## Phase B — Wiring (Authorized & Complete)

Leo **"all provisions are approved"** recorded.

### Rosie — ALL W1–W5 VERIFIED & PASS ✅

| # | Task | Verify | Status |
| --- | --- | --- | --- |
| W1 | Folder watch | test | **PASS** |
| W2 | Telegram alert | test | **PASS** |
| W3 | CoS triage | test | **PASS** |
| W4 | Tenant skeleton | test | **PASS** |
| W5 | Delegation sandbox | test | **PASS** |

### CoS (`COS_PROACTIVE_SOP.md` §10)

| # | Task | Verify |
| --- | --- | --- |
| P1 | Cron 8am + 6pm standup | Leo receives template |
| P2 | System prompt | hey → standup |

## Dry-Run Verification (§9 ROSIE_ONBOARDING_SOP.md) — PASS

## HOLD (unchanged)

- `#Alienware-hq` — HOLD

## QUEUED (from Leo / Hermes)

_None._
"""

SAMPLE_HERMES = """# Hermes Agent Operational Status

**Status:** Operational (Detached Gateway Daemon PID 37056 + Lease Guardian Watchdog PID 32880)
**Hold State:** STRICT HOLD on `#Alienware-hq` (Maintained)

| Agent / Component | Runtime & Model Route | Role & Status |
| --- | --- | --- |
| **Hermes Gateway** | Python 3.11 venv | Daemon PID 37056, Web Dashboard (`http://127.0.0.1:9119`) |

7. **Test Suite Verification:**
   - `python -m unittest discover -s tests` → **67/67 PASS**
"""


class TestCosProactive(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="apex_cos_proactive_"))
        self.anti_path = self.temp_dir / "ANTI_STATUS.md"
        self.hermes_path = self.temp_dir / "HERMES_STATUS.md"
        self.evidence_dir = self.temp_dir / "evidence"
        self.anti_path.write_text(SAMPLE_ANTI, encoding="utf-8")
        self.hermes_path.write_text(SAMPLE_HERMES, encoding="utf-8")

        self.up_health = GatewayHealth(
            gateway_up=True,
            gateway_pid="37056",
            telegram_ok=True,
            desktop_ok=True,
            last_incident="none",
        )
        self.down_health = GatewayHealth(
            gateway_up=False,
            gateway_pid="37056",
            telegram_ok=False,
            desktop_ok=False,
            last_incident="Gateway process not reachable",
            alert_message="🚨 GATEWAY DOWN — Anti required\nGateway process not running. Standup paused until UP.",
        )

        self.engine = CosProactiveEngine(
            anti_status_path=self.anti_path,
            hermes_status_path=self.hermes_path,
            gateway_probe_fn=lambda: self.up_health,
            evidence_dir=self.evidence_dir,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_p5_telemetry_reader_parses_status_files(self):
        reader = StatusTelemetryReader(self.anti_path, self.hermes_path)
        t = reader.read()
        self.assertEqual(t.gateway_pid, "37056")
        self.assertEqual(t.a4_status, "IN PROGRESS")
        self.assertEqual(t.dry_run_status, "PASS")
        self.assertIn("W1–W5 COMPLETE", t.rosie_wiring)
        self.assertTrue(t.hold_active)
        self.assertEqual(t.pytest_count, "67/67")

    def test_p1_standup_morning_template_format(self):
        payload = self.engine.build_standup("morning")
        self.assertIn("HERMES STANDUP", payload.body)
        self.assertIn("8:00 AM ET", payload.body)
        self.assertIn("ENGINE", payload.body)
        self.assertIn("ROSIE ONBOARDING", payload.body)
        self.assertIn("TEAM QUEUE", payload.body)
        self.assertIn("LEO DECISIONS NEEDED", payload.body)
        self.assertIn("NEXT AUTO ACTION", payload.body)
        self.assertIn("POSTURE (§12)", payload.body)

    def test_p1_standup_evening_template_format(self):
        payload = self.engine.build_standup("evening")
        self.assertIn("6:00 PM ET", payload.body)
        self.assertIn("Prepare evening summary", payload.body)

    def test_p4_gateway_down_alert_first(self):
        engine = CosProactiveEngine(
            anti_status_path=self.anti_path,
            hermes_status_path=self.hermes_path,
            gateway_probe_fn=lambda: self.down_health,
            evidence_dir=self.evidence_dir,
        )
        body = engine.build_cron_delivery("morning")
        self.assertIn("GATEWAY DOWN", body)
        self.assertNotIn("ROSIE ONBOARDING", body)

    def test_p4_gateway_up_full_standup(self):
        body = self.engine.build_cron_delivery("morning")
        self.assertIn("Gateway: UP PID 37056", body)
        self.assertIn("ROSIE ONBOARDING", body)

    def test_p2_hey_triggers_standup_not_echo(self):
        reply = self.engine.compose_proactive_reply("hey")
        self.assertIn("Hello, Leo. Here's your standup:", reply)
        self.assertIn("HERMES STANDUP", reply)
        self.assertFalse(CosProactiveEngine.is_passive_echo_only(reply))

    def test_p2_status_query_triggers_standup(self):
        reply = self.engine.compose_proactive_reply("what's going on?")
        self.assertIn("HERMES STANDUP", reply)
        self.assertIn("Gateway:", reply)

    def test_p2_passive_echo_forbidden(self):
        self.assertTrue(CosProactiveEngine.is_passive_echo_only("Hello, Leo. I'm here."))
        self.assertTrue(CosProactiveEngine.is_passive_echo_only("How can I help?"))
        standup_reply = self.engine.compose_proactive_reply("hey")
        self.assertFalse(CosProactiveEngine.is_passive_echo_only(standup_reply))

    def test_p2_response_quality_rubric_passes(self):
        reply = self.engine.compose_proactive_reply("hey")
        ok, issues = CosProactiveEngine.verify_response_quality(reply)
        self.assertTrue(ok, f"Rubric issues: {issues}")

    def test_p2_response_quality_catches_false_claims(self):
        bad = "Agent deployed: yes\nPortal live: yes\nMLS connected: yes"
        ok, issues = CosProactiveEngine.verify_response_quality(bad)
        self.assertFalse(ok)
        self.assertTrue(any("False live claim" in i for i in issues))

    def test_p2_prompt_block_contains_sop_sections(self):
        ok, missing = self.engine.verify_prompt_block(COS_PROACTIVE_PROMPT_BLOCK)
        self.assertTrue(ok, f"Missing: {missing}")

    def test_standup_staged_to_evidence(self):
        self.engine.build_standup("morning")
        evidence = self.evidence_dir / "cos_standup_latest.json"
        self.assertTrue(evidence.exists())
        data = json.loads(evidence.read_text(encoding="utf-8"))
        self.assertFalse(data["claims"]["agent_deployed"])
        self.assertFalse(data["claims"]["portal_created"])
        self.assertEqual(data["slot"], "morning")

    def test_zero_false_claims_in_standup_body(self):
        payload = self.engine.build_standup("morning")
        lower = payload.body.lower()
        self.assertIn("agent deployed: no", lower)
        self.assertIn("public portal live: no", lower)
        self.assertIn("mls connected: no", lower)
        self.assertNotIn("agent deployed: yes", lower)

    def test_gateway_probe_injectable(self):
        probe = GatewayHealthProbe(probe_fn=lambda: self.down_health)
        health = probe.probe()
        self.assertFalse(health.gateway_up)
        self.assertIsNotNone(health.alert_message)


if __name__ == "__main__":
    unittest.main()
