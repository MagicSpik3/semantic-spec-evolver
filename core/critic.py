import importlib.util
import os
import json
from sandbox.interface_adapter import SandboxAdapter

class Critic:
    def __init__(self, source_path):
        self.source_module = self._load_module("source_logic", source_path)
        self.adapter = SandboxAdapter()

    def _load_module(self, name, path):
        """Dynamically loads a python module from a file path."""
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def evaluate(self, candidate_path, num_trials=5):
        """
        Runs the Source vs Candidate on 'num_trials' random inputs.
        Returns a structured Report.
        """
        results = {
            "pass": True,
            "score": 0.0,
            "failures": []
        }
        
        try:
            candidate_module = self._load_module("candidate_logic", candidate_path)
        except Exception as e:
            results["pass"] = False
            results["failures"].append({"type": "Syntax/Import Error", "details": str(e)})
            return results

        passed_count = 0

        for i in range(num_trials):
            # 1. Generate Input
            test_input = self.adapter.generate_input()
            
            # 2. Run Ground Truth
            ground_truth = self.adapter.run_trial(self.source_module.process_data, test_input)
            
            # 3. Run Candidate
            candidate_output = self.adapter.run_trial(candidate_module.process_data, test_input)
            
            # 4. Compare
            if ground_truth == candidate_output:
                passed_count += 1
            else:
                results["pass"] = False
                results["failures"].append({
                    "trial_index": i,
                    "input_value": test_input,
                    "expected": ground_truth,
                    "actual": candidate_output
                })

        results["score"] = passed_count / num_trials
        return results