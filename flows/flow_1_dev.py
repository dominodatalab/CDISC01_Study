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
GitRef_value="prod_netapp"    

# Default for caching, set to True or False
cache = True


# Enter the command below to run this Flow. There is a single Flow input parameter for the SDTM Dataset snapshot
# pyflyte run --remote ./flows/flow_1_dev.py ADaM_only --netapp_volume_snapshot /mnt/netapp-volumes/CDISC01_SDTMBLIND

# If you want to give the run a name, then use this command and replace the MY_CUSTOM_NAME argument
# pyflyte run --remote --name ENTER_RUN_NAME ./flows/flow_1_dev.py ADaM_only --netapp_volume_snapshot /mnt/netapp-volumes/CDISC01_SDTMBLIND


# Define one Flow Artifact called ADaM Dataset to tag and group all of the ADAM task outputs as
DataArtifact = Artifact("ADaM Datasets", DATA)


@workflow
def ADaM_only(netapp_volume_snapshot: str):

    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam/ADSL.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot)],
        output_specs=[Output(name="adsl", type=DataArtifact.File(name="adsl", type="sas7bdat"))],
        hardware_tier_name=hardware_tier_name,
        environment_name=environment_name,
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id="c4b37e73-55bc-4f75-84af-7cd2ea9046ba", Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    return
 
    