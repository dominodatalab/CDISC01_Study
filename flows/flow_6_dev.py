from flytekit import workflow
from flytekit.types.file import FlyteFile
from typing import TypeVar, NamedTuple, Tuple
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, EnvironmentRevisionSpecification, EnvironmentRevisionType, DatasetSnapshot, NetAppVolumeSnapshot
from flytekitplugins.domino.artifact import Artifact, DATA, MODEL, REPORT


# Define variables to set the default compute environment and hardware tier for the Flow tasks
environment_name="SAS Analytics Pro"
hardware_tier_name="Small"
GitRef_type="branches"                                     
GitRef_value="CSR"  

# Default for caching, set to True or False
cache = True

# Enter the command below to run this Flow. There is a single Flow input parameter for the SDTM Dataset snapshot
# pyflyte run --remote ./flows/flow_6_dev.py SDTM_ADaM_TFL_P21 --netapp_volume_snapshot /mnt/netapp-volumes/CDISC01_SDTMBLIND --metadata_snapshot /mnt/netapp-volumes/MDR

# If you want to give the run a name, then use this command and replace the MY_CUSTOM_NAME argument
# pyflyte run --remote --name ENTER_RUN_NAME ./flows/flow_6_dev.py SDTM_ADaM_TFL_P21 --netapp_volume_snapshot /mnt/netapp-volumes/CDISC01_SDTMBLIND --metadata_snapshot /mnt/netapp-volumes/MDR



# Define Flow Artifacts for ADaM Datasets, TFL Reports, and Pinnacle21 Validation Reports
DataArtifact = Artifact("ADaM Datasets", DATA)
ReportArtifact = Artifact("TFL Reports", DATA)
P21Artifact = Artifact("Pinnacle21 Validation Report", DATA)


@workflow
def SDTM_ADaM_TFL_P21(netapp_volume_snapshot: str, metadata_snapshot: str):

    # Move ae from Dataset to Flows node
    ae_task = run_domino_job_task(
        flyte_task_name="ae SDTM",
        command="utils/SDTM_transfer/ae.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot)],
        output_specs=[Output(name="ae", type=FlyteFile[TypeVar('sas7bdat')])],
        hardware_tier_name=hardware_tier_name,
        environment_name="GxP R & Python",
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="c4b37e73-55bc-4f75-84af-7cd2ea9046ba", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Move cm from Dataset to Flows node
    cm_task = run_domino_job_task(
        flyte_task_name="cm SDTM",
        command="utils/SDTM_transfer/cm.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot)],
        output_specs=[Output(name="cm", type=FlyteFile[TypeVar('sas7bdat')])],
        hardware_tier_name=hardware_tier_name,
        environment_name="GxP R & Python",
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="c4b37e73-55bc-4f75-84af-7cd2ea9046ba", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Move dm from Dataset to Flows node
    dm_task = run_domino_job_task(
        flyte_task_name="dm SDTM",
        command="utils/SDTM_transfer/dm.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot)],
        output_specs=[Output(name="dm", type=FlyteFile[TypeVar('sas7bdat')])],
        hardware_tier_name=hardware_tier_name,
        environment_name="GxP R & Python",
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="c4b37e73-55bc-4f75-84af-7cd2ea9046ba", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Move ex from Dataset to Flows node
    ex_task = run_domino_job_task(
        flyte_task_name="ex SDTM",
        command="utils/SDTM_transfer/ex.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot)],
        output_specs=[Output(name="ex", type=FlyteFile[TypeVar('sas7bdat')])],
        hardware_tier_name=hardware_tier_name,
        environment_name="GxP R & Python",
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="c4b37e73-55bc-4f75-84af-7cd2ea9046ba", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Move lb from Dataset to Flows node
    lb_task = run_domino_job_task(
        flyte_task_name="lb SDTM",
        command="utils/SDTM_transfer/lb.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot)],
        output_specs=[Output(name="lb", type=FlyteFile[TypeVar('sas7bdat')])],
        hardware_tier_name=hardware_tier_name,
        environment_name="GxP R & Python",
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="c4b37e73-55bc-4f75-84af-7cd2ea9046ba", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Move mh from Dataset to Flows node
    mh_task = run_domino_job_task(
        flyte_task_name="mh SDTM",
        command="utils/SDTM_transfer/mh.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot)],
        output_specs=[Output(name="mh", type=FlyteFile[TypeVar('sas7bdat')])],
        hardware_tier_name=hardware_tier_name,
        environment_name="GxP R & Python",
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="c4b37e73-55bc-4f75-84af-7cd2ea9046ba", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Move vs from Dataset to Flows node
    vs_task = run_domino_job_task(
        flyte_task_name="vs SDTM",
        command="utils/SDTM_transfer/vs.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot)],
        output_specs=[Output(name="vs", type=FlyteFile[TypeVar('sas7bdat')])],
        hardware_tier_name=hardware_tier_name,
        environment_name="GxP R & Python",
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="c4b37e73-55bc-4f75-84af-7cd2ea9046ba", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Create ADSL dataset from the output of dm_task
    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam_flows_sdtm/ADSL.sas",
        inputs=[Input(name="dm", type=FlyteFile[TypeVar("sas7bdat")], value=dm_task["dm"])],
        output_specs=[Output(name="adsl", type=DataArtifact.File(name="adsl.sas7bdat", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Create ADAE dataset from the output of ae_task, ex_task and adsl_task
    adae_task = run_domino_job_task(
        flyte_task_name="Create ADAE Dataset",
        command="prod/adam_flows_sdtm/ADAE.sas",
        inputs=[Input(name="ae", type=FlyteFile[TypeVar("sas7bdat")], value=ae_task["ae"]),
                Input(name="ex", type=FlyteFile[TypeVar("sas7bdat")], value=ex_task["ex"]),
                Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"])],
        output_specs=[Output(name="adae", type=DataArtifact.File(name="adae.sas7bdat", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Create ADCM dataset from the output of cm_task and adsl_task
    adcm_task = run_domino_job_task(
        flyte_task_name="Create ADCM Dataset",
        command="prod/adam_flows_sdtm/ADCM.sas",
        inputs=[Input(name="cm", type=FlyteFile[TypeVar("sas7bdat")], value=cm_task["cm"]),
                Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"])],
        output_specs=[Output(name="adcm", type=DataArtifact.File(name="adcm.sas7bdat", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Create ADLB dataset from the output of lb_task and adsl_task
    adlb_task = run_domino_job_task(
        flyte_task_name="Create ADLB Dataset",
        command="prod/adam_flows_sdtm/ADLB.sas",
        inputs=[Input(name="lb", type=FlyteFile[TypeVar("sas7bdat")], value=lb_task["lb"]),
                Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"])],
        output_specs=[Output(name="adlb", type=DataArtifact.File(name="adlb.sas7bdat", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Create ADMH dataset from the output of lb_task and adsl_task
    admh_task = run_domino_job_task(
        flyte_task_name="Create ADMH Dataset",
        command="prod/adam_flows_sdtm/ADMH.sas",
        inputs=[Input(name="mh", type=FlyteFile[TypeVar("sas7bdat")], value=mh_task["mh"]),
                Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"])],
        output_specs=[Output(name="admh", type=DataArtifact.File(name="admh.sas7bdat", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Create ADVS dataset from the output of vs_task and adsl_task
    advs_task = run_domino_job_task(
        flyte_task_name="Create ADVS Dataset",
        command="prod/adam_flows_sdtm/ADVS.sas",
        inputs=[Input(name="vs", type=FlyteFile[TypeVar("sas7bdat")], value=vs_task["vs"]),
                Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"])],
        output_specs=[Output(name="advs", type=DataArtifact.File(name="advs.sas7bdat", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Create T_POP report from the output of adsl_task and the metadata dataset launch parameter
    t_pop_task = run_domino_job_task(
        flyte_task_name="Create T_POP Report",
        command="prod/tfl/t_pop.sas",
        inputs=[Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"]),
                Input(name="metadata_snapshot", type=str, value=metadata_snapshot)],
        output_specs=[Output(name="t_pop", type=ReportArtifact.File(name="t_pop.pdf", type="pdf"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="202c441a-6506-40dc-a77c-7851df7c11cb", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Create T_AE_REL report from the output of adsl_task, adae_task and the metadata dataset launch parameter
    t_ae_rel_task = run_domino_job_task(
        flyte_task_name="Create T_AE_REL Report",
        command="prod/tfl/t_ae_rel.sas",
        inputs=[Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"]),
                Input(name="adae", type=FlyteFile[TypeVar("sas7bdat")], value=adae_task["adae"]),
                Input(name="metadata_snapshot", type=str, value=metadata_snapshot)],
        output_specs=[Output(name="t_ae_rel", type=ReportArtifact.File(name="t_ae_rel.pdf", type="pdf"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="202c441a-6506-40dc-a77c-7851df7c11cb", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Create T_VSCAT report from the output of adsl_task, adae_task and the metadata dataset launch parameter
    t_vscat_task = run_domino_job_task(
        flyte_task_name="Create T_VSCAT Report",
        command="prod/tfl/t_vscat.sas",
        inputs=[Input(name="advs", type=FlyteFile[TypeVar("sas7bdat")], value=advs_task["advs"]),
                Input(name="metadata_snapshot", type=str, value=metadata_snapshot)],
        output_specs=[Output(name="t_vscat", type=ReportArtifact.File(name="t_vscat.pdf", type="pdf"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="202c441a-6506-40dc-a77c-7851df7c11cb", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    # Pinnacle21 Validation - Validate all ADaM datasets against CDISC standards
    p21_validation_task = run_domino_job_task(
        flyte_task_name="Pinnacle21 CDISC Validation",
        command="prod/validation/p21_validation.py",
        inputs=[
            Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"]),
            Input(name="adae_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adae_task["adae_dataset"]),
            Input(name="adcm_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adcm_task["adcm_dataset"]),
            Input(name="adlb_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adlb_task["adlb_dataset"]),
            Input(name="admh_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=admh_task["admh_dataset"]),
            Input(name="advs_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=advs_task["advs_dataset"])
        ],
        output_specs=[
            Output(name="p21_validation_summary", type=P21Artifact.File(name="p21_validation_summary.txt", type="txt")),
            Output(name="adsl_validation_report", type=P21Artifact.File(name="adsl_validation_report.pdf", type="pdf")),
            Output(name="adae_validation_report", type=P21Artifact.File(name="adae_validation_report.pdf", type="pdf")),
            Output(name="adcm_validation_report", type=P21Artifact.File(name="adcm_validation_report.pdf", type="pdf")),
            Output(name="adlb_validation_report", type=P21Artifact.File(name="adlb_validation_report.pdf", type="pdf")),
            Output(name="admh_validation_report", type=P21Artifact.File(name="admh_validation_report.pdf", type="pdf")),
            Output(name="advs_validation_report", type=P21Artifact.File(name="advs_validation_report.pdf", type="pdf"))
        ],
        hardware_tier_name=hardware_tier_name,
        environment_name="P21 Environment",
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    return