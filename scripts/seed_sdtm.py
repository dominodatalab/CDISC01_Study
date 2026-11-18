"""Seed the public CDISC Pilot 01 SDTM into a project dataset and snapshot it.

The domains come from a pinned commit of phuse-org/phuse-scripts (MIT) and are
checked against known hashes. Flow tasks mount the latest read-only snapshot of
the project dataset, not its live copy, so the files have to be in an active
snapshot before the flow is launched.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

PHUSE_SDTM_URL = (
    "https://raw.githubusercontent.com/phuse-org/phuse-scripts/"
    "398a6d33ced9359ffb58c46650a6d488811176b1/data/sdtm/cdiscpilot01"
)
SDTM_SHA256 = {
    "ae": "05cf23dadadf1b6a11f4474c76724f870de389ba6a4312c825b30e299cb1e4d9",
    "cm": "bb31e91b93a8e4854bd66270cb4d1677a4ab59add30ec8cdbebb3491c18f1582",
    "dm": "7327baea97fd532d02385248da0c7240402e770099507e2c3a88e2ac706c02a6",
    "ds": "0dea6d298cf248c953c556ff61d0ade5bb133044761a37709a136e2d9ef580e8",
    "ex": "37daacb3fdafba7b7ac7e254b51c43c4576f9ee45c87264da6b85e589ad7b8dc",
    "lb": "47394de7c6484bdf3d5b15c5fe580ca49125707475e6352d30afd5d75c2d7830",
    "mh": "d4c3539c2e9e14614b3261cea9564e004ef09ffc211e70320e2a1880aba18d90",
    "qs": "a1a68fbebbceb6237a8fba0f96b6b9ab8d476817200cde5a0b625966ac23cd6e",
    "relrec": "2376dff7eb74d917eb6fd90ca4690ae82227d98c59235eb1b56e499b96c64284",
    "sc": "9dca4cc3ef9631cbdbdd7b82db4a5f3cf7e52006da00f159fd293b53ae537957",
    "se": "0cfc6862368e4f4ffbd80baea626714ab93fd1793707bc89430b32a6c3d62728",
    "suppae": "97cad614024d0a9da646116505968952a7aa7eb4bcab2ae45ad15b18b9f5c1b9",
    "suppdm": "8258ec783c2dbc3dc0d7a426ad05f1d19f26ff84cf2eef797e7c6bfff1725f06",
    "suppds": "d97b153dc036b29f06369e4ae3922c178a9f6caf1947de4ee2639838013ea3c3",
    "supplb": "255a1149063aa0d8dbb8bb453b198b57e8cd748932bbad82864f208375fb091f",
    "sv": "ea831a4aceede71d26b6cc2d2a5bb04378dc91fcfeafae2aee6edc4fcb40fb52",
    "ta": "848c3d2e809b3fa91044a811717a57cd1f53e608000730792c102b646d1f5a4c",
    "te": "21ab1ae0d2dd629c618feda8a3fc09c88870d0bdd136e92d757fb20f9d9425e8",
    "ti": "c9ebf759ff99ca220a92c23d371a59472532dd47d9c278316ff353b8c2087492",
    "ts": "517ceea43a3c363ed1542df370f84a50bbcba00c7ca35973e93631edc0855afc",
    "tv": "127aa654b9de5c80b62acd153d32877a8e32e127280933150a7a0d28bdb75d4a",
    "vs": "eb54bb58944c1d725e74c7c0f91a9902212b072e8622c29976505283a8e64cd9",
}

SNAPSHOT_POLL_INTERVAL_S = 10
SNAPSHOT_TIMEOUT_S = 1800
SNAPSHOT_FAILURE_STATUSES = {"failed", "markForDeletion", "deletionInProgress", "deleted"}


def download_sdtm(dataset_dir: Path) -> None:
    dataset_dir.mkdir(parents=True, exist_ok=True)
    for domain, expected_sha256 in SDTM_SHA256.items():
        with urllib.request.urlopen(f"{PHUSE_SDTM_URL}/{domain}.xpt", timeout=300) as response:
            content = response.read()
        if hashlib.sha256(content).hexdigest() != expected_sha256:
            sys.exit(f"{domain}.xpt does not match its pinned sha256")
        (dataset_dir / f"{domain}.xpt").write_bytes(content)
        print(f"Wrote {dataset_dir / domain}.xpt ({len(content)} bytes)")


def _domino_api(method: str, path: str, body: dict | None = None) -> dict:
    request = urllib.request.Request(
        f"{os.environ['DOMINO_API_PROXY']}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def snapshot_sdtm(dataset_id: str) -> None:
    paths = [f"{domain}.xpt" for domain in SDTM_SHA256]
    snapshot = _domino_api("POST", f"/api/datasetrw/v1/datasets/{dataset_id}/snapshots", {"relativeFilePaths": paths})[
        "snapshot"
    ]
    print(f"Created snapshot {snapshot['id']} of dataset {dataset_id} ({snapshot['status']})")

    deadline = time.monotonic() + SNAPSHOT_TIMEOUT_S
    while snapshot["status"] != "active":
        if snapshot["status"] in SNAPSHOT_FAILURE_STATUSES:
            sys.exit(f"Snapshot {snapshot['id']} ended in status {snapshot['status']}")
        if time.monotonic() > deadline:
            sys.exit(f"Snapshot {snapshot['id']} still {snapshot['status']} after {SNAPSHOT_TIMEOUT_S}s")
        time.sleep(SNAPSHOT_POLL_INTERVAL_S)
        snapshot = _domino_api("GET", f"/api/datasetrw/v1/snapshots/{snapshot['id']}")["snapshot"]
    print(f"Snapshot {snapshot['id']} is active")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python scripts/seed_sdtm.py <dataset_dir> <dataset_id>")
    download_sdtm(Path(sys.argv[1]))
    snapshot_sdtm(sys.argv[2])
