from flytekit import workflow
from flytekit.types.file import FlyteFile
from typing import TypeVar, NamedTuple, Tuple
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, EnvironmentRevisionSpecification, EnvironmentRevisionType, DatasetSnapshot
from flytekitplugins.domino.artifact import Artifact, DATA, MODEL, REPORT


# Enter the command below to run this Flow. There is a single Flow input parameter for the SDTM Dataset snapshot
# pyflyte run --remote flow_5.py SDTM_ADaM_TFL --sdtm_dataset_snapshot /mnt/imported/data/SDTMBLIND --metadata_snapshot /mnt/data/METADATA 

DataArtifact = Artifact("ADaM Datasets", DATA)
ReportArtifact = Artifact("TFL Reports", REPORT)

@workflow
def SDTM_ADaM_TFL(sdtm_dataset_snapshot: str, metadata_snapshot: str):

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

    # Move suppdm from Dataset to Flows node
    suppdm_task = run_domino_job_task(
        flyte_task_name="suppdm SDTM",
        command="utils/SDTM_transfer/suppdm.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="suppdm", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move suppds from Dataset to Flows node
    suppds_task = run_domino_job_task(
        flyte_task_name="suppds SDTM",
        command="utils/SDTM_transfer/suppds.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="suppds", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move supplb from Dataset to Flows node
    supplb_task = run_domino_job_task(
        flyte_task_name="supplb SDTM",
        command="utils/SDTM_transfer/supplb.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="supplb", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move sv from Dataset to Flows node
    sv_task = run_domino_job_task(
        flyte_task_name="sv SDTM",
        command="utils/SDTM_transfer/sv.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="sv", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move ta from Dataset to Flows node
    ta_task = run_domino_job_task(
        flyte_task_name="ta SDTM",
        command="utils/SDTM_transfer/ta.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="ta", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move te from Dataset to Flows node
    te_task = run_domino_job_task(
        flyte_task_name="te SDTM",
        command="utils/SDTM_transfer/te.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="te", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move ti from Dataset to Flows node
    ti_task = run_domino_job_task(
        flyte_task_name="ti SDTM",
        command="utils/SDTM_transfer/ti.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="ti", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move ts from Dataset to Flows node
    ts_task = run_domino_job_task(
        flyte_task_name="ts SDTM",
        command="utils/SDTM_transfer/ts.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="ts", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move tv from Dataset to Flows node
    tv_task = run_domino_job_task(
        flyte_task_name="tv SDTM",
        command="utils/SDTM_transfer/tv.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="tv", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Move vs from Dataset to Flows node
    vs_task = run_domino_job_task(
        flyte_task_name="vs SDTM",
        command="utils/SDTM_transfer/vs.py",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="vs", type=FlyteFile[TypeVar('sas7bdat')])],
        use_project_defaults_for_omitted=True,
        environment_name="6.0 Restricted Domino Standard Environment Py3.10 R4.4",
        cache=True,
        cache_version="1.0"
    )

    # Create ADSL dataset from the output of dm_task
    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam_flows_sdtm/ADSL.sas",
        inputs=[Input(name="dm", type=FlyteFile[TypeVar("sas7bdat")], value=dm_task["dm"])],
        output_specs=[Output(name="adsl_dataset", type=DataArtifact.File(name="adsl.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
        cache=True,
        cache_version="1.0"
    )

    # Create ADAE dataset from the output of ae_task, ex_task and adsl_task
    adae_task = run_domino_job_task(
        flyte_task_name="Create ADAE Dataset",
        command="prod/adam_flows_sdtm/ADAE.sas",
        inputs=[Input(name="ae", type=FlyteFile[TypeVar("sas7bdat")], value=ae_task["ae"]),
                Input(name="ex", type=FlyteFile[TypeVar("sas7bdat")], value=ex_task["ex"]),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adae_dataset", type=DataArtifact.File(name="adae.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
        cache=True,
        cache_version="1.0"
    )

    # Create ADCM dataset from the output of cm_task and adsl_task
    adcm_task = run_domino_job_task(
        flyte_task_name="Create ADCM Dataset",
        command="prod/adam_flows_sdtm/ADCM.sas",
        inputs=[Input(name="cm", type=FlyteFile[TypeVar("sas7bdat")], value=cm_task["cm"]),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adcm_dataset", type=DataArtifact.File(name="adcm.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
        cache=True,
        cache_version="1.0"
    )

    # Create ADLB dataset from the output of lb_task and adsl_task
    adlb_task = run_domino_job_task(
        flyte_task_name="Create ADLB Dataset",
        command="prod/adam_flows_sdtm/ADLB.sas",
        inputs=[Input(name="lb", type=FlyteFile[TypeVar("sas7bdat")], value=lb_task["lb"]),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adlb_dataset", type=DataArtifact.File(name="adlb.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
        cache=True,
        cache_version="1.0"
    )

    # Create ADMH dataset from the output of lb_task and adsl_task
    admh_task = run_domino_job_task(
        flyte_task_name="Create ADMH Dataset",
        command="prod/adam_flows_sdtm/ADMH.sas",
        inputs=[Input(name="mh", type=FlyteFile[TypeVar("sas7bdat")], value=mh_task["mh"]),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="admh_dataset", type=DataArtifact.File(name="admh.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
        cache=True,
        cache_version="1.0"
    )

    # Create ADVS dataset from the output of vs_task and adsl_task
    advs_task = run_domino_job_task(
        flyte_task_name="Create ADVS Dataset",
        command="prod/adam_flows_sdtm/ADVS.sas",
        inputs=[Input(name="vs", type=FlyteFile[TypeVar("sas7bdat")], value=vs_task["vs"]),
                Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="advs_dataset", type=DataArtifact.File(name="advs.sas7bdat"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro",
        cache=True,
        cache_version="1.0"
    )

    # Create T_POP report from the output of adsl_task and the metadata dataset launch parameter
    t_pop_task = run_domino_job_task(
        flyte_task_name="Create T_POP Report",
        command="prod/tfl_flows/t_pop.sas",
        inputs=[Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"]),
                Input(name="metadata_snapshot", type=str, value=metadata_snapshot)],
        output_specs=[Output(name="t_pop", type=ReportArtifact.File(name="t_pop.pdf"))],
        use_project_defaults_for_omitted=True,
        environment_name="SAS Analytics Pro"
    )

    # Create T_AE_REL report from the output of adsl_task, adae_task and the metadata dataset launch parameter
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

    # Create T_VSCAT report from the output of adsl_task, adae_task and the metadata dataset launch parameter
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