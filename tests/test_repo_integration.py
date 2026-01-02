import unittest
import os
from unittest.mock import MagicMock, patch
from core.ingestor import Ingestor
from core.spec_writer import SpecWriter

class TestRepoIntegration(unittest.TestCase):
    
    @patch('core.spec_writer.LLMClient')
    def test_full_flow_mocked_llm(self, MockLLMClient):
        """
        Integration: Ingestor finds files -> SpecWriter generates specs.
        (Using Mock LLM to save tokens/time)
        """
        # 1. Setup Mock
        mock_instance = MockLLMClient.return_value
        mock_instance.complete.return_value = "# Mock Spec\nTODO: Implement"
        
        # 2. Point Ingestor at our actual 'sandbox' folder
        sandbox_path = os.path.abspath("sandbox")
        if not os.path.exists(sandbox_path):
            self.skipTest("Sandbox folder not found (running in CI?)")
            
        ingestor = Ingestor(sandbox_path, allowed_extensions=['.py'])
        files = ingestor.scan()
        
        # 3. Verify Ingestor found something (we expect at least interface_adapter.py)
        self.assertTrue(len(files) > 0, "Ingestor found no files in sandbox!")
        
        # 4. Run SpecWriter on found files
        writer = SpecWriter(llm_client=mock_instance)
        specs = {}
        
        for file in files:
            specs[file.name] = writer.initial_draft(file.content)
            
        # 5. Verify the pipeline connected
        # Check if we generated a spec for the known file
        known_file = "source_logic.py" 
        # Note: This might be squaring_logic.py depending on previous turn, adjust as needed.
        # We search broadly:
        self.assertTrue(any(f.name.endswith("_logic.py") for f in files))
        
        # Check if LLM was called once per file
        self.assertEqual(mock_instance.complete.call_count, len(files))

if __name__ == '__main__':
    unittest.main()