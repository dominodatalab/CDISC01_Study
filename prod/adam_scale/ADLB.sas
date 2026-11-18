/* ADLB: SDTM LB for ADSL subjects, one analysis value per test and visit. */
libname lb xport "/workflow/inputs/lb";
libname inputs "/workflow/inputs";
libname outputs "/workflow/outputs";
x "mv /workflow/inputs/adsl /workflow/inputs/adsl.sas7bdat";

proc sort data=lb.lb out=lb;
    by USUBJID;
run;

data outputs.adlb;
    merge inputs.adsl(in=in_adsl) lb(in=in_lb);
    by USUBJID;
    if in_adsl and in_lb;
    length PARAMCD $8;
    PARAMCD = LBTESTCD;
    AVAL = LBSTRESN;
    AVISITN = VISITNUM;
run;
