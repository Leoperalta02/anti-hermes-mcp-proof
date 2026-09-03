"""
test_panel_seat_auth.py
Verification suite for #panel-advisors seats: Grok 2, Cursor Pro, Hermes.
"""
import unittest
import json
import os

class TestPanelSeatAuth(unittest.TestCase):

    def setUp(self):
        self.managed_agents_path = os.path.expandvars(r'%APPDATA%\xyz.block.buzz.app\agents\managed-agents.json')
        with open(self.managed_agents_path, 'r', encoding='utf-8') as f:
            self.agents = json.load(f)

    def test_grok2_panel_seat_oauth(self):
        grok = next((a for a in self.agents if a.get('pubkey') == '7f7a088edf2bc7f02a0c47e2e162efa863631dff06a126246a38493e7cd9e235'), None)
        self.assertIsNotNone(grok, "Grok 2 panel seat missing")
        self.assertTrue(grok['model'].startswith('xai-oauth:'))
        self.assertEqual(grok['model'], 'xai-oauth:grok-2-latest')

    def test_cursor_pro_panel_seat(self):
        cursor = next((a for a in self.agents if a.get('pubkey') == '2cf56b3bf472df0a9ff819a86d8f84ad24e405f444af0a2d491173cfb32ea8e1'), None)
        self.assertIsNotNone(cursor, "Cursor Pro panel seat missing")
        self.assertIn('gpt-5.4-mini', cursor['model'])

    def test_hermes_panel_seat_oauth(self):
        hermes = next((a for a in self.agents if a.get('pubkey') == '16dac8fc4fbbc6d0c42eaec2fd46e77af1f86ac6268e31d8da7a4d372095a314'), None)
        self.assertIsNotNone(hermes, "Hermes panel seat missing")
        self.assertEqual(hermes['model'], 'openai-codex:gpt-5.6-luna')

if __name__ == '__main__':
    unittest.main()
