#!/bin/bash

# Mock Pinnacle21 ADaM Dataset Validation Script
# This script simulates sending ADaM datasets to Pinnacle21 for CDISC validation
# and generates mock PDF validation reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OUTPUT_DIR="validation_reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Function to print colored messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to generate mock validation data
generate_validation_data() {
    local dataset=$1
    local severity=$2
    
    case $severity in
        "clean")
            errors=0
            warnings=$((RANDOM % 3))
            notes=$((RANDOM % 5 + 1))
            ;;
        "moderate")
            errors=$((RANDOM % 3 + 1))
            warnings=$((RANDOM % 8 + 2))
            notes=$((RANDOM % 10 + 5))
            ;;
        "severe")
            errors=$((RANDOM % 10 + 5))
            warnings=$((RANDOM % 15 + 5))
            notes=$((RANDOM % 20 + 10))
            ;;
    esac
    
    echo "$errors,$warnings,$notes"
}

# Function to create mock PDF validation report using LaTeX
create_validation_report() {
    local dataset=$1
    local errors=$2
    local warnings=$3
    local notes=$4
    local output_file=$5
    
    # Create LaTeX content
    cat > "${output_file}.tex" <<EOF
\\documentclass[11pt,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[margin=1in]{geometry}
\\usepackage{graphicx}
\\usepackage{xcolor}
\\usepackage{longtable}
\\usepackage{booktabs}
\\usepackage{fancyhdr}

\\pagestyle{fancy}
\\fancyhf{}
\\rhead{Page \\thepage}
\\lhead{Pinnacle 21 Validation Report}

\\definecolor{errorcolor}{RGB}{220,53,69}
\\definecolor{warningcolor}{RGB}{255,193,7}
\\definecolor{notecolor}{RGB}{0,123,255}

\\begin{document}

\\begin{center}
\\Large\\textbf{Pinnacle 21 Community Validation Report}\\\\
\\large\\textbf{ADaM Dataset Validation}\\\\
\\vspace{0.3cm}
\\normalsize Generated: $(date +"%B %d, %Y at %H:%M:%S")
\\end{center}

\\vspace{0.5cm}

\\section*{Executive Summary}

\\begin{tabular}{ll}
\\textbf{Dataset:} & ${dataset} \\\\
\\textbf{Standard:} & CDISC ADaM v1.1 \\\\
\\textbf{Validation Date:} & $(date +"%Y-%m-%d") \\\\
\\textbf{Validator Version:} & Pinnacle 21 Community 4.1.0 \\\\
\\end{tabular}

\\vspace{0.5cm}

\\section*{Validation Results}

\\begin{tabular}{lc}
\\toprule
\\textbf{Issue Type} & \\textbf{Count} \\\\
\\midrule
\\textcolor{errorcolor}{\\textbf{Errors}} & ${errors} \\\\
\\textcolor{warningcolor}{\\textbf{Warnings}} & ${warnings} \\\\
\\textcolor{notecolor}{\\textbf{Notes}} & ${notes} \\\\
\\midrule
\\textbf{Total Issues} & $((errors + warnings + notes)) \\\\
\\bottomrule
\\end{tabular}

\\vspace{0.5cm}

EOF

    # Add sample issues based on counts
    if [ $errors -gt 0 ]; then
        cat >> "${output_file}.tex" <<EOF
\\section*{Critical Errors}

\\begin{longtable}{p{2cm}p{3cm}p{8cm}}
\\toprule
\\textbf{Rule ID} & \\textbf{Variable} & \\textbf{Description} \\\\
\\midrule
\\endfirsthead
\\toprule
\\textbf{Rule ID} & \\textbf{Variable} & \\textbf{Description} \\\\
\\midrule
\\endhead
EOF
        for ((i=1; i<=$errors; i++)); do
            rule_id="AD$(printf %04d $((RANDOM % 1000 + 1)))"
            variables=("PARAMCD" "AVAL" "AVISITN" "TRTP" "STUDYID" "USUBJID")
            var="${variables[$((RANDOM % ${#variables[@]}))]}"
            descriptions=(
                "Variable $var is required but missing from dataset"
                "Invalid value found in $var at record $((RANDOM % 1000 + 1))"
                "Variable $var does not conform to controlled terminology"
                "Missing label for variable $var"
                "Variable $var has incorrect data type (expected numeric)"
            )
            desc="${descriptions[$((RANDOM % ${#descriptions[@]}))]}"
            echo "$rule_id & $var & $desc \\\\" >> "${output_file}.tex"
        done
        echo "\\bottomrule" >> "${output_file}.tex"
        echo "\\end{longtable}" >> "${output_file}.tex"
        echo "" >> "${output_file}.tex"
    fi

    if [ $warnings -gt 0 ]; then
        cat >> "${output_file}.tex" <<EOF
\\section*{Warnings}

\\begin{longtable}{p{2cm}p{3cm}p{8cm}}
\\toprule
\\textbf{Rule ID} & \\textbf{Variable} & \\textbf{Description} \\\\
\\midrule
\\endfirsthead
\\toprule
\\textbf{Rule ID} & \\textbf{Variable} & \\textbf{Description} \\\\
\\midrule
\\endhead
EOF
        for ((i=1; i<=$warnings; i++)); do
            rule_id="AD$(printf %04d $((RANDOM % 1000 + 1)))"
            variables=("PARAM" "AVISIT" "BASE" "CHG" "DTYPE" "ANL01FL")
            var="${variables[$((RANDOM % ${#variables[@]}))]}"
            descriptions=(
                "Variable $var label exceeds recommended length"
                "Inconsistent ordering of records for $var"
                "Variable $var has missing values that may need investigation"
                "Non-standard format detected for $var"
                "Variable $var exists but is not defined in define.xml"
            )
            desc="${descriptions[$((RANDOM % ${#descriptions[@]}))]}"
            echo "$rule_id & $var & $desc \\\\" >> "${output_file}.tex"
        done
        echo "\\bottomrule" >> "${output_file}.tex"
        echo "\\end{longtable}" >> "${output_file}.tex"
        echo "" >> "${output_file}.tex"
    fi

    cat >> "${output_file}.tex" <<EOF
\\section*{Recommendations}

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
EOF

    # Generate PDF from LaTeX
    print_status "Compiling PDF report for ${dataset}..."
    pdflatex -interaction=nonstopmode -output-directory="$(dirname "$output_file")" "${output_file}.tex" > /dev/null 2>&1
    pdflatex -interaction=nonstopmode -output-directory="$(dirname "$output_file")" "${output_file}.tex" > /dev/null 2>&1
    
    # Clean up auxiliary files
    rm -f "${output_file}.tex" "${output_file}.aux" "${output_file}.log"
}

# Main script
main() {
    echo ""
    echo "=========================================="
    echo "  Mock Pinnacle21 Validation Service"
    echo "=========================================="
    echo ""
    
    # Check if pdflatex is installed
    if ! command -v pdflatex &> /dev/null; then
        print_error "pdflatex is not installed. Installing texlive-latex-base..."
        sudo apt-get update > /dev/null 2>&1
        sudo apt-get install -y texlive-latex-base texlive-latex-extra > /dev/null 2>&1
    fi
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    print_success "Output directory created: $OUTPUT_DIR"
    
    # Define ADaM datasets to validate
    declare -A datasets=(
        ["ADSL"]="clean"
        ["ADAE"]="moderate"
        ["ADLB"]="clean"
        ["ADVS"]="moderate"
        ["ADTTE"]="clean"
        ["ADEFF"]="severe"
    )
    
    print_status "Initiating mock validation for ${#datasets[@]} ADaM datasets..."
    echo ""
    
    # Simulate API call delay
    sleep 1
    
    # Process each dataset
    for dataset in "${!datasets[@]}"; do
        print_status "Validating ${dataset}.xpt against CDISC ADaM standards..."
        
        # Simulate validation processing
        sleep $((RANDOM % 3 + 2))
        
        # Generate mock validation results
        severity="${datasets[$dataset]}"
        IFS=',' read -r errors warnings notes <<< "$(generate_validation_data "$dataset" "$severity")"
        
        # Create report filename
        report_file="${OUTPUT_DIR}/${dataset}_validation_${TIMESTAMP}.pdf"
        
        # Generate PDF report
        create_validation_report "$dataset" "$errors" "$warnings" "$notes" "${OUTPUT_DIR}/${dataset}_validation_${TIMESTAMP}"
        
        # Print results
        total_issues=$((errors + warnings + notes))
        if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
            print_success "${dataset}: Validation passed (${notes} informational notes)"
        elif [ $errors -eq 0 ]; then
            print_warning "${dataset}: Validation completed with ${warnings} warnings, ${notes} notes"
        else
            print_error "${dataset}: Validation found ${errors} errors, ${warnings} warnings, ${notes} notes"
        fi
        
        echo "           Report: ${report_file}"
        echo ""
    done
    
    # Summary
    echo "=========================================="
    print_success "Validation completed for all datasets"
    echo "=========================================="
    echo ""
    echo "Reports generated in: ${OUTPUT_DIR}/"
    echo ""
    echo "Summary:"
    ls -lh "${OUTPUT_DIR}"/*.pdf 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
    echo ""
}

# Run main function
main