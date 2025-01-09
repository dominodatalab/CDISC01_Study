/*****************************************************************************\
*  ____                  _
* |  _ \  ___  _ __ ___ (_)_ __   ___
* | | | |/ _ \| '_ ` _ \| | '_ \ / _ \
* | |_| | (_) | | | | | | | | | | (_) |
* |____/ \___/|_| |_| |_|_|_| |_|\___/
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : CDISC01
* Program              : ADMH.sas
* Purpose              : Create ADaM ADMH dummy dataset
* ____________________________________________________________________________
* DESCRIPTION
*
* Input files:  SDTM.MH
*               ADaM.ADSL
*
* Output files: ADaM.ADMH
*
* Macros:       None
*
* Assumptions:
*
* ____________________________________________________________________________
* PROGRAM HISTORY
*  10MAY2023  | Megan Harries  | Original
* ----------------------------------------------------------------------------
\*****************************************************************************/

*********;
** Setup environment including libraries for this reporting effort;
*%include "/mnt/code/domino.sas";

* Assign read/write folders for Flows inputs/outputs;
  libname inputs "/workflow/inputs"; /* All inputs live in this directory at workflow/inputs/<NAME OF INPUT> */ 
  libname outputs "/workflow/outputs"; /* All outputs must go to this directory at workflow/inputs/<NAME OF OUTPUT> */ 

/* Mandatory step to add sas7bdat file extension to inputs */
  x "mv /workflow/inputs/mh /workflow/inputs/mh.sas7bdat";
  x "mv /workflow/inputs/adsl_dataset /workflow/inputs/adsl_dataset.sas7bdat";



data outputs.admh_dataset;
	merge inputs.adsl_dataset inputs.mh (in = mh);
	by usubjid;
	if mh;
run;
