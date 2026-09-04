"""
Apex Luxury AI — Gated Provision Executor (ROSIE_ONBOARDING_SOP §6.5 & §8)
Provisions tenant skeleton + specialist drafts only when Leo provision gate is open.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from apex_core.provision_gate import assert_provision_allowed, evaluate_provision_gate

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BRIEFS_DIR = Path(r"C:\LEO-LAB-ANTIGRAVITY\business-scope\onboarding-briefs")
DEFAULT_TENANTS_DIR = Path(r"C:\LEO-LAB-ANTIGRAVITY\business-scope\tenants")
_BRIEFS_FALLBACK = WORKSPACE_ROOT / "evidence" / "onboarding-briefs"
_TENANTS_FALLBACK = WORKSPACE_ROOT / "evidence" / "tenants"

SLUG_RE = re.compile(r"[^a-z0-9]+")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_briefs_dir() -> Path:
    env = os.getenv("APEX_BRIEFS_DIR")
    if env:
        return Path(env)
    if DEFAULT_BRIEFS_DIR.parent.exists():
        return DEFAULT_BRIEFS_DIR
    return _BRIEFS_FALLBACK


def resolve_tenants_dir() -> Path:
    env = os.getenv("APEX_TENANTS_DIR")
    if env:
        return Path(env)
    if DEFAULT_TENANTS_DIR.parent.exists():
        return DEFAULT_TENANTS_DIR
    return _TENANTS_FALLBACK


def slugify(name: str) -> str:
    slug = SLUG_RE.sub("-", (name or "tenant").lower()).strip("-")
    return slug[:48] or "tenant"


def derive_tenant_slug(brief: Dict[str, Any]) -> str:
    if brief.get("assigned_tenant_slug"):
        return str(brief["assigned_tenant_slug"])
    answers = brief.get("answers") if isinstance(brief.get("answers"), dict) else {}
    name = answers.get("full_name") or answers.get("brokerage") or "tenant"
    return slugify(str(name))


def _write_specialist_drafts(
    tenant_dir: Path,
    *,
    market: str,
    dryrun: bool,
) -> Dict[str, str]:
    harbor_dir = tenant_dir / "harbor"
    keystone_dir = tenant_dir / "keystone"
    quill_dir = tenant_dir / "quill"

    for d in (harbor_dir, keystone_dir, quill_dir):
        d.mkdir(parents=True, exist_ok=True)

    harbor_path = harbor_dir / "follow_up_queue.json"
    keystone_path = keystone_dir / "cma_market_consult.md"
    quill_path = quill_dir / "listing_marketing_drafts.md"

    if dryrun:
        harbor_payload = {
            "lead_name": "Mock Inbound Buyer",
            "market": market,
            "inquiry_type": "3-Bed Single Family Home w/ Screened Pool",
            "initial_sms_draft": (
                "Hi! Thanks for checking out homes in Estero. Are you looking to move "
                "within the next 30-60 days, or just browsing the market?"
            ),
            "status": "DRAFT_PENDING_REALTOR_APPROVAL",
        }
        keystone_body = (
            f"# Keystone Comparative Market Analysis Draft ({market})\n\n"
            "**Baseline $/sqft:** $260 - $320/sqft\n\n"
            "### 3 Strategic Pricing Tiers:\n"
            "1. **Conservative / 14-Day Fast Liquidation:** $525,000\n"
            "2. **Target Market List Price:** $565,000\n"
            "3. **Premium / Low-Inventory Test:** $595,000\n"
        )
        quill_body = (
            f"# Quill Marketing & MLS Drafts ({market})\n\n"
            "## MLS Public Remarks (Draft)\n"
            "Southwest Florida sanctuary draft — pending realtor approval.\n"
        )
    else:
        harbor_payload = {
            "queue_name": "Inbound Lead Follow-Up Queue",
            "status": "DRAFT_PENDING_APPROVAL",
            "entries": [],
        }
        keystone_body = (
            f"# Keystone Comparative Market Analysis Guidelines ({market})\n\n"
            "- Establish local $/sqft benchmark range.\n"
            "- Apply pool/lanai, roof, and view adjustments.\n"
        )
        quill_body = (
            f"# Quill Marketing Templates ({market})\n\n"
            "- Public MLS remarks draft.\n"
            "- Private broker remarks draft.\n"
        )

    harbor_path.write_text(json.dumps(harbor_payload, indent=2), encoding="utf-8")
    keystone_path.write_text(keystone_body, encoding="utf-8")
    quill_path.write_text(quill_body, encoding="utf-8")

    return {
        "harbor": str(harbor_path),
        "keystone": str(keystone_path),
        "quill": str(quill_path),
    }


def execute_gated_provision(
    brief: Dict[str, Any],
    *,
    brief_path: Optional[Path] = None,
    tenants_dir: Optional[Path] = None,
    force_dryrun: bool = False,
) -> Dict[str, Any]:
    """
    Provision tenant skeleton when Leo gate allows. Raises PermissionError if blocked.
    """
    leo_decision = brief.get("leo_decision")
    provision_gate = assert_provision_allowed(leo_decision)

    answers = brief.get("answers") if isinstance(brief.get("answers"), dict) else {}
    slug = derive_tenant_slug(brief)
    market = answers.get("market") or "Southwest Florida"
    dryrun = force_dryrun or provision_gate["gate_mode"] == "DRYRUN"

    tenants_root = Path(tenants_dir) if tenants_dir else resolve_tenants_dir()
    tenants_root.mkdir(parents=True, exist_ok=True)
    tenant_dir = tenants_root / slug
    tenant_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "tenant_slug": slug,
        "provisioned_at": utc_now_iso(),
        "source_brief": str(brief_path) if brief_path else None,
        "status": "staged_drafts_only",
        "market": market,
        "specialists": ["harbor", "keystone", "quill"],
        "send_gate": "LEO_AND_REALTOR_APPROVAL_REQUIRED",
        "provision_gate": provision_gate["gate_mode"],
        "claims": provision_gate["claims"],
    }
    (tenant_dir / "TENANT_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    drafts = _write_specialist_drafts(tenant_dir, market=market, dryrun=dryrun)

    brief["assigned_tenant_slug"] = slug
    brief["provisioned_at"] = manifest["provisioned_at"]
    brief["provision_gate_mode"] = provision_gate["gate_mode"]

    if brief_path:
        brief_path.write_text(json.dumps(brief, indent=2), encoding="utf-8")

    return {
        "status": "PROVISIONED",
        "tenant_slug": slug,
        "tenant_dir": str(tenant_dir),
        "provision_gate": provision_gate,
        "drafts_generated": drafts,
        "false_claims_clean": True,
        "external_sends_performed": 0,
    }


def execute_gated_provision_from_file(
    brief_path: Path,
    *,
    tenants_dir: Optional[Path] = None,
    force_dryrun: bool = False,
) -> Dict[str, Any]:
    brief_path = Path(brief_path)
    with open(brief_path, "r", encoding="utf-8") as f:
        brief = json.load(f)
    return execute_gated_provision(
        brief,
        brief_path=brief_path,
        tenants_dir=tenants_dir,
        force_dryrun=force_dryrun,
    )


def evaluate_brief_provision_gate(brief: Dict[str, Any]) -> Dict[str, Any]:
    """Non-throwing gate evaluation for triage surfaces."""
    return evaluate_provision_gate(brief.get("leo_decision"))
