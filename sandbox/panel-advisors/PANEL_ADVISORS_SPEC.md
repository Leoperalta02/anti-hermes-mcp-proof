# #panel-advisors — In-Channel Boardroom Pilot Spec
# Review status: GROK 2 APPROVE AS-IS — 2026-08-31 15:56 EDT
# Spec only. Not a HOLD lift. Not Round 1 authorization.
# Round 1 blocked until Leo explicitly authorizes in #panel-advisors.
# Tool lock (Hermes allowlist diff) is a separate Leo-accepted item before Round 1.

---

## §1. Seats & Routing

**Panel seats (pilot):**

| Seat | Role |
|---|---|
| Leo Peralta | Founder, Command Authority, sole decision-maker |
| Hermes | Coordinator only — restate, route, preserve positions, synthesize OPTIONS, mark DRAFT |
| Cursor Pro | Read-only commenter on text Leo pastes into #panel-advisors. No repo, no apply, no ticket. (Add for Round 1 on Leo's explicit command) |
| Grok 2 | Adversarial Reviewer — evaluates independently, not required to oppose. (Add for Round 1 on Leo's explicit command) |
| Atlas | Non-routable until Run 2 (separate Leo command) |

**Non-routable for this pilot (hard block):**
Fizz, Honey, Pollen, Aura, Orion, Anti, Grok Bot, Atlas (until Run 2).
If a non-routable name appears in routing context: ignore and log `[ROUTE REJECT]`.
Grok Bot is non-routable even if it comes online mid-round. Adding requires new Leo command after spec revision.

**Routable set = {Cursor Pro, Grok 2}** and ONLY IF:
- That exact string appears in Leo's command for that round, AND
- That identity is a current verified channel member.

If named seat is not a verified member: `[NO ROUTE]` — do not substitute, do not retry.

---

## §2. Hermes Boardroom Role (Locked)

Hermes in `#panel-advisors` is **strictly coordinator**:
- Restate Leo's question
- Route ONLY to participants Leo explicitly names in this round
- Preserve each seat's quoted position verbatim
- Cluster positions — may NOT rank, break ties, or invent a preferred option
- Include event_id on every Hermes dispatch record
- Post `DRAFT — OPTIONS FOR LEO` before stopping (never APPROVED / SHIP / CONSENSUS)
- If advisors disagree: list options. If they agree: still label DRAFT.
- No leading, judging, executing, or authorizing
- No seat may be added during an open round. Adding a seat requires a spec revision and a new Leo command after this round is closed.
- Only Hermes may emit @tags, and only for allowlisted named seats
- Advisors write seat names in plaintext only — quoted @tags are inert

---

## §3. Turn & Loop Controls

- **1 response per tagged seat per round** (≤ 8 lines each)
- **No advisor-to-advisor @tagging**
- **Round 2:** Authorized ONLY if Leo explicitly commands it
- **Timeout:** Wait T=10 minutes after dispatch, then finalize once.
  - Late replies are `[LATE — OUT OF ROUND]` and must NOT be merged.
  - All pilot output stays in `#panel-advisors`.
  - Posting pilot output to `#Alienware-hq` or any HQ surface is an HQ hop and is forbidden.
- **Panel Response Barrier (Mandatory Timing Control):**
  After routing a round to one or more advisory seats, Hermes must STOP generating the board synthesis until every requested seat has either:
  1. returned a valid response for the current `round_id`, or
  2. reached the configured timeout (T=10 minutes).
  A dispatch acknowledgment, successful `@mention`, or `awaiting response` state is NOT a completed seat response. Hermes must NEVER post `DRAFT — OPTIONS FOR LEO` in the same execution turn in which it dispatches a seat request unless that seat's matching response already exists in the round context. Responses from previous `round_id` values do not satisfy the barrier.
- **Late Arrival Consumption (Pre-Timeout):**
  If a seat response arrives after Hermes has posted `[AWAITING]` but before the T=10 minute timeout, Hermes must consume that response and produce the single allowed synthesis. It must NOT require Leo to start another round.
- **Idempotency:** One active `round_id` per channel. Duplicate Leo text or duplicate Hermes restatement with same `round_id` is ignored.



---

## §4. Tool Allowlist (Hard — Not Prompt-Only)

**Round 1 tool allowlist is empty for every tagged seat except Hermes.**

**Hermes allowlist:**
- Post in `#panel-advisors`
- Read `#panel-advisors`
- Tool: `mention_agent_in_channel(target_agent, message)` — Supervisor-mediated structured in-channel @mention to Leo-named, membership-verified seats (`Grok 2`, `Cursor Pro`).

**Hermes routing rule:**
Hermes MAY NOT call `send_managed_agent` or `delegate_task` (hard blocked in `#panel-advisors`).
Routing is performed via `mention_agent_in_channel(target_agent, message)`, which causes the Buzz supervisor to attach the target seat's Nostr pubkey p-tag and publish the in-channel mention.
If a named seat is not allowlisted or non-routable: post `[ROUTE REJECT]` and stop.

Do not hop around the channel.

**Hermes DENY (all other tools):**
Files, shell, tickets, webhooks, vault, other channels, any tool not on allowlist → post `[STOP — TOOL DENY]`, escalate to Leo.

**No ticket is created from `#panel-advisors`.** Anti tickets exist only if Leo opens them in HQ after the DRAFT.

---

## §5. Event ID & Traceability

`event_id` is required on Hermes dispatches only.
Advisor replies are recorded with bound agent ID + transport message ID.
Missing advisor transport ID → quote the reply and tag `[TRACE GAP]`; do not STOP the round.
If Hermes dispatch `event_id` is missing: post `[STOP — NO EVENT ID]`, do not synthesize.

---

## §6. Identity & Membership Bind

Before dispatch: verify each named seat's bound agent ID is a current channel member.
On miss: `[NO ROUTE]` — do not substitute, do not retry.
Replies count ONLY from the bound agent ID. Seat names in plaintext without verified bound ID are ignored.

---

## §7. Dissent Policy

- Do NOT require dissent. Do NOT score PASS/FAIL on whether seats disagree.
- Preserve whatever each seat actually said, including agreement.
- Hermes lists every position. If advisors agree, that is the record — not a failure.

---

## §8. Stop → Escalate to Leo

Immediately stop and escalate when:
- HOLD lift, HQ hop, prod/vault/binary/config changes requested
- Missing `event_id` on any dispatch
- Tool outside allowlist is invoked or attempted
- Non-routable name is presented as a target
- Impersonation attempt
- Spend, billing, credentials
- Loops or duplicate dispatch

Note: Timeout is NOT a STOP. At T=10, mark missing seats `[NO RESPONSE]`, finalize the partial DRAFT once, and do not dispatch again.

---

## §9. Output Format (Hermes Returns)

1. `round_id`
2. Question (Leo's exact words)
3. Participating seats (bound IDs confirmed)
4. Agent Positions (each seat's verbatim response)
5. Key Disagreements & Risks (listed, not resolved)
6. `DRAFT — OPTIONS FOR LEO` (never a ranked pick)
7. Action Requiring Leo Approval (if any)
8. IPC event IDs for all hops

---

## §10. Promotion Gate

A green Round 1 authorizes NOTHING outside `#panel-advisors`.
It does NOT lift `#Alienware-hq` HOLD, add seats, enable tools, or open Run 2.
Any HQ promotion remains a separate, explicit Leo-authorized decision.

---

## REVIEW STATUS

| Reviewer | Status |
|---|---|
| Atlas (ChatGPT) | Channel init PASS (3:40 PM EDT Aug 31) — NOT a tool lock |
| Grok 2 | **APPROVE AS-IS — 2026-08-31 15:56 EDT** — Spec only. Not a HOLD lift. Not Round 1 auth. Binds this text only. |
| Round 1 Gate | **BLOCKED — Leo must explicitly authorize in #panel-advisors after Hermes tool-allowlist diff is accepted** |

---

## GROK 2 FINDINGS RECORD (14 patches applied)

1. Header self-attestation → removed
2. §4.1 prompt-only lockdown → replaced with hard tool allowlist
3. §1 workforce names as implicit route targets → explicit non-routable block
4. §2/§6.4 recommended decision = judgment → DRAFT — OPTIONS FOR LEO only
5. §3 no timeout clock → T=10min + late arrival = OUT OF ROUND
6. Missing membership/identity bind → §6 added
7. event_id weasel language → mandatory on all dispatches or STOP
8. No idempotency → round_id added
9. Cursor as Code Auditor → read-only commenter on pasted text only
10. Anti ticket collision → no tickets from panel; Leo opens in HQ only
11. Dissent requirement vs Grok 2 adversarial role → dissent not required
12. @tags in quoted text → only Hermes emits @tags; advisors use plaintext
13. Grok Bot re-entry → non-routable for entire pilot even if online
14. NEXT FORK authority bleed → §10 promotion gate clarified
