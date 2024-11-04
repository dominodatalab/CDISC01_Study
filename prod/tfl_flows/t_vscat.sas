/*****************************************************************************\
*  ____                  _
* |  _ \  ___  _ __ ___ (_)_ __   ___
* | | | |/ _ \| '_ ` _ \| | '_ \ / _ \
* | |_| | (_) | | | | | | | | | | (_) |
* |____/ \___/|_| |_| |_|_|_| |_|\___/                                               
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : CDISC01
* Program              : t_vscat.sas
* Purpose              : Create the Categorical Summary Table
* ____________________________________________________________________________
* DESCRIPTION                                                    
*                                                                   
* Input files: ADaM.ADVS
*              
* Output files: t_vscat.pdf
*				t_vscat.sas7bdat
*               
* Macros:       tfl_metadata.sas
*         
* Assumptions: a
*
* ____________________________________________________________________________
* PROGRAM HISTORY                                                         
*  09MAY2023  | Megan Harries  | Original
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

* Assign values to these macro variables. I have no idea where they are coming from;
  %let __PROG_NAME = t_vscat;       
  %let __PROG_EXT = sas;          
  %let __DCUTDTC = %sysfunc(today(), yymmdd10.);
  %let __WORKING_DIR = /mnt/code;
  %let __PROJECT_NAME = MyProject;
  %let __PROTOCOL = MyProtocol;
  %let __PROJECT_TYPE = MyType;
  %let __localdata_path = /mnt/data;
  %let __prog_path = /mnt/code/t_vscat.sas;
  %let __results_path = /mnt/artifacts/results;
  %let __runmode = batch;

* Assign read/write folders for Flows inputs/outputs;
  libname inputs "/workflow/inputs"; /* All inputs live in this directory at workflow/inputs/<NAME OF INPUT> */ 
  libname outputs "/workflow/outputs"; /* All outputs must go to this directory at workflow/inputs/<NAME OF OUTPUT> */ 

/* Mandatory step to add sas7bdat file extension to inputs */
  x "mv /workflow/inputs/advs_dataset /workflow/inputs/advs_dataset.sas7bdat";

/* Read in the METADATA data path input from the Flow input parameter */
data _null__;
    infile '/workflow/inputs/metadata_snapshot' truncover;
    input metadata_path $CHAR100.;
    call symputx('metadata_path', metadata_path, 'G');
run;
libname sdtm "&metadata_path.";

* Assign Metadata Dataset;
  libname metadata "&metadata_path.";


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

** vital signs adam and include required variables for table;
data advs (rename = (visitnum = avisitn actarm = trta vstest = param vstestcd = paramcd vsstresn = aval));
	length trtan paramn 8. crit1cd $1;
	set inputs.advs_dataset;
	
	if actarm = "Placebo" then trtan = 1;
	else if actarm = "Xanomeline Low Dose" then trtan = 2;
	else if actarm = "Xanomeline High Dose" then trtan = 3;
	
	if vstestcd = "SYSBP" then paramn = 1;
	else if vstestcd = "DIABP" then paramn = 2;
	else if vstestcd = "PULSE" then paramn = 3;

	** 1: Systolic bp, 2: Diastolic bp, 3: Heart rate;
	if paramn = 1 and vsstresn = . then crit1cd = "";
		else if paramn = 1 and vsstresn < 90 then crit1cd = "L";
		else if paramn = 1 and vsstresn > 140 then crit1cd = "H";
	if paramn = 2 and vsstresn = . then crit1cd = "";
		else if paramn = 2 and vsstresn < 60 then crit1cd = "L";
		else if paramn = 2 and vsstresn > 90 then crit1cd = "H";
	if paramn = 3 and vsstresn = . then crit1cd = "";
		else if paramn = 3 and vsstresn < 60 then crit1cd = "L";
		else if paramn = 3 and vsstresn > 100 then crit1cd = "H";
run;

** observations in the population, post-baseline visits and the parameters specified in SAP;
data post_base (keep = usubjid trta trtan param paramcd paramn crit1cd);
    set advs;
    where avisitn > 2 and paramcd in ("SYSBP", "DIABP", "PULSE");
run;

** create macro for counting number of placebo participants;
proc sql noprint;
    select count(distinct usubjid)
    into :placebo_n
    from advs(where = (trta = "Placebo"));
quit;

** create macro for counting number of Xanomeline Low Dose participants;
proc sql noprint;
    select count(distinct usubjid)
    into :low_dose_n
    from advs(where = (trta = "Xanomeline Low Dose"));
quit;

** create macro for counting number of Xanomeline High Dose participants;
proc sql noprint;
    select count(distinct usubjid)
    into :high_dose_n
    from advs(where = (trta = "Xanomeline High Dose"));
quit;

** create datasets for each variable's results;
data pb_sysbp;
    set post_base;
    where paramcd = "SYSBP";
run;

data pb_diabp;
    set post_base;
    where paramcd = "DIABP";
run;

data pb_hr;
    set post_base;
    where paramcd = "PULSE";
run;


**** any results ****;
** calculate number of unique subjects with post-baseline results;
proc sql;
    create table total_pb as
    select trta, count(distinct usubjid) as count_pb
    from post_base
    group by trta;
quit;

** calculate number of unique subjects with high or low post-baseline results and number of events;
proc sql;
    create table total_criteria as
    select trta, count(distinct usubjid) as n, count(usubjid) as e
    from post_base(where = (crit1cd ne ""))
    group by trta;
quit;

** merge the counts and calculate percentages;
data any_results;
    merge total_pb total_criteria;
    by trta;
    if n ne . then p = cats("(", put(100*n/count_pb, 6.1), ")");
run;

** create macro for each variable results;
%macro results(variable = );
    ** calculate number of unique subjects with post-baseline results;
    proc sql;
        create table total_pb_&variable. as
        select trta, count(distinct usubjid) as count_pb
        from pb_&variable.
        group by trta;
    quit;
    
    ** calculate number of unique subjects with high post-baseline results and number of events;
    proc sql;
        create table total_&variable._h as
        select trta, count(distinct usubjid) as n_h, count(usubjid) as e_h
        from pb_&variable.(where = (crit1cd = "H"))
        group by trta;
    quit;
    
    ** calculate number of unique subjects with low post-baseline results and number of events;
    proc sql;
        create table total_&variable._l as
        select trta, count(distinct usubjid) as n_l, count(usubjid) as e_l
        from pb_&variable.(where = (crit1cd = "L"))
        group by trta;
    quit;
    
    ** merge the counts and calculate percentages;
    data &variable._results;
        merge total_pb_&variable. total_&variable._h total_&variable._l;
        by trta;
        if n_h ne . then p_h = cats("(", put(100*n_h/count_pb, 6.1), ")");
        if n_l ne . then p_l = cats("(", put(100*n_l/count_pb, 6.1), ")");
    run;
%mend;

%results(variable = sysbp);
%results(variable = diabp);
%results(variable = hr);

** concatenate results for any parameter data;
data any_results_c;
    length results $32;
    set any_results;
    
    ** convert post baseline count to character;
    count_pb_c = put(count_pb, 8.);
    
    ** if 100% then no decimal places;
    if p = "(100.0)" then p = "(100)";
    
    ** if 0% then only n = 0 is displayed, no event or percentage;
    if p = " " then results = "0";
        ** concatenate n p and e;
        else results = catx(" ", put(n, 8.), p, put(e, 8.));
    
    name = "";
run;    

** create macro to concatenate results for each variable;
%macro concatenate_results(variable = );
    data &variable._results_c;
        length results_l results_h $32;
        set &variable._results;
        
        ** convert post baseline count to character;
        count_pb_c = put(count_pb, 8.);
        
        ** if 100% then no decimal places;
        if p_l = "(100.0)" then p_l = "(100)";
        if p_h = "(100.0)" then p_h= "(100)";
        
        ** if 0% then only n = 0 is displayed, no event or percentage;
        if p_l = " " then results_l = "0";
            ** concatenate n p and e;
            else results_l = catx(" ", put(n_l, 8.), p_l, put(e_l, 8.));
        ** if 0% then only n = 0 is displayed, no event or percentage;
        if p_h = " " then results_h = "0";
            ** concatenate n p and e;
            else results_h = catx(" ", put(n_h, 8.), p_h, put(e_h, 8.));
            
        name = "";
    run;
%mend;
    
%concatenate_results(variable = sysbp);  
%concatenate_results(variable = diabp);  
%concatenate_results(variable = hr);        

options validvarname=v7;
** transpose any results dataset;
proc transpose data = any_results_c out = any_results_t;
    id trta;
    var name count_pb_c results;
run;

** create macro to transpose parameter datasets;
%macro transpose_datasets(parameter = );
    proc transpose data = &parameter._results_c out = &parameter._results_t;
        id trta;
        var name count_pb_c results_l results_h;
    run;
%mend; 

%transpose_datasets(parameter = sysbp);
%transpose_datasets(parameter = diabp);
%transpose_datasets(parameter = hr);

** add parameter identifier and order variable;
data stack_results;
    set any_results_t (in = a) sysbp_results_t (in = b) diabp_results_t (in = c) hr_results_t (in = d);
    if a then do;
        parameter = "ANY";
        order1 = 1;
        end;
        else if b then do;
            parameter = "SYS";
            order1 = 2;
            end;
        else if c then do;
            parameter = "DIA";
            order1 = 3;
            end;
        else if d then do;
            parameter = "HR";
            order1 = 4;
            end;
run;

** create param_results column;
data add_param_results_stat;
    length param_results $50 stat $8;
    set stack_results (rename = (Xanomeline_Low_Dose = Low_Dose Xanomeline_High_Dose = High_Dose));
    
    if _NAME_ = "name" then do;
        order2 = 1;
        if parameter = "ANY" then param_results = "Any result";
            else if parameter = "SYS" then param_results = "Systolic blood pressure";
            else if parameter = "DIA" then param_results = "Diastolic blood pressure";
            else if parameter = "HR" then param_results = "Heart Rate";
    end;
    if _NAME_ = "count_pb_c" then do;
        order2 = 2;
        param_results = "  Patients with post-baseline results";
    end;
    if _NAME_ = "results" then do;
        order2 = 3;
        param_results = "  Results meeting criteria of interest";
    end;
    if _NAME_ = "results_l" then do;
        order2 = 3;
        if parameter = "SYS" then param_results = "    <90 mmHg";
            else if parameter = "DIA" then param_results = "    <60 mmHg";
            else if parameter = "HR" then param_results = "    <60 beats/min";
    end;
    if _NAME_ = "results_h" then do;
        order2 = 4;
        if parameter = "SYS" then param_results = "    >140 mmHg";
            else if parameter = "DIA" then param_results = "    >90 mmHg";
            else if parameter = "HR" then param_results = "    >100 beats/min";
    end;
    
    ** create statistic column;
    if _NAME_ = "count_pb_c" then stat = "n";
        else if _NAME_ in ("results", "results_l", "results_h") then stat = "n (%) e";
run;

*include metadata;
data metadata;
		set metadata.t_vscat;
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

ods pdf file = "/workflow/outputs/t_vscat"
        style = newstyle;
        
ods noproctitle;
ods escapechar = "^";

** add titles to output;
title1 justify = left "Domino" justify = right "Page ^{thispage} of ^{lastpage}";
title2 "&DisplayName.";
title3 "&DisplayTitle.";
title4 "&Title1.";

** justify contents to decimal places;
proc report data = add_param_results_stat headline split = "*" style(report) = {width = 100% cellpadding = 3};
        column  (order1 order2 param_results stat placebo low_dose high_dose);
        
        ** order variables;
        define order1 / order noprint;
        define order2 / order noprint;
        
        define param_results / "Parameter*  Results" style(column) = {just = l asis = on width = 27%} style(header) = {just = l asis = on};
        define stat / "*Statistic" style(column) = {just = l width = 10%};
        define placebo / "Placebo* (N=%cmpres(&placebo_n))" style(column) = {just = d width = 18%};
        define low_dose / "Xanomeline Low Dose* (N=%cmpres(&low_dose_n))" style(column) = {just = d width = 20%};
        define high_dose / "Xanomeline High Dose* (N=%cmpres(&high_dose_n))" style(column) = {just = d width = 20%};
        
        ** create a blank line before each parameter;
        compute before order1;
            line ' ';
        endcomp;
        
        ** add footnotes describing the critical codes;
        footnote1 justify = left "&Footer1.";
        footnote2 justify = left "&Footer2.";
        footnote3 justify = left "&Footer3.";
run;
    
ods pdf close;