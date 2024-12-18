/*****************************************************************************\
*  ____                  _
* |  _ \  ___  _ __ ___ (_)_ __   ___
* | | | |/ _ \| '_ ` _ \| | '_ \ / _ \
* | |_| | (_) | | | | | | | | | | (_) |
* |____/ \___/|_| |_| |_|_|_| |_|\___/                                               
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : CDISC01
* Program              : ADSL.sas
* Purpose              : Create ADaM ADSL dummy dataset
* ____________________________________________________________________________
* DESCRIPTION                                                    
*                                                                   
* Input files:  SDTM: DM
*              
* Output files: adam.ADSL123456
*               
* Macros:       None
*         
* Assumptions: 
*
* ____________________________________________________________________________
* PROGRAM HISTORY                                                         
*  09MAY2023  | Megan Harries  | Original
* ----------------------------------------------------------------------------
\*****************************************************************************/

*********;
** Setup environment including libraries for this reporting effort;
*%include "/mnt/code/domino_flows.sas";
*********;


/* Retrieve the value of the DOMINO_IS_WORKFLOW_JOB environment variable */
%let is_workflow_job = %sysget(DOMINO_IS_WORKFLOW_JOB);

/* Check the value and set the libraries accordingly */
%macro set_libpaths;
    %if &is_workflow_job = true %then %do;
        libname inputs "/workflow/inputs";
        libname outputs "/workflow/outputs";
    %end;
    %else %if &is_workflow_job = false %then %do;
        libname inputs "/mnt/imported/data/SDTMBLIND";
        libname outputs "/mnt/artifacts";
    %end;
%mend set_libpaths;

/* Execute the macro to set library paths */
%set_libpaths;

/* Read in the SDTM data path input from the Flow input parameter */
data _null__;
    infile '/workflow/inputs/sdtm_snapshot_task_input' truncover;
    input data_path $CHAR100.;
    call symputx('data_path', data_path, 'G');
run;
libname sdtm "&data_path.";

data outputs.adsl_dataset;
	set sdtm.dm; *reading in the dm sas7bdat file from the SDTM Dataset which is fed in as Flow parameter.
run;