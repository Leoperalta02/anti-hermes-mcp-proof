"""
test_specialist_oauth.py
Verification suite for specialist OAuth model migration (Fizz, Honey, Pollen).
"""
import unittest
import json
import os

class TestSpecialistOAuthMigration(unittest.TestCase):

    def setUp(self):
        self.managed_agents_path = os.path.expandvars(r'%APPDATA%\xyz.block.buzz.app\agents\managed-agents.json')
        self.harness_dir = os.path.expandvars(r'%APPDATA%\xyz.block.buzz.app\custom_harnesses')
        
        with open(self.managed_agents_path, 'r', encoding='utf-8') as f:
            self.agents = json.load(f)

    def test_fizz_oauth_migration(self):
        fizz_entry = next((a for a in self.agents if a.get('pubkey') == '467866fc6339b3ba8acb4a7e0ab3146e77b5160725a3f2fa3439ada18e2e0b24'), None)
        self.assertIsNotNone(fizz_entry, "Fizz pubkey entry missing")
        self.assertEqual(fizz_entry['model'], 'openai-codex:gpt-5.6-luna')
        self.assertTrue(fizz_entry['model'].startswith('openai-codex:'))

        # Harness check
        harness_path = os.path.join(self.harness_dir, 'hermes-agent-fizz.json')
        with open(harness_path, 'r', encoding='utf-8') as f:
            harness = json.load(f)
        self.assertEqual(harness['env']['BUZZ_EXECUTING_AGENT_PUBKEY'], '467866fc6339b3ba8acb4a7e0ab3146e77b5160725a3f2fa3439ada18e2e0b24')
        self.assertNotIn('OPENAI_API_KEY', harness['env'])

    def test_honey_oauth_migration(self):
        honey_entry = next((a for a in self.agents if a.get('pubkey') == 'bcc3e4bcb9ed35bb45c765a61e5aa2082ed09404e2297f376d96dba06f66b842'), None)
        self.assertIsNotNone(honey_entry, "Honey pubkey entry missing")
        self.assertEqual(honey_entry['model'], 'openai-codex:gpt-5.6-luna')
        self.assertTrue(honey_entry['model'].startswith('openai-codex:'))

        # Harness check
        harness_path = os.path.join(self.harness_dir, 'hermes-agent-honey.json')
        with open(harness_path, 'r', encoding='utf-8') as f:
            harness = json.load(f)
        self.assertEqual(harness['env']['BUZZ_EXECUTING_AGENT_PUBKEY'], 'bcc3e4bcb9ed35bb45c765a61e5aa2082ed09404e2297f376d96dba06f66b842')
        self.assertNotIn('GOOGLE_API_KEY', harness['env'])

    def test_pollen_oauth_migration(self):
        pollen_entry = next((a for a in self.agents if a.get('pubkey') == '2f7188798fe95455d8375b3f54fe777e2cade67c3ff9694aaaea4a82b8c7b507'), None)
        self.assertIsNotNone(pollen_entry, "Pollen pubkey entry missing")
        self.assertTrue(pollen_entry['model'].startswith('xai-oauth:'))


        # Harness check
        harness_path = os.path.join(self.harness_dir, 'hermes-agent-pollen.json')
        with open(harness_path, 'r', encoding='utf-8') as f:
            harness = json.load(f)
        self.assertEqual(harness['env']['BUZZ_EXECUTING_AGENT_PUBKEY'], '2f7188798fe95455d8375b3f54fe777e2cade67c3ff9694aaaea4a82b8c7b507')
        self.assertNotIn('XAI_API_KEY', harness['env'])

if __name__ == '__main__':
    unittest.main()
