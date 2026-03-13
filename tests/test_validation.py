import unittest
from ananas_ai.validator import validate_agent_output

class ValidationTests(unittest.TestCase):
    def test_valid_payload(self):
        payload = {"agent_name": "performance-agent", "module_name": "performance", "output_type": "daily-summary", "date_from": "2026-03-01", "date_to": "2026-03-01", "data": {"headline": "ok"}}
        self.assertEqual(validate_agent_output(payload), [])
