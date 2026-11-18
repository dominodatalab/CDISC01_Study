"""CDISC Pilot 01 study flow that exports its artifacts with Flows Artifact Export (DOM-79203).

SDTM -> ADaM -> TFL on the public CDISC Pilot 01 data, plus synthetic study
files shaped like the customer report in flows/scale_profiles.py. The DATA
artifacts (SDTM, ADaM and study files) are exported to a project dataset or a
NetApp volume; export does not accept REPORT artifacts, so the TFL PDFs stay
on the flow run. Launched by run_scale_export.sh, which
sets the environment variables read below before `pyflyte run`.
"""

import math
import os
from typing import TypeVar

from flytekit import workflow
from flytekit.types.file import FlyteFile
from flytekitplugins.domino.artifact import (
    DATA,
    REPORT,
    Artifact,
    ExportArtifactToDatasetsSpec,
    ExportArtifactToNetAppVolumesSpec,
    run_launch_export_artifacts_task,
)
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task

from flows.scale_profiles import GIB, LARGE_TASK_BYTES, profile_batches

SCALE_PROFILE = os.environ.get("SCALE_PROFILE", "regular")
SAS_ENVIRONMENT = os.environ.get("SAS_ENVIRONMENT", "SAS Environment")
LARGE_TASK_HARDWARE_TIER_ID = os.environ.get("LARGE_TASK_HARDWARE_TIER_ID", "small-k8s")
EXPORT_DATASET_ID = os.environ.get("EXPORT_DATASET_ID")
EXPORT_NETAPP_VOLUME_ID = os.environ.get("EXPORT_NETAPP_VOLUME_ID")

AdamArtifact = Artifact("ADaM Datasets", DATA)
ReportArtifact = Artifact("TFL Reports", REPORT)
StudyFilesArtifact = Artifact("Study Files", DATA)

SDTM_DOMAINS = ("ae", "cm", "dm", "ds", "ex", "lb", "mh", "qs", "relrec", "sc", "se")
SDTM_DOMAINS += ("suppae", "suppdm", "suppds", "supplb", "sv", "ta", "te", "ti", "ts", "tv", "vs")

# dataset -> SDTM and ADaM inputs, in the order the program reads them
ADAM_INPUTS = {
    "adsl": ("dm",),
    "adae": ("ae", "ex", "adsl"),
    "adcm": ("cm", "adsl"),
    "adlb": ("lb", "adsl"),
    "admh": ("mh", "adsl"),
    "advs": ("vs", "adsl"),
}
TFL_INPUTS = {
    "t_pop": ("adsl",),
    "t_ae_rel": ("adae",),
    "t_vscat": ("advs",),
}

XptFile = FlyteFile[TypeVar("xpt")]
Sas7bdatFile = FlyteFile[TypeVar("sas7bdat")]


def _sas_task(name: str, program: str, input_files: dict, output_type) -> dict:
    return run_domino_job_task(
        flyte_task_name=f"Create {name.upper()}",
        command=program,
        inputs=[
            Input(name=key, type=XptFile if key in SDTM_DOMAINS else Sas7bdatFile, value=value)
            for key, value in input_files.items()
        ],
        output_specs=[Output(name=name, type=output_type)],
        environment_name=SAS_ENVIRONMENT,
        use_project_defaults_for_omitted=True,
        use_latest_git_ref=True,
        cache=False,
    )


def _export_spec(artifact: Artifact):
    if EXPORT_NETAPP_VOLUME_ID:
        return ExportArtifactToNetAppVolumesSpec(artifact=artifact, netapp_volume_id=EXPORT_NETAPP_VOLUME_ID)
    return ExportArtifactToDatasetsSpec(artifact=artifact, dataset_id=EXPORT_DATASET_ID)


@workflow
def export_scale_study(sdtm_dataset_snapshot: str):
    sdtm_dir = Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)
    files = {}

    for domain in SDTM_DOMAINS:
        files[domain] = run_domino_job_task(
            flyte_task_name=f"Transfer {domain.upper()} SDTM",
            command=f"python /mnt/code/scripts/transfer_sdtm.py {domain}",
            inputs=[sdtm_dir],
            output_specs=[Output(name=domain, type=StudyFilesArtifact.File(name=f"sdtm__{domain}.xpt"))],
            use_project_defaults_for_omitted=True,
            use_latest_git_ref=True,
            cache=False,
        )[domain]

    for dataset, inputs in ADAM_INPUTS.items():
        files[dataset] = _sas_task(
            dataset,
            f"prod/adam_scale/{dataset.upper()}.sas",
            {name: files[name] for name in inputs},
            AdamArtifact.File(name=f"{dataset}.sas7bdat"),
        )[dataset]

    for table, inputs in TFL_INPUTS.items():
        _sas_task(
            table,
            f"prod/tfl_scale/{table}.sas",
            {name: files[name] for name in inputs},
            ReportArtifact.File(name=f"{table}.pdf"),
        )

    for index, batch in enumerate(profile_batches(SCALE_PROFILE)):
        batch_bytes = sum(scale_file.size_bytes for scale_file in batch)
        run_domino_job_task(
            flyte_task_name=f"Emit study files batch {index}",
            command=f"python /mnt/code/scripts/emit_scale_artifacts.py --profile {SCALE_PROFILE} --batch {index}",
            inputs=[sdtm_dir],
            output_specs=[
                Output(name=f.output_name, type=StudyFilesArtifact.File(name=f.artifact_filename)) for f in batch
            ],
            volume_size_gib=max(10, math.ceil(batch_bytes / GIB) + 4),
            hardware_tier_id=LARGE_TASK_HARDWARE_TIER_ID if batch_bytes >= LARGE_TASK_BYTES else None,
            use_project_defaults_for_omitted=True,
            use_latest_git_ref=True,
            cache=False,
        )

    run_launch_export_artifacts_task(
        spec_list=[_export_spec(AdamArtifact), _export_spec(StudyFilesArtifact)],
        use_project_defaults_for_omitted=True,
    )
