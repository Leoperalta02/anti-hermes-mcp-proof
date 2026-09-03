"""
Test Suite for Multi-Subscription Model Failover Cascade
Verifies failover sequence generation, fallback routing, and zero-downtime cascade.
"""

import unittest
from apex_core.apex_models import ModelFailoverCascade, AgentModelConfig

class TestModelFailoverCascade(unittest.TestCase):

    def setUp(self):
        self.hermes_cascade = ModelFailoverCascade(
            primary_model="gpt-5.6-luna",
            fallback_models=["grok-2-latest", "claude-3.7-sonnet", "gpt-4o"]
        )
        self.cursor_cascade = ModelFailoverCascade(
            primary_model="gpt-5.6-sol",
            fallback_models=["grok-2-latest", "claude-3.7-sonnet", "gpt-4o"]
        )

    def test_hermes_failover_sequence(self):
        sequence = self.hermes_cascade.get_failover_sequence()
        expected = ["gpt-5.6-luna", "grok-2-latest", "claude-3.7-sonnet", "gpt-4o"]
        self.assertEqual(sequence, expected)

    def test_cursor_failover_sequence(self):
        sequence = self.cursor_cascade.get_failover_sequence()
        expected = ["gpt-5.6-sol", "grok-2-latest", "claude-3.7-sonnet", "gpt-4o"]
        self.assertEqual(sequence, expected)

    def test_exclude_free_tier_keywords(self):
        cascade = ModelFailoverCascade(
            primary_model="gpt-5.6-luna",
            fallback_models=["generativelanguage-free_tier", "grok-2-latest"]
        )
        sequence = cascade.get_failover_sequence()
        self.assertNotIn("generativelanguage-free_tier", sequence)
        self.assertEqual(sequence, ["gpt-5.6-luna", "grok-2-latest"])

    def test_no_duplicate_models_in_sequence(self):
        cascade = ModelFailoverCascade(
            primary_model="grok-2-latest",
            fallback_models=["grok-2-latest", "gpt-5.6-luna", "grok-2-latest"]
        )
        sequence = cascade.get_failover_sequence()
        self.assertEqual(sequence, ["grok-2-latest", "gpt-5.6-luna"])

    def test_agent_model_config(self):
        config = AgentModelConfig(
            agent_name="Hermes",
            role="Chief Operating Officer",
            model_cascade=self.hermes_cascade
        )
        self.assertEqual(config.agent_name, "Hermes")
        self.assertTrue(config.model_cascade.paid_subscriptions_only)

if __name__ == "__main__":
    unittest.main()

