* Scale ADAE for DOM-79203. Sequences after ADSL/AE/EX; writes a real sas7bdat.
libname inputs "/workflow/inputs";
libname outputs "/workflow/outputs";
x "mv /workflow/inputs/adsl /workflow/inputs/adsl.sas7bdat";

data outputs.adae;
    set inputs.adsl;
    length AEDECOD $32;
    AEDECOD = "HEADACHE";
run;
