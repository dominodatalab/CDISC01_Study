#!/usr/bin/env bash
##
## Launch the DOM-79203 CDISC1-shaped Flows Artifact Export scale workflow.
##
## Usage:
##   bash generate_and_run_scale_export.sh <dataset_url> <project_name> <profile> [--skip-export]
##
## profile is `reduced` or `full`.
## --skip-export generates the clinical + extra-file DAG without a programmatic
## export so a Cucu scenario can drive per-stage UI exports instead.
##
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: bash generate_and_run_scale_export.sh <dataset_url> <project_name> <profile> [--skip-export]" >&2
  exit 1
fi

DATASET_URL="$1"
PROJECT_NAME="$2"
PROFILE="$3"
SKIP_EXPORT="${4:-}"

DATASET_ID="$(basename "$DATASET_URL")"
DATASET_DIR="/domino/datasets/local/${PROJECT_NAME}"
ROOT="${DOMINO_WORKING_DIR:-/mnt/code}"

cd "$ROOT"

python "$ROOT/scripts/seed_sdtm_placeholders.py" "$DATASET_DIR"

GEN_ARGS=(--profile "$PROFILE" --dataset-id "$DATASET_ID" --out "$ROOT/generate_artifacts_scale_run.py")
if [[ "$SKIP_EXPORT" == "--skip-export" ]]; then
  GEN_ARGS+=(--skip-export)
fi
python "$ROOT/flows/gen_scale_export_workflow.py" "${GEN_ARGS[@]}"

pyflyte run --remote "$ROOT/generate_artifacts_scale_run.py" export_scale_study \
  --sdtm_dataset_snapshot "$DATASET_DIR"
