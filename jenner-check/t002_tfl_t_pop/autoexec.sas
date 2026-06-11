/* autoexec for jenner-check bundle t002_tfl_t_pop
 * Source: prod/tfl/t_pop.sas (Summary of Populations table)
 *
 * t_pop.sas reads ADAM.ADSL (created upstream by prod/adam/ADSL.sas from the
 * SDTM snapshot on a NetApp volume). For a hermetic run this autoexec stands
 * in a small mock ADSL with the columns the table consumes: USUBJID, ACTARM,
 * AGE, SEX. 90 subjects, 30 per treatment arm, ages spread across the six
 * SAP age bands. Jenner auto-creates the ADAM libref backed by WORK, so the
 * table program below can reference adam.adsl exactly as written.
 */
options obs=100;

data adam.adsl;
    length usubjid $20 actarm $30 sex $1;
    call streaminit(20230509);
    do i = 1 to 90;
        usubjid = cats("SUBJ-", put(i, z4.));
        if i <= 30 then actarm = "Placebo";
        else if i <= 60 then actarm = "Xanomeline Low Dose";
        else actarm = "Xanomeline High Dose";
        /* ages spread across the six SAP bands: <60,60-,65-,70-,75-,80+ */
        select (mod(i, 6));
            when (0) age = 57;
            when (1) age = 62;
            when (2) age = 67;
            when (3) age = 72;
            when (4) age = 77;
            when (5) age = 82;
            otherwise age = 65;
        end;
        if rand("uniform") < 0.55 then sex = "F";
        else sex = "M";
        output;
    end;
    drop i;
run;
