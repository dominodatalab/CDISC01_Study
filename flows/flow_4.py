from flytekit import workflow
from flytekit.types.file import FlyteFile
from typing import TypeVar, NamedTuple
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, EnvironmentRevisionSpecification, EnvironmentRevisionType, DatasetSnapshot
from flytekitplugins.domino.artifact import Artifact, DATA, MODEL, REPORT


# # Enter the command below to run this Flow. There are two Flow input parameters. One for the SDTM Dataset snapshot and one for the METADATA dataset snapshot.
# pyflyte run --remote flow_4.py ADaM_TFL_QC --sdtm_dataset_snapshot /mnt/imported/data/SDTMBLIND --metadata_snapshot /mnt/data/METADATA 

DataArtifact = Artifact("ADaM Datasets", DATA)
QCDataArtifact = Artifact("QC ADaM Datasets", DATA)
ReportArtifact = Artifact("TFL Reports", REPORT)
QCReportArtifact = Artifact("QC TFL Reports", REPORT)


@workflow
def ADaM_TFL_QC(sdtm_dataset_snapshot: str, metadata_snapshot: str):

    #PROD 
    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam_flows/ADSL.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="adsl_dataset", type=DataArtifact.File(name="adsl.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    ) 

    #PROD 
    adae_task = run_domino_job_task(
        flyte_task_name="Create ADAE Dataset",
        command="prod/adam_flows/ADAE.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adae_dataset", type=DataArtifact.File(name="adae.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )
    #PROD 
    adcm_task = run_domino_job_task(
        flyte_task_name="Create ADCM Dataset",
        command="prod/adam_flows/ADCM.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adcm_dataset", type=DataArtifact.File(name="adcm.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )
    #PROD 
    adlb_task = run_domino_job_task(
        flyte_task_name="Create ADLB Dataset",
        command="prod/adam_flows/ADLB.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adlb_dataset", type=DataArtifact.File(name="adlb.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
    )
    #PROD 
    admh_task = run_domino_job_task(
        flyte_task_name="Create ADMH Dataset",
        command="prod/adam_flows/ADMH.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="admh_dataset", type=DataArtifact.File(name="admh.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )
    #PROD 
    advs_task = run_domino_job_task(
        flyte_task_name="Create ADVS Dataset",
        command="prod/adam_flows/ADVS.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="advs_dataset", type=DataArtifact.File(name="advs.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )
    #QC 
    qc_adsl_task = run_domino_job_task(
        flyte_task_name="Create QC ADSL Dataset",
        command="qc/adam_flows/qc_ADSL.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="qc_adsl_dataset", type=QCDataArtifact.File(name="qc_adsl.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
    ) 
 
    #QC 
    qc_adae_task = run_domino_job_task(
        flyte_task_name="Create QC ADAE Dataset",
        command="qc/adam_flows/qc_ADAE.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="qc_adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_adsl_task["qc_adsl_dataset"])],
        output_specs=[Output(name="qc_adae_dataset", type=QCDataArtifact.File(name="qc_adae.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )
    #QC 
    qc_adcm_task = run_domino_job_task(
        flyte_task_name="Create QC ADCM Dataset",
        command="qc/adam_flows/qc_ADCM.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="qc_adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_adsl_task["qc_adsl_dataset"])],
        output_specs=[Output(name="qc_adcm_dataset", type=QCDataArtifact.File(name="qc_adcm.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )
    #QC 
    qc_adlb_task = run_domino_job_task(
        flyte_task_name="Create QC ADLB Dataset",
        command="qc/adam_flows/qc_ADLB.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="qc_adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_adsl_task["qc_adsl_dataset"])],
        output_specs=[Output(name="qc_adlb_dataset", type=QCDataArtifact.File(name="qc_adlb.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )
    #QC 
    qc_admh_task = run_domino_job_task(
        flyte_task_name="Create QC ADMH Dataset",
        command="qc/adam_flows/qc_ADMH.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="qc_adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_adsl_task["qc_adsl_dataset"])],
        output_specs=[Output(name="qc_admh_dataset", type=QCDataArtifact.File(name="qc_admh.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )
    #QC 
    qc_advs_task = run_domino_job_task(
        flyte_task_name="Create QC ADVS Dataset",
        command="qc/adam_flows/qc_ADVS.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
                Input(name="qc_adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_adsl_task["qc_adsl_dataset"])],
        output_specs=[Output(name="qc_advs_dataset", type=QCDataArtifact.File(name="qc_advs.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )

    #PROD
    t_pop_task = run_domino_job_task(
        flyte_task_name="Create T_POP Report",
        command="prod/tfl_flows/t_pop.sas",
        inputs=[Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"]),
                Input(name="metadata_snapshot", type=str, value=metadata_snapshot)],
        output_specs=[Output(name="t_pop", type=ReportArtifact.File(name="t_pop.pdf"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )

    #PROD
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

    #PROD
    t_vscat_task = run_domino_job_task(
        flyte_task_name="Create T_VSCAT Report",
        command="prod/tfl_flows/t_vscat.sas",
        inputs=[Input(name="advs_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=advs_task["advs_dataset"]),
                Input(name="metadata_snapshot", type=str, value=metadata_snapshot)],
        output_specs=[Output(name="t_vscat", type=ReportArtifact.File(name="t_vscat.pdf"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )

    #QC
    qc_t_pop_task = run_domino_job_task(
        flyte_task_name="Create QC T_POP Report",
        command="qc/tfl_flows/qc_t_pop.sas",
        inputs=[Input(name="qc_adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_adsl_task["qc_adsl_dataset"]),
                Input(name="metadata_snapshot", type=str, value=metadata_snapshot)],
        output_specs=[Output(name="qc_t_pop", type=QCReportArtifact.File(name="qc_t_pop.pdf"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )

    #QC
    qc_t_ae_rel_task = run_domino_job_task(
        flyte_task_name="Create QC T_AE_REL Report",
        command="qc/tfl_flows/qc_t_ae_rel.sas",
        inputs=[Input(name="qc_adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_adsl_task["qc_adsl_dataset"]),
                Input(name="qc_adae_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_adae_task["qc_adae_dataset"]),
                Input(name="metadata_snapshot", type=str, value=metadata_snapshot)],
        output_specs=[Output(name="qc_t_ae_rel", type=QCReportArtifact.File(name="qc_t_ae_rel.pdf"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )
    
    #QC
    qc_t_vscat_task = run_domino_job_task(
        flyte_task_name="Create QC T_VSCAT Report",
        command="qc/tfl_flows/qc_t_vscat.sas",
        inputs=[Input(name="qc_advs_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=qc_advs_task["qc_advs_dataset"]),
                Input(name="metadata_snapshot", type=str, value=metadata_snapshot)],
        output_specs=[Output(name="qc_t_vscat", type=QCReportArtifact.File(name="qc_t_vscat.pdf"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )

    return 