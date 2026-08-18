* Scale ADCM for DOM-79203.
libname inputs "/workflow/inputs";
libname outputs "/workflow/outputs";
x "mv /workflow/inputs/adsl /workflow/inputs/adsl.sas7bdat";

data outputs.adcm;
    set inputs.adsl;
    length CMDECOD $32;
    CMDECOD = "ASPIRIN";
run;
