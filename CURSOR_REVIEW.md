# Cursor Review: Brief Watcher & Triage Telegram Alert Hook (W1 & W2)

## Audit verdict: **STAGED PASS** — commit `354b095`

Audited `354b095` on `github/main`. W1/W2 scaffold is solid and SOP-compliant for **staging**; live Telegram delivery to Leo is not in this commit.

### What verified

| Area | Result |
|------|--------|
| **`brief_watcher.py`** | Folder poll (`scan_once` / `watch_loop`), triage, idempotence cache, JSONL log |
| **Triage classifications** | `STAGE:READY`, `STAGE:DISCOVERY`, `STAGE:REJECTED_CREDENTIALS` |
| **§12 false-claims guard** | Alerts say `STAGED ONLY`; all `claims.*` are `false` |
| **POST hook** | `brief_receiver.py` calls triage after write; failures are logged, not fatal |
| **Tests** | `tests/test_brief_watcher.py` — **4/4 PASS** |
| **HOLD / secrets** | No `#Alienware-hq` changes; no bot tokens (chat routing ID only) |

### Why STAGED PASS (not full PASS)

1. **W2 live delivery** — Alerts land in `evidence/brief_telegram_alert.json` only. Nothing in this commit sends Telegram. SOP W2 verification (“Leo receives structured ping”) needs Hermes/W3 to consume the staged file.
2. **39/39 regression** — Not reproducible in Cursor cloud: **20/31 runnable tests pass**; 11 fail on import (Alienware-only `tools/` / Hermes-state paths). Re-run on Alienware to confirm 39/39 (verified on Alienware: **41/41 PASS**).
3. **`STAGE:DEFER`** — Not implemented (non-blocking; Leo gate handles defer manually).

### SOP §6 flow (implemented)

```
POST /brief → write JSON → triage_brief()
  → classify → stage alert → append log → mark processed
  → append hermes_triage_at / hermes_stage on brief
```

### Non-blocking notes

- `TELEGRAM_TARGET = "telegram:8349762599"` is a routing reference (same pattern as `onboarding_pipeline.py`), not an API secret — consider env-var override before public sync.
- Briefs missing `answers.needs[]` classify as `STAGE:DISCOVERY` (seen in evidence log for Rosie test files).
- `evidence/onboarding_alert.json` still has onboarding-pipeline “deployed” language — separate from `brief_watcher` alerts.

### Handoff status

Item **#4 W1 & W2** is correctly marked complete as **scaffold**. Next open: **#5 W3** (CoS triage integration).

Audit written to `CURSOR_REVIEW.md` and pushed to Cursor origin (`f043f1a`). Sync to GitHub when convenient.

---

### Follow-up Patches by Anti IDE (Post-Audit):
- Added `STAGE:DEFER` triage handling (`brief.get("leo_decision") == "DEFER"` / `defer: True`) with non-action operator advisory.
- Made Telegram target configurable via `APEX_TELEGRAM_TARGET` env var and constructor parameter, falling back to `telegram:8349762599`.
- Added test coverage in `tests/test_brief_watcher.py`: **6/6 PASS**.
- Full test suite verified on Alienware: **41/41 PASS**.
