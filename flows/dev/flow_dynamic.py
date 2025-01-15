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
# pyflyte run --remote flow_dynamic.py adsl --sdtm_dataset_snapshot /mnt/imported/data/SDTMBLIND 


DataArtifact = Artifact("ADaM Datasets", DATA)


@workflow
def adsl(sdtm_dataset_snapshot: str):

    #Crete ADSL dataset. The only input is the SDTM Dataset. 
    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="ADSLd.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="adsl_dataset", type=DataArtifact.File(name="adsl.sas7bdat"))],
        dataset_snapshots=[DatasetSnapshot(Name=sdtm_dataset,Version=sdtm_dataset_snapshot_version)],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True,
        #cache=True,
        #cache_version="1.0"
    )

    return