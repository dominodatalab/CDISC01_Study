/* autoexec for jenner-check bundle t004_adam_adae
 * Source: prod/adam/ADAE.sas (ADaM ADAE derivation)
 *
 * ADAE.sas (interactive branch) builds adam.adae by merging adam.adsl with
 * sdtm.ae, deriving an analysis visit from the AE start day, sorting, then
 * merging on sdtm.ex by usubjid/visitnum. This autoexec stands in the three
 * inputs the merge reads:
 *   - adam.adsl : USUBJID, ACTARM (subject-level)
 *   - sdtm.ae   : USUBJID, AESTDY, AESOC, AEDECOD, AEREL
 *   - sdtm.ex   : USUBJID, VISITNUM, EXTRT, EXDOSE
 * 6 subjects (2 per arm) with adverse events whose start days fall in each of
 * the three visit windows the program derives (1-12 -> 3, 13-161 -> 4,
 * 162+ -> 12). Jenner auto-creates the ADAM / SDTM librefs backed by WORK so
 * the program below can reference adam.adsl, sdtm.ae and sdtm.ex as written.
 */
options obs=100;

data adam.adsl;
    length usubjid $20 actarm $30;
    usubjid = "SUBJ-0001"; actarm = "Placebo";              output;
    usubjid = "SUBJ-0002"; actarm = "Placebo";              output;
    usubjid = "SUBJ-0003"; actarm = "Xanomeline Low Dose";  output;
    usubjid = "SUBJ-0004"; actarm = "Xanomeline Low Dose";  output;
    usubjid = "SUBJ-0005"; actarm = "Xanomeline High Dose"; output;
    usubjid = "SUBJ-0006"; actarm = "Xanomeline High Dose"; output;
run;

data sdtm.ae;
    length usubjid $20 aesoc $40 aedecod $40 aerel $10;
    /* aestdy chosen to land in each visit window: 1-12, 13-161, 162+ */
    usubjid="SUBJ-0001"; aestdy=5;   aesoc="Nervous system disorders";   aedecod="Headache";  aerel="POSSIBLE";    output;
    usubjid="SUBJ-0001"; aestdy=40;  aesoc="Gastrointestinal disorders"; aedecod="Nausea";    aerel="NOT RELATED"; output;
    usubjid="SUBJ-0002"; aestdy=170; aesoc="Nervous system disorders";   aedecod="Dizziness"; aerel="PROBABLE";    output;
    usubjid="SUBJ-0003"; aestdy=8;   aesoc="Gastrointestinal disorders"; aedecod="Diarrhoea"; aerel="DEFINITE";    output;
    usubjid="SUBJ-0004"; aestdy=90;  aesoc="Skin disorders";             aedecod="Rash";      aerel="POSSIBLE";    output;
    usubjid="SUBJ-0005"; aestdy=200; aesoc="Nervous system disorders";   aedecod="Headache";  aerel="NOT RELATED"; output;
    usubjid="SUBJ-0006"; aestdy=15;  aesoc="Cardiac disorders";          aedecod="Palpitations"; aerel="POSSIBLE"; output;
run;

data sdtm.ex;
    length usubjid $20 extrt $30;
    /* exposure records keyed by the derived analysis visit number */
    usubjid="SUBJ-0001"; visitnum=3;  extrt="Placebo";              exdose=0;  output;
    usubjid="SUBJ-0001"; visitnum=4;  extrt="Placebo";              exdose=0;  output;
    usubjid="SUBJ-0002"; visitnum=12; extrt="Placebo";              exdose=0;  output;
    usubjid="SUBJ-0003"; visitnum=3;  extrt="Xanomeline Low Dose";  exdose=54; output;
    usubjid="SUBJ-0004"; visitnum=4;  extrt="Xanomeline Low Dose";  exdose=54; output;
    usubjid="SUBJ-0005"; visitnum=12; extrt="Xanomeline High Dose"; exdose=81; output;
    usubjid="SUBJ-0006"; visitnum=4;  extrt="Xanomeline High Dose"; exdose=81; output;
run;
