* Scale T_POP for DOM-79203. Real SAS PDF from ADSL; no TFL metadata volume required.
libname inputs "/workflow/inputs";
x "mv /workflow/inputs/adsl /workflow/inputs/adsl.sas7bdat";

ods pdf file="/workflow/outputs/t_pop";
title "Scale T_POP";
proc print data=inputs.adsl;
run;
ods pdf close;
