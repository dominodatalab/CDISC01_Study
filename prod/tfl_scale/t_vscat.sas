* Scale T_VSCAT for DOM-79203.
libname inputs "/workflow/inputs";
x "mv /workflow/inputs/advs /workflow/inputs/advs.sas7bdat";

ods pdf file="/workflow/outputs/t_vscat";
title "Scale T_VSCAT";
proc print data=inputs.advs;
run;
ods pdf close;
