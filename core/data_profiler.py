import pandas as pd
import os

class DataProfiler:
    """
    The Forensic Analyst.
    Reads input/output artifacts to give the SpecWriter 'Ground Truth' on what actually changed.
    """
    
    def sniff(self, file_path: str) -> str:
        """Returns a markdown summary of the CSV: Columns, Types, and Head."""
        if not os.path.exists(file_path):
            return f"(File not found: {os.path.basename(file_path)})"

        try:
            # Read only first 5 rows to save tokens and time
            df = pd.read_csv(file_path, nrows=5)
            
            summary = f"### File: {os.path.basename(file_path)}\n"
            summary += f"- **Shape:** {df.shape[0]} rows (sample) x {df.shape[1]} columns\n"
            summary += f"- **Columns:** {', '.join(list(df.columns))}\n"
            summary += "- **Data Sample:**\n"
            summary += df.to_markdown(index=False)
            return summary
        except Exception as e:
            return f"(Error reading {os.path.basename(file_path)}: {e})"