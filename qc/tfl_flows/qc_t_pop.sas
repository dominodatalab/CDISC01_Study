/*****************************************************************************\
*  ____                  _
* |  _ \  ___  _ __ ___ (_)_ __   ___
* | | | |/ _ \| '_ ` _ \| | '_ \ / _ \
* | |_| | (_) | | | | | | | | | | (_) |
* |____/ \___/|_| |_| |_|_|_| |_|\___/                                               
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : CDISC01
* Program              : qc_t_pop.sas
* Purpose              : Create the Summary of Populations Table
* ____________________________________________________________________________
* DESCRIPTION                                                    
*                                                                   
* Input files: qc_ADaM.qc_ADSL
*              
* Output files: qc_t_pop.pdf
*				qc_t_pop.sas7bdat
*               
* Macros:       tfl_metadata_flows.sas
*         
* Assumptions: 
*
* ____________________________________________________________________________
* PROGRAM HISTORY                                   
*  10MAY2023  | Megan Harries  | Original
* ----------------------------------------------------------------------------
\*****************************************************************************/

** Setup environment including libraries for this reporting effort;

* ==================================================================;
* Set SASAUTOS to search for shared macros. 
* This would usually be in domino.sas but putting in program for now. ;
* ==================================================================;
options
  MAUTOSOURCE
  MAUTOLOCDISPLAY 
  sasautos=(
    "/mnt/code/share/macros"
    ,"/mnt/imported/code/SCE_STANDARD_LIB/macros"
    ,SASAUTOS) ;

* Assign read/write folders for Flows inputs/outputs;
  libname inputs "/workflow/inputs"; /* All inputs live in this directory at workflow/inputs/<NAME OF INPUT> */ 
  libname outputs "/workflow/outputs"; /* All outputs must go to this directory at workflow/inputs/<NAME OF OUTPUT> */ 

/* Mandatory step to add sas7bdat file extension to inputs */
  x "mv /workflow/inputs/qc_adsl_dataset /workflow/inputs/qc_adsl_dataset.sas7bdat";

* Assign Metadata Dataset;
  libname metadata "/mnt/data/METADATA";


* Assign values to these macro variables. I have no idea where they are coming from;
  %let __PROG_NAME = t_pop;       
  %let __PROG_EXT = sas;          
  %let __DCUTDTC = %sysfunc(today(), yymmdd10.);
  %let __WORKING_DIR = /mnt/code;
  %let __PROJECT_NAME = MyProject;
  %let __PROTOCOL = MyProtocol;
  %let __PROJECT_TYPE = MyType;
  %let __localdata_path = /mnt/data;
  %let __prog_path = /mnt/code/qc_t_pop.sas;
  %let __results_path = /mnt/results;
  %let __runmode = batch;

*********;




ods path(prepend) work.templat(update);

*Set the template for the output;
proc template;
  define style newstyle;

  class Table  /
			 Rules = Groups
             Frame = void;

  style header
       / just              = c
         fontweight        = medium;

  replace Body from Document /
    bottommargin = 1.54cm
    topmargin = 2.54cm
    rightmargin = 2.54cm
    leftmargin = 2.54cm;

  replace fonts /
           'TitleFont2' = ("Courier New",9pt)
           'TitleFont' = ("Courier New",9pt/*,Bold*/)     /* titles */
           'StrongFont' = ("Courier New",9pt/*,Bold*/)
           'EmphasisFont' = ("Courier New",9pt,Italic)
           'FixedEmphasisFont' = ("Courier New, Courier",9pt,Italic)
           'FixedStrongFont' = ("Courier New, Courier",9pt/*,Bold*/)
           'FixedHeadingFont' = ("Courier New, Courier",9pt/*,Bold*/)
           'BatchFixedFont' = ("SAS Monospace, Courier New, Courier",9pt)
           'FixedFont' = ("Courier New, Courier",9pt)
           'headingEmphasisFont' = ("Courier New",9pt,Bold Italic)
           'headingFont' = ("Courier New",9pt/*,Bold*/)   /* header block */
           'docFont' = ("Courier New",9pt);           /* table cells */

   replace color_list
         "Colors used in the default style" /
         'link' = blue
         'bgH' = white     /* header background */
         'fg' = black
         'bg' = _undef_;
end;
run ;

options orientation = landscape nonumber nodate nobyline;

** adsl and include required variables for table;
data adsl_all (rename = (actarm = trta));
	length trtan agen sexn 8.;
	set inputs.qc_adsl_dataset;
	
	if actarm = "Placebo" then trtan = 1;
	else if actarm = "Xanomeline Low Dose" then trtan = 2;
	else if actarm = "Xanomeline High Dose" then trtan = 3;

	if age < 60 then agen = 1;
	else if 60 <= age < 65 then agen = 2;
	else if 65 <= age < 70 then agen = 3;
	else if 70 <= age < 75 then agen = 4;
	else if 75 <= age < 80 then agen = 5;
	else if 80 <= age then agen = 6;
	
	if sex = 'M' then sexn = 1;
	if sex = 'F' then sexn = 2;
run;

** observations in the population, and the parameters specified in SAP;
data adsl (keep = usubjid trta trtan age agen sex sexn);
    set adsl_all(where = (trtan ne .));
run;

** create macro for counting number of placebo participants;
proc sql noprint;
    select count(distinct usubjid)
    into :placebo_n
    from adsl(where = (trta = "Placebo"));
quit;

** create macro for counting number of Xanomeline Low Dose participants;
proc sql noprint;
    select count(distinct usubjid)
    into :low_dose_n
    from adsl(where = (trta = "Xanomeline Low Dose"));
quit;

** create macro for counting number of Xanomeline High Dose participants;
proc sql noprint;
    select count(distinct usubjid)
    into :high_dose_n
    from adsl(where = (trta = "Xanomeline High Dose"));
quit;

** create macro for each variable results;
** calculate number of unique subjects with post-baseline results;
proc sql;
    create table total_age as
    select trta, count(distinct usubjid) as count_age
    from adsl
    group by trta;
quit;

** calculate number of unique subjects for each age group;
%macro age_data(agen = );
	data age&agen.;
	    set adsl;
	    where agen = &agen.;
	run;

	proc sql;
	    create table total_age&agen. as
	    select trta, count(distinct usubjid) as n&agen.
	    from age&agen.
	    group by trta;
	quit;
%mend age_data;   

%age_data(agen = 1);
%age_data(agen = 2);
%age_data(agen = 3);
%age_data(agen = 4);
%age_data(agen = 5);
%age_data(agen = 6);

** merge the counts and calculate percentages;
data results;
    merge total_age total_age1 total_age2 total_age3 total_age4 total_age5 total_age6;
    by trta;
	if n1 ne . then p1 = cats("(", put(100*n1/count_age, 6.1), ")");
	if n2 ne . then p2 = cats("(", put(100*n2/count_age, 6.1), ")");
	if n3 ne . then p3 = cats("(", put(100*n3/count_age, 6.1), ")");
	if n4 ne . then p4 = cats("(", put(100*n4/count_age, 6.1), ")");
	if n5 ne . then p5 = cats("(", put(100*n5/count_age, 6.1), ")");
	if n6 ne . then p6 = cats("(", put(100*n6/count_age, 6.1), ")");
run;

** concatenate results for any parameter data;
data results_c;
    length results1 results2 results3 results4 results5 results6 $32;
    set results;
    
    ** convert post baseline count to character;
    count_age_c = "";
    
    ** if 100% then no decimal places;
    if p1 = "(100.0)" then p1 = "(100)";
	if p2 = "(100.0)" then p2 = "(100)";
    if p3 = "(100.0)" then p3 = "(100)";
	if p4 = "(100.0)" then p4 = "(100)";
    if p5 = "(100.0)" then p5 = "(100)";
	if p6 = "(100.0)" then p6 = "(100)";

    
    ** if 0% then only n = 0 is displayed, no event or percentage;
	** concatenate n and p;
    if p1 = " " then results1 = "0";
        else results1 = catx(" ", put(n1, 8.), p1);
    if p2 = " " then results2 = "0";
        else results2 = catx(" ", put(n2, 8.), p2);
    if p3 = " " then results3 = "0";
        else results3 = catx(" ", put(n3, 8.), p3);
    if p4 = " " then results4 = "0";
        else results4 = catx(" ", put(n4, 8.), p4);
    if p5 = " " then results5 = "0";
        else results5 = catx(" ", put(n5, 8.), p5);
    if p6 = " " then results6 = "0";
        else results6 = catx(" ", put(n6, 8.), p6);
run;           

** transpose any results dataset;
options validvarname=v7;
proc transpose data = results_c out = results_t name = agegroup;
    id trta;
    var count_age_c results1 results2 results3 results4 results5 results6;
run;


** add parameter identifier and order variable;
data order_results(rename = (Xanomeline_Low_Dose = Low_Dose Xanomeline_High_Dose = High_Dose));
	length order1 8. ageresults $50 stat $8;
    set results_t;
	if agegroup = "count_age_c" then do;
		order1 = 1;
		ageresults = "";
		stat = "";
	end;
	else do;
		order1 = input(substr(agegroup, 8), 8.)+1;
		stat = "n (%)";
	end;

	if agegroup = "results1" then ageresults = "Less than 60 years old";
	else if agegroup = "results2" then ageresults = "60 years old <= age < 65 years old";
	else if agegroup = "results3" then ageresults = "65 years old <= age < 70 years old";
	else if agegroup = "results4" then ageresults = "70 years old <= age < 75 years old";
	else if agegroup = "results5" then ageresults = "75 years old <= age < 80 years old";
	else if agegroup = "results6" then ageresults = "80 years and older";
run;

*include metadata;
data metadata;
		set metadata.t_pop;
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

** create the table output;

ods pdf file = "/workflow/outputs/qc_t_pop"
		style = newstyle;
        
ods noproctitle;
ods escapechar = "^";

** add titles to output;
title1 justify = left "Domino" justify = right "Page ^{thispage} of ^{lastpage}";
title2 "&DisplayName.";
title3 "&DisplayTitle.";
title4 "&Title1.";

** justify contents to decimal places;
proc report data = order_results headline split = "*" style(report) = {width = 100% cellpadding = 3} out = outputs.qc_t_pop_data;
        column  (order1 ageresults stat placebo low_dose high_dose);
        
        ** order variables;
        define order1 / order noprint;
        
        define ageresults / "*Age Group" style(column) = {just = l asis = on width = 30%} style(header) = {just = l asis = on};
        define stat / "*Statistic" style(column) = {just = l width = 10%};
        define placebo / "Placebo* (N=%cmpres(&placebo_n))" style(column) = {just = d width = 18%};
        define low_dose / "Xanomeline Low Dose* (N=%cmpres(&low_dose_n))" style(column) = {just = d width = 20%};
        define high_dose / "Xanomeline High Dose* (N=%cmpres(&high_dose_n))" style(column) = {just = d width = 20%};
        
        ** add footnotes describing the critical codes;
        footnote1 justify = left "&Footer1.";
        footnote2 justify = left "&Footer2.";
        footnote3 justify = left "&Footer3.";
run;
    
ods pdf close;


