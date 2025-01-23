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
# pyflyte run --remote ./flows/flow_3.py ADaM_only_QC --sdtm_dataset_snapshot /mnt/imported/data/SDTMBLIND

# If you want to give the run a name, then use this command and replace the MY_CUSTOM_NAME argument
# pyflyte run --remote --name MY_CUSTOM_NAME ./flows/flow_3.py ADaM_only_QC --sdtm_dataset_snapshot /mnt/imported/data/SDTMBLIND


# Define two Flow Artifacts called ADaM Dataset and QC ADaM Dataset to tag and group ADaM outputs respectively
DataArtifact = Artifact("ADaM Datasets", DATA)
QCDataArtifact = Artifact("QC ADaM Datasets", DATA)

@workflow
def ADaM_only_QC(sdtm_dataset_snapshot: str):

    #PROD 
    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam/ADSL.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="adsl_dataset", type=DataArtifact.File(name="adsl", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True
    ) 

    #PROD 
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
    #PROD 
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
    #PROD 
    adlb_task = run_domino_job_task(
        flyte_task_name="Create ADLB Dataset",
        command="prod/adam/ADLB.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adlb_dataset", type=DataArtifact.File(name="adlb", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True,
    )
    #PROD 
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
    #PROD 
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
    #QC 
    qc_adsl_task = run_domino_job_task(
        flyte_task_name="Create QC ADSL Dataset",
        command="qc/adam/qc_ADSL.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="qc_adsl_dataset", type=QCDataArtifact.File(name="qc_adsl", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True,
    ) 
 
    #QC 
    qc_adae_task = run_domino_job_task(
        flyte_task_name="Create QC ADAE Dataset",
        command="qc/adam/qc_ADAE.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="qc_adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_adsl_task["qc_adsl_dataset"])],
        output_specs=[Output(name="qc_adae_dataset", type=QCDataArtifact.File(name="qc_adae", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True
    )
    #QC 
    qc_adcm_task = run_domino_job_task(
        flyte_task_name="Create QC ADCM Dataset",
        command="qc/adam/qc_ADCM.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="qc_adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_adsl_task["qc_adsl_dataset"])],
        output_specs=[Output(name="qc_adcm_dataset", type=QCDataArtifact.File(name="qc_adcm", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True
    )
    #QC 
    qc_adlb_task = run_domino_job_task(
        flyte_task_name="Create QC ADLB Dataset",
        command="qc/adam/qc_ADLB.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="qc_adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_adsl_task["qc_adsl_dataset"])],
        output_specs=[Output(name="qc_adlb_dataset", type=QCDataArtifact.File(name="qc_adlb", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True
    )
    #QC 
    qc_admh_task = run_domino_job_task(
        flyte_task_name="Create QC ADMH Dataset",
        command="qc/adam/qc_ADMH.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="qc_adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_adsl_task["qc_adsl_dataset"])],
        output_specs=[Output(name="qc_admh_dataset", type=QCDataArtifact.File(name="qc_admh", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True
    )
    #QC 
    qc_advs_task = run_domino_job_task(
        flyte_task_name="Create QC ADVS Dataset",
        command="qc/adam/qc_ADVS.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="qc_adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_adsl_task["qc_adsl_dataset"])],
        output_specs=[Output(name="qc_advs_dataset", type=QCDataArtifact.File(name="qc_advs", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True
    )

    return 