/* Populations and demographics by planned treatment, from ADSL. */
libname inputs "/workflow/inputs";
x "mv /workflow/inputs/adsl /workflow/inputs/adsl.sas7bdat";

ods pdf file="/workflow/outputs/t_pop.pdf";

title "Summary of Populations";
proc freq data=inputs.adsl;
    tables TRT01P * SAFFL / nocol nopercent;
run;

title "Age by Planned Treatment";
proc means data=inputs.adsl n mean std min max maxdec=1;
    class TRT01P;
    var AGE;
run;

title "Sex and Race by Planned Treatment";
proc freq data=inputs.adsl;
    tables (SEX RACE) * TRT01P / nocol nopercent;
run;

ods pdf close;
