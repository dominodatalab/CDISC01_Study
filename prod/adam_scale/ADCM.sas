/* ADCM: SDTM CM for ADSL subjects. */
libname cm xport "/workflow/inputs/cm";
libname inputs "/workflow/inputs";
libname outputs "/workflow/outputs";
x "mv /workflow/inputs/adsl /workflow/inputs/adsl.sas7bdat";

proc sort data=cm.cm out=cm;
    by USUBJID;
run;

data outputs.adcm;
    merge inputs.adsl(in=in_adsl) cm(in=in_cm);
    by USUBJID;
    if in_adsl and in_cm;
run;
