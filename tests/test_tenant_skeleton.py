"""
Automated Test Suite for Hermes Tenant Skeleton Manager (W4)
Per ROSIE_ONBOARDING_SOP.md §8 & §10 and ANTI_STATUS.md W4.

Verifies:
1. Template skeleton generation under tenants/skeleton/.
2. Sovereign tenant provisioning (Harbor, Keystone, Quill).
3. Manifest integrity & SOP §12 zero false-claims verification.
4. SOUL.md synchronization and profile loading verification under real-estate-copilot.
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Ensure workspace root on sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
import sys
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from apex_core.tenant_skeleton_manager import (
    DEFAULT_PROFILE_DIR,
    TenantSkeletonManager,
)


class TestTenantSkeletonManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="apex_tenant_skeleton_test_"))
        self.mock_profile_dir = self.temp_dir / "real-estate-copilot"
        self.mock_profile_dir.mkdir(parents=True)
        self.mock_soul_file = self.mock_profile_dir / "SOUL.md"
        self.mock_soul_file.write_text(
            "# Rosie's Real Estate AI CoPilot\n\n"
            "## YOUR 4 CORE BUILT-IN REAL ESTATE SKILLS:\n"
            "### 1. Comparative Market Analysis (CMA) & Valuation Expert:\n"
            "### 2. MLS Remarks & Marketing Copywriter:\n"
            "### 3. Lead Triage & Qualification:\n"
            "### 4. Transaction Coordinator & Florida FAR/BAR Contract Dates:\n",
            encoding="utf-8"
        )
        self.manager = TenantSkeletonManager(profile_dir=self.mock_profile_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ensure_skeleton_template(self):
        """Verify template skeleton is created with all specialist directories and manifest."""
        skeleton_dir = self.manager.ensure_skeleton_template()
        self.assertTrue(skeleton_dir.exists())

        # Check required files
        self.assertTrue((skeleton_dir / "TENANT_MANIFEST.json").exists())
        self.assertTrue((skeleton_dir / "SOUL.md").exists())
        self.assertTrue((skeleton_dir / "harbor" / "follow_up_queue.json").exists())
        self.assertTrue((skeleton_dir / "harbor" / "lead_triage_protocol.md").exists())
        self.assertTrue((skeleton_dir / "keystone" / "cma_guidelines.md").exists())
        self.assertTrue((skeleton_dir / "quill" / "marketing_templates.md").exists())

        manifest = json.loads((skeleton_dir / "TENANT_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "template")
        self.assertFalse(manifest["claims"]["agent_deployed"])
        self.assertFalse(manifest["claims"]["portal_created"])
        self.assertFalse(manifest["claims"]["mls_connected"])

    def test_provision_tenant(self):
        """Verify provisioning a new tenant creates isolated skeleton and customized SOUL.md."""
        tenant_dir = self.manager.provision_tenant(
            slug="rosie",
            realtor_name="Rosie Rivera",
            brokerage="Rosie Rivera Luxury Real Estate",
            market="Estero & Naples, FL",
            email="rosie@rosieriveraluxury.com",
            phone="239-555-0144"
        )
        self.assertTrue(tenant_dir.exists())

        # Verify manifest
        manifest = json.loads((tenant_dir / "TENANT_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["tenant_slug"], "rosie")
        self.assertEqual(manifest["realtor_name"], "Rosie Rivera")
        self.assertEqual(manifest["status"], "staged_drafts_only")
        self.assertFalse(manifest["claims"]["agent_deployed"])

        # Verify SOUL
        soul = (tenant_dir / "SOUL.md").read_text(encoding="utf-8")
        self.assertIn("Rosie Rivera", soul)
        self.assertIn("Harbor", soul)
        self.assertIn("Keystone", soul)
        self.assertIn("Quill", soul)
        self.assertIn("STAGED DRAFTS ONLY", soul)

        # Verify specialists
        self.assertTrue((tenant_dir / "harbor" / "follow_up_queue.json").exists())
        self.assertTrue((tenant_dir / "keystone" / "cma_market_consult.md").exists())
        self.assertTrue((tenant_dir / "quill" / "welcome_packet.md").exists())

        # Verify verification method
        is_ok, missing = self.manager.verify_tenant_skeleton("rosie")
        self.assertTrue(is_ok)
        self.assertEqual(len(missing), 0)

    def test_verify_tenant_skeleton_catches_missing_and_false_claims(self):
        """Verify verification catches missing directories and false claims."""
        # Non-existent tenant
        is_ok, missing = self.manager.verify_tenant_skeleton("nonexistent")
        self.assertFalse(is_ok)
        self.assertIn("does not exist", missing[0])

        # Provision and tamper with manifest
        tenant_dir = self.manager.provision_tenant(
            slug="tampered",
            realtor_name="Tampered Realtor",
            brokerage="Tampered Realty",
            market="Estero, FL"
        )
        manifest_path = tenant_dir / "TENANT_MANIFEST.json"
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_data["claims"]["agent_deployed"] = True  # SOP §12 violation
        manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")

        is_ok, missing = self.manager.verify_tenant_skeleton("tampered")
        self.assertFalse(is_ok)
        self.assertTrue(any("SOP §12 violation" in m for m in missing))

    def test_sync_rosie_profile_soul_and_idempotence(self):
        """Verify syncing delegation block to SOUL.md is clean and idempotent."""
        synced = self.manager.sync_rosie_profile_soul()
        self.assertTrue(synced)

        content = self.mock_soul_file.read_text(encoding="utf-8")
        self.assertIn("Tenant Workspace & Specialist Delegation", content)
        self.assertIn("Active Tenant Skeleton Root: `tenants/rosie/`", content)
        self.assertIn("Harbor Specialist", content)
        self.assertIn("Keystone Specialist", content)
        self.assertIn("Quill Specialist", content)

        # Idempotent call
        synced_again = self.manager.sync_rosie_profile_soul()
        self.assertTrue(synced_again)
        content_again = self.mock_soul_file.read_text(encoding="utf-8")
        self.assertEqual(content_again.count("Tenant Workspace & Specialist Delegation"), 1)

    def test_verify_profile_loaded(self):
        """Verify profile loaded checker validates SOUL.md skills and tenants directory."""
        self.manager.ensure_skeleton_template()
        is_ok, missing = self.manager.verify_profile_loaded()
        self.assertTrue(is_ok)
        self.assertEqual(len(missing), 0)

    def test_live_real_estate_copilot_profile(self):
        """Verify the live Alienware real-estate-copilot profile passes verification if present."""
        if DEFAULT_PROFILE_DIR.exists():
            live_mgr = TenantSkeletonManager()
            is_ok, missing = live_mgr.verify_profile_loaded()
            self.assertTrue(is_ok, f"Live profile check failed with missing: {missing}")

            rosie_ok, rosie_missing = live_mgr.verify_tenant_skeleton("rosie")
            self.assertTrue(rosie_ok, f"Live Rosie tenant skeleton check failed: {rosie_missing}")


if __name__ == "__main__":
    unittest.main()
