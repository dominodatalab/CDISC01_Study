from flytekit import workflow
from flytekit.types.file import FlyteFile
from typing import TypeVar, NamedTuple, Tuple
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, EnvironmentRevisionSpecification, EnvironmentRevisionType, DatasetSnapshot
from flytekitplugins.domino.artifact import Artifact, DATA, MODEL, REPORT

sdtm_dataset="SDTMUNBLIND"
sdtm_dataset_snapshot_number=1

# Enter the command below to run this Flow. There is a single Flow input parameter for the SDTM Dataset snapshot
# pyflyte run --remote flow_1.py ADaM_only --sdtm_dataset_snapshot /mnt/imported/data/SDTMBLIND 


DataArtifact = Artifact("ADaM Datasets", DATA)


@workflow
def ADaM_only(sdtm_dataset_snapshot: str):

    # Move ae from Dataset to Flows node
    adsl_task = run_domino_job_task(
        flyte_task_name="ae SDTM",
        command="prod/adam_flows/ADSL.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="adsl_dataset", type=DataArtifact.File(name="adsl.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
        cache=True,
        cache_version="1.0"
    )
    
    # Create ADSL dataset. The only input is the SDTM Dataset. 
    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam_flows/ADSL.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="adsl_dataset", type=DataArtifact.File(name="adsl.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
        cache=True,
        cache_version="1.0"
       # dataset_snapshots=[DatasetSnapshot(Name=sdtm_dataset,Version=sdtm_dataset_snapshot_number)]
    )


    return