/* autoexec for jenner-check bundle t003_tfl_t_vscat
 * Source: prod/tfl/t_vscat.sas (Vital Signs Categorical Summary)
 *
 * t_vscat.sas reads ADAM.ADVS (vital signs analysis dataset). For a hermetic
 * run this autoexec stands in a small mock ADVS with the columns the table
 * consumes: USUBJID, VISITNUM, ACTARM, VSTEST, VSTESTCD, VSSTRESN.
 *
 * 9 subjects (3 per arm). For each subject, three parameters
 * (SYSBP / DIABP / PULSE) are recorded at one baseline visit (visitnum 2,
 * which the table filters out) and two post-baseline visits (visitnum 4, 8).
 * Some post-baseline values are deliberately outside the SAP limits so the
 * High / Low criteria columns are exercised. Jenner auto-creates the ADAM
 * libref backed by WORK so the table program can read adam.advs as written.
 */
options obs=100;

data adam.advs;
    length usubjid $20 actarm $30 vstest $20 vstestcd $8;
    array params[3] $8 _temporary_ ("SYSBP" "DIABP" "PULSE");
    array labels[3] $20 _temporary_ ("Systolic BP" "Diastolic BP" "Pulse Rate");
    /* base values per param: SYSBP, DIABP, PULSE */
    array basev[3] _temporary_ (120 75 72);
    do s = 1 to 9;
        usubjid = cats("SUBJ-", put(s, z4.));
        if s <= 3 then actarm = "Placebo";
        else if s <= 6 then actarm = "Xanomeline Low Dose";
        else actarm = "Xanomeline High Dose";
        do p = 1 to 3;
            vstestcd = params[p];
            vstest   = labels[p];
            do visitnum = 2, 4, 8;
                /* deterministic excursion: subject 1,4,7 push a high SYSBP,
                   subject 3,6,9 push a low PULSE at the later visit */
                vsstresn = basev[p];
                if visitnum = 8 and vstestcd = "SYSBP" and mod(s,3) = 1 then vsstresn = 150;
                if visitnum = 8 and vstestcd = "PULSE" and mod(s,3) = 0 then vsstresn = 52;
                if visitnum = 4 and vstestcd = "DIABP" and mod(s,3) = 2 then vsstresn = 95;
                output;
            end;
        end;
    end;
    drop s p;
run;
