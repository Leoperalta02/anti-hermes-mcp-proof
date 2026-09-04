"""
Hermes Chief of Staff — Proactive Operations Engine (P1–P5)
Per COS_PROACTIVE_SOP.md §2, §4, §9 & §10.

Provides:
- P1: Daily standup template composer (8am + 6pm ET format per §4).
- P2: CoS system prompt block (§2 principle + §9 rubric) and proactive reply composer.
- P4: Gateway health probe preamble (alert-first when degraded).
- P5: Telemetry reader parsing ANTI_STATUS.md and HERMES_STATUS.md into standup bullets.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

DEFAULT_ANTI_STATUS = WORKSPACE_ROOT / "ANTI_STATUS.md"
DEFAULT_HERMES_STATUS = WORKSPACE_ROOT / "HERMES_STATUS.md"
DEFAULT_COS_PROFILE_PATH = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-state\profiles\anti-cos\SOUL.md")
DEFAULT_GATEWAY_URL = "http://127.0.0.1:9119"
EVIDENCE_DIR = WORKSPACE_ROOT / "evidence"
STANDUP_EVIDENCE = EVIDENCE_DIR / "cos_standup_latest.json"

try:
    from zoneinfo import ZoneInfo
    ET = ZoneInfo("America/New_York")
except Exception:
    from datetime import timezone, timedelta
    ET = timezone(timedelta(hours=-4))

COS_PROACTIVE_PROMPT_BLOCK = """
## Proactive Chief of Staff Operating Protocol (COS_PROACTIVE_SOP.md §2 & §9)

You are Hermes, Chief Operating Officer — not a polite echo bot.

### §2 Core Principle (mandatory every CoS turn)
Every reply MUST include at least one of:
1. **Status** — what is true right now (gateway, tasks, blockers)
2. **Action** — what Hermes or the team did / will do next
3. **Decision** — what Leo must approve, defer, or reject

**FORBIDDEN as sole response** (never send these alone):
- "Hello, Leo. I'm here."
- "Good—you're back."
- "How can I help?"

**Required pattern for greetings:** If Leo says "hey", "hi", "hello", or asks status, respond:
"Hello, Leo. Here's your standup:" followed immediately by the full §4 standup block.

### §9 Response Quality Rubric (self-check before send)
- [ ] Did I include status OR action OR decision request?
- [ ] Did I avoid false live claims (portal live, MLS connected, voice deployed)?
- [ ] Did I avoid vault/secret content?
- [ ] If Leo asked "what's going on" — did I cite gateway + open blockers?
- [ ] If stuck — did I name who can fix it (Anti / Cursor / Leo)?

### §12 Posture (Zero False Claims)
All standups and alerts must state STAGED ONLY posture:
- Agent deployed: NO (unless Leo explicitly approved live provision)
- Public portal live: NO (local demo sites are not live client deployments)
- MLS connected: NO
- HOLD on #Alienware-hq: ACTIVE
"""

PASSIVE_ECHO_PATTERNS = (
    "i'm here",
    "how can i help",
    "good—you're back",
    "good - you're back",
    "how may i assist",
)

GREETING_TRIGGERS = (
    "hey",
    "hi",
    "hello",
    "yo",
    "what's going on",
    "whats going on",
    "status",
    "standup",
    "update me",
)


@dataclass
class GatewayHealth:
    gateway_up: bool
    gateway_pid: Optional[str] = None
    telegram_ok: bool = False
    desktop_ok: bool = False
    last_incident: str = "none"
    alert_message: Optional[str] = None
    probe_source: str = "http_probe"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StatusTelemetry:
    gateway_pid: Optional[str] = None
    gateway_status_line: str = "unknown"
    hold_active: bool = True
    phase_a_summary: str = "unknown"
    a4_status: str = "unknown"
    rosie_wiring: str = "unknown"
    dry_run_status: str = "NOT STARTED"
    cos_p_tasks: Dict[str, str] = field(default_factory=dict)
    anti_queue: str = "None"
    cursor_queue: str = "None"
    leo_decisions_needed: List[str] = field(default_factory=list)
    pytest_count: Optional[str] = None
    last_incident: str = "none"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StandupPayload:
    slot: str
    timestamp_et: str
    gateway_health: GatewayHealth
    telemetry: StatusTelemetry
    body: str
    claims: Dict[str, bool] = field(
        default_factory=lambda: {
            "agent_deployed": False,
            "portal_created": False,
            "mls_connected": False,
            "voice_enabled": False,
            "calendar_synced": False,
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["gateway_health"] = self.gateway_health.to_dict()
        d["telemetry"] = self.telemetry.to_dict()
        return d


class StatusTelemetryReader:
    """P5: Parse ANTI_STATUS.md and HERMES_STATUS.md into structured standup bullets."""

    def __init__(
        self,
        anti_status_path: Optional[Path] = None,
        hermes_status_path: Optional[Path] = None,
    ):
        self.anti_status_path = Path(anti_status_path or DEFAULT_ANTI_STATUS)
        self.hermes_status_path = Path(hermes_status_path or DEFAULT_HERMES_STATUS)

    def read(self) -> StatusTelemetry:
        anti = self._read_text(self.anti_status_path)
        hermes = self._read_text(self.hermes_status_path)
        return self._parse(anti, hermes)

    @staticmethod
    def _read_text(path: Path) -> str:
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def _parse(self, anti: str, hermes: str) -> StatusTelemetry:
        t = StatusTelemetry()

        pid_match = re.search(r"Gateway Daemon PID\s+(\d+)", hermes, re.I)
        if not pid_match:
            pid_match = re.search(r"Daemon PID\s+(\d+)", hermes, re.I)
        if not pid_match:
            pid_match = re.search(r"PID\s+\*\*(\d+)\*\*", hermes)
        if pid_match:
            t.gateway_pid = pid_match.group(1)

        if re.search(r"Operational", hermes, re.I):
            t.gateway_status_line = "Operational"
        elif re.search(r"DOWN|degraded", hermes, re.I):
            t.gateway_status_line = "Degraded"

        t.hold_active = bool(re.search(r"HOLD.*#Alienware-hq|Alienware-hq.*HOLD", anti + hermes, re.I))

        a4 = re.search(r"A4[^\|]*\|\s*\*\*(IN PROGRESS|PASS|FAIL)[^*]*\*\*", anti, re.I)
        t.a4_status = a4.group(1).upper() if a4 else "unknown"
        t.phase_a_summary = f"A4 {t.a4_status}; gateway PID {t.gateway_pid or 'unknown'}"

        w_pass = len(re.findall(r"W[1-5].*\|\s*\*\*PASS", anti))
        if w_pass >= 5:
            t.rosie_wiring = "W1–W5 COMPLETE (all PASS)"
        elif w_pass > 0:
            t.rosie_wiring = f"W1–W5 partial ({w_pass}/5 PASS)"
        else:
            t.rosie_wiring = "W1–W5 not verified in status file"

        if re.search(r"Dry-Run Verification.*PASS|Dry-run.*\*\*PASS\*\*", anti, re.I | re.S):
            t.dry_run_status = "PASS"
        elif re.search(r"Dry-run|Dry-Run", anti, re.I):
            t.dry_run_status = "IN PROGRESS"

        for pnum in range(1, 6):
            row = re.search(rf"P{pnum}[^\|]*\|[^\n]+", anti)
            if row:
                t.cos_p_tasks[f"P{pnum}"] = row.group(0).split("|")[-1].strip()

        queued = re.search(r"## QUEUED[^\n]*\n\n([^\n#]+)", anti, re.S)
        t.anti_queue = queued.group(1).strip() if queued else "None"

        t.cursor_queue = "See CURSOR_REVIEW.md for latest audit verdict"
        if re.search(r"all provisions are approved", anti, re.I):
            t.leo_decisions_needed.append("Awaiting A4 72h completion before first live APPROVE PROVISION")

        pytest = re.search(r"(\d+/\d+)\s+PASS", anti + hermes)
        if not pytest:
            pytest = re.search(r"\*\*(\d+/\d+)\s+PASS\*\*", anti + hermes)
        if pytest:
            t.pytest_count = pytest.group(1)

        return t


class GatewayHealthProbe:
    """P4: Probe gateway/desktop health; alert-first when degraded."""

    def __init__(
        self,
        dashboard_url: str = DEFAULT_GATEWAY_URL,
        timeout_sec: float = 2.0,
        probe_fn: Optional[Callable[[], GatewayHealth]] = None,
        telemetry: Optional[StatusTelemetryReader] = None,
    ):
        self.dashboard_url = dashboard_url
        self.timeout_sec = timeout_sec
        self.probe_fn = probe_fn
        self.telemetry = telemetry or StatusTelemetryReader()

    def probe(self) -> GatewayHealth:
        if self.probe_fn:
            return self.probe_fn()

        telemetry = self.telemetry.read()
        pid = telemetry.gateway_pid

        desktop_ok = False
        try:
            req = urllib.request.Request(self.dashboard_url, method="GET")
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                desktop_ok = 200 <= resp.status < 300
        except (urllib.error.URLError, TimeoutError, OSError):
            desktop_ok = False

        gateway_up = desktop_ok or telemetry.gateway_status_line.lower() == "operational"
        telegram_ok = gateway_up and telemetry.gateway_status_line.lower() == "operational"

        if not gateway_up:
            return GatewayHealth(
                gateway_up=False,
                gateway_pid=pid,
                telegram_ok=False,
                desktop_ok=desktop_ok,
                last_incident="Gateway process not reachable",
                alert_message="🚨 GATEWAY DOWN — Anti required\nGateway process not running. Standup paused until UP.",
                probe_source="http_probe",
            )

        return GatewayHealth(
            gateway_up=True,
            gateway_pid=pid,
            telegram_ok=telegram_ok,
            desktop_ok=desktop_ok,
            last_incident=telemetry.last_incident,
            alert_message=None,
            probe_source="http_probe",
        )


class StandupComposer:
    """P1: Build §4 standup template for 8am and 6pm ET delivery."""

    SLOT_LABELS = {"morning": "8:00 AM", "evening": "6:00 PM"}

    def compose(
        self,
        slot: str,
        health: GatewayHealth,
        telemetry: StatusTelemetry,
        now: Optional[datetime] = None,
    ) -> StandupPayload:
        slot_norm = slot.lower().strip()
        if slot_norm not in self.SLOT_LABELS:
            raise ValueError(f"Invalid standup slot '{slot}'. Use 'morning' or 'evening'.")

        dt = now or datetime.now(ET)
        time_label = self.SLOT_LABELS[slot_norm]
        date_label = dt.strftime("%Y-%m-%d")
        ts_et = f"{date_label} {time_label} ET"

        if not health.gateway_up:
            body = health.alert_message or "🚨 GATEWAY DOWN — Anti required"
            return StandupPayload(
                slot=slot_norm,
                timestamp_et=ts_et,
                gateway_health=health,
                telemetry=telemetry,
                body=body.strip(),
            )

        gw_flag = "UP" if health.gateway_up else "DOWN"
        tg_flag = "OK" if health.telegram_ok else "FAIL"
        desk_flag = "OK" if health.desktop_ok else "FAIL"
        pid = health.gateway_pid or "unknown"

        open_briefs = "0 staged (see onboarding-briefs/)"
        awaiting_leo = "1" if telemetry.dry_run_status == "PASS" else "0"

        anti_line = f"A4 {telemetry.a4_status}; {telemetry.phase_a_summary.split(';')[0]}"
        cursor_line = telemetry.cursor_queue

        decisions = telemetry.leo_decisions_needed or ["None"]
        decisions_block = "\n".join(f"• {d}" for d in decisions)

        if slot_norm == "morning":
            next_action = "Monitor gateway health; surface any new onboarding briefs to Leo."
        else:
            next_action = "Prepare evening summary; verify A4 uptime watch continuity."

        body = f"""HERMES STANDUP — {date_label} {time_label} ET

ENGINE
• Gateway: {gw_flag} PID {pid} | Telegram: {tg_flag} | Desktop :9119: {desk_flag}
• Last incident: {health.last_incident}

ROSIE ONBOARDING
• Open briefs: {open_briefs} | Awaiting Leo: {awaiting_leo}
• Dry-run status: {telemetry.dry_run_status}
• Wiring: {telemetry.rosie_wiring}
• Blocker: {"A4 72h watch in progress" if telemetry.a4_status == "IN PROGRESS" else "none"}

TEAM QUEUE
• Anti (Phase A): {anti_line}
• Cursor (Phase B): {cursor_line}

LEO DECISIONS NEEDED
{decisions_block}

NEXT AUTO ACTION (Hermes)
• {next_action}

POSTURE (§12)
• STAGED ONLY | Agent deployed: NO | Public portal live: NO | MLS connected: NO
• HOLD #Alienware-hq: {"ACTIVE" if telemetry.hold_active else "unchanged"}"""

        return StandupPayload(
            slot=slot_norm,
            timestamp_et=ts_et,
            gateway_health=health,
            telemetry=telemetry,
            body=body.strip(),
        )


class CosProactiveEngine:
    """Orchestrates P1–P5 proactive CoS operations."""

    def __init__(
        self,
        anti_status_path: Optional[Path] = None,
        hermes_status_path: Optional[Path] = None,
        cos_profile_path: Optional[Path] = None,
        gateway_probe_fn: Optional[Callable[[], GatewayHealth]] = None,
        evidence_dir: Optional[Path] = None,
    ):
        self.telemetry_reader = StatusTelemetryReader(anti_status_path, hermes_status_path)
        self.health_probe = GatewayHealthProbe(probe_fn=gateway_probe_fn, telemetry=self.telemetry_reader)
        self.composer = StandupComposer()
        self.cos_profile_path = Path(cos_profile_path or DEFAULT_COS_PROFILE_PATH)
        self.evidence_dir = Path(evidence_dir or EVIDENCE_DIR)
        self.standup_evidence = self.evidence_dir / "cos_standup_latest.json"

    def read_telemetry(self) -> StatusTelemetry:
        return self.telemetry_reader.read()

    def probe_gateway(self) -> GatewayHealth:
        return self.health_probe.probe()

    def build_standup(self, slot: str = "morning") -> StandupPayload:
        telemetry = self.read_telemetry()
        health = self.probe_gateway()
        payload = self.composer.compose(slot, health, telemetry)
        self._stage_standup(payload)
        return payload

    def build_cron_delivery(self, slot: str = "morning") -> str:
        """P4: Gateway alert preamble + standup body (or alert-only if DOWN)."""
        return self.build_standup(slot).body

    def compose_proactive_reply(self, user_message: str, slot: str = "morning") -> str:
        """P2: Convert passive greetings into proactive standup (§2)."""
        msg = user_message.strip().lower()
        standup = self.build_standup(slot).body

        if any(trigger in msg for trigger in GREETING_TRIGGERS) or len(msg) <= 12:
            return f"Hello, Leo. Here's your standup:\n\n{standup}"

        return standup

    @staticmethod
    def is_passive_echo_only(response: str) -> bool:
        """Returns True if response violates §2 (passive echo only)."""
        normalized = response.strip().lower()
        if len(normalized) > 120:
            return False
        return any(pat in normalized for pat in PASSIVE_ECHO_PATTERNS)

    @staticmethod
    def verify_response_quality(response: str) -> Tuple[bool, List[str]]:
        """P2/§9: Self-check rubric validation."""
        issues: List[str] = []
        lower = response.lower()

        has_status = any(k in lower for k in ("gateway", "standup", "engine", "blocker", "phase a", "rosie"))
        has_action = any(k in lower for k in ("next auto action", "monitor", "prepare", "surface"))
        has_decision = any(k in lower for k in ("leo decisions", "approve", "defer", "awaiting"))

        if not (has_status or has_action or has_decision):
            issues.append("Missing status, action, or decision request (§2)")

        if CosProactiveEngine.is_passive_echo_only(response):
            issues.append("Passive echo-only response forbidden (§2)")

        false_claim_phrases = (
            "portal live: yes",
            "mls connected: yes",
            "agent deployed: yes",
            "voice enabled: yes",
        )
        for phrase in false_claim_phrases:
            if phrase in lower:
                issues.append(f"False live claim detected: {phrase} (§12)")

        secret_markers = ("api_key", "sk-", "bearer ", "password:")
        for marker in secret_markers:
            if marker in lower:
                issues.append(f"Possible secret content: {marker} (§9)")

        return len(issues) == 0, issues

    def verify_prompt_block(self, soul_content: Optional[str] = None) -> Tuple[bool, List[str]]:
        """Verify §2 + §9 prompt block content."""
        required = [
            "Proactive Chief of Staff Operating Protocol",
            "FORBIDDEN as sole response",
            "Response Quality Rubric",
            "Zero False Claims",
            "HOLD on #Alienware-hq",
        ]
        content = soul_content if soul_content is not None else COS_PROACTIVE_PROMPT_BLOCK
        missing = [s for s in required if s not in content]
        return len(missing) == 0, missing

    def sync_prompt_block_to_profile(self) -> bool:
        """Append P2 prompt block to CoS SOUL.md if not already present."""
        if not self.cos_profile_path.exists():
            return False
        existing = self.cos_profile_path.read_text(encoding="utf-8")
        if "Proactive Chief of Staff Operating Protocol" in existing:
            return True
        updated = existing.rstrip() + "\n\n" + COS_PROACTIVE_PROMPT_BLOCK.strip() + "\n"
        self.cos_profile_path.write_text(updated, encoding="utf-8")
        return True

    def _stage_standup(self, payload: StandupPayload) -> None:
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        with open(self.standup_evidence, "w", encoding="utf-8") as f:
            json.dump(payload.to_dict(), f, indent=2)


cos_proactive = CosProactiveEngine()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hermes CoS Proactive Standup Engine (P1–P5)")
    parser.add_argument("--standup", choices=["morning", "evening"], default="morning")
    parser.add_argument("--probe", action="store_true", help="Gateway health probe only")
    args = parser.parse_args()

    engine = CosProactiveEngine()
    if args.probe:
        health = engine.probe_gateway()
        print(json.dumps(health.to_dict(), indent=2))
    else:
        print(engine.build_cron_delivery(args.standup))
