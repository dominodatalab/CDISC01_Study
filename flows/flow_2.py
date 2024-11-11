from flytekit import workflow
from flytekit.types.file import FlyteFile
from typing import TypeVar, NamedTuple
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, EnvironmentRevisionSpecification, EnvironmentRevisionType, DatasetSnapshot
from flytekitplugins.domino.artifact import Artifact, DATA, MODEL, REPORT


# Enter the command below to run this Flow. There are two Flow input parameters. One for the SDTM Dataset snapshot and one for the METADATA dataset snapshot.
# pyflyte run --remote flow_2.py ADaM_TFL --sdtm_dataset_snapshot /mnt/imported/data/SDTMBLIND --metadata_snapshot /mnt/data/METADATA 

DataArtifact = Artifact("ADaM Datasets", DATA)
ReportArtifact = Artifact("TFL Reports", REPORT)

@workflow
def ADaM_TFL(sdtm_dataset_snapshot: str, metadata_snapshot: str): 

   #Crete ADSL dataset. The only input is the SDTM Dataset. 
    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam_flows/ADSL.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="adsl_dataset", type=DataArtifact.File(name="adsl.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    ) 

    #Crete ADAE dataset. This has two inputs, the SDTM Dataset and the output from the previous task i.e. ADSL. 
    adae_task = run_domino_job_task(
        flyte_task_name="Create ADAE Dataset",
        command="prod/adam_flows/ADAE.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adae_dataset", type=DataArtifact.File(name="adae.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )
    
    adcm_task = run_domino_job_task(
        flyte_task_name="Create ADCM Dataset",
        command="prod/adam_flows/ADCM.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adcm_dataset", type=DataArtifact.File(name="adcm.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )

    adlb_task = run_domino_job_task(
        flyte_task_name="Create ADLB Dataset",
        command="prod/adam_flows/ADLB.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adlb_dataset", type=DataArtifact.File(name="adlb.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )

    admh_task = run_domino_job_task(
        flyte_task_name="Create ADMH Dataset",
        command="prod/adam_flows/ADMH.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="admh_dataset", type=DataArtifact.File(name="admh.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )

    advs_task = run_domino_job_task(
        flyte_task_name="Create ADVS Dataset",
        command="prod/adam_flows/ADVS.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="advs_dataset", type=DataArtifact.File(name="advs.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )

    t_pop_task = run_domino_job_task(
        flyte_task_name="Create T_POP Report",
        command="prod/tfl_flows/t_pop.sas",
        inputs=[Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"]),
                Input(name="metadata_snapshot", type=str, value=metadata_snapshot)],
        output_specs=[Output(name="t_pop", type=ReportArtifact.File(name="t_pop.pdf"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )

    t_ae_rel_task = run_domino_job_task(
        flyte_task_name="Create T_AE_REL Report",
        command="prod/tfl_flows/t_ae_rel.sas",
        inputs=[Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"]),
                Input(name="adae_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adae_task["adae_dataset"]),
                Input(name="metadata_snapshot", type=str, value=metadata_snapshot)],
        output_specs=[Output(name="t_ae_rel", type=ReportArtifact.File(name="t_ae_rel.pdf"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )

    t_vscat_task = run_domino_job_task(
        flyte_task_name="Create T_VSCAT Report",
        command="prod/tfl_flows/t_vscat.sas",
        inputs=[Input(name="advs_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=advs_task["advs_dataset"]),
                Input(name="metadata_snapshot", type=str, value=metadata_snapshot)],
        output_specs=[Output(name="t_vscat", type=ReportArtifact.File(name="t_vscat.pdf"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )

    return