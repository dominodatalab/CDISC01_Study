#!/usr/bin/env python3
"""Write one scale-profile batch of artifact files to /workflow/outputs.

Called from generated DominoJobTasks. Files are written in chunks so a
multi-GB file does not have to fit in RAM.
"""

from __future__ import annotations

import argparse
import os
import sys

# /mnt/code is the project repo mount inside a Domino job.
sys.path.insert(0, os.environ.get("DOMINO_WORKING_DIR", "/mnt/code"))

from flows.scale_profiles import profile_batches  # noqa: E402

CHUNK_SIZE = 8 * 1024 * 1024
OUTPUT_DIR = "/workflow/outputs"


def write_file(path: str, size_bytes: int) -> None:
    remaining = size_bytes
    with open(path, "wb") as handle:
        while remaining > 0:
            chunk = min(CHUNK_SIZE, remaining)
            handle.write(b"\0" * chunk)
            remaining -= chunk


def main(profile: str, batch_index: int) -> None:
    batches = profile_batches(profile)
    if batch_index < 0 or batch_index >= len(batches):
        raise SystemExit(f"batch {batch_index} out of range 0..{len(batches) - 1}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for scale_file in batches[batch_index]:
        dest = os.path.join(OUTPUT_DIR, scale_file.output_name)
        write_file(dest, scale_file.size_bytes)
        print(f"Wrote {dest} ({scale_file.size_bytes} bytes) as {scale_file.artifact_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, choices=("reduced", "full"))
    parser.add_argument("--batch", required=True, type=int)
    args = parser.parse_args()
    main(args.profile, args.batch)
