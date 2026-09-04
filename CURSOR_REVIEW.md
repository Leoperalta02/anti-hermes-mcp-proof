# Cursor Review: Hermes Onboarding Wiring Stack (W1–W5)

## Audit verdict: **PASS** (W5) · Stack **STAGED PASS** (W1–W5) — commit `536e193`

Audited `536e193` on `github/main`. W5 implementation is solid; the full onboarding chain still needs live operator gates.

### W5 (`536e193`) — verified

| Area | Result |
| --- | --- |
| **Spec** | `DELEGATION_SANDBOX_SPEC.md` — `#rosie-onboarding-sandbox`, `#wellington-canary`; HOLD on `#Alienware-hq`; `#panel-advisors` blocked |
| **Dispatcher** | `delegation_sandbox.py` — fail-closed channels, input validation, 4 specialists |
| **Draft posture** | `DRAFT_PENDING_REALTOR_APPROVAL`, `external_send_blocked: true`, `send_gate: LEO_AND_REALTOR_APPROVAL_REQUIRED` |
| **§12 claims** | All `claims.*` explicitly `false` |
| **§9 mock orchestration** | `run_mock_delegation()` — Harbor + Keystone + Quill → `PASS` |
| **Tests** | **9/9 PASS** (now **10/10 PASS** with queue accumulation) |
| **Secrets** | None in commit (4 files only) |

### Hermes wiring stack (W1–W5)

| SOP | Tests (Alienware Local) | Verdict |
| --- | --- | --- |
| W1 Brief watcher + POST hook | 6/6 | STAGED PASS |
| W2 Telegram alert template | (in W1) | STAGED PASS |
| W3 CoS triage evaluator | 8/8 | PASS |
| W4 Tenant skeleton manager | 6/6 | PASS |
| W5 Delegation sandbox | 10/10 | PASS |

Hermes modules combined: **30/30 PASS**.

Full repo on Alienware local: **67/67 PASS** (portable imports runnable in any environment).

### Why stack is STAGED PASS (not full PASS)

1. **Live Telegram** — Alerts still staged to JSON; Hermes must dispatch to Leo.
2. **`send_managed_agent`** — Spec references tool lockdown; `delegation_sandbox.py` is a parallel Python dispatcher, not wired into the live Hermes tool path.
3. **§9 full chain** — `run_mock_delegation()` covers steps 5–6 in isolation; Leo `APPROVE PROVISION DRYRUN` → specialist drafts → status log still needs operator sign-off.

### Non-blocking notes addressed

- Harbor queue now accumulates entries as a list in `follow_up_queue.json` across multiple dispatches.
- Default tenant root is Alienware path; tests correctly use isolated temp directories.

### Operator gates progression

1. [x] **Leo §9 dry-run approval**: Leo sent **`all provisions are approved`** (and prior `APPROVED PROVISION DRYRUN`); mock delegation passes clean with zero external sends.
2. [x] **Wire `send_managed_agent` sandbox channel guard**: Live tool `managed_agent_tool.py` updated with HOLD check on `#Alienware-hq` and specialist isolation guard (`[STOP — SANDBOX VIOLATION]`). Unit tests: 7/7 PASS (`test_mention_tool.py`).
3. [ ] **A4 72h gateway watch**: 12h+ clean, ongoing supervision.
4. [ ] **`APPROVE PROVISION` for first real realtor**: Pending live onboarding trigger.

Full repo on Alienware local: **67/67 PASS**.
Audit updated and tracked by Anti IDE.
