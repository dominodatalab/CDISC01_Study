import os
from PyPDF2 import PdfMerger

# Determine the input and output folders based on the environment variable
if os.getenv("DOMINO_IS_WORKFLOW_JOB", "false").lower() == "true":
    input_folder = "/workflow/input"
    output_file = "/workflow/output/CDISC01_tfls.pdf"
else:
    input_folder = "/mnt/artifacts/tfl"
    output_file = "/mnt/artifacts/tfl/CDISC01_tfls.pdf"

def combine_pdfs(input_folder, output_file):
    # Create a PdfMerger object
    merger = PdfMerger()

    # List all files in the input folder
    files = sorted(f for f in os.listdir(input_folder) if f.endswith('.pdf'))

    # Add each PDF file to the merger
    for file in files:
        file_path = os.path.join(input_folder, file)
        print(f"Adding {file_path} to the combined PDF.")
        merger.append(file_path)

    # Write the combined PDF to the output file
    merger.write(output_file)
    merger.close()
    print(f"Combined PDF saved as {output_file}")

if __name__ == "__main__":
    combine_pdfs(input_folder, output_file)