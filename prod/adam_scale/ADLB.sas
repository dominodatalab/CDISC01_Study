* Scale ADLB for DOM-79203.
libname inputs "/workflow/inputs";
libname outputs "/workflow/outputs";
x "mv /workflow/inputs/adsl /workflow/inputs/adsl.sas7bdat";

data outputs.adlb;
    set inputs.adsl;
    length PARAM $32;
    PARAM = "Hemoglobin";
    AVAL = 13.5;
run;
