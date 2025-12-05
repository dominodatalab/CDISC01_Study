/*****************************************************************************\
*  ____                  _
* |  _ \  ___  _ __ ___ (_)_ __   ___
* | | | |/ _ \| '_ ` _ \| | '_ \ / _ \
* | |_| | (_) | | | | | | | | | | (_) |
* |____/ \___/|_| |_| |_|_|_| |_|\___/                                               
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : CDISC01
* Program              : convert_metadata.sas
* Purpose              : Convert TFL_metadata.xls to sas7bdat's in the NetApp Volume
* ____________________________________________________________________________
* DESCRIPTION                                                    
*                                                                   
* Input files: TFL_Metadata.xlsx
*              
* Output files: t_ae_rel.sas7bdat
*				t_pop.sas7bdat
*				t_vscat.sas7bdat
*               
* Macros:       None
*         
* Assumptions: 
*
* ____________________________________________________________________________
* PROGRAM HISTORY                                   
*  12NOV2025  | ROSS SHARP  | Original
* ----------------------------------------------------------------------------
\*****************************************************************************/

%include "/mnt/code/domino.sas";

* Convert Display sheet of xlsx to sas7bdat;
proc import out = tfl
			datafile = "/mnt/netapp-volumes/MDR/TFL_Metadata.xlsx"
			dbms = xlsx replace;
	sheet = "Display";
	getnames = YES;
run;

* Count number of programs;
proc sql noprint;
	select count(*) into :count
	from tfl;
quit;

* Assign library to output location;
libname tflout "/mnt/netapp-volumes/MDR/TFL_Metadata_sas7bdat";

* Loop through each program;
%macro loop_through;
	
	* Create individual datasets for each observation;
	%macro create(i = );
		data _null_;
			set tfl;
			if _n_ = &i.;
			call symput(catx("_", "prog_name", &i.), strip(ResultDisplayOID));
		run;
		
		data tflout.&&prog_name_&i.;
			set tfl;
			if _n_ = &i then output tflout.&&prog_name_&i.;
		run;
	%mend create;
	
	%do row = 1 %to &count.;
		%create(i = &row.);
	%end;

%mend loop_through;

%loop_through;