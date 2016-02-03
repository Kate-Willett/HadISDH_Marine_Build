# HadISDH_Marine_Build

Notes on modifying EUSTACE_SST_MAT code to work with humidity data.

Kate Willett and Robert Dunn

This code is a branch from:

svn://fcm9/ClimateMonitoringAttribution_svn//EUSTACE/EUSTACE_SST_MAT 

It was branched off by Robert Dunn on 3rd Feb 2016 at some time in the
afternoon.

It is now hosted in a GitHub repository - Robert Dunn and Kate Willett are
collaborators:

https://github.com/Kate-Willett/HadISDH_Marine_Build

******************************************************************
The Plan:

Modify read in routines to pull out dew point temperature (and possibly other
humidity variables when they exist, wet bulb temperaure, relative humidity) and
also humidity related metadata (instrument type, ship height???). 

Add code to convert T and dew point T to q, e, RH, DPD, Tw.

Add qc routines to work on Td, q, e, RH, Tw and DPD.

Add initial pentad climatology fields for Td, q, e, RH, Tw and DPD - most likely from
ERA-Interim so using 1981-2010 climatology period.

Modify the qc software to also run the qc routines.

Add code to bias correct the humidity data for ship height (adjust to 10m)
following methods described in Berry and Kent, 2011.

Add code to bias correct the humidity data for screened instruments verses hand
held instruments following methods described in Berry and Kent, 2011.

Add code to assess uncertainties in the hourly data: rounding, measurement,
height bias adjustment, instrument type adjustment.

Add code to grid the data.

Add code to assess climatological uncertainties at the gridbox scale

Add code to assess the sampling uncertainty at the gridbox scale

Add code to combine the gridbox level uncertainties and also somehow establish a
covariance matrix.


******************************************************************
Work Done:

Feb 3rd 2016
First off I want to see if it runs as is with just a change to the output file
directories. I have modified:

configuration.txt 


Feb 3rd 2016
I have made an OLD_CODE_FEB2016 directory and copied all files as they are into here to
keep a static version of this code for us to look back at if need be. These
files SHOULD NOT be modified.
