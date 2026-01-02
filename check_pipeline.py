
import os
from core.spec_writer import SpecWriter
from utils.llm_client import LLMClient

def run_check():
    # 1. Load the "Arbitrarily Simple" Logic
    source_path = "sandbox/squaring_logic.py"
    if not os.path.exists(source_path):
        print(f"❌ Source file not found: {source_path}")
        return

    with open(source_path, 'r') as f:
        code_content = f.read()

    # 2. Initialize the Writer Agent
    # Ensure your Ollama is running! 
    # (ollama run qwen2.5-coder:latest)
    client = LLMClient(model="qwen2.5-coder:latest") 
    writer = SpecWriter(client)

    print("🧠 Reading code and generating Spec with Diagram...")
    
    # 3. Generate
    spec = writer.initial_draft(code_content)

    # 4. Save and Show
    output_file = "generated_spec.md"
    with open(output_file, 'w') as f:
        f.write(spec)

    print(f"\n✅ Spec generated: {output_file}")
    print("="*40)
    print(spec)
    print("="*40)

if __name__ == "__main__":
    run_check()