/*****************************************************************************\
*  ____                  _
* |  _ \  ___  _ __ ___ (_)_ __   ___
* | | | |/ _ \| '_ ` _ \| | '_ \ / _ \
* | |_| |cds (_) | | | | | | | | | | (_) |
* |____/ \___/|_| |_| |_|_|_| |_|\___/
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : CDISC01
* Program              : qc_ADAE.sas
* Purpose              : Create QC ADaM ADAE dummy dataset
* ____________________________________________________________________________
* DESCRIPTION
*
* Input files:  SDTM.AE
*				SDTM.EX
*               qc_ADaM.qc_ADSL
*
* Output files: qc_ADaM.qc_ADAE
*
* Macros:       None
*
* Assumptions: 
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
  x "mv /workflow/inputs/qc_adsl_dataset /workflow/inputs/qc_adsl_dataset.sas7bdat";

/* Read in the SDTM data path input from the Flow input parameter */
data _null__;
    infile '/workflow/inputs/sdtm_snapshot_task_input' truncover;
    input data_path $CHAR100.;
    call symputx('data_path', data_path, 'G');
run;
libname sdtm "&data_path.";
*********;


data qc_adae_dataset;
	merge inputs.qc_adsl_dataset sdtm.ae (in = ae);
		by usubjid;
	if ae;
	if 1 <= aestdy < 13 then visitnum = 3;
	else if 13 <= aestdy < 161 then visitnum = 4;
	else if 162 <= aestdy then visitnum = 12;
run;

proc sort data = qc_adae_dataset out = qc_adae_s;
	by usubjid visitnum;
run;

data outputs.qc_adae_dataset;
	merge qc_adae_s (in = ae) sdtm.ex;
	by usubjid visitnum;
	if ae;
run;
