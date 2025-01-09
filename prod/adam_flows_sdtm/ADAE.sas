/*****************************************************************************\
*  ____                  _
* |  _ \  ___  _ __ ___ (_)_ __   ___
* | | | |/ _ \| '_ ` _ \| | '_ \ / _ \
* | |_| |cds (_) | | | | | | | | | | (_) |
* |____/ \___/|_| |_| |_|_|_| |_|\___/
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : CDISC01
* Program              : ADAE.sas
* Purpose              : Create ADaM ADAE dummy dataset
* ____________________________________________________________________________
* DESCRIPTION
*
* Input files:  SDTM.AE
*				SDTM.EX
*               ADaM.ADSL
*
* Output files: ADaM.ADAE
*
* Macros:       None
*
* Assumptions: making change to test caching make a second edit
*
* ____________________________________________________________________________
* PROGRAM HISTORY
*  10MAY2023  | Megan Harries  | Original
*  19SEP2023  | Petter Olsson  | Added this comment
*  19SEP2023  | Petter Olsson  | Added this comment as a second comment
* ----------------------------------------------------------------------------
\*****************************************************************************/

*********;
** Setup environment including libraries for this reporting effort;
*%include "/mnt/code/domino.sas";

* Assign read/write folders for Flows inputs/outputs;
  libname inputs "/workflow/inputs"; /* All inputs live in this directory at workflow/inputs/<NAME OF INPUT> */ 
  libname outputs "/workflow/outputs"; /* All outputs must go to this directory at workflow/inputs/<NAME OF OUTPUT> */ 

/* Mandatory step to add sas7bdat file extension to inputs */
  x "mv /workflow/inputs/ae /workflow/inputs/ae.sas7bdat";
  x "mv /workflow/inputs/ex /workflow/inputs/ex.sas7bdat";
  x "mv /workflow/inputs/adsl_dataset /workflow/inputs/adsl_dataset.sas7bdat";


data adae_dataset;
	merge inputs.adsl_dataset inputs.ae (in = ae);
		by usubjid;
	if ae;
	if 1 <= aestdy < 13 then visitnum = 3;
	else if 13 <= aestdy < 161 then visitnum = 4;
	else if 162 <= aestdy then visitnum = 12;
run;

proc sort data = adae_dataset out = adae_s;
	by usubjid visitnum;
run;

data outputs.adae_dataset;
	merge adae_s (in = ae) inputs.ex;
	by usubjid visitnum;
	if ae;
run;
