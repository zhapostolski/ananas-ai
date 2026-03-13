import unittest
from ananas_ai.cli import doctor

class CLISmokeTests(unittest.TestCase):
    def test_doctor(self):
        self.assertEqual(doctor(), 0)
