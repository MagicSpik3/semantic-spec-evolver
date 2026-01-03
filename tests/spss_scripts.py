# tests/spss_scripts.py

# A basic script that creates data and exports it.
# Contains a placeholder {output_filename} for dynamic testing.
BASIC_DATA_GENERATOR = """
* Define raw data inline.
DATA LIST LIST /id (F) score (F).
BEGIN DATA
1 50
2 75
3 99
END DATA.

* Export to CSV (The engine must find this filename).
SAVE TRANSLATE /OUTFILE='{output_filename}' /TYPE=CSV /REPLACE.
"""

# You can add more scripts here later, e.g.:
# MISSING_EXPORT_SCRIPT = "..."
# SYNTAX_ERROR_SCRIPT = "..."