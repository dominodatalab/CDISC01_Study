import os
import shutil

SDTM_DATA_PATH = workflows/inputs/sdtm_snapshot_task_input
OUTPUT_PATH = "/workflow/outputs"

src_file = os.path.join(SDTM_DATA_PATH, "ae.sas7bdat")
dst_file = os.path.join(OUTPUT_PATH, "ae.sas7bdat")

if os.path.exists(src_file):
    shutil.copy(src_file, dst_file)
    print("File moved successfully.")
else:
    print(f"File not found: {src_file}")