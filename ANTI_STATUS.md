# Anti Status — Hermes / Rosie Ops

**Updated:** 2026-09-04 (Cursor sync after Anti Phase A report + GitHub push)  
**Executive gate:** Leo **APPROVE SOPs** recorded.

---

## Phase A — Engine (Anti)

| Task | Status | Evidence |
| --- | --- | --- |
| A1 Gateway supervision | **PASS** | WMI-detached daemon; Scheduled Task `Hermes_Gateway`; PID **37056** |
| A2 Electron git path fix | **PASS** | `allowUnsafeCustomBinary: true` in `git-review-ops.ts`; Desktop active |
| A3 SQLite Lease Guardian | **PASS** | `apex_core/lease_guardian.py` daemon PID **4284**; 28/28 tests |
| A4 72h uptime watch | **IN PROGRESS** | 12h+ clean; no unclean exits on gateway |
| A5 Telegram polling | **PASS** | Sticky polling active; 8am standup delivered to Telegram |
| A6 Aura Storage & Inbox Sentinel | **PASS** | WMI-detached daemon PID **33372**; 15-min heartbeat; Samsung Drive `D:\Email_Archives` |

**Commit:** `053aee7` on `github/main` (lease guardian + HERMES_STATUS)

---

## Phase B — Wiring (Authorized & Complete)

Leo **"all provisions are approved"** recorded. Specs on `github/main`: `ROSIE_ONBOARDING_SOP.md`, `COS_PROACTIVE_SOP.md`, `DELEGATION_SANDBOX_SPEC.md`.

### Rosie (`ROSIE_ONBOARDING_SOP.md` §10) — ALL W1–W5 VERIFIED & PASS ✅

| # | Task | Verify | Status |
| --- | --- | --- | --- |
| W1 | Folder watch/cron: `onboarding-briefs/*.json` → Hermes task | Test file triggers alert (`test_brief_watcher.py`) | **PASS** |
| W2 | Telegram alert template (no false claims) | Structured alert in `evidence/brief_telegram_alert.json` | **PASS** (Staged) |
| W3 | Hermes triage prompt block in CoS profile | Synced into `anti-cos/SOUL.md`; `cos_triage_evaluator.py` | **PASS** |
| W4 | Tenant skeleton under `hermes-state/profiles/real-estate-copilot/` | `tenant_skeleton_manager.py`; Rosie tenant & SOUL.md synced | **PASS** |
| W5 | Internal delegation sandbox | `delegation_sandbox.py`; multi-agent dry-run §9 passes; `send_managed_agent` sandbox guard | **PASS** |

### CoS (`COS_PROACTIVE_SOP.md` §10)

| # | Task | Verify |
| --- | --- | --- |
| P1 | Cron 8am + 6pm standup | Leo receives template |
| P2 | System prompt: §2 principle + §9 rubric | "hey" → standup, not echo |
| P3 | Folder watch: `onboarding-briefs/` | New file → 5 min alert |
| P4 | Gateway health probe in cron preamble | DOWN → alert first |
| P5 | Read `ANTI_STATUS.md` + `HERMES_STATUS.md` for standup | Matches live state |

---

## Tool Governance & Sandboxing Updates

- **`send_managed_agent` Channel Guards**:
  - `#panel-advisors` — hard blocked with `[STOP — TOOL DENY]`
  - `#Alienware-hq` — hard blocked with `[STOP — HOLD ACTIVE]`
  - Specialist agents (`Harbor`, `Keystone`, `Quill`, `Rosie`) — hard blocked outside sandbox channels (`#rosie-onboarding-sandbox`, `#wellington-canary`) with `[STOP — SANDBOX VIOLATION]`; fails closed if channel context is missing or None
- **Live Sync**: Synced to `C:\LEO-LAB-ANTIGRAVITY\hermes-agent\tools\managed_agent_tool.py`

---

## Dry-Run Verification (§9 ROSIE_ONBOARDING_SOP.md) — PASS

- **Executive Approval:** Leo Peralta sent **`all provisions are approved`** (and prior **`APPROVED PROVISION DRYRUN`**)
- **Execution Script:** `apex_core/execute_dryrun_lead.py` & `DelegationSandbox.run_mock_delegation()`
- **Result:** **PASS** (Zero external sends, all false-claim boundaries respected)
- **Lead Name:** `DRYRUN Rosie Test` (Apex Staging Brokerage, Estero FL)
- **Staged Brief:** `business-scope/onboarding-briefs/20260904T003033Z-dryrun-rosie-test.json` (.md included)
- **Staged Tenant:** `business-scope/tenants/dryrun-rosie-test/TENANT_MANIFEST.json`
- **Drafts Generated on Disk:**
  - **Harbor:** `business-scope/tenants/dryrun-rosie-test/harbor/follow_up_queue.json` & protocol
  - **Keystone:** `business-scope/tenants/dryrun-rosie-test/keystone/cma_market_consult.md`
  - **Quill:** `business-scope/tenants/dryrun-rosie-test/quill/listing_marketing_drafts.md`
- **Test Suite:** `python -m unittest discover -s tests` → **68/68 PASS** (0 failures, 0 errors)

---

## HOLD (unchanged)

- `#Alienware-hq` — HOLD
- Buzz / Nostr relay — retired
- Vapi production webhooks — HOLD until Leo separate gate

---

## QUEUED (from Leo / Hermes)

_None._
