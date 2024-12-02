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

    #Crete ADSL dataset. The only input is the SDTM Dataset. 
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

    #Crete ADAE dataset. This has two inputs, the SDTM Dataset and the output from the previous task i.e. ADSL. 
    adae_task = run_domino_job_task(
        flyte_task_name="Create ADAE Dataset",
        command="prod/adam_flows/ADAE.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adae_dataset", type=DataArtifact.File(name="adae.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
        cache=True,
        cache_version="1.0"
        #dataset_snapshots=[DatasetSnapshot(Name=sdtm_dataset,Version=sdtm_dataset_snapshot_number)]
    )
    
    adcm_task = run_domino_job_task(
        flyte_task_name="Create ADCM Dataset",
        command="prod/adam_flows/ADCM.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adcm_dataset", type=DataArtifact.File(name="adcm.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
        cache=True,
        cache_version="1.0"
      #  dataset_snapshots=[DatasetSnapshot(Name=sdtm_dataset,Version=sdtm_dataset_snapshot_number)]
    )

    adlb_task = run_domino_job_task(
        flyte_task_name="Create ADLB Dataset",
        command="prod/adam_flows/ADLB.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adlb_dataset", type=DataArtifact.File(name="adlb.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
        cache=True,
        cache_version="1.0"
        #dataset_snapshots=[DatasetSnapshot(Name=sdtm_dataset,Version=sdtm_dataset_snapshot_number)]
    )

    admh_task = run_domino_job_task(
        flyte_task_name="Create ADMH Dataset",
        command="prod/adam_flows/ADMH.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="admh_dataset", type=DataArtifact.File(name="admh.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
        cache=True,
        cache_version="1.0"
      #  dataset_snapshots=[DatasetSnapshot(Name=sdtm_dataset,Version=sdtm_dataset_snapshot_number)]
    )

    advs_task = run_domino_job_task(
        flyte_task_name="Create ADVS Dataset",
        command="prod/adam_flows/ADVS.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="advs_dataset", type=DataArtifact.File(name="advs.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
        cache=True,
        cache_version="1.0"
        #dataset_snapshots=[DatasetSnapshot(Name=sdtm_dataset,Version=sdtm_dataset_snapshot_number)]
    )

    return