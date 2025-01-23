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
* Purpose              : Create QC ADaM ADCM dummy dataset
* ____________________________________________________________________________
* DESCRIPTION
*
* Input files:  SDTM.CM
*				ADaM.ADCM
*               ADaMQC.ADSL
*
* Output files: ADaMQC.ADCM
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

%macro run_domino_code;

   /* Retrieve the environment variable */
   %let domino_is_workflow_job = %sysget(DOMINO_IS_WORKFLOW_JOB);

   %put NOTE: DOMINO_IS_WORKFLOW_JOB is &domino_is_workflow_job;

   /* If DOMINO_IS_WORKFLOW_JOB=true, run the following block */
   %if &domino_is_workflow_job = false %then %do;


*********;
** Setup environment including libraries for this reporting effort;
%include "/mnt/code/domino.sas";
*********;

data adamqc.adcm;
	merge adamqc.adsl sdtm.cm (in = cm);
	by usubjid;
	if cm;
run;


%end;
   /* If DOMINO_IS_WORKFLOW_JOB=false, run the second block */
   %else %if &domino_is_workflow_job = true %then %do;


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

data outputs.qc_adcm_dataset;
	merge inputs.qc_adsl_dataset sdtm.cm (in = cm);
	by usubjid;
	if cm;
run;


%end;
   /* Otherwise, log a warning that the variable is not recognized */
   %else %do;
      %put WARNING: DOMINO_IS_WORKFLOW_JOB environment variable not recognized or missing.;
   %end;

%mend run_domino_code;

/* Invoke the macro */
%run_domino_code;

