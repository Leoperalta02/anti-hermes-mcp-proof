# Rosie Real Estate CoPilot — Onboarding SOP

**Version:** 1.0 (approved)  
**Author:** @cursor (Deep Code Auditor) — Anti wires after Phase A engine green  
**Date:** September 4, 2026  
**Status:** APPROVED by Leo — Anti wires W1–W5 after Phase A A4 green  

---

## 1. Purpose

Define the **exact process** from first realtor discovery brief → staged intake → Leo approval → Rosie tenant provision → first deliverables — with **no silent auto-deploy**, **no false claims**, and **HOLD intact** on production surfaces until Leo lifts.

This SOP replaces ad-hoc handoffs. Hermes executes it; Anti wires infrastructure; Cursor audits; Leo approves gates.

---

## 2. Scope & boundaries

### In scope
- Apex landing page discovery form (`landing_page/index.html`)
- Local staged brief receiver (`landing_page/brief_receiver.py` → `onboarding-briefs/`)
- Hermes CoS triage and Leo approval
- Rosie profile (`hermes-state/profiles/real-estate-copilot/SOUL.md`)
- Tenant team roles: **Harbor** (CRM/follow-up), **Keystone** (CMA/transactions), **Quill** (copy/marketing)
- Internal Hermes subagent delegation (Buzz/Nostr relay **retired**)
- Dry-run mock lead before first real client

### Out of scope (until Leo explicitly approves)
- Public HTTPS host / `*.apexluxuryai.com` portal
- MLS / IDX / ShowingTime / CRM OAuth connections
- Live Vapi voice lines (`apex_core/vapi_bilingual_pipeline.py` — prompts ready, webhooks HOLD)
- Auto-send to clients without Leo/realtor approval
- `#Alienware-hq` production hops

---

## 3. Prerequisites (Phase A — Anti)

Do **not** start Rosie onboarding wiring until all pass:

| Gate | Owner | Pass criteria |
|------|-------|---------------|
| A1 | Anti | Gateway supervised daemon survives reboot; single PID |
| A2 | Anti | Desktop `Hermes.exe` loads session; `:9119` reachable |
| A3 | Anti | SQLite lease guardian deployed; no stale lease >24h |
| A4 | Anti | 72h clean gateway log (no `UNCLEANLY exited`) |
| A5 | Anti | Telegram DM + optional group relay working |

Cursor drafts this SOP during Phase A. Anti wires after A4.

---

## 4. Actors & authority

| Actor | Role in onboarding |
|-------|-------------------|
| **Leo** | Sole authority to approve provision, public host, voice, first real client |
| **Hermes** | CoS — triages briefs, assigns work, surfaces blockers, never auto-provisions |
| **Anti** | Infrastructure — receiver, alerts, cron, profiles, gateway |
| **Cursor** | Audits SOP compliance, prompt/schema review, static verification |
| **Rosie** | Realtor-facing copilot persona (post-provision) |
| **Harbor / Keystone / Quill** | Tenant specialists — drafts only until realtor approves send |

---

## 5. End-to-end flow (target state)

```text
[Realtor] → Discovery form (landing_page)
         → POST brief_receiver (:8787 loopback OR approved public proxy)
         → onboarding-briefs/{timestamp}-{slug}.json + .md
         → Hermes alert (Telegram + log)
         → Hermes triage checklist (§6)
         → Leo APPROVE / DEFER / REJECT
         → [If APPROVE] Anti provisions tenant skeleton (local/staged)
         → Hermes delegates draft tasks (§8)
         → Leo + realtor review drafts
         → [Future] voice / public portal (separate Leo gate)
```

---

## 6. Hermes triage checklist (on every new brief)

Within **15 minutes** of brief landing (cron or folder watch), Hermes must:

1. **Acknowledge** — log brief ID, name, brokerage, market (no PII in group chats beyond what Leo allows).
2. **Validate** — confirm:
   - No secrets in brief (receiver already rejects; double-check)
   - Required fields present: `full_name` OR explicit `profile_unknown`
   - At least one `needs[]` checkbox OR `needs_unknown`
3. **Classify** — tag brief:
   - `STAGE:DISCOVERY` — incomplete / unknown-heavy
   - `STAGE:READY` — enough to mock-provision
   - `STAGE:DEFER` — Leo asked to wait
4. **Surface to Leo** (Telegram or Desktop) with:
   - One-line summary
   - Recommended next action
   - Explicit blockers (if any)
   - **Never** claim agent deployed, portal live, or MLS connected
5. **Wait** — no provision until Leo replies `APPROVE PROVISION` or equivalent

---

## 7. Brief artifact spec

**Location:** `C:\LEO-LAB-ANTIGRAVITY\business-scope\onboarding-briefs\`

**Files created by receiver:**
- `{timestamp}-{slug}.json` — machine-readable
- `{timestamp}-{slug}.md` — human-readable

**Required JSON fields (from form):**
- `answers.full_name`, `answers.brokerage`, `answers.market`, `answers.email`
- `answers.needs[]` — intake, follow_up, appointments, copy, dates
- `status: "staged"` — immutable until Leo gate

**Hermes must append** (after triage):
- `hermes_triage_at`, `hermes_stage`, `leo_decision`, `assigned_tenant_slug` (if approved)

---

## 8. Post-approval delegation (internal Hermes only)

After Leo approves provision, Hermes may delegate **draft** work only:

| Task type | Delegate | Output | Send gate |
|-----------|----------|--------|-----------|
| Follow-up queue setup | Harbor | Draft queue JSON / notes | Leo + realtor |
| CMA / consult packet | Keystone | Draft packet (comps TBD) | Leo + realtor |
| Listing / social copy | Quill | Draft copy in tenant folder | Leo + realtor |
| CoS coordination | Hermes | Status in daily standup | Leo |

**Rules:**
- Use `send_managed_agent` with **non-empty** `target_agent` and `content` (kwargs merge patch required)
- No client-facing send without explicit approver from brief (`approver` field)
- Sandbox channel only until Leo lifts HOLD on production client comms

---

## 9. Dry-run — mock lead (mandatory before first real client)

**Owner:** Anti executes; Cursor verifies; Leo signs PASS.

1. Submit form with test data:
   - Name: `DRYRUN Rosie Test`
   - Brokerage: `Apex Staging Brokerage`
   - Market: `Estero, FL`
   - Needs: intake + follow_up + copy
2. Confirm brief lands in `onboarding-briefs/`
3. Hermes triage fires within 15 min
4. Leo sends `APPROVE PROVISION DRYRUN` in Telegram
5. Hermes delegates one draft task each to Harbor, Keystone, Quill (sandbox)
6. Verify drafts exist; **no external send**
7. Log result in `HERMES_STATUS.md` + `ANTI_STATUS.md`

**PASS:** Full chain in <24h with zero false live claims.  
**FAIL:** Stop; fix blocker; re-run dry-run.

---

## 10. Anti wiring tasks (post Leo approval of this SOP)

| # | Task | Verification |
|---|------|--------------|
| W1 | Folder watch or cron: new `onboarding-briefs/*.json` → Hermes task | Test file triggers alert |
| W2 | Telegram alert template (no false claims) | Leo receives structured ping |
| W3 | Hermes triage prompt block in CoS profile | Mock brief → correct checklist |
| W4 | Tenant skeleton path under `hermes-state/profiles/real-estate-copilot/` | Directory + SOUL loaded |
| W5 | Internal delegation sandbox channel configured | Dry-run §9 passes |

---

## 11. Cursor audit tasks

| # | Task |
|---|------|
| C1 | Review `brief_receiver.py` — no credential acceptance, loopback default |
| C2 | Review Vapi pipeline — locked PIP strings if accident module reused |
| C3 | Sign off dry-run transcript |
| C4 | Update `CURSOR_HANDOFF_SEP03.md` when dry-run PASS |

---

## 12. False claims — never say these unless gate passed

- "Your agent is live"
- "Portal URL: https://…"
- "MLS / ShowingTime connected"
- "Voice line active"
- "Calendar synced"
- "Message sent to your client"

Approved language: **"Staged brief received"**, **"Draft ready for your review"**, **"Awaiting Leo approval"**.

---

## 13. HOLD & retirement notes

- `#Alienware-hq`: HOLD unchanged
- Buzz / Nostr relay: **retired** — internal Hermes delegation only
- Vapi production webhooks: HOLD until Leo separate gate

---

## 14. Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Executive | Leo Peralta | 2026-09-04 | **APPROVE SOPs** |
| Infrastructure | Anti | ______ | WIRED (pending Phase A + W1–W5) |
| Audit | Cursor | 2026-09-04 | DRAFT COMPLETE |

---

*Next: `COS_PROACTIVE_SOP.md` — how Hermes drives this forward without passive echo replies.*
