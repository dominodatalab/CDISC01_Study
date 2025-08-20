filename headfile '/mnt/code/.git/HEAD';
data _null_;
  infile headfile;
  input;
  put _infile_;
run;