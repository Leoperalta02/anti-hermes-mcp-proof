"""Local-only Rosy staging workspace loop.

Synthetic contacts and drafts only. There is deliberately no transport adapter:
approved items become copy-ready manual-send records, never external sends.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SECRET_RE = re.compile(r"(password|passwd|api[_-]?key|secret|token|bearer|authorization|connection string|private[_-]?key)", re.I)
CLAIMS = {"agent_deployed": False, "portal_created": False, "mls_connected": False, "voice_enabled": False, "calendar_synced": False}

def now() -> datetime:
    return datetime.now(timezone.utc)

def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:40] or "realtor"

def _paths(root: Path, tenant_id: str) -> tuple[Path, Path]:
    folder = root / "rosy-demo" / tenant_id
    return folder, folder / "workspace.json"

def _synthetic_contacts(needs: list[str], market: str) -> list[dict[str, Any]]:
    focus = "follow-up and qualification" if "follow_up" in needs or "intake" in needs else "practice priorities"
    due = (now() - timedelta(hours=2)).isoformat()
    tomorrow = (now() + timedelta(days=1)).date().isoformat()
    return [
        {"contact_id": "demo-contact-001", "display_name": "Maya Chen", "type": "buyer", "temperature": "hot", "pipeline": "buyer", "stage": "Qualified", "consent": "known", "next_follow_up_at": due, "synthetic": True, "market": market, "notes": f"Synthetic sample for {focus}."},
        {"contact_id": "demo-contact-002", "display_name": "Jordan Ellis", "type": "seller", "temperature": "warm", "pipeline": "listing", "stage": "Follow-up", "consent": "known", "next_follow_up_at": due, "synthetic": True, "market": market, "notes": "Synthetic sample seller opportunity."},
        {"contact_id": "demo-contact-003", "display_name": "Priya Shah", "type": "sphere", "temperature": "cold", "pipeline": "buyer", "stage": "New lead", "consent": "unknown", "next_follow_up_at": tomorrow, "synthetic": True, "market": market, "notes": "Synthetic sample with unknown consent; no outbound draft."},
    ]

def create_workspace(brief: dict[str, Any], root: Path) -> dict[str, Any]:
    if SECRET_RE.search(json.dumps(brief)):
        raise ValueError("credentials are not accepted")
    answers = brief.get("answers") if isinstance(brief.get("answers"), dict) else {}
    name = str(answers.get("full_name") or answers.get("brokerage") or "realtor")
    # Keep every submission in its own sandbox, even when the clock is frozen
    # or two same-name submissions arrive in the same millisecond.
    tenant_id = f"rosy-demo-{slug(name)}-{now().strftime('%Y%m%d%H%M%S%f')}-{uuid.uuid4().hex[:12]}"
    needs = answers.get("needs") if isinstance(answers.get("needs"), list) else []
    contacts = _synthetic_contacts(needs, str(answers.get("market") or "market not specified"))
    queue = []
    for contact in contacts:
        if contact["consent"] == "unknown":
            status = "due"
            draft = None
        else:
            status = "waiting_approval"
            draft = f"Hi {contact['display_name'].split()[0]}, checking in on your real estate plans. Would a quick update this week be useful? — {name}"
        queue.append({"item_id": f"{tenant_id}-item-{contact['contact_id'][-3:]}", "contact_id": contact["contact_id"], "reason": "Due today or overdue", "due_at": contact["next_follow_up_at"], "priority": contact["temperature"], "channel": "manual text", "status": status, "draft_body": draft, "next_follow_up_at": contact["next_follow_up_at"], "synthetic": True})
    workspace = {"tenant_id": tenant_id, "tenant_name": name, "surface": "private-rosy-demo", "environment": "STAGING / DEMO", "created_at": now().isoformat(), "source_needs": needs, "contacts": contacts, "queue": queue, "claims": CLAIMS.copy(), "send_gate": "EXTERNAL_SEND_DISABLED_COPY_READY_ONLY", "agent_workflow": {"agent": "Harbor (demo)", "result": "Daily follow-up queue built from synthetic contacts and submitted needs."}}
    folder, path = _paths(root, tenant_id)
    folder.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(workspace, indent=2), encoding="utf-8")
    return workspace

def load_workspace(root: Path, tenant_id: str) -> dict[str, Any] | None:
    _, path = _paths(root, tenant_id)
    if not path.exists(): return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("tenant_id") != tenant_id: return None
    return data

def transition_workspace(root: Path, tenant_id: str, item_id: str, action: str, snooze_date: str | None = None) -> dict[str, Any]:
    workspace = load_workspace(root, tenant_id)
    if not workspace: raise FileNotFoundError("workspace not found")
    item = next((x for x in workspace["queue"] if x["item_id"] == item_id), None)
    if not item: raise KeyError("queue item not found")
    if action == "approve":
        if not item.get("draft_body"): raise ValueError("item has no outbound draft")
        item["status"] = "approved_for_manual_send"
        item["send_evidence"] = "manual-copy-ready; external send disabled"
        item["next_follow_up_at"] = (now() + timedelta(days=3)).date().isoformat()
    elif action == "skip":
        item["status"] = "skipped"
        item["next_follow_up_at"] = (now() + timedelta(days=7)).date().isoformat()
    elif action == "snooze":
        if not snooze_date: raise ValueError("snooze date required")
        item["status"] = "snoozed"
        item["next_follow_up_at"] = snooze_date
    else: raise ValueError("unsupported action")
    _, path = _paths(root, tenant_id)
    path.write_text(json.dumps(workspace, indent=2), encoding="utf-8")
    return workspace
