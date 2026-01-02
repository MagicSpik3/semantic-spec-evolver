
import os
import shutil
import pandas as pd
from core.engine import EvolutionEngine
from core.data_profiler import DataProfiler

# Hardcoded Configuration
SOURCE_REPO = "sandbox/spss_repo"  # Where your .sps and .csvs live
TARGET_REPO = "migrated_repo"      # Where we want the new R/Python code
TARGET_LANG = "Python"             # Or "R"

def setup_demo_environment():
    """Sets up a mock SPSS repo with data for testing."""
    if os.path.exists(SOURCE_REPO): shutil.rmtree(SOURCE_REPO)
    os.makedirs(SOURCE_REPO)
    
    # 1. The Input Data (Age, Weight, Height)
    input_csv = os.path.join(SOURCE_REPO, "patients.csv")
    with open(input_csv, 'w') as f:
        f.write("id,age,weight_kg,height_m\n1,25,70,1.75\n2,30,90,1.80\n3,45,60,1.65")
        
    # 2. The Legacy Code (SPSS)
    # Note: We assume this matches the logic of "Calculate BMI"
    spss_code = os.path.join(SOURCE_REPO, "logic.sps")
    with open(spss_code, 'w') as f:
        f.write("""
GET DATA /TYPE=TXT /FILE='patients.csv' /DELCASE=LINE /DELIMITERS="," /ARRANGEMENT=DELIMITED /FIRSTCASE=2 /VARIABLES=id F3 age F3 weight_kg F3 height_m F4.2.
COMPUTE bmi = weight_kg / (height_m * height_m).
SAVE OUTFILE='results.csv' /KEEP=id,bmi.
EXECUTE.
""")

    # 3. The "Proven" Output (We simulate running PSPP by pre-calculating it)
    # The SpecWriter needs to see this exists to verify the logic!
    output_csv = os.path.join(SOURCE_REPO, "results.csv")
    df = pd.read_csv(input_csv)
    df['bmi'] = df['weight_kg'] / (df['height_m'] ** 2)
    df[['id', 'bmi']].to_csv(output_csv, index=False)
    
    print(f"✅ Environment Set: {SOURCE_REPO} (Contains Code + Input + Proven Output)")

def main():
    # 1. Setup (or point to real repo)
    setup_demo_environment()
    
    # 2. Locate Artifacts
    # In a real run, you'd use the Ingestor to find these dynamically
    spss_file = os.path.join(SOURCE_REPO, "logic.sps")
    input_file = os.path.join(SOURCE_REPO, "patients.csv")
    output_file = os.path.join(SOURCE_REPO, "results.csv")
    
    # 3. Gather Forensics (The Architect looks at the files)
    print("\n🔍 Phase 1: Gathering Forensics...")
    profiler = DataProfiler()
    context = profiler.sniff(input_file) + "\n" + profiler.sniff(output_file)
    print(context)
    
    # 4. Initialize Engine targeting the NEW location
    # We pass the 'context' into the engine so the SpecWriter can use it
    engine = EvolutionEngine(
        source_path=spss_file,
        data_context=context,
        target_lang=TARGET_LANG,
        workspace_dir=TARGET_REPO
    )
    
    # 5. Run the Evolution Loop
    success = engine.start(max_iterations=3)
    
    if success:
        print(f"\n🎉 Migration Complete! New pipeline is in: {TARGET_REPO}")
        print("   Verified: The new code produces identical CSVs to the legacy SPSS.")

if __name__ == "__main__":
    main()