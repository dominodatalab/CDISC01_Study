"""
Stage: Ingest Adverse Event Reports
Fetches drug adverse event reports from the FDA OpenFDA API for a given
drug name and date range, flattens nested JSON to a flat CSV, and writes
it to /workflow/outputs/raw_events.

Inputs (from /workflow/inputs/):
    drug_name     - medicinal product name to filter on (e.g. "metformin")
    start_date    - YYYYMMDD start of receivedate range (e.g. "20230101")
    end_date      - YYYYMMDD end of receivedate range (e.g. "20230331")
    record_limit  - maximum number of records to fetch
    study_id      - study identifier, included in output for traceability

Outputs (to /workflow/outputs/):
    raw_events    - flat CSV of adverse event records
"""

import csv
import json
import os
import sys
from pathlib import Path

import requests

INPUTS  = Path("/workflow/inputs")
OUTPUTS = Path("/workflow/outputs")
OUTPUTS.mkdir(parents=True, exist_ok=True)

OPENFDA_URL = "https://api.fda.gov/drug/event.json"


def read_input(name: str) -> str:
    p = INPUTS / name
    if not p.exists():
        raise RuntimeError(f"Input '{name}' not found at {p}")
    return p.read_text().strip()


def fetch_events(drug_name: str, start_date: str, end_date: str, limit: int) -> list[dict]:
    search = (
        f"receivedate:[{start_date}+TO+{end_date}]"
        f"+AND+patient.drug.medicinalproduct:{drug_name}"
    )
    url = f"{OPENFDA_URL}?search={search}&limit={limit}"
    print(f"Fetching: {url}")
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(
            f"OpenFDA API returned HTTP {r.status_code} for drug='{drug_name}' "
            f"dates={start_date}-{end_date}. Response: {r.text[:300]}"
        )
    data = r.json()
    if "results" not in data:
        raise RuntimeError(
            f"OpenFDA returned no 'results' field for drug='{drug_name}' "
            f"dates={start_date}-{end_date}. Response: {json.dumps(data)[:300]}"
        )
    return data["results"]


def flatten_event(ev: dict, study_id: str) -> dict:
    """Flatten one OpenFDA adverse event record to a single-row dict."""
    # Primary drug (first drug listed)
    drugs = ev.get("patient", {}).get("drug", [])
    primary_drug = drugs[0] if drugs else {}

    # Primary reaction (first MedDRA reaction term)
    reactions = ev.get("patient", {}).get("reaction", [])
    reaction_terms = [r.get("reactionmeddrapt", "") for r in reactions]

    patient = ev.get("patient", {})

    return {
        "STUDYID":       study_id,
        "SAFETYREPORTID": ev.get("safetyreportid", ""),
        "RECEIVEDATE":   ev.get("receivedate", ""),
        "SERIOUS":       ev.get("serious", ""),
        "SERIOUSNESSDEATH": ev.get("seriousnessdeath", ""),
        "SERIOUSNESSHOSPITALIZATION": ev.get("seriousnesshospitalization", ""),
        "DRUG_NAME":     primary_drug.get("medicinalproduct", ""),
        "DRUG_ROUTE":    primary_drug.get("drugadministrationroute", ""),
        "DRUG_INDICATION": primary_drug.get("drugindication", ""),
        "PATIENT_AGE":   patient.get("patientonsetage", ""),
        "PATIENT_AGE_UNIT": patient.get("patientonsetageunit", ""),
        "PATIENT_SEX":   patient.get("patientsex", ""),
        "PATIENT_WEIGHT": patient.get("patientweight", ""),
        "REACTIONS":     "|".join(reaction_terms),
        "REACTION_COUNT": len(reaction_terms),
        "REPORTER_COUNTRY": ev.get("primarysourcecountry", ""),
        "REPORT_TYPE":   ev.get("reporttype", ""),
    }


def main():
    drug_name    = read_input("drug_name")
    start_date   = read_input("start_date")
    end_date     = read_input("end_date")
    record_limit = int(read_input("record_limit"))
    study_id     = read_input("study_id")

    print(f"Study: {study_id} | Drug: {drug_name} | Dates: {start_date}–{end_date} | Limit: {record_limit}")

    events = fetch_events(drug_name, start_date, end_date, record_limit)
    print(f"Fetched {len(events)} adverse event records")

    rows = [flatten_event(ev, study_id) for ev in events]
    if not rows:
        raise RuntimeError("No records returned — cannot proceed with empty dataset")

    out_path = OUTPUTS / "raw_events"
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
