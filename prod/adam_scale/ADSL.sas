* Scale ADSL for DOM-79203. Generates a small valid SAS dataset so downstream
* ADaM/TFL tasks have real sas7bdat inputs without depending on CDISC01_SDTM.
libname outputs "/workflow/outputs";

data outputs.adsl;
    length USUBJID $8 ACTARM $32 AGE 8 SEX $1;
    USUBJID = "001"; ACTARM = "Placebo";               AGE = 62; SEX = "F"; output;
    USUBJID = "002"; ACTARM = "Xanomeline Low Dose";   AGE = 71; SEX = "M"; output;
    USUBJID = "003"; ACTARM = "Xanomeline High Dose";  AGE = 58; SEX = "F"; output;
    USUBJID = "004"; ACTARM = "Placebo";               AGE = 66; SEX = "M"; output;
run;
