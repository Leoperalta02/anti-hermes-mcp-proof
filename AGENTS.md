# Antigravity Session & Handoff Instructions for Anti IDE

**Last Updated:** August 30, 2026 - 2:40 PM EDT
**Redacted by CoS:** vault-grade secrets were removed from this file. Keys, tokens, nsec, and phones stay in the vault. Do not put them back here.

## Do not store in this file
- API keys, service-role keys, OAuth tokens, nsec, SSH keys
- Phone numbers
- Droplet passwords
- Anything from the vault or #Leo-private-hq

## Session rules
1. ALWAYS read `BUZZ_HANDOFF.md` first for live Buzz hashes, PIDs, HOLD, and hop records.
2. Anti is the sole writer of live Buzz state (`BUZZ_HANDOFF.md`, HQ, prod `buzz-acp.exe`).
3. HOLD remains on `#Alienware-hq` until Leo lifts it. Practice hops only in `#wellington-canary`.
4. Business hops: subscription OAuth (Codex / configured cloud). Do not put `ollama_num_ctx` on the Hermes Codex block. Aura/Qwen is local/personal only.
5. Next Hermes git pull must re-apply `hermes_adapter_0206.patch` (`buzz_ipc` + `get_acp_requester`). Do not hard-reset without restoring those.
6. Do not clone panel members as Buzz channel agents. Do not treat a Buzz avatar as a reviewer's position.
