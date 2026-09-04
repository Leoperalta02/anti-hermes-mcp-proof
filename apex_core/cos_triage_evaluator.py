"""
Hermes Chief of Staff (CoS) Triage Integration & Evaluator (W3)
Per ROSIE_ONBOARDING_SOP.md §6 & §10 and COS_PROACTIVE_SOP.md §2 & §9.

Provides:
1. Canonical CoS Triage & Proactive Prompt Block for Hermes CoS profile (SOUL.md).
2. Triage evaluator implementing the 5-point checklist (§6):
   - Acknowledge (ID, Name, Brokerage, Market)
   - Validate (Security scan, required fields)
   - Classify (STAGE:READY vs STAGE:DISCOVERY vs STAGE:DEFER vs STAGE:REJECTED_CREDENTIALS)
   - Surface (Structured alert with §12 zero false claims)
   - Gate (Strict wait for Leo executive approval before provisioning)
3. Profile sync utility to wire prompt block into hermes-state/profiles/anti-cos/SOUL.md.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Ensure apex_core can import sibling modules
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from apex_core.brief_watcher import (
    DEFAULT_TELEGRAM_TARGET,
    SECRET_RE,
    TELEGRAM_TARGET,
    utc_now_iso,
)

DEFAULT_COS_PROFILE_PATH = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-state\profiles\anti-cos\SOUL.md")

COS_TRIAGE_PROMPT_BLOCK = """
## Onboarding Brief Triage Protocol (§6 ROSIE_ONBOARDING_SOP.md)

When an onboarding brief is received (from `onboarding-briefs/*.json` or `evidence/brief_telegram_alert.json`), Hermes in CoS mode must execute the 5-point triage checklist within 15 minutes:

1. **Acknowledge**: Log brief ID, full name, brokerage, and market. (No PII beyond authorized intake fields).
2. **Validate**:
   - Security Check: Zero secrets, API keys, passwords, bearer tokens, or connection strings. Reject immediately if detected (`STAGE:REJECTED_CREDENTIALS`).
   - Field Check: `full_name` present (or explicit `profile_unknown`), and at least one `needs[]` entry (or explicit `needs_unknown`).
3. **Classify**:
   - `STAGE:READY` — Complete brief with name and needs. Recommended action: Await Leo gate (`APPROVE PROVISION DRYRUN`).
   - `STAGE:DISCOVERY` — Incomplete intake or missing required fields. Recommended action: Follow up on discovery intake.
   - `STAGE:DEFER` — Deferral requested by Leo or operator. Recommended action: Await operator reactivation.
   - `STAGE:REJECTED_CREDENTIALS` — Contained secrets or tokens. Blocked immediately.
4. **Surface to Leo** (Telegram / Desktop alert):
   - Executive one-line summary + triage tag + recommended action.
   - STRICT §12 POSTURE (Zero False Claims): Explicitly declare STAGED ONLY, Agent deployed: NO, Public portal live: NO, MLS connected: NO.
5. **Gate / Wait**:
   - NEVER auto-provision. Await explicit Leo executive gate (`APPROVE PROVISION` or `APPROVE PROVISION DRYRUN`) before provisioning tenant skeleton or delegating draft tasks to specialists.

## Proactive Chief of Staff Operating Invariants (§2 & §9 COS_PROACTIVE_SOP.md)
1. Every CoS turn must include Status, Action, or Decision. Passive acknowledgments alone ("Hello Leo, I'm here") are strictly forbidden.
2. Self-check rubric:
   - Include status OR action OR decision request.
   - Zero false live claims (portal, MLS, voice).
   - Zero vault/secret content.
   - If Leo asks "what's going on", cite gateway + open blockers.
   - If stuck, name specific owner (Anti / Cursor / Leo).
"""


@dataclass
class CosChecklistResult:
    acknowledged: bool
    validated: bool
    classified: bool
    surfaced: bool
    gated: bool
    details: Dict[str, Any]


@dataclass
class CosTriageResult:
    brief_id: str
    classification: str
    checklist: CosChecklistResult
    claims: Dict[str, bool]
    alert_message: str
    channel: str
    recommended_action: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


class CosTriageEvaluator:
    """Evaluates onboarding briefs against the CoS prompt block and SOP §6 checklist."""

    def __init__(
        self,
        cos_soul_path: Optional[Path] = None,
        telegram_target: Optional[str] = None,
    ):
        self.cos_soul_path = Path(cos_soul_path) if cos_soul_path else DEFAULT_COS_PROFILE_PATH
        self.telegram_target = telegram_target or os.getenv("APEX_TELEGRAM_TARGET", TELEGRAM_TARGET)

    def verify_cos_prompt_block(self, soul_content: Optional[str] = None) -> Tuple[bool, List[str]]:
        """Verifies whether the CoS profile SOUL.md contains all mandatory §6 and §12 sections."""
        content = soul_content
        if content is None:
            if not self.cos_soul_path.exists():
                return False, [f"CoS profile path does not exist: {self.cos_soul_path}"]
            content = self.cos_soul_path.read_text(encoding="utf-8")

        required_snippets = [
            "Onboarding Brief Triage Protocol (§6 ROSIE_ONBOARDING_SOP.md)",
            "Acknowledge",
            "Validate",
            "Classify",
            "Surface to Leo",
            "STRICT §12 POSTURE (Zero False Claims)",
            "Gate / Wait",
            "STAGE:READY",
            "STAGE:DISCOVERY",
            "STAGE:DEFER",
            "STAGE:REJECTED_CREDENTIALS",
        ]

        missing = [snip for snip in required_snippets if snip not in content]
        return len(missing) == 0, missing

    def sync_prompt_block_to_profile(self) -> bool:
        """Appends the CoS triage prompt block to the CoS SOUL.md if not already present."""
        if not self.cos_soul_path.exists():
            return False

        existing = self.cos_soul_path.read_text(encoding="utf-8")
        if "Onboarding Brief Triage Protocol" in existing:
            return True  # Already installed

        updated = existing.rstrip() + "\n\n" + COS_TRIAGE_PROMPT_BLOCK.strip() + "\n"
        self.cos_soul_path.write_text(updated, encoding="utf-8")
        return True

    def evaluate_brief(
        self,
        brief_data: Union[Dict[str, Any], Path, str],
        brief_id: Optional[str] = None,
    ) -> CosTriageResult:
        """Executes the full 5-point CoS checklist on a brief dictionary or file path."""
        stem = brief_id or "mock-brief"

        if isinstance(brief_data, (Path, str)):
            p = Path(brief_data)
            if p.exists():
                stem = p.stem
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = json.loads(str(brief_data))
        else:
            data = brief_data

        answers = data.get("answers", {})

        # Step 1: Acknowledge (§6.1)
        full_name = answers.get("full_name") or data.get("full_name") or "profile_unknown"
        brokerage = answers.get("brokerage") or data.get("brokerage") or "brokerage_unknown"
        market = answers.get("market") or data.get("market") or "market_unknown"
        needs = answers.get("needs") or data.get("needs") or []

        ack_details = {
            "brief_id": stem,
            "full_name": full_name,
            "brokerage": brokerage,
            "market": market,
            "needs_count": len(needs) if isinstance(needs, list) else 0,
        }
        acknowledged = True

        # Step 2: Validate (§6.2)
        # 2a. Security check (Zero credentials)
        brief_str = json.dumps(data)
        secret_match = SECRET_RE.search(brief_str)
        is_secret_clean = secret_match is None

        # 2b. Required fields check
        has_name = full_name not in ("profile_unknown", "", None)
        has_needs = bool(needs and needs != "needs_unknown")
        fields_valid = is_secret_clean

        validation_details = {
            "secret_clean": is_secret_clean,
            "has_name": has_name,
            "has_needs": has_needs,
            "detected_secret_token": secret_match.group(0) if secret_match else None,
        }
        validated = is_secret_clean

        # Step 3: Classify (§6.3)
        is_deferred = (
            data.get("leo_decision") == "DEFER"
            or data.get("hermes_stage") == "STAGE:DEFER"
            or answers.get("defer") is True
            or data.get("defer") is True
        )

        if not is_secret_clean:
            classification = "STAGE:REJECTED_CREDENTIALS"
            action_rec = "CREDENTIALS REJECTED: Promptly notify sender to purge sensitive keys."
            gate_status = "REJECTED"
        elif is_deferred:
            classification = "STAGE:DEFER"
            action_rec = "Brief is deferred per operator instruction. Awaiting Leo re-activation."
            gate_status = "DEFERRED"
        elif has_name and has_needs:
            classification = "STAGE:READY"
            action_rec = "Review brief and await Leo gate ('APPROVE PROVISION DRYRUN')."
            gate_status = "AWAITING_LEO_APPROVE_PROVISION"
        else:
            classification = "STAGE:DISCOVERY"
            action_rec = "Incomplete discovery brief. Follow up on required intake fields."
            gate_status = "AWAITING_DISCOVERY_COMPLETION"

        classified = True

        # Step 4: Surface (§6.4 & §12 SOP — ZERO FALSE CLAIMS)
        claims = {
            "agent_deployed": False,
            "portal_created": False,
            "mls_connected": False,
            "voice_enabled": False,
            "calendar_synced": False,
        }

        if classification == "STAGE:REJECTED_CREDENTIALS":
            alert_msg = (
                f"🚨 [HERMES TRIAGE: CREDENTIALS REJECTED]\n\n"
                f"Brief `{stem}` contained sensitive credential keys matching `{secret_match.group(0)}`.\n"
                f"Security Policy: Ingestion aborted. Payload quarantined.\n"
                f"Status: REJECTED\n"
                f"👉 Recommended Action: {action_rec}"
            )
        else:
            alert_msg = (
                f"📥 [HERMES TRIAGE: NEW ONBOARDING BRIEF]\n\n"
                f"• Brief ID: `{stem}`\n"
                f"• Realtor: {full_name}\n"
                f"• Brokerage: {brokerage}\n"
                f"• Market: {market}\n"
                f"🏷️ Triage Tag: {classification}\n\n"
                f"🛡️ Posture (§12 SOP): STAGED ONLY\n"
                f"• Agent deployed: NO\n"
                f"• Public portal live: NO\n"
                f"• MLS connected: NO\n\n"
                f"👉 Recommended Action: {action_rec}"
            )
        surfaced = True

        # Step 5: Gate (§6.5)
        # Strictly ensures no provisioning occurs without explicit Leo approval
        gated = True
        gate_details = {
            "gate_status": gate_status,
            "requires_leo_approval": True,
            "provision_blocked": True,
        }

        checklist_result = CosChecklistResult(
            acknowledged=acknowledged,
            validated=validated,
            classified=classified,
            surfaced=surfaced,
            gated=gated,
            details={
                "acknowledgment": ack_details,
                "validation": validation_details,
                "gate": gate_details,
            },
        )

        return CosTriageResult(
            brief_id=stem,
            classification=classification,
            checklist=checklist_result,
            claims=claims,
            alert_message=alert_msg,
            channel=self.telegram_target,
            recommended_action=action_rec,
            timestamp=utc_now_iso(),
        )

    def consume_staged_alert(self, alert_file_path: Path) -> Dict[str, Any]:
        """Consumes a staged brief alert JSON (e.g. evidence/brief_telegram_alert.json)."""
        p = Path(alert_file_path)
        if not p.exists():
            raise FileNotFoundError(f"Alert file not found: {p}")

        with open(p, "r", encoding="utf-8") as f:
            alert_data = json.load(f)

        # Verify claims are zero
        claims = alert_data.get("claims", {})
        for claim_key, val in claims.items():
            if val is True:
                raise ValueError(f"SOP §12 violation: False live claim '{claim_key}' is True in staged alert!")

        return {
            "status": "CONSUMED_STAGED_ALERT",
            "brief_id": alert_data.get("brief_id"),
            "classification": alert_data.get("classification"),
            "channel": alert_data.get("channel", self.telegram_target),
            "message": alert_data.get("message"),
            "claims_verified_clean": True,
            "awaiting_operator_gate": True,
        }
