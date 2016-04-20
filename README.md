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

Add code to bias correct the humidity data for screened instruments verses hand
held instruments following methods described in Berry and Kent, 2011.
DONE

Add code to bias correct the humidity data for ship height (adjust to 10m)
following methods described in Berry and Kent, 2011. DO AFTER ADJ FOR SCREEN (Berry Thesis 2009 says to do this)
DONE

Add code to assess uncertainties in the hourly data: rounding, measurement,
height bias adjustment, instrument type adjustment.
DONE

Add code to grid the data: THIS IS NOT SO SIMPLE!
- first grid to closest 3 hourly (00, 03....21) 1by1s (most likely using the anomalies) - could use winsorising or median?
- average time first over days in the 1by1s - mean of at least 4 obs per day, check for sampling in both halves of day, may mean over both halves and then mean of means
- average dailies to pentad 1by1s (at least 2 days present) - mean
- average dailies to monthly 1by1s (at least 50% of days present) - mean
- average monthly 1by1s over 5by5 grids (at least one 1by1) - mean
DONE - ROBERT

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
APR 20th
[KW]
After MUCHOS bug fixing I have finally output monthyears of extended (bias corrected) and uncertainty (on the hourly ob) data in ERAclimBC.
Theses can now be read in a gridded.

I have worked through:
- skipping silly values AT/DPT < -80, > 65, SHU == 0. (COULD BE DONE IN make_and_full_qc.py!!!)
- made sure the read in doesn't treat # as comments and therefore misread in some obs
- pulling out the climatological P
- faking a solar bias correction 
  - faking a solar bias uncertainty
- applying a 3.4% reduction in q for all unaspirated/unventilated obs (EOT/EOH = S or SN, PT = Buoy/Platform) or 3.4%*0.3 for all unassigned obs
  - applying a 0.2 g/kg uncertainty in q to all adjusted obs
- estimating a height based on HOT/HOB, adjusted HOA (as long as its bigger than 2m), adjusted HOP (as long as its bigger than 2m), 16m*nmonths*increment to
2007, buoy = 4, platform = 20.. estHOA = height +10.
    # Parameters (gradients and intercept) for HOA and HOP linear equations
    HOAGradPre2004 = 0.502
    HOAIntCPre2004 = 5.44
    HOAGradPost2004 = 0.753
    HOAIntCPost2004 = (-2.06)
    HOPGrad = 1.03
    HOPIntC = (-0.93)
    
    # Increments for estimating height by YR and MN 
    StHeight = 16.
    EdHeight = 24.
    StYr = 1973 # assume January
    EdYr = 2007 # assume December 2006 so 2007 gives correct NYrs and better for testing which year later.
    MnInc = (EdHeight / StHeight) / (((EdYr) - StYr) * 12.) # should be ~0.2
- ensured that all of these heights are floats!!!
- estimated height adjustments for at adn shu and derived for all other variables
  - made these zero where adjustment makes shu <0 or at > 100 or where it cannot stabalise sensibly - some silly values are still getting in
  - esimated height adjustment uncertainty 0.1 for given heights, 0.5% for esimated heights.
- estimated uncertainty in measurement following HadISDH land and based on marine air temperature derived unc in RH
    t_bins = np.array([-40,-30,-20,-10,0,10,20,30,40,50,100])	# degrees C
    # 1 sigma uncertainty in RH corresponding to t_bins
    rh_unc_bins = np.array([15,15,15,10,5,2.75,1.8,1.35,1.1,0.95,0.8]) 
    # 1 sigma uncertainty in AT
    t_unc = 0.2
    # 1 sigma uncertaint in CWB
    tw_unc = 0.15
    rh_unc = rh_unc_bin[np.where(t_bins > ATtbc)[0]][0]
- estimated uncertainty in roundind by adding 0.5 to AT and or DPT and deriving when the ATround/DPTround flag = 1 (trk > 24 obs has >50% .0s) or
  where the ob is a zero and is from a deck/year in the AT or DPT lists where DECKS have .0s >2x any other decimal.
- combined uncetainties in quadrature

These now need gridding and we need to think about how to combine the uncertainties.  

APR 15th
[KW]
It seems to be working very close to David Berry's code which is now in this file.

The Test_HeightCorrect.py figures look very different though. 
BIGGEST (VERY LARGE) adjustments in VERY STABLE conditions.
Smallest changes in VERY UNSTABLE or neutral conditions (where L is +ve but very large!)
Changes get bigger towards neutrality as a -VE L gets more -ve (is this neutral?).
This does seem to make some sense with fig. 9.5 in p377 of Stull 1988.

import HeightCorrect as hc

adjDB,hDB = hc.run_davidberry_final(10.,15.,8.,6.,20.,18.,18)
adjK,hK = hc.run_heightcorrection_final(10.,15.,8.,6.,20.,18.,18)
adjDB['at_10m'] = 13.788, adjDB['shu_10m'] = 7.872 (u_10m = 4.262)
hDB['L'] = 6.654, hDB['u_star'] = 0.085

adjK['at_10m'] = 13.750, adjK['shu_10m'] = 7.861  (u_10m = 4.246)
hK['L'] = 9.34, hK['u_star'] = 0.120 

# LOW WIND SPEED
adjDB,hDB = hc.run_davidberry_final(10.,15.,8.,3.,20.,18.,18)
adjK,hK = hc.run_heightcorrection_final(10.,15.,8.,3.,20.,18.,18)
adjDB['at_10m'] = 10.015, adjDB['shu_10m'] = 7.540 (u_10m = -0.300)
hDB['L'] = 0.013, hDB['u_star'] = 0.0003

adjK['at_10m'] = 12.802, adjK['shu_10m'] = 7.757 (u_10m = 1.515)
hK['L'] = 0.054, hK['u_star'] = 0.0014 

Our t_star and q_star methods are still quite different.
In this version I now have Yx for zx/L and Yx10 for 10/L. (Y is PSI!!!)
I have altered the calc_flux from david berry to not include the PSI (I call them Y) parameters when calculating the neutral elements at 10m.
I have altered the PSI (Y!) calculations in david berry's code to include teh **-1 **-2 and **-1 that appeared to be missing.
I have changed david berry's GAMMA constant to 5 to match mine. I could make them both 8 instead as in David's original code.

My code differs in that I use the Bretherton iteration method.
I also have some catch for neutral conditions (where -0.01 < zx/L < 0.01) which forces PHIx = 1 and Y(PSI!!!)=0.

I don't change q (SHU) to q/1000. except for when calculating vpt and vt. This doesn't appear to have a large effect - perhaps because its usage is
in a relative sense? I should try this though.

I also don't convert AT to Kelvin using the adiabatic lapse rate adjustment and I use 273.15 instead of 273.16.

My calculation for qsat(sst)*0.98 uses a different equation for vapour pressure - see CalcHums.py


APR 14th
[KW]
I've now coded up run_iterate_L. This didn't work with the Bretherton L equation. It does work using the Stull 1988 L equation with
the B0 (surface buoyancy flux) from Bretheton. I'm not 100% sure this is correct but it does seem to produce something sensible,
converging in <10 iterations.

I discovered that there is sensitivity to the estimation of z0 even though this is tiny and only really varies between 0.0001 and
0.001 over ocean (Stull 1988). The estimation of u_star doesn't vary too much or affect the estimated u10n neutral wind speed at 10m
and the u10m isn't that different to the actual wind speed at 20m. So I start z0_est with u, estimate the drag coefficent Cd, 
estimate u_star, recalculate u10n, recalculate z0, Cd, u_star and then get on with it. 

    It is clear that the resulting L is very sensitive to z0. If I vary it from z0=0.001 to 0.0001.
    z0=0.001 hc.run_iterate_L(10.,15.,8.,3.,20.,18.,18.)
    LresB=4.606 LresS=136.021 
    z0=0.0001 hc.run_iterate_L(10.,15.,8.,3.,20.,18.,18.)
    LresB=3.119 LresS=92.112
    
    z0 = (0.61 + (0.063*u10n))/1000.
    It depends on u10n (neutral wind speed at 10m) 
    u10n = get_hieghtcorrected(u,u_star,k,zu,Ym,L) where Ym = 0 and L can be anything because it is not effective (multiplied by 0!)
    u10n = get_hieghtcorrected(1.,0.05 or 0.5,0.41,20.,0.1000.)
    u10n = 0.915 or 0.155 
    z0 = 0.0007 or 0.0006 (or at u 0.0007)	
    u10n = get_hieghtcorrected(5.,0.05 or 0.5,0.41,20.,0.1000.)
    u10n = 4.915 or 4.155 
    z0 = 0.0009 or 0.0009 (or at u 0.0009)	
    u10n = get_hieghtcorrected(10.,0.05 or 0.5,0.41,20.,0.1000.)
    u10n = 9.915 or 9.155  	
    z0 = 0.0013 or 0.0012 (or at u 0.0012)
    So - u10n isn't very much lower than actual wind speed and its not that sensitive to u_star.
    So - I think from an esimate of u_star we can estimate u10n and z0

I've now created plots of actual and difference adjustments for a range of sst, at, q, u, zu, zt/zq for L -250 to 250, greyed out the
area where little_zeta is < -1 or > 0.5, overplotted the actual resolved adjustment vs L for each scenario. This is a circle where the
scenario is reasonably plausible. THis is an x where the scenario is unlikely - e.g. at = -30, sst = 30.

I have now worked through adjustments converted to all other humidity variables. Conceivably an adjustment could result in changes to
at and shu that are not physically consistent - the most obvious (only obvious?) case would be where the resulting adjustment in
dpt_10m making dpt_10m>at_10m or crh_10m>100%rh. Our main focus here is humidity so my way to solve this is to adjust the at_10m to
match the dpt_10m in such cases - making the assumption that 100%rh was reached. Its actually quite likely that we're going to screw
up the real cases of 100% rh here, quite possibly by making them too low. Not really sure what to do about that.

Annoyingly and predictably, David Berry's code pyflux.py is different from mine and gives quite different results. I can't follow his
code from the literature. His equation for 0.98qsat(sst) is different. He computes q from 0.98 * saturated vapour pressured (sst) and
his equation for calculating vapour pressure is different to mine. His falls over when the wind speed is low - I'm not sure why.
For SST=10., AT=15., SHU=8., U=6., zu = 20., zt = 18., zq = 18
Kates:
'at_10m': 14.70403129871521,'shu_10m': 7.9667163746499501
u10n = 5.5819
'L': 583.07588400518853,
'little_zeta': 0.034300836165418985, 
'z0': 0.00096166329973870399, 
'u_star': 0.24727442321874857, 
'PHIm': 1.171504180827095, 
'PHIt': 1.171504180827095, 
'PHIq': 1.171504180827095, 
'Ym': -0.17150418082709495, 
'Yq': -0.17150418082709495, 
'Yt': -0.17150418082709495,
'q_star': 0.023123821340186777, 
't_star': 0.20562445643519264

Daves:
u, u10n, u10 6.0, 0.38645200748, 3.1855396335 - I think the u10n is too low.
ta, t10n, t10 15.0, 10.3601167406, 12.8379251666
q, q10n, q10 8.0, 7.56546752324, 7.79367791257
ts, qsea     10.0, 7.53033711173,
ustar, tol   0.0182782137428, 7.61230466731


I've also looked/plotted decimal frequencies by decade and for 1973-1981 and 1982-1990. This does show a higher proportion of .0s in
the first period but they are still quite common after too.

APR 13th
[KW]
I've worked a lot on the grids to make sure they were doing what they said on the tin after finding poorer coverage than we had before. This has
now been sorted and unfortunately we just can't increase the coverage enough to provide a climatological average from the data themselves without
relaxing the selection criteria to silly extents - fewer than 10 hrly obs in a 1x1 pentad climatology! The plan now is to go with 'relax' settings
to create 5x5 monthly anomalies (>=1 ob in a 1x1 3hr day/night (shoulders pushed to day), >=1 1x1 3hr grid in a 1x1 day/night_daily grid, >=30% of days in month 1x1 day/night_daily 
grids in a 5x5_day/night_monthly, merge 5x5 monthly day/night) and also pentad climatologies where we can (>=1 ob in a 1x1 3hr day/night (shoulders pushed to day), >=1 1x1 3hr
day/night in a 1x1 3hrpentad day/night, >=1 1x1 3hrpentad day/night (CHECK) in a 1x1 pentad day/night, >=10/15 1x1 pentad day/nights in a 1x1
pentad climatology day/night, merge 1x1 pentad climatology day/night). This method tries to prevent any biasing from more obs coming from the day
or night part of the diurnal cycle by ultimately only averaging between one day and one night component.

I've also been working on the height corrections. I have build HeightCorrect.py which contains all of the algorithms for converting heights based
on Berry 2009, Smith 1980, 1988 and Bretherton lecture. I've first gone through and tested that plausible values are being pushed out - they are.
I've then looked at the sensitivity to the Monin Obukhov Lenght (L) using Test_HeightCorrect.py for a range of heights, AT, SST and SHU. This shows
that the height correction can be quite large (up to 10 deg C or 5 g/kg) in extreme cases. For the most part it would be small but there would be
some error introduced from making a flat assumption of L (-50 in UNSTABLE, SST>AT conditions / 50 in STABLE, SST<AT conditions). Although in some
ways we could argue that this makes a more simple adjustment - and we could probably quantify the error.

As expected - the largest changes are in the lowest layers (e.g., 4m to 10m adjustment >> 16m to 10m adjustment).

I'm now going to code up the iteration to resolve L. It will be interesting to see where this fits between using L = -50 or 50.
DONE



APR 8th
[KW]
I have build PlotDecimalFreq_APR2016.py to look at the frequency of whole numbers verses decimal places throughout the record. I now have a line plot for each year
that shows the total distribution of decimals and then the distribution for each deck present. The percentage of obs in that deck that are also flagged at ATround/DPTround 
is also shown. These statistics - for each year (all obs) are output in text files so I can plot them later if need be. I have also pulled out the number of obs in each deck in
each year just in case we want it - 43 decks represented in total (including ' -1'.

So it looks like the prevalence of .0 is throughout reducing from ~35% to 20% for AT with the most noticeable drop in 1993. It reduces from 30-40% in the 1970s to less than 20%
by 2010s. The biggest drop is in 1980 with a smaller drop in 1982. 

******************
GRRRR - this next bit is only because of the way python does silly things with floats - it seems impossible to actually round to 0.1 so the histogram is screwy!!! 
What is super interesting is the VERY uneven sampling across the decimals. After .0, .5 is the next most
heavily sampled in AT. This is not so noticable for DPT. For both DPT and AT there are VERY few .2,s .4s, .7s and .9s. This is very strange. It happens throughout the entire
record.
**********
So I've changed the bins to capture -0.05 to 0.95 which should then work. How annoying!

Now run for each year and also each decade and 73-81, 82-90 to see the differences.

APR 7th
[KW]
I have now adapted make_and_full_qc.py to use min=1 and max=4 deg stdev for clim check. I could have gone larger but
we do want to make sure as much crud as possible is kicked out and its borderline between keeping data and chucking
rubbish. The max=3 (13.25 deg) threshold resulted in a large cut off, especially for 2015, less bad for 1980. The
max of 4 (18 deg) would allow most of that cluster in. Any bigger and we're including a lot of negative anomalies
that do not look that plausible. I've kept the thresholds the same for AT and DPT even though OBS DPT appears to be more
different to ERA than AT.

I have also added the ATround and DPTround qc flag (in place of nbud which I have no idea what it is). This is part
of the Voyage.find_repeated_values() routine. For any tracks greater than 20 obs in length (same as for repeated
values (rep) and repeated saturation (repsat) where >= 50% of obs are whole numbers, they are flagged as
ATround/DPTround = 1. I've also commented out the 'find_repeated_values' check on SST as I don't think this is
needed.

I'm testing the new versions on Dec 1973 and Jan 2010 which had a few rep values. I would hope the 1973 one at least
has some 'round' values too. Also checkin Jan 2015 to check anoms from clims.

Also edited MDS_basic_KATE.py so that it now reads in ATround and DPTround.

Now need to work on the post-processing new_suite files for bias corrections and uncertainty. Read in using
MDS_basic_Kate.py MDStools. Reprocess using CalcHums and HeightCorrections. Write out using MDStoolsEXTWrite and
MDStoolsUNCwrite. Also then write MDStoolsEXTRead and MDStoolsUNCRead.

All looking ok so rerunning everything with new clim thresholds and round flags

APR 6th
[KW]

Today I have spent a LOT of time thinking about the height corrections. Its almost doable but I'm not 100% sure I'm using the equations correctly, or iterating through appropriately. The
BIG crux seems to be the Monin-Obukhov lenth which requires vertical flux information that we do not have. It could be that it can be approximated by -u*^3/kz but its not clear and I'm not
really sure that we can have a negative u*.

David Berry has been helping A LOT - I now have his thesis which is quite helpful.

I have written a step by step procedure to iterate through but I'm not really confident in it. Parking this until David decides whether he can share his code with me on Monday.

David has also given me his version of the obs for Feb 1994 which has original, height corrected, height and bias corrected version for each observation. I could use this to create a 
new_suite_199401_BERRY,txt version of our own data that we can then select and grid as before. There are no UIDs so I would have to match up using callsign, lat, lon, day, hour, AT, SST. 
I would also have to somehow apply those corrections to the other variables. This is worth doing at some point.

There is an issue in our method because we cannot easily estimate the variance within the gridbox because we are computing from multiple processes. Actually, if we go from 1x1 days to 5x5 
months that might allow a good estimate. This is more difficult if we use my preferred method of 1x1 daily_day/night to 5x5 monthly_day/night then combined to 5x5 monthly. Can we combine 
the standard deviations of the two?

new_suite_197301_ERAclimBC_extended.txt in ERAclimBC - bias corrections, estimated height, estimated exposure, ATround, DPTround: 
shipid
UID
LAT
LON
YR
MO
DY
HR

SST 
SSTA
SLP 

AT   # = original
ATA 
DPT 
DPTA
SHU 
SHUA
VAP 
VAPA
CRH 
CRHA
CWB 
CWBA
DPD 
DPDA

ATtbc  #tbc = total bias corrected (not solar!)
ATAtbc 
DPTtbc 
DPTAtbc
SHUtbc 
SHUAtbc
VAPtbc 
VAPAtbc
CRHtbc 
CRHAtbc
CWBtbc 
CWBAtbc
DPDtbc 
DPDAtbc

AThc   #hc = height corrected
ATAhc 
DPThc 
DPTAhc
SHUhc 
SHUAhc
VAPhc 
VAPAhc
CRHhc 
CRHAhc
CWBhc 
CWBAhc
DPDhc 
DPDAhc

ATsnc
ATAsnc
DPTsnc # snc = screen corrected
DPTAsnc
SHUsnc 
SHUAsnc
VAPsnc 
VAPAsnc
CRHsnc 
CRHAsnc
CWBsnc 
CWBAsnc
DPDsnc 
DPDAsnc

ATslc
ATAslc
DPTslc # slc = solar bias corrected
DPTAslc
SHUslc 
SHUAslc
VAPslc 
VAPAslc
CRHslc 
CRHAslc
CWBslc 
CWBAslc
DPDslc 
DPDAslc

DCK
SID
PT

EOT
EOH
ESTE # estimated exposure
LOV
HOP
HOT
HOB
HOA
ESTH # estimated height

day 
land  
trk   
date1 
date2 
pos   
blklst
dup   

SSTbud   
SSTclim  
SSTnonorm
SSTfreez 
SSTrep   

ATbud   
ATclim  
ATnonorm
ATround # has .0 precision and is part of a track with>= 50% .0 that is longer than 24 obs
ATrep   

DPTbud  
DPTclim 
DPTssat 
DPTround
DPTrep  
DPTrepsat

new_suite_197301_ERAclimNOCSBC_extended.txt in ERAclimNOCSBC - NOCS bias corrections, estimated height, estimated exposure, ATround, DPTround: 
shipid
UID
LAT
LON
YR
MO
DY
HR

AT   # = original
ATA 
SST 
SSTA
SLP 
DPT 
DPTA
SHU 
SHUA
VAP 
VAPA
CRH 
CRHA
CWB 
CWBA
DPD 
DPDA

ATtbc  #tbc = total bias correction from NOCS
ATAtbc 
DPTtbc 
DPTAtbc
SHUtbc 
SHUAtbc
VAPtbc 
VAPAtbc
CRHtbc 
CRHAtbc
CWBtbc 
CWBAtbc
DPDtbc 
DPDAtbc

AThc   #hc = height correction from NOCS
ATAhc 
DPThc 
DPTAhc
SHUhc 
SHUAhc
VAPhc 
VAPAhc
CRHhc 
CRHAhc
CWBhc 
CWBAhc
DPDhc 
DPDAhc

DPTsnc # snc = screen correction from NOCS
DPTAsnc
SHUsnc 
SHUAsnc
VAPsnc 
VAPAsnc
CRHsnc 
CRHAsnc
CWBsnc 
CWBAsnc
DPDsnc 
DPDAsnc

ATslc
ATAslc
DPTslc # slc = solar bias correction from NOCS
DPTAslc
SHUslc 
SHUAslc
VAPslc 
VAPAslc
CRHslc 
CRHAslc
CWBslc 
CWBAslc
DPDslc 
DPDAslc

DCK
SID
PT

EOT
EOH
ESTE # estimated exposure
LOV
HOP
HOT
HOB
HOA
ESTH # estimated height

day 
land  
trk   
date1 
date2 
pos   
blklst
dup   

SSTbud   
SSTclim  
SSTnonorm
SSTfreez 
SSTrep   

ATbud   
ATclim  
ATnonorm
ATround # has .0 precision and is part of a track with>= 50% .0 that is longer than 24 obs
ATrep   

DPTbud   
DPTclim  
DPTssat  
DPTround 
DPTrep   
DPTrepsat

new_suite_197301_ERAclimBC_uncertainty.txt in ERAclimBC

new_suite_197301_ERAclimNOCSBC_extended.txt in ERAclimNOCSBC - NOCS bias corrections, estimated height, estimated exposure, ATround, DPTround: 
shipid
UID
LAT
LON
YR
MO
DY
HR

ATtotU   # = total uncertainty (any difference for anomalies vs actuals?
DPTtotU 
SHUtotU 
VAPtotU 
CRHtotU 
CWBtotU 
DPDtotU 

ATclimU   # = total uncertainty (any difference for anomalies vs actuals?
DPTclimU 
SHUclimU
VAPclimU 
CRHclimU 
CWBclimU 
DPDclimU 

ATheightU   #hc = height correction from NOCS
DPTheightU 
SHUheightU
VAPheightU 
CRHheightU 
CWBheightU 
DPDheightU 

DPTscreenU # snc = screen correction from NOCS
SHUscreenU 
VAPscreenU 
CRHscreenU 
CWBscreenU 
DPDscreenU 

ATsolarU
DPTsolarU # slc = solar bias correction from NOCS
SHUsolarU 
VAPsolarU 
CRHsolarU 
CWBsolarU 
DPDsolarU 

DCK
SID
PT

EOT
EOH
ESTE # estimated exposure
LOV
HOP
HOT
HOB
HOA
ESTH # estimated height

day 
land  
trk   
date1 
date2 
pos   
blklst
dup   

SSTbud   
SSTclim  
SSTnonorm
SSTfreez 
SSTrep   

ATbud   
ATclim  
ATnonorm
ATround # has .0 precision and is part of a track with>= 50% .0 that is longer than 24 obs
ATrep   

DPTbud   
DPTclim  
DPTssat  
DPTround 
DPTrep   
DPTrepsat

The bias corrected obs will be in the normal version
too. Extended will contain both bias corrected and uncorrected actual and anomalies.
Flag for 0s prevalence - use track check. If track is > 50% .0s (and longer than 20 obs - same as repeated value
check), flag as a ATround or
DPTround - use nbud as I have no idea what this is for - or, only list in the _extended.txt
 - Add UNCround for every ob with an ATround and or DPTround.
Apply 3.4% adjustment (reduction) to specific humidity - and back out to all other humidity variables - BEFORE clim
check. Apply this to ship obs from unventilated screens, all buoys and platforms. Apply 1/3rd or this adjustment 
to ship obs with no info (after Josey et al (1999) estimate of 30% unscreened - although we could raise this to 50%?)
A 3.4% reduction in q can be backed out to a change in e, reverse calculate Td, RH, then reverse calculate DPD and
Tw.
 - Add UNCscreen to all obs.
For obs without HOB or HOT - estimate from HOA, HOP or LOV. For obs (ships only) with no height info - estimate 
based on year and linear increment from 16 to 24 m 1973-2007. (HEIGHT ADJ AFTER SCREEN ADJ!!!)
 - Add UNCheight for all esimated heights - will need to have figured out height adjustment.
 - Add UNCheight to buoys +/- 10m - will need to have figured out height adjustment.
 - Add UNCheight to platforms +/- 20m - will need to have figured out heigh adjustment.
Add measurement uncertainty UNCmeas based on table
ALL UNCERTAINTIES WILL BE PROVIDED FOR AT and DPT - and equivalent amounts calculated for all other humidity
variables.


Apr 5th
[KW]
So - last night I created CompareERAOBSclims_APR2016.py to compare OBS-ERA AT and DPT climatologies for pentads 1, 13, 25, 37, 49 and 61.

I was looking for any overall differences between the ERA climatology and that from the obs ICOADS: 
>= 1 ob in 1x1 3hrly, >= 2 1x1 3hrly in 1x1 3hrlypentad, >=4 1x1 3hrlypentad in 1x1 pentad, >= 15 1x1 pentad in 30 year 1x1 pentad climatology 
now looking to relax to:
>= 1 ob in 1x1 3hrly, >= 1 1x1 3hrly in 1x1 3hrlypentad, >=4(or 2) 1x1 3hrlypentad in 1x1 pentad, >= 15 1x1 pentad in 30 year 1x1 pentad climatology 

Really I wanted to see whether we could 'bias correct' ERA-Interim at all. I had thought that the +ve skew in anomalies in the N. Hemi mid-lats that appears in pretty much all of the months I
have looked at so far (AT and DPT) was due a bias between ERA and OBS. The coverage of the OBS is ok but quite poor so it would be better to use ERA to allow more obs to be checked (and
passed?) initially. Actually, it looks like ERA and OBS do not differ as much as I had expected - which is kind of nice! The maps show that the vast majority of obs are within +/- 2 degrees (AT
and DPT). The differences are worse for DPT but not horrendously. You could just about argue that the OBS are warmer/higher dew point than ERA but there are plenty of points (especially over
the northern Pacific) where ERA is warmer. The differences are largest in regions of relatively enclosed seas/coastlines e.g., Norwegian Sea north of Norway, Mediterranean Sea around the
Gibralta Straits, Red Sea adn Persian Gulf, southeast coastline of Africa, southeast coastline of Australia. Although coastlines typically have a higher standard deviation in ERA this isn't the
case for Australia, Africa or the Red Sea/Persian Gulf - which is a shame because then we could relax a little as more obs would be accepted where stdevs are higher. There is some seasonal
variability in the differences. Until we can increase the OBS clim coverage it seems best to use ERA, which is reasonably close, with a largish range permitted (4.5*stdev where max is 4 or 5 
deg?). I have also plotted the differences by latitude and shown a smoothed (+/- 1 deg lat box) median and 25th/75th percentile. The scatter is well spread across zero but the median difference
does suggest an overall warm bias in the obs relative to ERA (~1deg for DPT, <1deg for AT) for most latitudes. The variance (IQR/2th-75th percentiles are much larger for DPT than AT. ERA stdevs
don't appear to be much larger for DPT though.

SHOULD HAVE A QUICk LOOK AT DIFFS FOR q, RH, e, Tw, DPD - THESE COULD WELL BE LARGER!!! DONE larger for RH
SHOULD ALSO HAVE A QUICK LOOK AT DIFF IN STDEVS - REALLY WANT TO USE THE LARGEST!!! DONE Pretty much always smaller for OBS

Apr 4th
[KW]
The PlotMetaData_APR2016.py is now working (and on SLURM as long as matpltlib is set to use 'agg'.
I have run for 
ALL obs
SHIP only (PT = 0-5)
 - SHIP0
 - SHIP1
 - SHIP2
 - SHIP3
 - SHIP4
 - SHIP5
BUOY only (PT = 6 or 8 - moored or ice)
PLATFORM only (PT = 9, 10 or 15)

It is clear from this that there is only really metadata for ships - very very little bit for buoys - instrument type is S/SN (screen, ships screen) for a few, no type for others
It is clear that ships make up the majority of the obs for most of the records but buoys are almost equal by 1999 and a >100000 more by 2002. There are quite a few (<100000) platform obs,
peaking first in the late 1980s and then much more around 2009 to 2013 reaching > 200000 obs. SHIPS 2 (ocean station vessell off station) and 5 (ship) are the most prolific. 

Using a conversion from HOA or HOP to HOB - we can provide an estimate obs height for 30% to 70% of ship obs from 1973 to 2007. HOP looks similar to HOB and HOT (HOT slightly smaller than
HOB - but fewer obs so could just be missing the higher estimates). HOA ~10m higher. For instrument exposre there are 30% to 70% (1973 to 2007) which have info for either thermometer or
hygrometer available - and so can be adjusted where necessary. Around 50% of those with info are from unventilated screens - % ot total obs will be much lower of course  - can assess for
each year deptending on whether we choose to include buoys and platforms (assume all buoys are unaspirated?) Josey et al 1999 (30% estimated to be unventilated - so probably similar). 

For the buoys - can we make an assumption? Only reported height of HOP is 19m which sounds like a lot for a Buoy - perhaps an ice buoy? May be best to ignore buoys as they are 
more likely to be contaminated? http://www.ndbc.noaa.gov/bmanht.shtml suggests height of thermometers at 4m for most NDBC buoys but then puts some barometer heights at ~180m! That sounds a
bit screwy. or at least large uncertainty? +/-10m? For instrument type there are only a few with info 1988,1989, 1994-1997 - 100% unventilated screens!!! So - apply bias correction to ALL
BUOYS!

For the platforms - these could be anything - maybe best to ignore these two? or at least large uncertainty? +/-20m? No info on instrument type - assume unventilated? Add large uncertainty
estimate to account for this!!!

The few SHIP0s (1973-1978 only) with even fewer reported HOA/HOP are around 27m HOA and 18m HOP - quite large st dev.
~30% have instrument type, 50-60% of those are unventilated.

The even fewer SHIP1s (1973-1975) with few reported HOA/HOP are around 25m HOA and 17m HOP - quite large st dev.
46-94% have instrument info - mostly slings/whirlies. <= 20% unventilated screen.

The SHIP2s have no height info or instrument info.

The extremely few (1973-1974) SHIP3s have 25% HOA at 25m HOP at 11 - st dev ~2-3m. All with info are slings/whirlies.

The extremely (2013, 2014) few SHIP4s have no height info. No instrument info.

The VAST majority are SHIP5s and we have HOA/HOP/HOB/HOT for 30-70% of these. HOB/HOT ~22m, HOA ~32m, HOP ~22m. There are also a good number of ships with LOV data 1994 to 2007 which may
add a few more height estimates to obs. 30-75% have instrument info - 30-60% unventilated screens, ~40%
sling/shirlies, ~10% ventilated screen.

We now have MANY text files with various statistics for heights, number of observations, percentage, best fit linear models and also instrument type breakdown:
InstrumentMetaData_*_ERAclimNBC_APR2016.txt
HeightMetaData_*_ERAclimNBC_APR2016.txt
There are plots to go with 'all' but not for 'ships','buoys','platforms' - easy to plot if needed later. All
assessed annually.
Can use these text files to create plots of contributions from obs types/instrument/heights over time.

We probably want to look at obs that get kicked out from qc too - are these predominantly one type?

WORK TO DO:

Progs to write:
Break down of QC failing obs by platform type and instrument type
Break down of prevalance of .0s in each track/deck pre and post 1982

Add to QC - output a new_suite_197301_ERAclimBC_extended.txt: The bias corrected obs will be in the normal version
too. Extended will contain both bias corrected and uncorrected actual and anomalies.
Flag for 0s prevalence - use track check. If track is > 50% .0s (and longer than 24 obs), flag as a ATround or
DPTround - use nbud as I have no idea what this is for - or, only list in the _extended.txt
 - Add UNCround for every ob with an ATround and or DPTround.
Apply 3.4% adjustment (reduction) to specific humidity - and back out to all other humidity variables - BEFORE clim
check. Apply this to ship obs from unventilated screens, all buoys and platforms. Apply 1/3rd or this adjustment 
to ship obs with no info (after Josey et al (1999) estimate of 30% unscreened - although we could raise this to 50%?)
A 3.4% reduction in q can be backed out to a change in e, reverse calculate Td, RH, then reverse calculate DPD and
Tw.
 - Add UNCscreen to all obs.
For obs without HOB or HOT - estimate from HOA, HOP or LOV. For obs (ships only) with no height info - estimate 
based on year and linear increment from 16 to 24 m 1973-2007. (HEIGHT ADJ AFTER SCREEN ADJ!!!)
 - Add UNCheight for all esimated heights - will need to have figured out height adjustment.
 - Add UNCheight to buoys +/- 10m - will need to have figured out height adjustment.
 - Add UNCheight to platforms +/- 20m - will need to have figured out heigh adjustment.
Add measurement uncertainty UNCmeas based on table
ALL UNCERTAINTIES WILL BE PROVIDED FOR AT and DPT - and equivalent amounts calculated for all other humidity
variables.

ALSO: 
Compare OBS clims with ERAclims. Is there an overall 'bias'? Can this be used to adjust ERAclim in any sensible way?
WE can't only use OBSclims because there are too few data points represented. It would be better to bias correct
ERAclim.

NOTES:
1998 06 - way more obs for 1x1 daily day and night rather than the full daily. Monthly coverage is horrendous - even
at 5x5. We REALLY need to increase the coverage so either drastically reducing minimum thresholds. Daily full should
be similar to day and night. Maybe its too much to expect a whole day in a grid box - we coul average all day and
night dailies to 5 by 5 monthlies?

Ultimately - we're gridding anomalies - so can just grid everything within the
month??? Better to take care over the climatologies but the anomalie grids can
be more relaxed.

Also - don't need climatological anomalies - replace with climatological stdevs!


Mar 31st
[KW]
I've been looking at odd months of data to see whether there is much difference between day and nighttime obs. In short - the positive skew in the anomalies is still very
much present in both AT and DPT. So, I think that this is most likely to be a bias relative to the ERA climatologies. We had previously thought that it could be a warm period
related to ENSO or other modes of variability but it is common to all months looked at so far.

The anomalies of both AT and DPT show very clear cutoffs at the limit of the climatology check. This is especially noticeable in the Northern mid-latitudes where the maximum
permitted anomaly is 13 deg (4.5 * sd where sd is set to 3 if it is larger in reality). This is larger than the previous clim test of a flat 10 deg everywhere. You can also
see that the 'good' obs anomalies are generally much narrower than the 'all obs'. By doing this we are removing the obviously bad data very well. However, we're clearly
removing good data too. Its difficult to do a better job here. 4.5*sd is fairly generous for getting rid of outliers (removes <0.1% of data). We could arguably raise the
minimum permitted sd from 0.5 to 1 deg C - so 4.5*1 = 4.5 deg minimum threshold. We could raise the maximum permitted sd from 3 deg to 4 - we could well be losing a lot of
coastal data.

AT from ERA pentad clim st devs (st dev of all pentads going into climatology)
75% within 3deg
84% within 4deg
91% within 5deg
96% within 6deg
mean = 2.1 deg, st dev = 1.76

DPT from ERA pentad clim st devs (st dev of all pentads going into climatology)
71% within 3deg
81% within 4deg
89% within 5deg
95% within 6deg
mean = 2.1 deg, st dev = 1.76

If we allowed min=1 max=4 then 4.5*1 to 4 = 4.5 to 18 deg anomalies permitted - quite a lot but we are dealing with the diurnal cycle verses pentad mean?
So - ok to go with 0.5 and 3 for first stab - to create obs clims - from then on, go with 1 and 4.5. May assess for v2?

Also looked at obs height as provided by HOT, HOB or possibly inferred from LOV, HOP or HOA.
HOT and or HOB are not often present.
Can we infer HOT/HOB from HOA or HOP of LOV?
Generally, HOA is higher than HOP - not a clear relationship.
Generally, HOA is ~12m higher than HOT or HOB but this needs to be tested across more months - does this change over time/latitude etc?
Generally, LOV is ~10*HOT/HOB
I'm now writing some code to read in groups of months, pull out LOV,HOA,HOP,HOT,HOB,PT - and also the type/exposure info TOT, EOT, TOH, EOH
 - plots, EOT/EOH by latitude where 0 = none, 1 = aspirated/ventilated (A/VS), 2 = whirled (SG/SL/W), 3 = screen not aspirated (S/SN), 4 = unscreend (US)
 - prints, number and % of obs with TOT, EOT, TOH and EOH present
 
 - plots, HOB, HOT, HOA, HOP, LOV (second axis?) by latitude
 - prints, number and % of obs with HOB, HOT, HOA, HOP and LOV
 - plots histograms of HOB, HOT, HOA, HOP and LOV
 - prints mean and stdevs
 - plots, HOA vs HOT, HOA vs HOB, HOP vs HOB, HOP vs HOT with lines of best fit
 - prints, number and % where HOA and HOT present, HOA and HOB present, HOP and HOB present, HOP and HOT present, print equation for fit
 - plots difference by Height of anemometer/platform 
 - prints mean and stdevs of differences
 - plots, LOV vs HOT, LOV vs HOB with lines of best fit
 - prints, number and % where LOV and HOB present, where LOV and HOT present and equations for fit
 - plots ratios of HOB and HOT to LOV by length of vessell
 - prints mean and stddev of differences

Mar 30th
[KW]
Some thoughts on the use of median vs mean 
Essentially we're using the average as a way of smoothing in time and space so ideally it would have influence from all viable values
within that time/space period.
The median might be better when we're first using the raw obs to create the 1x1 3 hrlies because we know that there may be some shockers in there.
There is NO expectation that the values would be very similar or very different (not necessarily normally distributed)
After that, we're averaging already smoothed values but missing data may make our resulting average skewed.
There IS an expectation that the values would quite different across the diurnal cycle (quite possibly normally distributed)
For dailies we could set up specific averaging routines depending on the sampling pattern
e.g.,
      All 8 3hrly 1x1s present = mean(0,3,6,9,12,15,18,21)
      6 to 7 3hrly 1x1s present = interpolate between missing vals (if 3 to 18hrs missing), repeat 0=3 or 21=18 (if 0 or 21 hrs missing), mean(0,3,6,9,12,15,18,21)
      5 or fewer 3hrly 1x1s present = mean(mean(0 to 9hrs),mean(12 to 21hrs)) or just mean(0 to 9hrs) or mean(12 to 21hrs) if either one of those results in 0/missing.
a median of 5 values might give you 3 cool values and 2 warm, the 'average' would then be the cool value with no influence from the warmer daytime value (or vice versa)
For pentad or monthlies I think the median or mean would be ok - and median might be safer.
There is NO expectation that the values would be very similar or very different (not necessarily normally distributed) 
For monthly 5x5s I think we should use the mean to make sure the influence of sparse obs are included.
There IS an expectation that the values could quite different across a 500km2 area and 1 month (quite possibly, but not necessarily normally distributed)

RH>100 BUG!!!
I have found a bug. There are many cases of RH>100 in the new_suit..., and therefore the grids - where DPTssat has not been set to 1.
When calculating RH I was using the rounded (to one decimal place) e but the non-rounded es (and a slightly different check on wet bulb<=0.0.
I have modified CalcHums.py to now use the non-rounded version of both - they should be identical if AT == DPT. This will only have affected RH
but for consistency I have now made all conversions go through the non-rounded feed in values - values are only rounded when they are returned 
to the main program. Each equation function now requires DPT, AT and SLP (except for DPD) - and calculates e within. This will take a little more
time unfortunately but reduces the rounding uncertainty a small amount.

RECENT ICOADS:
I'm running this for Jan 2015 with a pointet to the new file directory and names whenever the readyear => 2015. This failed after running for 6 hours. I
don't understand why because the 2015 files are smaller than those for 2014 and all of 2014 (bar December) ran ok. I need to dig a little deeper. The 2015 files are
.Z instead of .gz but unzipped ok using gunzip when I tested it.

I've found a big issue with the climatologies - mid-lats and tropics are far too low in many many cases. The grids in the 1x1 3hrlies have too many grids with 
data present for Dec 1973 - so either this version was created pre-QC-filtering or we're not getting the QC flags right. 138144 obs in new_suite of which 108986 pass
QC for AT and DPT combined. 126105 grids in the 1x1 3hrlies have data present! Also there are far too many cases where
the gridbox value for both AT and DPT is 0.0 - there are only 112 in the new_suite file but 25512 in the gridded file. This could be something to do with the way that
the QC mask is applied?

I should really now look at applying any bias correction that I can - still not heard from David Berry about this.

Mar 29th
[KW]
I have downloaded the 2015 ICOADS data into
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/RECENTICOADS/
from: /project/mds/ICOADS_2.5_IMMA_FILES/latest/IMMA.2015.MM.Z
These files can be gunzipped.
They are almost identical to those at: http://www1.ncdc.noaa.gov/pub/data/icoads2.5/
The NCDC files are IMMA_R2.5P.2015.MM_ENH the 'enhanced' IMMA format
These two version are VERY similar - slightly more obs in the inhouse version - ???
The format is IMMA - so a core of 108 characters (attachment 0) with most of variables and basic info.
This is then followed by attachment number (i2) and attachment length (i2) and each attachment.
For Jan 2015 these all have attachment 1 ( 1) which is 65 characters long (65) including the '65'. 
This has the PT in it and some other info. They then mostly go straight to attachment 99 (99).
THERE IS NO UID!!!

So - my next job is to adapt make_and_full_qc.py to read in this different format for January 2015
onwards.

Easiest thing to try is just to try and read in the files! so - if 2015 then look for a different file
name!

Meanwhile - Robert has created a gridding routine. We explored going from 3hourly 1x1 grids (nearest
hour) to 3hrly 1x1 pentad means (>=3 days worth) and then to full pentad means (>= 4 3hrly pentad means
worth). However, this resulted in fewer grids than if we go from 3hrly 1x1 grids (nearest hour) to daily
1x1 grids (>=4 3hrly grids) to pentad 1x1 grids (>= 3 days worth). This could be because ships move - so
there are unlikely to be very many obs in a gridbox for each 3 hrly but a day could be made up from the
passage of one ship.

Monthlies were previously made up from pentads means but this leads to some leakage at the ends of
months. We can build months from 1x1 dailies (>=50% daily 1x1 grids) and then grid a 5x5 monthly if there is at least 1 monthly 1x1
present. Better comparison with land!


Mar 17th
[KW}
RD discovered that 197304 has a line that is longer than all of the others 414 characters as opposed to 409. A 'wc -L *' shows that this problem is pervasive:
414 new_suite_197304_ERAclimNBC.txt
410 new_suite_198201_ERAclimNBC.txt
410 new_suite_198203_ERAclimNBC.txt
410 new_suite_198204_ERAclimNBC.txt
412 new_suite_198206_ERAclimNBC.txt
410 new_suite_198207_ERAclimNBC.txt
410 new_suite_198210_ERAclimNBC.txt
412 new_suite_198506_ERAclimNBC.txt
412 new_suite_198603_ERAclimNBC.txt
414 new_suite_198605_ERAclimNBC.txt
410 new_suite_198606_ERAclimNBC.txt
410 new_suite_198607_ERAclimNBC.txt
416 new_suite_198609_ERAclimNBC.txt
410 new_suite_198610_ERAclimNBC.txt
412 new_suite_198703_ERAclimNBC.txt
410 new_suite_198709_ERAclimNBC.txt
414 new_suite_198710_ERAclimNBC.txt
412 new_suite_198806_ERAclimNBC.txt
416 new_suite_199003_ERAclimNBC.txt
412 new_suite_199007_ERAclimNBC.txt
412 new_suite_199112_ERAclimNBC.txt
410 new_suite_199212_ERAclimNBC.txt
410 new_suite_199302_ERAclimNBC.txt
412 new_suite_199308_ERAclimNBC.txt
412 new_suite_199409_ERAclimNBC.txt
412 new_suite_199502_ERAclimNBC.txt
410 new_suite_199503_ERAclimNBC.txt
410 new_suite_199802_ERAclimNBC.txt
412 new_suite_199804_ERAclimNBC.txt
412 new_suite_199805_ERAclimNBC.txt
410 new_suite_199812_ERAclimNBC.txt
410 new_suite_199901_ERAclimNBC.txt
410 new_suite_199902_ERAclimNBC.txt
410 new_suite_199903_ERAclimNBC.txt
410 new_suite_199909_ERAclimNBC.txt
410 new_suite_199910_ERAclimNBC.txt
410 new_suite_200001_ERAclimNBC.txt
410 new_suite_200005_ERAclimNBC.txt
410 new_suite_200006_ERAclimNBC.txt
410 new_suite_200007_ERAclimNBC.txt
410 new_suite_200008_ERAclimNBC.txt
410 new_suite_200009_ERAclimNBC.txt
410 new_suite_200010_ERAclimNBC.txt
410 new_suite_200011_ERAclimNBC.txt
412 new_suite_200012_ERAclimNBC.txt
410 new_suite_200101_ERAclimNBC.txt
410 new_suite_200103_ERAclimNBC.txt
410 new_suite_200106_ERAclimNBC.txt
412 new_suite_200107_ERAclimNBC.txt
412 new_suite_200108_ERAclimNBC.txt
412 new_suite_200109_ERAclimNBC.txt
410 new_suite_200110_ERAclimNBC.txt
412 new_suite_200112_ERAclimNBC.txt
412 new_suite_200201_ERAclimNBC.txt
412 new_suite_200202_ERAclimNBC.txt
410 new_suite_200204_ERAclimNBC.txt
410 new_suite_200205_ERAclimNBC.txt
412 new_suite_200207_ERAclimNBC.txt
410 new_suite_200208_ERAclimNBC.txt
412 new_suite_200210_ERAclimNBC.txt
412 new_suite_200402_ERAclimNBC.txt
410 new_suite_200404_ERAclimNBC.txt
412 new_suite_200501_ERAclimNBC.txt
410 new_suite_200503_ERAclimNBC.txt
414 new_suite_200603_ERAclimNBC.txt
412 new_suite_200605_ERAclimNBC.txt
410 new_suite_200703_ERAclimNBC.txt
410 new_suite_200810_ERAclimNBC.txt
412 new_suite_200811_ERAclimNBC.txt
412 new_suite_200901_ERAclimNBC.txt
412 new_suite_200902_ERAclimNBC.txt
410 new_suite_200903_ERAclimNBC.txt
412 new_suite_201002_ERAclimNBC.txt
410 new_suite_201012_ERAclimNBC.txt
412 new_suite_201109_ERAclimNBC.txt
410 new_suite_201112_ERAclimNBC.txt
412 new_suite_201207_ERAclimNBC.txt
410 new_suite_201212_ERAclimNBC.txt
410 new_suite_201303_ERAclimNBC.txt
412 new_suite_201308_ERAclimNBC.txt
412 new_suite_201309_ERAclimNBC.txt
410 new_suite_201410_ERAclimNBC.txt

On further investigation, the long line in 1973 has a VERY LOW AT value (-90 at 30N, 117W is silly). This results in screwy related humidity 
variables: CRH, CWB and DPD. The DPT is ok - ~4degC. The RH is greater than the 8 characters (when divided by 10 for actual and 100 for 
anomalies - so > 9999999.9%rh and 999999.99%rh respectively. This makes the line longer. We can pull out the longest lines using:
egrep -n "^.{$(wc -L < new_suite_198201_ERAclimNBC.txt)}$" new_suite_198201_ERAclimNBC.txt

For 198201 this gives;

line 99512: PIWB      26K4CY     -3880   14300    1982       1       9       0    -819   -9892  -32768  -32768  -32768      89    -222      78     -66     125    -10431101894311011839    -309   -4463    -908   -9670    9999     732      57       5  -32768 BU         1  0 -9 -9  -32768  0     300  0     550  0  -32768   0NL AN  MER W  P W   -999   15 -999 -999 -999  19820 190000099 980019909 810909909 000109900 09999999

So - an AT of -81.9 at 38S, 143E resulting in an anomlay of -98! DPT of 8.9 looks plausible. RH is screwy!

For now, we need a catch in the gridding routine. I will edit the QC suite to check for such silly values and remove them though because the change in line length screws
up the search on QC flags.


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
AT clim and buddy pass: 119238 (86.3%) [18958, 13.7%]
DPT clim and buddy pass: 119618 (86.6%) [18578, 13.4%]

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

+ve skew in anomalies of both DPT and AT:
Unlikely to be solar bias as this shouldn't really affect DPT (check by plotting day vs night?)
Unlikely to be climate change because this is 1973 relative to 1981-2010
Quite likely to be a positive bias in climatology relative to ERA-Interim.

COMPARE WITH Jan 2010:
200971 obs (passing pos, date, blklst and with DPT and AT present!)
94.4 % (189817) DPT anomalies within +/- 10.deg
97.1 % (194895) AT anomalies within +/- 10 deg
DPT clims 0=195919 (97.5%), 1=5052 (2.5%), 8=0 (no stdev - bad pos/date?), 9=0
AT clims 0=196149 (97.6%), 1=4822 (2.4%), 8=0 (no stdev - bad pos/date?), 9=0
SST clims 0=141519 (70.4%), 1=1340 (0.7%), 8=58112 (28.9%) (no stdev - bad pos/date?), 9=0

DPT bud 0=180787 (90.0%), 1=14580 (6.8%), 8=5604 (2.8%), 9=0
AT bud 0=185466 (92.3%), 1=10152 (5.1%), 8=5353 (2.7%), 9=0

DPT and AT clim and buddy pass: 171178 (85.2%)
AT clim and buddy pass: 185466 (92.3%) [15505, 7.7%]
DPT clim and buddy pass: 180787 (90.0%) [20184, 10.0%]

DPT rep 0=200947 (>99.9%), 1=24 (<0.1%), 8=0, 9=0
AT rep 0=200925 (>99.9%), 1=46 (<0.1%), 8=0, 9=0

DPT ssat 0=199920 (99.5%), 1=1051 (0.5%), 8=0, 9=0
DPT repsat 0=200676 (99.9%), 1=295 (0.1%), 8=0, 9=0

trk 0=200329 (99.7%), 1=585 (0.3%), 9=57 (<0.1%) (not passed through to buddy)
land - not set!

DPT and AT clim buddy rep ssat repsat (and trk by default) pass: 170109 (84.6%)
DPT clim buddy rep ssat repsat (and trk by default) pass: 179689 (89.4%)
AT clim buddy rep ssat repsat (and trk by default) pass: 185431 (92.3%)

This is all now written up in the blog (with figures): http://hadisdh.blogspot.co.uk/2016/03/exploring-marine-data-qc.html

I have started to run the QC properly - fingers crossed this will write to ICOADS.2.5.1/ERAclimNBC/new_suite_197312_ERAclimNBC.txt
>sbatch --mem=12000 --time=360 --ntasks=1 --output=mds10MAR2016_19731977.log ./run_MDS_MAR2016.sh 1973 1977 1 12
DOH - should have updated the length of time it can run for!!! Set going at 15:02 - will fall at 18:02. WON'T LET ME GO OVER 360mins (6 hours)
Seems to take ~30mins to complete (for Jan 1973 at least) so we may just be ok.

Jan 2010 investigation:
There is a line of AT and DPT at ~81N that looks a bit odd - stands out from the rest, very little variation in latitude. On further
investigation, all valid obs (not clim fails) are 81.? N and between 138W to 144W. These are mostly shipid=UFTA, with a few shipid=MASKSTID.
All are PT=5 (ship). So these are probably ok.

There is a line of AT and DPT at ~-66S and between 139E adnd(351 obs between -66 and -67S). These are mostly shipid=FHZI and PT=5 (ship). FHZI
has 645 obs in total - all -45 to -67 S and 135-145E. Looking at the time points of the latitude steps the ship sits at ~-66 between 90 to 460
time points. Looking at time series of the actual and anomaly values for AT, DPT and SST it doesn't look so much like something wierd is going
on. SST looks fine although there is a lot of missing data between 90 and 250 time steps. AT looks ok. The temperautre dances around 0 deg for
the 90 to 460 time steps, peaking between 350 and 450 to give anomalies around 10 deg. The anomalies are mostly above zero but not often
peaking more than 6 degrees positive. The location of the ship is just at the Antarctic Circle and very close/possibly on the land mass 
(Magnetic Pole?). Its summer (January) down there so temperatures could be above zero. The DPT is a little more interesting. The actual values
dip down very low between 100 to 200 time steps and again between 430-450. In between those periods it rises close to (but mostly below) zero.
The anomalies are close to zero during the 'dip down' periods and well above zero in between. So, this could be and ERA bias. It could be some
odd data but it could be real - nothing totally crazy. This may lessen when we start using OBSclims?
See ~hadkw/Desktop/HadISDH/MARINEIMAGES/*FHZI* for images and blog post: 
FHZI is an Australian ship: http://www.meteo.shom.fr/cgi-bin/meteo/display_vos_ext.cgi?callchx=FHZI

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


What about solar bias? NOCS has NO solar correction applied to Td - only to T!!!
This shouldn't affect Td directly (or therefore q, e, Td) although it could affect the decision over whether it is an icebulb
but in these cases the humidity is very low.
However, Td is most likely derived from T and Tw or T and RH - so it could be affected - we're seeing positive skew in northern mid-lats anomalies of Td and T for Dec 1973 and Jan
2010. 
Any affect on T but not Td would still affect RH, DPD and Tw and so we either need to bias correct or use night humidities.
If Td is also affected then q, e and Td will also be affected.
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
