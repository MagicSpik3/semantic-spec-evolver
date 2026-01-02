import unittest
from unittest.mock import MagicMock
from core.optimizer import Optimizer
from core.prompts import OPTIMIZER_V1

class TestOptimizer(unittest.TestCase):
    def test_evolve_flow(self):
        """Verify Optimizer sends the report and old spec to LLM."""
        
        # 1. Mock LLM
        mock_llm = MagicMock()
        expected_spec = "# Improved Spec"
        mock_llm.complete.return_value = expected_spec
        
        # 2. Setup Data
        old_spec = "# Bad Spec"
        report = {
            "pass": False,
            "score": 0.5,
            "failures": ["Output column 'A' missing", "Expected int, got str"]
        }
        
        # 3. Run
        optimizer = Optimizer(llm_client=mock_llm)
        result = optimizer.evolve(old_spec, report)
        
        # 4. Verify
        self.assertEqual(result, expected_spec)
        
        # Check prompt content
        args, _ = mock_llm.complete.call_args
        sent_prompt = args[1] # user_prompt
        self.assertIn("Output column 'A' missing", sent_prompt)
        self.assertIn("# Bad Spec", sent_prompt)

if __name__ == '__main__':
    unittest.main()