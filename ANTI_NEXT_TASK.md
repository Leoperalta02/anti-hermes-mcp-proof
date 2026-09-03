# ANTI — NEXT TASK ONLY
From Leo via Grok, 29 Aug 2026, 3:48 PM EDT.
Cursor drafted. Atlas agreed. Grok corrected. Leo approved this version.

Same HOLD. Do not redesign. Do not touch production buzz-acp.exe. Do not retarget Atlas / Aura / Leo-private-hq.
Do not lift HOLD. Cursor / Grok / Atlas remain read-only.

Read `C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof\BUZZ_HANDOFF.md`

## Latest honest fail
3:38 PM, #Alienware-hq:

Relay exception communicating with supervisor for target : Missing or empty target_agent

Meaning:
- ext_method / supervisor path is live
- wire name is no longer the blocker
- send_managed_agent was invoked with target_agent=""

Rust already lowercases names. Live agent name is `Pollen`. Empty string was the fail, not `Pollen` vs `pollen`.

## Do this

1. In `hermes-agent/tools/managed_agent_tool.py`, refuse to call the supervisor if `target_agent` or `content` is missing/whitespace. Do not use `args.get(..., "")` as the only check.

2. Keep the JSON field name `target_agent`. That is what Rust expects. Do not also send `target` / `agent` / `name`.

3. Do not add a special-case Pollen map. Name resolve is already case-insensitive. Empty is the bug.

4. Tool description: `target_agent` is the managed agent's name (example: Pollen), required, never empty. Filling the tool arg is not a channel @mention. Do not hardcode this canary into the tool.

5. Restart Hermes only.

6. Retest in a throwaway channel, not Alienware-hq, with this prompt:

@Hermes Call send_managed_agent exactly once. Set target_agent to Pollen (tool argument only, not an @mention). Content: ask for exactly three luxury real-estate SEO keywords. Do not @-mention Pollen in the channel. Do not answer until the relay returns. Report the tool result or the exact relay error.

Pass: non-empty `target_agent` on the wire, relay returns Pollen's three keywords, Pollen was not @-mentioned by Leo.
Fail: empty `target_agent`, method-not-found, or Pollen posting only because it was @-mentioned.

7. Update BUZZ_HANDOFF.md with the exact JSON payload sent to `_buzz/send_managed_agent` (redact secrets), pass/fail, transcript. Stop. Do not lift HOLD.