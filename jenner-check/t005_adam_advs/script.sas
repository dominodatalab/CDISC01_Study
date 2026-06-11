/*****************************************************************************\
* Sponsor              : Domino
* Study                : CDISC01
* Program              : ADVS.sas  (jenner-check bundle)
* Purpose              : Create ADaM ADVS dataset
* ____________________________________________________________________________
* Adapted for the jenner-check bundle from prod/adam/ADVS.sas (the interactive
* DOMINO_IS_WORKFLOW_JOB=false branch). The derivation is unchanged: merge the
* subject-level ADSL with the SDTM vital signs domain by USUBJID, keeping the
* VS records. The %include "/mnt/code/domino.sas" environment setup is replaced
* by the bundled mock ADSL / SDTM.VS (see autoexec). A PROC PRINT of the
* derived ADVS is added so the run produces visible output.
\*****************************************************************************/

data adam.advs;
	merge adam.adsl sdtm.vs (in = v);
		by usubjid;
	if v;
run;

title "ADaM ADVS - vital signs analysis dataset (ADSL merged with SDTM.VS)";
proc print data = adam.advs;
	var usubjid actarm age sex visitnum vstestcd vstest vsstresn;
run;
title;
