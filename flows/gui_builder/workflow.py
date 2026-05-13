"""
Pharma — Drug Adverse Event Surveillance Pipeline

Fetches real adverse event reports from the FDA OpenFDA API for a given
drug and date range, maps them to SDTM-like domain datasets, derives
ADaM analysis datasets, and produces a safety summary HTML report.

Demo re-run: change drug_name to "insulin" and dates to Q2 2023 to
compare adverse event profiles across drug/time combinations.

Requirements:
    - DSE 6.0+ (contains flytekit + flytekitplugins-domino)
    - pip install pandas requests (in the environment)

Run:
    pyflyte run --remote workflow.py adverse_event_pipeline \
        --drug_name metformin \
        --start_date 20230101 \
        --end_date 20230331 \
        --study_id FAERS-001 \
        --record_limit 100
"""
from flytekit import workflow
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask
from flytekit.types.file import FlyteFile
from typing import TypeVar

# ── Task definitions ──────────────────────────────────────────────────────────

ingest_ae = DominoJobTask(
    name="Ingest AE Reports",
    domino_job_config=DominoJobConfig(
        Command="python examples/pharma_data_engineering/stages/ingest_ae.py",
    ),
    inputs={
        "drug_name":    str,
        "start_date":   str,
        "end_date":     str,
        "record_limit": int,
        "study_id":     str,
    },
    outputs={"raw_events": FlyteFile[TypeVar("csv")]},
    use_latest=True,
)

sdtm_mapping = DominoJobTask(
    name="SDTM Mapping",
    domino_job_config=DominoJobConfig(
        Command="python examples/pharma_data_engineering/stages/sdtm_mapping.py",
    ),
    inputs={
        "raw_events": FlyteFile[TypeVar("csv")],
        "study_id":   str,
    },
    outputs={
        "sdtm_ae": FlyteFile[TypeVar("csv")],
        "sdtm_dm": FlyteFile[TypeVar("csv")],
    },
    use_latest=True,
)

adam_derivation = DominoJobTask(
    name="ADaM Derivation",
    domino_job_config=DominoJobConfig(
        Command="python examples/pharma_data_engineering/stages/adam_derivation.py",
    ),
    inputs={
        "sdtm_ae": FlyteFile[TypeVar("csv")],
        "sdtm_dm": FlyteFile[TypeVar("csv")],
    },
    outputs={
        "adae": FlyteFile[TypeVar("csv")],
        "adsl": FlyteFile[TypeVar("csv")],
    },
    use_latest=True,
)

summary_statistics = DominoJobTask(
    name="Summary Statistics",
    domino_job_config=DominoJobConfig(
        Command="python examples/pharma_data_engineering/stages/summary_statistics.py",
    ),
    inputs={
        "adae":      FlyteFile[TypeVar("csv")],
        "adsl":      FlyteFile[TypeVar("csv")],
        "drug_name": str,
        "study_id":  str,
    },
    outputs={"summary_report": FlyteFile[TypeVar("html")]},
    use_latest=True,
)

# ── Workflow ──────────────────────────────────────────────────────────────────

@workflow
def adverse_event_pipeline(
    drug_name:    str = "metformin",
    start_date:   str = "20230101",
    end_date:     str = "20230331",
    study_id:     str = "FAERS-001",
    record_limit: int = 100,
) -> FlyteFile[TypeVar("html")]:
    r1 = ingest_ae(
        drug_name=drug_name,
        start_date=start_date,
        end_date=end_date,
        record_limit=record_limit,
        study_id=study_id,
    )
    r2 = sdtm_mapping(raw_events=r1.raw_events, study_id=study_id)
    r3 = adam_derivation(sdtm_ae=r2.sdtm_ae, sdtm_dm=r2.sdtm_dm)
    r4 = summary_statistics(
        adae=r3.adae,
        adsl=r3.adsl,
        drug_name=drug_name,
        study_id=study_id,
    )
    return r4.summary_report
