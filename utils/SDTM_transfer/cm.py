import os
import shutil

# The name of the Flow input, which Domino places into a file blob under /workflow/inputs
task_input_name = "sdtm_snapshot_task_input"
input_location = f"/workflow/inputs/{task_input_name}"


# 1. Read the directory path fed as a Launch parameter
with open(input_location, "r") as file:
    sdtm_dir = file.read().strip()

# 2. Construct the full path to ae.sas7bdat
ae_file_path = os.path.join(sdtm_dir, "cm.sas7bdat")

# 3. Copy the file to /workflow/outputs
output_file_path = "/workflow/outputs/cm.sas7bdat"
if os.path.exists(ae_file_path):
    shutil.copy(ae_file_path, output_file_path)
    print(f"Copied {ae_file_path} to {output_file_path}")
else:
    print(f"File not found: {ae_file_path}")

    