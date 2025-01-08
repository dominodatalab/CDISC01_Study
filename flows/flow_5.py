from flytekit import workflow
from flytekit.types.file import FlyteFile
from typing import TypeVar, NamedTuple, Tuple
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, EnvironmentRevisionSpecification, EnvironmentRevisionType, DatasetSnapshot
from flytekitplugins.domino.artifact import Artifact, DATA, MODEL, REPORT

sdtm_dataset="SDTMUNBLIND"
sdtm_dataset_snapshot_number=1

# Enter the command below to run this Flow. There is a single Flow input parameter for the SDTM Dataset snapshot
# pyflyte run --remote flow_5.py sdtm_to_adam --sdtm_dataset_snapshot /mnt/imported/data/SDTMBLIND 



@workflow
def sdtm_to_adam(sdtm_dataset_snapshot: str):

    # Move ae from Dataset to Flows node
    ae_task = run_domino_job_task(
        flyte_task_name="ae SDTM",
        command="utils/SDTM_transfer/ae.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="ae", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )
    

    return