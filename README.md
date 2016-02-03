# HadISDH_Marine_Build
Code to work with ICOADS marine data and convert to a monthly mean QC'd gridded product.

The code is based on EUSTACE_SST_MAT marine database suite created by John Kennedy.

It has been modified here to read in extra variables related to humidity (actual observations and additional metadata), apply humidity related QC and bias adjustments, estimate humidity related uncertainty, and grid into a 5 by 5 degree monitoring product.
