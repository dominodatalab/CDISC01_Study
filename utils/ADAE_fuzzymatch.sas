data work.ae;
  length USUBJID $12 AETERM $40;
  input USUBJID $ AETERM & $40.;
cards;
ABC-001 headache
ABC-002 head ache
ABC-003 nausea
ABC-004 nausia
ABC-005 fever
ABC-006 pyrexia
;
run;

proc python;
submit;

import pandas as pd
from rapidfuzz import process

ae = SAS.sd2df("ae", libref="WORK")

# Dictionary of standard clinical AE terms
standard_terms = ["HEADACHE", "NAUSEA", "FEVER"]

def map_term(term):
    match, score, _ = process.extractOne(term.upper(), standard_terms)
    return match if score > 80 else term.upper()

# Derive coded term
ae["AEDECOD"] = ae["AETERM"].apply(map_term)

# Write back to SAS
SAS.df2sd(ae, "ae_coded", libref="WORK")

endsubmit;
run;

title "AE Coding Results (Verbatim → Standardized Term)";
proc print data=work.ae_coded noobs;
run;
title;