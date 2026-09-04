# Hermes Agent Operational Status

**Last Updated:** September 3, 2026 - 8:20 PM EDT  
**Status:** Operational (Detached Gateway Daemon PID 37056 + Lease Guardian Watchdog PID 32880)  
**Hold State:** STRICT HOLD on `#Alienware-hq` (Maintained)  

---

## Architecture & Fleet Baseline

| Agent / Component | Runtime & Model Route | Role & Status |
| --- | --- | --- |
| **Hermes Gateway** | Python 3.11 venv (`hermes-state`) | Daemon PID 37056, Telegram sticky IPv4 polling (`149.154.166.110`), Web Dashboard (`http://127.0.0.1:9119`) |
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
     - W3: `COS_TRIAGE_PROMPT_BLOCK` synced into `anti-cos/SOUL.md`.
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
   - `python -m unittest discover -s tests` → **68/68 PASS** (0 failures, 0 errors in 0.51s).
