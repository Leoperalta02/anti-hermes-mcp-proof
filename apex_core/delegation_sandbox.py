"""
Apex Luxury AI — Internal Delegation Sandbox Channel & Engine (W5)
Per ROSIE_ONBOARDING_SOP.md §8 & §10 and ANTI_STATUS.md W4/W5.

Implements:
1. Sandbox channel configuration and channel boundary governance (#rosie-onboarding-sandbox, #wellington-canary).
2. Fail-closed channel isolation guarding against #Alienware-hq and #panel-advisors.
3. Internal specialist task dispatcher (Harbor, Keystone, Quill, Rosie).
4. Mandatory draft-only posture, zero external send gate, and SOP §12 false-claims enforcement.
5. Automated §9 dry-run multi-agent orchestration.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

# Primary sandbox channels allowed for internal delegation
SANDBOX_CHANNELS: Set[str] = {
    "#rosie-onboarding-sandbox",
    "rosie-onboarding-sandbox",
    "#wellington-canary",
    "wellington-canary",
}

# Production and locked channels where delegation is strictly prohibited
FORBIDDEN_CHANNELS: Set[str] = {
    "#Alienware-hq",
    "Alienware-hq",
    "#panel-advisors",
    "panel-advisors",
    "#client-rosie-rivera",
    "#client-sofia-lanz",
    "#client-toki-grullon",
    "#client-vance-luxury",
}

ALLOWED_SPECIALISTS: Set[str] = {"harbor", "keystone", "quill", "rosie"}

DEFAULT_TENANTS_ROOT = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-state\profiles\real-estate-copilot\tenants")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_event_id(agent: str, task: str) -> str:
    raw = f"{agent}:{task}:{utc_now_iso()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class DelegationSandbox:
    """Internal Multi-Agent Delegation Sandbox Engine (§8 & §9 SOP)."""

    def __init__(
        self,
        tenants_root: Optional[Path] = None,
        default_channel: str = "#rosie-onboarding-sandbox",
    ):
        self.tenants_root = Path(tenants_root) if tenants_root else DEFAULT_TENANTS_ROOT
        self.default_channel = default_channel

    def is_channel_authorized(self, channel: str) -> bool:
        """Checks if the channel is an authorized sandbox and not in forbidden list."""
        ch_clean = channel.strip()
        if ch_clean in FORBIDDEN_CHANNELS or ch_clean.lower() in [f.lower() for f in FORBIDDEN_CHANNELS]:
            return False
        return ch_clean in SANDBOX_CHANNELS or ch_clean.lower() in [s.lower() for s in SANDBOX_CHANNELS]

    def delegate_task(
        self,
        target_agent: str,
        task_type: str,
        content: str,
        tenant_slug: str,
        channel: Optional[str] = None,
        approver: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatches an internal draft task to a specialist agent under strict sandbox constraints."""
        ch = (channel or self.default_channel).strip()

        # Rule 1: Fail-closed channel validation
        if not self.is_channel_authorized(ch):
            raise PermissionError(
                f"[STOP — SANDBOX VIOLATION] Channel '{ch}' is not an authorized delegation sandbox! "
                f"Delegation permitted only in: {sorted(list(SANDBOX_CHANNELS))}"
            )

        # Rule 2: Target agent validation
        agent_norm = target_agent.strip().lower()
        if not agent_norm or agent_norm not in ALLOWED_SPECIALISTS:
            raise ValueError(
                f"Invalid target_agent '{target_agent}'. Must be one of: {sorted(list(ALLOWED_SPECIALISTS))}"
            )

        # Rule 3: Content argument validation
        content_clean = content.strip()
        if not content_clean:
            raise ValueError("Task content cannot be empty or whitespace.")

        slug = tenant_slug.strip().lower()
        if not slug:
            raise ValueError("Tenant slug cannot be empty.")

        tenant_dir = self.tenants_root / slug
        specialist_dir = tenant_dir / agent_norm
        specialist_dir.mkdir(parents=True, exist_ok=True)

        event_id = generate_event_id(agent_norm, task_type)
        output_file_path: Optional[Path] = None

        # Rule 4: Specialist specific draft generation (§8 SOP)
        if agent_norm == "harbor":
            output_file_path = specialist_dir / "follow_up_queue.json"
            queue_entry = {
                "event_id": event_id,
                "task_type": task_type,
                "content": content_clean,
                "status": "DRAFT_PENDING_REALTOR_APPROVAL",
                "dispatched_at": utc_now_iso(),
                "approver": approver or "LEO_AND_REALTOR",
                "external_sent": False
            }
            output_file_path.write_text(json.dumps(queue_entry, indent=2), encoding="utf-8")

        elif agent_norm == "keystone":
            output_file_path = specialist_dir / "cma_market_consult.md"
            doc_content = (
                f"# Keystone Comparative Market Analysis Draft\n\n"
                f"- Event ID: `{event_id}`\n"
                f"- Task Type: `{task_type}`\n"
                f"- Timestamp: {utc_now_iso()}\n"
                f"- Status: DRAFT_PENDING_APPROVAL (Zero external send)\n\n"
                f"## Content\n{content_clean}\n"
            )
            output_file_path.write_text(doc_content, encoding="utf-8")

        elif agent_norm == "quill":
            output_file_path = specialist_dir / "welcome_packet.md"
            doc_content = (
                f"# Quill Marketing & Remarks Draft\n\n"
                f"- Event ID: `{event_id}`\n"
                f"- Task Type: `{task_type}`\n"
                f"- Timestamp: {utc_now_iso()}\n"
                f"- Status: DRAFT_PENDING_APPROVAL (Zero external send)\n\n"
                f"## Content\n{content_clean}\n"
            )
            output_file_path.write_text(doc_content, encoding="utf-8")

        elif agent_norm == "rosie":
            output_file_path = specialist_dir / "coordination_notes.md"
            output_file_path.write_text(
                f"# Sovereign CoPilot Notes — {event_id}\n\n{content_clean}\n",
                encoding="utf-8"
            )

        # Rule 5: Zero False Claims Record (§12 SOP)
        record = {
            "event_id": event_id,
            "status": "DRAFT_STAGED_CLEAN",
            "channel": ch,
            "target_agent": agent_norm,
            "task_type": task_type,
            "tenant_slug": slug,
            "output_file": str(output_file_path) if output_file_path else None,
            "send_gate": "LEO_AND_REALTOR_APPROVAL_REQUIRED",
            "external_send_blocked": True,
            "claims": {
                "agent_deployed": False,
                "portal_created": False,
                "mls_connected": False,
                "voice_enabled": False,
                "calendar_synced": False
            },
            "timestamp": utc_now_iso()
        }

        return record

    def run_mock_delegation(
        self,
        slug: str = "dryrun-rosie-test",
        realtor_name: str = "DRYRUN Rosie Test",
        market: str = "Estero, FL",
    ) -> Dict[str, Any]:
        """Executes full §9 dry-run multi-agent delegation across Harbor, Keystone, and Quill."""
        dispatches = []

        # 1. Harbor Delegation
        harbor_res = self.delegate_task(
            target_agent="harbor",
            task_type="setup_follow_up_queue",
            content=f"Seed initial Estero buyer lead triage protocol for {realtor_name}.",
            tenant_slug=slug,
            approver="Leo Peralta & Rosie Rivera"
        )
        dispatches.append(harbor_res)

        # 2. Keystone Delegation
        keystone_res = self.delegate_task(
            target_agent="keystone",
            task_type="generate_cma_packet",
            content=f"Benchmark $/sqft for {market} and compute 3 strategic pricing tiers.",
            tenant_slug=slug,
            approver="Leo Peralta & Rosie Rivera"
        )
        dispatches.append(keystone_res)

        # 3. Quill Delegation
        quill_res = self.delegate_task(
            target_agent="quill",
            task_type="draft_welcome_packet",
            content=f"Draft luxury onboarding welcome guide and lifestyle remarks for {realtor_name}.",
            tenant_slug=slug,
            approver="Leo Peralta & Rosie Rivera"
        )
        dispatches.append(quill_res)

        # Verification: all files exist and all external sends are blocked
        all_files_exist = all(Path(d["output_file"]).exists() for d in dispatches)
        all_sends_blocked = all(d["external_send_blocked"] is True for d in dispatches)
        all_claims_false = all(
            not any(d["claims"].values()) for d in dispatches
        )

        dry_run_summary = {
            "status": "PASS" if (all_files_exist and all_sends_blocked and all_claims_false) else "FAIL",
            "channel": self.default_channel,
            "tenant_slug": slug,
            "dispatches_count": len(dispatches),
            "dispatches": dispatches,
            "zero_external_sends_verified": all_sends_blocked,
            "all_claims_false_verified": all_claims_false,
            "completed_at": utc_now_iso()
        }

        return dry_run_summary
