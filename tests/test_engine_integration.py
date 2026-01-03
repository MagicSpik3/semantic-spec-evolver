import os
import pytest
import shutil
import re
from unittest.mock import patch
from core.engine import EvolutionEngine
from tests.spss_scripts import BASIC_DATA_GENERATOR

def validate_mermaid_syntax(markdown_content):
    """
    Simple heuristic check to ensure a mermaid block exists and looks valid.
    """
    pattern = r"```mermaid\n(.*?)\n```"
    match = re.search(pattern, markdown_content, re.DOTALL)
    
    if not match:
        return False, "No mermaid code block found."
    
    diagram_code = match.group(1).strip()
    
    if not re.match(r"^(graph|flowchart)\s+[A-Z]{2}", diagram_code):
        return False, f"Invalid Mermaid header. Got: {diagram_code.splitlines()[0]}"
        
    if "-->" not in diagram_code and "---" not in diagram_code:
        return False, "Diagram contains no connections."

    return True, "Valid"

@pytest.mark.skipif(shutil.which("pspp") is None, reason="PSPP executable not found")
def test_engine_full_iteration_with_diagram_check(tmp_path):
    # 1. Setup Repo
    repo_dir = tmp_path / "integration_test_repo"
    repo_dir.mkdir()
    
    sps_filename = "data_generator.sps"
    output_filename = "real_output.csv"
    sps_content = BASIC_DATA_GENERATOR.format(output_filename=output_filename)
    (repo_dir / sps_filename).write_text(sps_content)

    # 2. Mock the Spec Content (Defined INSIDE the function)
    mock_spec_content = """
# Technical Spec

## Executive Summary
This script generates data.

## Architecture
```mermaid
graph TD;
    A[Start] --> B{Generate Data};
    B --> C[Save CSV];

```
"""

    # 3. Initialize Engine with Patches
    # We patch SpecWriter to inject our mock spec.
    # We patch Builder/Critic/Optimizer so we don't need their real logic yet.
    with patch("core.engine.SpecWriter") as MockWriterCls, \
        patch("core.engine.Builder"), \
        patch("core.engine.Critic"), \
        patch("core.engine.Optimizer"):
        
        # Configure the Mock Writer
        mock_writer_instance = MockWriterCls.return_value
        mock_writer_instance.initial_draft.return_value = mock_spec_content

        print(f"\n🧪 Running Full Integration Test in: {repo_dir}")
        engine = EvolutionEngine(repo_path=str(repo_dir))
        
        # 4. Trigger the Loop
        engine.start(max_iterations=1)

        # 5. Locate the Output
        # We assume the engine saves to 'history' in the CWD.
        history_dir = os.path.join(os.getcwd(), "history")
        assert os.path.exists(history_dir), "History directory was not created."
        
        # Find latest run (filtering for the one we just made)
        all_runs = sorted([d for d in os.listdir(history_dir) if d.startswith("run_")])
        assert len(all_runs) > 0, "No run folder created."
        
        latest_run = os.path.join(history_dir, all_runs[-1])
        iter_path = os.path.join(latest_run, "iteration_01")
        spec_path = os.path.join(iter_path, "spec.md")
        
        assert os.path.exists(spec_path), "spec.md was not saved."

        # 6. Validate Content
        saved_content = open(spec_path).read()
        assert "Executive Summary" in saved_content
        
        is_valid, msg = validate_mermaid_syntax(saved_content)
        assert is_valid, f"Mermaid Diagram Validation Failed: {msg}"
        
        print("✅ Integration Test Passed: Spec saved with valid Mermaid diagram.")
