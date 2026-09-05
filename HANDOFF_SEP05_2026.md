# Apex Luxury AI — Handoff Document (Sep 05, 2026)

**Last Updated:** September 5, 2026 — 12:01 PM EDT  
**Status:** Ready for Live Client Onboarding Test

---

## 1. What Was Just Completed & Verified
1. **Direct Camera Roll & Device Video Dropzone (`#listings`)**:
   - Liquid glass dropzone in the private portal (`public_sites/rosie/portal.html#listings`).
   - Drag-and-drop & file picker (`image/*`) for direct photo uploads with automatic `★ COVER` photo badge and instant delete controls.
   - Direct video file upload (`video/*`) and virtual tour embed (YouTube, Vimeo, Matterport 3D).
   - Multi-photo gallery thumbnail strip and cinematic video player in the Front Door estate modal (`public_sites/rosie/index.html`).
   - Upload backend endpoint `POST /api/listing/upload` storing media in `public_sites/{tenant}/assets/uploads/`.
2. **Linter & Accessibility Clean Sweep**:
   - Resolved all 41 Edge Tools / axe linter errors/warnings in `index.html`.
   - Added semantic `<label for="...">`, `title`, and `aria-label` tags across all forms.
   - Enforced `-webkit-` CSS vendor prefix ordering.
   - Added workspace configuration in `.vscode/settings.json` and `.hintrc`.
3. **Verification**:
   - `python -m unittest tests/test_listing_intake.py`: 7/7 PASS.
   - `pytest tests/test_lead_flow.py`: 6/6 PASS.
   - All commits clean on `main` branch.

---

## 2. Active Local Infrastructure (Running in Background)
- **Port 8000**: Web Preview Server (`python apex_core/dev_launcher.py`)
  - Front Door: `http://127.0.0.1:8000/public_sites/rosie/index.html`
  - Sovereign Portal: `http://127.0.0.1:8000/public_sites/rosie/portal.html`
  - Onboarding Landing Page: `http://127.0.0.1:8000/landing_page/index.html`
- **Port 8765**: Listing Intake & Auto-Fetch Server (`listing_intake_server.py`)
- **Port 8787**: Brief Receiver (`brief_receiver.py`)

---

## 3. The Next Immediate Step (For the Fresh Chat)
**Goal:** Run the very first realistic onboarding test with Leo as the client.

**Workflow:**
1. Leo opens [http://127.0.0.1:8000/landing_page/index.html](http://127.0.0.1:8000/landing_page/index.html) and submits the discovery brief.
2. The brief lands in `brief_receiver.py` (Port 8787).
3. **Hermes** acts as the Real Estate AI Architect within our Apex platform (strictly in-project, no Buzz):
   - Reviews the brief and extracts Leo's luxury market parameters.
   - Automatically provisions Leo's customized luxury site (`public_sites/leo/index.html` and `portal.html`).
   - Delivers Leo's personalized VIP onboarding action plan and portal launch.
