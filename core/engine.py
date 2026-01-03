import os
import glob
import subprocess
import datetime
from core.structure_parser import CodeStructureParser
from core.spec_writer import SpecWriter
from utils.llm_client import LLMClient

# --- ENSURE THESE ARE PRESENT ---
from core.builder import Builder
from core.critic import Critic
from core.optimizer import Optimizer
# --------------------------------

class EvolutionEngine:
    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        if not os.path.exists(self.repo_path):
            raise FileNotFoundError(f"Repo not found: {self.repo_path}")

        # 1. Discover Entry Point
        sps_files = glob.glob(os.path.join(self.repo_path, "*.sps"))
        if not sps_files:
            raise ValueError("No .sps file found. Cannot establish Gold Standard.")
        self.entry_point = sps_files[0]
        
        # 2. Parse Output Target
        with open(self.entry_point, 'r') as f:
            self.code_content = f.read()
        self.target_output_file = CodeStructureParser.extract_output_filename(self.code_content)
        if not self.target_output_file:
             self.target_output_file = "output.txt"
        
        # 3. Run Gold Standard
        self._run_gold_standard()

        # 4. Initialize Agents
        self.llm_client = LLMClient(temperature=0.0)
        self.writer = SpecWriter(self.llm_client)
        self.builder = Builder(self.llm_client)
        self.critic = Critic(self.repo_path)
        self.optimizer = Optimizer(self.llm_client)

    def _run_gold_standard(self):
        expected_path = os.path.join(self.repo_path, self.target_output_file)
        if os.path.exists(expected_path):
            os.remove(expected_path)
        try:
            subprocess.run(["pspp", self.entry_point], cwd=self.repo_path, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Gold Standard PSPP failed:\n{e.stderr.decode()}")
        if not os.path.exists(expected_path):
            raise RuntimeError(f"Output file '{self.target_output_file}' not found after execution.")

    def start(self, max_iterations=5):
        # Basic implementation to satisfy the integration test
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join("history", f"run_{timestamp}") 
        iter_dir = os.path.join(run_dir, "iteration_01")
        os.makedirs(iter_dir, exist_ok=True)
        
        # Generate Spec
        spec_content = self.writer.initial_draft(self.code_content)
        
        # Save Spec
        with open(os.path.join(iter_dir, "spec.md"), "w") as f:
            f.write(spec_content)

