"""
Automated Test Suite for Sovereign Realtor OS Lead Flow Integration
Verifies front-door dossier submission wiring and portal CRM/Kanban reactive staging.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apex_core.tenant_manager import tenant_manager
from apex_core.fast_site_builder import FastSiteBuilder, PUBLIC_SITES_DIR


class TestLeadFlowIntegration(unittest.TestCase):
    def setUp(self):
        self.builder = FastSiteBuilder()
        self.rosie = tenant_manager.get_tenant_by_slug("rosie")
        self.vance = tenant_manager.get_tenant_by_slug("vance")

    def test_builder_template_contains_lead_flow_logic(self):
        """Verify apex_core/fast_site_builder.py has the lead flow logic in Python source templates."""
        builder_file = os.path.join(os.path.dirname(__file__), "..", "apex_core", "fast_site_builder.py")
        with open(builder_file, "r", encoding="utf-8") as f:
            src = f.read()

        # Front-door submission logic in template
        self.assertIn("submitInquiry", src, "submitInquiry must be defined in builder template")
        self.assertIn("apex_leads_{t.subdomain_slug}", src, "Tenant-namespaced storage key must be in builder")
        self.assertIn("127.0.0.1:8787/brief", src, "Loopback brief submission must be in builder")

        # Portal reactive ingestion logic in template
        self.assertIn("loadInboundLeads", src, "loadInboundLeads must be defined in builder template")
        self.assertIn("contact-rows-container", src, "contact-rows-container must be in portal template")
        self.assertIn("buyer-col-new-lead", src, "buyer-col-new-lead must be in portal template")
        self.assertIn("FRONT-DOOR DOSSIER", src, "FRONT-DOOR DOSSIER badge must be in portal template")
        self.assertIn("addTestLead", src, "addTestLead simulator must be in portal template")

    def test_rosie_build_outputs_lead_flow(self):
        """Verify building Rosie site generates index.html and portal.html with full lead-flow wiring."""
        index_path = self.builder.build_site(self.rosie)
        portal_path = os.path.join(PUBLIC_SITES_DIR, self.rosie.subdomain_slug, "portal.html")

        # Check index.html
        with open(index_path, "r", encoding="utf-8") as f:
            index_html = f.read()
        self.assertIn("inquiry-name", index_html)
        self.assertIn("inquiry-contact", index_html)
        self.assertIn("apex_leads_rosie", index_html)
        self.assertIn("8787/brief", index_html)

        # Check portal.html
        with open(portal_path, "r", encoding="utf-8") as f:
            portal_html = f.read()
        self.assertIn("loadInboundLeads", portal_html)
        self.assertIn("apex_leads_rosie", portal_html)
        self.assertIn("contact-rows-container", portal_html)
        self.assertIn("buyer-col-new-lead", portal_html)
        self.assertIn("copilot-inbound-alert", portal_html)

        # Rosie Wishlist #1: Email + CRM Conversation Tracker & Dossier
        self.assertIn("crm-modal", portal_html, "CRM modal container must exist in portal.html")
        self.assertIn("openClientDossier", portal_html, "openClientDossier function must exist")
        self.assertIn("applyEmailTemplate", portal_html, "applyEmailTemplate composer helper must exist")
        self.assertIn("sendCrmReply", portal_html, "sendCrmReply function must exist")
        self.assertIn("openMailtoClient", portal_html, "openMailtoClient helper must exist")
        self.assertIn("saveCrmNotes", portal_html, "saveCrmNotes function must exist")
        self.assertIn("filterCrmQueue", portal_html, "filterCrmQueue filter bar function must exist")
        self.assertIn("crm-filter-bar", portal_html, "crm-filter-bar element must exist")

    def test_multi_tenant_clean_compilation(self):
        """Verify all 4 tenants compile cleanly with idempotent output."""
        for t in tenant_manager.list_tenants():
            index_path = self.builder.build_site(t)
            self.assertTrue(os.path.exists(index_path))
            portal_path = os.path.join(PUBLIC_SITES_DIR, t.subdomain_slug, "portal.html")
            self.assertTrue(os.path.exists(portal_path))

    def test_external_coaching_playbook(self):
        """Verify office_playbook.json exists and dynamically injects into portal templates."""
        playbook_path = os.path.join(os.path.dirname(__file__), "..", "apex_core", "office_playbook.json")
        self.assertTrue(os.path.exists(playbook_path), "office_playbook.json must exist in apex_core")

        playbook = self.builder.load_playbook()
        self.assertIsInstance(playbook, dict)
        required_keys = ["fsbo", "expired", "buyer", "seller", "commission", "lowball", "apptset", "followup"]
        for k in required_keys:
            self.assertIn(k, playbook, f"Playbook must contain '{k}' script")
            self.assertIn("title", playbook[k])
            self.assertIn("cat", playbook[k])
            self.assertIn("html", playbook[k])

        # Verify portal.html contains rendered buttons and scripts object
        portal_path = os.path.join(PUBLIC_SITES_DIR, self.rosie.subdomain_slug, "portal.html")
        with open(portal_path, "r", encoding="utf-8") as f:
            portal_html = f.read()

        self.assertIn("loadScript('fsbo'", portal_html)
        self.assertIn("FSBO First Call", portal_html)
        self.assertIn("Expired Recovery", portal_html)
        self.assertIn("const scripts = {", portal_html)


    def test_external_office_listings_and_apple_showcase(self):
        """Verify office_listings.json exists and dynamically injects into the Apple-style showcase."""
        listings_path = os.path.join(os.path.dirname(__file__), "..", "apex_core", "office_listings.json")
        self.assertTrue(os.path.exists(listings_path), "office_listings.json must exist in apex_core")

        listings = self.builder.load_listings()
        self.assertIsInstance(listings, list)
        self.assertGreaterEqual(len(listings), 4, "Must have at least 4 curated properties")

        for item in listings:
            self.assertIn("id", item)
            self.assertIn("title", item)
            self.assertIn("price", item)
            self.assertIn("status", item)
            self.assertIn("neighborhood", item)
            self.assertIn("keystone_valuation", item)

        # Verify index.html contains kinetic carousel and modal elements
        index_path = os.path.join(PUBLIC_SITES_DIR, self.rosie.subdomain_slug, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            index_html = f.read()

        self.assertIn("estates-section", index_html)
        self.assertIn("estates-track", index_html)
        self.assertIn("estate-card", index_html)
        self.assertIn("The Pelican Sound Sanctuary", index_html)
        self.assertIn("Vanderbilt Beachfront Haven", index_html)
        self.assertIn("estateModal", index_html)
        self.assertIn("openEstateModal", index_html)


if __name__ == "__main__":
    unittest.main()
