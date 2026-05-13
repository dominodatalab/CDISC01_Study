"""
Stage: SDTM Mapping
Maps the flat adverse event CSV to CDISC SDTM-like domain datasets:
  - SDTM AE (Adverse Events) domain
  - SDTM DM (Demographics) domain

Inputs:  raw_events (CSV), study_id
Outputs: sdtm_ae (CSV), sdtm_dm (CSV)
"""

import pandas as pd
from pathlib import Path

INPUTS  = Path("/workflow/inputs")
OUTPUTS = Path("/workflow/outputs")
OUTPUTS.mkdir(parents=True, exist_ok=True)


def read_input(name: str) -> str:
    p = INPUTS / name
    if not p.exists():
        raise RuntimeError(f"Input '{name}' not found at {p}")
    return p.read_text().strip()


# MedDRA-like severity mapping based on seriousness flags
def derive_aesev(row) -> str:
    if str(row.get("SERIOUSNESSDEATH", "")) == "1":
        return "SEVERE"
    if str(row.get("SERIOUSNESSHOSPITALIZATION", "")) == "1":
        return "MODERATE"
    if str(row.get("SERIOUS", "")) == "1":
        return "MODERATE"
    return "MILD"


def derive_aeout(row) -> str:
    if str(row.get("SERIOUSNESSDEATH", "")) == "1":
        return "FATAL"
    if str(row.get("SERIOUS", "")) == "1":
        return "NOT RECOVERED/NOT RESOLVED"
    return "RECOVERED/RESOLVED"


def sex_decode(val: str) -> str:
    return {"1": "M", "2": "F", "0": "U"}.get(str(val), "U")


def main():
    raw_events_path = INPUTS / "raw_events"
    if not raw_events_path.exists():
        raise RuntimeError(f"raw_events input not found at {raw_events_path}")

    study_id = read_input("study_id")

    df = pd.read_csv(raw_events_path)
    print(f"SDTM mapping: {len(df)} records, study={study_id}")

    # ── AE domain ─────────────────────────────────────────────────────────────
    # One row per reaction per report
    ae_rows = []
    for _, row in df.iterrows():
        reactions = str(row.get("REACTIONS", "")).split("|") if row.get("REACTIONS") else [""]
        for seq, reaction in enumerate(reactions, 1):
            if not reaction:
                continue
            ae_rows.append({
                "STUDYID":   study_id,
                "DOMAIN":    "AE",
                "USUBJID":   f"{study_id}-{row['SAFETYREPORTID']}",
                "AESEQ":     seq,
                "AETERM":    reaction,
                "AEDECOD":   reaction,           # simplified: no MedDRA lookup
                "AESEV":     derive_aesev(row),
                "AESER":     "Y" if str(row.get("SERIOUS","")) == "1" else "N",
                "AEOUT":     derive_aeout(row),
                "AESTDTC":   row.get("RECEIVEDATE", ""),
                "DRUG_NAME": row.get("DRUG_NAME", ""),
                "TRTEMFL":   "Y",                # all post-market reports are treatment-emergent
            })

    sdtm_ae = pd.DataFrame(ae_rows)
    sdtm_ae.to_csv(OUTPUTS / "sdtm_ae", index=False)
    print(f"SDTM AE: {len(sdtm_ae)} rows")

    # ── DM domain ─────────────────────────────────────────────────────────────
    # One row per unique report (subject)
    dm_rows = []
    for _, row in df.drop_duplicates("SAFETYREPORTID").iterrows():
        dm_rows.append({
            "STUDYID":    study_id,
            "DOMAIN":     "DM",
            "USUBJID":    f"{study_id}-{row['SAFETYREPORTID']}",
            "SUBJID":     row["SAFETYREPORTID"],
            "AGE":        row.get("PATIENT_AGE", ""),
            "AGEU":       row.get("PATIENT_AGE_UNIT", ""),
            "SEX":        sex_decode(row.get("PATIENT_SEX", "")),
            "COUNTRY":    row.get("REPORTER_COUNTRY", ""),
            "ARMCD":      "DRUG",
            "ARM":        row.get("DRUG_NAME", ""),
        })

    sdtm_dm = pd.DataFrame(dm_rows)
    sdtm_dm.to_csv(OUTPUTS / "sdtm_dm", index=False)
    print(f"SDTM DM: {len(sdtm_dm)} rows")


if __name__ == "__main__":
    main()
