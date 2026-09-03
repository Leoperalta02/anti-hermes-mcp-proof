# Master Architecture: Cloud-First OAuth Subscription MSP Engine

---

## 1. Core Principle: Zero Per-Token API Billing via OAuth Subscriptions

Instead of paying variable per-token API fees or requiring local hardware on Day 1:
1. **Cloud-First Execution:** Top-tier cloud LLMs (Gemini Flash/Pro, xAI Grok, OpenAI Codex) handle agent reasoning.
2. **OAuth Subscription Authentication:** Authenticate cloud requests using high-tier subscription OAuth tokens stored in `vault_backup/`:
   - `google_oauth_token.json`: Google Workspace & Gemini OAuth token.
   - `xai_oauth_access_token`: xAI Grok Tier-3 OAuth token.
   - `openai_codex_access_token`: OpenAI Plus/Codex OAuth token.
3. **Zero Hardware Dependency at Launch:** Runs entirely on lightweight cloud VPS (`159.223.183.138`), eliminating Alienware hardware startup requirements.
4. **Hardware Upgrade Path:** Monthly client retainer profits are reinvested to purchase dedicated high-spec local GPU hardware for sensitive on-premise workloads.

---

## 2. Token Cost & Infrastructure Comparison

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│                              INFRASTRUCTURE STRATEGY                                  │
├──────────────────────────────────────────────────┬────────────────────────────────────┤
│ TRADITIONAL PER-TOKEN API BILLING (UNFAVORABLE)  │ OUR OAUTH SUBSCRIPTION ENGINE (BEST)│
├──────────────────────────────────────────────────┼────────────────────────────────────┤
│ • Variable costs scaling with message volume     │ • Flat-rate monthly subscription   │
│ • Unexpected $1,000+ monthly API invoices        │ • Zero per-token API billing       │
│ • Requires upfront hardware investment           │ • Pure Cloud VPS execution         │
└──────────────────────────────────────────────────┴────────────────────────────────────┘
```

---

## 3. Retainer Pricing & Profit Margin Structure

Since cloud execution costs are locked to flat-rate OAuth subscriptions:
- **Small Business Retainer:** $499 – $999 / month per client.
- **Enterprise Security Retainer:** $1,500 – $3,500 / month per client.
- **Gross Profit Margin:** **95%+** (No token usage bills, pure recurring monthly retainer profit).

---

## 4. Vault Attachment Matrix (`vault_backup/`)

| Asset File | Identity / Purpose | Auth Type |
| :--- | :--- | :--- |
| `google_oauth_token.json` | Gmail & Google Calendar Live APIs + Gemini | OAuth 2.0 |
| `vault_secrets.json` | xAI Grok & OpenAI Codex OAuth Tokens | OAuth Bearer Tokens |
| `SECURITY_MODEL.md` | Machine-Verified Security Provenance Banners | Tier 1 Scoped |
