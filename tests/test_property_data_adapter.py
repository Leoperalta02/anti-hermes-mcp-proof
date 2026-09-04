"""
tests/test_property_data_adapter.py
Unit tests asserting the Real Estate Data Quadrant (MLS x Zillow x County Records).
"""

import unittest
from apex_core.property_data_adapter import property_adapter

class TestPropertyDataAdapter(unittest.TestCase):
    def test_benchmark_property_lookup(self):
        result = property_adapter.lookup_property("21450 Bella Terra Blvd, Estero, FL")
        
        # Check Base Properties
        self.assertIn("Bella Terra", result["submarket"])
        self.assertEqual(result["beds"], 4)
        self.assertEqual(result["baths"], 3)
        self.assertEqual(result["living_sqft"], 2480)
        
        # Check MLS Quadrant
        self.assertIn("SWFL-", result["mls"]["mls_id"])
        self.assertGreater(len(result["mls"]["active_subdivision_comps"]), 0)
        
        # Check Consumer Quadrant (Zillow)
        self.assertGreater(result["consumer"]["zestimate"], 500000)
        self.assertGreater(result["consumer"]["rent_zestimate"], 2000)
        
        # Check County Records Quadrant (LeePA)
        self.assertIn("15-46-25-E4", result["county_records"]["parcel_id"])
        self.assertEqual(result["county_records"]["owner_type"], "ABSENTEE_OWNER")
        self.assertFalse(result["county_records"]["homestead_exempt"])
        self.assertGreater(result["county_records"]["equity_percentage"], 70)
        self.assertIn("X", result["county_records"]["flood_zone"])
        
        # Check Keystone Intelligence Output
        keystone = result["keystone_valuation"]
        self.assertGreater(keystone["target_recommended_price"], 700000)
        self.assertGreater(keystone["seller_motivation_score"], 80)
        self.assertIn("Absentee owner", keystone["seller_motivation_indicators"][0])

    def test_synthetic_property_synthesis(self):
        result = property_adapter.lookup_property("742 Evergreen Terrace, Naples, FL")
        self.assertIn("Naples", result["submarket"])
        self.assertIn("Collier", result["county_records"]["county"])
        self.assertGreater(result["keystone_valuation"]["target_recommended_price"], 1000000)
        self.assertIn("SWFL-", result["mls"]["mls_id"])

if __name__ == "__main__":
    unittest.main()
