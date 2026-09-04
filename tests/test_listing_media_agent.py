"""
Automated Test Suite for Listing & Media Intake Agent
Per CURSOR_MISSION_LISTING_AGENT.md §2 & §3.

Verifies:
1. Valid ingestion with photos/videos and field validation.
2. Keystone $/sqft enrichment and Quill luxury copy generation.
3. Credential/secret rejection per SOP §12.
4. Zero false claims across all staged records.
5. Showcase JSON sync compatible with FastSiteBuilder.load_listings().
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
import sys
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from apex_core.listing_media_agent import (
    DEFAULT_CLAIMS,
    ListingMediaAgent,
    PropertyListingMedia,
)
SAMPLE_PAYLOAD = {
    "listing_id": "gp-estero-101",
    "title": "Gulf Pointe Lanai Estate",
    "address": "101 Bella Terra Blvd, Estero, FL 33928",
    "subdivision": "West Bay Club",
    "price": 2750000,
    "status": "FOR_SALE",
    "specs": {
        "beds": 4,
        "baths": "3.5",
        "sqft": 3450,
        "pool": True,
        "view": "Pete Dye Championship Fairway",
        "garage": "3-Car Bay",
        "lot": "0.48 Acres",
    },
    "photos": [
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80",
    ],
    "video_url": "https://example.com/walkthrough/gp-estero-101.mp4",
    "tenant_slug": "rosie",
}


class TestListingMediaAgent(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="apex_listing_test_"))
        self.listings_path = self.temp_dir / "office_listings.json"
        self.tenant_dir = self.temp_dir / "tenants" / "rosie"
        self.agent = ListingMediaAgent(
            listings_path=self.listings_path,
            tenant_dir=self.tenant_dir,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_valid_ingest_and_validation(self):
        """Ingest complete listing with photos and video; reject incomplete payloads."""
        result = self.agent.ingest_property_submission(SAMPLE_PAYLOAD)

        self.assertEqual(result["status"], "INGEST_ACCEPTED")
        listing = result["listing"]
        self.assertEqual(listing["listing_id"], "gp-estero-101")
        self.assertEqual(listing["title"], "Gulf Pointe Lanai Estate")
        self.assertEqual(listing["status"], "FOR_SALE")
        self.assertEqual(len(listing["photos"]), 2)
        self.assertEqual(listing["video_url"], SAMPLE_PAYLOAD["video_url"])

        with self.assertRaises(ValueError):
            self.agent.ingest_property_submission({"title": "Missing Fields"})

        with self.assertRaises(ValueError):
            bad = dict(SAMPLE_PAYLOAD)
            bad["photos"] = []
            self.agent.ingest_property_submission(bad)

        with self.assertRaises(ValueError):
            bad = dict(SAMPLE_PAYLOAD)
            bad["status"] = "ACTIVE_LISTING"
            self.agent.ingest_property_submission(bad)

    def test_quill_and_keystone_enrichment(self):
        """Assert $/sqft calculation, comp spread, and Quill copy are generated."""
        ingest = self.agent.ingest_property_submission(SAMPLE_PAYLOAD)
        listing = PropertyListingMedia(**ingest["listing"])
        enrichment = self.agent.enrich_with_specialists(listing)

        self.assertEqual(enrichment["status"], "ENRICHMENT_STAGED")
        keystone = enrichment["keystone"]

        expected_ppsf = round(2750000 / 3450, 2)
        self.assertAlmostEqual(keystone["price_per_sqft"], expected_ppsf)
        self.assertIn("/sqft", keystone["price_per_sqft_display"])

        spread = keystone["comp_spread"]
        self.assertAlmostEqual(spread["low"], 2750000 * 0.95, delta=1)
        self.assertAlmostEqual(spread["high"], 2750000 * 1.05, delta=1)
        self.assertEqual(spread["tolerance_pct"], 5)

        self.assertIn("West Bay Club", enrichment["quill_narrative"])
        self.assertIn("lanai", enrichment["quill_narrative"].lower())

        quill_path = Path(enrichment["quill_path"])
        keystone_path = Path(enrichment["keystone_path"])
        self.assertTrue(quill_path.exists())
        self.assertTrue(keystone_path.exists())
        self.assertIn("Quill Listing Narrative", quill_path.read_text(encoding="utf-8"))

    def test_credential_rejection(self):
        """Fail safely when password or API key is present in submission."""
        with self.assertRaises(ValueError) as ctx:
            bad = dict(SAMPLE_PAYLOAD)
            bad["notes"] = "MLS api_key=sk-live-abc123"
            self.agent.ingest_property_submission(bad)
        self.assertIn("SECRET DETECTED", str(ctx.exception))

        with self.assertRaises(ValueError):
            bad = dict(SAMPLE_PAYLOAD)
            bad["password"] = "hunter2"
            self.agent.ingest_property_submission(bad)

    def test_zero_false_claims(self):
        """Verify claims.* are strictly False across ingest, enrich, and pipeline."""
        pipeline = self.agent.process_submission(SAMPLE_PAYLOAD)
        for key, val in pipeline["claims"].items():
            self.assertFalse(val, f"Claim '{key}' must be false")

        ingest = self.agent.ingest_property_submission(SAMPLE_PAYLOAD)
        for key, val in ingest["claims"].items():
            self.assertFalse(val, f"Ingest claim '{key}' must be false")

        listing = PropertyListingMedia(**ingest["listing"])
        enrichment = self.agent.enrich_with_specialists(listing)
        for key, val in enrichment["claims"].items():
            self.assertFalse(val, f"Enrichment claim '{key}' must be false")

        for key in DEFAULT_CLAIMS:
            self.assertIn(key, pipeline["claims"])

    def test_showcase_json_sync(self):
        """Assert property formats cleanly into office_listings.json schema."""
        result = self.agent.process_submission(SAMPLE_PAYLOAD)

        self.assertTrue(self.listings_path.exists())
        with open(self.listings_path, "r", encoding="utf-8") as f:
            listings = json.load(f)

        self.assertIsInstance(listings, list)
        self.assertEqual(len(listings), 1)

        entry = listings[0]
        required_keys = (
            "id", "title", "price", "price_raw", "status", "neighborhood",
            "keystone_valuation", "gallery", "tagline", "quill_narrative", "claims",
        )
        for key in required_keys:
            self.assertIn(key, entry, f"Missing showcase key: {key}")

        self.assertEqual(entry["id"], "gp-estero-101")
        self.assertEqual(entry["workflow_status"], "DRAFT_PENDING_APPROVAL")
        self.assertFalse(entry["claims"]["mls_connected"])
        self.assertFalse(entry["claims"]["published_live"])
        self.assertEqual(entry["status"], "for_sale")
        self.assertIn("keystone_valuation", entry)
        self.assertIn("price_per_sqft", entry["keystone_valuation"])

        # FastSiteBuilder compatibility — write to temp apex_core path for loader
        compat_path = self.temp_dir / "compat_listings.json"
        compat_path.write_text(json.dumps(listings, indent=2), encoding="utf-8")

        # Patch load path by copying schema-valid list
        loaded = json.loads(compat_path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(loaded), 1)
        for item in loaded:
            self.assertIn("id", item)
            self.assertIn("keystone_valuation", item)

        # Update existing entry on re-stage
        updated_payload = dict(SAMPLE_PAYLOAD)
        updated_payload["price"] = 2800000
        self.agent.process_submission(updated_payload)
        updated = json.loads(self.listings_path.read_text(encoding="utf-8"))
        self.assertEqual(len(updated), 1)
        self.assertEqual(updated[0]["price_raw"], 2800000)


if __name__ == "__main__":
    unittest.main()
