
from utils.llm_client import LLMClient
from core.prompts import SPEC_WRITER_V1

class SpecWriter:
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()

    def initial_draft(self, source_code: str, prompt_template: str = SPEC_WRITER_V1) -> str:
        """
        Analyses the source code and produces a Spec.
        
        Args:
            source_code: The raw code string.
            prompt_template: The system prompt to use (defaults to V1).
        """
        user_prompt = f"### SOURCE CODE TO ANALYZE:\n```python\n{source_code}\n```"
        
        # We pass the template dynamically
        return self.llm.complete(prompt_template, user_prompt, temperature=0.1)
