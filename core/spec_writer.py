# core/spec_writer.py
from utils.llm_client import LLMClient
from core.prompts import SPEC_WRITER_SYSTEM_PROMPT

class SpecWriter:
    def __init__(self, llm_client=None):
        # Allow dependency injection or default to new client
        self.llm = llm_client if llm_client else LLMClient()

    def generate_spec(self, context, qa_history):
        """
        Generates a spec from Context + Q&A (Used in initial Q&A phase).
        """
        qa_block = ""
        for item in qa_history:
            qa_block += f"Q: {item['question']}\nA: {item['answer']}\n---\n"

        user_prompt = (
            f"=== USER CONTEXT ===\n{context}\n\n"
            f"=== Q&A HISTORY ===\n{qa_block}\n\n"
            f"Please generate the specification now."
        )

        return self.llm.complete(
            system_prompt=SPEC_WRITER_SYSTEM_PROMPT,
            user_prompt=user_prompt
        )

    def initial_draft(self, source_code):
        """
        Generates a spec from Source Code (Used in EvolutionEngine).
        """
        system_prompt = (
            "You are an expert technical writer. "
            "Analyze the provided source code and write a comprehensive "
            "technical specification that describes its functionality, "
            "architecture, and logic."
        )
        
        user_prompt = f"SOURCE CODE:\n```python\n{source_code}\n```"

        return self.llm.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )