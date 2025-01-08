import os
import shutil
from argparse import ArgumentParser

parser = ArgumentParser(description='SDTM data movement script')
parser.add_argument('--sdtm_snapshot_task_input',
                    type=str,
                    default="/mnt/imported/data/SDTMBLIND",
                    help="Path to SDTM data directory (default: /mnt/imported/data/SDTMBLIND)")
args = parser.parse_args()

SDTM_DATA_PATH = args.sdtm_snapshot_task_input
OUTPUT_PATH = "/workflow/outputs"

src_file = os.path.join(SDTM_DATA_PATH, "ae.sas7bdat")
dst_file = os.path.join(OUTPUT_PATH, "ae.sas7bdat")

if os.path.exists(src_file):
    shutil.copy(src_file, dst_file)
    print("File moved successfully.")
else:
    print(f"File not found: {src_file}")