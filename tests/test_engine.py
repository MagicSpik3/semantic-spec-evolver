# tests/test_engine.py
import os
import shutil
import pytest
from unittest.mock import patch, MagicMock
from core.engine import EvolutionEngine

@pytest.fixture
def mock_repo(tmp_path):
    """
    Creates a temporary directory acting as a repo with a dummy .sps file.
    """
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    
    # Create the SPSS file
    sps_file = repo_dir / "pipeline.sps"
    sps_file.write_text("SAVE TRANSLATE /OUTFILE='gold.csv'.")
    
    # We DO NOT create gold.csv here anymore, or if we do, the engine deletes it.
    # The subprocess mock must recreate it.
    
    yield str(repo_dir)

@patch("core.engine.subprocess.run")
@patch("core.engine.SpecWriter")
@patch("core.engine.LLMClient")
def test_engine_initialization_and_gold_standard(
    mock_llm, 
    mock_spec_writer, 
    mock_subprocess, 
    mock_repo
):
    """
    Verifies that the engine:
    1. Finds the .sps file.
    2. Parses 'gold.csv'.
    3. Calls 'pspp'.
    4. Verifies output creation.
    """
    
    # --- FIX: DEFINE SIDE EFFECT ---
    def recreate_gold_file(*args, **kwargs):
        # Simulate PSPP creating the file
        gold_path = os.path.join(mock_repo, "gold.csv")
        with open(gold_path, 'w') as f:
            f.write("id,val\n1,100")
        return MagicMock(returncode=0)

    mock_subprocess.side_effect = recreate_gold_file
    # -------------------------------

    # Initialize Engine
    engine = EvolutionEngine(repo_path=mock_repo)
    
    # Assertions
    assert engine.repo_path == mock_repo
    assert engine.target_output_file == "gold.csv"
    
    # Verify Subprocess was called
    mock_subprocess.assert_called_once()
    args, kwargs = mock_subprocess.call_args
    assert args[0][0] == "pspp"
    assert kwargs['cwd'] == mock_repo

def test_engine_fails_if_no_sps_file(tmp_path):
    """
    Engine should raise ValueError if the repo is empty.
    """
    empty_repo = tmp_path / "empty"
    empty_repo.mkdir()
    
    with pytest.raises(ValueError, match="No .sps file found"):
        EvolutionEngine(str(empty_repo))