# 📋 CURSOR PRO HANDOFF DOSSIER — LIVE SYSTEM STATE
**Date & Time:** September 3, 2026 — 12:40 PM EDT  
**Prepared By:** Anti IDE (Antigravity)  
**Recipient:** Cursor Pro (Coding Agent / Auditor)  
**Executive Authority:** Leo Peralta  
**Master Governance Rules:** [AGENTS.md](file:///c:/LEO-LAB-ANTIGRAVITY/anti-hermes-mcp-proof/AGENTS.md) & [BUZZ_HANDOFF.md](file:///c:/LEO-LAB-ANTIGRAVITY/anti-hermes-mcp-proof/BUZZ_HANDOFF.md)

---

## 🟢 1. Active MCP Connection Restored (Cursor ↔ Hermes)
Your Cursor MCP integration is now **100% active and connected** with green status indicators in Cursor Customize:
* **`anti-hermes-mcp-proof` (8 tools enabled):**
  - `get_status`, `get_assignment`, `submit_result`, `get_pending_escalations`, `resolve_escalation`, `get_workspace_sync_status`, `get_subscription_model_routes`, `call_subscription_model`
* **`hermes-sandbox-adapter` (4 tools enabled):**
  - `get_hermes_sandbox_status`, `list_hermes_sandbox_assignments`, `read_hermes_sandbox_assignment`, `stage_hermes_result`
* **Configuration Path:** Global Cursor config at `C:\Users\leope\.cursor\mcp.json` mapped to Hermes Python runtime (`hermes-agent\venv\Scripts\python.exe`).

---

## 🏛️ 2. Hermes Desktop & Runtime Posture
* **Hermes Primary Model:** `qwen3.5:9b` via Ollama local (with explicit `context_length: 64000` override and 300s timeout headroom configured in `config.yaml`).
* **The Hybrid Breakthrough (Offloaded Memory Compaction):**
  - Previously, Hermes froze the laptop's RTX 3070 GPU for 45–70s trying to summarize 240,000-token histories using local VRAM.
  - Anti offloaded `auxiliary.compression` directly to **`gemini:gemini-3.6-flash`**.
  - All background context compaction now runs in the cloud in **< 1.5 seconds**, keeping the local GPU 100% free and snappy for pure conversation and local code execution.
* **Tiered Cloud Fallback Cascade (Verified & Live Pinged on the Wire):**
  1. `gemini` → `gemini-flash-lite-latest` (Tested & live)
  2. `gemini` → `gemini-3.6-flash` (Tested & live)
  3. `openai-codex` → `gpt-5.4-mini` (Tested & live)
  4. `xai-oauth` → `grok-4.20-0309-non-reasoning` (Tested & live)
* **Sunset Endpoints Cleared:** Deprecated `gemini-2.0-flash` 404 endpoint completely purged.

---

## 🚨 3. Operational Governance & Strict Rules
1. **HOLD Posture on `#Alienware-hq`:** Strict HOLD remains active per Leo Peralta. Do NOT dispatch commands, messages, or unvetted scripts to live Alienware production supervisors.
2. **Single Writer Rule:** Anti IDE is the sole author of live Buzz infrastructure and core files (`BUZZ_HANDOFF.md`, production binaries). Cursor Pro operates as Deep Code Auditor, Reviewer, and Static Verifier.
3. **No Vault Leaks:** Secrets, API keys, OAuth tokens, and PII remain in the local vault. Never output raw keys.
4. **Proxy Route & Tiered Intelligence Escalation:**
   - **Tier 1 (Go-To Workhorse):** `composer-2.5` (Fast, most token/credit efficient, direct surgical edits).
   - **Tier 2 (Deep Reasoning Escalation):** `grok-4.6` (Native first-party xAI frontier reasoning).
   - **Tier 3 (Frontier Specialist):** `sonnet-4.5` / `opus-4.5` (Heavy multi-file refactoring).
   - All routed via `127.0.0.1:4646` with live daemon active.

## 🎯 4. Completed Milestones (Sep 3, 2026 - 1:06 PM EDT)
* **Bilingual Vapi Pipeline Audit — PASS & MERGED:**
  - Cursor Pro identified and patched:
    1. Dual EN/ES greetings & closers (eradicating the Spanish-only opener bug).
    2. Immutable Florida 14-Day PIP compliance constants (`PIP_DISCLAIMER_EN`, `PIP_DISCLAIMER_ES`).
    3. Mandatory `LANGUAGE_CONTEXT_RULE` preserving slots across mid-call EN↔ES switches.
  - Test Suite Updated: `tests/test_vapi_bilingual_pipeline.py` expanded with 2 new assertion tests.
  - **Verification Result:** `25/25 total workspace unit tests PASSing` in `0.010s`.
  - **HOLD Integrity:** Strict HOLD on `#Alienware-hq` remains 100% intact (zero external webhooks or live credentials used).

---

## 🎯 5. Cursor Pro Role in Fresh Session
* Use your newly connected MCP tools (`anti-hermes-mcp-proof` and `hermes-sandbox-adapter`) to inspect live state, retrieve assignments, and audit code.
* Assist Leo with code review, sandbox testing, and architecture planning without modifying locked configuration files.
