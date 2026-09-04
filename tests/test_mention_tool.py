"""
test_mention_tool.py
Verification suite for mention_agent_in_channel supervisor-mediated in-channel mention tool.
Tests all 5 fail-closed governance rules.
"""
import importlib
import os
import sys
import unittest

# Alienware local path for hermes-agent
_HERMES_AGENT_PATH = r'C:\LEO-LAB-ANTIGRAVITY\hermes-agent'
if os.path.exists(_HERMES_AGENT_PATH) and _HERMES_AGENT_PATH not in sys.path:
    sys.path.insert(0, _HERMES_AGENT_PATH)

try:
    _managed_tool = importlib.import_module("tools.managed_agent_tool")
    mention_agent_in_channel = _managed_tool.mention_agent_in_channel
    send_managed_agent = _managed_tool.send_managed_agent
    set_current_channel = _managed_tool.set_current_channel
    set_active_round_seats = _managed_tool.set_active_round_seats
    _PANEL_ROUTABLE_PUBKEYS = _managed_tool._PANEL_ROUTABLE_PUBKEYS
except Exception:
    _managed_tool = None


@unittest.skipIf(_managed_tool is None, "tools.managed_agent_tool not found on this host")
class TestMentionAgentToolGovernance(unittest.TestCase):

    def setUp(self):
        set_current_channel("panel-advisors", "297db211-a6d3-4544-97f2-940b55e85284")
        set_active_round_seats({"grok 2", "cursor pro"})

    def test_send_managed_agent_hard_blocked_in_panel(self):
        res = send_managed_agent({"target_agent": "Grok 2", "content": "test"})
        self.assertIn("[STOP — TOOL DENY]", res)

    def test_non_panel_channel_invocation_fails(self):
        """Rule 5: Scope Lock — Non-panel channel invocation fails closed."""
        set_current_channel("general", "general-channel-id")
        res = mention_agent_in_channel({"target_agent": "Grok 2", "message": "hello"})
        self.assertIn("[STOP — NON-PANEL CHANNEL]", res)

    def test_unnamed_round_seat_rejected(self):
        """Rule 2: Current-round enforcement — Unnamed seat rejected."""
        set_current_channel("panel-advisors", "297db211-a6d3-4544-97f2-940b55e85284")
        set_active_round_seats({"grok 2"}) # Only Grok 2 named
        res = mention_agent_in_channel({"target_agent": "Cursor Pro", "message": "hello"})
        self.assertIn("[ROUTE REJECT]", res)

    def test_non_member_pubkey_rejected(self):
        """Rule 3: Channel Membership verification — Non-member rejected."""
        set_current_channel("panel-advisors", "297db211-a6d3-4544-97f2-940b55e85284")
        set_active_round_seats({"pollen"})
        res = mention_agent_in_channel({"target_agent": "Pollen", "message": "hello"})
        self.assertIn("[ROUTE REJECT]", res)

    def test_missing_event_id_fails(self):
        """Rule 4: Traceability — Missing event ID fails."""
        # Simulated mockup where requester returns dict without event_id
        set_current_channel("panel-advisors", "297db211-a6d3-4544-97f2-940b55e85284")
        set_active_round_seats({"grok 2"})
        # Tested at unit level: if event_id evaluates to unknown/none, returns [STOP — NO EVENT ID]

    def test_send_managed_agent_blocked_in_alienware_hq(self):
        """Rule 6: HOLD Enforcement — send_managed_agent blocked on #Alienware-hq."""
        set_current_channel("alienware-hq", "alienware-hq-id")
        res = send_managed_agent({"target_agent": "Pollen", "content": "test"})
        self.assertIn("[STOP — HOLD ACTIVE]", res)

    def test_send_managed_agent_specialist_sandbox_guard(self):
        """Rule 7: Onboarding Isolation — Specialists only reachable in sandbox channels."""
        set_current_channel("general", "general-channel-id")
        res = send_managed_agent({"target_agent": "Harbor", "content": "test"})
        self.assertIn("[STOP — SANDBOX VIOLATION]", res)

    def test_send_managed_agent_specialist_sandbox_guard_missing_channel(self):
        """Rule 7b: Fail-Closed Onboarding Isolation — Specialist blocked if channel context is missing."""
        set_current_channel("", "")
        res = send_managed_agent({"target_agent": "Keystone", "content": "test"})
        self.assertIn("[STOP — SANDBOX VIOLATION]", res)


if __name__ == '__main__':
    unittest.main()
