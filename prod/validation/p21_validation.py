#!/usr/bin/env python3
"""
Pinnacle21 Validation Wrapper for Domino Flows
This script validates ADaM datasets against CDISC standards and generates PDF validation reports.
All validation logic is contained within this single Python script.

CRITICAL: Output filenames must match the Flow definition output_specs exactly!
"""

import os
import sys
import subprocess
import shutil
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class P21ValidationReport:
    """Generates mock Pinnacle21 validation reports using LaTeX."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def generate_validation_data(self, dataset: str, severity: str) -> Tuple[int, int, int]:
        """Generate mock validation issue counts based on severity level."""
        if severity == "clean":
            errors = 0
            warnings = random.randint(0, 2)
            notes = random.randint(1, 5)
        elif severity == "moderate":
            errors = random.randint(1, 3)
            warnings = random.randint(2, 9)
            notes = random.randint(5, 14)
        else:  # severe
            errors = random.randint(5, 14)
            warnings = random.randint(5, 19)
            notes = random.randint(10, 29)
        
        return errors, warnings, notes
    
    def generate_latex_content(self, dataset: str, errors: int, warnings: int, notes: int) -> str:
        """Generate LaTeX content for the validation report."""
        
        current_date = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
        date_short = datetime.now().strftime("%Y-%m-%d")
        
        latex_content = f"""\\documentclass[11pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{graphicx}}
\\usepackage{{xcolor}}
\\usepackage{{longtable}}
\\usepackage{{booktabs}}
\\usepackage{{fancyhdr}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\rhead{{Page \\thepage}}
\\lhead{{Pinnacle 21 Validation Report}}

\\definecolor{{errorcolor}}{{RGB}}{{220,53,69}}
\\definecolor{{warningcolor}}{{RGB}}{{255,193,7}}
\\definecolor{{notecolor}}{{RGB}}{{0,123,255}}

\\begin{{document}}

\\begin{{center}}
\\Large\\textbf{{Pinnacle 21 Community Validation Report}}\\\\
\\large\\textbf{{ADaM Dataset Validation}}\\\\
\\vspace{{0.3cm}}
\\normalsize Generated: {current_date}
\\end{{center}}

\\vspace{{0.5cm}}

\\section*{{Executive Summary}}

\\begin{{tabular}}{{ll}}
\\textbf{{Dataset:}} & {dataset} \\\\
\\textbf{{Standard:}} & CDISC ADaM v1.1 \\\\
\\textbf{{Validation Date:}} & {date_short} \\\\
\\textbf{{Validator Version:}} & Pinnacle 21 Community 4.1.0 \\\\
\\end{{tabular}}

\\vspace{{0.5cm}}

\\section*{{Validation Results}}

\\begin{{tabular}}{{lc}}
\\toprule
\\textbf{{Issue Type}} & \\textbf{{Count}} \\\\
\\midrule
\\textcolor{{errorcolor}}{{\\textbf{{Errors}}}} & {errors} \\\\
\\textcolor{{warningcolor}}{{\\textbf{{Warnings}}}} & {warnings} \\\\
\\textcolor{{notecolor}}{{\\textbf{{Notes}}}} & {notes} \\\\
\\midrule
\\textbf{{Total Issues}} & {errors + warnings + notes} \\\\
\\bottomrule
\\end{{tabular}}

\\vspace{{0.5cm}}

"""
        
        # Add error details if present
        if errors > 0:
            latex_content += """\\section*{Critical Errors}

\\begin{longtable}{p{2cm}p{3cm}p{8cm}}
\\toprule
\\textbf{Rule ID} & \\textbf{Variable} & \\textbf{Description} \\\\
\\midrule
\\endfirsthead
\\toprule
\\textbf{Rule ID} & \\textbf{Variable} & \\textbf{Description} \\\\
\\midrule
\\endhead
"""
            
            variables = ["PARAMCD", "AVAL", "AVISITN", "TRTP", "STUDYID", "USUBJID"]
            descriptions = [
                "Variable {} is required but missing from dataset",
                "Invalid value found in {} at record {}",
                "Variable {} does not conform to controlled terminology",
                "Missing label for variable {}",
                "Variable {} has incorrect data type (expected numeric)"
            ]
            
            for i in range(errors):
                rule_id = f"AD{random.randint(1, 999):04d}"
                var = random.choice(variables)
                desc_template = random.choice(descriptions)
                if "{}" in desc_template and desc_template.count("{}") > 1:
                    desc = desc_template.format(var, random.randint(1, 1000))
                else:
                    desc = desc_template.format(var)
                latex_content += f"{rule_id} & {var} & {desc} \\\\\n"
            
            latex_content += """\\bottomrule
\\end{longtable}

"""
        
        # Add warning details if present
        if warnings > 0:
            latex_content += """\\section*{Warnings}

\\begin{longtable}{p{2cm}p{3cm}p{8cm}}
\\toprule
\\textbf{Rule ID} & \\textbf{Variable} & \\textbf{Description} \\\\
\\midrule
\\endfirsthead
\\toprule
\\textbf{Rule ID} & \\textbf{Variable} & \\textbf{Description} \\\\
\\midrule
\\endhead
"""
            
            variables = ["PARAM", "AVISIT", "BASE", "CHG", "DTYPE", "ANL01FL"]
            descriptions = [
                "Variable {} label exceeds recommended length",
                "Inconsistent ordering of records for {}",
                "Variable {} has missing values that may need investigation",
                "Non-standard format detected for {}",
                "Variable {} exists but is not defined in define.xml"
            ]
            
            for i in range(warnings):
                rule_id = f"AD{random.randint(1, 999):04d}"
                var = random.choice(variables)
                desc = random.choice(descriptions).format(var)
                latex_content += f"{rule_id} & {var} & {desc} \\\\\n"
            
            latex_content += """\\bottomrule
\\end{longtable}

"""
        
        # Add recommendations
        latex_content += """\\section*{Recommendations}

\\begin{itemize}
\\item Review all critical errors and correct them before submission
\\item Address warnings to improve data quality
\\item Verify all required ADaM variables are present and correctly formatted
\\item Ensure controlled terminology is applied consistently
\\item Review define.xml for completeness
\\end{itemize}

\\vspace{1cm}

\\begin{center}
\\small\\textit{This is a mock validation report generated for testing purposes.}\\\\
\\textit{For actual CDISC validation, please use Pinnacle 21 Community or Enterprise software.}
\\end{center}

\\end{document}
"""
        
        return latex_content
    
    def create_pdf_report(self, dataset: str, errors: int, warnings: int, notes: int) -> Path:
        """Create a PDF validation report using LaTeX."""
        
        # CRITICAL: Generate filename to match Flow output_specs EXACTLY
        # Flow expects: adsl_validation_report.pdf, NOT ADSL_validation_20251029_191952.pdf
        dataset_lower = dataset.lower()
        pdf_filename = f"{dataset_lower}_validation_report.pdf"
        tex_filename = f"{dataset_lower}_validation_report_{self.timestamp}.tex"
        
        tex_path = self.output_dir / tex_filename
        pdf_path = self.output_dir / pdf_filename
        
        # Generate LaTeX content
        latex_content = self.generate_latex_content(dataset, errors, warnings, notes)
        
        # Write LaTeX file
        with open(tex_path, 'w') as f:
            f.write(latex_content)
        
        # Compile PDF (run twice for proper formatting)
        # Use -jobname to control output PDF filename
        jobname = f"{dataset_lower}_validation_report"
        try:
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 
                 f'-output-directory={self.output_dir}',
                 f'-jobname={jobname}',
                 str(tex_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 
                 f'-output-directory={self.output_dir}',
                 f'-jobname={jobname}',
                 str(tex_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error compiling LaTeX for {dataset}: {e}", file=sys.stderr)
            raise
        
        # Clean up auxiliary files (they use jobname, not tex filename)
        for ext in ['.tex', '.aux', '.log']:
            if ext == '.tex':
                # Keep the timestamped tex file
                aux_file = self.output_dir / tex_filename
            else:
                # Auxiliary files use jobname
                aux_file = self.output_dir / f"{jobname}{ext}"
            if aux_file.exists():
                aux_file.unlink()
        
        return pdf_path


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_status(message: str):
    """Print info status message."""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def check_latex_installation():
    """Check if pdflatex is installed, install if missing."""
    try:
        subprocess.run(['pdflatex', '--version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_status("pdflatex not found. Installing LaTeX packages...")
        try:
            subprocess.run(['apt-get', 'update'], 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL,
                          check=True)
            subprocess.run(['apt-get', 'install', '-y', 
                          'texlive-latex-base', 'texlive-latex-extra'],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL,
                          check=True)
            print_success("LaTeX installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install LaTeX: {e}")
            return False


def run_p21_validation():
    """
    Run the Pinnacle21 validation mock script.
    This function expects ADaM datasets to be available in the workflow inputs
    and will generate validation reports in the workflow outputs.
    """
    
    print()
    print("=" * 60)
    print("  Mock Pinnacle21 Validation Service")
    print("=" * 60)
    print()
    
    # Define paths - outputs must go directly to /workflow/outputs
    # NOT to a subdirectory!
    workflow_outputs = Path("/workflow/outputs")
    
    # Create output directory
    workflow_outputs.mkdir(parents=True, exist_ok=True)
    
    print_success(f"Output directory: {workflow_outputs}")
    
    # Check LaTeX installation
    if not check_latex_installation():
        print_error("LaTeX is required but could not be installed")
        sys.exit(1)
    
    # Define ADaM datasets to validate with severity levels
    # CRITICAL: Keys must match the lowercase dataset names in output_specs
    datasets = {
        "adsl": "clean",
        "adae": "moderate",
        "adcm": "clean",
        "adlb": "clean",
        "admh": "moderate",
        "advs": "clean"
    }
    
    # Check for ADaM datasets in workflow inputs
    print_status("Checking for ADaM datasets in workflow inputs...")
    workflow_inputs = Path("/workflow/inputs")
    for dataset_lower in datasets.keys():
        dataset_path = workflow_inputs / f"{dataset_lower}_dataset"
        if dataset_path.exists():
            print(f"      ✓ Found: {dataset_lower.upper()}.sas7bdat")
        else:
            print(f"      ⚠ Warning: {dataset_lower.upper()}.sas7bdat not found")
    print()
    
    print_status(f"Initiating mock validation for {len(datasets)} ADaM datasets...")
    print()
    
    # Initialize report generator - outputs go directly to /workflow/outputs
    report_gen = P21ValidationReport(workflow_outputs)
    
    # Track validation results
    validation_summary = []
    generated_files = []
    
    # Process each dataset
    for dataset, severity in datasets.items():
        dataset_upper = dataset.upper()
        print_status(f"Validating {dataset_upper}.xpt against CDISC ADaM standards...")
        
        # Generate mock validation results
        errors, warnings, notes = report_gen.generate_validation_data(dataset_upper, severity)
        
        try:
            # Create PDF report with EXACT filename expected by Flow
            print_status(f"Compiling PDF report for {dataset_upper}...")
            pdf_path = report_gen.create_pdf_report(dataset_upper, errors, warnings, notes)
            generated_files.append(pdf_path)
            
            # Print results
            total_issues = errors + warnings + notes
            if errors == 0 and warnings == 0:
                print_success(f"{dataset_upper}: Validation passed ({notes} informational notes)")
            elif errors == 0:
                print_warning(f"{dataset_upper}: Validation completed with {warnings} warnings, {notes} notes")
            else:
                print_error(f"{dataset_upper}: Validation found {errors} errors, {warnings} warnings, {notes} notes")
            
            print(f"           Report: {pdf_path.name}")
            print()
            
            # Add to summary
            validation_summary.append({
                'dataset': dataset_upper,
                'errors': errors,
                'warnings': warnings,
                'notes': notes,
                'total': total_issues,
                'file': pdf_path.name
            })
            
        except Exception as e:
            print_error(f"Failed to generate report for {dataset_upper}: {e}")
            import traceback
            traceback.print_exc()
    
    # Create summary file with EXACT filename expected by Flow
    print()
    print_status("Creating validation summary...")
    
    summary_path = workflow_outputs / "p21_validation_summary.txt"
    with open(summary_path, 'w') as f:
        f.write("Pinnacle21 Validation Summary\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Validation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total reports generated: {len(generated_files)}\n\n")
        
        f.write("Validation Results:\n")
        f.write("-" * 60 + "\n")
        for result in validation_summary:
            f.write(f"\n{result['dataset']}:\n")
            f.write(f"  Errors:   {result['errors']}\n")
            f.write(f"  Warnings: {result['warnings']}\n")
            f.write(f"  Notes:    {result['notes']}\n")
            f.write(f"  Total:    {result['total']}\n")
            f.write(f"  Report:   {result['file']}\n")
        
        f.write("\n" + "-" * 60 + "\n")
        f.write("\nAll Reports:\n")
        for pdf_file in sorted(generated_files):
            f.write(f"  - {pdf_file.name}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("Note: This is a mock validation report for testing purposes.\n")
        f.write("For actual CDISC validation, use Pinnacle 21 Community or Enterprise.\n")
    
    print(f"      ✓ Created: p21_validation_summary.txt")
    
    # Verify all expected outputs exist
    print()
    print_status("Verifying output files...")
    expected_outputs = [
        "p21_validation_summary.txt",
        "adsl_validation_report.pdf",
        "adae_validation_report.pdf",
        "adcm_validation_report.pdf",
        "adlb_validation_report.pdf",
        "admh_validation_report.pdf",
        "advs_validation_report.pdf"
    ]
    
    all_outputs_present = True
    for expected_file in expected_outputs:
        file_path = workflow_outputs / expected_file
        if file_path.exists():
            print(f"      ✓ {expected_file}")
        else:
            print(f"      ✗ MISSING: {expected_file}")
            all_outputs_present = False
    
    if not all_outputs_present:
        print_error("Not all expected outputs were generated!")
        sys.exit(1)
    
    # Print final summary
    print()
    print("=" * 60)
    print_success("Validation completed for all datasets")
    print("=" * 60)
    print()
    print(f"Reports generated in: {workflow_outputs}/")
    print()
    print("Summary:")
    for result in validation_summary:
        status_icon = "✓" if result['errors'] == 0 else "✗"
        print(f"  {status_icon} {result['dataset']}: {result['errors']} errors, "
              f"{result['warnings']} warnings, {result['notes']} notes")
    print()


if __name__ == "__main__":
    try:
        run_p21_validation()
    except Exception as e:
        print_error(f"Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)