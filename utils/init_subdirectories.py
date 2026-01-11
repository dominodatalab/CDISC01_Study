"""
NetApp Volume Subdirectory Initialization Script

This script creates the required subdirectory structure within NetApp volumes
that have been newly created. It must run in a separate Domino job where the
volumes are properly mounted.

This script creates:
- OUTPUT_DEV and OUTPUT_PROD volumes: logs, lst, qc, tfl
- DATA_DEV and DATA_PROD volumes: adam, adhoc, logs, misc, qc

Author: Domino Data Lab
Version: 1.0
"""

import os
import sys

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Get project name from environment
DOMINO_PROJECT_NAME = os.environ.get("DOMINO_PROJECT_NAME")

if not DOMINO_PROJECT_NAME:
    print("ERROR: DOMINO_PROJECT_NAME environment variable is required")
    sys.exit(1)

# NetApp volume mount point
NETAPP_ROOT = "/mnt/netapp-volumes"

# ==============================================================================
# DEFINE VOLUME SUBDIRECTORY STRUCTURES
# ==============================================================================

# Define subdirectories for each volume type
VOLUME_STRUCTURES = {
    f"{DOMINO_PROJECT_NAME}_OUTPUT_DEV": {
        "subdirs": ["logs", "lst", "qc", "tfl"],
        "description": "Development output volume"
    },
    f"{DOMINO_PROJECT_NAME}_OUTPUT_PROD": {
        "subdirs": ["logs", "lst", "qc", "tfl"],
        "description": "Production output volume"
    },
    f"{DOMINO_PROJECT_NAME}_DATA_DEV": {
        "subdirs": ["adam", "adhoc", "logs", "misc", "qc"],
        "description": "Development data volume"
    },
    f"{DOMINO_PROJECT_NAME}_DATA_PROD": {
        "subdirs": ["adam", "adhoc", "logs", "misc", "qc"],
        "description": "Production data volume"
    }
}

# ==============================================================================
# CREATE SUBDIRECTORY STRUCTURES
# ==============================================================================

print("=" * 80)
print("NETAPP VOLUME SUBDIRECTORY INITIALIZATION")
print("=" * 80)
print(f"\nProject: {DOMINO_PROJECT_NAME}")
print(f"NetApp root: {NETAPP_ROOT}")

# Track success/failure
created_count = 0
skipped_count = 0
failed_count = 0
missing_volumes = []

for volume_name, config in VOLUME_STRUCTURES.items():
    volume_path = os.path.join(NETAPP_ROOT, volume_name)

    print(f"\n{'='*80}")
    print(f"Volume: {volume_name}")
    print(f"  Description: {config['description']}")
    print(f"  Path: {volume_path}")

    # Check if volume is mounted
    if not os.path.exists(volume_path):
        print(f"  ✗ ERROR: Volume not mounted at {volume_path}")
        missing_volumes.append(volume_name)
        failed_count += 1
        continue

    print(f"  ✓ Volume is mounted")
    print(f"  Creating subdirectories: {', '.join(config['subdirs'])}")

    # Create each subdirectory
    for subdir in config["subdirs"]:
        subdir_path = os.path.join(volume_path, subdir)

        try:
            if os.path.exists(subdir_path):
                print(f"    ✓ Already exists: {subdir}/")
                skipped_count += 1
            else:
                os.makedirs(subdir_path, exist_ok=True)
                print(f"    ✓ Created: {subdir}/")
                created_count += 1

        except Exception as e:
            print(f"    ✗ ERROR creating {subdir}/: {e}")
            failed_count += 1

# Additional nested subdirectory structures for QC
print(f"\n{'='*80}")
print("Creating nested QC subdirectory structures")
print("="*80)

# QC subdirectories for OUTPUT volumes
qc_structures_output = {
    f"{DOMINO_PROJECT_NAME}_OUTPUT_DEV": ["qc/tfl", "qc/logs"],
    f"{DOMINO_PROJECT_NAME}_OUTPUT_PROD": ["qc/tfl", "qc/logs"],
}

# QC subdirectories for DATA volumes
qc_structures_data = {
    f"{DOMINO_PROJECT_NAME}_DATA_DEV": ["qc/adam", "qc/logs"],
    f"{DOMINO_PROJECT_NAME}_DATA_PROD": ["qc/adam", "qc/logs"],
}

# Combine all QC structures
all_qc_structures = {**qc_structures_output, **qc_structures_data}

for volume_name, subdirs in all_qc_structures.items():
    volume_path = os.path.join(NETAPP_ROOT, volume_name)

    print(f"\nVolume: {volume_name}")

    if not os.path.exists(volume_path):
        print(f"  ✗ Skipping (volume not mounted)")
        continue

    for subdir in subdirs:
        subdir_path = os.path.join(volume_path, subdir)

        try:
            if os.path.exists(subdir_path):
                print(f"  ✓ Already exists: {subdir}/")
                skipped_count += 1
            else:
                os.makedirs(subdir_path, exist_ok=True)
                print(f"  ✓ Created: {subdir}/")
                created_count += 1

        except Exception as e:
            print(f"  ✗ ERROR creating {subdir}/: {e}")
            failed_count += 1

# ==============================================================================
# SUMMARY
# ==============================================================================

print("\n" + "=" * 80)
print("SUBDIRECTORY INITIALIZATION COMPLETE")
print("=" * 80)
print(f"\nSummary:")
print(f"  ✓ Created: {created_count} directories")
print(f"  → Skipped (already exist): {skipped_count} directories")
print(f"  ✗ Failed: {failed_count} operations")

if missing_volumes:
    print(f"\n⚠ WARNING: {len(missing_volumes)} volume(s) not mounted:")
    for vol in missing_volumes:
        print(f"    - {vol}")
    print("\nPlease ensure volumes are properly attached to this Domino environment.")
    sys.exit(1)

if failed_count > 0:
    print("\n⚠ WARNING: Some operations failed. Check the output above for details.")
    sys.exit(1)

print("\n✓ All subdirectories successfully initialized!")
sys.exit(0)
