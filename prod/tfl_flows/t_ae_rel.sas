/*****************************************************************************\
*  ____                  _
* |  _ \  ___  _ __ ___ (_)_ __   ___
* | | | |/ _ \| '_ ` _ \| | '_ \ / _ \
* | |_| | (_) | | | | | | | | | | (_) |
* |____/ \___/|_| |_| |_|_|_| |_|\___/                                               
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : CDISC01
* Program              : t_ae_rel.sas
* Purpose              : Create the Treatment Emergent Adverse Events Table
* ____________________________________________________________________________
* DESCRIPTION                                                    
*                                                                   
* Input files: ADaM.ADSL
*			   ADaM.ADAE
*              
* Output files: t_ae_rel.pdf
*				t_ae_rel.sas7bdat
*               
* Macros:       tfl_metadata.sas
*         
* Assumptions: test
*
* ____________________________________________________________________________
* PROGRAM HISTORY       
*  24MAY2022  | Jake Tombeur   | Original version                            
*  10MAY2023  | Megan Harries  | Updates for CDISC01 ADaMs
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
  %let __PROG_NAME = t_pop;       
  %let __PROG_EXT = sas;          
  %let __DCUTDTC = %sysfunc(today(), yymmdd10.);
  %let __WORKING_DIR = /mnt/code;
  %let __PROJECT_NAME = MyProject;
  %let __PROTOCOL = MyProtocol;
  %let __PROJECT_TYPE = MyType;
  %let __localdata_path = /mnt/data;
  %let __prog_path = /mnt/code/t_pop.sas;
  %let __results_path = /mnt/results;
  %let __runmode = batch;

* Assign read/write folders for Flows inputs/outputs;
  libname inputs "/workflow/inputs"; /* All inputs live in this directory at workflow/inputs/<NAME OF INPUT> */ 
  libname outputs "/workflow/outputs"; /* All outputs must go to this directory at workflow/inputs/<NAME OF OUTPUT> */ 

/* Mandatory step to add sas7bdat file extension to inputs */
  x "mv /workflow/inputs/adsl_dataset /workflow/inputs/adsl_dataset.sas7bdat";
  x "mv /workflow/inputs/adae_dataset /workflow/inputs/adae_dataset.sas7bdat";

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

proc format;
   picture pctmf (round default = 8)                               /* Picture format for percentages */
               .     = ' '        (noedit)
        low-0.001    = ' '        (noedit)
        0.001-<0.1   = ' (<0.1%)' (noedit)
              0.1-<1 = '  (9.9%)' (prefix='  (')
         1-<99.90001 = ' (00.0%)' (prefix=' (')
       99.90001-<100 = '(>99.9%)' (noedit)
                 100 = '(100%)  ' (noedit)
   ;
run;

data teae (rename = (actarm = trta));
    length relcat $20;
    set inputs.adae_dataset;
    
	if aerel in ('POSSIBLE' 'PROBABLE' 'DEFINITE') then relcat = 'Related';
    else relcat = 'Not Related';

	if actarm = "Placebo" then trtan = 1;
	else if actarm = "Xanomeline Low Dose" then trtan = 2;
	else if actarm = "Xanomeline High Dose" then trtan = 3;
run;

** exclude non-treated subjects;
data adsl1 (rename = (actarm = trta) where = (trtan ^= .));
    set inputs.adsl_dataset;
	
	if actarm = "Placebo" then trtan = 1;
	else if actarm = "Xanomeline Low Dose" then trtan = 2;
	else if actarm = "Xanomeline High Dose" then trtan = 3;
run; 

%let indat     = teae;
%let trtvarn   = trtan;
%let inadsl    = adsl1;
%let socvar    = aesoc;
%let ptvar     = aedecod;
%let totval    = 99;
%let trtnord   = 99;
%let pctfmt    = pctmf.;
%let byvar     = relcat;

/* Macro for creating #patients/#events counts */
%macro ne_freq (indat =,outdat =, byvars =, anyvars = );

    %let byvars2  = %sysfunc(tranwrd(%quote(&byvars.) ,%str( ),%str( , )));
    %if &byvars ^= %then %let sep = %str( , );
    %else %let sep = ;

    proc sql;
        create table &outdat. as
        select count(distinct USUBJID) as stat_n,
               count(USUBJID) as stat_e
               &sep. &byvars2.
               %if &anyvars ^= %then %do i = 1 %to %sysfunc(countw(&anyvars));
                , 'ANY' as %scan(&anyvars, &i)
               %end;
        from &indat.
        %if &byvars. ^= %then group by &byvars2.;
        ;
    quit;

%mend;

/* All aes (with total column if required) */
data aes;
    set &indat  
        &indat (in = intot);
    if intot then &trtvarn = &totval; 
run;

/* Adsl with total column if required */
data adslmod;
    set &inadsl
        &inadsl (in = intot );
    if intot then &trtvarn = &totval; 
run;

/* Counts including totals (by Severity) */
%ne_freq(indat = aes, outdat = out1, byvars = &byvar &trtvarn,                anyvars = &socvar &ptvar);
%ne_freq(indat = aes, outdat = out2, byvars = &byvar &trtvarn &socvar,        anyvars = &ptvar);
%ne_freq(indat = aes, outdat = out3, byvars = &byvar &trtvarn &socvar &ptvar, anyvars =);

/* Counts including totals (Any Severity) */
%ne_freq(indat = aes, outdat = out4, byvars = &trtvarn,                       anyvars = &byvar &socvar &ptvar);
%ne_freq(indat = aes, outdat = out5, byvars = &trtvarn &socvar,               anyvars = &byvar &ptvar);
%ne_freq(indat = aes, outdat = out6, byvars = &trtvarn &socvar &ptvar,        anyvars = &byvar);

/* N counts for denominators */
%ne_freq(indat = adslmod, outdat = Ncounts, byvars = &trtvarn, anyvars =);

data Ncounts; 
    set Ncounts (drop = stat_e rename = (stat_n = bigN)); 
    call symputx(cats('N_',&trtvarn), bigN, 'g');
run; 

/* Set all ae counts together */
data allcounts;
    length &socvar &ptvar $ 200;
    set out1-out6;
run;

/* Template dataset */
proc sql;
    create table template as
    select *, 0 as stat_e, 0 as stat_n
    from (select distinct &socvar, &ptvar from &indat 
          union 
          select distinct &socvar, 'ANY' as &ptvar from &indat 
          union 
          select distinct 'ANY' as &ptvar, 'ANY' as &socvar from &indat),
         (select distinct &byvar from &indat
          union 
          select distinct 'ANY' as &byvar from &indat),
         Ncounts
    order by &trtvarn, &socvar, &ptvar, &byvar;
    ;
quit;
    
/* Merge on observed counts to template */
proc sort data = allcounts out = allcounts_s;
    by &trtvarn &socvar &ptvar &byvar;
run;
data counts_w0;
    length &socvar &ptvar $ 200 statc_n statc_e statc_p $ 30;
    merge template allcounts_s;
    by &trtvarn &socvar &ptvar &byvar;
    /* Create character versions of counts */
    statc_n = strip(put(stat_n,5.));
    statc_e = strip(put(stat_e,5.));
    statc_p = put(stat_n/bigN * 100, &pctfmt);
run;

/* Concatenate n and percent*/
data counts_cat (keep = &socvar &ptvar &trtvarn &byvar npp statc_e);
    length npp $ 50;
    set counts_w0;
    npp = cat(strip(statc_n), ' ', strip(statc_p));
run;

/* Create SOC and PT order variables based on # patients / frequency of event */
proc rank data = counts_w0  (where = (&trtvarn = &trtnord & &ptvar = 'ANY' & &socvar ^= 'ANY' & &byvar = 'ANY')) out = socranks (keep = &socvar SOCord_NP SOCord_EV) ties = low descending;
    var stat_n stat_e;
    ranks SOCord_NP SOCord_EV;
run;

proc sort data = counts_w0 out = counts_w0s;
	by &socvar;
run;

proc rank data = counts_w0s (where = (&trtvarn = &trtnord & &ptvar ^= 'ANY' & &socvar ^= 'ANY' & &byvar = 'ANY')) out = ptranks (keep = &socvar &ptvar PTord_NP PTord_EV) ties = low descending;
    by &socvar;
    var stat_n stat_e;
    ranks PTord_NP PTord_EV;
run;

proc format;
    invalue relord 'ANY'         = 1
                   'Related'     = 2
                   'Not Related' = 3
                   ;
run;

proc sql;
    create table counts_word as 
    select a.*, 
           case when a.&socvar = 'ANY' then 1 else b.SOCord_NP + 1 end as SOCord_NP, 
           case when a.&socvar = 'ANY' then 1 else b.SOCord_EV + 1 end as SOCord_EV,
           case when a.&ptvar  = 'ANY' then 1 else c.PTord_NP  + 1 end as PTord_NP,
           case when a.&ptvar  = 'ANY' then 1 else c.PTord_EV  + 1 end as PTord_EV,
           input(&byvar,relord.) as relord
    from counts_cat a left join socranks b
                          on  a.&socvar = b.&socvar
                      left join ptranks c
                          on  a.&socvar = c.&socvar
                          and a.&ptvar  = c.&ptvar
    order by SOCord_NP, &socvar, PTord_NP, &ptvar, relord, &byvar, &trtvarn
    ;
quit;

/* Transpose into long format */
proc transpose data = counts_word out = counts_T (rename = (_NAME_ = statty COL1 = statval));
    by SOCord_NP &socvar PTord_NP &ptvar relord &byvar &trtvarn ;
    var npp statc_e;
run;

data counts_T;
	set counts_T;
	where &trtvarn ^= .;
run;

/* Transpose to trts are cols */
proc transpose delim = _ prefix = trt_ data = counts_T out = counts_TT (drop = _NAME_);
    id &trtvarn statty;
    by SOCord_NP &socvar PTord_NP  &ptvar relord &byvar;
    var statval;
run;

data extrow (keep = aesoc aedecod soc_pt_disp &byvar trt_99_npp); 
    length soc_pt_disp $ 132; 
    set counts_TT;
    by SOCord_NP aesoc;

    if first.aesoc & aesoc ^= 'ANY' then do;
        soc_pt_disp = aesoc;
        output;
    end;
    if aesoc = 'ANY' then do;
        soc_pt_disp = 'Subjects with at least one TEAE';
        output;
    end;
    if aedecod = 'ANY' then aedecod = 'Any event';
    soc_pt_disp = aedecod;
    if aesoc ^= 'ANY' then output;
run;

data final (drop = i);
    set extrow;
    array trtcounts $ trt_:;
    if aesoc = soc_pt_disp then do i = 1 to dim(trtcounts);
        trtcounts[i] = '';
        &byvar = '  ';
    end;
    if aedecod = soc_pt_disp then indent = 'Y';
    else indent = 'N';

    if &byvar = 'ANY' then &byvar = 'Total';
    &byvar = propcase(&byvar);

	soc_pt_disp = propcase(soc_pt_disp);
	aesoc = propcase(aesoc);
	aedecod = propcase(aedecod); 
	
	soc_pt_disp = tranwrd(soc_pt_disp, "Teae", "TEAE");
run;

*include metadata;
data metadata;
		set metadata.t_ae_rel;
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

ods pdf file = "/workflow/outputs/t_ae_rel"
		style = newstyle;
        
ods noproctitle;
ods escapechar = "^";

** add titles to output;
title1 justify = left "Domino" justify = right "Page ^{thispage} of ^{lastpage}";
title2 "&DisplayName.";
title3 "&DisplayTitle.";
title4 "&Title1.";

** justify contents to decimal places;
proc report data = final headline split = "*" 
			style(report) = {width = 100%};
        column  aesoc
                   aedecod
                   indent soc_pt_disp &byvar trt_99_npp;
        
        ** order variables;
        define aesoc        / order order = data noprint;
        define aedecod      / order order = data noprint;
        define indent       / order order = data noprint;
        define &byvar       / display ''
                                style(header) = {width = 8% just = l};
        define soc_pt_disp  / order order = data  "System Organ Class*    Preferred Term"
                                style(header) = {width = 60% asis = on just = l};
        define trt_99_npp  / display "All Treatments*(N=&N_99)*n (%)"
                                style(header) = {width = 30%} style(column) = {just = d};
        compute soc_pt_disp;
            if indent = 'Y' then call define(_COL_, "style", "style=[leftmargin = 0.3in]");
        endcomp;

        compute before aedecod;
            line '';
        endcomp;

        ** add footnotes;
        footnote1 justify = left "&Footer1.";
		footnote2 justify = left "&Footer2.";
		footnote3 justify = left "&Footer3.";
		footnote4 justify = left "&Footer4.";
		footnote5 justify = left "&Footer5.";
run;
    
ods pdf close;

