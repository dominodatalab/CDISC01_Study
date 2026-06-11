/* autoexec for jenner-check bundle t005_adam_advs
 * Source: prod/adam/ADVS.sas (ADaM ADVS derivation)
 *
 * ADVS.sas (interactive branch) builds adam.advs by merging the subject-level
 * adam.adsl with the SDTM vital signs domain sdtm.vs by USUBJID, keeping the
 * VS records. This autoexec stands in the two inputs the merge reads:
 *   - adam.adsl : USUBJID, ACTARM, AGE, SEX (subject-level)
 *   - sdtm.vs   : USUBJID, VISITNUM, VSTESTCD, VSTEST, VSSTRESN (vital signs)
 * 6 subjects (2 per arm), each with systolic/diastolic BP and pulse recorded
 * at a baseline and a post-baseline visit. Jenner auto-creates the ADAM / SDTM
 * librefs backed by WORK so the program below can reference adam.adsl and
 * sdtm.vs as written.
 */
options obs=100;

data adam.adsl;
    length usubjid $20 actarm $30 sex $1;
    usubjid="SUBJ-0001"; actarm="Placebo";              age=64; sex="F"; output;
    usubjid="SUBJ-0002"; actarm="Placebo";              age=71; sex="M"; output;
    usubjid="SUBJ-0003"; actarm="Xanomeline Low Dose";  age=58; sex="F"; output;
    usubjid="SUBJ-0004"; actarm="Xanomeline Low Dose";  age=66; sex="M"; output;
    usubjid="SUBJ-0005"; actarm="Xanomeline High Dose"; age=77; sex="F"; output;
    usubjid="SUBJ-0006"; actarm="Xanomeline High Dose"; age=69; sex="M"; output;
run;

data sdtm.vs;
    length usubjid $20 vstestcd $8 vstest $20;
    array codes[3] $8  _temporary_ ("SYSBP" "DIABP" "PULSE");
    array names[3] $20 _temporary_ ("Systolic BP" "Diastolic BP" "Pulse Rate");
    array basev[3]     _temporary_ (122 78 70);
    do s = 1 to 6;
        usubjid = cats("SUBJ-", put(s, z4.));
        do p = 1 to 3;
            vstestcd = codes[p];
            vstest   = names[p];
            do visitnum = 2, 6;
                vsstresn = basev[p] + mod(s + visitnum, 5);
                output;
            end;
        end;
    end;
    drop s p;
run;
