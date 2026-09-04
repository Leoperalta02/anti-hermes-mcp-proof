# Cursor Review: Sovereign Realtor OS & Playbook Decoupling

## Audit verdict: **PASS** — commit `63591df`

Audited `63591df` on `github/main` (stack includes `e8d1df2` for the SOP §12 button rename). Working tree matches that commit; tests and portal JSON checks were run locally.

### What changed

| Area | Result |
|------|--------|
| **External playbook** | `apex_core/office_playbook.json` holds all 8 scripts with `menu_title`, `title`, `cat`, `html` |
| **Dynamic menu** | `_generate_portal_html()` loops playbook entries into `.script-item` buttons |
| **JSON injection** | `const scripts = {playbook_json_str}` via `json.dumps(playbook)` |
| **Python decoupling** | ~84 lines of inline script literals removed from `fast_site_builder.py` |
| **Single-writer** | Portal HTML remains a generated artifact from the builder only |
| **Log to Timeline** | Present in builder + all 4 portals (`e8d1df2`) |
| **HOLD / secrets** | HOLD documented; playbook is coaching copy only — no keys/tokens |

### Verification run

```bash
python3 -m unittest tests.test_lead_flow -v   # 4/4 PASS
```

Node.js JSON parse of `const scripts = {...}`: **4/4 portals clean** (rosie, vance, sofia, toki).

New test `test_external_coaching_playbook` asserts playbook load, required keys, dynamic buttons, and serialized scripts object.

### Handoff status

`HANDOFF_SEP04_2026.md` item **#3 External Coaching Injection** is correctly marked **[x] complete**. Next open item: **#4 Hermes Telegram Alert Hook (W1)**.

### Non-blocking notes

- Playbook `html` is injected via `innerHTML` — same trust model as before; treat JSON as trusted brokerage content.
- Script keys in `onclick` assume simple keys (current 8 are fine).

### Still open (unchanged)

A4 72h gateway watch · W1–W5 Hermes live wiring · live email/CRM OAuth · `APPROVE PROVISION` gate after A4 + W1–W5.
