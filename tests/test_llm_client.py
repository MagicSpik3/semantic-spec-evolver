import unittest
import requests
from unittest.mock import patch, MagicMock
from utils.llm_client import LLMClient

class TestLLMClient(unittest.TestCase):
    
    @patch("utils.llm_client.requests.post")
    def test_ollama_call_success(self, mock_post):
        """Test that client formats request correctly for Ollama."""
        # 1. Setup Mock Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "```python\nprint('Hello Local')\n```"
        }
        mock_post.return_value = mock_response

        # 2. Execute
        client = LLMClient(model="test-model")
        result = client.complete("System", "User")

        # 3. Verify Output (Markdown cleaning)
        self.assertEqual(result, "print('Hello Local')")

        # 4. Verify Request Payload
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        self.assertEqual(call_kwargs['json']['model'], "test-model")

    @patch("utils.llm_client.requests.post")
    def test_ollama_connection_error(self, mock_post):
        """Test graceful handling of connection failures."""
        # FIX: Raise a RequestException, not a generic Exception
        mock_post.side_effect = requests.exceptions.RequestException("Connection Refused")

        client = LLMClient()
        result = client.complete("Sys", "User")
        
        # Now the client should catch it and return the error string
        self.assertIn("# ERROR:", result)

if __name__ == '__main__':
    unittest.main()