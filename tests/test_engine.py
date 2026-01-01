import unittest
import sys
import os
import shutil
from unittest.mock import MagicMock, patch

# --- 1. MOCK THE MISSING MODULES ---
# We must do this BEFORE importing EvolutionEngine, 
# otherwise the import will fail because the files don't exist yet.
sys.modules['core.spec_writer'] = MagicMock()
sys.modules['core.builder'] = MagicMock()
sys.modules['core.optimizer'] = MagicMock()

# Now we can safely import
from core.engine import EvolutionEngine

class TestEvolutionEngine(unittest.TestCase):
    def setUp(self):
        self.test_source = "sandbox/source_logic.py"
        # Ensure we have a dummy source file to read
        if not os.path.exists(self.test_source):
            with open(self.test_source, 'w') as f:
                f.write("def process_data(): pass")

    def tearDown(self):
        # Cleanup the history folder after tests
        if os.path.exists("history"):
            shutil.rmtree("history")

    @patch('core.engine.SpecWriter')
    @patch('core.engine.Builder')
    @patch('core.engine.Optimizer')
    @patch('core.engine.Critic')
    def test_engine_flow_success(self, MockCritic, MockOpt, MockBuilder, MockSpec):
        """Test a full successful run where the Critic passes immediately."""
        
        # A. Setup the Mocks
        # 1. SpecWriter returns a dummy spec
        MockSpec.return_value.initial_draft.return_value = "Spec v1"
        
        # 2. Builder returns dummy code
        MockBuilder.return_value.build.return_value = "print('hello')"
        
        # 3. Critic returns SUCCESS
        mock_critic_instance = MockCritic.return_value
        mock_critic_instance.evaluate.return_value = {
            "pass": True, 
            "score": 1.0, 
            "failures": []
        }

        # B. Run the Engine
        engine = EvolutionEngine(self.test_source)
        engine.start(max_iterations=1)

        # C. Verification
        # Check if history folder was created
        self.assertTrue(os.path.exists("history"))
        runs = os.listdir("history")
        self.assertEqual(len(runs), 1)
        
        run_path = os.path.join("history", runs[0], "iteration_01")
        
        # Check if artifacts were saved
        self.assertTrue(os.path.exists(os.path.join(run_path, "spec.md")))
        self.assertTrue(os.path.exists(os.path.join(run_path, "report.json")))
        
        # Verify interactions
        MockSpec.return_value.initial_draft.assert_called_once()
        MockBuilder.return_value.build.assert_called_once_with("Spec v1")

    @patch('core.engine.SpecWriter')
    @patch('core.engine.Builder')
    @patch('core.engine.Optimizer')
    @patch('core.engine.Critic')
    def test_engine_flow_failure_retry(self, MockCritic, MockOpt, MockBuilder, MockSpec):
        """Test that the engine loops and calls Optimizer on failure."""
        
        # A. Setup Mocks
        MockSpec.return_value.initial_draft.return_value = "Spec v1"
        MockBuilder.return_value.build.return_value = "Bad Code"
        MockOpt.return_value.evolve.return_value = "Spec v2"
        
        mock_critic_instance = MockCritic.return_value
        
        # Critic fails the first time, passes the second time
        mock_critic_instance.evaluate.side_effect = [
            {"pass": False, "score": 0.5, "failures": ["Error 1"]}, # Iteration 1
            {"pass": True, "score": 1.0, "failures": []}            # Iteration 2
        ]

        # B. Run Engine
        engine = EvolutionEngine(self.test_source)
        engine.start(max_iterations=2)

        # C. Verification
        runs = os.listdir("history")
        run_path = os.path.join("history", runs[0])
        
        # Should have 2 iterations
        self.assertTrue(os.path.exists(os.path.join(run_path, "iteration_01")))
        self.assertTrue(os.path.exists(os.path.join(run_path, "iteration_02")))
        
        # Verify Optimizer was called with the failure
        MockOpt.return_value.evolve.assert_called_once()
        args = MockOpt.return_value.evolve.call_args
        self.assertEqual(args[0][0], "Spec v1") # Previous spec

if __name__ == '__main__':
    unittest.main()