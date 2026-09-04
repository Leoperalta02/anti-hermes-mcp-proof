"""
Apex Luxury AI — Leo Provision Gate (ROSIE_ONBOARDING_SOP §6.5)
Fail-closed gate before tenant skeleton provisioning or live onboarding.

Live provision requires:
  1. Leo decision matching APPROVE PROVISION (not DRYRUN)
  2. A4 watch complete (evidence/operator_gates.json or APEX_A4_WATCH_COMPLETE=1)

Dry-run provision requires:
  Leo decision matching APPROVE PROVISION DRYRUN
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

DRYRUN_PATTERN = re.compile(r"approve\s+provision\s+dryrun", re.IGNORECASE)
LIVE_PATTERN = re.compile(r"approve\s+provision(?!\s+dryrun)", re.IGNORECASE)
ALL_APPROVED_PATTERN = re.compile(r"all\s+provisions\s+are\s+approved", re.IGNORECASE)

DEFAULT_CLAIMS: Dict[str, bool] = {
    "agent_deployed": False,
    "portal_created": False,
    "mls_connected": False,
    "published_live": False,
    "voice_enabled": False,
    "calendar_synced": False,
}


from apex_core.operator_gates import is_a4_watch_complete as _operator_a4_complete


def is_a4_watch_complete() -> bool:
    return _operator_a4_complete()


def normalize_decision(decision: Optional[str]) -> str:
    return (decision or "").strip()


def classify_leo_decision(decision: Optional[str]) -> str:
    """Return DRYRUN, LIVE, ALL_APPROVED, or NONE."""
    text = normalize_decision(decision)
    if not text:
        return "NONE"
    if DRYRUN_PATTERN.search(text):
        return "DRYRUN"
    if LIVE_PATTERN.search(text):
        return "LIVE"
    if ALL_APPROVED_PATTERN.search(text):
        return "ALL_APPROVED"
    return "NONE"


def evaluate_provision_gate(
    leo_decision: Optional[str] = None,
    *,
    a4_complete: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Evaluate whether provisioning may proceed.

    Returns a gate record with provision_allowed, gate_mode, and reason.
    """
    decision_class = classify_leo_decision(leo_decision)
    a4_ok = is_a4_watch_complete() if a4_complete is None else a4_complete

    record: Dict[str, Any] = {
        "gate_mode": "BLOCKED",
        "provision_allowed": False,
        "requires_leo_approval": True,
        "provision_blocked": True,
        "decision_class": decision_class,
        "a4_watch_complete": a4_ok,
        "claims": dict(DEFAULT_CLAIMS),
        "reason": "No Leo executive gate recorded — provisioning blocked per SOP §6.5",
    }

    if decision_class == "DRYRUN":
        record.update(
            {
                "gate_mode": "DRYRUN",
                "provision_allowed": True,
                "provision_blocked": False,
                "reason": "APPROVE PROVISION DRYRUN — staged skeleton provisioning allowed",
            }
        )
        return record

    if decision_class in {"LIVE", "ALL_APPROVED"}:
        if not a4_ok:
            record.update(
                {
                    "gate_mode": "LIVE_BLOCKED_A4",
                    "reason": (
                        "Leo approval recorded but A4 72h gateway watch incomplete "
                        "(record lift in evidence/operator_gates.json or set APEX_A4_WATCH_COMPLETE=1)"
                    ),
                }
            )
            return record

        record.update(
            {
                "gate_mode": "LIVE",
                "provision_allowed": True,
                "provision_blocked": False,
                "reason": "APPROVE PROVISION — live provisioning gate open (operator confirmed A4)",
            }
        )
        return record

    return record


def assert_provision_allowed(
    leo_decision: Optional[str] = None,
    *,
    a4_complete: Optional[bool] = None,
) -> Dict[str, Any]:
    """Raise PermissionError if gate is closed; otherwise return gate record."""
    gate = evaluate_provision_gate(leo_decision, a4_complete=a4_complete)
    if not gate["provision_allowed"]:
        raise PermissionError(gate["reason"])
    return gate
