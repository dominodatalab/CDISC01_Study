#!/usr/bin/env python3
"""Write placeholder SDTM domain files into a project dataset.

The CDISC1 SDTM-transfer tasks copy `{domain}.sas7bdat` from the dataset
mount. ADaM scale programs generate their own SAS datasets from datalines, so
these placeholders only need to exist for the transfer tasks to succeed.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.environ.get("DOMINO_WORKING_DIR", "/mnt/code"))

from flows.scale_profiles import SDTM_DOMAINS  # noqa: E402

PLACEHOLDER = b"SDTM_PLACEHOLDER\n"


def main(dataset_dir: str) -> None:
    os.makedirs(dataset_dir, exist_ok=True)
    for domain in SDTM_DOMAINS:
        path = os.path.join(dataset_dir, f"{domain}.sas7bdat")
        with open(path, "wb") as handle:
            handle.write(PLACEHOLDER)
        print(f"Wrote {path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python scripts/seed_sdtm_placeholders.py <dataset_dir>\n")
        sys.exit(1)
    main(sys.argv[1])
