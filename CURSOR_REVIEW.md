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
