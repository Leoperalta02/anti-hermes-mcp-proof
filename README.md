# Rosy Real Estate AI Copilot — Product Blueprint & Architecture

## Overview
**Rosy Real Estate AI Copilot** is a clean, headless AI platform designed specifically to empower individual Realtors and real estate brokerages with autonomous valuation analysis, MLS listing description generation, and lead qualification workflows.

---

## Key Features

1. **Autonomous Property Valuation Engine (`rosy_agent.py`)**
   - Calculates comparative market valuations based on square footage, bedroom/bathroom count, and key upgrades (pools, new roofs, lake views, gated communities).
   - Generates multi-tiered pricing strategies (**Conservative**, **Market-Realistic**, **Premium**).

2. **Instant MLS Description Generator**
   - Produces high-converting public MLS listing descriptions ready for copy-pasting into MLS systems (Zillow, Realtor.com, Matrix).

3. **Lead Qualification Pipeline**
   - Automatically triages buyer and seller inquiries based on budget, purchase timeframe, and mortgage pre-approval status.

4. **Preserved Credentials & Vault Assets**
   - OAuth token configuration & vault secrets safely preserved in `vault_backup/`.
   - Real estate knowledge playbooks preserved in `evidence/real_estate_copilot_clean.md`.

---

## Directory Structure

```
c:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof\
├── rosy_core/
│   ├── rosy_agent.py          # Core valuation, MLS copy, & lead qualification logic
│   └── rosy_prompts.py        # System prompts & Rosy persona definitions
├── api/
│   └── realtor_api.py         # Headless FastAPI endpoints for Realtor websites/integrations
├── vault_backup/              # Preserved Google OAuth tokens & API credentials
├── evidence/                  # Preserved Real Estate research reports & prompts
└── legacy_archive/            # Archived old experimental code
```

---

## How to Run

### Run Core Engine Test
```bash
python rosy_core/rosy_agent.py
```

### Run FastAPI Service (Headless)
```bash
python api/realtor_api.py
```
API endpoints will be available at `http://127.0.0.1:8000/docs` (Swagger UI).
