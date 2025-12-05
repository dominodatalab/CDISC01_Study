/*****************************************************************************\
*        O                                                                      
*       /                                                                       
*  O---O     _  _ _  _ _  _  _|                                                 
*       \ \/(/_| (_|| | |(/_(_|                                                 
*        O                                                                      
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : H2QMCLZZT
* Program              : compare.SAS
* Purpose              : To compare all adam datasets
* ____________________________________________________________________________
* DESCRIPTION                                                    
*                                                                   
* Input files:  ADAM ADAMQC
*              
* Output files: compare.pdf, adsl.sas7bdat
*               
* Macros:       s_compare
*         
* Assumptions: 
*
* ____________________________________________________________________________
* PROGRAM HISTORY                                                         
*  08JUN2022   | Jake Tombeur   | Original version
\*****************************************************************************/

options user=work;
options errorcheck=normal noerrorabend;

%let _STUDYID = CDISC01;

* Assign read/write folders for Flows inputs/outputs;
  libname inputs "/workflow/inputs"; /* All inputs live in this directory at workflow/inputs/<NAME OF INPUT> */ 
  libname outputs "/workflow/outputs"; /* All outputs must go to this directory at workflow/inputs/<NAME OF OUTPUT> */ 

/* Mandatory step to add sas7bdat file extension to inputs */
  x "mv /workflow/inputs/adsl_dataset /workflow/inputs/adsl_dataset.sas7bdat";
  x "mv /workflow/inputs/adae_dataset /workflow/inputs/adae_dataset.sas7bdat";
  x "mv /workflow/inputs/adcm_dataset /workflow/inputs/adcm_dataset.sas7bdat";
  x "mv /workflow/inputs/adlb_dataset /workflow/inputs/adlb_dataset.sas7bdat";
  x "mv /workflow/inputs/admh_dataset /workflow/inputs/admh_dataset.sas7bdat";
  x "mv /workflow/inputs/advs_dataset /workflow/inputs/advs_dataset.sas7bdat";
  x "mv /workflow/inputs/qc_adsl_dataset /workflow/inputs/qc_adsl_dataset.sas7bdat";
  x "mv /workflow/inputs/qc_adae_dataset /workflow/inputs/qc_adae_dataset.sas7bdat";
  x "mv /workflow/inputs/qc_adcm_dataset /workflow/inputs/qc_adcm_dataset.sas7bdat";
  x "mv /workflow/inputs/qc_adlb_dataset /workflow/inputs/qc_adlb_dataset.sas7bdat";
  x "mv /workflow/inputs/qc_admh_dataset /workflow/inputs/qc_admh_dataset.sas7bdat";
  x "mv /workflow/inputs/qc_advs_dataset /workflow/inputs/qc_advs_dataset.sas7bdat";




%xpt2loc(filespec='/mnt/data/ADAM/adsl.xpt');

data inputs.adsl;
	set adsl;
run;

/* Compare all */
%s_compare(
    base   = inputs(adsl_dataset 
                    adae_dataset 
                    adcm_dataset 
                    adlb_dataset 
                    admh_dataset 
                    advs_dataset),
    comp   = inputs(qc_adsl_dataset 
                    qc_adae_dataset 
                    qc_adcm_dataset 
                    qc_adlb_dataset 
                    qc_admh_dataset 
                    qc_advs_dataset),
    comprpt = 'workflow/outputs/compare.pdf',
    prefix  = ,
    tidyup  = N
);

/* json file from results */
proc sql noprint;
	select count(distinct base) into: all_ds
	from ___LIBALLCOMP;

	select  count(*), count(distinct base) into :all_issues, :ds_issues 
	from ___LIBALLCOMP (where = (compstatus = 'Issues'));

	select count(distinct base) into: ds_clean
	from ___LIBALLCOMP (where = (compstatus = 'Clean'));
quit;

proc json out = "/mnt/artifacts/dominostats.json" pretty;
	write values "Number of Datasets" &all_ds;
    write values "Clean Datasets" &ds_clean;
    write values "Datasets with Issues" &ds_issues;
    write values "Total number of Issues" &all_issues;
run;

/* Output results dataset */
libname compare '/workflow/outputs/COMPARE';
data compare.summary;
	set ___LIBALLCOMP;
run;


/* Removing warnings status from backend so batch job doesnt fail*/
data _null_;
   if &syserr in (4, 6) then call symputx('syserr', 0);
run;

proc options option=config; run;








