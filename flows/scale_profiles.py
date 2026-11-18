"""Study-file profiles for the DOM-79203 Flows Artifact Export test.

Folder file counts and sizes come from the customer file-size report attached
to DOM-79203, rounded up. `full` keeps the report's bytes, including its largest
file (supplb.sas7bdat, about 11 GiB), but only 60% of its files. At the report's
5,204 files, one output per file compiles past the 2 MiB Flyte workflow limit and
the flow fails to launch. `regular` keeps the same folder mix at a small fraction
of the files and bytes so it can run in the standard suite.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

GIB = 1024**3

# (folder, file_count, size_gib, extension)
FOLDER_SPEC = (
    ("derived_data", 65, 28.82, "sas7bdat"),
    ("analysis_data", 62, 43.94, "sas7bdat"),
    ("crt", 495, 111.88, "sas7bdat"),
    ("pgm", 2126, 0.05, "sas"),
    ("util", 618, 2.17, "sas7bdat"),
    ("reports", 1816, 30.95, "rtf"),
)
LARGE_FILE_FOLDER = "crt"
LARGE_FILE_NAME = "supplb.sas7bdat"
LARGE_FILE_BYTES = 11 * GIB

# profile -> (fraction of each folder's files, fraction of its bytes, include the large file)
PROFILES = {
    "regular": (0.02, 0.01, False),
    "full": (0.6, 1.0, True),
}

FILES_PER_TASK = 50
BYTES_PER_TASK = 8 * GIB
LARGE_TASK_BYTES = GIB  # batches this size or larger run on the launcher's --large-task-hardware-tier-id


@dataclass(frozen=True)
class ScaleFile:
    folder: str
    name: str
    size_bytes: int
    output_name: str

    @property
    def artifact_filename(self) -> str:
        return f"{self.folder}__{self.name}"


def profile_files(profile: str) -> list[ScaleFile]:
    count_fraction, size_fraction, include_large_file = PROFILES[profile]
    files = []
    for folder, count, size_gib, ext in FOLDER_SPEC:
        count = math.ceil(count * count_fraction)
        total_bytes = math.ceil(size_gib * size_fraction * GIB)
        has_large_file = include_large_file and folder == LARGE_FILE_FOLDER
        sizes = [total_bytes // count] * count
        if has_large_file:
            sizes = [LARGE_FILE_BYTES] + [(total_bytes - LARGE_FILE_BYTES) // (count - 1)] * (count - 1)
        for index, size in enumerate(sizes):
            output_name = f"{folder}_{index:04d}"
            name = LARGE_FILE_NAME if has_large_file and index == 0 else f"{output_name}.{ext}"
            files.append(ScaleFile(folder, name, size, output_name))
    return files


def profile_batches(profile: str) -> list[list[ScaleFile]]:
    """Group files into flow tasks of at most FILES_PER_TASK files and BYTES_PER_TASK bytes."""
    batches: list[list[ScaleFile]] = [[]]
    for scale_file in profile_files(profile):
        batch = batches[-1]
        if batch and (
            len(batch) == FILES_PER_TASK or sum(f.size_bytes for f in batch) + scale_file.size_bytes > BYTES_PER_TASK
        ):
            batches.append([])
        batches[-1].append(scale_file)
    return batches
