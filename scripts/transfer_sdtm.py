"""Copy one SDTM domain from the snapshot directory input to this task's output."""

import shutil
import sys
from pathlib import Path

domain = sys.argv[1]
sdtm_dir = Path(Path("/workflow/inputs/sdtm_snapshot_task_input").read_text().strip())
shutil.copy(sdtm_dir / f"{domain}.xpt", f"/workflow/outputs/{domain}.xpt")
print(f"Copied {sdtm_dir / domain}.xpt")
