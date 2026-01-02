import os
import json
from datetime import datetime
from utils.llm_client import LLMClient
from core.critic import Critic

# Placeholder imports (we will implement these next)
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
            code_path = os.path.join(iter_dir, "candidate.py")
            with open(code_path, 'w') as f:
                f.write(candidate_code)

            # --- Step C: Criticize ---
            print("🕵️  Running Critic...")
            report = self.critic.evaluate(code_path)
            self._save_artifact(iter_dir, "report.json", json.dumps(report, indent=2))

            if report["pass"]:
                print(f"✅ SUCCESS! Logic matched in iteration {i}.")
                break
            
            print(f"❌ Failed (Score: {report['score']}). Preparing feedback...")
            # Extract simple failures for the Optimizer
            last_failure_digest = [f for f in report["failures"]][:3] # Top 3 errors

        print("\nRun Complete.")

    def _save_artifact(self, folder, filename, content):
        """Helper to save string content to a file."""
        with open(os.path.join(folder, filename), 'w') as f:
            f.write(content)