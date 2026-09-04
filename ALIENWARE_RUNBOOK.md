# Alienware Terminal Runbook (Anti Dark Fallback)

**Prefer the unified CLI** (same commands on cloud or Alienware):

```powershell
python -m apex_core.apex_cli host      # am I on Alienware or cloud?
python -m apex_core.apex_cli status    # gates + posture
python -m apex_core.apex_cli dev       # start dev stack
python -m apex_core.apex_cli brief provision
python -m apex_core.apex_cli governance   # Alienware only
```

Run on the **Alienware host** in **PowerShell** from the repo root.

## 1. Pull latest

```powershell
cd C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof
git pull github main
```

## 2. Apply HQ HOLD lift to live Hermes tool

```powershell
python update_managed_agent_tool_governance.py
```

## 3. Set Telegram bot token (current session)

Replace with your real token from @BotFather:

```powershell
$env:APEX_TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
$env:APEX_TELEGRAM_LIVE = "1"
```

To persist for the gateway user, set them in the Hermes gateway startup script or System Environment Variables.

## 4. Run tests (optional sanity check)

```powershell
python -m unittest discover -s tests
```

Alienware should see ~100+ pass; cloud-only harness tests may error — that is expected.

## 5. Start local dev stack (preview + intake + brief receiver)

```powershell
python apex_core\dev_launcher.py
```

Then open:
- Portal: http://127.0.0.1:8000/public_sites/rosie/portal.html
- Listings tab: same URL with `#listings`
- On phone width: tap **☰ Menu** for mobile nav drawer

## 6. First live provision (when brief has APPROVE PROVISION)

Ensure the brief JSON under `business-scope\onboarding-briefs\` includes:

```json
"leo_decision": "APPROVE PROVISION",
"hermes_stage": "STAGE:READY"
```

Then:

```powershell
python apex_core\brief_watcher.py --provision-approved --dir C:\LEO-LAB-ANTIGRAVITY\business-scope\onboarding-briefs
```

## 7. Quick gate check

```powershell
python apex_core\operator_gates.py show
type evidence\leo_provision_approval.json
```

## 8. Gateway health (manual A4 check)

```powershell
hermes gateway status
```

Confirm PID is up (was **37056**) and Lease Guardian is running.

---

**§12 posture:** Gates open ≠ live claims. Portal/MLS/voice remain staged until verified.
