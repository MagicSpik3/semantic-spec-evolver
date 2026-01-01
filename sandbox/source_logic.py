import csv
import os

def process_data(input_path, output_path):
    """
    The GROUND TRUTH logic.
    1. Reads a CSV.
    2. Column 'A' must be an integer.
    3. If 'A' is even, square it.
    4. If 'A' is odd, keep it as is.
    5. Write result to output.
    """
    results = []
    with open(input_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            val = int(row['value'])
            
            # The "Hidden" Logic we hope the spec catches
            if val % 2 == 0:
                new_val = val ** 2
            else:
                new_val = val
            
            results.append({'original': val, 'processed': new_val})

    # Write output
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['original', 'processed'])
        writer.writeheader()
        writer.writerows(results)