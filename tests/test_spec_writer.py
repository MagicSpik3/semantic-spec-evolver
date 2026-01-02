# tests/test_spec_writer.py
import pytest
from unittest.mock import patch, MagicMock
from core.spec_writer import SpecWriter

@patch("core.spec_writer.LLMClient")
def test_generate_spec_flow(mock_llm_client_cls):
    # 1. Setup
    # Mock the instance created by the class
    mock_instance = mock_llm_client_cls.return_value
    mock_instance.complete.return_value = "# Final Technical Spec"
    
    # Initialize SpecWriter (which will use the mocked LLMClient)
    writer = SpecWriter()
    
    context = "Build a CLI tool"
    qa_history = [{"question": "What language?", "answer": "Python"}]
    
    # 2. Execute
    result = writer.generate_spec(context, qa_history)

    # 3. Assert
    assert result == "# Final Technical Spec"
    
    # Verify complete() was called
    mock_instance.complete.assert_called_once()
    
    # Verify arguments passed to complete()
    call_args = mock_instance.complete.call_args
    # call_args[1] is kwargs, call_args[0] is args. 
    # Since we used named args or positional, let's check safely.
    
    # Check if system prompt was passed
    args, kwargs = mock_instance.complete.call_args
    
    # If passed as keyword args:
    if 'user_prompt' in kwargs:
        assert "Build a CLI tool" in kwargs['user_prompt']
    else:
        # If passed as positional args (system, user)
        assert "Build a CLI tool" in args[1]

def test_dependency_injection():
    # Verify we can pass a specific client (useful for Engine tests)
    mock_client = MagicMock()
    mock_client.complete.return_value = "Injected"
    
    writer = SpecWriter(llm_client=mock_client)
    result = writer.generate_spec("ctx", [])
    
    assert result == "Injected"