# =============================================================================
# Program : adsl.R
# Purpose : Derive ADSL (Subject-Level Analysis Dataset) from SDTM using admiral
# Bundle  : ADSL Dataset (id c96c47f9-a3e6-4fa8-871f-292a8587a97c)
#           Policy: ADaM QC Plan - High Risk; stage: Self QC
# Study   : CDISC01 (project CDISC01_CSR, STUDYID CDISCPILOT01)
# Inputs  : SDTM DM, EX, DS  (volume CDISC01_SDTMBLIND, snapshot v54, SDTM_PATH)
#           Spec: adam_derivations_spec.csv (CDISC01_CSR_DATA_DEV, snapshot v4)
#           No upstream ADaM datasets.
# Output  : adsl.rds / adsl.xpt in ADAM_PATH
# Session : 20261118-131129-628669~3164038a-6809-4f20-bb5f-0efba00494ab
# =============================================================================

library(admiral)
library(dplyr)
library(lubridate)
library(stringr)
library(tibble)
library(haven)

# ---- Read SDTM inputs --------------------------------------------------------
dm <- haven::read_sas(file.path(Sys.getenv("SDTM_PATH"), "dm.sas7bdat")) |>
  convert_blanks_to_na()
ex <- haven::read_sas(file.path(Sys.getenv("SDTM_PATH"), "ex.sas7bdat")) |>
  convert_blanks_to_na()
ds <- haven::read_sas(file.path(Sys.getenv("SDTM_PATH"), "ds.sas7bdat")) |>
  convert_blanks_to_na()

stopifnot(nrow(dm) == dplyr::n_distinct(dm$USUBJID))

# ---- Starting data frame: DM, all variables kept except DOMAIN ----------------
adsl <- dm |>
  select(-DOMAIN)

# ---- Derive: TRT01P, TRT01A · ADaMIG §3.2 ----
# TRT01P / TRT01A from DM.ARM / DM.ACTARM; numeric companions TRT01PN / TRT01AN.
# REVIEW: TRT01PN / TRT01AN added per sponsor standards S-1 / S-3, not in the spec.
#   Numeric codes (1 = Placebo, 2 = Xanomeline Low Dose, 3 = Xanomeline High Dose)
#   are assumed; confirm against the SAP / randomisation schedule.
# REVIEW: "Screen Failure" is a DM.ARM/ACTARM value, not a treatment. Per S-3 these
#   subjects get null TRT01P/TRT01A (not assigned / not treated). Confirm with the statistician.
trt_lookup <- tribble(
  ~TRT, ~TRTN,
  "Placebo",              1L,
  "Xanomeline Low Dose",  2L,
  "Xanomeline High Dose", 3L
)

adsl <- adsl |>
  mutate(
    TRT01P = if_else(ARM %in% trt_lookup$TRT, ARM, NA_character_),
    TRT01A = if_else(ACTARM %in% trt_lookup$TRT, ACTARM, NA_character_)
  ) |>
  derive_vars_merged_lookup(
    dataset_add = trt_lookup |> rename(TRT01P = TRT, TRT01PN = TRTN),
    by_vars     = exprs(TRT01P),
    new_vars    = exprs(TRT01PN)
  ) |>
  derive_vars_merged_lookup(
    dataset_add = trt_lookup |> rename(TRT01A = TRT, TRT01AN = TRTN),
    by_vars     = exprs(TRT01A),
    new_vars    = exprs(TRT01AN)
  )

# ---- Derive: TRTSDTM, TRTEDTM · ADaMIG §3.2 ----
# TRTSDTM / TRTEDTM from EX. EX dates are date-only: time is imputed (start 00:00:00,
# end 23:59:59) and the time imputation flags TRTSTMF / TRTETMF are kept (S-5).
# Dates themselves are not imputed (no partial dates are imputed for end dates, S-5).
ex_ext <- ex |>
  select(-DOMAIN) |>
  derive_vars_dtm(
    dtc             = EXSTDTC,
    new_vars_prefix = "EXST",
    time_imputation = "first",
    flag_imputation = "time"
  ) |>
  derive_vars_dtm(
    dtc             = EXENDTC,
    new_vars_prefix = "EXEN",
    time_imputation = "last",
    flag_imputation = "time"
  )

# REVIEW: "valid dose" = EXDOSE > 0, or EXDOSE == 0 for PLACEBO (placebo patches are recorded
#   with dose 0 in this study: EXTRT PLACEBO/EXDOSE 0, XANOMELINE/54 or 81 mg). Confirm with SAP.
# REVIEW: 6 EX records have missing EXENDTC; they are skipped for TRTEDTM, so a subject whose
#   final EX record has no end date gets the end of the previous record. Confirm handling.
adsl <- adsl |>
  derive_vars_merged(
    dataset_add = ex_ext,
    by_vars     = exprs(STUDYID, USUBJID),
    new_vars    = exprs(TRTSDTM = EXSTDTM, TRTSTMF = EXSTTMF),
    filter_add  = (EXDOSE > 0 | (EXDOSE == 0 & str_detect(EXTRT, "PLACEBO"))) & !is.na(EXSTDTM),
    order       = exprs(EXSTDTM, EXSEQ),
    mode        = "first"
  ) |>
  derive_vars_merged(
    dataset_add = ex_ext,
    by_vars     = exprs(STUDYID, USUBJID),
    new_vars    = exprs(TRTEDTM = EXENDTM, TRTETMF = EXENTMF),
    filter_add  = (EXDOSE > 0 | (EXDOSE == 0 & str_detect(EXTRT, "PLACEBO"))) & !is.na(EXENDTM),
    order       = exprs(EXENDTM, EXSEQ),
    mode        = "last"
  )

# ---- Derive: TRTSDT, TRTEDT · ADaMIG §3.2 ----
# TRTSDT / TRTEDT: date part of TRTSDTM / TRTEDTM.
adsl <- adsl |>
  derive_vars_dtm_to_dt(source_vars = exprs(TRTSDTM, TRTEDTM))

# ---- Derive: TRTDURD · ADaMIG §3.2 ----
# TRTDURD = TRTEDT - TRTSDT + 1 (days, unrounded; admiral default adds one day).
adsl <- adsl |>
  derive_var_trtdurd()

# ---- Derive: SAFFL, ITTFL · ADaMIG §3.2 ----
# Population flags are Y/N (ADaMIG 3.2 Table 3.2.3: subject-level population flags cannot be blank;
# sponsor standard S-4).
# REVIEW: the generic admiral guidance says Y/NA for all flags; ADaMIG 3.2 and sponsor S-4 say
#   population flags are Y or N. Followed ADaMIG / S-4 here. Record-level flags stay Y/null.
# REVIEW: SAFFL = at least one EX record with a valid dose (EXDOSE > 0, or EXDOSE == 0 for PLACEBO).
#   Confirm against the SAP.
# REVIEW: ITTFL = randomized, i.e. ARMCD not missing and not "Scrnfail" (52 screen failures in DM).
#   Confirm against the SAP.
adsl <- adsl |>
  derive_var_merged_exist_flag(
    dataset_add   = ex,
    by_vars       = exprs(STUDYID, USUBJID),
    new_var       = SAFFL,
    condition     = EXDOSE > 0 | (EXDOSE == 0 & str_detect(EXTRT, "PLACEBO")),
    true_value    = "Y",
    false_value   = "N",
    missing_value = "N"
  ) |>
  mutate(
    ITTFL = if_else(!is.na(ARMCD) & ARMCD != "Scrnfail" & ARM != "Screen Failure", "Y", "N")
  )

# ---- Derive: EOSSTT, DCSREAS · ADaMIG §3.2 ----
# EOSSTT / DCSREAS from the DS record with DSCAT == "DISPOSITION EVENT" (one per subject).
# DS "OTHER EVENT" records (FINAL LAB VISIT / FINAL RETRIEVAL VISIT) are not dispositions.
ds_eos <- ds |>
  select(-DOMAIN) |>
  filter(DSCAT == "DISPOSITION EVENT")

stopifnot(nrow(ds_eos) == dplyr::n_distinct(ds_eos$USUBJID))

# REVIEW: EOSSTT mapping: COMPLETED -> COMPLETED; SCREEN FAILURE -> null (not enrolled in the
#   treatment phase, so no end-of-study status); any other DSDECOD (AE, DEATH, withdrawal,
#   sponsor termination, ...) -> DISCONTINUED; subjects with no disposition record -> ONGOING.
#   Confirm treatment of DEATH and STUDY TERMINATED BY SPONSOR with the statistician.
# REVIEW: DCSREAS is null for screen failures as well as completers (they have no EOSSTT);
#   the spec says "DSDECOD when not COMPLETED", so SCREEN FAILURE could alternatively be kept.
adsl <- adsl |>
  derive_vars_merged(
    dataset_add    = ds_eos,
    by_vars        = exprs(STUDYID, USUBJID),
    new_vars       = exprs(
      EOSSTT = case_when(
        DSDECOD == "COMPLETED"      ~ "COMPLETED",
        DSDECOD == "SCREEN FAILURE" ~ NA_character_,
        TRUE                        ~ "DISCONTINUED"
      )
    ),
    missing_values = exprs(EOSSTT = "ONGOING")
  ) |>
  derive_vars_merged(
    dataset_add = ds_eos,
    by_vars     = exprs(STUDYID, USUBJID),
    new_vars    = exprs(DCSREAS = DSDECOD),
    filter_add  = !DSDECOD %in% c("COMPLETED", "SCREEN FAILURE")
  )

# ---- Derive: AGEGR1 · ADaMIG §3.2 ----
# AGEGR1 per spec: <65 / 65-80 / >80 (AGE in years, DM.AGEU = YEARS).
# REVIEW: spec cut points (<65, 65-80, >80) override sponsor standard S-2 (<65, >=65); spec has priority.
# REVIEW: AGEGR1N added per sponsor standard S-1, not in the spec (1 = <65, 2 = 65-80, 3 = >80).
adsl <- adsl |>
  mutate(
    AGEGR1 = case_when(
      AGE < 65               ~ "<65",
      AGE >= 65 & AGE <= 80  ~ "65-80",
      AGE > 80               ~ ">80",
      TRUE                   ~ NA_character_
    ),
    AGEGR1N = case_when(
      AGEGR1 == "<65"   ~ 1L,
      AGEGR1 == "65-80" ~ 2L,
      AGEGR1 == ">80"   ~ 3L,
      TRUE              ~ NA_integer_
    )
  )

# ---- Derive: DTHFL · ADaMIG §3.1.5 ----
# DTHFL = "Y" if a death date (DM.DTHDTC) is present, otherwise null (Y/null flag, ADaMIG 3.1.4).
# Overwrites the DM.DTHFL carried over from the DM spine so the flag follows the spec rule.
adsl <- adsl |>
  mutate(DTHFL = if_else(!is.na(DTHDTC), "Y", NA_character_))

# ---- Finalize: labels, QC and outputs ----
# ---- Variable labels (ADaMIG labels for standard variables; sponsor S-7) -------
labels <- c(
  STUDYID  = "Study Identifier",
  USUBJID  = "Unique Subject Identifier",
  SUBJID   = "Subject Identifier for the Study",
  SITEID   = "Study Site Identifier",
  RFSTDTC  = "Subject Reference Start Date/Time",
  RFENDTC  = "Subject Reference End Date/Time",
  RFXSTDTC = "Date/Time of First Study Treatment",
  RFXENDTC = "Date/Time of Last Study Treatment",
  RFICDTC  = "Date/Time of Informed Consent",
  RFPENDTC = "Date/Time of End of Participation",
  DTHDTC   = "Date/Time of Death",
  AGE      = "Age",
  AGEU     = "Age Units",
  SEX      = "Sex",
  RACE     = "Race",
  ETHNIC   = "Ethnicity",
  ARMCD    = "Planned Arm Code",
  ARM      = "Description of Planned Arm",
  ACTARMCD = "Actual Arm Code",
  ACTARM   = "Description of Actual Arm",
  COUNTRY  = "Country",
  DMDTC    = "Date/Time of Collection",
  DMDY     = "Study Day of Collection",
  TRT01P   = "Planned Treatment for Period 01",
  TRT01PN  = "Planned Treatment for Period 01 (N)",
  TRT01A   = "Actual Treatment for Period 01",
  TRT01AN  = "Actual Treatment for Period 01 (N)",
  TRTSDTM  = "Datetime of First Exposure to Treatment",
  TRTSTMF  = "Time Imputation Flag, First Exposure",
  TRTEDTM  = "Datetime of Last Exposure to Treatment",
  TRTETMF  = "Time Imputation Flag, Last Exposure",
  TRTSDT   = "Date of First Exposure to Treatment",
  TRTEDT   = "Date of Last Exposure to Treatment",
  TRTDURD  = "Total Treatment Duration (Days)",
  SAFFL    = "Safety Population Flag",
  ITTFL    = "Intent-To-Treat Population Flag",
  EOSSTT   = "End of Study Status",
  DCSREAS  = "Reason for Discontinuation from Study",
  AGEGR1   = "Pooled Age Group 1",
  AGEGR1N  = "Pooled Age Group 1 (N)",
  DTHFL    = "Subject Death Flag"
)
stopifnot(all(nchar(labels) <= 40))

# ---- Column order (sponsor S-8) ------------------------------------------------
col_order <- c(
  "STUDYID", "USUBJID", "SUBJID", "SITEID",
  "AGE", "AGEU", "AGEGR1", "AGEGR1N", "SEX", "RACE", "ETHNIC", "COUNTRY",
  "ARMCD", "ARM", "ACTARMCD", "ACTARM", "TRT01P", "TRT01PN", "TRT01A", "TRT01AN",
  "SAFFL", "ITTFL",
  "TRTSDTM", "TRTSTMF", "TRTEDTM", "TRTETMF", "TRTSDT", "TRTEDT", "TRTDURD"
)
adsl <- adsl |>
  select(any_of(col_order), everything())

for (v in intersect(names(labels), names(adsl))) {
  attr(adsl[[v]], "label") <- labels[[v]]
}

# ---- QC assertions --------------------------------------------------------------
stopifnot(nrow(adsl) == dplyr::n_distinct(adsl$USUBJID))
stopifnot(nrow(adsl) == nrow(dm))
if ("EOSSTT" %in% names(adsl)) {
  stopifnot(all(adsl$EOSSTT %in% c("COMPLETED", "DISCONTINUED", "ONGOING", NA)))
}
if ("DCSREAS" %in% names(adsl) && "EOSSTT" %in% names(adsl)) {
  stopifnot(all(is.na(adsl$DCSREAS[adsl$EOSSTT %in% c("COMPLETED", "ONGOING")])))
}
for (f in intersect(c("SAFFL", "ITTFL"), names(adsl))) {
  stopifnot(all(adsl[[f]] %in% c("Y", "N")))
}
if ("DTHFL" %in% names(adsl)) stopifnot(all(adsl$DTHFL %in% c("Y", NA)))
if (all(c("TRTSDT", "TRTEDT") %in% names(adsl))) {
  stopifnot(all(adsl$TRTEDT >= adsl$TRTSDT, na.rm = TRUE))
}

# ---- Write outputs ---------------------------------------------------------------
out_dir <- Sys.getenv("ADAM_PATH")
saveRDS(adsl, file.path(out_dir, "adsl.rds"))
haven::write_xpt(adsl, file.path(out_dir, "adsl.xpt"), version = 5)
