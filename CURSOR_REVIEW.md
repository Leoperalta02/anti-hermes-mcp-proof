# Cursor Review: Hermes Onboarding Wiring Stack (W1–W5) & Tool Governance

## Audit verdict: **PASS** — commit `76f0a69` (stack includes `89208e5`)

Audited `76f0a69` on `github/main`. The lint commit completes portable test imports; the governance rules landed in parent commit `89208e5`.

### 1. Fail-closed rules (`update_managed_agent_tool_governance.py`)

| Rule | Guard | Status |
| --- | --- | --- |
| `#panel-advisors` (existing) | `[STOP — TOOL DENY]` | **PASS** |
| **`#Alienware-hq` HOLD** (Rule 6) | `[STOP — HOLD ACTIVE]` — runs before arg parse / ACP relay | **PASS** |
| **Specialist sandbox** (Rule 7) | `[STOP — SANDBOX VIOLATION]` — Harbor, Keystone, Quill, Rosie blocked outside `#rosie-onboarding-sandbox` / `#wellington-canary` | **PASS** |
| **Missing channel context** (Rule 7b) | Fail-closed default: specialist blocked if `ch_val` is missing or None | **PASS** |

### 2. Portable imports (`76f0a69`)

**PASS** — `test_mention_tool.py` now uses:

```python
_managed_tool = importlib.import_module("tools.managed_agent_tool")  # try/except
@unittest.skipIf(_managed_tool is None, "tools.managed_agent_tool not found on this host")
```

- Path inserted only if `C:\LEO-LAB-ANTIGRAVITY\hermes-agent` exists
- No import-time crash in cloud CI
- All 8 governance tests skip gracefully when module is absent

### 3. Test execution comparison

| Metric | Cursor Cloud VM | Alienware Local Host |
| --- | --- | --- |
| **Ran** | 62 | 68 |
| **PASS** | 45 | **68 (100%)** |
| **SKIP** | 7 (`TestMentionAgentToolGovernance`) | 0 |
| **FAIL / ERROR** | 10 (Alienware-only harness dependencies) | **0** |

### 4. Non-blocking remediations applied

- **Harbor queue accumulation**: Dispatches accumulate as a list in `follow_up_queue.json`.
- **Fail-closed channel context**: Rule 7 updated in `managed_agent_tool.py` so that if ACP omits channel context (`ch_val is None`), specialist delegation immediately returns `[STOP — SANDBOX VIOLATION]`. Tested via `test_send_managed_agent_specialist_sandbox_guard_missing_channel`.

### 5. Operator gates progression

1. [x] **Leo §9 dry-run approval**: Leo confirmed **`all provisions are approved`**; mock delegation verified.
2. [x] **Wire `send_managed_agent` sandbox guard**: Live tool `managed_agent_tool.py` updated and verified (**8/8 PASS** in `test_mention_tool.py`).
3. [ ] **A4 72h gateway watch**: 12h+ clean, ongoing supervision.
4. [ ] **`APPROVE PROVISION` for first real realtor**: Pending live onboarding trigger.

Audit recorded and synchronized by Anti IDE.

---

# Role Switch (Sep 04, 2026 - 3:08 PM EDT)

**Division of Labor:**
- **Code Author:** Cursor
- **Auditor & Host Gatekeeper:** Antigravity (Anti)

### Active Mission: Listing & Media Intake Agent (`apex_core/listing_media_agent.py`)
- Full spec detailed in [`CURSOR_MISSION_LISTING_AGENT.md`](file:///c:/LEO-LAB-ANTIGRAVITY/anti-hermes-mcp-proof/CURSOR_MISSION_LISTING_AGENT.md).

## Audit Verdict: **PASS** — Commit `f818e11`
**Audited by Anti IDE on Alienware host (Sep 04, 2026 - 3:24 PM EDT)**

| Check | Specification | Result |
|---|---|---|
| **1. Ingest & Validation** | `ingest_property_submission` rejects missing fields, enforces `VALID_STATUSES` | **PASS** |
| **2. Security & Anti-Leak** | Rejects passwords, API keys, tokens via `SECRET_RE` per SOP §12 | **PASS** |
| **3. Keystone Benchmark** | Calculates $/sqft and ±5% comp corridor with Florida submarket benchmarks | **PASS** |
| **4. Quill Copywriting** | Generates Apple-style kinetic narrative staged under `tenants/{slug}/quill/` | **PASS** |
| **5. Showcase Staging** | Formats cleanly into `office_listings.json` with `FastSiteBuilder` compatibility | **PASS** |
| **6. Zero False Claims** | All `claims.*` strictly `False`; `external_send_blocked: True` | **PASS** |
| **7. Unit Test Suite** | 5/5 module tests pass; **89/89 overall host tests pass** (0.59s) | **PASS** |
| **8. Visual Browser Audit** | Front door kinetic carousel & Apple Lightbox Dossier Modal verified | **PASS** |

**Artifacts Generated & Verified:**
- Test Suite: `tests/test_listing_media_agent.py` (**5/5 PASS**, 0.053s)
- Browser Recording: `audit_listing_showcase_1788549685795.webp`
- Browser Screenshot: `estate_dossier_modal_1788549738369.png`

Audit synchronized and approved by Anti IDE.

---

# Audit Verdict: **PASS** — Commit `a5393a2`
**Audited by Anti IDE on Alienware host (Sep 04, 2026 - 3:36 PM EDT)**

### Mission: Media & Listing Intake Form + Sovereign Portal Queue Integration

| Check | Specification | Result | Evidence |
|---|---|---|---|
| **1. Intake Server** | `apex_core/listing_intake_server.py` (`GET /`, `POST /api/listing/submit`, `POST /api/listing/approve`) | **PASS** | HTTP server on port 8765 binds cleanly |
| **2. Portal Queue UI** | `public_sites/rosie/portal.html` — `Listings` nav tab with intake form & pending queue | **PASS** | Browser-verified on `:8000/public_sites/rosie/portal.html` |
| **3. Specialist Staging** | Displays Keystone calculated $/sqft, comp corridor spread, and Quill luxury copy | **PASS** | Staged under `tenants/{slug}/` with 1-click `✓ Approve for Showcase` |
| **4. Zero False Claims** | SOP §12 compliance badge (`STAGED — not live MLS`) | **PASS** | All `claims.*` strictly `False` across schemas |
| **5. Host Test Suite** | Unittests for server, queue, and media agent | **PASS** | **94 / 94 tests PASS** (0.75s) |
| **6. Browser Verification** | Interactive queue rendering and spec display | **PASS** | Verified via Jetski Browser subagent (`listing_intake_queue_1788550537036.png`) |

Audit synchronized and approved by Anti IDE.

---

## Cursor Implementation — Commit `531e58f` (pending Anti audit)

**Gated Telegram Dispatch (W2 live path)**
- `apex_core/telegram_dispatch.py` — stages alerts to `evidence/telegram_dispatch_latest.json`; live send only when `APEX_TELEGRAM_LIVE=1` + `APEX_TELEGRAM_BOT_TOKEN`
- Wired into `apex_core/brief_watcher.py` after alert staging
- Tests: `tests/test_telegram_dispatch.py` — 6/6 PASS

## Cursor Implementation — provision gate + onboarding dispatch (pending commit)

**Leo Provision Gate (SOP §6.5)**
- `apex_core/provision_gate.py` — fail-closed gate: DRYRUN allowed on `APPROVE PROVISION DRYRUN`; live requires `APPROVE PROVISION` + `APEX_A4_WATCH_COMPLETE=1`
- `apex_core/onboarding_pipeline.py` — requires `leo_decision` in payload; Hermes alert routed through `telegram_dispatch`
- Tests: `tests/test_provision_gate.py` — 7/7 PASS; onboarding pipeline updated for gate + dispatch

**Deferred to Anti:** Realtor mobile PWA / portal nav fix at ≤680px (Leo directive Sep 04).

## Operator Gate Lift — Sep 04, 2026 (Leo Peralta)

Recorded in `evidence/operator_gates.json`:
- `a4_watch_complete`: **true**
- `live_provision_enabled`: **true**
- `telegram_live_enabled`: **true**
- `#Alienware-hq` HOLD: **unchanged (still active)**

Live `APPROVE PROVISION` now passes gate check. Telegram live send still requires `APEX_TELEGRAM_BOT_TOKEN` on Alienware.

## Leo Executive Approval — Sep 04, 2026

**Decision:** `APPROVE PROVISION` (Leo: "approve")  
**Artifact:** `evidence/leo_provision_approval.json`  
**HQ HOLD:** **LIFTED** (`alienware_hq_hold_active: false` in operator_gates.json)  
**Governance:** `update_managed_agent_tool_governance.py` now reads operator_gates for conditional HQ block — Anti must re-run patch on Alienware.

## Cursor Implementation — provision executor (pending commit)

**Gated Provision Executor (§6.5 & §8)**
- `apex_core/provision_executor.py` — shared gated skeleton provisioning; portable briefs/tenants dir resolution
- `execute_dryrun_lead.py` refactored to use executor + gate
- `brief_watcher.py` — triage payloads include `provision_gate`; `--provision-approved` CLI scans and provisions approved briefs
- Tests: `tests/test_provision_executor.py` — 6/6 PASS; brief_watcher + dryrun updated

