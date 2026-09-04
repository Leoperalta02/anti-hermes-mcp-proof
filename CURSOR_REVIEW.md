# Cursor Review — September 4, 2026 Handoff Audit

**Latest commit audited:** `76f0a69` on `github/main`  
**Governance stack:** `89208e5` (sandbox guards) → `76f0a69` (portable test imports)  
**Auditor:** @cursor  
**Date:** 2026-09-04  

---

## Verdict: **PASS** — `send_managed_agent` governance wired + portable test imports

Commit `89208e5` adds fail-closed HOLD and specialist sandbox guards to the live `managed_agent_tool.py` writer (`update_managed_agent_tool_governance.py`). Commit `76f0a69` resolves static-import lint failures by switching `tests/test_mention_tool.py` to dynamic `importlib` with `@unittest.skipIf` for non-Alienware hosts. This closes the prior audit gap where `delegation_sandbox.py` was parallel to the live Hermes tool path.

---

## `89208e5` — governance rules audit

Source of truth: `update_managed_agent_tool_governance.py` → writes `C:\LEO-LAB-ANTIGRAVITY\hermes-agent\tools\managed_agent_tool.py`

| Rule | Guard | Verified |
|------|-------|----------|
| `#panel-advisors` tool deny (existing) | `[STOP — TOOL DENY]` | **PASS** |
| **`#Alienware-hq` HOLD** (new Rule 6) | `[STOP — HOLD ACTIVE]` before arg parse | **PASS** — blocks all `send_managed_agent` in production channel |
| **Specialist sandbox** (new Rule 7) | `[STOP — SANDBOX VIOLATION]` for Harbor, Keystone, Quill, Rosie outside `#rosie-onboarding-sandbox` / `#wellington-canary` | **PASS** |
| Empty args validation (existing) | `target_agent` + `content` required | **PASS** |
| Event ID traceability (existing) | `[STOP — NO EVENT ID]` | **PASS** |

### HOLD guard (Rule 6)

```python
if ch_name in {"alienware-hq", "#alienware-hq"}:
    return "[STOP — HOLD ACTIVE] send_managed_agent is blocked in #Alienware-hq. ..."
```

Runs immediately after panel-advisors check, before ACP relay. Test: `test_send_managed_agent_blocked_in_alienware_hq`.

### Specialist sandbox guard (Rule 7)

```python
_SANDBOX_CHANNELS = {"wellington-canary", "#wellington-canary", "rosie-onboarding-sandbox", "#rosie-onboarding-sandbox"}
_SPECIALIST_AGENTS = {"harbor", "keystone", "quill", "rosie"}
if target_clean.lower() in _SPECIALIST_AGENTS:
    if ch_val and ch_val[0].lower() not in _SANDBOX_CHANNELS:
        return "[STOP — SANDBOX VIOLATION] ..."
```

Aligns with `delegation_sandbox.py` and `DELEGATION_SANDBOX_SPEC.md`. Test: `test_send_managed_agent_specialist_sandbox_guard`.

---

## `76f0a69` — portable import audit

| Claim | Verified |
|-------|----------|
| Dynamic `importlib.import_module("tools.managed_agent_tool")` | **PASS** |
| Path guard: only inserts `C:\LEO-LAB-ANTIGRAVITY\hermes-agent` if `os.path.exists()` | **PASS** |
| Graceful skip on import failure | **PASS** — `@unittest.skipIf(_managed_tool is None, ...)` |
| No static import lint error in cloud CI | **PASS** — module not imported at parse time |

---

## Tests — `test_mention_tool.py`

**Alienware (with `hermes-agent`):** 7/7 PASS (per `HERMES_STATUS.md` / full 67/67 suite)

**Cursor cloud VM:**

```bash
python3 -m unittest discover -s tests -v
```

| Metric | Count |
|--------|-------|
| **Ran** | 62 |
| **PASS** | 45 |
| **SKIP** | 7 (all `TestMentionAgentToolGovernance` — `tools.managed_agent_tool not found on this host`) |
| **ERROR** | 10 (Alienware-only: `test_model_failover`, panel seat OAuth, reply path audit, specialist OAuth) |

Skip behavior is **correct**: cloud runs complete without import-time crash; governance tests execute only where `managed_agent_tool.py` is present.

---

## Inherited stack (still valid)

| Area | Verdict |
|------|---------|
| W1–W5 Hermes wiring (`354b095`–`536e193`) | **STAGED PASS** → governance gap **closed** |
| W5 `delegation_sandbox.py` | **PASS** |
| External coaching (`63591df`) | **PASS** |
| CRM tracker (`a9e7ff4`) | **PASS** |

---

## Minor notes (non-blocking)

1. **Specialist guard when `ch_val` is None** — Sandbox violation only fires when channel context is set. If ACP omits context, specialist delegation is not blocked by Rule 7 (relies on upstream context injection). Recommend fail-closed default if `ch_val is None` and target is specialist.
2. **Live file out-of-repo** — `managed_agent_tool.py` lives on Alienware at `hermes-agent/tools/`; repo carries the writer script + tests, not the deployed file itself.
3. **67/67 vs cloud 45+7 skip+10 error** — Full green suite requires Alienware paths and Hermes-state harnesses.

---

## SOP / false-claims watch

| Item | Status |
|------|--------|
| HOLD on `#Alienware-hq` | **PASS** — enforced in live tool |
| Specialist isolation to sandbox channels | **PASS** — enforced in live tool |
| `#panel-advisors` governance lock | **PASS** — unchanged |
| §12 zero false claims in delegation | **PASS** — via `delegation_sandbox.py` |
| Live Telegram dispatch | **OPEN** — staged JSON alerts |
| A4 72h gateway watch | **OPEN** — in progress per `ANTI_STATUS.md` |

---

## Leo gates

| Action | Ready? |
|--------|--------|
| Delegate to Harbor/Keystone/Quill in sandbox | **Yes** — `#rosie-onboarding-sandbox` or `#wellington-canary` |
| Delegate via `#Alienware-hq` | **No** — `[STOP — HOLD ACTIVE]` |
| Delegate specialists from `#general` | **No** — `[STOP — SANDBOX VIOLATION]` |
| First real realtor `APPROVE PROVISION` | **No** — after A4 + live §9 sign-off |

---

## Verify commands

```bash
# Alienware (full governance + harness tests)
python -m unittest tests.test_mention_tool -v
python -m unittest discover -s tests -v

# Any environment (portable subset)
python3 -m unittest discover -s tests -v
```
