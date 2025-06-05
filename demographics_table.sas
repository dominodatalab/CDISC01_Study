/*****************************************************************************\
*  ____                  _
* |  _ \  ___  _ __ ___ (_)_ __   ___
* | | | |/ _ \| '_ ` _ \| | '_ \ / _ \
* | |_| | (_) | | | | | | | | | | (_) |
* |____/ \___/|_| |_| |_|_|_| |_|\___/
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : DEMO_STUDY
* Program              : standalone_demographics.sas
* Purpose              : Create a standalone demographics table with simulated data
* ____________________________________________________________________________
* DESCRIPTION
*
* Input files: None (creates simulated data)
*
* Output files: demographics_table.pdf
*
* Macros:       None
*
* Assumptions: None - fully self-contained
*
* ____________________________________________________________________________
* PROGRAM HISTORY
*  05JUN2025  | AI Assistant  | Original
* ----------------------------------------------------------------------------
\*****************************************************************************/

/* Set project name - modify this as needed */
%let project_name = %sysget(DOMINO_PROJECT_NAME);
%let table_name = demographics_table;

/* Create output directory if it doesn't exist */
%macro ensure_directory(path);
    %if %sysfunc(fileexist(&path)) = 0 %then %do;
        %put NOTE: Creating directory &path;
        x "mkdir -p &path";
    %end;
%mend ensure_directory;

/* Create artifacts directory */
%ensure_directory(/mnt/artifacts);
%ensure_directory(/mnt/artifacts/&project_name);

/* Define output file path */
%let output_path = /mnt/artifacts/&project_name/&table_name..pdf;

/* Create simulated ADSL-like dataset */
data adsl_simulated;
    /* Set random seed for reproducible results */
    call streaminit(12345);
    
    length usubjid $20 actarm $30 sex $1;
    
    /* Create 300 subjects across 3 treatment arms */
    do i = 1 to 300;
        /* Generate subject ID */
        usubjid = cats("SUBJ-", put(i, z4.));
        
        /* Assign treatment arms */
        if i <= 100 then actarm = "Placebo";
        else if i <= 200 then actarm = "Xanomeline Low Dose";
        else actarm = "Xanomeline High Dose";
        
        /* Generate age (normal distribution around 65, SD=12) */
        age = max(18, min(90, round(rand('normal', 65, 12))));
        
        /* Generate sex (60% female, 40% male) */
        if rand('uniform') < 0.6 then sex = 'F';
        else sex = 'M';
        
        /* Generate race with realistic distribution */
        race_rand = rand('uniform');
        if race_rand < 0.75 then race = "WHITE";
        else if race_rand < 0.85 then race = "BLACK OR AFRICAN AMERICAN";
        else if race_rand < 0.92 then race = "ASIAN";
        else race = "OTHER";
        
        output;
    end;
    
    drop i race_rand;
run;

/* Process data similar to original script */
data adsl_processed;
    set adsl_simulated;
    
    /* Create treatment number */
    if actarm = "Placebo" then trtan = 1;
    else if actarm = "Xanomeline Low Dose" then trtan = 2;
    else if actarm = "Xanomeline High Dose" then trtan = 3;
    
    /* Create age groups */
    if age < 60 then agen = 1;
    else if 60 <= age < 65 then agen = 2;
    else if 65 <= age < 70 then agen = 3;
    else if 70 <= age < 75 then agen = 4;
    else if 75 <= age < 80 then agen = 5;
    else if 80 <= age then agen = 6;
    
    /* Create sex number */
    if sex = 'M' then sexn = 1;
    else if sex = 'F' then sexn = 2;
    
    /* Rename for consistency */
    trta = actarm;
    
    keep usubjid trta trtan age agen sex sexn race;
run;

/* Count participants by treatment */
proc sql noprint;
    select count(distinct usubjid) into :placebo_n
    from adsl_processed where trta = "Placebo";
    
    select count(distinct usubjid) into :low_dose_n
    from adsl_processed where trta = "Xanomeline Low Dose";
    
    select count(distinct usubjid) into :high_dose_n
    from adsl_processed where trta = "Xanomeline High Dose";
quit;

/* Calculate total counts by treatment */
proc sql;
    create table total_age as
    select trta, count(distinct usubjid) as count_age
    from adsl_processed
    group by trta;
quit;

/* Create age group analysis macro */
%macro age_data(agen = );
    data age&agen.;
        set adsl_processed;
        where agen = &agen.;
    run;

    proc sql;
        create table total_age&agen. as
        select trta, count(distinct usubjid) as n&agen.
        from age&agen.
        group by trta;
    quit;
%mend age_data;

/* Process all age groups */
%age_data(agen = 1);
%age_data(agen = 2);
%age_data(agen = 3);
%age_data(agen = 4);
%age_data(agen = 5);
%age_data(agen = 6);

/* Sort datasets before merging */
proc sort data=total_age; by trta; run;
%macro sort_age_tables;
    %do i = 1 %to 6;
        proc sort data=total_age&i; by trta; run;
    %end;
%mend sort_age_tables;
%sort_age_tables;

/* Merge counts and calculate percentages */
data results;
    merge total_age total_age1 total_age2 total_age3 total_age4 total_age5 total_age6;
    by trta;
    
    /* Calculate percentages, handling missing values */
    if n1 ne . and count_age > 0 then p1 = cats("(", put(100*n1/count_age, 6.1), ")");
    else p1 = "";
    
    if n2 ne . and count_age > 0 then p2 = cats("(", put(100*n2/count_age, 6.1), ")");
    else p2 = "";
    
    if n3 ne . and count_age > 0 then p3 = cats("(", put(100*n3/count_age, 6.1), ")");
    else p3 = "";
    
    if n4 ne . and count_age > 0 then p4 = cats("(", put(100*n4/count_age, 6.1), ")");
    else p4 = "";
    
    if n5 ne . and count_age > 0 then p5 = cats("(", put(100*n5/count_age, 6.1), ")");
    else p5 = "";
    
    if n6 ne . and count_age > 0 then p6 = cats("(", put(100*n6/count_age, 6.1), ")");
    else p6 = "";
run;

/* Format results for display */
data results_formatted;
    length results1 results2 results3 results4 results5 results6 $32;
    set results;
    
    /* Clean up 100% display */
    if p1 = "(100.0)" then p1 = "(100)";
    if p2 = "(100.0)" then p2 = "(100)";
    if p3 = "(100.0)" then p3 = "(100)";
    if p4 = "(100.0)" then p4 = "(100)";
    if p5 = "(100.0)" then p5 = "(100)";
    if p6 = "(100.0)" then p6 = "(100)";
    
    /* Format results: n (%) or just 0 if no subjects */
    if n1 = 0 or n1 = . then results1 = "0";
    else results1 = catx(" ", put(n1, 8.), p1);
    
    if n2 = 0 or n2 = . then results2 = "0";
    else results2 = catx(" ", put(n2, 8.), p2);
    
    if n3 = 0 or n3 = . then results3 = "0";
    else results3 = catx(" ", put(n3, 8.), p3);
    
    if n4 = 0 or n4 = . then results4 = "0";
    else results4 = catx(" ", put(n4, 8.), p4);
    
    if n5 = 0 or n5 = . then results5 = "0";
    else results5 = catx(" ", put(n5, 8.), p5);
    
    if n6 = 0 or n6 = . then results6 = "0";
    else results6 = catx(" ", put(n6, 8.), p6);
    
    /* Empty count_age_c for transpose */
    count_age_c = "";
run;

/* Transpose data for reporting */
options validvarname=v7;
proc transpose data=results_formatted out=results_transposed name=agegroup;
    id trta;
    var count_age_c results1 results2 results3 results4 results5 results6;
run;

/* Create final reporting dataset */
data order_results;
    length order1 8. ageresults $50 stat $8;
    set results_transposed;
    
    /* Rename columns for cleaner display */
    rename Xanomeline_Low_Dose = Low_Dose 
           Xanomeline_High_Dose = High_Dose;
    
    /* Set order and labels */
    if agegroup = "count_age_c" then do;
        order1 = 1;
        ageresults = "";
        stat = "";
    end;
    else do;
        order1 = input(substr(agegroup, 8), 8.) + 1;
        stat = "n (%)";
    end;
    
    /* Age group labels */
    if agegroup = "results1" then ageresults = "Less than 60 years";
    else if agegroup = "results2" then ageresults = "60 to <65 years";
    else if agegroup = "results3" then ageresults = "65 to <70 years";
    else if agegroup = "results4" then ageresults = "70 to <75 years";
    else if agegroup = "results5" then ageresults = "75 to <80 years";
    else if agegroup = "results6" then ageresults = "80 years and older";
run;

/* Define custom style template */
ods path(prepend) work.templat(update);

proc template;
    define style demostyle;
        class Table /
            Rules = Groups
            Frame = void
            cellpadding = 3
            borderwidth = 1;
            
        style header /
            just = center
            fontweight = bold
            background = lightgray
            fontsize = 10pt;
            
        replace Body from Document /
            bottommargin = 1.5cm
            topmargin = 2.5cm
            rightmargin = 2cm
            leftmargin = 2cm;
            
        replace fonts /
            'TitleFont' = ("Arial", 11pt, Bold)
            'headingFont' = ("Arial", 10pt, Bold)
            'docFont' = ("Arial", 9pt);
    end;
run;

/* Generate PDF report */
%put NOTE: Creating PDF report at &output_path;

ods pdf file="&output_path" style=demostyle;
ods noproctitle;
ods escapechar = "^";

/* Report titles */
title1 justify=left "&project_name" justify=right "Page ^{thispage} of ^{lastpage}";
title2 "Table 1.1";
title3 "Demographics Summary - Age Distribution by Treatment";
title4 "Simulated Analysis Population";

/* Generate the report */
proc report data=order_results headline split="*" 
    style(report)={width=100% cellpadding=3};
    
    column (order1 ageresults stat placebo low_dose high_dose);
    
    /* Column definitions */
    define order1 / order noprint;
    define ageresults / "*Age Group" 
        style(column)={just=left width=35%} 
        style(header)={just=left};
    define stat / "*Statistic" 
        style(column)={just=left width=12%};
    define placebo / "Placebo*(N=%cmpres(&placebo_n))" 
        style(column)={just=center width=18%};
    define low_dose / "Xanomeline Low Dose*(N=%cmpres(&low_dose_n))" 
        style(column)={just=center width=20%};
    define high_dose / "Xanomeline High Dose*(N=%cmpres(&high_dose_n))" 
        style(column)={just=center width=15%};
    
    /* Footnotes */
    footnote1 justify=left "Note: n = number of subjects in age group";
    footnote2 justify=left "Note: Percentages are based on total subjects per treatment";
    footnote3 justify=left "Program: standalone_demographics.sas; Generated: %sysfunc(today(), date9.) %sysfunc(time(), time8.)";
run;

ods pdf close;

/* Clear titles and footnotes */
title;
footnote;

/* Print confirmation message */
%put NOTE: ========================================;
%put NOTE: PDF REPORT GENERATED SUCCESSFULLY!;
%put NOTE: ========================================;
%put NOTE: Project: &project_name;
%put NOTE: Output: &output_path;
%put NOTE: Total subjects: %eval(&placebo_n + &low_dose_n + &high_dose_n);
%put NOTE: - Placebo: &placebo_n subjects;
%put NOTE: - Low Dose: &low_dose_n subjects; 
%put NOTE: - High Dose: &high_dose_n subjects;
%put NOTE: ========================================;

/* Optional: Display summary statistics */
proc freq data=adsl_processed;
    tables trta*agen / nocol nopercent;
    title "Age Group Distribution by Treatment (Verification)";
run;
title;/*****************************************************************************\
*  ____                  _
* |  _ \  ___  _ __ ___ (_)_ __   ___
* | | | |/ _ \| '_ ` _ \| | '_ \ / _ \
* | |_| | (_) | | | | | | | | | | (_) |
* |____/ \___/|_| |_| |_|_|_| |_|\___/
* ____________________________________________________________________________
* Sponsor              : Domino
* Study                : DEMO_STUDY
* Program              : standalone_demographics.sas
* Purpose              : Create a standalone demographics table with simulated data
* ____________________________________________________________________________
* DESCRIPTION
*
* Input files: None (creates simulated data)
*
* Output files: demographics_table.pdf
*
* Macros:       None
*
* Assumptions: None - fully self-contained
*
* ____________________________________________________________________________
* PROGRAM HISTORY
*  05JUN2025  | AI Assistant  | Original
* ----------------------------------------------------------------------------
\*****************************************************************************/

/* Set project name - modify this as needed */
%let project_name = DEMO_STUDY_2025;
%let table_name = demographics_table;

/* Create output directory if it doesn't exist */
%macro ensure_directory(path);
    %if %sysfunc(fileexist(&path)) = 0 %then %do;
        %put NOTE: Creating directory &path;
        x "mkdir -p &path";
    %end;
%mend ensure_directory;

/* Create artifacts directory */
%ensure_directory(/mnt/artifacts);
%ensure_directory(/mnt/artifacts/&project_name);

/* Define output file path */
%let output_path = /mnt/artifacts/&project_name/&table_name..pdf;

/* Create simulated ADSL-like dataset */
data adsl_simulated;
    /* Set random seed for reproducible results */
    call streaminit(12345);
    
    length usubjid $20 actarm $30 sex $1;
    
    /* Create 300 subjects across 3 treatment arms */
    do i = 1 to 300;
        /* Generate subject ID */
        usubjid = cats("SUBJ-", put(i, z4.));
        
        /* Assign treatment arms */
        if i <= 100 then actarm = "Placebo";
        else if i <= 200 then actarm = "Xanomeline Low Dose";
        else actarm = "Xanomeline High Dose";
        
        /* Generate age (normal distribution around 65, SD=12) */
        age = max(18, min(90, round(rand('normal', 65, 12))));
        
        /* Generate sex (60% female, 40% male) */
        if rand('uniform') < 0.6 then sex = 'F';
        else sex = 'M';
        
        /* Generate race with realistic distribution */
        race_rand = rand('uniform');
        if race_rand < 0.75 then race = "WHITE";
        else if race_rand < 0.85 then race = "BLACK OR AFRICAN AMERICAN";
        else if race_rand < 0.92 then race = "ASIAN";
        else race = "OTHER";
        
        output;
    end;
    
    drop i race_rand;
run;

/* Process data similar to original script */
data adsl_processed;
    set adsl_simulated;
    
    /* Create treatment number */
    if actarm = "Placebo" then trtan = 1;
    else if actarm = "Xanomeline Low Dose" then trtan = 2;
    else if actarm = "Xanomeline High Dose" then trtan = 3;
    
    /* Create age groups */
    if age < 60 then agen = 1;
    else if 60 <= age < 65 then agen = 2;
    else if 65 <= age < 70 then agen = 3;
    else if 70 <= age < 75 then agen = 4;
    else if 75 <= age < 80 then agen = 5;
    else if 80 <= age then agen = 6;
    
    /* Create sex number */
    if sex = 'M' then sexn = 1;
    else if sex = 'F' then sexn = 2;
    
    /* Rename for consistency */
    trta = actarm;
    
    keep usubjid trta trtan age agen sex sexn race;
run;

/* Count participants by treatment */
proc sql noprint;
    select count(distinct usubjid) into :placebo_n
    from adsl_processed where trta = "Placebo";
    
    select count(distinct usubjid) into :low_dose_n
    from adsl_processed where trta = "Xanomeline Low Dose";
    
    select count(distinct usubjid) into :high_dose_n
    from adsl_processed where trta = "Xanomeline High Dose";
quit;

/* Calculate total counts by treatment */
proc sql;
    create table total_age as
    select trta, count(distinct usubjid) as count_age
    from adsl_processed
    group by trta;
quit;

/* Create age group analysis macro */
%macro age_data(agen = );
    data age&agen.;
        set adsl_processed;
        where agen = &agen.;
    run;

    proc sql;
        create table total_age&agen. as
        select trta, count(distinct usubjid) as n&agen.
        from age&agen.
        group by trta;
    quit;
%mend age_data;

/* Process all age groups */
%age_data(agen = 1);
%age_data(agen = 2);
%age_data(agen = 3);
%age_data(agen = 4);
%age_data(agen = 5);
%age_data(agen = 6);

/* Sort datasets before merging */
proc sort data=total_age; by trta; run;
%macro sort_age_tables;
    %do i = 1 %to 6;
        proc sort data=total_age&i; by trta; run;
    %end;
%mend sort_age_tables;
%sort_age_tables;

/* Merge counts and calculate percentages */
data results;
    merge total_age total_age1 total_age2 total_age3 total_age4 total_age5 total_age6;
    by trta;
    
    /* Calculate percentages, handling missing values */
    if n1 ne . and count_age > 0 then p1 = cats("(", put(100*n1/count_age, 6.1), ")");
    else p1 = "";
    
    if n2 ne . and count_age > 0 then p2 = cats("(", put(100*n2/count_age, 6.1), ")");
    else p2 = "";
    
    if n3 ne . and count_age > 0 then p3 = cats("(", put(100*n3/count_age, 6.1), ")");
    else p3 = "";
    
    if n4 ne . and count_age > 0 then p4 = cats("(", put(100*n4/count_age, 6.1), ")");
    else p4 = "";
    
    if n5 ne . and count_age > 0 then p5 = cats("(", put(100*n5/count_age, 6.1), ")");
    else p5 = "";
    
    if n6 ne . and count_age > 0 then p6 = cats("(", put(100*n6/count_age, 6.1), ")");
    else p6 = "";
run;

/* Format results for display */
data results_formatted;
    length results1 results2 results3 results4 results5 results6 $32;
    set results;
    
    /* Clean up 100% display */
    if p1 = "(100.0)" then p1 = "(100)";
    if p2 = "(100.0)" then p2 = "(100)";
    if p3 = "(100.0)" then p3 = "(100)";
    if p4 = "(100.0)" then p4 = "(100)";
    if p5 = "(100.0)" then p5 = "(100)";
    if p6 = "(100.0)" then p6 = "(100)";
    
    /* Format results: n (%) or just 0 if no subjects */
    if n1 = 0 or n1 = . then results1 = "0";
    else results1 = catx(" ", put(n1, 8.), p1);
    
    if n2 = 0 or n2 = . then results2 = "0";
    else results2 = catx(" ", put(n2, 8.), p2);
    
    if n3 = 0 or n3 = . then results3 = "0";
    else results3 = catx(" ", put(n3, 8.), p3);
    
    if n4 = 0 or n4 = . then results4 = "0";
    else results4 = catx(" ", put(n4, 8.), p4);
    
    if n5 = 0 or n5 = . then results5 = "0";
    else results5 = catx(" ", put(n5, 8.), p5);
    
    if n6 = 0 or n6 = . then results6 = "0";
    else results6 = catx(" ", put(n6, 8.), p6);
    
    /* Empty count_age_c for transpose */
    count_age_c = "";
run;

/* Transpose data for reporting */
options validvarname=v7;
proc transpose data=results_formatted out=results_transposed name=agegroup;
    id trta;
    var count_age_c results1 results2 results3 results4 results5 results6;
run;

/* Create final reporting dataset */
data order_results;
    length order1 8. ageresults $50 stat $8;
    set results_transposed;
    
    /* Rename columns for cleaner display */
    rename Xanomeline_Low_Dose = Low_Dose 
           Xanomeline_High_Dose = High_Dose;
    
    /* Set order and labels */
    if agegroup = "count_age_c" then do;
        order1 = 1;
        ageresults = "";
        stat = "";
    end;
    else do;
        order1 = input(substr(agegroup, 8), 8.) + 1;
        stat = "n (%)";
    end;
    
    /* Age group labels */
    if agegroup = "results1" then ageresults = "Less than 60 years";
    else if agegroup = "results2" then ageresults = "60 to <65 years";
    else if agegroup = "results3" then ageresults = "65 to <70 years";
    else if agegroup = "results4" then ageresults = "70 to <75 years";
    else if agegroup = "results5" then ageresults = "75 to <80 years";
    else if agegroup = "results6" then ageresults = "80 years and older";
run;

/* Define custom style template */
ods path(prepend) work.templat(update);

proc template;
    define style demostyle;
        class Table /
            Rules = Groups
            Frame = void
            cellpadding = 3
            borderwidth = 1;
            
        style header /
            just = center
            fontweight = bold
            background = lightgray
            fontsize = 10pt;
            
        replace Body from Document /
            bottommargin = 1.5cm
            topmargin = 2.5cm
            rightmargin = 2cm
            leftmargin = 2cm;
            
        replace fonts /
            'TitleFont' = ("Arial", 11pt, Bold)
            'headingFont' = ("Arial", 10pt, Bold)
            'docFont' = ("Arial", 9pt);
    end;
run;

/* Generate PDF report */
%put NOTE: Creating PDF report at &output_path;

ods pdf file="&output_path" style=demostyle;
ods noproctitle;
ods escapechar = "^";

/* Report titles */
title1 justify=left "&project_name" justify=right "Page ^{thispage} of ^{lastpage}";
title2 "Table 1.1";
title3 "Demographics Summary - Age Distribution by Treatment";
title4 "Simulated Analysis Population";

/* Generate the report */
proc report data=order_results headline split="*" 
    style(report)={width=100% cellpadding=3};
    
    column (order1 ageresults stat placebo low_dose high_dose);
    
    /* Column definitions */
    define order1 / order noprint;
    define ageresults / "*Age Group" 
        style(column)={just=left width=35%} 
        style(header)={just=left};
    define stat / "*Statistic" 
        style(column)={just=left width=12%};
    define placebo / "Placebo*(N=%cmpres(&placebo_n))" 
        style(column)={just=center width=18%};
    define low_dose / "Xanomeline Low Dose*(N=%cmpres(&low_dose_n))" 
        style(column)={just=center width=20%};
    define high_dose / "Xanomeline High Dose*(N=%cmpres(&high_dose_n))" 
        style(column)={just=center width=15%};
    
    /* Footnotes */
    footnote1 justify=left "Note: n = number of subjects in age group";
    footnote2 justify=left "Note: Percentages are based on total subjects per treatment";
    footnote3 justify=left "Program: standalone_demographics.sas; Generated: %sysfunc(today(), date9.) %sysfunc(time(), time8.)";
run;

ods pdf close;

/* Clear titles and footnotes */
title;
footnote;

/* Print confirmation message */
%put NOTE: ========================================;
%put NOTE: PDF REPORT GENERATED SUCCESSFULLY!;
%put NOTE: ========================================;
%put NOTE: Project: &project_name;
%put NOTE: Output: &output_path;
%put NOTE: Total subjects: %eval(&placebo_n + &low_dose_n + &high_dose_n);
%put NOTE: - Placebo: &placebo_n subjects;
%put NOTE: - Low Dose: &low_dose_n subjects; 
%put NOTE: - High Dose: &high_dose_n subjects;
%put NOTE: ========================================;

/* Optional: Display summary statistics */
proc freq data=adsl_processed;
    tables trta*agen / nocol nopercent;
    title "Age Group Distribution by Treatment (Verification)";
run;
title;