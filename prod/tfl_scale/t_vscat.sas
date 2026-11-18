/* Vital signs by parameter, visit and planned treatment, from ADVS. */
libname inputs "/workflow/inputs";
x "mv /workflow/inputs/advs /workflow/inputs/advs.sas7bdat";

ods pdf file="/workflow/outputs/t_vscat.pdf";

title "Vital Signs Summary by Visit";
proc means data=inputs.advs n mean std min max maxdec=1;
    class PARAMCD AVISITN TRT01P;
    var AVAL;
run;

ods pdf close;
