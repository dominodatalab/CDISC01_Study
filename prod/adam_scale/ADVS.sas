/* ADVS: SDTM VS for ADSL subjects, one analysis value per test and visit. */
libname vs xport "/workflow/inputs/vs";
libname inputs "/workflow/inputs";
libname outputs "/workflow/outputs";
x "mv /workflow/inputs/adsl /workflow/inputs/adsl.sas7bdat";

proc sort data=vs.vs out=vs;
    by USUBJID;
run;

data outputs.advs;
    merge inputs.adsl(in=in_adsl) vs(in=in_vs);
    by USUBJID;
    if in_adsl and in_vs;
    length PARAMCD $8;
    PARAMCD = VSTESTCD;
    AVAL = VSSTRESN;
    AVISITN = VISITNUM;
run;
