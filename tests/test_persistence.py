import unittest
from ananas_ai.persistence import bootstrap, insert_agent_output, fetch_latest_outputs

class PersistenceTests(unittest.TestCase):
    def test_insert_and_fetch(self):
        bootstrap()
        insert_agent_output({"agent_name": "test-agent", "module_name": "test", "output_type": "daily-summary", "date_from": "2026-03-01", "date_to": "2026-03-01", "data": {"headline": "test"}, "model_used": "claude-sonnet", "version": "test"})
        self.assertTrue(len(fetch_latest_outputs()) >= 1)
