import csv
import os
import random
import tempfile

class SandboxAdapter:
    """
    Handles the messy details of creating CSVs, passing them to functions,
    and reading the results back.
    """

    def generate_input(self):
        """Generates a random integer for the test case."""
        # Simple int generator for our specific 'square the number' logic
        return random.randint(1, 100)

    def run_trial(self, logic_func, input_val):
        """
        1. Creates a temp input CSV with the 'input_val'.
        2. Runs the 'logic_func' (Source or Candidate).
        3. Reads the temp output CSV.
        4. Returns the structured data.
        """
        # A. Setup Temp Files
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f_in:
            input_path = f_in.name
            writer = csv.DictWriter(f_in, fieldnames=['value'])
            writer.writeheader()
            writer.writerow({'value': input_val})
            
        # Output path (just a name)
        output_path = input_path.replace('.csv', '_out.csv')

        try:
            # B. EXECUTE THE LOGIC
            # We assume logic_func takes (input_path, output_path)
            logic_func(input_path, output_path)

            # C. Read Result
            if not os.path.exists(output_path):
                return {"error": "Output file not created"}
                
            with open(output_path, 'r') as f_out:
                reader = list(csv.DictReader(f_out))
                if not reader:
                    return {"error": "Output file empty"}
                return reader[0] # Return the first row dict
                
        except Exception as e:
            return {"error": str(e)}
        finally:
            # Cleanup
            if os.path.exists(input_path): os.remove(input_path)
            if os.path.exists(output_path): os.remove(output_path)