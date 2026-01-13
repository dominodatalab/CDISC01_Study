from flytekit import workflow
from flytekit.types.file import FlyteFile
from typing import TypeVar, NamedTuple
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

# Enter the command below to run this Flow. There are two Flow input parameters. One for the SDTM Dataset snapshot and one for the METADATA dataset snapshot.
# pyflyte run --remote ./flows/flow_2_dev.py ADaM_TFL --netapp_volume_snapshot /mnt/netapp-volumes/CDISC01_SDTMBLIND --metadata_snapshot /mnt/netapp-volumes/MDR

# If you want to give the run a name, then use this command and replace the MY_CUSTOM_NAME argument
# pyflyte run --remote --name ENTER_RUN_NAME ./flows/flow_2_dev.py ADaM_TFL --netapp_volume_snapshot /mnt/netapp-volumes/CDISC01_SDTMBLIND --metadata_snapshot /mnt/netapp-volumes/MDR


# Define two Flow Artifacts called ADaM Dataset and TFL Reports to tag and group ADaM and TFL outputs respectively
DataArtifact = Artifact("ADaM Datasets", DATA)
ReportArtifact = Artifact("TFL Reports", DATA)

@workflow
def ADaM_TFL(netapp_volume_snapshot: str, metadata_snapshot: str): 

    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam/ADSL.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot)],
        output_specs=[Output(name="adsl", type=DataArtifact.File(name="adsl.sas7bdat", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="43d47cd8-af02-4d8e-8d0b-ab046102c03b", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    adae_task = run_domino_job_task(
        flyte_task_name="Create ADAE Dataset",
        command="prod/adam/ADAE.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot),
                Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"])],
        output_specs=[Output(name="adae", type=DataArtifact.File(name="adae.sas7bdat", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="43d47cd8-af02-4d8e-8d0b-ab046102c03b", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    adcm_task = run_domino_job_task(
        flyte_task_name="Create ADCM Dataset",
        command="prod/adam/ADCM.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot),
                Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"])],
        output_specs=[Output(name="adcm", type=DataArtifact.File(name="adcm.sas7bdat", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="43d47cd8-af02-4d8e-8d0b-ab046102c03b", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    adlb_task = run_domino_job_task(
        flyte_task_name="Create ADLB Dataset",
        command="prod/adam/ADLB.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot),
                Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"])],
        output_specs=[Output(name="adlb", type=DataArtifact.File(name="adlb.sas7bdat", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="43d47cd8-af02-4d8e-8d0b-ab046102c03b", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    admh_task = run_domino_job_task(
        flyte_task_name="Create ADMH Dataset",
        command="prod/adam/ADMH.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot),
                Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"])],
        output_specs=[Output(name="admh", type=DataArtifact.File(name="admh.sas7bdat", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="43d47cd8-af02-4d8e-8d0b-ab046102c03b", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    advs_task = run_domino_job_task(
        flyte_task_name="Create ADVS Dataset",
        command="prod/adam/ADVS.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot),
                Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"])],
        output_specs=[Output(name="advs", type=DataArtifact.File(name="advs.sas7bdat", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        use_project_defaults_for_omitted=True,
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="43d47cd8-af02-4d8e-8d0b-ab046102c03b", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        cache=cache,
        cache_version="1.0"
    )

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
        cache=False,
        cache_version="1.0"
    )

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
        cache=False,
        cache_version="1.0"
    )

    return
