import os
import time
import json
import shutil
from datetime import datetime

# Import the Real Agents
from core.spec_writer import SpecWriter
from core.builder import Builder
from core.critic import Critic
from core.optimizer import Optimizer
from utils.llm_client import LLMClient

class EvolutionEngine:
    def __init__(self, source_path: str):
        self.source_path = os.path.abspath(source_path)
        self.llm_client = LLMClient(temperature=0.0) # Zero temp for repeatability
        
        # Initialize Agents
        self.writer = SpecWriter(self.llm_client)
        self.builder = Builder(self.llm_client)
        self.critic = Critic(self.source_path)
        self.optimizer = Optimizer(self.llm_client)

        # Setup History
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = os.path.join("history", f"run_{timestamp}")
        os.makedirs(self.run_dir, exist_ok=True)

    def start(self, max_iterations=5):
        print(f"🚀 Starting Evolution Loop for: {os.path.basename(self.source_path)}")
        
        # 1. Read Source Code
        with open(self.source_path, 'r') as f:
            source_code = f.read()

        current_spec = None
        
        for i in range(1, max_iterations + 1):
            iter_dir = os.path.join(self.run_dir, f"iteration_{i:02d}")
            os.makedirs(iter_dir, exist_ok=True)
            
            print(f"\n--- Iteration {i}/{max_iterations} ---")
            
            # ------------------------------------------------------------------
            # STEP 1: GENERATE / EVOLVE SPEC
            # ------------------------------------------------------------------
            if i == 1:
                print("📝 SpecWriter: Drafting initial v1...")
                current_spec = self.writer.initial_draft(source_code)
            else:
                # Load previous failure report
                prev_report_path = os.path.join(self.run_dir, f"iteration_{i-1:02d}", "report.json")
                with open(prev_report_path, 'r') as f: prev_report = json.load(f)
                
                print("🔧 Optimizer: Refining spec based on failures...")
                current_spec = self.optimizer.evolve(current_spec, prev_report)

            # Save Spec
            spec_path = os.path.join(iter_dir, "spec.md")
            with open(spec_path, 'w') as f: f.write(current_spec)

            # ------------------------------------------------------------------
            # STEP 2: BUILD CANDIDATE
            # ------------------------------------------------------------------
            print("👷 Builder: Implementing code from spec...")
            candidate_code = self.builder.build(current_spec)
            
            # Save Candidate
            candidate_path = os.path.join(iter_dir, "candidate.py")
            with open(candidate_path, 'w') as f: f.write(candidate_code)

            # ------------------------------------------------------------------
            # STEP 3: CRITIQUE (THE COST FUNCTION)
            # ------------------------------------------------------------------
            print("⚖️  Critic: Running behavioral comparison...")
            report = self.critic.evaluate(candidate_path)
            
            # Save Report
            report_path = os.path.join(iter_dir, "report.json")
            with open(report_path, 'w') as f: json.dump(report, f, indent=2)

            # ------------------------------------------------------------------
            # STEP 4: EVALUATE COST
            # ------------------------------------------------------------------
            score = report.get("score", 0.0)
            cost = 1.0 - score
            
            print(f"   📊 Score: {score:.2f} | Cost: {cost:.2f}")
            
            if report.get("pass"):
                print(f"✅ SUCCESS! Behavioral Equivalence Achieved in {i} iterations.")
                print(f"   Artifacts: {iter_dir}")
                return True
            else:
                print(f"   ❌ Failures: {len(report.get('failures', []))}")
                for fail in report.get("failures", [])[:3]: # Show top 3
                    print(f"      - {fail}")

        print("\n⏹️  Max iterations reached. Optimization failed.")
        return False