# Handoff: Anti-Hermes Group Chat & System Status

**Date:** September 3, 2026 - 11:10 AM EDT  
**Operator:** Leo  
**Lead Assistant:** Antigravity (Anti)  

---

## 1. Executive Summary & Root Cause Resolved

- **Issue with Hermes:** Hermes encountered an unhandled API error (`Gemini HTTP 404: models/gemini-2.0-flash is no longer available`). When failing over from local Ollama/Qwen, Hermes fell back to the old deprecated `gemini-2.0-flash` endpoint listed under `fallback_providers` in `C:\LEO-LAB-ANTIGRAVITY\hermes-state\config.yaml`.
- **The Fix:** Updated `fallback_providers` to `gemini-3.6-flash`. Fallbacks now resolve cleanly without throwing 404 exceptions.
- **Group Chat State:** The 3-way room ("Anti Cos, Cursor Coding Agent, Hermes") has settled into stable `(pass)` cycles with no pending deadlocks.
- **Cursor Performance:** Switched to low-reasoning `gpt-5.3-codex-low-fast`, eliminating the high-latency stall.
- **Console Window Glitch:** Permanently resolved via `windowsHide: true` in `cursor-agent-api-proxy`.
- **Buzz State:** Strict HOLD remains active. No changes to Buzz production tables or executables.

---

## 2. Model Baseline Matrix & Fallback Hierarchy

### Default Local Primary (Zero Cost)
- **Primary:** `qwen2.5:7b` (Ollama local, 32k context, fast low latency)
- **Alternatives Tested & Verified Healthy:**
  - `qwen3.5:9b` (Ollama local, 262k context, vision + tools)
  - `llama3.1:8b-instruct-q4_K_M` (Ollama local, 131k context)
  - `qwen3.8:latest` (27B Q4, 262k context, heavy local reasoning)

### Tiered Fallback Cascade in `config.yaml` (Least Expensive / Lowest Latency First)
1. **Tier 1 (Ultra-Low Cost & Fast):** `gemini` → `gemini-flash-lite-latest`
2. **Tier 2 (Standard High-Speed Cloud):** `gemini` → `gemini-3.6-flash`
3. **Tier 3 (Subscription Coding/Mini):** `openai-codex` → `gpt-5.4-mini`
4. **Tier 4 (Non-Reasoning Fast Advisory):** `xai-oauth` → `grok-4.20-0309-non-reasoning`

| Bot Seat / Slot | Provider | Model String | Reasoning Effort |
| :--- | :--- | :--- | :--- |
| **Hermes Primary** | `ollama` | `qwen3.5:9b` / `qwen2.5:7b` | `low` |
| **@cursor** | `cursor` proxy | `gpt-5.3-codex-low-fast` | `low` |
| **@anti-cos** | `xai-oauth` | `grok-composer-2.5-fast` | `low` |
| **Auxiliary Compression** | `gemini` | `gemini-3.6-flash` | `default (sub-second memory sync)` |
| **Fallback 1** | `gemini` | `gemini-flash-lite-latest` | `default` |
| **Fallback 2** | `gemini` | `gemini-3.6-flash` | `default` |
| **Fallback 3** | `openai-codex` | `gpt-5.4-mini` | `low` |
| **Fallback 4** | `xai-oauth` | `grok-4.20-0309-non-reasoning` | `none` |

---

## 3. UI Diagnostics & Code Fixed

- **`styles.css`:** Added `-webkit-backdrop-filter: blur(12px);` for Safari/iOS compatibility.
- **`accident_hq.html`:** Added standard `background-clip: text;` alongside `-webkit-background-clip: text;`.

---

## 4. Instructions for Next Conversation

1. Anti is connected via ACP MCP (`anti-hermes-mcp-proof` + `hermes-sandbox-adapter`).
2. Do not touch Buzz or remove HOLD on `#Alienware-hq`.
3. If Hermes UI shows high latency or stalled turns, check whether `cursor-agent-api-proxy` is listening on `127.0.0.1:4646`.

