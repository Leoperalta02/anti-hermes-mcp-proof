# CURSOR HANDOFF & ACTIVE MISSION BRIEF
**Timestamp:** September 22, 2026 - 19:10 EDT  
**From:** Leo Peralta (Founder) & Anti (Antigravity IDE, Alienware HQ)  
**To:** Cursor, Primary Engineering Super Agent (HP Compute Node `MININT-VLESCGA` / `192.168.1.248`)

---

### Executive Directive from Leo:
> *"Have Cursor work so Anti can save credits. Perform everyday heavy builds, code audits, subagent supervision, and verification from This PC on HP Node."*

---

### 1. Active Infrastructure & Runtime Alignment (Ground Truth)
- **Primary Orchestrators:** Anti (HQ Antigravity IDE) & Cursor (HP Node Native CLI/IDE).
- **Sole Hermes Engine Host:** HP Compute Node (`MININT-VLESCGA`) runs `hermes serve` on port `9119`, accessible via Tailscale MagicDNS (`https://minint-vlescga.tailf79969.ts.net`).
- **Alienware HQ Surface:** Glass cockpit / UI only. Zero local backend engines.
- **FastMCP SSE Bridge:** Running on Alienware HQ at `http://100.67.249.106:8799/sse` (exposing `anti-hermes-mcp-proof` tools to HP Node).
- **Telegram Gateways:** Hosted strictly on HP Compute Node for `@AntiCosLeo_bot` and `@CursorCodeHQ_bot`.

---

### 2. Cursor Standing Directives & Responsibilities
1. **Take Over Heavy Execution:**
   - Execute all tests, terminal operations, linting, deep code refactors, and multi-file builds on HP Node.
   - Run subagents through their paces and keep Anti in high-level architectural oversight to conserve credit expenditure.
2. **Subagent Supervision & Durable Skill Building:**
   - When delegating to specialist subagents (Harbor, Keystone, Quill, Atelier, Mosaic, Scout, Rowan), audit their output against acceptance criteria.
   - If output contains placeholders, fake assertions, or fails tests, reject the deliverable and instruct the subagent to re-run and remediate until verified.
3. **Mandatory State Logging:**
   - Record every completed milestone or structural update as a 1-line timestamped receipt in `SYSTEM_STATE.md` immediately upon completion.

---

### 3. Immediate Work Queue & Focus Areas
1. **Verify Live Remote MCP Connectivity:**
   - Confirm Hermes Desktop on HP Node registers `anti-hermes-mcp-proof` (FastMCP SSE over `http://100.67.249.106:8799/sse`) with green status.
2. **Onboarding & Workforce Pipeline Maintenance:**
   - Supervise `sandbox/apex-workforce-sandbox` test suites.
   - Ensure `apex_core/onboarding_pipeline.py` and the listing intake receiver on port `8765` continue running cleanly.
3. **Carlos Mesa & Public Deliverables Audit:**
   - Maintain the frozen state on Carlos Mesa (`carlos-mesa-lightning-page`) and Rosie Rivera (`public_sites/rosie/`) platforms.
   - Keep all mock placeholders strictly barred per Rule 10.
4. **Provision Codex Super Agent (Failover Engineer Seat):**
   - Create profile `C:\LEO-LAB-ANTIGRAVITY\hermes-state\profiles\codex` on HP Node.
   - Configure `SOUL.md`: Identity as **Codex — Fallback Super Agent Engineer & Independent Validator**, paired with Anti (Lead Architect) and Cursor (Heavy Builder).
   - Configure `config.yaml`: Model `gpt-5.6-luna`, provider `openai-codex`, shared Codex OAuth auth, terminal cwd `C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof`.
   - Wire MCP: Register `anti-hermes-mcp-proof` via FastMCP SSE (`http://100.67.249.106:8799/sse`) and verify test handshake.
   - Verify ACP & Roster: Ensure `codex` is discoverable via `profiles.list` WS RPC so he appears seated in Hermes Desktop alongside Anti and Cursor.
   - Record 1-line completion receipt in `SYSTEM_STATE.md`.

---

### 11. Ground-Truth Runtime & Seated Profiles (Override of Legacy Directives)
- **Engine Process:** `serve_with_public_host.py` (PID 5900) listening on `127.0.0.1:9119`.
- **Tailscale Publishing:** Tailscale Serve publishes `https://minint-vlescga.tailf79969.ts.net/` directly to port 9119.
- **Anti IDE Bridge:** Active on `100.67.249.106:8799` (FastMCP SSE).
- **Telegram Gateways:**
  - Default Gateway (`@AntiCosLeo_bot`): PID 4472.
  - Cursor Gateway (`@CursorCodeHQ_bot`): PID 6736.
- **Seated Profiles on Disk:**
  `Anti`, `Atelier`, `Aura`, `Cursor`, `Harbor`, `Keystone`, `Mosaic`, `Quill`, `Rowan`, and `Scout`.
- **Seat & Runtime Alignment:**
  Hermes is strictly the runtime engine executing under the **Anti seat**. Cursor must disregard any older lines in legacy handoffs or historical notes that describe the seat as Hermes.

---

**Anti & Leo Status:** Anti is on standby in Antigravity IDE on HQ, conserving quota and paired with Leo. Cursor on HP has the floor!
