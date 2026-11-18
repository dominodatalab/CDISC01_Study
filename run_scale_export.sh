#!/usr/bin/env bash
##
## Seed the public CDISC Pilot 01 SDTM into the project dataset, then run
## flows/scale_export_flow.py and export its artifacts (DOM-79203).
##
## Usage:
##   bash run_scale_export.sh <dataset_url> <project_name> <regular|full> [--netapp-volume-id <id>]
##     [--sas-environment <name>] [--large-task-hardware-tier-id <id>]
##
## The SDTM is always seeded into the project dataset at <dataset_url>. The flow
## exports to that dataset unless --netapp-volume-id names a NetApp volume.
## Study-file batches of 1 GiB or more run on --large-task-hardware-tier-id
## (default small-k8s); everything else uses the project's default tier.
##
set -euo pipefail

USAGE="Usage: bash run_scale_export.sh <dataset_url> <project_name> <regular|full> [--netapp-volume-id <id>] [--sas-environment <name>] [--large-task-hardware-tier-id <id>]"
if [[ $# -lt 3 ]]; then
  echo "$USAGE" >&2
  exit 1
fi

DATASET_ID="$(basename "$1")"
PROJECT_NAME="$2"
export SCALE_PROFILE="$3"
export SAS_ENVIRONMENT="SAS Environment"
export EXPORT_DATASET_ID="$DATASET_ID"
export EXPORT_NETAPP_VOLUME_ID=""
export LARGE_TASK_HARDWARE_TIER_ID="small-k8s"
shift 3
while [[ $# -gt 0 ]]; do
  case "$1" in
    --netapp-volume-id) EXPORT_NETAPP_VOLUME_ID="$2"; shift 2 ;;
    --sas-environment) SAS_ENVIRONMENT="$2"; shift 2 ;;
    --large-task-hardware-tier-id) LARGE_TASK_HARDWARE_TIER_ID="$2"; shift 2 ;;
    *) echo "$USAGE" >&2; exit 1 ;;
  esac
done

# Git-based projects mount the project dataset at /mnt/data; DFS projects at /domino/datasets/local.
if [[ -d "/mnt/data/${PROJECT_NAME}" ]]; then
  DATASET_DIR="/mnt/data/${PROJECT_NAME}"
else
  DATASET_DIR="/domino/datasets/local/${PROJECT_NAME}"
fi

cd "${DOMINO_WORKING_DIR:-/mnt/code}"
python scripts/seed_sdtm.py "$DATASET_DIR" "$DATASET_ID"
pyflyte run --remote flows/scale_export_flow.py export_scale_study --sdtm_dataset_snapshot "$DATASET_DIR"
