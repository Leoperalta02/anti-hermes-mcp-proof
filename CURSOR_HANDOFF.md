# DISPATCH TO CURSOR (HP NODE) — CO-ENGINEERING WORKFORCE ACTIVATION
**Timestamp:** September 21, 2026 - 01:38 EDT  
**From:** Leo Peralta (Founder) & Anti (Antigravity IDE, Alienware HQ)  
**To:** Cursor, Primary Engineering Super Agent (HP Compute Node `MININT-VLESCGA` / `192.168.1.248`)

---

### Executive Directive from Leo:
> *"We need to get Cursor, Primary Engineering Super Agent more involved in everyday HQ work with his Super Agent Engineering skills so Anti Super Agent Supreme can get some credit expenditure relief."*

---

### 1. Active Division of Labor (The Anti & Cursor Super-Agent Tandem)

To optimize credit expenditure, eliminate token burn, and maximize engineering velocity, Leo has instituted the following operational split:

| Responsibility | Anti (Antigravity IDE @ HQ) | Cursor (Super Agent @ HP Node This PC) |
| :--- | :--- | :--- |
| **Primary Domain** | **Lead Architect, High-Level Orchestrator, Executive Pair** | **Heavy Builder, Test Execution, Code Auditing & Maintenance** |
| **Everyday Duties** | • Product architecture, system design & high-level plans<br>• Executive gate alignment with Leo<br>• Visual review (Mosaic GPU assets, frontends)<br>• MCP tool routing & governance oversight | • Heavy code writing, refactoring, and multi-file implementation<br>• Running full test suites (`pytest`, linters, build checks)<br>• Heavy background scrapers, workers & data ingestion (:8765, :8787)<br>• Routine audits, dependency maintenance, and bug fixing |
| **Credit Posture** | High-leverage, credit-efficient strategic turns | Unlimited / heavy autonomous building turns via native Cursor on HP Node |

---

### 2. Immediate Standing Workflow & Subagent Coaching Protocol

> **CRITICAL FOUNDER DIRECTIVE (Leo Peralta):**
> *"Hermes agents do the work. Cursor verifies, and if something is wrong, Cursor instructs and makes them fix it so they learn and create durable skills."*

1. **Anti Architecture Dispatches:**
   - Anti drafts architecture specs, high-level roadmaps, and accepts Leo's directives in HQ Antigravity IDE.
   - Anti writes task dispatches into `CURSOR_HANDOFF.md` or git commits on `main`.

2. **Hermes Subagents Do the Daily Labor:**
   - **Harbor** (CRM/follow-up routing)
   - **Keystone** (CMA/pricing analytics)
   - **Quill** (copywriting & dossiers)
   - **Atelier** (UI layouts & styling)
   - **Scout & Rowan** (intel gathering & business packets)
   - **Mosaic** (visual graphics & flyers on GPU)

3. **Cursor's Role: Supervisor, Auditor & Code Coach:**
   - Cursor does NOT manually redo the subagents' work.
   - Cursor audits their output against acceptance gates and tests.
   - If a subagent's output fails or has flaws, Cursor rejects the deliverable, writes specific remediation instructions, and makes the subagent re-run and fix it until it passes.
   - This builds durable operational skills in the Hermes agent team and eliminates human/super-agent babysitting.

4. **Anti Review & Executive Sign-Off:**
   - Anti pulls Cursor's verified code on HQ, validates live ports or UI with Leo, and logs final sign-offs in `SYSTEM_STATE.md`.

---

### 3. Current Active Task: Final Rosie & Onboarding Pipeline Verification

Leo has requested that the workforce verify and complete the **Rosie Rivera project** and the **Onboarding Pipeline**.
- **Rosie Platform Assets:**
  - Front Door: `public_sites/rosie/index.html` (Apple-grade luxury public landing page)
  - Back Door: `public_sites/rosie/portal.html` (Sovereign Realtor OS & PWA portal)
  - Onboarding SOP: `ROSIE_ONBOARDING_SOP.md`
  - Automated Pipeline: `apex_core/onboarding_pipeline.py` & `tests/test_onboarding_pipeline.py`
- **Assignment for Cursor on HP Node:**
  1. Pull `main`.
  2. Run `python -m unittest tests/test_onboarding_pipeline.py` and verify all 8 onboarding stages execute cleanly in <0.5s.
  3. Verify `public_sites/rosie/index.html` and `public_sites/rosie/portal.html` for any dead click handlers, missing assets, or placeholder text.
  4. Confirm the listing intake endpoint integration (`LISTING_INTAKE_API:8765`) matches the active HP Node port.
  5. Log the verification results in a concise receipt in `SYSTEM_STATE.md` and report completion.

---

### 5. Direct Engineering Order from Anti to Cursor (Autonomous Ops)

**Leo should not have to manually run gateway commands or type in Telegram. You are the Primary Engineering Super Agent on This PC (HP Node). Execute this directly in your terminal now:**

1. **Launch the HP Hermes Gateway Daemon:**
   Run in PowerShell on HP Node:
   ```powershell
   $env:HERMES_HOME = "C:\LEO-LAB-ANTIGRAVITY\hermes-state"
   Start-Process -NoNewWindow -FilePath "C:\LEO-LAB-ANTIGRAVITY\hermes-state\hermes-agent\venv\Scripts\hermes.exe" -ArgumentList "gateway", "run", "--replace", "--accept-hooks"
   ```

2. **Reset the 102k Bloated Session via Database:**
   Do not make Leo type `/new`. Run this Python command on HP Node to programmatically close the bloated session:
   ```powershell
   python -c "import sqlite3, time; con = sqlite3.connect('C:/LEO-LAB-ANTIGRAVITY/hermes-state/state.db'); con.execute('UPDATE sessions SET ended_at = ?, end_reason = ? WHERE source = ? AND ended_at IS NULL', (time.time(), 'SESSION_RESET_BY_CURSOR', 'telegram')); con.commit(); con.close(); print('TELEGRAM SESSION RESET')"
   ```

3. **Verify Gateway Process:**
   Verify `hermes` is running with `Get-Process python | Where-Object { $_.CommandLine -like '*gateway*' }` and log the PID to `SYSTEM_STATE.md`.

Cursor: Execute steps 1-3 autonomously right now, then confirm back here via git commit so Leo does not have to touch it!

