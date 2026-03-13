import unittest
from ananas_ai.config import load_settings

class ConfigTests(unittest.TestCase):
    def test_load_settings(self):
        settings = load_settings()
        self.assertEqual(settings.project_overview["project_name"], "Ananas AI Platform")
        self.assertIn("phase_1_agents", settings.agents)
