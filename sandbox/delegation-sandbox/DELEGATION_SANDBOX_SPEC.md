# #rosie-onboarding-sandbox — Internal Delegation Sandbox Spec
# Version: 1.0 (approved)
# Authority: §8 & §10 ROSIE_ONBOARDING_SOP.md and §8 COS_PROACTIVE_SOP.md
# Posture: Internal Drafts Only · Sandbox Scoped · Zero External Send

---

## §1. Purpose & Channel Scope

This specification governs internal multi-agent delegation for sovereign realtor onboarding and dry-runs:
- **Sandbox Channels:** `#rosie-onboarding-sandbox`, `#wellington-canary`
- **Excluded / Blocked Channels:** `#Alienware-hq` (HOLD active), `#panel-advisors` (Boardroom governance lock)
- **Execution Surface:** Local filesystem tenant skeleton sandbox (`hermes-state/profiles/real-estate-copilot/tenants/{slug}/` and `business-scope/tenants/{slug}/`)

---

## §2. Roster & Roles

| Seat | Role | Scope | Output Target |
|------|------|-------|---------------|
| **Hermes** | Supervisor / Coordinator | Dispatches draft tasks to specialists after Leo triage approval (`APPROVE PROVISION DRYRUN`) | Daily Standup / Triage Log |
| **Harbor** | Lead Intake & Triage Specialist | Inbound routing, qualification questions, and follow-up queue | `tenants/{slug}/harbor/follow_up_queue.json` |
| **Keystone** | CMA & Valuation Specialist | Micro-comp analysis, $/sqft benchmarks, 3-tier pricing | `tenants/{slug}/keystone/cma_market_consult.md` |
| **Quill** | Copy & Marketing Specialist | MLS public/private remarks, welcome packets, social posts | `tenants/{slug}/quill/welcome_packet.md` |
| **Rosie** | Sovereign Realtor CoPilot | Context owner for Southwest Florida luxury real estate operations | `tenants/{slug}/SOUL.md` |

---

## §3. Invariant Governance Rules (§8 & §12 SOP)

1. **Internal Drafts Only**:
   All specialist deliverables land on disk as draft JSON or Markdown files with status `DRAFT_PENDING_REALTOR_APPROVAL`.
2. **Zero External Send**:
   Never dispatch emails, SMS, webhooks, or public MLS remarks to external recipients. Any live client outreach requires explicit dual approval from Leo and the realtor.
3. **Zero False Claims (§12 SOP)**:
   All claims remain strictly `false`:
   - `agent_deployed: false`
   - `portal_created: false`
   - `mls_connected: false`
   - `voice_enabled: false`
   - `calendar_synced: false`
4. **Tool & Channel Lockdown**:
   - `send_managed_agent` invocations are strictly locked to authorized sandbox channels.
   - Any invocation targeting `#Alienware-hq` or non-whitelisted channels fails closed (`[STOP — SANDBOX VIOLATION]`).
5. **Argument Integrity**:
   `target_agent` and `content` must be non-empty, sanitized strings. Empty or whitespace-only payloads raise immediate validation errors.
