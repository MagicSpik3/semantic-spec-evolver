import os
import shutil
import pytest
from unittest.mock import patch, MagicMock
from core.engine import EvolutionEngine

@pytest.fixture
def source_path():
    # Setup dummy source file
    path = "sandbox/dummy_source.py"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write("def run(): pass")
    
    yield path 
    
    # Cleanup
    if os.path.exists(path):
        os.remove(path)
    if os.path.exists("history"):
        shutil.rmtree("history")

def test_engine_initialization(source_path):
    """
    Test that the engine initializes with the correct path.
    """
    engine = EvolutionEngine(source_path)
    assert engine.source_path == os.path.abspath(source_path)

# We mock ALL agents to prevent them from running real logic during the test
@patch("core.engine.Optimizer")
@patch("core.engine.Critic")
@patch("core.engine.Builder")
@patch("core.engine.SpecWriter")
def test_engine_start_generates_initial_draft(
    mock_spec_writer_cls, 
    mock_builder_cls, 
    mock_critic_cls, 
    mock_optimizer_cls, 
    source_path
):
    """
    Test that start() reads the source code and calls the writer for an initial draft.
    """
    # 1. Setup Mocks
    mock_writer_instance = mock_spec_writer_cls.return_value
    mock_writer_instance.initial_draft.return_value = "# Initial Spec"
    
    # Mock the Critic to return a 'fail' or 'pass' report so the loop can proceed or stop
    # If we want to test just the first iteration, we can make it fail or pass.
    mock_critic_instance = mock_critic_cls.return_value
    mock_critic_instance.evaluate.return_value = {"score": 0.0, "pass": False, "failures": []}

    mock_builder_instance = mock_builder_cls.return_value
    mock_builder_instance.build.return_value = "def candidate(): pass"

    # 2. Initialize Engine
    engine = EvolutionEngine(source_path)

    # 3. Execute the loop (limit to 1 iteration for this test)
    engine.start(max_iterations=1)

    # 4. Assertions
    # Verify that the writer was asked to draft the spec
    # It should be called with the content of our dummy file ("def run(): pass")
    mock_writer_instance.initial_draft.assert_called_once_with("def run(): pass")
    
    # Verify that the builder was called with the generated spec
    mock_builder_instance.build.assert_called_once_with("# Initial Spec")