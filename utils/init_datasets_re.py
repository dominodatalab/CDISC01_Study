from domino import Domino
import os

DOMINO_USER_API_KEY = os.environ['DOMINO_USER_API_KEY']
DOMINO_API_HOST = os.environ['DOMINO_API_HOST']
DOMINO_PROJECT_ID = os.environ['DOMINO_PROJECT_ID']
DOMINO_PROJECT_OWNER = os.environ['DOMINO_PROJECT_OWNER']
DOMINO_PROJECT_NAME = os.environ['DOMINO_PROJECT_NAME']

domino = Domino(f"{DOMINO_PROJECT_OWNER}/{DOMINO_PROJECT_NAME}")

# Create domino datasets

# Required Datasets & Descriptions
REQUIRED = {
    "METADATA": "Internal metadata",
    "COMPARE": "PROC COMPARE datasets for QC",
    "ADAM": "ADAM is created using SDTM data for production",
    "ADAMQC": "ADAMQC is created using SDTM data for qc",
    "TFL": "TFL is created using ADAM for production tfls",
    "TFLQC": "TFLQC is created using ADAM for qc tfls"
}

# Existing Datasets
CURRENT = set(d['datasetName'] for d in domino.datasets_list(project_id=os.environ["DOMINO_PROJECT_ID"]))

# For any required datasets which do not exist 
for key in set(REQUIRED.keys()).difference(CURRENT):
    # Make them
    domino.datasets_create(key, REQUIRED[key])

# From multijob.py
import requests
def submit_api_call(method, endpoint, data=None):
    headers = {
        'X-Domino-Api-Key': DOMINO_USER_API_KEY, 
        'Content-Type': 'application/json',
        'accept': 'application/json',
    }
    url = f'{DOMINO_API_HOST}/{endpoint}'
    response = requests.request(method, url, headers=headers, json=data)

    # Some API responses have JSON bodies, some are empty
    try:
        return response.json()
    except:
        try:
            return response.text
        except:
            return response

# Mount imported datasets

REQUIRED_MOUNTED = {
    "SDTMBLIND",
    "METADATA"
}

# What datasets are currently mounted? And What are they called?
CURRENT_MOUNTED_ID = submit_api_call(
    'GET',
     f"api/projects/v1/projects/{DOMINO_PROJECT_ID}/shared-datasets"
)['dataset']['sharedDatasetIds']

CURRENT_MOUNTED = set()
for id in CURRENT_MOUNTED_ID:
    CURRENT_MOUNTED.add(submit_api_call(
        "GET",
        f"api/datasetrw/v1/datasets/{id}"
    )['dataset']['name'])

# Make SDTM project name
from re import sub
SDTM_PROJECT = sub(r"RE_\w+","SDTM", DOMINO_PROJECT_NAME)

# Get SDTM project ID
SDTM_PROJECT_IDs = {
    x['name']: x['id'] 
    for x in 
    submit_api_call(
        "GET",
        "api/projects/beta/projects?limit=999",
    )['projects']
}

SDTM_PROJECT_ID = SDTM_PROJECT_IDs[SDTM_PROJECT]

# For every unmounted datasets, mount it
# ASSUMPTION: We are only mounting datasets from the SDTM project
SDTM_DATASETS = {
    x['dataset']['name']: x['dataset']['id'] 
    for x in 
    submit_api_call(
        "GET",
        f"api/datasetrw/v2/datasets?projectIdsToInclude={SDTM_PROJECT_ID}",
    )['datasets']
}

for missing_dataset in REQUIRED_MOUNTED.difference(CURRENT_MOUNTED):
    try:
        submit_api_call(
            "POST",
            f"api/projects/v1/projects/{DOMINO_PROJECT_ID}/shared-datasets",
            {
                "datasetId": SDTM_DATASETS[missing_dataset]
            })
    except KeyError:
        print(f"ERROR: Could not find required dataset {missing_dataset} in {SDTM_PROJECT} datasets: {SDTM_DATASETS.keys()}")
    except Exception as e:
        print(e)

# Create TFL artifacts directory
os.makedirs("/mnt/artifacts/TFL", exist_ok=True)
