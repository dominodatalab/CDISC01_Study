from flytekit import workflow
from flytekit.types.file import FlyteFile
from typing import TypeVar, NamedTuple, Tuple
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, EnvironmentRevisionSpecification, EnvironmentRevisionType, DatasetSnapshot
from flytekitplugins.domino.artifact import Artifact, DATA, MODEL, REPORT


# Set these variables for to configure all your task parameters. 
sdtm_dataset="SDTMBLIND" # What Dataset is mounted to your Flow Job. 
sdtm_dataset_snapshot_version=1 # What snapshot of this Dataset is mounted to your Flow Job. 
hardware_tier_name="Small" # What hardware tier your Flow Job uses.
environment_name="SAS Analytics Pro" # What Compute Environment your Flow Job uses.

# Enter the command below to run this Flow. There is a single Flow input parameter for the SDTM Dataset snapshot
# pyflyte run --remote ./flows/dev/flow_dynamic.py adsl --sdtm_dataset_snapshot /mnt/imported/data/SDTMBLIND 


DataArtifact = Artifact("ADaM Datasets", DATA)


@workflow
def adsl(sdtm_dataset_snapshot: str):

    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam/ADSL.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="adsl_dataset", type=DataArtifact.File(name="adsl", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True
    )
 
    adae_task = run_domino_job_task(
        flyte_task_name="Create ADAE Dataset",
        command="prod/adam/ADAE.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adae_dataset", type=DataArtifact.File(name="adae", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True
    )
    
    adcm_task = run_domino_job_task(
        flyte_task_name="Create ADCM Dataset",
        command="prod/adam/ADCM.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adcm_dataset", type=DataArtifact.File(name="adcm", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True
    )

    adlb_task = run_domino_job_task(
        flyte_task_name="Create ADLB Dataset",
        command="prod/adam/ADLB.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adlb_dataset", type=DataArtifact.File(name="adlb", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True
    )

    admh_task = run_domino_job_task(
        flyte_task_name="Create ADMH Dataset",
        command="prod/adam/ADMH.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="admh_dataset", type=DataArtifact.File(name="admh", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True
    )

    advs_task = run_domino_job_task(
        flyte_task_name="Create ADVS Dataset",
        command="prod/adam/ADVS.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="advs_dataset", type=DataArtifact.File(name="advs", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True
    )
    return