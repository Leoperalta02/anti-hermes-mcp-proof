# CoS SOP - Buzz operating board

**Last Updated:** August 30, 2026 - 2:40 PM EDT
**Writer:** Chief of Staff. This is the operating SOP. `BUZZ_HANDOFF.md` stays Anti's live-state file. Do not merge them.

## 1. Authority
- **Leo:** production, credentials, spend, external comms, HOLD lift.
- **Anti (Antigravity IDE):** sole writer of live Buzz state: `BUZZ_HANDOFF.md`, `#Alienware-hq`, prod `buzz-acp.exe`.
- **CoS (Grok Bot):** oversee, nay, inventory, droplet SSH, lean janitor. Does not lift HOLD, swap prod exe, click Buzz, or send client messages.
- **Gemini (Antigravity 2.0):** panel. Not Anti. She/her.
- **Cursor:** sandbox implementer when Anti is away. Currently quit on Taxcore (RAM).
- **Codex / ChatGPT:** architecture review + implementation failover.
- **Aura:** Taxcore personal files on local Qwen. CoS does not join `#Leo-private-hq`.

## 2. Live Buzz (until the node)
- HOLD on `#Alienware-hq`.
- Only practice channel: `#wellington-canary`.
- Last pass: 2026-08-30 1:43 PM Hermes 0.20.6 `send_managed_agent` to Pollen, ACK 0.19s. Practice, not a ship.
- Prod hash unchanged: `9AA289DF...`
- Taxcore hosts Buzz desktop + 6 seats. Do not sleep Taxcore.
- Droplet (`ubuntu-s-1vcpu-1gb-nyc1`): `buzz-prod` relay/postgres/redis/minio + landing on :80. Idle Keycloak stack parked. Compose leftovers in `/opt/parked-compose`.
- Taxcore has no cloudflared. Relay is the droplet.

## 3. Secrets
Never in `BUZZ_HANDOFF.md`, `AGENTS.md`, panel docs, this SOP, or chat. If a lab markdown grows keys or phones, CoS redacts it.

## 4. Phone / away
- No HQ hop. No prod exe swap. No vault paste.
- CoS may read logs, SSH the droplet, park items Leo already named.
- Hermes toggle / canary hop waits for the desk.

## 5. Lean
- Weekday 8am CoS check. Ping only if fat.
- No auto-kill without a named PARK list.
- 6 `buzz-acp` + 24 `hermes-acp` are the live seats, not leftovers.
- Panel apps are KEEP while working. Cursor was parked 8/30 for RAM.

## 6. Hermes adapter
On any git pull or hard reset of `hermes-agent`, restore `hermes_adapter_0206.patch` plus `get_acp_requester`. Keep stash `hermes-adapter-v0.20.6-buzz-ipc-snapshot`. Do not drop stash@{1}.

## 7. Node (Miami, this week)
Wipe seller Windows first. No Buzz/vault login on that disk. Then fresh Buzz + Hermes 0.20.6 + adapter, one wellington prove, then tunnel. Taxcore keeps Qwen/Aura/vault/Anti. Droplet stays relay + landing. HOLD until Leo lifts it.

## 8. Not approved
- HQ hop / HOLD lift
- Parallel Hermes delegation
- Cloning panel people as Buzz avatars
- Moving Hermes onto the 1GB droplet
- Calling a wellington pass "production promotion"
