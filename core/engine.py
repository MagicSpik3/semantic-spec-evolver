import os
import time
import json
from datetime import datetime
from utils.llm_client import LLMClient
from core.critic import Critic

# We will import the agent prompts in the next step, 
# but for now, we'll placeholder them to get the logic working.
from core.spec_writer import SpecWriter
from core.builder import Builder
from core.optimizer import Optimizer

class EvolutionEngine:
    def __init__(self, source_path):
        self.source_path = source_path
        self.llm = LLMClient() 
        self.critic = Critic(source_path)
        
        # Initialize Agents
        self.spec_writer = SpecWriter(self.llm)
        self.builder = Builder(self.llm)
        self.optimizer = Optimizer(self.llm)

    def start(self, max_iterations=5):
        # 1. Setup History Directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join("history", f"run_{timestamp}")
        os.makedirs(run_dir, exist_ok=True)
        print(f"🚀 Starting Evolution Run: {run_dir}")

        # 2. Load Ground Truth Code
        with open(self.source_path, 'r') as f:
            source_code = f.read()

        current_spec = ""
        last_failure_digest = None

        # 3. The Evolution Loop
        for i in range(1, max_iterations + 1):
            iter_dir = os.path.join(run_dir, f"iteration_{i:02d}")
            os.makedirs(iter_dir, exist_ok=True)
            print(f"\n--- Cycle {i} ---")

            # --- Step A: Write/Evolve Spec ---
            if i == 1:
                print("📝 Drafting Initial Spec...")
                current_spec = self.spec_writer.initial_draft(source_code)
            else:
                print("🧬 Evolving Spec...")
                current_spec = self.optimizer.evolve(current_spec, last_failure_digest)
            
            self._save_artifact(iter_dir, "spec.md", current_spec)

            # --- Step B: Build Code ---
            print("🔨 Building Candidate Code...")
            candidate_code = self.builder.build(current_spec)
            
            # Save code so the Critic can load it
            code_path = os.path.join