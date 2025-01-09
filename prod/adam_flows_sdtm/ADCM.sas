/*****************************************************************************\
*  ____                  _
* |  _ \  ___  _ __ ___ (_)_ __   ___
* | | | |/ _ \| '_ ` _ \| | '_ \ / _ \
* | |_| | (_) | | | | | | | | | | (_) |
* |____/ \___/|_| |_| |_|_|_| |_|\___/
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : CDISC01
* Program              : ADCM.sas
* Purpose              : Create ADaM ADCM dummy dataset
* ____________________________________________________________________________
* DESCRIPTION
*
* Input files:  SDTM.CM
*               ADaM.ADSL
*
* Output files: ADaM.ADCM
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
  x "mv /workflow/inputs/cm /workflow/inputs/cm.sas7bdat";
  x "mv /workflow/inputs/adsl_dataset /workflow/inputs/adsl_dataset.sas7bdat";


data outputs.adcm_dataset;
	merge inputs.adsl_dataset inputs.cm (in = cm);
	by usubjid;
	if cm;
run;
