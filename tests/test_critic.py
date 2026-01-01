import unittest
import os
from core.critic import Critic

class TestCritic(unittest.TestCase):
    def setUp(self):
        # We point both source and candidate to the SAME file for the control test
        self.source_path = os.path.abspath("sandbox/source_logic.py")
        
    def test_perfect_match(self):
        """Test that identical code results in a score of 1.0"""
        critic = Critic(self.source_path)
        
        # We pass the source logic AS the candidate logic
        report = critic.evaluate(self.source_path, num_trials=5)
        
        self.assertTrue(report["pass"])
        self.assertEqual(report["score"], 1.0)
        self.assertEqual(len(report["failures"]), 0)

if __name__ == '__main__':
    unittest.main()