from flytekit import workflow
from flytekit.types.file import FlyteFile
from typing import TypeVar, NamedTuple, Tuple
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, EnvironmentRevisionSpecification, EnvironmentRevisionType, DatasetSnapshot
from flytekitplugins.domino.artifact import Artifact, DATA, MODEL, REPORT


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

    # Move cm from Dataset to Flows node
    cm_task = run_domino_job_task(
        flyte_task_name="cm SDTM",
        command="utils/SDTM_transfer/cm.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="cm", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move dm from Dataset to Flows node
    dm_task = run_domino_job_task(
        flyte_task_name="dm SDTM",
        command="utils/SDTM_transfer/dm.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="dm", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move ds from Dataset to Flows node
    ds_task = run_domino_job_task(
        flyte_task_name="ds SDTM",
        command="utils/SDTM_transfer/ds.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="ds", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )
    # Move ex from Dataset to Flows node
    ex_task = run_domino_job_task(
        flyte_task_name="ex SDTM",
        command="utils/SDTM_transfer/ex.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="ex", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move lb from Dataset to Flows node
    lb_task = run_domino_job_task(
        flyte_task_name="lb SDTM",
        command="utils/SDTM_transfer/lb.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="lb", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move mh from Dataset to Flows node
    mh_task = run_domino_job_task(
        flyte_task_name="mh SDTM",
        command="utils/SDTM_transfer/mh.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="mh", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move qs from Dataset to Flows node
    qs_task = run_domino_job_task(
        flyte_task_name="qs SDTM",
        command="utils/SDTM_transfer/qs.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="qs", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

     # Move relrec from Dataset to Flows node
    relrec_task = run_domino_job_task(
        flyte_task_name="relrec SDTM",
        command="utils/SDTM_transfer/relrec.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="relrec", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move sc from Dataset to Flows node
    sc_task = run_domino_job_task(
        flyte_task_name="sc SDTM",
        command="utils/SDTM_transfer/sc.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="sc", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move se from Dataset to Flows node
    se_task = run_domino_job_task(
        flyte_task_name="se SDTM",
        command="utils/SDTM_transfer/se.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="se", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move suppae from Dataset to Flows node
    suppae_task = run_domino_job_task(
        flyte_task_name="suppae SDTM",
        command="utils/SDTM_transfer/suppae.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="suppae", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )
    
    return