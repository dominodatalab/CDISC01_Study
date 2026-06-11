/* autoexec for jenner-check bundle t001_tfl_demographics_table
 * Source: prod/tfl/demographics_table.sas (self-contained, simulated data)
 *
 * This program is fully self-contained: it generates its own ADSL-like
 * dataset with a fixed CALL STREAMINIT seed, so no external SDTM/ADaM data
 * is required. The only adaptation needed is to keep output local:
 *   - provide a default for DOMINO_PROJECT_NAME (read via %sysget upstream)
 *   - the original writes the PDF under /mnt/artifacts/<project>/; here we
 *     leave ODS PDF off and let the LISTING output carry the report so the
 *     run is hermetic.
 *   - the simulated cohort is generated at 90 subjects (30 per arm) instead
 *     of 300 so all three treatment arms are represented within the run;
 *     the derivation, counts, and report are otherwise unchanged.
 */
options obs=100000;
%let DOMINO_PROJECT_NAME = CDISC01;
