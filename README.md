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

Modify code to only use ship and moored buoy platform types - should speed up a little in later years with ARGOs?
DONE

Modify read in routines to pull out dew point temperature (and possibly other
humidity variables when they exist, wet bulb temperaure, relative humidity) and
also humidity related metadata (instrument type, ship height???). 
DONE

Add code to convert T and dew point T to q, e, RH, DPD, Tw.
DONE

Add qc routines to work on Td, q, e, RH, Tw and DPD.
DONE (just T and Td though!)

Add initial pentad climatology fields for Td, q, e, RH, Tw and DPD - most likely from
ERA-Interim so using 1981-2010 climatology period.

Modify the qc software to also run the qc routines.

Add code to bias correct the humidity data for ship height (adjust to 10m)
following methods described in Berry and Kent, 2011.

Add code to bias correct the humidity data for screened instruments verses hand
held instruments following methods described in Berry and Kent, 2011.

Add code to assess uncertainties in the hourly data: rounding, measurement,
height bias adjustment, instrument type adjustment.

Add code to grid the data: THIS IS NOT SO SIMPLE!
- first grid to closest 3 hourly (00, 03....21) 1by1s (most likely using the anomalies) - could use winsorising or median?
- average time first in the 1by1s
- average dailies to 5by5s

Add code to assess climatological uncertainties at the gridbox scale

Add code to assess the sampling uncertainty at the gridbox scale

Add code to combine the gridbox level uncertainties and also somehow establish a
covariance matrix.

DAVID: Exploring 1982 shift
i) Using just Deck 926 (International Maritime Meteorological (IMM) Data) create difference maps of mean anomaly q 1983-1986 minus 1978-1981 like Figure 4.17 of your PhD thesis. 
ii) Repeat using just Deck 732, just Deck 889, just Deck 892, just Deck 896. 
iii) Repeat using all the remaining decks combined: essentially decks 254 and 927.

If iii) displays no bias, then re-create the marine humidity dataset up to 1983 using it and any other decks which also show no bias. Possibly do collocated comparisons between bias-free and biased decks to understand the problem better, but I expect that adjustment of a biased deck would be fraught with too many difficulties? 
If iii) displays the bias, Dave Berry may be correct in ascribing it to real climatic fluctuations.


******************************************************************
Work Done:

Mar 7th
[RD] Gridding code taking shape.  Working on all variables at the moment (might as well).  Using a simple
mean of observations in the 1x1 box.  Outputting test netcdf file.  Working on 3hourlies (most obs at
those times).  Will probably need SPICE for running in the end - 3hourlies and 1x1 for 17 variables lead
to large arrays for each month.

Mar 4th
Tested new pentad dataset and it looks much better - clims pulled out appear to match with those I pulled out by hand.
I've now opened up the clim read in for all variables except SLP (did this get created?) and am testing for Dec 1973.
??
I've also written the qc.supersat_check() in qc.py which tests whether a valid Td is greater than a valid T. Need to test. 


Feb 16th 

I have now created 1by1 degree pentad climatology files for all variables from
ERA-Interim based on 1981-2010. I used the makeERApentads_FEB2016.pro IDL code 
in /data/local/hadkw/HADCRUH2/UDPATE2015/PROGS/IDL/. These are stored in 
/project/hadobs2/hadisdh/land/UPDATE2015/OTHERDATA/ and have been copied across 
to /project/hadobs2/hadisdh/marine/otherdata/. I've adapted
make_and_full_qc.py to read in all clims but commented them out for now. I have
uncommented everything linked with DPT climatology to test and now listed in 
the configuration.txt.

Testing for December 1973

Next:
Read in climatologies and getanoms for all other variables.
Build the supersat QC test for DPT and test.
Sort out a DPT buddy check.


Feb 9th

Temporarily commented out buddy_check for SST and AT (and DPT) to save time on debugging.

Now pulling through all extra metadata to ascii which took a little faffing to explicitly set when its missing from the ob. Tested read in
and output for Dec 1973 - OK!

Now working out whether there are some meta that are so rarly used that there is very little point pulling them through:
Dec 1973:
self.data['II']  # ID Indicator
self.data['IT']  # AT Indicator - quite a few
self.data['DPTI']# DPT Indicator - a few
*self.data['RHI'] # RH Indicator - NONE
*self.data['RH']  # RH - NONE
self.data['WBTI']# WBT Indicator - a few 
self.data['WBT'] # WBT - many
self.data['DI']  # Wind Direction Indicator - many
self.data['D']   # Wind Direction - many
self.data['WI']  # Wind Speed Indicator - many 
self.data['W']   # Wind Speed -many
self.data['VI']  # Visibility Indicator - many
self.data['VV']  # Visibility - many
self.data['DUPS']# Duplicate? - all
self.data['COR'] # Country of residence - some
self.data['TOB'] # Type of barometer - quite a few
self.data['TOT'] # Type of thermometer - quite a few
self.data['EOT'] # Exposure of thermometer - quite a few
*self.data['LOT'] # Screen location - NONE
self.data['TOH'] # Type of hygrometer - quite a few
self.data['EOH'] # Exposure of hygrometer - quite a few
self.data['LOV'] # Length of vessel - NONE, some 2001 - is this really necessary? A check on height or if height doesn't exist?	   
self.data['HOP'] # Height of vis obs platform - some
*self.data['HOT'] # Height of AT sensor - NONE but optimistic?
self.data['HOB'] # Height of barometer - NONE, some 2001
self.data['HOA'] # Height of anemometer - some 
self.data['SMF'] # Source Metadata file - some

Test for a few more year/months before ditching.
Tested 2001 - decided to ditch RHI, RH and LOT 

Next:
Create climatology files and pull through anoms, clim and nonorm.

Create files for buddy check and pull through bud and bbud.

Run!



Feb 8th 2016

Qs:
What happens if an ob is reported with a missing data identifier e.g. -99.9? Will that be read as None? Does this ever happen or would it
just be blank?

How is the QC flag for nbud set and what is it? I can only find mention of it in 'print_report' in Extended_IMMA.py. Does self.qc.get_qc just
return 0 if there is no flag set?

Starting to work on QC for DPT. Most of these can be done as for SST and AT:
- 'bud' and 'bbud' is the buddy check and bayesian buddy check. It is set to 1 if an ob is too desimilar to its neighbours in space and time.
- 'clim' fails if value is greater than given value (8 for SST, 10 for AT and DPT) away from climatology
- 'nonorm' (MEANS NO clim CAN HAVE BEEN PERFORMED - CASE IN ICY ZONES?)
- 'freez' SST ONLY - value below freezing point at that salinity (or there abouts)
- 'ssat' DPT ONLY - DPT value greater than AT implying >100 %rh
- 'noval' no value present for this value in this ob (unnecessary?)
- 'nbud' not sure how this is set - fails if buddy check cannot be performed?
- 'bbud' see above
- 'rep' is done at time of track_check. It is set to 1 (fail) if >= 70%(given threshold 0.7) of obs (where there are more than 20) in a single
track are identical
- 'repsat' DPT ONLY - DPT == AT for a persistent string of track - greater than 2 days? (TRICKY!) HadISD is >24 hours but 100%Rh more likely
over ocean? 


Added blank QC values for DPT (ready to build in real QC functions) and print_report block for DPT. Commented out anything that requires a
climatology or buddy checking files at present. Testing for 1973...OK!

Added a repsat QC test for DPT within the track_check in Extended_IMMA.py. Its actually within the 'find_repeated_values()' function. It
looks for consecutive strings of AT==DPT. If a string is more than 4 obs and >=48 hours in length then all DPT values within have their
repsat flag set to 1. Testing for 1973...the repsat test appears to work at least..OUTPUT OK!


Feb 5th 2016
I've edited with a choice to only pull through ship and moored buoy data and
only data that have a AT and DPT ob present. This 
may not be what we want to do in the long run for the database but it should speed things up for now,
especially in the float dense later years.

I've edited to pull in extra variables, convert to other humidity variables 
(added CalcHums.py) and output the new variables

This is now tested and works - reduces Dec 1973 ob count by ~40%. 

I could switch off SST buddy check, QC and output but in some ways this is a
good check on AT if I want to look at solar bias later so I will keep it.

Next:
Output all extra meta data variables.

Build QC for dewpoint temperature and sort out print_report.

Build climatology files for dewpoint temp, wet bulb temp, vapour pressure,
specific humidity, relative humidity and dew point depression. Run with these
being used to create anomalies (we will have to re run everything again once we
have HadISDH related anomalies.

Build buddy checking files for dew point temperature and implement.


Feb 4th 2016
Made '# KW' comments in make_and_full_qc.py, Extended_IMMA.py, IMMA2.py and
qc.py as I understand the code flow.

Made '# KW' comments on possible ways to speed up the code that may or may not
be possible/sensible:
 - 1) for each loop through the candidate month save the candidate and proceding
 month of processed data for the next candidate month. Shift candidate month to
 be preceding month, proceding month to be candidate month and read in new
 proceding month. This may not be that simple as you may have to reset any track
 and buddy QC flags (unless suggestion 2 can be implemented) and search through the reps for
 any 'YR', 'MO' that match the preceding year and remove. base and other qc
 flags would not need to be reset because they do not use any other obs other
 than clim and st devs.
 - 2) for track check and buddy check only apply process to actual candidate
 years. This would mean parsing the CandYR and CandMO through to the tests
 somehow. This would mean no resetting would be necessary if you keep the needed
 months in the memory for each loop through.

Found a bug:
 - make_and_full_qc.py
 Removed second instance of 'inputfile' which sets it to
 configuration_local.txt
 Added the 'data_base_dir' set up so that the ascii files are output to a
 different directory - changed output code here too.
 Changed 'year' to 'readyear' at line 322 if readyear > 2007: because if the
 candidate year month was 2008, January then it tried to read R2.5.2.2007.12
 instead of R2.5.1.2007.12.
 Note that December 2007 is a bit dodge - its the time when they stopped putting
 in the callsigns. John isn't sure whether this has been corrected for yet ini
 R2.5.1 - we only have R2.5.1 for Dec 2007 in the /project/ archive.
 Note also that from Jan 2008 the file size grows massively - I think this is
 why the code fell over for a run on Jan 2008.
 
Tidied up:
 Its apparent that quite a few of the scripts aren't needed to run from
 make_and_full_qc.py. Some would be needed if the SQL database is invoked. Some
 would be needed should you wish to run any parts seperately. It looks like a
 lot of the individual scripts have now been ingested as functions into a few
 larger scripts: Extended_IMMA.py, qc.py, IMM2.py and qc_new_track_check.py and
 spherical_geometry.py. I'm rerunning with all other files moved to /REDUNDANT/
 to see what happens.
 Ran for Dec 1973 and it has worked fine.
 
Next:
 I would like to try running with some additional things:
 - only pulling through ship and moored buoy. This may not be what we want to do
 in the long run for the database but it should speed things up for now,
 especially in the float dense later years.
 - pulling in extra variables, converting to other humidity variables and
 outputting
 - qc-ing Td in addition to MAT before converting to other humidity variables
 - bringing in ERA as a TD clim and sd
 - buddy checking Td (or is it preferable to buddy check something else?)
 - bias adjustments for Td???
 - uncertainty estimates for all
 
 I would then like to try and optimise the code:
 - remove unnecessary SST qc, track and buddy check to save run time - althouhg it may be a useful
 cross-check on ob quality. Set all to fail on write out.
 - try to save read ins of candidate and proceding month with each iteration to
 save read in and processing time.
 - try to only apply track and buddy check to candidate month
 
 I would then like to try gridding
 - select only night obs
 - select only day obs
 - select both day and night obs?
 - explore gridding of different decks?

Feb 4th 2016
First off I want to see if it runs as is with just a change to the output file
directories. I have modified:

configuration.txt
I have changed all of the filepaths to work with
/project/hadobs2/hadisdh/marine/ and copied over all static files needed from
John's directories. I have changed to my hostname eld256 - Robert will need to
change to his own on his working version.

configuration_commented.txt
I have made a second version of configuration.txt where comments on the lines
can be kept without interfering with the code.


Feb 3rd 2016
I have made an OLD_CODE_FEB2016 directory and copied all files as they are into here to
keep a static version of this code for us to look back at if need be. These
files SHOULD NOT be modified.


******************************************************************
Notes:

Work with make_and_full_qc.py. This doesn't actually build or populate the SQL
database but pulls out and QCs the ICOADS month by month and stores as ASCII.
