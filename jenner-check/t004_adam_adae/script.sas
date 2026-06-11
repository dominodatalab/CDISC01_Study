/*****************************************************************************\
* Sponsor              : Domino
* Study                : CDISC01
* Program              : ADAE.sas  (jenner-check bundle)
* Purpose              : Create ADaM ADAE dataset
* ____________________________________________________________________________
* Adapted for the jenner-check bundle from prod/adam/ADAE.sas (the interactive
* DOMINO_IS_WORKFLOW_JOB=false branch). The derivation is unchanged:
*   1. merge ADSL with SDTM.AE by USUBJID, keep AE records
*   2. derive an analysis visit number from the AE start day (AESTDY)
*   3. sort by USUBJID / VISITNUM
*   4. merge on SDTM.EX by USUBJID / VISITNUM
* The %include "/mnt/code/domino.sas" environment setup is replaced by the
* bundled mock ADSL / SDTM.AE / SDTM.EX (see autoexec). A PROC PRINT of the
* derived ADAE is added so the run produces visible output.
\*****************************************************************************/

data adae;
	merge adam.adsl sdtm.ae (in = ae);
		by usubjid;
	if ae;
	if 1 <= aestdy < 13 then visitnum = 3;
	else if 13 <= aestdy < 161 then visitnum = 4;
	else if 162 <= aestdy then visitnum = 12;
run;

proc sort data = adae out = adae_s;
	by usubjid visitnum;
run;

data adam.adae;
	merge adae_s (in = ae) sdtm.ex;
	by usubjid visitnum;
	if ae;
run;

title "ADaM ADAE - derived adverse events with analysis visit and exposure";
proc print data = adam.adae;
	var usubjid actarm aedecod aesoc aerel aestdy visitnum extrt exdose;
run;
title;
