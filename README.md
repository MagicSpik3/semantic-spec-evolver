### File: `README.md`

```markdown
# Semantic Spec Evolver
**A Self-Correcting "Round-Trip" Logic Extraction Engine**

## 1. The Core Concept
This project solves the "Ground Truth" problem in LLM prompt engineering. 
Most prompt optimization systems rely on subjective evaluation ("Is this output good?"). 
**Semantic Spec Evolver** relies on objective **Behavioral Equivalence**.

### The "Round-Trip" Test
We prove a Natural Language Specification is "perfect" if a blind agent can use it to reconstruct the original code's behavior exactly.

1.  **Reverse Engineering:** LLM reads `Legacy Code` $\to$ writes `English Spec`.
2.  **Blind Reconstruction:** Different LLM reads `English Spec` (without seeing code) $\to$ writes `New Code`.
3.  **The "Critic":** We run `Legacy Code` vs `New Code` on random inputs.
4.  **Evolution:** If outputs mismatch, the **Optimizer** refines the `English Spec` based on the specific failure.

---

## 2. Architecture



[Image of closed loop control system diagram]


The system operates as a closed feedback loop:

* **The Source (Ground Truth):** The legacy logic we want to capture (`sandbox/source_logic.py`).
* **The Generator (Spec Writer):** Extracts the initial spec.
* **The Actor (Blind Builder):** Attempts to build code from the spec alone.
* **The Judge (Critic):** Compares behavior (Input $\to$ Output) of Source vs. Actor.
* **The Fixer (Optimizer):** Analyzes the Judge's report and evolves the Spec.

---

## 3. Project Structure

The repository is organized to separate the **Generic Engine** from the **Specific Problem**.

```text
semantic-spec-evolver/
├── core/                           # THE BRAIN (Generic Logic)
│   ├── engine.py                   # The Orchestrator. Manages the loop and "History" folders.
│   ├── critic.py                   # The Judge. Compares Source vs Candidate execution.
│   ├── spec_writer.py              # (Pending) Prompt: Code -> Spec
│   ├── builder.py                  # (Pending) Prompt: Spec -> Code
│   └── optimizer.py                # (Pending) Prompt: Spec + Error -> New Spec
│
├── sandbox/                        # THE TEST CASE (Specific Problem)
│   ├── source_logic.py             # The Legacy Code we are trying to clone.
│   └── interface_adapter.py        # Wrapper that standardizes inputs/outputs for the Critic.
│
├── utils/                          # INFRASTRUCTURE
│   └── llm_client.py               # Wrapper for Ollama/OpenAI. Handles retry logic.
│
├── history/                        # THE VINTAGE (Artifacts)
│   └── run_YYYYMMDD_HHMMSS/        # A self-contained log of an evolution run.
│       ├── iteration_01/
│       │   ├── spec.md             # The prompt used.
│       │   ├── candidate.py        # The code generated.
│       │   └── report.json         # The pass/fail score.
│       └── ...
│
├── tests/                          # UNIT TESTS
│   ├── test_critic.py              # Verifies the comparator works.
│   ├── test_engine.py              # Verifies folder creation and flow.
│   └── test_llm_client.py          # Verifies API connectivity.
│
├── .gitignore                      # Excludes venv/ and history/
└── README.md                       # This file.

```

---

## 4. Current Status (Phase 1 Complete)

* **[x] Infrastructure:** The `EvolutionEngine` correctly manages the loop and file history.
* **[x] Evaluation:** The `Critic` can dynamically load two Python files and compare their outputs.
* **[x] AI Connection:** The `LLMClient` successfully talks to a local Ollama instance (Qwen2.5-Coder).
* **[x] Testing:** The test suite passes (5/5 tests), confirming mocks and file operations work.

---

## 5. Roadmap

### Phase 2: The Agents (Next Step)

We need to implement the actual prompts for the three agents. Currently, they are mocked in tests.

1. **`SpecWriter`:** System prompt to extract logic without implementation details.
2. **`Builder`:** System prompt to write strict Python from English text.
3. **`Optimizer`:** The complex prompt that takes a `Failure Digest` and rewrites the spec.

### Phase 3: The Entry Point

Create `main.py` to allow running the tool from the command line:
`python main.py --source sandbox/source_logic.py --iterations 10`

### Phase 4: Generalization

Refactor `sandbox/` so users can plug in their own legacy code without changing the `core` engine.

```

---

### What We Are Doing Next

We are moving to **Phase 2: The Agents**.

We will implement the agents one by one, starting with **`core/spec_writer.py`**.
* **Goal:** A class that takes source code string and returns a Markdown spec.
* **Test:** A unit test verifying it constructs the prompt correctly and parses the LLM output.
