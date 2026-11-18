/* ADAE: SDTM AE for ADSL subjects, with the dose in effect at AE onset from EX. */
libname ae xport "/workflow/inputs/ae";
libname ex xport "/workflow/inputs/ex";
libname inputs "/workflow/inputs";
libname outputs "/workflow/outputs";
x "mv /workflow/inputs/adsl /workflow/inputs/adsl.sas7bdat";

proc sort data=ae.ae out=ae;
    by USUBJID;
run;

data adae;
    merge inputs.adsl(in=in_adsl) ae(in=in_ae);
    by USUBJID;
    if in_adsl and in_ae;
    /* EX records one dosing period per visit: 3 (days 1-13), 4 (14-161), 12 (162+). */
    if AESTDY < 14 then VISITNUM = 3;
    else if AESTDY < 162 then VISITNUM = 4;
    else VISITNUM = 12;
run;

proc sort data=adae;
    by USUBJID VISITNUM;
run;

proc sort data=ex.ex(keep=USUBJID VISITNUM EXTRT EXDOSE EXDOSU) out=ex nodupkey;
    by USUBJID VISITNUM;
run;

data outputs.adae;
    merge adae(in=in_ae) ex;
    by USUBJID VISITNUM;
    if in_ae;
run;
