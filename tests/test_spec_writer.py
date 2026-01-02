import unittest
from unittest.mock import MagicMock
from core.spec_writer import SpecWriter

class TestSpecWriter(unittest.TestCase):
    def test_initial_draft_flow(self):
        """Verify SpecWriter formats the prompt and calls the LLM."""
        
        # 1. Mock the LLM Client
        mock_llm = MagicMock()
        mock_llm.complete.return_value = "# Functional Specification\nTest Content"
        
        # 2. Initialize Writer with Mock
        writer = SpecWriter(llm_client=mock_llm)
        
        # 3. Run
        dummy_code = "def add(a, b): return a + b"
        result = writer.initial_draft(dummy_code)
        
        # 4. Verify Output
        self.assertEqual(result, "# Functional Specification\nTest Content")
        
        # 5. Verify Prompt Construction
        # We check if the code was actually injected into the prompt
        args, _ = mock_llm.complete.call_args
        self.assertIn("def add(a, b):", args[1]) # user_prompt is the second arg

if __name__ == '__main__':
    unittest.main()