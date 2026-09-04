"""
Tests for Listing Intake Server and Portal Integration
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

from apex_core.listing_intake_server import handle_request
from apex_core.listing_media_agent import DEFAULT_CLAIMS, ListingMediaAgent
from apex_core.fast_site_builder import FastSiteBuilder
from apex_core.tenant_manager import tenant_manager

SAMPLE_PAYLOAD = {
    "listing_id": "gp-intake-202",
    "title": "Pelican Sound Media Draft",
    "address": "202 Pelican Sound Dr, Estero, FL",
    "subdivision": "Pelican Sound",
    "price": 3895000,
    "status": "FOR_SALE",
    "specs": {"beds": 4, "baths": "4.5", "sqft": 4620, "pool": True, "view": "Gulf access"},
    "photos": ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800"],
    "tenant_slug": "rosie",
}


class TestListingIntake(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="apex_intake_test_"))
        self.listings_path = self.temp_dir / "office_listings.json"
        self.queue_path = self.temp_dir / "listing_intake_queue.json"
        self.tenant_dir = self.temp_dir / "tenants" / "rosie"
        self.agent = ListingMediaAgent(
            listings_path=self.listings_path,
            tenant_dir=self.tenant_dir,
            queue_path=self.queue_path,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_submit_via_handler_queues_entry(self):
        status, body = handle_request("POST", "/api/listing/submit", SAMPLE_PAYLOAD, agent=self.agent)
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "QUEUE_STAGED")
        self.assertFalse(self.listings_path.exists())

        status, body = handle_request("GET", "/api/listing/queue?tenant=rosie", agent=self.agent)
        self.assertEqual(status, 200)
        self.assertEqual(len(body["queue"]), 1)

    def test_approve_stages_showcase(self):
        handle_request("POST", "/api/listing/submit", SAMPLE_PAYLOAD, agent=self.agent)
        status, body = handle_request(
            "POST", "/api/listing/approve", {"listing_id": "gp-intake-202", "tenant_slug": "rosie"}, agent=self.agent
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "APPROVED_FOR_SHOWCASE")
        self.assertTrue(self.listings_path.exists())
        self.assertIn("rebuild", body)
        self.assertEqual(body["rebuild"]["status"], "SHOWCASE_REBUILT")
        self.assertFalse(body["rebuild"]["claims"]["published_live"])

        listings = json.loads(self.listings_path.read_text(encoding="utf-8"))
        self.assertEqual(listings[0]["id"], "gp-intake-202")
        self.assertFalse(listings[0]["claims"]["mls_connected"])
        self.assertFalse(listings[0]["claims"]["published_live"])

    def test_zero_false_claims_on_queue_and_approve(self):
        handle_request("POST", "/api/listing/submit", SAMPLE_PAYLOAD, agent=self.agent)
        _, submit_body = handle_request("GET", "/api/listing/queue", agent=self.agent)
        for key, val in submit_body["claims"].items():
            self.assertFalse(val)

        _, approve_body = handle_request(
            "POST", "/api/listing/approve", {"listing_id": "gp-intake-202"}, agent=self.agent
        )
        for key, val in approve_body["claims"].items():
            self.assertFalse(val)

        for key in DEFAULT_CLAIMS:
            self.assertIn(key, approve_body["claims"])

    def test_portal_contains_listing_intake_panel(self):
        rosie = tenant_manager.get_tenant_by_slug("rosie")
        self.assertIsNotNone(rosie)
        builder = FastSiteBuilder()
        html = builder._generate_portal_html(rosie)
        self.assertIn("Media & Listing Intake Queue", html)
        self.assertIn("panel-listings", html)
        self.assertIn("approveListingForShowcase", html)
        self.assertIn("listing-intake-form", html)
        self.assertIn("SOP §12", html)

    def test_front_door_listing_media_modal(self):
        rosie = tenant_manager.get_tenant_by_slug("rosie")
        builder = FastSiteBuilder()
        html = builder._generate_luxury_realty_html(rosie)
        self.assertIn("listingMediaModal", html)
        self.assertIn("openListingMediaModal", html)
        self.assertIn("submitListingMedia", html)
        self.assertIn("/api/listing/submit", html)
        self.assertIn("portal.html#listings", html)
        self.assertIn("STAGED ONLY", html)


if __name__ == "__main__":
    unittest.main()
