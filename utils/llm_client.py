# core/llm_client.py
import requests
import logging

# Configure logger
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, 
                 provider="ollama", 
                 model="qwen2.5-coder:latest", 
                 endpoint="http://localhost:11434/api/generate",
                 temperature=0.0): # Centralized Default
        
        self.provider = provider
        self.model = model
        self.endpoint = endpoint
        self.temperature = temperature

    def complete(self, system_prompt, user_prompt, temperature=None):
        """
        Sends a request to the LLM.
        
        Args:
            system_prompt: The instruction set.
            user_prompt: The specific task content.
            temperature: (Optional) Override the default temperature.
        """
        # Use instance default if no specific override is provided
        temp_setting = temperature if temperature is not None else self.temperature
        
        # Combine prompts for simple API endpoints
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        logger.info(f"Sending request to Ollama (Model: {self.model}, Temp: {temp_setting})...")

        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temp_setting,
                "num_predict": 4000  # Increased window for full file generation
            }
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            response_data = response.json()
            raw_text = response_data.get("response", "").strip()

            return self._clean_markdown(raw_text)

        except requests.exceptions.RequestException as e:
            error_msg = f"Ollama Connection Error: {e}"
            logger.error(error_msg)
            return f"# ERROR: {error_msg}"
    
    def _clean_markdown(self, text):
        """Removes markdown code fences (```) if present."""
        if "```" in text:
            lines = text.splitlines()
            # Remove start fence
            if lines[0].strip().startswith("```"):
                lines = lines[1:]
            # Remove end fence
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return text