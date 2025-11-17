/*****************************************************************************
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
*               t_vscat.sas7bdat
*               
* Macros:       tfl_metadata.sas (Flows branch reads metadata directly)
*         
* Assumptions: a
*
* ____________________________________________________________________________
* PROGRAM HISTORY                                                         
*  09MAY2023  | Megan Harries  | Original
* ----------------------------------------------------------------------------
*****************************************************************************/
%macro run_domino_code;

   /* Retrieve the environment variable */
   %let domino_is_workflow_job = %sysget(DOMINO_IS_WORKFLOW_JOB);
   %put NOTE: DOMINO_IS_WORKFLOW_JOB is &domino_is_workflow_job;

   /* If DOMINO_IS_WORKFLOW_JOB=false, run the following block (interactive / standard run) */
   %if &domino_is_workflow_job = false %then %do;

      /** Setup environment including libraries for this reporting effort;*/
      %include "/mnt/code/domino.sas";

      /* Ensure program name is set for output path usage */
      %global __prog_name;
      %let __prog_name = t_vscat;

      /* Provide safe defaults for TFL title/footer macro vars if not already defined */
      %global DisplayName DisplayTitle Title1 Footer1 Footer2 Footer3;
      %if %sysevalf(%superq(DisplayName)=,boolean) %then %let DisplayName=Vital Signs;
      %if %sysevalf(%superq(DisplayTitle)=,boolean) %then %let DisplayTitle=Categorical Summary;
      %if %sysevalf(%superq(Title1)=,boolean) %then %let Title1=Post-baseline results;
      %if %sysevalf(%superq(Footer1)=,boolean) %then %let Footer1=H = High, L = Low by prespecified limits.;
      %if %sysevalf(%superq(Footer2)=,boolean) %then %let Footer2=Percentages are based on patients with post-baseline results.;
      %if %sysevalf(%superq(Footer3)=,boolean) %then %let Footer3=--;

      ods path(prepend) work.templat(update);

      /* If running in batch mode, write log to /mnt/artifacts/logs */
      %if %symexist(__runmode) %then %do;
        %if %upcase(&__runmode) = BATCH %then %do;
          %put NOTE: BATCH run detected. Log will be written to /mnt/artifacts/logs/&__prog_name..log;
          filename tfllog "/mnt/artifacts/logs/&__prog_name..log";
          proc printto log=tfllog new;
          run;
        %end;
      %end;


      /* Set the template for the output; inherit from a printer style to avoid parent errors */
      proc template;
        define style newstyle / store=work.templat;
          parent = styles.printer;

          class Table /
                 rules = groups
                 frame = void;

          style header /
               just       = c
               fontweight = medium;

          /* smaller footnotes */
          style Footer /
               fontsize = 7pt
               just = l;

          replace Body from Document /
            bottommargin = 1.54cm
            topmargin    = 2.54cm
            rightmargin  = 2.54cm
            leftmargin   = 2.54cm;

          class fonts /
             'TitleFont2'         = ("Courier New",9pt)
             'TitleFont'          = ("Courier New",9pt)
             'StrongFont'         = ("Courier New",9pt)
             'EmphasisFont'       = ("Courier New",9pt,italic)
             'FixedEmphasisFont'  = ("Courier New, Courier",9pt,italic)
             'FixedStrongFont'    = ("Courier New, Courier",9pt)
             'FixedHeadingFont'   = ("Courier New, Courier",9pt)
             'BatchFixedFont'     = ("SAS Monospace, Courier New, Courier",9pt)
             'FixedFont'          = ("Courier New, Courier",9pt)
             'headingEmphasisFont'= ("Courier New",9pt,bold italic)
             'headingFont'        = ("Courier New",9pt)
             'docFont'            = ("Courier New",9pt);

          class color_list /
             'link' = blue
             'bgH'  = white
             'fg'   = black
             'bg'   = _undef_;

        end;
      run;

      options orientation = landscape nonumber nodate nobyline;

      /** vital signs adam and include required variables for table;*/
      data advs (rename = (visitnum = avisitn actarm = trta vstest = param vstestcd = paramcd vsstresn = aval));
        length trtan paramn 8. crit1cd $1;
        set adam.advs;
        
        if actarm = "Placebo" then trtan = 1;
        else if actarm = "Xanomeline Low Dose" then trtan = 2;
        else if actarm = "Xanomeline High Dose" then trtan = 3;
        
        if vstestcd = "SYSBP" then paramn = 1;
        else if vstestcd = "DIABP" then paramn = 2;
        else if vstestcd = "PULSE" then paramn = 3;

        /** 1: Systolic bp, 2: Diastolic bp, 3: Heart rate;*/
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

      /** observations in the population, post-baseline visits and the parameters specified in SAP;*/
      data post_base (keep = usubjid trta trtan param paramcd paramn crit1cd);
          set advs;
          where avisitn > 2 and paramcd in ("SYSBP", "DIABP", "PULSE");
      run;

      /** create macro for counting number of participants by arm;*/
      proc sql noprint;
          select count(distinct usubjid) into :placebo_n     from advs(where = (trta = "Placebo"));
          select count(distinct usubjid) into :low_dose_n    from advs(where = (trta = "Xanomeline Low Dose"));
          select count(distinct usubjid) into :high_dose_n   from advs(where = (trta = "Xanomeline High Dose"));
      quit;

      /** create datasets for each variable's results;*/
      data pb_sysbp; set post_base; where paramcd = "SYSBP"; run;
      data pb_diabp; set post_base; where paramcd = "DIABP"; run;
      data pb_hr;    set post_base; where paramcd = "PULSE"; run;

      /**** any results ****/
      proc sql;
          create table total_pb as
          select trta, count(distinct usubjid) as count_pb
          from post_base
          group by trta;
      quit;

      proc sql;
          create table total_criteria as
          select trta, count(distinct usubjid) as n, count(usubjid) as e
          from post_base(where = (crit1cd ne ""))
          group by trta;
      quit;

      data any_results;
          merge total_pb total_criteria;
          by trta;
          if n ne . then p = cats("(", put(100*n/count_pb, 6.1), ")");
      run;

      /** macro to compute results for each variable **/
      %macro results(variable = );
          proc sql;
              create table total_pb_&variable. as
              select trta, count(distinct usubjid) as count_pb
              from pb_&variable.
              group by trta;
          quit;

          proc sql;
              create table total_&variable._h as
              select trta, count(distinct usubjid) as n_h, count(usubjid) as e_h
              from pb_&variable.(where = (crit1cd = "H"))
              group by trta;
          quit;

          proc sql;
              create table total_&variable._l as
              select trta, count(distinct usubjid) as n_l, count(usubjid) as e_l
              from pb_&variable.(where = (crit1cd = "L"))
              group by trta;
          quit;

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

      /** concatenate results for any parameter data;*/
      data any_results_c;
          length results $32;
          set any_results;
          count_pb_c = put(count_pb, 8.);
          if p = "(100.0)" then p = "(100)";
          if p = " " then results = "0";
          else results = catx(" ", put(n, 8.), p, put(e, 8.));
          name = "";
      run;

      /** create macro to concatenate results for each variable;*/
      %macro concatenate_results(variable = );
          data &variable._results_c;
              length results_l results_h $32;
              set &variable._results;
              count_pb_c = put(count_pb, 8.);
              if p_l = "(100.0)" then p_l = "(100)";
              if p_h = "(100.0)" then p_h = "(100)";
              if p_l = " " then results_l = "0";
              else results_l = catx(" ", put(n_l, 8.), p_l, put(e_l, 8.));
              if p_h = " " then results_h = "0";
              else results_h = catx(" ", put(n_h, 8.), p_h, put(e_h, 8.));
              name = "";
          run;
      %mend;

      %concatenate_results(variable = sysbp);
      %concatenate_results(variable = diabp);
      %concatenate_results(variable = hr);

      options validvarname=v7;

      proc transpose data = any_results_c out = any_results_t;
          id trta;
          var name count_pb_c results;
      run;

      %macro transpose_datasets(parameter = );
          proc transpose data = &parameter._results_c out = &parameter._results_t;
              id trta;
              var name count_pb_c results_l results_h;
          run;
      %mend;

      %transpose_datasets(parameter = sysbp);
      %transpose_datasets(parameter = diabp);
      %transpose_datasets(parameter = hr);

      data stack_results;
          set any_results_t (in = a)
              sysbp_results_t (in = b)
              diabp_results_t (in = c)
              hr_results_t    (in = d);
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

      data add_param_results_stat;
          length param_results $50 stat $8;
          set stack_results (rename = (Xanomeline_Low_Dose = Low_Dose
                                       Xanomeline_High_Dose = High_Dose));
          
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

          if _NAME_ = "count_pb_c" then stat = "n";
          else if _NAME_ in ("results", "results_l", "results_h") then stat = "n (%) e";
      run;

      /** create the table output;*/

      ods pdf file = "/mnt/artifacts/tfl/&__prog_name..pdf"
              style = newstyle;
      ods noproctitle;
      ods escapechar = "^";

      title1 justify = left "Domino" justify = right "Page ^{thispage} of ^{lastpage}";
      title2 "&DisplayName.";
      title3 "&DisplayTitle.";
      title4 "&Title1.";

      proc report data = add_param_results_stat headline split = "*"
                   style(report) = {width = 100% cellpadding = 3} out = tfl.&__prog_name.;
          column  (order1 order2 param_results stat placebo low_dose high_dose);
          define order1 / order noprint;
          define order2 / order noprint;

          define param_results / "Parameter*  Results"
                 style(column) = {just = l asis = on width = 27%}
                 style(header) = {just = l asis = on};
          define stat     / "*Statistic"                         style(column) = {just = l width = 10%};
          define placebo  / "Placebo* (N=%cmpres(&placebo_n))"   style(column) = {just = d width = 18%};
          define low_dose / "Xanomeline Low Dose* (N=%cmpres(&low_dose_n))"  style(column) = {just = d width = 20%};
          define high_dose/ "Xanomeline High Dose* (N=%cmpres(&high_dose_n))" style(column) = {just = d width = 20%};

          compute before order1;
              line ' ';
          endcomp;

          footnote1 justify = left h=7pt "&Footer1.";
          footnote2 justify = left h=7pt "&Footer2.";
          footnote3 justify = left h=7pt "&Footer3.";
      run;

      ods pdf close;


      /* Reset log destination back to default if running in batch */
      %if %symexist(__runmode) %then %do;
        %if %upcase(&__runmode) = BATCH %then %do;
          proc printto;
          run;
        %end;
      %end;

   %end;


   /* If DOMINO_IS_WORKFLOW_JOB=true, run the Flows block */
   %else %if &domino_is_workflow_job = true %then %do;

      /* ==================================================================;
      * Set SASAUTOS to search for shared macros. 
      * This would usually be in domino.sas but putting in program for now. ;
      * ==================================================================;*/
      options
        mautocomplete
        MAUTOSOURCE
        MAUTOLOCDISPLAY 
        sasautos=(
          "/mnt/code/share/macros"
          ,"/mnt/imported/code/SCE_STANDARD_LIB/macros"
          ,SASAUTOS) ;

      /* Assign values to these macro variables (Flows provides inputs separately) */
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

      /* Assign read/write folders for Flows inputs/outputs*/
      libname inputs "/workflow/inputs"; 
      libname outputs "/workflow/outputs"; 

      /* Mandatory: add extension to inputs */
      x "mv /workflow/inputs/advs /workflow/inputs/advs.sas7bdat";

      /* Read in METADATA path from Flow input parameter */
      data _null__;
          infile '/workflow/inputs/metadata_snapshot' truncover;
          input metadata_path $CHAR100.;
          call symputx('metadata_path', metadata_path, 'G');
      run;
      libname sdtm "&metadata_path.";

      * Assign Metadata NetApp Volume;
  libname metadata "&metadata_path./TFL_Metadata_sas7bdat";

      ods path(prepend) work.templat(update);

      proc template;
        define style newstyle / store=work.templat;
          parent = styles.printer;

          class Table /
                 rules = groups
                 frame = void;

          style header /
               just       = c
               fontweight = medium;

          style Footer /
               fontsize = 7pt
               just = l;

          replace Body from Document /
            bottommargin = 1.54cm
            topmargin    = 2.54cm
            rightmargin  = 2.54cm
            leftmargin   = 2.54cm;

          class fonts /
             'TitleFont2'         = ("Courier New",9pt)
             'TitleFont'          = ("Courier New",9pt)
             'StrongFont'         = ("Courier New",9pt)
             'EmphasisFont'       = ("Courier New",9pt,italic)
             'FixedEmphasisFont'  = ("Courier New, Courier",9pt,italic)
             'FixedStrongFont'    = ("Courier New, Courier",9pt)
             'FixedHeadingFont'   = ("Courier New, Courier",9pt)
             'BatchFixedFont'     = ("SAS Monospace, Courier New, Courier",9pt)
             'FixedFont'          = ("Courier New, Courier",9pt)
             'headingEmphasisFont'= ("Courier New",9pt,bold italic)
             'headingFont'        = ("Courier New",9pt)
             'docFont'            = ("Courier New",9pt);

          class color_list /
             'link' = blue
             'bgH'  = white
             'fg'   = black
             'bg'   = _undef_;
        end;
      run;

      options orientation = landscape nonumber nodate nobyline;

      /** vital signs adam and include required variables for table;*/
      data advs (rename = (visitnum = avisitn actarm = trta vstest = param vstestcd = paramcd vsstresn = aval));
        length trtan paramn 8. crit1cd $1;
        set inputs.advs;
        
        if actarm = "Placebo" then trtan = 1;
        else if actarm = "Xanomeline Low Dose" then trtan = 2;
        else if actarm = "Xanomeline High Dose" then trtan = 3;
        
        if vstestcd = "SYSBP" then paramn = 1;
        else if vstestcd = "DIABP" then paramn = 2;
        else if vstestcd = "PULSE" then paramn = 3;

        /** 1: Systolic bp, 2: Diastolic bp, 3: Heart rate;*/
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

      /** observations in the population, post-baseline visits and the parameters specified in SAP;*/
      data post_base (keep = usubjid trta trtan param paramcd paramn crit1cd);
          set advs;
          where avisitn > 2 and paramcd in ("SYSBP", "DIABP", "PULSE");
      run;

      /** counts per arm */
      proc sql noprint;
          select count(distinct usubjid) into :placebo_n   from advs(where = (trta = "Placebo"));
          select count(distinct usubjid) into :low_dose_n  from advs(where = (trta = "Xanomeline Low Dose"));
          select count(distinct usubjid) into :high_dose_n from advs(where = (trta = "Xanomeline High Dose"));
      quit;

      data pb_sysbp; set post_base; where paramcd = "SYSBP"; run;
      data pb_diabp; set post_base; where paramcd = "DIABP"; run;
      data pb_hr;    set post_base; where paramcd = "PULSE"; run;

      proc sql;
          create table total_pb as
          select trta, count(distinct usubjid) as count_pb
          from post_base
          group by trta;
      quit;

      proc sql;
          create table total_criteria as
          select trta, count(distinct usubjid) as n, count(usubjid) as e
          from post_base(where = (crit1cd ne ""))
          group by trta;
      quit;

      data any_results;
          merge total_pb total_criteria;
          by trta;
          if n ne . then p = cats("(", put(100*n/count_pb, 6.1), ")");
      run;

      %macro results(variable = );
          proc sql;
              create table total_pb_&variable. as
              select trta, count(distinct usubjid) as count_pb
              from pb_&variable.
              group by trta;
          quit;

          proc sql;
              create table total_&variable._h as
              select trta, count(distinct usubjid) as n_h, count(usubjid) as e_h
              from pb_&variable.(where = (crit1cd = "H"))
              group by trta;
          quit;

          proc sql;
              create table total_&variable._l as
              select trta, count(distinct usubjid) as n_l, count(usubjid) as e_l
              from pb_&variable.(where = (crit1cd = "L"))
              group by trta;
          quit;

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

      data any_results_c;
          length results $32;
          set any_results;
          count_pb_c = put(count_pb, 8.);
          if p = "(100.0)" then p = "(100)";
          if p = " " then results = "0";
          else results = catx(" ", put(n, 8.), p, put(e, 8.));
          name = "";
      run;

      %macro concatenate_results(variable = );
          data &variable._results_c;
              length results_l results_h $32;
              set &variable._results;
              count_pb_c = put(count_pb, 8.);
              if p_l = "(100.0)" then p_l = "(100)";
              if p_h = "(100.0)" then p_h = "(100)";
              if p_l = " " then results_l = "0";
              else results_l = catx(" ", put(n_l, 8.), p_l, put(e_l, 8.));
              if p_h = " " then results_h = "0";
              else results_h = catx(" ", put(n_h, 8.), p_h, put(e_h, 8.));
              name = "";
          run;
      %mend;

      %concatenate_results(variable = sysbp);
      %concatenate_results(variable = diabp);
      %concatenate_results(variable = hr);

      options validvarname=v7;

      proc transpose data = any_results_c out = any_results_t;
          id trta;
          var name count_pb_c results;
      run;

      %macro transpose_datasets(parameter = );
          proc transpose data = &parameter._results_c out = &parameter._results_t;
              id trta;
              var name count_pb_c results_l results_h;
          run;
      %mend;

      %transpose_datasets(parameter = sysbp);
      %transpose_datasets(parameter = diabp);
      %transpose_datasets(parameter = hr);

      data stack_results;
          set any_results_t (in = a)
              sysbp_results_t (in = b)
              diabp_results_t (in = c)
              hr_results_t    (in = d);
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

      data add_param_results_stat;
          length param_results $50 stat $8;
          set stack_results (rename = (Xanomeline_Low_Dose = Low_Dose
                                       Xanomeline_High_Dose = High_Dose));
          
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

          if _NAME_ = "count_pb_c" then stat = "n";
          else if _NAME_ in ("results", "results_l", "results_h") then stat = "n (%) e";
      run;

      /* Pull titles/footers from metadata dataset "metadata.t_vscat" if present */
      %global DisplayName DisplayTitle Title1 Footer1 Footer2 Footer3;
      %let DisplayName=Vital Signs;
      %let DisplayTitle=Categorical Summary;
      %let Title1=Post-baseline results;
      %let Footer1=H = High, L = Low by prespecified limits.;
      %let Footer2=Percentages are based on patients with post-baseline results.;
      %let Footer3=--;

      %if %sysfunc(exist(metadata.t_vscat)) %then %do;
        data _null_;
          set metadata.t_vscat;
          call symputx('DisplayName',  DisplayName,  'G');
          call symputx('DisplayTitle', DisplayTitle, 'G');
          call symputx('Title1',       Title1,       'G');
          call symputx('Footer1',      Footer1,      'G');
          call symputx('Footer2',      Footer2,      'G');
          call symputx('Footer3',      Footer3,      'G');
        run;
      %end;

      ods pdf file = "/workflow/outputs/t_vscat"
              style = newstyle;
      ods noproctitle;
      ods escapechar = "^";

      title1 justify = left "Domino" justify = right "Page ^{thispage} of ^{lastpage}";
      title2 "&DisplayName.";
      title3 "&DisplayTitle.";
      title4 "&Title1.";

      proc report data = add_param_results_stat headline split = "*"
                   style(report) = {width = 100% cellpadding = 3};
          column  (order1 order2 param_results stat placebo low_dose high_dose);
          define order1 / order noprint;
          define order2 / order noprint;

          define param_results / "Parameter*  Results"
                 style(column) = {just = l asis = on width = 27%}
                 style(header) = {just = l asis = on};
          define stat     / "*Statistic"                         style(column) = {just = l width = 10%};
          define placebo  / "Placebo* (N=%cmpres(&placebo_n))"   style(column) = {just = d width = 18%};
          define low_dose / "Xanomeline Low Dose* (N=%cmpres(&low_dose_n))"  style(column) = {just = d width = 20%};
          define high_dose/ "Xanomeline High Dose* (N=%cmpres(&high_dose_n))" style(column) = {just = d width = 20%};

          compute before order1;
              line ' ';
          endcomp;

          footnote1 justify = left h=7pt "&Footer1.";
          footnote2 justify = left h=7pt "&Footer2.";
          footnote3 justify = left h=7pt "&Footer3.";
      run;

      ods pdf close;

   %end;
   /* Otherwise, log a warning that the variable is not recognized */
   %else %do;
      %put WARNING: DOMINO_IS_WORKFLOW_JOB environment variable not recognized or missing.;
   %end;

%mend run_domino_code;

/* Invoke the macro */
%run_domino_code;
