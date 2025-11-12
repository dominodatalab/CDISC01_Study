/******************************************************************************
* NetApp-only SAS setup (CDISC01)
* ____________________________________________________________________________
* ENV VARS (required unless noted):
* - SDTM_DATASET   : SDTMBLIND | SDTMUNBLIND      (user supplies WITHOUT CDISC01_ prefix)
* - SNAPSHOT_TAG   : e.g. PROD_NOV112025          (exact directory name; no transforms)
* - DOMINO_WORKING_DIR (optional; for sasautos)
* - DOMINO_PROJECT_NAME (optional; logged)
*
* BEHAVIOR:
* - INTERACTIVE (SAS Studio) -> DEV volumes
* - BATCH (SYSIN set)        -> PROD volumes
*
* NETAPP ROOTS USED:
* - /mnt/netapp-volumes/CDISC01_CSR_DATA_DEV
* - /mnt/netapp-volumes/CDISC01_CSR_DATA_PROD
* - /mnt/netapp-volumes/CDISC01_CSR_OUTPUT_DEV
* - /mnt/netapp-volumes/CDISC01_CSR_OUTPUT_PROD
* - /mnt/netapp-volumes/snapshot-tags/CDISC01_SDTMBLIND/<SNAPSHOT_TAG>
* - /mnt/netapp-volumes/snapshot-tags/CDISC01_SDTMUNBLIND/<SNAPSHOT_TAG>
*
* LIBNAMES CREATED:
* - SDTM   : read-only snapshot tag path
* - ADAM   : <CSR_DATA_[DEV|PROD]>/adam
* - ADAMQC : <CSR_DATA_[DEV|PROD]>/qc/adam
* - TFL    : <CSR_OUTPUT_[DEV|PROD]>/tfl
* - TFLQC  : <CSR_OUTPUT_[DEV|PROD]>/qc/tfl
******************************************************************************/

%macro __setup();

  /* ----------------------------- */
  /* Globals                       */
  /* ----------------------------- */
  %global
    __WORKING_DIR
    __PROJECT_NAME
    __SNAPSHOT_TAG
    __SDTM_DATASET
    __SDTM_VOLUME
    __netapp_root
    __runmode
    __target_env
    __full_path
    __prog_path
    __prog_name
    __prog_ext
    __DATA_ROOT
    __OUT_ROOT;

  /* ----------------------------- */
  /* Read environment              */
  /* ----------------------------- */
  %let __WORKING_DIR   = %sysget(DOMINO_WORKING_DIR);
  %let __PROJECT_NAME  = %sysget(DOMINO_PROJECT_NAME);
  %let __SNAPSHOT_TAG  = %sysget(SNAPSHOT_TAG);
  %let __SDTM_DATASET  = %sysget(SDTM_DATASET);

  %if %superq(__SNAPSHOT_TAG)= %then %put %str(ER)ROR: Environment variable SNAPSHOT_TAG is required.;
  %if %superq(__SDTM_DATASET)= %then %put %str(ER)ROR: Environment variable SDTM_DATASET is required.;

  /* Normalize SDTM_DATASET (user provides SDTMBLIND/SDTMUNBLIND only) */
  %let __SDTM_DATASET = %upcase(%superq(__SDTM_DATASET));
  %if &__SDTM_DATASET = SDTMBLIND %then %let __SDTM_VOLUME = CDISC01_SDTMBLIND;
  %else %if &__SDTM_DATASET = SDTMUNBLIND %then %let __SDTM_VOLUME = CDISC01_SDTMUNBLIND;
  %else %do;
    %put %str(ER)ROR: SDTM_DATASET must be SDTMBLIND or SDTMUNBLIND (received=&__SDTM_DATASET).;
  %end;

  /* ----------------------------- */
  /* Determine run mode            */
  /* ----------------------------- */
  %let __runmode=UNKNOWN;

  /* INTERACTIVE (SAS Studio has _SASPROGRAMFILE) */
  %if %symexist(_SASPROGRAMFILE) %then %do;
    %let __full_path = %sysfunc(coalescec(&_SASPROGRAMFILE.));
    %let __runmode=INTERACTIVE;
    %put %str(TR)ACE: (setup) Running in SAS Studio (INTERACTIVE).;
  %end;
  /* BATCH (SYSIN set) */
  %else %if %quote(%sysfunc(getoption(sysin))) ne %str() %then %do;
    %let __full_path = %quote(%sysfunc(getoption(sysin)));
    %let __runmode=BATCH;
    %put %str(TR)ACE: (setup) Running in BATCH SAS.;
  %end;

  %if %superq(__full_path)= %then %put %str(WAR)NING: Cannot determine program name/path;

  /* Program name/path components */
  %local filename;
  %let filename    = %scan(&__full_path,-1,/);
  %let __prog_path = %substr(&__full_path.,1,%index(&__full_path.,&filename.)-1);
  %let __prog_name = %scan(&filename,1,.);
  %let __prog_ext  = %scan(&filename,2,.);

  /* ----------------------------- */
  /* Target environment (DEV/PROD) */
  /* ----------------------------- */
  %if %upcase(&__runmode)=INTERACTIVE %then %let __target_env=DEV;
  %else %if %upcase(&__runmode)=BATCH %then %let __target_env=PROD;
  %else %let __target_env=DEV; /* default */

  %put %str(TR)ACE: (setup) Target environment = &__target_env.;

  /* ----------------------------- */
  /* NetApp roots                  */
  /* ----------------------------- */
  %let __netapp_root   = /mnt/netapp-volumes;

  %let __DATA_DEV_ROOT  = &__netapp_root./CDISC01_CSR_DATA_DEV;
  %let __DATA_PROD_ROOT = &__netapp_root./CDISC01_CSR_DATA_PROD;

  %let __OUT_DEV_ROOT   = &__netapp_root./CDISC01_CSR_OUTPUT_DEV;
  %let __OUT_PROD_ROOT  = &__netapp_root./CDISC01_CSR_OUTPUT_PROD;

  %if &__target_env=DEV %then %do;
    %let __DATA_ROOT = &__DATA_DEV_ROOT;
    %let __OUT_ROOT  = &__OUT_DEV_ROOT;
  %end;
  %else %do;
    %let __DATA_ROOT = &__DATA_PROD_ROOT;
    %let __OUT_ROOT  = &__OUT_PROD_ROOT;
  %end;

  /* ----------------------------- */
  /* Libraries                     */
  /* ----------------------------- */

  /* SDTM via snapshot-tags (read-only) */
  libname SDTM
    "&__netapp_root./snapshot-tags/&__SDTM_VOLUME./&__SNAPSHOT_TAG."
    access=readonly;

  /* ADaM / QC (R/W) */
  libname ADAM    "&__DATA_ROOT./adam";
  libname ADAMQC  "&__DATA_ROOT./qc/adam";

  /* TFL / QC (R/W) */
  libname TFL     "&__OUT_ROOT./tfl";
  libname TFLQC   "&__OUT_ROOT./qc/tfl";

  /* ----------------------------- */
  /* SASAUTOS                      */
  /* ----------------------------- */
  options
    MAUTOSOURCE
    MAUTOLOCDISPLAY
    sasautos=(
      "&__WORKING_DIR./share/macros"
      ,"/mnt/imported/code/SCE_STANDARD_LIB/macros"
      ,SASAUTOS
    );

/* ----------------------------- */
/* Redirect logs (BATCH only)    */
/* ----------------------------- */
%if %upcase(&__runmode)=BATCH %then %do;

  %local __log_dir __base_root __is_tfl __is_qc
         __PROD_DATA_ROOT __PROD_OUT_ROOT __path_lc;

  /* PROD roots for log placement */
  %let __PROD_DATA_ROOT = &__netapp_root./CDISC01_CSR_DATA_PROD;
  %let __PROD_OUT_ROOT  = &__netapp_root./CDISC01_CSR_OUTPUT_PROD;

  /* Classifiers */
  %let __path_lc = %lowcase(&__prog_path.);
  %let __is_tfl  = %sysfunc(index(&__path_lc.,/tfl/))>0;   /* TFL if path contains /tfl/ */
  %let __is_qc   = %upcase(%substr(&__prog_name,1,3)) = QC_; /* QC if program starts with qc_ */

  /* Choose PROD base root: TFL -> OUTPUT_PROD, else -> DATA_PROD */
  %if &__is_tfl %then %let __base_root = &__PROD_OUT_ROOT.;
  %else            %let __base_root = &__PROD_DATA_ROOT.;

  /* Choose logs or qc/logs */
  %if &__is_qc %then %let __log_dir = &__base_root./qc/logs;
  %else            %let __log_dir = &__base_root./logs;

  %put TRACE: (setup) Batch log -> &__log_dir./&__prog_name..log (is_tfl=&__is_tfl is_qc=&__is_qc);
  %put TRACE: (setup) Also copying to /mnt/artifacts/logs/&__prog_name..log;

  /* Primary log to PROD volume */
  proc printto log="&__log_dir./&__prog_name..log" NEW;
  run;

  /* Duplicate log to /mnt/artifacts/logs */
  proc printto;
  run;

  data _null_;
    infile "&__log_dir./&__prog_name..log" recfm=n;
    file "/mnt/artifacts/logs/&__prog_name..log" recfm=n;
    input c $char1.;
    put c $char1.;
  run;

%end;

%mend __setup;

/* Run setup */
%__setup;

/* Trace for reproducibility */
%put TRACE: [PROJECT_NAME=&__PROJECT_NAME] [SDTM_DATASET=&__SDTM_DATASET] [SDTM_VOLUME=&__SDTM_VOLUME];
%put TRACE: [SNAPSHOT_TAG=&__SNAPSHOT_TAG] [runmode=&__runmode] [env=&__target_env] [prog=&__prog_name..&__prog_ext];
%put TRACE: [DATA_ROOT=&__DATA_ROOT] [OUT_ROOT=&__OUT_ROOT];

libname _all_ list;
/* EOF */

