* Scale T_AE_REL for DOM-79203.
libname inputs "/workflow/inputs";
x "mv /workflow/inputs/adsl /workflow/inputs/adsl.sas7bdat";
x "mv /workflow/inputs/adae /workflow/inputs/adae.sas7bdat";

ods pdf file="/workflow/outputs/t_ae_rel";
title "Scale T_AE_REL";
proc print data=inputs.adae;
run;
ods pdf close;
