/* Adverse events by relationship to study drug and planned treatment, from ADAE. */
libname inputs "/workflow/inputs";
x "mv /workflow/inputs/adae /workflow/inputs/adae.sas7bdat";

ods pdf file="/workflow/outputs/t_ae_rel.pdf";

title "Adverse Events by Relationship to Study Drug";
proc freq data=inputs.adae;
    tables AEREL * TRT01P / nocol nopercent;
run;

title "Adverse Events by Body System";
proc freq data=inputs.adae order=freq;
    tables AEBODSYS * TRT01P / nocol nopercent;
run;

ods pdf close;
