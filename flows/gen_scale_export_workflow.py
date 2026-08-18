#!/usr/bin/env python3
"""Emit generate_artifacts_scale_run.py for a DOM-79203 scale profile.

The generated workflow keeps the CDISC1 SDTM -> ADaM -> TFL fan-out from
flows/dev/flow_5_all_SDTM.py, then adds extra artifact-producing tasks so the
accumulated DATA artifacts match the Novartis file-count/size mix. A single
programmatic dataset export covers both ADaM Datasets and Study Files.
"""

from __future__ import annotations

import argparse
import math
import pathlib
import sys
import textwrap

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from flows.scale_profiles import GIB, SDTM_DOMAINS, profile_batches, profile_totals

SAS_ENVIRONMENT = "SAS Environment"
WORKFLOW_NAME = "export_scale_study"
OUTPUT_NAME = "generate_artifacts_scale_run.py"


def _sdtm_tasks() -> str:
    blocks = []
    for domain in SDTM_DOMAINS:
        blocks.append(
            f"""
    {domain}_task = run_domino_job_task(
        flyte_task_name="{domain} SDTM",
        command="utils/SDTM_transfer/{domain}.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="{domain}", type=FlyteFile[TypeVar("sas7bdat")])],
        use_project_defaults_for_omitted=True,
        use_latest_git_ref=True,
        cache=False,
    )
"""
        )
    return "".join(blocks)


def _adam_tasks() -> str:
    return """
    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam_scale/ADSL.sas",
        inputs=[Input(name="dm", type=FlyteFile[TypeVar("sas7bdat")], value=dm_task["dm"])],
        output_specs=[Output(name="adsl", type=DataArtifact.File(name="adsl.sas7bdat", type="sas7bdat"))],
        use_project_defaults_for_omitted=True,
        use_latest_git_ref=True,
        environment_name=SAS_ENVIRONMENT,
        cache=False,
    )

    adae_task = run_domino_job_task(
        flyte_task_name="Create ADAE Dataset",
        command="prod/adam_scale/ADAE.sas",
        inputs=[
            Input(name="ae", type=FlyteFile[TypeVar("sas7bdat")], value=ae_task["ae"]),
            Input(name="ex", type=FlyteFile[TypeVar("sas7bdat")], value=ex_task["ex"]),
            Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"]),
        ],
        output_specs=[Output(name="adae", type=DataArtifact.File(name="adae.sas7bdat", type="sas7bdat"))],
        use_project_defaults_for_omitted=True,
        use_latest_git_ref=True,
        environment_name=SAS_ENVIRONMENT,
        cache=False,
    )

    adcm_task = run_domino_job_task(
        flyte_task_name="Create ADCM Dataset",
        command="prod/adam_scale/ADCM.sas",
        inputs=[
            Input(name="cm", type=FlyteFile[TypeVar("sas7bdat")], value=cm_task["cm"]),
            Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"]),
        ],
        output_specs=[Output(name="adcm", type=DataArtifact.File(name="adcm.sas7bdat", type="sas7bdat"))],
        use_project_defaults_for_omitted=True,
        use_latest_git_ref=True,
        environment_name=SAS_ENVIRONMENT,
        cache=False,
    )

    adlb_task = run_domino_job_task(
        flyte_task_name="Create ADLB Dataset",
        command="prod/adam_scale/ADLB.sas",
        inputs=[
            Input(name="lb", type=FlyteFile[TypeVar("sas7bdat")], value=lb_task["lb"]),
            Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"]),
        ],
        output_specs=[Output(name="adlb", type=DataArtifact.File(name="adlb.sas7bdat", type="sas7bdat"))],
        use_project_defaults_for_omitted=True,
        use_latest_git_ref=True,
        environment_name=SAS_ENVIRONMENT,
        cache=False,
    )

    admh_task = run_domino_job_task(
        flyte_task_name="Create ADMH Dataset",
        command="prod/adam_scale/ADMH.sas",
        inputs=[
            Input(name="mh", type=FlyteFile[TypeVar("sas7bdat")], value=mh_task["mh"]),
            Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"]),
        ],
        output_specs=[Output(name="admh", type=DataArtifact.File(name="admh.sas7bdat", type="sas7bdat"))],
        use_project_defaults_for_omitted=True,
        use_latest_git_ref=True,
        environment_name=SAS_ENVIRONMENT,
        cache=False,
    )

    advs_task = run_domino_job_task(
        flyte_task_name="Create ADVS Dataset",
        command="prod/adam_scale/ADVS.sas",
        inputs=[
            Input(name="vs", type=FlyteFile[TypeVar("sas7bdat")], value=vs_task["vs"]),
            Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"]),
        ],
        output_specs=[Output(name="advs", type=DataArtifact.File(name="advs.sas7bdat", type="sas7bdat"))],
        use_project_defaults_for_omitted=True,
        use_latest_git_ref=True,
        environment_name=SAS_ENVIRONMENT,
        cache=False,
    )
"""


def _tfl_tasks() -> str:
    return """
    t_pop_task = run_domino_job_task(
        flyte_task_name="Create T_POP Report",
        command="prod/tfl_scale/t_pop.sas",
        inputs=[Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"])],
        output_specs=[Output(name="t_pop", type=ReportArtifact.File(name="t_pop.pdf", type="pdf"))],
        use_project_defaults_for_omitted=True,
        use_latest_git_ref=True,
        environment_name=SAS_ENVIRONMENT,
        cache=False,
    )

    t_ae_rel_task = run_domino_job_task(
        flyte_task_name="Create T_AE_REL Report",
        command="prod/tfl_scale/t_ae_rel.sas",
        inputs=[
            Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"]),
            Input(name="adae", type=FlyteFile[TypeVar("sas7bdat")], value=adae_task["adae"]),
        ],
        output_specs=[Output(name="t_ae_rel", type=ReportArtifact.File(name="t_ae_rel.pdf", type="pdf"))],
        use_project_defaults_for_omitted=True,
        use_latest_git_ref=True,
        environment_name=SAS_ENVIRONMENT,
        cache=False,
    )

    t_vscat_task = run_domino_job_task(
        flyte_task_name="Create T_VSCAT Report",
        command="prod/tfl_scale/t_vscat.sas",
        inputs=[Input(name="advs", type=FlyteFile[TypeVar("sas7bdat")], value=advs_task["advs"])],
        output_specs=[Output(name="t_vscat", type=ReportArtifact.File(name="t_vscat.pdf", type="pdf"))],
        use_project_defaults_for_omitted=True,
        use_latest_git_ref=True,
        environment_name=SAS_ENVIRONMENT,
        cache=False,
    )
"""


def _emit_tasks(profile: str) -> str:
    batches = profile_batches(profile)
    blocks = []
    for index, batch in enumerate(batches):
        outputs = ",\n            ".join(
            f'Output(name="{item.output_name}", type=StudyFilesArtifact.File(name="{item.artifact_filename}"))'
            for item in batch
        )
        batch_bytes = sum(item.size_bytes for item in batch)
        volume_gib = max(10, math.ceil(batch_bytes / GIB) + 4)
        hardware = 'hardware_tier_id="small-k8s",' if batch_bytes >= GIB else ""
        blocks.append(
            f"""
    study_files_batch_{index} = run_domino_job_task(
        flyte_task_name="Emit study files batch {index}",
        command="python /mnt/code/scripts/emit_scale_artifacts.py --profile {profile} --batch {index}",
        output_specs=[
            {outputs}
        ],
        use_project_defaults_for_omitted=True,
        use_latest_git_ref=True,
        volume_size_gib={volume_gib},
        {hardware}
        cache=False,
    )
"""
        )
    return "".join(blocks)


def _export_block(dataset_id: str) -> str:
    return f"""
    from flytekitplugins.domino.artifact import run_launch_export_artifacts_task, ExportArtifactToDatasetsSpec
    run_launch_export_artifacts_task(
        spec_list=[
            ExportArtifactToDatasetsSpec(artifact=DataArtifact, dataset_id="{dataset_id}"),
            ExportArtifactToDatasetsSpec(artifact=StudyFilesArtifact, dataset_id="{dataset_id}"),
        ],
        use_project_defaults_for_omitted=True,
    )
"""


def render(profile: str, dataset_id: str, include_export: bool) -> str:
    file_count, total_bytes = profile_totals(profile)
    header = textwrap.dedent(
        f"""\
        # Generated by flows/gen_scale_export_workflow.py — do not edit.
        # profile={profile} extra_files={file_count} extra_bytes={total_bytes}
        from flytekit import workflow
        from flytekit.types.file import FlyteFile
        from typing import TypeVar
        from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
        from flytekitplugins.domino.artifact import Artifact, DATA, REPORT

        SAS_ENVIRONMENT = "{SAS_ENVIRONMENT}"
        DataArtifact = Artifact("ADaM Datasets", DATA)
        ReportArtifact = Artifact("TFL Reports", REPORT)
        StudyFilesArtifact = Artifact("Study Files", DATA)

        @workflow
        def {WORKFLOW_NAME}(sdtm_dataset_snapshot: str):
        """
    )
    body = (
        _sdtm_tasks()
        + _adam_tasks()
        + _tfl_tasks()
        + _emit_tasks(profile)
        + (_export_block(dataset_id) if include_export else "\n    return\n")
    )
    if include_export:
        body += "\n    return\n"
    return header + body


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, choices=("reduced", "full"))
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--out", default=OUTPUT_NAME)
    parser.add_argument("--skip-export", action="store_true")
    args = parser.parse_args()
    out_path = pathlib.Path(args.out)
    out_path.write_text(render(args.profile, args.dataset_id, include_export=not args.skip_export))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
