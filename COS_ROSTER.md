# Agent model pins (specialty)

**Updated:** August 30, 2026 - 2:50 PM EDT
**Writer:** CoS. Anti applies this to live Buzz. CoS does not edit `managed-agents.json`.

Paid subs: Grok (xAI), Grok Bot (this CoS chat, not a Buzz model), Cursor (Buzz model per Leo), Gemini, ChatGPT/Codex.
OAuth only. Do not use leftover API-key slots.

## Pins
| Agent | Specialty | Pin | Status |
| Hermes | COO / hops | Codex `gpt-5.6-luna` | LIVE, proven wellington |
| Pollen | Market / SEO | xAI OAuth `grok-4.6` (not `grok-2-latest`) | OAuth signed in, 0 hops. Config still has stale grok-2 |
| Honey | Luxury copy | Gemini current flash (not `gemini-2.0-flash`) | Intended. Hermes Gemini is still an API-key slot. Do not burn that key. Park on Codex until Gemini OAuth |
| Fizz | Builder / tech | Cursor (Buzz model) | Intended. Not present in saved Buzz JSON. Park on Codex `gpt-5.6-luna` until Cursor provider exists. Kill `gpt-4o` / openai-compat |
| Atlas | In-room ops | Do not pin as CoS. This Grok Bot seat is CoS. Rename first, then Grok `grok-4.6` | Model empty today. Duplicate entries in roster |
| Aura | Personal / vault | Local `qwen3.5:9b` | Never Codex. Never wellington |

## Also
- Roster has 12 rows / 6 dupes. Dedupe on apply.
- Grok Bot stays panel CoS. Not a Buzz agent and not a Hermes model.
- HOLD. Practice `#wellington-canary` only.
- Prove one pin at a time: Pollen Grok first, then Honey Gemini, then Fizz Cursor.

## FOR ANTI
1. Do not clone CoS or Grok Bot into Buzz.
2. Dedupe `managed-agents.json`.
3. Hermes stays `gpt-5.6-luna` / Codex.
4. Pollen: provider `xai-oauth`, model `grok-4.6`.
5. Fizz: remove `gpt-4o` openai-compat. Codex until Cursor provider is visible in Buzz.
6. Honey: do not keep `gemini-2.0-flash`. Codex park until Gemini OAuth.
7. Aura: local Qwen only.
8. Restart Hermes at the desk, then Leo runs one wellington Hermes-to-Pollen hop. CoS log-verifies.
