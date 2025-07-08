/*****************************************************************************\
*  ____                  _
* |  _ \  ___  _ __ ___ (_)_ __   ___
* | | | |/ _ \| '_ ` _ \| | '_ \ / _ \
* | |_| | (_) | | | | | | | | | | (_) |
* |____/ \___/|_| |_| |_|_|_| |_|\___/                                               
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : CDISC01
* Program              : import_metadata.sas
* Purpose              : Import External NFS TFL_Metadata to Domino Dataset
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
*  18MAY2023  | Megan Harries  | Original
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
proc sql;
	select count(*) into: count
	from tfl;
quit;

* Loop through the each program;
%macro loop_through;
	
	* Create individual datasets for each observation;
	%macro create(i = );
		data _null_;
			set tfl;
			if _n_ = &i.;
			call symput(catx("_", "prog_name", &i.), strip(ResultDisplayOID));
		run;
		
		data metadata.&&prog_name_&i.;
			set tfl;
			if _n_ = &i then output metadata.&&prog_name_&i.;
		run;
	%mend create;
	
	%do row = 1 %to &count.;
		%create(i = &row.);
	%end;

%mend loop_through;

%loop_through;