"""
tests/test_onboarding_pipeline.py
Unit tests asserting the autonomous end-to-end onboarding pipeline.
"""

import hashlib
import importlib
import os
from pathlib import Path
import tempfile
import unittest
from contextlib import ExitStack
from unittest.mock import patch

from apex_core.onboarding_pipeline import onboarding_pipeline


pipeline_module = importlib.import_module("apex_core.onboarding_pipeline")


class TestOnboardingPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="apex_onboarding_test_")
        self.temp_root = Path(self.temp_dir.name)
        self.public_sites_root = self.temp_root / "public_sites"
        self.rosie_site = Path(__file__).resolve().parents[1] / "public_sites" / "rosie"
        self.rosie_before = self._tree_digest(self.rosie_site)

        self.patches = ExitStack()
        self.patches.enter_context(patch.object(pipeline_module, "BRIEFS_DIR", str(self.temp_root / "briefs")))
        self.patches.enter_context(patch.object(pipeline_module, "TENANTS_DIR", str(self.temp_root / "tenants")))
        self.patches.enter_context(patch.object(pipeline_module, "EVIDENCE_DIR", str(self.temp_root / "evidence")))
        self.patches.enter_context(patch.object(pipeline_module.fast_builder, "output_dir", str(self.public_sites_root)))
        self.patches.enter_context(
            patch.object(pipeline_module.tenant_manager, "data_path", str(self.temp_root / "tenants.json"))
        )
        for directory in ("briefs", "tenants", "evidence"):
            (self.temp_root / directory).mkdir()

    def tearDown(self):
        self.patches.close()
        self.temp_dir.cleanup()

    @staticmethod
    def _tree_digest(root):
        digest = hashlib.sha256()
        if not root.exists():
            return digest.hexdigest()
        for path in sorted(root.rglob("*")):
            digest.update(str(path.relative_to(root)).encode("utf-8"))
            if path.is_file():
                digest.update(path.read_bytes())
        return digest.hexdigest()

    def _client_payload(self):
        return {
            "full_name": "Rosie Rivera",
            "subdomain_slug": "rosie_dryrun_test",
            "email": "rosie@rosieriveraluxury.com",
            "phone": "239-555-0199",
            "brokerage": "Rosie Rivera Luxury Real Estate",
            "market": "Estero & Naples, FL",
            "package_tier": "pro_realty",
            "monthly_price": 499,
            "leo_decision": "APPROVE PROVISION DRYRUN",
        }

    def test_full_onboarding_cycle(self):
        result = onboarding_pipeline.run_onboarding(self._client_payload())

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["tenant_slug"], "rosie_dryrun_test")
        self.assertTrue(os.path.exists(result["front_door_url"]))
        self.assertTrue(os.path.exists(result["portal_url"]))
        self.assertIn("Welcome to Your Private AI Office", result["welcome_instructions"])
        self.assertIn("APEX ONBOARDING SUCCESS", result["telegram_alert"])
        self.assertTrue(result["provision_gate"]["provision_allowed"])
        self.assertEqual(result["provision_gate"]["gate_mode"], "DRYRUN")
        self.assertIn(result["dispatch"]["dispatch_status"], ("STAGED_ONLY", "LIVE_BLOCKED_NO_TOKEN"))

    def test_dryrun_uses_temp_tenant_and_leaves_rosie_site_unchanged(self):
        result = onboarding_pipeline.run_onboarding(self._client_payload())

        temp_tenant_root = self.temp_root / "tenants" / "rosie_dryrun_test"
        temp_site_root = self.public_sites_root / "rosie_dryrun_test"
        self.assertTrue(temp_tenant_root.joinpath("TENANT_MANIFEST.json").exists())
        self.assertTrue(temp_site_root.joinpath("index.html").exists())
        self.assertEqual(Path(result["front_door_url"]).resolve(), temp_site_root.joinpath("index.html").resolve())
        self.assertEqual(Path(result["portal_url"]).resolve(), temp_site_root.joinpath("portal.html").resolve())
        self.assertEqual(self._tree_digest(self.rosie_site), self.rosie_before)


if __name__ == "__main__":
    unittest.main()
