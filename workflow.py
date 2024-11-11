from flytekit import workflow
from flytekit.types.file import FlyteFile
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask
from flytekitplugins.domino.artifact import Artifact, DATA, MODEL, REPORT
from typing import TypeVar, NamedTuple

#pyflyte run --remote workflow.py generate_artifacts

# may use any name and the type DATA, MODEL or REPORT
DataArtifact = Artifact(name="My Data", type=DATA)

final_outputs = NamedTuple(
    "final_outputs",
    random1=DataArtifact.File(name="random1.csv"),
    random2=DataArtifact.File(name="random2.csv"),
)

@workflow
def generate_artifacts() -> final_outputs: 
    random_csv_job = DominoJobTask(
        name="Generate CSV data",
        domino_job_config=DominoJobConfig(Command="python random-csv.py"),
        inputs={'rows': int, 'cols': int},
        outputs={'random_data': FlyteFile[TypeVar("csv")]},
        use_latest=True
    )

    # produce one CSV file with 10 rows
    random1 = random_csv_job(rows=10, cols=10)
    # and another CSV file with 20 rows
    random2 = random_csv_job(rows=20, cols=10)

    return final_outputs(random1.random_data, random2.random_data)