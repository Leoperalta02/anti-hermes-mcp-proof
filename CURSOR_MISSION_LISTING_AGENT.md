# Cursor Mission: Listing & Media Intake Agent (`apex_core/listing_media_agent.py`)

**Role Division (effective Sep 04, 2026 — 7:24 PM UTC):**
- **Code Author:** Antigravity (Anti) — **local Alienware IDE only**; avoid cloud-agent runs to preserve credits
- **Auditor & Gatekeeper:** Cursor — cloud VM: diff review, `python -m unittest discover`, browser/showcase verification, `CURSOR_REVIEW.md` verdicts
- **Authority:** `ROSIE_ONBOARDING_SOP.md` §8 & §12, `ANTI_STATUS.md`

*Previous division (3:08 PM EDT): Cursor authored / Anti audited — reversed per Leo credit conservation.*

---

## 1. Context & Objective
Leo noted:
> *"also do we have the agent that handles listings, when the realtor sends pictures/videos of homes, sold, for sale etc etc and the nice home should apple style scroll more nice homes or actual listed homes... Rosies Brokerage is eXp Realty in a mentor team team leader Bradley Dohack (Gulf Pointe Properties in Estero FL)."*

You are building the **Listing & Media Intake Engine** (`apex_core/listing_media_agent.py`) and its test suite (`tests/test_listing_media_agent.py`).

---

## 2. Technical Specification

### A. Module: `apex_core/listing_media_agent.py`
Create a clean, typed Python module with:

1. **`PropertyListingMedia` Dataclass**:
   - `listing_id`: str (e.g. `gp-estero-101`)
   - `title`: str
   - `address`: str
   - `subdivision`: str (e.g. `Pelican Sound`, `West Bay Club`, `Shadow Wood`)
   - `price`: int or float
   - `status`: str (`FOR_SALE`, `UNDER_CONTRACT`, `RECORD_SOLD`)
   - `specs`: Dict[str, Any] (`beds`, `baths`, `sqft`, `pool`, `view`)
   - `photos`: List[str] (paths or URLs)
   - `video_url`: Optional[str]
   - `tenant_slug`: str (default `"rosie"`)
   - `submitted_at`: str (ISO UTC timestamp)

2. **`ListingMediaAgent` Class**:
   - `__init__(self, listings_path: Optional[Path] = None, tenant_dir: Optional[Path] = None)`
     - Default `listings_path` = `apex_core/office_listings.json`.
     - Default `tenant_dir` = `hermes-state/profiles/real-estate-copilot/tenants/rosie`.
   - `ingest_property_submission(self, payload: Dict[str, Any]) -> Dict[str, Any]`:
     - Validates required fields (title, address, price, status, photos/media).
     - Rejects any credentials/passwords per SOP §12 (`SECRET_RE`).
   - `enrich_with_specialists(self, listing: PropertyListingMedia) -> Dict[str, Any]`:
     - **Keystone Valuation Benchmark**: Calculates $/sqft and comp spread ($\pm 5\%$).
     - **Quill Luxury Copywriting**: Generates an Apple-style kinetic narrative highlighting Florida architectural lifestyle (lanai, pool, sunsets, golf, Gulf access).
     - Staged drafts land under `tenants/{tenant_slug}/quill/listings/{listing_id}.md` and `tenants/{tenant_slug}/keystone/valuation_{listing_id}.json`.
   - `stage_for_showcase(self, listing_data: Dict[str, Any]) -> Path`:
     - Merges into `office_listings.json` with `status: "DRAFT_PENDING_APPROVAL"` or updates active showcase.
     - Triggers `FastSiteBuilder.load_listings()` compatibility.
     - Strict SOP §12: Sets `claims.mls_connected = False` and `claims.published_live = False`.

### B. Test Suite: `tests/test_listing_media_agent.py`
Write thorough unittests covering:
1. `test_valid_ingest_and_validation`: Ingest complete listing with photos/videos.
2. `test_quill_and_keystone_enrichment`: Asserts $/sqft calculation and Quill copy generated.
3. `test_credential_rejection`: Fails safely if password/API key is present in submission.
4. `test_zero_false_claims`: Verifies `claims.*` are strictly `False`.
5. `test_showcase_json_sync`: Asserts property formats cleanly into `office_listings.json` schema.

---

## 3. Governance Guardrails (Mandatory)
- **HOLD Active on `#Alienware-hq`**: Do not remove or bypass.
- **Fail-Closed Sandbox**: Any multi-agent delegation must stay inside `#rosie-onboarding-sandbox` or `#wellington-canary`.
- **Zero False Claims**: All `claims.*` flags remain `false`.
- **Clean Run**: All tests must execute cleanly with `python -m unittest discover -s tests`.

---

## 4. When Complete
Push your commit to `github/main`. **Cursor** (Auditor) will inspect the diff, run tests, perform browser verification, and record the verdict in `CURSOR_REVIEW.md`. Anti does **not** re-audit unless Leo explicitly requests a host-only spot-check.
