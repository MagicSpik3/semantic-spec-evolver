from utils.llm_client import LLMClient
from core.prompts import OPTIMIZER_V1

class Optimizer:
    """
    The Fixer Agent.
    Role: reads the Critic's report and rewrites the Spec to fix behavioral gaps.
    """
    
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()

    def evolve(self, current_spec: str, critique_report: dict, prompt_template: str = OPTIMIZER_V1) -> str:
        """
        Rewrites the spec to address failures.
        
        Args:
            current_spec: The Markdown string of the failed spec.
            critique_report: The dictionary returned by Critic.evaluate().
        """
        # Format the failures into a readable string
        failures_text = "\n".join([f"- {f}" for f in critique_report.get("failures", [])])
        
        user_prompt = f"""
### CONTEXT:
The previous spec failed to produce correct code.

### ORIGINAL SPEC:
{current_spec}

### CRITICAL FAILURES (QA REPORT):
{failures_text}

### TASK:
Rewrite the spec to prevent these failures.
"""
        return self.llm.complete(prompt_template, user_prompt)