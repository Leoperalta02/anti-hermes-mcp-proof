# Hermes Agent Operational Status

**Last Updated:** September 6, 2026 - 2:42 PM EDT
**Status:** Operational — Hermes Desktop `v2026.8.31` verified clean install
**Hold State:** STRICT HOLD on `#Alienware-hq` (Maintained)  

## Current Access Verification — September 13, 2026

- The dual-host architecture is retained: Hermes/Anti have local execution surfaces on HQ and Node.
- This file's older PID, gateway, Telegram, and service claims are historical unless backed by a current receipt.
- Current HQ-local inspection found Hermes runtime processes, but did not prove the local `:9119` listener.
- A current HQ-to-Node probe found only RDP `:3389` and WinRM transport `:5985` reachable; Node application ports were not reachable.
- WinRM authenticated execution remains unverified after `0x8009030e`.
- The Node-local Hermes/Anti surface remains the preferred path for Node work. No RDP/WinRM/HP connector is required when that local surface is available.
- Full access from this specific HQ session is **not claimed** until a Node-local canary returns live Node identity and runtime evidence.
- Receipt: `evidence/DUAL_HOST_ACCESS_VERIFICATION_2026-09-13.md`.

## Verified Hermes Installation (September 6, 2026)

| Property | Value |
| ---------- | ------- |
| **Official Release** | `v2026.8.31` |
| **Backend Version** | `0.21.0` |
| **Desktop Shell** | `0.17.0` |
| **Commit** | `29112bef099274229cadff79cdff7bf7b99c4b77` |
| **Desktop PID** | `9412` |
| **Backend PID** | `36536` |
| **Stable Install Path** | `C:\hsi21` |
| **State / Profiles** | `C:\LEO-LAB-ANTIGRAVITY\hermes-state` (intact) |
| **Fixed By** | ChatGPT Codex (Atlas — Leo OS Command Center III) |
| **Root Cause** | Desktop received wrong `HERMES_HOME` env variable |

> **Note:** Desktop shell `0.17.0` and backend `0.21.0` are separate version numbers.
> Hermes checks development `main` which may be 1 commit ahead of stable release — do NOT click "Update now" to stay on stable.

**Prior Directives (Executed Under Leo's Guidance):**

- Purged front-door listing intake modal from public sites; enclosed strictly inside private portal (`portal.html#listings`).
- Built standalone mobile PWA app architecture for Rosie's portal (`manifest.json`, gold touch icons, install banner, tested at 390×844 mobile viewport).
- Cursor scoped as Alienware CLI dev fallback; live actions fail-closed; zero vault access. All tests 100% PASS.

---

## Architecture & Fleet Baseline

| Agent / Component | Runtime & Model Route | Role & Status |
| --- | --- | --- |
| **Hermes Gateway** | Python 3.11 venv (`hermes-state`) | Historical PID/telemetry claims only; legacy dashboard `http://127.0.0.1:9119` is not current live-health proof |
| **Lease Guardian** | `apex_core/lease_guardian.py` (PID 32880) | 60s Watchdog: auto-purges expired leases, restarts Gateway via WMI if dropped |
| **Cursor Bridge** | Node Daemon (`cursor-agent-api-proxy`, port 4646) | Profile `cursor`: `gpt-5.3-codex-low-fast` via local proxy (~1s response time) |
| **Aura (Sentinel)** | Local Ollama `qwen3.5:9b` (262k ctx, 100% offline) | HQ Sentinel & Multi-Drive Facility Organizer (`C:\`, `D:\`, `G:\`) |
| **Anti (CoS)** | Antigravity Native / Gemini Pro | Infrastructure Execution, Process Lifecycle, DB Integrity |
| **Relay / Buzz** | **RETIRED / DEPRECATED** | Legacy Nostr Buzz relays & rust `buzz-acp.exe` retired per user directive |

---

## Hardening & Incident Remediations Applied

1. **Gateway Process Lifecycle:**
   - Terminated ephemeral child processes killed by Windows Job Objects on shell closure.
   - Detached gateway from Job Objects via WMI process spawn (`PID 37056`).
   - Installed persistent Windows Login Item (`Hermes_Gateway.vbs`).
   - Verified single instance (`hermes gateway status` confirms single running PID: `37056`).

2. **SQLite Database Contention (`state.db`):**
   - Cleaned up stale turn leases in `session_turn_leases`.
   - Deployed automated Lease Guardian daemon (`apex_core/lease_guardian.py`, PID 32880) running 60s cycle.
   - Enforced single-writer rule with immediate connection termination to prevent WAL lock contention.

3. **`managed_agent_tool.py` Kwargs Merge:**
   - Patched `C:\LEO-LAB-ANTIGRAVITY\hermes-agent\tools\managed_agent_tool.py`.
   - Added keyword argument merging (`def _handler(args, **kw): ... merged.update(kw)`).
   - Restored fail-closed separate validations for empty `target_agent` vs `content`.
   - Verified panel advisor security barriers intact.

4. **Desktop Electron Path Validation:**
   - Verified `allowUnsafeCustomBinary: true` in `git-review-ops.ts` (line 59) preventing space-in-path unhandled exceptions.
   - Hermes desktop running cleanly without GUI crash.

5. **Rosie Dry-Run Lead Verification & Wiring Stack (§9 & §10 ROSIE_ONBOARDING_SOP.md):**
   - Executive approval: Leo Peralta recorded **`all provisions are approved`** (and prior `APPROVED PROVISION DRYRUN`).
   - W1–W5 Hermes onboarding stack fully verified:
     - W1: `brief_watcher.py` triage & folder monitoring.
     - W2: Telegram alert payload in `evidence/brief_telegram_alert.json`.
     - W3: `COS_TRIAGE_PROMPT_BLOCK` synced into active CoS `SOUL.md` (legacy `anti-cos` path decommissioned).
     - W4: `tenant_skeleton_manager.py` deployed with template & `tenants/rosie/` sandbox.
     - W5: `delegation_sandbox.py` dispatcher with draft posture and mock multi-agent delegation.
   - Executed mock lead intake via `apex_core/execute_dryrun_lead.py`: **PASS**.
   - Generated staged briefs and tenant skeleton (`dryrun-rosie-test`) with drafts from Harbor, Keystone, and Quill.
   - Zero external sends, zero false claims.

6. **Tool Governance & Sandboxing Enforcement:**
   - Patched `C:\LEO-LAB-ANTIGRAVITY\hermes-agent\tools\managed_agent_tool.py`:
     - `#panel-advisors` hard blocked with `[STOP — TOOL DENY]`.
     - `#Alienware-hq` hard blocked with `[STOP — HOLD ACTIVE]`.
     - Specialists (`Harbor`, `Keystone`, `Quill`, `Rosie`) restricted strictly to `#rosie-onboarding-sandbox` and `#wellington-canary` with `[STOP — SANDBOX VIOLATION]`; fails closed if channel context is missing or None.

7. **Test Suite Verification:**
   - `python -m unittest discover -s tests` → **82/82 PASS** (0 failures, 0 errors in 0.51s).

8. **CoS Proactive Stack (P1–P5 `COS_PROACTIVE_SOP.md` §10):**
   - `apex_core/cos_proactive.py` — standup composer (8am/6pm ET), gateway health probe preamble, telemetry reader, proactive reply composer.
   - P2 prompt block: §2 principle + §9 rubric wired (`COS_PROACTIVE_PROMPT_BLOCK`) and synced to active CoS `SOUL.md` (legacy `anti-cos` path decommissioned).
   - P4: Gateway DOWN → alert-first standup (skips body sections per §4).
   - P5: Parses `ANTI_STATUS.md` + `HERMES_STATUS.md` into structured standup bullets.
   - Staged output: `evidence/cos_standup_latest.json` (§12 false-claims enforced).
   - Verified: `tests/test_cos_proactive.py` → **14/14 PASS**.
