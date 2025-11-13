/*****************************************************************************\
*  ____                  _
* |  _ \  ___  _ __ ___ (_)_ __   ___
* | | | |/ _ \| '_ ` _ \| | '_ \ / _ \
* | |_| | (_) | | | | | | | | | | (_) |
* |____/ \___/|_| |_| |_|_|_| |_|\___/                                               
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : CDISC01
* Program              : tfl_metadata.sas
* Purpose              : Subset metadata for use in output displays
* ____________________________________________________________________________
* DESCRIPTION                                                    
*                                                                   
* Input files: metadata.{__prog_name}
*              
* Output files: 
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

%macro tfl_metadata();
	data metadata;
		set metadata.&__prog_name.;
	run;

	** create macro variables for all variable names;
	data _null_;
		set metadata;

		* numeric variables;
		array xxx{*} _numeric_;
		do i =1 to dim(xxx);
			call symput(vname(xxx[i]),xxx[i]);
		end;

		* character variables;
		array yyy{*} $ _character_;
		do i =1 to dim(yyy);
			call symput(vname(yyy[i]),yyy[i]);
		end;
	run; 
%mend;
