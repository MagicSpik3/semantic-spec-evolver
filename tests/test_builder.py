import unittest
from unittest.mock import MagicMock
from core.builder import Builder
from core.prompts import BUILDER_V1

class TestBuilder(unittest.TestCase):
    def test_build_flow(self):
        """Verify Builder sends the spec to the LLM and returns code."""
        
        # 1. Mock the LLM
        mock_llm = MagicMock()
        expected_code = "def process(x): return x * x"
        mock_llm.complete.return_value = expected_code
        
        # 2. Initialize Builder
        builder = Builder(llm_client=mock_llm)
        
        # 3. Run Build
        dummy_spec = "# Spec: Square\nLogic: Multiply input by itself."
        result = builder.build(dummy_spec)
        
        # 4. Verify Output
        self.assertEqual(result, expected_code)
        
        # 5. Verify Prompt Construction
        args, _ = mock_llm.complete.call_args
        self.assertEqual(args[0], BUILDER_V1) # System prompt
        self.assertIn(dummy_spec, args[1])    # User prompt contains spec

if __name__ == '__main__':
    unittest.main()