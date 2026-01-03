# core/structure_parser.py
import re

class CodeStructureParser:
    """
    Parses code to identify structure and metadata.
    """
    
    PATTERNS = {
        "INPUT": r"(GET DATA|MATCH FILES|ADD FILES|IMPORT)",
        "TRANSFORM": r"(COMPUTE|RECODE|IF|DO IF|AGGREGATE)",
        "ANALYSIS": r"(DESCRIPTIVES|FREQUENCIES|CROSSTABS|CORRELATIONS|REGRESSION)",
        "OUTPUT": r"(SAVE TRANSLATE|WRITE|EXPORT|SAVE)"
    }

    @staticmethod
    def extract_output_filename(code: str) -> str | None:
        """
        Scans SPSS code for output file definitions.
        Targeting: /OUTFILE='filename' or /FILE="filename"
        """
        # Regex explanation:
        # 1. Look for /OUTFILE or /FILE (case insensitive)
        # 2. Allow optional equals sign and whitespace
        # 3. Capture content inside single or double quotes
        regex = r"/(?:OUTFILE|FILE)\s*=\s*['\"]([^'\"]+)['\"]"
        
        match = re.search(regex, code, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def parse_spss(code: str):
        """Returns structured blocks (imports, logic, exports)."""
        blocks = []
        lines = code.splitlines()
        current_block = {"type": "UNKNOWN", "content": []}
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("*"): 
                continue 

            matched_type = None
            for key, pattern in CodeStructureParser.PATTERNS.items():
                if re.match(pattern, line, re.IGNORECASE):
                    matched_type = key
                    break
            
            if matched_type:
                if current_block["content"]:
                    blocks.append(current_block)
                current_block = {"type": matched_type, "content": [line]}
            else:
                current_block["content"].append(line)
        
        if current_block["content"]:
            blocks.append(current_block)
            
        return blocks