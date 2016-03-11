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

Add initial pentad climatology fields for SLP, Td, q, e, RH, Tw and DPD - most likely from
ERA-Interim so using 1981-2010 climatology period.
DONE

Modify the qc software to also run the qc routines.
DONE - testing not buddy check for Td yet though.

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
Mar 11th
[KW]
I've written python code to read in the output files into a dictionary so its
easy to analyse: MDS_basic_KATE.py ReadMDSkate
Dec 1973 tiny clim (latest run with clim threshold min and max
138196 obs (passing pos, date, blklst and with DPT and AT present!)
98.4 % (135998) DPT anomalies within +/- 10.deg
99.3 % (137248) AT anomalies within +/- 10 deg
DPT clims 0=133753 (96.8%), 1=4443 (3.2%), 8=0 (no stdev - bad pos/date?), 9=0
AT clims 0=132123 (95.6%), 1=6073 (4.4%), 8=0 (no stdev - bad pos/date?), 9=0
SST clims 0=130239 (94.2%), 1=1259 (0.9%), 8=6698 (4.8%) (no stdev - bad pos/date?), 9=0

DPT bud 0=119618 (86.6%), 1=10930 (7.9%), 8=7648 (5.6%), 9=0
AT bud 0=119238 (86.3%), 1=9753 (7.1%), 8=9205 (6.7%), 9=0

DPT and AT clim and buddy pass: 109102 (78.9%)
AT clim and buddy pass: 119238 (86.3%)
DPT clim and buddy pass: 119618 (86.6%)

DPT rep 0=138193 (>99.999%), 1=3 (<0.001%), 8=0, 9=0
AT rep 0=138191 (>99.999%), 1=5 (<0.001%), 8=0, 9=0

DPT ssat 0=138094 (99.9%), 1=102 (0.1%), 8=0, 9=0
DPT repsat 0=138084 (99.9%), 1=112 (0.1%), 8=0, 9=0

trk 0=134655 (97.4%), 1=2303 (1.7%), 9=1238 (0.9%) (not passed through to buddy)
land - not set!

DPT and AT clim buddy rep ssat repsat (and trk by default) pass: 108986 (78.9%)
DPT clim buddy rep ssat repsat (and trk by default) pass: 119485 (86.5%)
AT clim buddy rep ssat repsat (and trk by default) pass: 119233 (86.3%)

See figures in ~hadkw/Desktop/HadISDH/MARINEIMAGES/197312_*MAR2016.png
So - this all looks like its doing ok in the large scale sense.

COMPARE WITH Jan 2010:
200971 obs (passing pos, date, blklst and with DPT and AT present!)

DPT and AT clim buddy rep ssat repsat (and trk by default) pass: 170109 (84.6%)
DPT clim buddy rep ssat repsat (and trk by default) pass: 179689 (89.4%)
AT clim buddy rep ssat repsat (and trk by default) pass: 185431 (92.3%)



Mar 10th
[KW]
Can now run using SLURM and the run_MDS_MAR2016.sh
This has to be run from /project/hadobs2/hadisdh/marine/PROGS/Build/
Logged in as hadobs ssh -Y hadobs@eld256
>sbatch --mem=8000 --time=180 --ntasks=1 --output=mds10MAR2016.log ./run_MDS_MAR2016.sh 1973 1973 12 12

For the stdev limit on clim check I have now added a minimum test so if stdev is <0.5 then it is set at 4.5*0.5 to make sure we're not kicking out stuff in the very stable tropics.
I have also changed the flag in qc.climatological_check to 8 if it cannot run the test so we have 9 = not used, 8 = unable to test, 1 = fail and 0 = pass.

In theory - this should be a good run. We will have several runs eventually:
ERAclimsNBC: (ERA clim and stdev), no bias corrections
ERAclimsBC: (ERA clim and stdev), with bias corrections for height and screen?
Grid up ERAclimsNBC
Grid up ERAclimsBC
Make NBC OBS-ERA combo clim and stdev (will then need the noval flag to be eraval and somehow read in an extra file where the ERA vals are masked? so 0 = obs and 1 = era)
Make BC OBS-ERA combo clim and stdev (will then need the noval flag to be eraval and somehow read in an extra file where the ERA vals are masked? so 0 = obs and 1 = era)
OBS+ERAclims: OBS+ERA clim and stdev (and mask) file, no bias corrections
OBS+ERAclims: OBS+ERA clim and stdev (and mask) file, no bias corrections
Grid up OBS+ERAclimsNBC
Grid up OBS+ERAclimsBC

So - how often are we going to be able to apply correction for height/screen?
Dec 1973
Height in metres!
No info on height of thermometer HOT or barometer HOB
Some info on height of visual observation HOP and anemometer HOA - not so useful unless assume anemometer is 8m>
thermometer?
Observing height (of thermometer) has increased from ~16m in 1973 to ~24m by 2006 (Kent et al., 2007 in: Berry and
Kent, 2011).
Correct to ~10m above sea level using Smith 1980, Smith 1988 - see Josey et al. 1999.
APPLY CORRECTION TO VARIABLES AFTER CONVERSION!!! IT COULD AFFECT ANOMALIES BECAUSE THE CLIMATOLOGY IS THE SAME BUT THE
SHIPS HAVE GOT HIGHER SO THE ANOMALIES SHOULD GET LOWER WITH RESPECT TO THE CLIMATOLOGY.

ASSUME 16m scaling linearly to 24m between 1973-2006 - so 0.24m increase per year - so in theory we should scale all
observations to ~10m making an assumption of their thermometer height if none is provided.

Quite a lot (>50%?) info on type of thermometer TOT and exposure EOT, and type of hygrometer TOH and exposure EOH.
TOT:
ALC=alcohol thermometer, 
ELE=electronic (resistance ) thermometer, 
MER=dry bulb mercury thermometer
EOT:
A=aspirated, 
S=screen (not ventilated), 
SG=ship's sling, 
SL=sling, 
SN=ship's screen, 
US=unscreened, 
VS=screen (ventilated), 
W=whirling
TOH:
1=hygristor, 
2=chilled mirror, 
3=other, 
C=capacitance, 
E=electric, 
H=hair hygrometer, 
P=psychrometer, 
T=torsion
EOH:
A=aspirated, 
S=screen (not ventilated), 
SG=ship's sling, 
SL=sling, 
SN=ship's screen, 
US=unscreened, 
VS=screen (ventilated), 
W=whirling

Need an assumption when missing - ideally to apply no correction either

Berry and Kent 2011 say screen derived humidities (EOH: S, SN, possibly VS?) should be reduced by 3.4% specific humidity (residual unc =
0.2g/kg).
The effect is worse in low latitudes but this correction does very well. May wish to scale with windspeed? Worse in low winds?
Plot no-EOH obs vs A/SG/SL/US/W possibly VS? by latitude and non-EOH obs vs S/SN/VS to see if there are any patterns in the populations.
This will help us to make an assumption over whether the no-EOH obs are more likely to be screen (greater than A/SG/SL/US/W/VS?) or sling
(greater than S/SN/VS?).


What about solar bias?
This shouldn't affect Td (or therefore q, e, Td) although it could affect the decision over whether it is an icebulb
but in these cases the humidity is very low.
This will affect RH, DPD, Td and Tw and so we either need to bias correct or use night humidities.
Bias correction seems involved and ideally we would perform some analysis to assess how bad this is. Could use the mode
from Berry et al. 2004 and Berry and Kent (2005).
I think for version 1 - use night humidities. Good to show the difference from this baseline anyway.

Mar 9th
[KW] So it ran (from Mar 8th) which is good. I noticed a few things:
	- the order of the obs is different in different runs. The previous run was not sorted after buddy
	so is different again from the initial ones. It should be sorted on time but there are many
	'simultaneous' obs so maybe there is some randomness in the way they are sorted? This may also be
	due to the buddy_check filtering (and so whether it has been switched on or off for the run to save
	time). In particular the day/night filter for AT (and DPT) will change the reps/passes which could?
	affect the sort?
	- for AT (and DPT at the moment) only nighttime (POS, day=0) obs are buddy checked. This is probably
	because only the nighttime obs are passed through. THis may also be because of the large biases in
	daytime. Can't decide whether this is a good or bad thing? We may expect daytime biases to affect
	obs similarly across ships so it shouldn't matter so much???

It does seem to be flagging some values as failing buddy check - quite a few
Supersat QC test seems to be working, and clim (still wonder if 10deg flat is too much/too little - eventually it would be good to
use stdevs from clim instead - should be quite easy to apply that because we have clim stdevs for each variable.
Couldn't see any rep (repeat strings) or repsat (prolongued saturation) flags for December 1973! - this was tested and found to work
previously (FEB 8th) - looked through new_suite_197312_noclim.txt and couldn't see any repsat=1 (fails) - but I did have some print
statements that were then commented out which showed it looking for these. I can't believe they don't exist!

SO IN NEXT RUN I WILL COMMENT OUT THE POS,day=0 filter for both AT and DPT!!!
RUN with AT buddy_check on (including daytime) - see if those that fail DPT also fail AT?
Work on clim test that uses 4.5 stdevs
CHECK repsat thresholds

Dec 1973 run with no day=0 filter for AT or DPT and both AT and DPT buddy checks running:
This runs! It takes a LONG time (hours!). Quite a few obs kicked out for buddy so need to look at if
its more than for AT with old buddy. SOme match up with bayesian buddy. Bayesian buddy seems more
conservative.

Now also written in code to pull through the climatological stdev to each rep (stdev_variables{},add_stdev_variable,StdevVariable,StdevVariable.getstdev(),rep.getstdev().
I've put in a test to look at this (it will slow things down and use more memory unfortunately).
I've changed the climatolgical test within base_qc_report() to apply 4.5*stdev as the limit instead of 10.0 for AT and DPT.
Previous run was 1203 seconds for obs read and base QC.
Running for Dec 1973:
Had to add a catch for when the stdev=None. This happens when there is an issue with the date (i.e. Nov 31st) or pos (lat > 90.0) so it can't find a clim or stdev. In
these cases the limit is set to 10deg (as before) although as there isn't a clim then it will be given a value of 1 (fail) anyway. Going to change this to 8 - not able to set!
This runs! Quite a lot kicked out for climatology so going to add a minimum threshold so that if stdev < 0.5 then it is forced to be 0.5. It can be very low in the tropics.

Mar 8th
[KW] 
If DPT mdsKATE_buddy_check works then try for AT too - do not actually need to run SST for humidity.

Can we think about applying bias corrections for height and screen vs hadnheld now? Produce full set without and full set with - grid both to see the difference.

We should re-run once we have data driven climatologies - although we won't have climatologies for all data points due to cut offs when there are two few obs 
in a gridbox over time. So we may need to augment with ERA over datagap regions? Could create a combo file to read in. Also think about the threshold - 10 deg DPT from clim sounds like quite a
lot. We could use st devs? We could use a smaller threshold. 

Either way, once the buddy check is working we need to produce a file for each month - using SPICE.

BUG FOUND - in original mds_buddy_check which at the moment reads in the HadSST stdev file (73,180,360) but then only ever pulls out the first pentad:
	- get_buddy_limits(pentad_stdev)
	- qc.get_single_sst - this requires the input to be 3dimensional!
	
Taken a few runs to get this pulling out a pentad slice and passing it through - that bit seems to now work (hurrah!) but its just fallen over on the thisyear thismonth filtering. 
It takes AGES to get to this point, even though I've switched off AT and SST buddy check. I've also streamlined the DPT filter prior to buddy check, removing date, pos and blklst because we've
already removed those obs from further processing. I've also removed nonorm from the filter because with ERA (or even later with an ERA/OBS combo) there will always be a norm). I think we
shoudl change nonorm to be eranorm so that we know when we've had to use ERA instead of the obs. Just tried a second run now I've changed squre brackets for curly brackets. Fingers crossed...

Mar 7th
[KW] Assuming everything from last time works:
Apply a filter after basic QC has been applied. Can do this when OBS are filtered in make_and_full_qc.py.
I onlt want to keep those that pass date/pos/blklist (ALREADY filtered for those with AT and DPT present and
those that are ships/moored buoys or platforms using the HadISDHSwitch in the configuration.txt file

I am trying to work out how to apply the buddy check to Td. It looks like the buddy check for T uses SST fields.
MDS buddy check: 
This uses a single stdev for each 1by1 gridbox (no temporal difference) - this is some average standard deviation within the average pentad
 - so could improve this by having a standard deviation that varies in time? And use Td fields (should probably do the same for T - so create ERA t fields too)
 	- ERA t fields (and Td) may have a lower stdev because of the gridded nature initially and 
	- ERA t fields (and Td) may be affected to the move to OSTIA post 2000 - cooler SSTs?
 - also only apply to obs in the candidate year and month - save's time.
 

Bayesian buddy check:
This tries to increase the variance by breaking it down into 4 component parts:
	- measurement error - set to 1.0 deg C
	- stdev1 - sd of a 1by1 pentad box to the 5by5 5pentad average
	- stdev2 - sd of an ob to the 1by1 pentad box (under estimate because OSTIA is still gridded, albeit tiny grids
	- stdev3 - uncertainty in a 1by1 pentad box due to incomplete spatio-temporal sampling.
These have been created using OSTIA which is daily, 0.05by0.05 degrees
I could try and do something similar from ERA but due to the MUCH coarser resolution it wouldn't be very equivalent - far too smooth

SO - NO BAYESIAN BUDDY for DPT or AT!!!
USE SEASONALLY VARYING PENTAD STDEVS FOR AT and DPT - MDS buddy check
ONLY APPLY MDS BUDDY CHECK TO CANDYR and CANDMO 
THESE ARE QUITE MAJOR CHANGES!

I have got rid of any obs that fail the base QC (date/pos/blklist) - this removes 88 obs only! for Dec 1973
I have now set up make_and_full_qc.py to read in stdevs for AT and DPT (those created from all points going into each pentad clim from ERA-Interim (1981-2010).
I have now set up the buddy check to run on DPT (not AT yet - later) to test - only mdsKATE_buddy_check - 
I have now set up mdsKATE_buddy_check in Extended_IMMA.py - takes a 73 pentad field and thisyear, thismonth
	- this finds the right pentad slice (hopefully)
	- this only checks the candidate month reps
	
Testing for December 1973 - but also testing still whether the humidity values stil work now we're reading in SLP
climatolgy from ERA. We don't apply any height correction - all sea level! It did fall over earlier - not sure why really.
It said something about CalcHums not liking float or NoneType - ho hum

ClimSLP works!

Mar 7th
[RD] Gridding code taking shape.  Working on all variables at the moment (might as well).  Using a simple
mean of observations in the 1x1 box.  Outputting test netcdf file.  Working on 3hourlies (most obs at
those times).  Will probably need SPICE for running in the end - 3hourlies and 1x1 for 17 variables lead
to large arrays for each month.

Mar 4th
[KW] Tested new pentad dataset and it looks much better - clims pulled out appear to match with those I pulled out by hand.
I've now opened up the clim read in for all variables except SLP (did this get created?) and am testing for Dec 1973.
It works!
I've also written the qc.supersat_check() in qc.py which tests whether a valid Td is greater than a valid T and am testing on Dec 1973. 


Feb 16th 
[KW] 
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
[KW] 
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
[KW] 
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
[KW] I've edited with a choice to only pull through ship and moored buoy data and
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
[KW] Made '# KW' comments in make_and_full_qc.py, Extended_IMMA.py, IMMA2.py and
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
[KW] First off I want to see if it runs as is with just a change to the output file
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
[KW] I have made an OLD_CODE_FEB2016 directory and copied all files as they are into here to
keep a static version of this code for us to look back at if need be. These
files SHOULD NOT be modified.


******************************************************************
Notes:

Work with make_and_full_qc.py. This doesn't actually build or populate the SQL
database but pulls out and QCs the ICOADS month by month and stores as ASCII.
