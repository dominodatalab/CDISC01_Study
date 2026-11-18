/* ADSL: one record per randomized CDISC Pilot 01 subject, from SDTM DM. */
libname dm xport "/workflow/inputs/dm";
libname outputs "/workflow/outputs";

proc sort data=dm.dm out=dm;
    by USUBJID;
run;

data outputs.adsl;
    set dm;
    where ARM ne "Screen Failure";
    length TRT01P $40 SAFFL $1;
    TRT01P = ARM;
    SAFFL = "Y";
    keep STUDYID USUBJID SUBJID SITEID AGE AGEU SEX RACE ETHNIC ARMCD ARM TRT01P SAFFL RFSTDTC RFENDTC;
run;
