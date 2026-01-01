import requests
import logging

# Configure logger
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, provider="ollama", model="qwen2.5-coder:latest", endpoint="http://localhost:11434/api/generate"):
        self.provider = provider
        self.model = model
        self.endpoint = endpoint

    def complete(self, system_prompt, user_prompt, temperature=0.0):
        """
        Sends a request to the local Ollama instance.
        Combines system and user prompts since the /api/generate endpoint takes a single string.
        """
        # Combine prompts to fit the simple /api/generate format
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        logger.info(f"Sending request to Ollama (Model: {self.model})...")

        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 2000  # Increased token limit for complex specs
            }
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=120  # Generous timeout for local inference
            )
            response.raise_for_status()

            response_data = response.json()
            raw_text = response_data.get("response", "").strip()

            return self._clean_markdown(raw_text)

        except requests.exceptions.RequestException as e:
            error_msg = f"Ollama Connection Error: {e}"
            logger.error(error_msg)
            # Return a comment so the pipeline doesn't crash, but the failure is visible
            return f"# ERROR: {error_msg}"
    
    def _clean_markdown(self, text):
        """
        Removes markdown code fences (```) if present.
        Crucial because Qwen/Llama often wrap code in these blocks.
        """
        if text.startswith("```"):
            lines = text.splitlines()
            # Remove first line if it's a backtick fence (e.g., ```python)
            if lines[0].startswith("```"):
                lines = lines[1:]
            # Remove last line if it's a backtick fence
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return text