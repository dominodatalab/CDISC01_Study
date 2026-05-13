"""
Stage: ADaM Derivation
Derives analysis datasets from SDTM domains:
  - ADSL (Subject-Level Analysis Dataset) — one row per unique subject
  - ADAE (Adverse Events Analysis Dataset) — one row per AE with analysis flags

Inputs:  sdtm_ae (CSV), sdtm_dm (CSV)
Outputs: adae (CSV), adsl (CSV)
"""

import pandas as pd
from pathlib import Path

INPUTS  = Path("/workflow/inputs")
OUTPUTS = Path("/workflow/outputs")
OUTPUTS.mkdir(parents=True, exist_ok=True)


def load_csv(name: str) -> pd.DataFrame:
    p = INPUTS / name
    if not p.exists():
        raise RuntimeError(f"Input '{name}' not found at {p}")
    return pd.read_csv(p)


SEVERITY_NUM = {"MILD": 1, "MODERATE": 2, "SEVERE": 3}


def main():
    ae = load_csv("sdtm_ae")
    dm = load_csv("sdtm_dm")
    print(f"ADaM derivation: AE={len(ae)} rows, DM={len(dm)} rows")

    # ── ADAE ──────────────────────────────────────────────────────────────────
    adae = ae.copy()
    adae["AESEVN"]  = adae["AESEV"].map(SEVERITY_NUM).fillna(0).astype(int)
    adae["ANL01FL"] = "Y"                           # include in analysis population
    adae["SAFFL"]   = "Y"                           # safety population flag
    adae["FATAL"]   = (adae["AEOUT"] == "FATAL").map({True: "Y", False: "N"})

    # SOC-level grouping — simplified mapping by keyword
    def assign_soc(term: str) -> str:
        term = str(term).lower()
        if any(w in term for w in ["cardiac", "heart", "myocardial"]):
            return "Cardiac disorders"
        if any(w in term for w in ["nausea", "vomit", "diarrhea", "abdom"]):
            return "Gastrointestinal disorders"
        if any(w in term for w in ["rash", "itch", "urticaria", "skin"]):
            return "Skin and subcutaneous tissue disorders"
        if any(w in term for w in ["headache", "dizz", "syncope", "neuro"]):
            return "Nervous system disorders"
        if any(w in term for w in ["dyspnea", "cough", "respiratory", "breath"]):
            return "Respiratory, thoracic and mediastinal disorders"
        if any(w in term for w in ["glucose", "blood", "lab", "creatinine"]):
            return "Investigations"
        return "General disorders and administration site conditions"

    adae["AEBODSYS"] = adae["AETERM"].apply(assign_soc)
    adae.to_csv(OUTPUTS / "adae", index=False)
    print(f"ADAE: {len(adae)} rows, {adae['AEBODSYS'].nunique()} SOCs")

    # ── ADSL ──────────────────────────────────────────────────────────────────
    adsl = dm.copy()
    adsl["SAFFL"]   = "Y"
    adsl["ANL01FL"] = "Y"

    # Flag subjects with any serious AE
    serious_subjects = set(ae[ae["AESER"] == "Y"]["USUBJID"])
    adsl["AESERFLT"] = adsl["USUBJID"].isin(serious_subjects).map({True: "Y", False: "N"})

    # Flag subjects with fatal AE
    fatal_subjects = set(ae[ae["AEOUT"] == "FATAL"]["USUBJID"])
    adsl["FATALFL"]  = adsl["USUBJID"].isin(fatal_subjects).map({True: "Y", False: "N"})

    # AE count per subject
    ae_counts = ae.groupby("USUBJID").size().rename("AECNT").reset_index()
    adsl = adsl.merge(ae_counts, on="USUBJID", how="left")
    adsl["AECNT"] = adsl["AECNT"].fillna(0).astype(int)

    adsl.to_csv(OUTPUTS / "adsl", index=False)
    print(f"ADSL: {len(adsl)} subjects, {adsl['AESERFLT'].eq('Y').sum()} with serious AE")


if __name__ == "__main__":
    main()
