# BUZZ & ALIEN AGENTS ARCHITECTURE HANDOFF

**Last Updated:** August 30, 2026 — 1:48 PM EDT  
**Current Milestone:** Production Promotion Live (6 Supervisors Active on Promoted Binary — HOLD Maintained)

---

## 1. Verified Production Live State (Confirmed via Review)
* **Desktop App:** PID `37196` (`buzz-desktop.exe`) active on screen.
* **Production Binary Path:** `C:\Users\leope\AppData\Local\Buzz\buzz-acp.exe`
  - **Promoted SHA256:** `9AA289DFF0AE6D47255688AE6968DEC801D577232BC6BA9A912DE620DDF59AC4`
* **Preflight Backup Intact:** `C:\Users\leope\AppData\Local\Buzz\buzz-acp.exe.bak-95CDAAD0-20260829`
  - **Backup SHA256:** `95CDAAD04FAD8B2CAB1DF2BEA4D779B9C3963DAAB76DE57E78BF118DEA431D8C`
* **Live Supervisors:**
  - Exactly **6 production supervisor processes** (`buzz-acp.exe`) running the promoted binary:
    - PIDs: `16388`, `24076`, `28648`, `36292`, `39876`, `40020` (all started ~6:19 PM).
* **Instant Rollback Command:**
  ```powershell
  Get-Process | Where-Object { $_.Path -like "*AppData\Local\Buzz\buzz-acp.exe*" } | Stop-Process -Force
  Copy-Item "C:\Users\leope\AppData\Local\Buzz\buzz-acp.exe.bak-95CDAAD0-20260829" -Destination "C:\Users\leope\AppData\Local\Buzz\buzz-acp.exe" -Force
  (Get-FileHash "C:\Users\leope\AppData\Local\Buzz\buzz-acp.exe").Hash
  ```

---

## 2. Canary & Practice Pass Records

### A) 6:03 PM Canary Pass (2026-08-29 in `#Welcome`)
* **Delegation Event ID:** `7a24d14fd88c0f619fbc55dc52c5eb8c2beaab7615ec36a7272cc04b721ba3ba` (published in 0.29s).
  - *Wire Tag Status:* The `["buzz", "managed_agent_delegation"]` marker and Pollen's one-shot return `p`-tag were inferred from the supervisor dispatch path and were NOT dumped off the wire.
* **Return Hop & Execution:** Pollen returned 3 keywords $\rightarrow$ Hermes second turn reported args sent + summarized keywords to Leo.
* **Loop Status:** No loop observed on this single test run.

### B) Practice Pass (2026-08-30 in `#wellington-canary`)
* **Record:** 2026-08-30 1:43 PM EDT `#wellington-canary` Hermes 0.20.6 hop PASS, event `498b148384a8e9abd96cf46a9fa1bfa90e0898aa9a1d06c16d4264a04acdbb40`, ACK 0.19s, Pollen answered, no loop.
* **Scope:** Practice pass, not a HOLD lift, not a prod ship.

---

## 3. Strict Operational Governance
* **HOLD Authority:** Only **Leo Peralta** can authorize lifting the HOLD. Advisors review; they do not clear or lift holds.
* **Current Status:** Strict **HOLD** remains fully active on `#Alienware-hq`.
* **Proposals Only:** Any future parallel delegations or new delegation patterns remain unapproved proposals until Leo explicitly clears them.

---

## 4. Wire / Dispatch Log Extracts

### A) 6:03 PM Canary Pass (Binary `9AA289DF...`)
- **Event ID:** `7a24d14fd88c0f619fbc55dc52c5eb8c2beaab7615ec36a7272cc04b721ba3ba`
- **Created At / Timestamp:** `2026-08-29T22:03:25.842432Z` (Local: `2026-08-29 18:03:25`)
- **Pubkey Prefix:**
  - Sender (Hermes): `16dac8fc...`
  - Target (Pollen): `2f718879...`
- **Tags (as logged in supervisor dispatch):**
  - Channel: `16339f2f-3ffa-4700-80b8-13c9210d743f`
  - Recipient `p`-tag: `2f7188798fe95455d8375b3f54fe777e2cade67c3ff9694aaaea4a82b8c7b507`
  - Marker Tag `["buzz", "managed_agent_delegation"]`: Inferred from supervisor dispatch path (raw wire envelope not dumped separately).
- **Log File Path:** `C:\Users\leope\AppData\Roaming\xyz.block.buzz.app\agents\logs\16dac8fc4fbbc6d0c42eaec2fd46e77af1f86ac6268e31d8da7a4d372095a314__e48b6574f7019fdf5cae5b111df54828ee3b306a3260394673fbc95c8aa94add.log`
- **PID:** Not named on the supervisor dispatch log line (supervisor PID was `7092` at 6:03 PM).

---

### B) PRE-PROMOTE / Different Binary: 5:17 PM outbound hop (event b6962bfe...)
- **Event ID:** `b6962bfeb52dd427c21c4ea923736dc6294e2a4856a86af420cfb80cba802423`
- **Created At / Timestamp:** `2026-08-29T21:17:08.378187Z` (Local: `2026-08-29 17:17:08`)
- **Pubkey Prefix:**
  - Sender (Hermes): `16dac8fc...`
  - Target (Pollen): `2f718879...`
- **Tags (as logged in supervisor dispatch):**
  - Channel: `16339f2f-3ffa-4700-80b8-13c9210d743f`
  - Target `p`-tag: `2f7188798fe95455d8375b3f54fe777e2cade67c3ff9694aaaea4a82b8c7b507`
- **Log File Path:** `C:\Users\leope\AppData\Roaming\xyz.block.buzz.app\agents\logs\16dac8fc4fbbc6d0c42eaec2fd46e77af1f86ac6268e31d8da7a4d372095a314__e48b6574f7019fdf5cae5b111df54828ee3b306a3260394673fbc95c8aa94add.log`
- **PID:** Not named on supervisor log line.
