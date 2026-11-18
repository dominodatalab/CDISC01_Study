/* ADMH: SDTM MH for ADSL subjects. */
libname mh xport "/workflow/inputs/mh";
libname inputs "/workflow/inputs";
libname outputs "/workflow/outputs";
x "mv /workflow/inputs/adsl /workflow/inputs/adsl.sas7bdat";

proc sort data=mh.mh out=mh;
    by USUBJID;
run;

data outputs.admh;
    merge inputs.adsl(in=in_adsl) mh(in=in_mh);
    by USUBJID;
    if in_adsl and in_mh;
run;
