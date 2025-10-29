#!/usr/bin/env python3
"""
Pinnacle21 Validation Wrapper for Domino Flows
This script acts as a bridge between Domino Flows and the mock P21 validation bash script.
It accepts ADaM datasets as inputs and generates validation reports as outputs.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_p21_validation():
    """
    Run the Pinnacle21 validation mock script.
    This function expects ADaM datasets to be available in the workflow inputs
    and will generate validation reports in the workflow outputs.
    """
    
    print("=" * 60)
    print("Pinnacle21 Validation - Domino Flow Integration")
    print("=" * 60)
    print()
    
    # Define paths
    workflow_outputs = Path("/workflow/outputs")
    validation_script = Path("/mnt/code/prod/validation/mock_pinnacle21_validation.sh")
    
    # Create output directory if it doesn't exist
    workflow_outputs.mkdir(parents=True, exist_ok=True)
    
    # List of expected ADaM datasets
    expected_datasets = ['adsl', 'adae', 'adcm', 'adlb', 'admh', 'advs']
    
    print("Checking for ADaM datasets in workflow inputs...")
    for dataset in expected_datasets:
        dataset_path = Path(f"/workflow/inputs/{dataset}_dataset")
        if dataset_path.exists():
            print(f"  ✓ Found: {dataset.upper()}.sas7bdat")
        else:
            print(f"  ⚠ Warning: {dataset.upper()}.sas7bdat not found")
    print()
    
    # Check if validation script exists
    if not validation_script.exists():
        print(f"Error: Validation script not found at {validation_script}")
        print("Please ensure the mock_pinnacle21_validation.sh script is available.")
        sys.exit(1)
    
    # Make the script executable
    os.chmod(validation_script, 0o755)
    
    print("Running Pinnacle21 validation...")
    print()
    
    # Run the validation script
    try:
        # Change to the script directory
        script_dir = validation_script.parent
        
        # Run the bash script
        result = subprocess.run(
            [str(validation_script)],
            cwd=script_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Print the output
        print(result.stdout)
        
        if result.stderr:
            print("Warnings/Errors:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        
        # Copy validation reports to workflow outputs
        validation_reports_dir = script_dir / "validation_reports"
        
        if validation_reports_dir.exists():
            print()
            print("Copying validation reports to workflow outputs...")
            
            # Create a combined validation report
            pdf_files = list(validation_reports_dir.glob("*.pdf"))
            
            if pdf_files:
                # Copy individual reports
                for pdf_file in pdf_files:
                    dest_path = workflow_outputs / pdf_file.name
                    shutil.copy2(pdf_file, dest_path)
                    print(f"  ✓ Copied: {pdf_file.name}")
                
                # Create a summary report
                summary_path = workflow_outputs / "p21_validation_summary.txt"
                with open(summary_path, 'w') as f:
                    f.write("Pinnacle21 Validation Summary\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"Validation completed at: {validation_reports_dir}\n")
                    f.write(f"Total reports generated: {len(pdf_files)}\n\n")
                    f.write("Reports:\n")
                    for pdf_file in sorted(pdf_files):
                        f.write(f"  - {pdf_file.name}\n")
                
                print(f"  ✓ Created: p21_validation_summary.txt")
                print()
                print("=" * 60)
                print("Validation completed successfully!")
                print(f"Reports available in: {workflow_outputs}")
                print("=" * 60)
            else:
                print("Warning: No PDF reports were generated")
                sys.exit(1)
        else:
            print(f"Error: Validation reports directory not found: {validation_reports_dir}")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"Error running validation script: {e}", file=sys.stderr)
        print(f"Return code: {e.returncode}", file=sys.stderr)
        if e.stdout:
            print("STDOUT:", e.stdout, file=sys.stderr)
        if e.stderr:
            print("STDERR:", e.stderr, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_p21_validation()