"""Write one batch of a study-file profile to /workflow/outputs.

File contents are tiled from the real CDISC Pilot 01 lb.xpt so they compress
like clinical data, and every 4 KiB block starts with a unique (file, block)
stamp so storage-level deduplication cannot collapse them.
"""

from __future__ import annotations

import argparse
import os
import random
import struct
import sys
from pathlib import Path

sys.path.insert(0, os.environ.get("DOMINO_WORKING_DIR", "/mnt/code"))

from flows.scale_profiles import profile_batches, profile_files  # noqa: E402

BLOCK_SIZE = 4096
CHUNK_SIZE = 8 * 1024 * 1024
OUTPUT_DIR = Path("/workflow/outputs")


def write_file(path: Path, size_bytes: int, texture: bytes, file_id: int) -> None:
    rng = random.Random(file_id)
    block_index = 0
    with open(path, "wb") as handle:
        for offset in range(0, size_bytes, CHUNK_SIZE):
            length = min(CHUNK_SIZE, size_bytes - offset)
            start = rng.randrange(len(texture) - length)
            chunk = bytearray(texture[start : start + length])
            for block_start in range(0, length, BLOCK_SIZE):
                stamp = struct.pack("<QQ", file_id, block_index)[: length - block_start]
                chunk[block_start : block_start + len(stamp)] = stamp
                block_index += 1
            handle.write(chunk)


def main(profile: str, batch_index: int, sdtm_dir: Path) -> None:
    texture = (sdtm_dir / "lb.xpt").read_bytes()
    file_ids = {scale_file: file_id for file_id, scale_file in enumerate(profile_files(profile))}
    for scale_file in profile_batches(profile)[batch_index]:
        dest = OUTPUT_DIR / scale_file.output_name
        write_file(dest, scale_file.size_bytes, texture, file_ids[scale_file])
        print(f"Wrote {dest} ({scale_file.size_bytes} bytes) as {scale_file.artifact_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--batch", required=True, type=int)
    args = parser.parse_args()
    sdtm_dir = Path(Path("/workflow/inputs/sdtm_snapshot_task_input").read_text().strip())
    main(args.profile, args.batch, sdtm_dir)
