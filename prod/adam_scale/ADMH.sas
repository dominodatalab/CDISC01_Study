* Scale ADMH for DOM-79203.
libname inputs "/workflow/inputs";
libname outputs "/workflow/outputs";
x "mv /workflow/inputs/adsl /workflow/inputs/adsl.sas7bdat";

data outputs.admh;
    set inputs.adsl;
    length MHTERM $32;
    MHTERM = "HYPERTENSION";
run;
