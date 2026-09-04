"""
Apex Luxury AI — Hermes Tenant Skeleton Manager (W4)
Per ROSIE_ONBOARDING_SOP.md §8 & §10 and ANTI_STATUS.md W4.

Manages:
1. Tenant skeleton template under hermes-state/profiles/real-estate-copilot/tenants/skeleton/
2. Provisioning sovereign tenant skeletons (Harbor, Keystone, Quill) under real-estate-copilot/tenants/{slug}/
3. Syncing and verifying SOUL.md in real-estate-copilot profile with §8 specialist delegation protocols.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

DEFAULT_PROFILE_DIR = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-state\profiles\real-estate-copilot")
DEFAULT_TENANTS_DIR = DEFAULT_PROFILE_DIR / "tenants"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


ROSIE_SOUL_DELEGATION_BLOCK = """
## Tenant Workspace & Specialist Delegation (§8 ROSIE_ONBOARDING_SOP.md)

Active Tenant Skeleton Root: `tenants/rosie/`
Specialist Fleet & Roles:
- **Harbor Specialist** (`harbor/`): Inbound lead routing, qualification questionnaires, and follow-up queue management.
- **Keystone Specialist** (`keystone/`): Neighborhood valuation benchmarks, CMA consult packets, and Florida property adjustments.
- **Quill Specialist** (`quill/`): MLS public/private remarks, lifestyle marketing copy, and social media announcements.

### Operating & Delegation Rules (§8 & §12 SOP):
1. **Internal Drafts Only**: All specialist outputs land in tenant folders as drafts pending review.
2. **Zero External Send**: Never send client emails, SMS, or publish remarks without explicit operator and realtor approval.
3. **Zero False Claims**: All claims regarding live agent deployment, public portals, or MLS connections remain strictly false.
"""


class TenantSkeletonManager:
    """Manages tenant skeletons under hermes-state/profiles/real-estate-copilot/."""

    def __init__(
        self,
        profile_dir: Optional[Path] = None,
        tenants_dir: Optional[Path] = None,
    ):
        self.profile_dir = Path(profile_dir) if profile_dir else DEFAULT_PROFILE_DIR
        self.tenants_dir = Path(tenants_dir) if tenants_dir else (self.profile_dir / "tenants")
        self.soul_path = self.profile_dir / "SOUL.md"

    def ensure_skeleton_template(self) -> Path:
        """Creates the canonical template skeleton under tenants/skeleton/."""
        skeleton_dir = self.tenants_dir / "skeleton"
        harbor_dir = skeleton_dir / "harbor"
        keystone_dir = skeleton_dir / "keystone"
        quill_dir = skeleton_dir / "quill"

        for d in (skeleton_dir, harbor_dir, keystone_dir, quill_dir):
            d.mkdir(parents=True, exist_ok=True)

        manifest = {
            "template_name": "Sovereign Realtor OS — Tenant Skeleton",
            "version": "1.0.0",
            "created_at": utc_now_iso(),
            "specialists": ["harbor", "keystone", "quill"],
            "status": "template",
            "send_gate": "LEO_AND_REALTOR_APPROVAL_REQUIRED",
            "claims": {
                "agent_deployed": False,
                "portal_created": False,
                "mls_connected": False,
                "voice_enabled": False,
                "calendar_synced": False
            }
        }
        (skeleton_dir / "TENANT_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        # Template SOUL
        soul_content = (
            "# Sovereign Realtor AI CoPilot\n\n"
            "You are a dedicated Private Real Estate AI CoPilot for an independent luxury realtor.\n"
            "You coordinate with Harbor (CRM & Follow-up), Keystone (CMA & Valuation), and Quill (Marketing Copy).\n"
            "All generated outputs are internal drafts pending explicit realtor review.\n"
        )
        (skeleton_dir / "SOUL.md").write_text(soul_content, encoding="utf-8")

        # Harbor seed
        harbor_init = {
            "queue_name": "Inbound Lead Follow-Up Queue",
            "status": "DRAFT_PENDING_APPROVAL",
            "entries": []
        }
        (harbor_dir / "follow_up_queue.json").write_text(json.dumps(harbor_init, indent=2), encoding="utf-8")
        (harbor_dir / "lead_triage_protocol.md").write_text(
            "# Harbor Lead Triage Protocol\n\n"
            "1. Casual introductory SMS draft.\n"
            "2. 3 core qualification questions (pre-approval, timeline, target sub-market).\n",
            encoding="utf-8"
        )

        # Keystone seed
        (keystone_dir / "cma_guidelines.md").write_text(
            "# Keystone Comparative Market Analysis Guidelines\n\n"
            "- Establish local $/sqft benchmark range.\n"
            "- Apply pool/lanai, roof, and view adjustments.\n"
            "- Deliver 3 strategic pricing tiers (conservative, target, premium).\n",
            encoding="utf-8"
        )

        # Quill seed
        (quill_dir / "marketing_templates.md").write_text(
            "# Quill Marketing & MLS Remarks Engine\n\n"
            "- Public MLS remarks highlighting architectural features & Florida lifestyle.\n"
            "- Private broker remarks.\n"
            "- Instagram/Facebook social media captions with hashtags.\n",
            encoding="utf-8"
        )

        return skeleton_dir

    def provision_tenant(
        self,
        slug: str,
        realtor_name: str,
        brokerage: str,
        market: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        team_name: Optional[str] = None,
        team_leader: Optional[str] = None,
        office_address: Optional[str] = None,
    ) -> Path:
        """Provisions a sovereign tenant skeleton directory under real-estate-copilot/tenants/{slug}/."""
        self.ensure_skeleton_template()

        tenant_dir = self.tenants_dir / slug
        harbor_dir = tenant_dir / "harbor"
        keystone_dir = tenant_dir / "keystone"
        quill_dir = tenant_dir / "quill"

        for d in (tenant_dir, harbor_dir, keystone_dir, quill_dir):
            d.mkdir(parents=True, exist_ok=True)

        manifest = {
            "tenant_slug": slug,
            "realtor_name": realtor_name,
            "brokerage": brokerage,
            "team_name": team_name,
            "team_leader": team_leader,
            "office_address": office_address,
            "market": market,
            "email": email or f"{slug}@sovereign.realtor",
            "phone": phone or "239-555-0100",
            "provisioned_at": utc_now_iso(),
            "status": "staged_drafts_only",
            "specialists": ["harbor", "keystone", "quill"],
            "send_gate": "LEO_AND_REALTOR_APPROVAL_REQUIRED",
            "claims": {
                "agent_deployed": False,
                "portal_created": False,
                "mls_connected": False,
                "voice_enabled": False,
                "calendar_synced": False
            }
        }
        (tenant_dir / "TENANT_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        # Customized tenant SOUL
        org_line = f" ({team_name}, {brokerage})" if team_name else f" ({brokerage})"
        mentor_note = f" Operating under mentor leadership of {team_leader}." if team_leader else ""
        tenant_soul = (
            f"# {realtor_name} — Real Estate AI CoPilot\n\n"
            f"You are the Private Real Estate AI CoPilot for {realtor_name}{org_line} covering {market}.{mentor_note}\n\n"
            f"## Specialists:\n"
            f"- **Harbor**: Lead intake, qualification questions, and follow-up routing.\n"
            f"- **Keystone**: Comparative Market Analysis (CMA), valuation adjustments, and contract timelines.\n"
            f"- **Quill**: MLS remarks, luxury marketing brochures, and social copy.\n\n"
            f"## Guardrails (§8 & §12 SOP):\n"
            f"- Posture: STAGED DRAFTS ONLY\n"
            f"- All deliverables require explicit signoff before external dispatch.\n"
        )
        (tenant_dir / "SOUL.md").write_text(tenant_soul, encoding="utf-8")

        # Specialist draft seeds
        harbor_data = {
            "realtor": realtor_name,
            "market": market,
            "queue": [],
            "status": "ACTIVE_STAGED"
        }
        (harbor_dir / "follow_up_queue.json").write_text(json.dumps(harbor_data, indent=2), encoding="utf-8")

        (keystone_dir / "cma_market_consult.md").write_text(
            f"# Keystone CMA Baseline — {market}\n\n"
            f"**Advisor:** {realtor_name}\n"
            f"**Brokerage:** {brokerage}\n"
            f"**Baseline Status:** Seeded\n",
            encoding="utf-8"
        )

        (quill_dir / "welcome_packet.md").write_text(
            f"# Sovereign Realtor Setup Guide — {realtor_name}\n\n"
            f"Welcome to Sovereign Realtor OS. Your specialist team (Harbor, Keystone, Quill) is staged.\n",
            encoding="utf-8"
        )

        return tenant_dir

    def verify_tenant_skeleton(self, slug: str) -> Tuple[bool, List[str]]:
        """Verifies that a tenant skeleton directory contains all required SOP artifacts."""
        tenant_dir = self.tenants_dir / slug
        if not tenant_dir.exists():
            return False, [f"Tenant directory does not exist: {tenant_dir}"]

        missing = []
        required_paths = [
            tenant_dir / "TENANT_MANIFEST.json",
            tenant_dir / "SOUL.md",
            tenant_dir / "harbor",
            tenant_dir / "harbor" / "follow_up_queue.json",
            tenant_dir / "keystone",
            tenant_dir / "quill",
        ]

        for p in required_paths:
            if not p.exists():
                missing.append(str(p.relative_to(self.tenants_dir)))

        # Verify claims inside manifest
        manifest_path = tenant_dir / "TENANT_MANIFEST.json"
        if manifest_path.exists():
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                claims = data.get("claims", {})
                for k, v in claims.items():
                    if v is True:
                        missing.append(f"SOP §12 violation: False claim '{k}' is True")
            except Exception as e:
                missing.append(f"Invalid JSON in manifest: {e}")

        return len(missing) == 0, missing

    def sync_rosie_profile_soul(self) -> bool:
        """Appends the specialist delegation block to real-estate-copilot/SOUL.md if missing."""
        if not self.soul_path.exists():
            return False

        existing = self.soul_path.read_text(encoding="utf-8")
        if "Tenant Workspace & Specialist Delegation" in existing:
            return True  # Already installed

        updated = existing.rstrip() + "\n\n" + ROSIE_SOUL_DELEGATION_BLOCK.strip() + "\n"
        self.soul_path.write_text(updated, encoding="utf-8")
        return True

    def verify_profile_loaded(self) -> Tuple[bool, List[str]]:
        """Verifies that real-estate-copilot profile exists, SOUL.md is loaded, and tenants dir is present."""
        if not self.profile_dir.exists():
            return False, [f"Profile directory not found: {self.profile_dir}"]

        missing = []
        if not self.soul_path.exists():
            missing.append("SOUL.md missing in profile directory")
        else:
            content = self.soul_path.read_text(encoding="utf-8")
            required_skills = [
                "Comparative Market Analysis (CMA)",
                "MLS Remarks & Marketing Copywriter",
                "Lead Triage & Qualification",
                "Transaction Coordinator",
            ]
            for skill in required_skills:
                if skill not in content:
                    missing.append(f"SOUL.md missing skill: {skill}")

        if not self.tenants_dir.exists():
            missing.append("tenants directory missing in profile directory")

        return len(missing) == 0, missing


if __name__ == "__main__":
    mgr = TenantSkeletonManager()
    print("Ensuring skeleton template...")
    t_path = mgr.ensure_skeleton_template()
    print(f"Skeleton template at: {t_path}")

    print("Provisioning Rosie tenant skeleton...")
    r_path = mgr.provision_tenant(
        slug="rosie",
        realtor_name="Rosie Rivera",
        brokerage="Rosie Rivera Luxury Real Estate",
        market="Estero & Naples, FL",
        email="rosie@rosieriveraluxury.com",
        phone="239-555-0144"
    )
    print(f"Rosie tenant skeleton at: {r_path}")

    print("Syncing real-estate-copilot SOUL.md...")
    synced = mgr.sync_rosie_profile_soul()
    print(f"SOUL.md synced: {synced}")

    ok, missing = mgr.verify_profile_loaded()
    print(f"Profile loaded: {ok}, missing: {missing}")

    tok, tmissing = mgr.verify_tenant_skeleton("rosie")
    print(f"Rosie skeleton verified: {tok}, missing: {tmissing}")
