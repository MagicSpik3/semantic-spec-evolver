import csv

def process_data(input_path, output_path):
    """
    1. Reads a CSV file with a header.
    2. Detects if the 'value' column is numeric.
    3. If numeric, squares it. Otherwise, keeps it as is.
    4. Saves the result to a new CSV.
    """
    results = []
    
    with open(input_path, 'r') as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            raw_val = row.get('value', '')
            
            # Logic: Type detection and transformation
            try:
                # Attempt to parse as float (covers integers too)
                numeric_val = float(raw_val)
                processed_val = numeric_val ** 2
            except ValueError:
                # Not a number? Keep original.
                processed_val = raw_val
            
            results.append({'original': raw_val, 'squared': processed_val})

    # Save output
    with open(output_path, 'w', newline='') as f_out:
        fieldnames = ['original', 'squared']
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)