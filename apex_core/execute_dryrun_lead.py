"""Dry-run mock lead onboarding executor per ROSIE_ONBOARDING_SOP.md §9.

Executes:
1. Staging discovery brief (DRYRUN Rosie Test, Apex Staging Brokerage, Estero FL)
2. Hermes CoS triage checklist validation
3. Gated tenant provision under business-scope/tenants/dryrun-rosie-test/
4. Multi-agent draft generation (Harbor, Keystone, Quill)
5. Zero-external-send verification & false-claims audit
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from apex_core.provision_executor import (
    execute_gated_provision,
    resolve_briefs_dir,
    resolve_tenants_dir,
    utc_now_iso,
)

logger = logging.getLogger("dryrun_lead")


def run_dryrun_lead() -> Dict[str, Any]:
    briefs_dir = resolve_briefs_dir()
    tenants_dir = resolve_tenants_dir()
    briefs_dir.mkdir(parents=True, exist_ok=True)
    tenants_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = "dryrun-rosie-test"
    brief_stem = f"{timestamp}-{slug}"

    brief_data: Dict[str, Any] = {
        "kind": "apex_realtor_onboarding_brief",
        "status": "staged",
        "received_at": utc_now_iso(),
        "answers": {
            "full_name": "DRYRUN Rosie Test",
            "brokerage": "Apex Staging Brokerage",
            "market": "Estero, FL",
            "email": "dryrun.rosie@apexstaging.local",
            "needs": ["intake", "follow_up", "copy"],
        },
        "can_stage": [
            "Local brief only",
            "Tenant profile skeleton",
            "Specialist draft queue generation",
        ],
        "needs_verification": [
            "Brokerage MLS board affiliation",
            "Realtor photo & bio approval",
        ],
        "optional": ["Bilingual Spanish follow-up templates"],
        "claims": {
            "agent_deployed": False,
            "portal_created": False,
            "mls_connected": False,
            "voice_enabled": False,
            "calendar_synced": False,
        },
        "hermes_triage_at": utc_now_iso(),
        "hermes_stage": "STAGE:READY",
        "leo_decision": "APPROVE PROVISION DRYRUN",
        "assigned_tenant_slug": slug,
    }

    json_path = briefs_dir / f"{brief_stem}.json"
    md_path = briefs_dir / f"{brief_stem}.md"
    json_path.write_text(json.dumps(brief_data, indent=2), encoding="utf-8")

    md_content = f"""# Staged Realtor Brief — {brief_stem}

- Status: staged (not deployed)
- Created: {brief_data['received_at']}
- Surface: dry-run mock lead (§9 ROSIE_ONBOARDING_SOP.md)

## Answers
- **full_name:** {brief_data['answers']['full_name']}
- **brokerage:** {brief_data['answers']['brokerage']}
- **market:** {brief_data['answers']['market']}
- **email:** {brief_data['answers']['email']}
- **needs:** {', '.join(brief_data['answers']['needs'])}

## Hermes Triage (§6)
- **Triage Timestamp:** {brief_data['hermes_triage_at']}
- **Stage Classification:** {brief_data['hermes_stage']}
- **Executive Decision:** {brief_data['leo_decision']}
- **Assigned Tenant Slug:** {brief_data['assigned_tenant_slug']}

## Claims That Remain False (§12)
- Agent deployed: no
- Portal URL created: no
- MLS / IDX / ShowingTime: no
- Voice or calendar sync: no
"""
    md_path.write_text(md_content, encoding="utf-8")

    provision_result = execute_gated_provision(
        brief_data,
        brief_path=json_path,
        tenants_dir=tenants_dir,
        force_dryrun=True,
    )

    drafts_exist = all(Path(p).exists() for p in provision_result["drafts_generated"].values())

    return {
        "status": "PASS" if drafts_exist else "FAIL",
        "dryrun_lead": brief_data["answers"]["full_name"],
        "brief_json": str(json_path),
        "brief_markdown": str(md_path),
        "tenant_dir": provision_result["tenant_dir"],
        "provision_gate": provision_result["provision_gate"],
        "drafts_generated": provision_result["drafts_generated"],
        "false_claims_clean": provision_result["false_claims_clean"],
        "external_sends_performed": provision_result["external_sends_performed"],
    }


if __name__ == "__main__":
    result = run_dryrun_lead()
    print("Dry-Run Lead Execution Result:")
    print(json.dumps(result, indent=2))
