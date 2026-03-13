import unittest
from ananas_ai.model_router import choose_model

class RouterTests(unittest.TestCase):
    def test_default_route(self):
        self.assertEqual(choose_model("performance-agent").model, "claude-sonnet")

    def test_escalation(self):
        self.assertEqual(choose_model("cross-channel-brief-agent", complexity="high").model, "claude-opus")
