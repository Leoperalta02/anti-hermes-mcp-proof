"""
test_reply_path_audit.py
Deterministic audit of Buzz agent reply paths and ACP supervisor publishing architecture.
"""
import unittest
import json
import os

class TestBuzzReplyPathAudit(unittest.TestCase):

    def setUp(self):
        self.managed_agents_path = os.path.expandvars(r'%APPDATA%\xyz.block.buzz.app\agents\managed-agents.json')
        self.harness_dir = os.path.expandvars(r'%APPDATA%\xyz.block.buzz.app\custom_harnesses')
        
        with open(self.managed_agents_path, 'r', encoding='utf-8') as f:
            self.agents = json.load(f)

    def test_no_private_key_injection_in_harnesses(self):
        harness_files = [f for f in os.listdir(self.harness_dir) if f.endswith('.json')]
        for h_file in harness_files:
            h_path = os.path.join(self.harness_dir, h_file)
            with open(h_path, 'r', encoding='utf-8') as f:
                h_data = json.load(f)
            env = h_data.get('env', {})
            self.assertNotIn('BUZZ_PRIVATE_KEY', env, f"BUZZ_PRIVATE_KEY must not be present in {h_file}")
            self.assertNotIn('NOSTR_PRIVATE_KEY', env, f"NOSTR_PRIVATE_KEY must not be present in {h_file}")

    def test_native_stdout_publisher_rules_in_prompts(self):
        for agent in self.agents:
            sp = agent.get('system_prompt', '')
            if sp:
                # System prompt must forbid CLI messaging commands and instruct native delivery
                self.assertNotIn('buzz messages send', sp.lower(), f"Agent {agent.get('name')} must not use legacy CLI buzz messages send")

    def test_fail_closed_acp_supervisor_isolation(self):
        for agent in self.agents:
            env = agent.get('env', {}) if isinstance(agent.get('env'), dict) else {}
            self.assertNotIn('BUZZ_PRIVATE_KEY', env, f"Agent {agent.get('name')} has injected BUZZ_PRIVATE_KEY")

if __name__ == '__main__':
    unittest.main()
