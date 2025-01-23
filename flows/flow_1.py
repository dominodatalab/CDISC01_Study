from flytekit import workflow
from flytekit.types.file import FlyteFile
from typing import TypeVar, NamedTuple, Tuple
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, EnvironmentRevisionSpecification, EnvironmentRevisionType, DatasetSnapshot
from flytekitplugins.domino.artifact import Artifact, DATA, MODEL, REPORT


# Define variables to set the default compute environment and hardware tier for the Flow tasks
environment_name="SAS Analytics Pro"
hardware_tier_name="Small"

# Enter the command below to run this Flow. There is a single Flow input parameter for the SDTM Dataset snapshot
# pyflyte run --remote ./flows/flow_1.py ADaM_only --sdtm_dataset_snapshot /mnt/imported/data/SDTMBLIND 

# If you want to give the run a name, then use this command and replace the MY_CUSTOM_NAME argument
# pyflyte run --remote --name MY_CUSTOM_NAME ./flows/flow_1.py ADaM_only --sdtm_dataset_snapshot /mnt/imported/data/SDTMBLIND 


# Define one Flow Artifact called ADaM Dataset to tag and group all of the ADAM task outputs as
DataArtifact = Artifact("ADaM Datasets", DATA)


@workflow
def ADaM_only(sdtm_dataset_snapshot: str):

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