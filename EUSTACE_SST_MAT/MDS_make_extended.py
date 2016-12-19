#!/usr/local/sci/bin/python
# PYTHON2.7
# 
# Author: Kate Willett
# Created: 15 April 2016
# Last update: 7 April 2016
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/EUSTACE_SST_MAT/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code reads in the qc'd MDS and outputs the extended version:
# Read in the new_suite QC'd MDS data

# BIAS CORRECTIONS

# Pretend to apply a solar corrections - this may be applied later.

# Obtain exposure information from EOH or EOT or esimate exposure - assume Buoys and platforma are unventilated screens, previously used the
# Josey et al., 1999 apply 30% of adjustment to ships with no info to represent that ~3rd of obs are not ventilated.

# Apply 3.4% q adjustment to all obs with a screened/unventilated exposure (VS, S and SN) (NOT TO BUOYS!) and a ??% of 3.4% to obs with no exposure or
# estimated exposure and convert across other humidity variables. DO this to orig and solar corrected obs.
# We have explored various different ??% to modify the 3.4% in the case of unknown observations (InstrumentMetaDAtaStats_ships_OBSclim2NBC_I300_OCT2016.xlsx 
# and hadisdh.blogspot.co.uk. I'm now going with 55% and a growth factor for 2015 where there are no metadata

# Obtain height info from HOB/HOT/HOP or HOA-10 orestimate height based on platform (ship = 17 to 22.5 scaling linearly every month between ~16m in 
# 1973 to ~24m by 2006 (Kent et al., 2007 in: Berry and Kent, 2011 used 16 to 24 from Jan 1973 to Dec 2006), buoy = assume 4m instrument height (howmany?, platform 
# = no adjustment - LARGE uncertaintyu)

# Use height info, SST (or AT), SLP (or climP), u (or 0.5m if < 0.5, ~6 if missing or > 100m/s) to create an estimated height adjusted 
# value. Do this to orig and solar/screen corrected obs. (fix SST to be between -1.8 and 40. or AT between -1.8 adn 40.)

# Write out orig, total, height, screen, solar to extended along with metadata (including estimated exposure and height) and QC
# flags.

# UNCERTAINTIES

# Apply UNCround uncertainty of 0.05 deg C to AT / DPT if the ATround or DPTround flag is set to 1. (> 50% of trk with at least
# 24 obs are .0s) OR if it is a zero and fits into one of these categories: (0s > 2x mean of others - by eye) xxxx is a fill in where we'll 
# include in the list even though its not shown in the figures - DecimalFreqDiagsDPT_all_ERAclimNBC_YYYYYYYYMMMM.png
# Years with ? are close but not 2X
# Years with ? that are isolated will not be included. This within a string of years will be.
# DPT:
# 254:                                              1982                1986
# 555: 1973 
# 666:      
# 732: 1973 1974 1975 1976 1977 1978 1979 1980 1981 1982 xxxx 1984 1985 xxxx 1987
# 735: 1973 1974 1975 1976 1977 1978 1979 1980 1981 1982 1983 1984 1985 1986 1987
# 792:                                                                                                                              1998 1999 2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015
# 793:                                                                                                                                                  2002?                    2007?
# 794:                                                                                                                                                                                                                   2015                                                                                                                                                   2002?                    2007?
# 849:                               1979
# 850:      
# 874:                                                                                                          1994 1995 1996 1997 xxxx xxxx 2000 2001 2002 2003 2004 2005 2006 2007
# 888: 1973 1974 1975 1976 1977	1978 1979 1980 1981 xxxx xxxx xxxx xxxx 1986 1987 1988 1989 1990 1991 1992 1993	1994 1995 1996 1997	     
# 889: 1973 1974 1975 1976 1977 xxxx 1979 1980 1981 xxxx xxxx 1984 1985 1986 1987 1988 1989 1990 1991 1992 1993 1994
# 892:                                    1980 1981 1982 1983 1984 1985 1986 1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997
# 893:                                                                                                1992?  
# 896:                                    1980 1981 1982 1983 1984 xxxx 1986      
# 926:                                    1980?xxxx 1982?1983?xxxx 1985?xxxx 1987?1988?1989?1990?1991?1992?xxxx xxxx xxxx 1996?1997 1998 1999 2000 xxxx 2002?2003?
# 927:                                                             1985?1986?1987?xxxx 1989?xxxx xxxx xxxx xxxx 1994 1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006 2007
# 992:                                                                                                                                                                                2008 2009 2010 2011 2012 2013 2014?

# AT: 0.5s also an issue to T but ignoring that for now. 555 all 0.5 in 1973!
# 128: 1973 1974 1975 1976 1977 1978
# 223: 1973 1974
# 233:                                                                                 1989 
# 254: 1973 1974 1975 1976 1977 1978 1979 1980 1981 1982 1983 1984 1985 1986 1987 1988 1989 1990 1991 1992
# 732: 1973 1974
# 792:                                                                                                                              1998 1999 2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015
# 793:                                                                                                                                                       2003?
# 794:                                                                                                                                                                                                                   2015
# 849:                               1979
# 850:                               1979
# 874:                                                                                                          1994 1995 1996 1997           2000 2001 2002 2003 2004 2005 2006 2007
# 888: 1973 1974 1975 1976 1977 1978 1979 1980 1981 xxxx 1983 xxxx xxxx 1986 1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997
# 892:                                    1980 1981 1982 1983 1984 1985 1986 1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997
# 893:                                                                                 1989
# 896:                                    1980 1981 1982
# 900: 1973 1974 1975 1976 1977 1978
# 926: 1973 1974 1975 1976 1977 1978 1979 1980 1981 1982 1983 1984 1985 1986 1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006 2007
# 927: 1973 1974 1975 1976 1977 1978 1979 1980 1981 1982 1983 1984 1985 1986 1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997 xxxx 1999 2000 2001 2002 2003 2004 2005 2006 2007
# 992:                                                                                                                                                                                2008 2009 2010 2011 2012 2013 2014                          

# Apply UNCsolar to all observations (daytime temperatures) that have had an adjustment for solar bias

# Apply UNCscreen to all observations that have had an adjustment for being screened/unventilated.

# Apply UNCheight to all observations depending on their height adjustment. Larg uncertainties for buoys +/- 10m? and platforms +/- 20m.

# Apply UNCmeas based on assumption of errors to the dry bulb and wet bulb, converted to other variables.

# Combine all uncertainties (assuming uncorrelated for now)
#
# NOTES:
# All uncertainties are presented as 1sigma
# Individual uncertainties are assessed on the adjustment applied to the tbc (total bias corrected) value because this is the one we will use/
# The uncertainties have NOT been assessed for when the adjustment is applied to the original value in isolation of the other adjustments!!!
# Just noticed some proper screwy values AT = 99.5 in Jan 1982 ob 44650. These should REALLY be kicked out
# in the make_and_full_qc.py so I will add a check in that to kick out AT and DPT < -80 > 65. For now though,
# this needs to be caught - should have failed QC (but will be included in warts and all!
# I've also added a check for SHU = 0.0 as over ocean this isn't really possible. Even if it is, it totally
# screws with the corrections as we get /0.0 in some cases. 
#
# -----------------------
# LIST OF MODULES
# -----------------------
# inbuilt:
# import numpy as np
# import copy
# import sys, os
# import sys, getopt
# import math
# from netCDF4 import Dataset
# import pdb # pdb.set_trace() or c 
#
# Kates:
# from LinearTrends import MedianPairwise - fits linear trend using Median Pairwise
# import HeightCorrect as hc
# import CalcHums as ch
#
# -----------------------
# DATA
# -----------------------
# /project/hadobs2/hadisdh/marine/ICOADS.2.5.1/*/new_suite_197312_ERAclimNBC.txt
# 
# Also requires climatological P for the nearest pentad 1x1 for recalculation of humidity values
# /project/hadobs2/hadisdh/marine/otherdata/p2m_pentad_1by1marine_ERA-Interim_data_19792015.nc
#
# -----------------------
# HOW TO RUN THE CODE
# -----------------------
# python2.7 MDS_make_extended.py --year1 '1973' --year2 '1973' --month1 '01' --month2 '01' --typee 'ERAclimNBC'
# 
# -----------------------
# OUTPUT
# -----------------------
# /project/hadobs2/hadisdh/marine/ICOADS.2.5.1/ERAclimBC/new_suite_197301_ERAclimBC_extended.txt
#
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
#
# Version 2 (12 October 2016)
# ---------
#  
# Enhancements
#  
# Changes
# Instrument Adjustments
#   We now include VS in the list of exposures to have the adjustment applied
#   We now do not apply adjustments to buoys and platforms
#   We now apply 55% of the 3.4% reduction in the case of unknown ship exposures and a growth factor for 2015 where there are no metadata
#
# Height Adjustments
#  We now have two options:
#	1) Apply adjustments based on our own metadata and assumptions
#	  We now have actual HOP as third choice after HOT and HOB - straight up use no calculation - unc = 0.1*adj
#	  If only HOA is present then use conversion from HOA to HOP (HOA-10) - most data available to derive relationship - unc = 0.85*adj
#	  If no height info is available then use linear relationship from new assessment - 17m to 22m (Dec 2000) and beyond - unc = 1*adj
#    	  If buoy assume 4m - unc = 1*adj
#	  If platform do not apply adjustment - unc = T-SST/2 or (q-q0)/2 
#	  If cannot apply adjustment (unstable calc) - unc = T-SST/2 or (q-q0)/2
#	2) Apply adjustments based on NOCS provided height estimates
# I have modified some of the asumptions used for height adjustment:
# 	Wind speed missing - assume moderage of 6m/s
#	Wind speed < 0.5 m/s - assume 0.5m/s minimum
#	Wind speed >= 100m/s ERROR! - assume moderate of 6m/s
#	
# I have modified the uncertainty estimates:
#	See above for height
#	Rounding 0.5/SQRT(3) for just AT or DPT and 1/SQRT(3) for both combined (e.g. RH)
#  
# Bug fixes
#   
#
# Version 1 (16 April 2016)
# ---------
#  
# Enhancements
#  
# Changes
#  
# Bug fixes
#  
# -----------------------
# OTHER INFORMATION
# -----------------------
#
# BIGGEST PROBLEM: We're only storing actual values to 1 decimal place. Many of the bias correctiosn are
# very small. So - when using higher precision it is possible that a bias correction which should DECREASE
# humidity could when populated through all of the humidity calculations result in an INCREASE in humidity.
# WHAT TO DO?
# Could always round to 1 decimal place but then we largely lose the adjustments and its fiddly with the anomalies
# Could just let it be - pretty bad. HO HUM - ultimately we need to preserve the anomalies more!!!
# Is there a better way of doing it that changes the core variables of AT and DPT and then propogates through the humidity variables
# in the same order as they were created in the first place?
# AT and DPT - then all are calculated based on AT and DPT
# How about starting from non-rounded vap, shu, crh, cwb and dpd? So - recalculate from AT and DPT, then start
# At the end this may work out the same but we've given it our best shot
# 
#
#************************************************************************
#                                 START
#************************************************************************
import numpy as np
import copy
import sys, os
import sys, getopt
import math
from netCDF4 import Dataset
import pdb # pdb.set_trace() or c 

import HeightCorrect as hc
import CalcHums as ch
import MDS_RWtools as mrw

SLPClimFilee = '/project/hadobs2/hadisdh/marine/otherdata/p2m_pentad_1by1marine_ERA-Interim_data_19792015.nc'

LocalType = 'local' # 'local' for our own height estimates, 'localNOCS' for NOCS heights

#***********************************************************************************
# FUNCTIONS
#***********************************************************************************
# ReCalcHums
#***********************************************************************************
def ReCalcHums(ExtDict,UncDict,climp,Counter):
    ''' 
    This recalculates the humidity values based on AT and DPT
    so that we can work with higher precisions values.
    This should be ok with applying adjustments to the anomalies
    because we apply the difference between the original and adjusted actual value.
    
    '''
    
    # Get Humidity Values for ExtDict
    ExtDict['SHU'][Counter] = ch.sh(ExtDict['DPT'][Counter],ExtDict['AT'][Counter],climp,roundit=False)
    ExtDict['VAP'][Counter] = ch.vap(ExtDict['DPT'][Counter],ExtDict['AT'][Counter],climp,roundit=False)
    ExtDict['CRH'][Counter] = ch.rh(ExtDict['DPT'][Counter],ExtDict['AT'][Counter],climp,roundit=False)
    ExtDict['CWB'][Counter] = ch.wb(ExtDict['DPT'][Counter],ExtDict['AT'][Counter],climp,roundit=False)
    ExtDict['DPD'][Counter] = ch.dpd(ExtDict['DPT'][Counter],ExtDict['AT'][Counter],roundit=False)
    ExtDict['SHUtbc'][Counter] = ExtDict['SHU'][Counter]
    ExtDict['VAPtbc'][Counter] = ExtDict['VAP'][Counter]
    ExtDict['CRHtbc'][Counter] = ExtDict['CRH'][Counter]
    ExtDict['CWBtbc'][Counter] = ExtDict['CWB'][Counter]
    ExtDict['DPDtbc'][Counter] = ExtDict['DPD'][Counter]
    
    return ExtDict,UncDict

#***********************************************************************************	
# FillABad
#***********************************************************************************
def FillABad(ExtDict,UncDict,Counter):
    ''' 
    This is some temporary code to catch silly values:
        AT < -80 or AT > 65
	DPT < -80 or DPT > 65
	SHU == 0.0 (actually to be sure I've done int(round(SHU*10)) == 0
    This fills in 0.0s for all uncertainties and the original value for all others
    '''
    
    # Fill VARslr
    ExtDict['ATslr'].append(ExtDict['AT'][Counter])
    ExtDict['ATAslr'].append(ExtDict['ATA'][Counter])
    ExtDict['DPTslr'].append(ExtDict['DPT'][Counter])
    ExtDict['DPTAslr'].append(ExtDict['DPTA'][Counter])
    ExtDict['SHUslr'].append(ExtDict['SHU'][Counter])
    ExtDict['SHUAslr'].append(ExtDict['SHUA'][Counter])
    ExtDict['VAPslr'].append(ExtDict['VAP'][Counter])
    ExtDict['VAPAslr'].append(ExtDict['VAPA'][Counter])
    ExtDict['CRHslr'].append(ExtDict['CRH'][Counter])
    ExtDict['CRHAslr'].append(ExtDict['CRHA'][Counter])
    ExtDict['CWBslr'].append(ExtDict['CWB'][Counter])
    ExtDict['CWBAslr'].append(ExtDict['CWBA'][Counter])
    ExtDict['DPDslr'].append(ExtDict['DPD'][Counter])
    ExtDict['DPDAslr'].append(ExtDict['DPDA'][Counter])
    
    # Fill VARscn
    ExtDict['ATscn'].append(ExtDict['AT'][Counter])
    ExtDict['ATAscn'].append(ExtDict['ATA'][Counter])
    ExtDict['DPTscn'].append(ExtDict['DPT'][Counter])
    ExtDict['DPTAscn'].append(ExtDict['DPTA'][Counter])
    ExtDict['SHUscn'].append(ExtDict['SHU'][Counter])
    ExtDict['SHUAscn'].append(ExtDict['SHUA'][Counter])
    ExtDict['VAPscn'].append(ExtDict['VAP'][Counter])
    ExtDict['VAPAscn'].append(ExtDict['VAPA'][Counter])
    ExtDict['CRHscn'].append(ExtDict['CRH'][Counter])
    ExtDict['CRHAscn'].append(ExtDict['CRHA'][Counter])
    ExtDict['CWBscn'].append(ExtDict['CWB'][Counter])
    ExtDict['CWBAscn'].append(ExtDict['CWBA'][Counter])
    ExtDict['DPDscn'].append(ExtDict['DPD'][Counter])
    ExtDict['DPDAscn'].append(ExtDict['DPDA'][Counter])
    
    # Fill VARhc
    ExtDict['AThc'].append(ExtDict['AT'][Counter])
    ExtDict['ATAhc'].append(ExtDict['ATA'][Counter])
    ExtDict['DPThc'].append(ExtDict['DPT'][Counter])
    ExtDict['DPTAhc'].append(ExtDict['DPTA'][Counter])
    ExtDict['SHUhc'].append(ExtDict['SHU'][Counter])
    ExtDict['SHUAhc'].append(ExtDict['SHUA'][Counter])
    ExtDict['VAPhc'].append(ExtDict['VAP'][Counter])
    ExtDict['VAPAhc'].append(ExtDict['VAPA'][Counter])
    ExtDict['CRHhc'].append(ExtDict['CRH'][Counter])
    ExtDict['CRHAhc'].append(ExtDict['CRHA'][Counter])
    ExtDict['CWBhc'].append(ExtDict['CWB'][Counter])
    ExtDict['CWBAhc'].append(ExtDict['CWBA'][Counter])
    ExtDict['DPDhc'].append(ExtDict['DPD'][Counter])
    ExtDict['DPDAhc'].append(ExtDict['DPDA'][Counter])
    
    # Fill VARtbc (Unc only, Ext already set)
    UncDict['ATtbc'].append(ExtDict['AT'][Counter])
    UncDict['ATAtbc'].append(ExtDict['ATA'][Counter])
    UncDict['DPTtbc'].append(ExtDict['DPT'][Counter])
    UncDict['DPTAtbc'].append(ExtDict['DPTA'][Counter])
    UncDict['SHUtbc'].append(ExtDict['SHU'][Counter])
    UncDict['SHUAtbc'].append(ExtDict['SHUA'][Counter])
    UncDict['VAPtbc'].append(ExtDict['VAP'][Counter])
    UncDict['VAPAtbc'].append(ExtDict['VAPA'][Counter])
    UncDict['CRHtbc'].append(ExtDict['CRH'][Counter])
    UncDict['CRHAtbc'].append(ExtDict['CRHA'][Counter])
    UncDict['CWBtbc'].append(ExtDict['CWB'][Counter])
    UncDict['CWBAtbc'].append(ExtDict['CWBA'][Counter])
    UncDict['DPDtbc'].append(ExtDict['DPD'][Counter])
    UncDict['DPDAtbc'].append(ExtDict['DPDA'][Counter])
    
    # Fill VARuncT
    UncDict['ATuncT'].append(0.0)
    UncDict['ATAuncT'].append(0.0)
    UncDict['DPTuncT'].append(0.0)
    UncDict['DPTAuncT'].append(0.0)
    UncDict['SHUuncT'].append(0.0)
    UncDict['SHUAuncT'].append(0.0)
    UncDict['VAPuncT'].append(0.0)
    UncDict['VAPAuncT'].append(0.0)
    UncDict['CRHuncT'].append(0.0)
    UncDict['CRHAuncT'].append(0.0)
    UncDict['CWBuncT'].append(0.0)
    UncDict['CWBAuncT'].append(0.0)
    UncDict['DPDuncT'].append(0.0)
    UncDict['DPDAuncT'].append(0.0)
    	
    # Fill VARuncSLR
    UncDict['ATuncSLR'].append(0.0)
    UncDict['ATAuncSLR'].append(0.0)
    UncDict['DPTuncSLR'].append(0.0)
    UncDict['DPTAuncSLR'].append(0.0)
    UncDict['SHUuncSLR'].append(0.0)
    UncDict['SHUAuncSLR'].append(0.0)
    UncDict['VAPuncSLR'].append(0.0)
    UncDict['VAPAuncSLR'].append(0.0)
    UncDict['CRHuncSLR'].append(0.0)
    UncDict['CRHAuncSLR'].append(0.0)
    UncDict['CWBuncSLR'].append(0.0)
    UncDict['CWBAuncSLR'].append(0.0)
    UncDict['DPDuncSLR'].append(0.0)
    UncDict['DPDAuncSLR'].append(0.0)

    # Fill VARuncSCN
    UncDict['ATuncSCN'].append(0.0)
    UncDict['ATAuncSCN'].append(0.0)
    UncDict['DPTuncSCN'].append(0.0)
    UncDict['DPTAuncSCN'].append(0.0)
    UncDict['SHUuncSCN'].append(0.0)
    UncDict['SHUAuncSCN'].append(0.0)
    UncDict['VAPuncSCN'].append(0.0)
    UncDict['VAPAuncSCN'].append(0.0)
    UncDict['CRHuncSCN'].append(0.0)
    UncDict['CRHAuncSCN'].append(0.0)
    UncDict['CWBuncSCN'].append(0.0)
    UncDict['CWBAuncSCN'].append(0.0)
    UncDict['DPDuncSCN'].append(0.0)
    UncDict['DPDAuncSCN'].append(0.0)

    # Fill VARuncHGT
    UncDict['ATuncHGT'].append(0.0)
    UncDict['ATAuncHGT'].append(0.0)
    UncDict['DPTuncHGT'].append(0.0)
    UncDict['DPTAuncHGT'].append(0.0)
    UncDict['SHUuncHGT'].append(0.0)
    UncDict['SHUAuncHGT'].append(0.0)
    UncDict['VAPuncHGT'].append(0.0)
    UncDict['VAPAuncHGT'].append(0.0)
    UncDict['CRHuncHGT'].append(0.0)
    UncDict['CRHAuncHGT'].append(0.0)
    UncDict['CWBuncHGT'].append(0.0)
    UncDict['CWBAuncHGT'].append(0.0)
    UncDict['DPDuncHGT'].append(0.0)
    UncDict['DPDAuncHGT'].append(0.0)

    # Fill VARuncM
    UncDict['ATuncM'].append(0.0)
    UncDict['ATAuncM'].append(0.0)
    UncDict['DPTuncM'].append(0.0)
    UncDict['DPTAuncM'].append(0.0)
    UncDict['SHUuncM'].append(0.0)
    UncDict['SHUAuncM'].append(0.0)
    UncDict['VAPuncM'].append(0.0)
    UncDict['VAPAuncM'].append(0.0)
    UncDict['CRHuncM'].append(0.0)
    UncDict['CRHAuncM'].append(0.0)
    UncDict['CWBuncM'].append(0.0)
    UncDict['CWBAuncM'].append(0.0)
    UncDict['DPDuncM'].append(0.0)
    UncDict['DPDAuncM'].append(0.0)

    # Fill VARuncR
    UncDict['ATuncR'].append(0.0)
    UncDict['ATAuncR'].append(0.0)
    UncDict['DPTuncR'].append(0.0)
    UncDict['DPTAuncR'].append(0.0)
    UncDict['SHUuncR'].append(0.0)
    UncDict['SHUAuncR'].append(0.0)
    UncDict['VAPuncR'].append(0.0)
    UncDict['VAPAuncR'].append(0.0)
    UncDict['CRHuncR'].append(0.0)
    UncDict['CRHAuncR'].append(0.0)
    UncDict['CWBuncR'].append(0.0)
    UncDict['CWBAuncR'].append(0.0)
    UncDict['DPDuncR'].append(0.0)
    UncDict['DPDAuncR'].append(0.0)
    
    # Fill ESTE and ESTH (Unc and Ext)
    ExtDict['ESTE'].append('XXX')
    UncDict['ESTE'].append('XXX')
    ExtDict['ESTH'].append(-999.)
    UncDict['ESTH'].append(-999.)

    return ExtDict,UncDict

#***********************************************************************************	
# GetClimSLP
#***********************************************************************************
def GetClimSLP(SLPField,TheLat,TheLon,TheMonth,TheDay):
    '''
    This works out which pentad and which gridbox is the closest to the ob
    It pulls out the SLP and returns it.
    
    TheLon must be -180 to 180
    TheLat must be -90 to 90
    There must be a sensible lat, lon, month and day!
    
    SLPField is a 73 pentad, 180 lat, 360 lon array
    
    '''
    
    #Set up the scalar
    ClimSLP = 0.
    
    # Find the nearest gridbox (-180 to 180, 90 to -90, 1x1 gridboxes)
    lat = int(90 - TheLat)
    if (lat == 180):
        lat = 179 # push -90.0 into last (most southerly) box
    lon = int(TheLon + 180.0)
    if (lon == 360):
        lon = 0 # push 180.0 into first western box
    
    # Find the nearest pentad
    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    count = 0
    
    #leap years.
    if TheMonth == 2 and TheDay == 29:
    # INTERESTING - I USUALLY MAKE FeB 29th FEB 28th but John's MDS Goes Mar 1st instead!!!
    # Same result though - becomes pentad 11 (12!)
        TheMonth = 3
        TheDay = 1
    pentad = -99	
    for month in range(1, 13):
        for day in range(1, month_lengths[month-1]+1):
            if month == TheMonth and day == TheDay:
                pentad = count/5
		break	
            count += 1
        # Get out of loop!!! 	    
	if (pentad > -99):
	    break    

# Actually we want 0 to 72 not 1 to 73!
#    pentad = pentad + 1
    
    # Extract SLP
    ClimSLP = SLPField[pentad,lat,lon]
    
    return ClimSLP

#***********************************************************************************
# ApplySolarAdjUnc
#***********************************************************************************
def ApplySolarAdjUnc(ExtDict,UncDict,Counter,ClimP):

    '''
    ExtDict = dictionary of orig AND adjusted values
    UncDict = dicitonary of uncertainty values
    Counter = loop number for finding right original ob    
    ClimP = climatological pentad mean SLP from nearest 1x1 gridbox to ob for humidity calculation 
    
    This applies solar adjustments to each observation.
    It isn't written yet so actually just appends a new ExtDict['XXXslr'], setting
    it to the original value, and setting the UncDict['XXXuncSLR'] 
    values to 0.0
    
    Eventually it will apply a solar bias adjustment to AT.
    It may apply a solar bias correction to DPT.
    The other humidity variables will have a derived adjustment applied accordingly.
    Uncertainty estimates will be made
    
    '''    
    # Append VARslrs using originals for now but would set up as adjusted solar
    ExtDict['ATslr'].append(ExtDict['AT'][Counter])
    ExtDict['ATAslr'].append(ExtDict['ATA'][Counter])
    ExtDict['DPTslr'].append(ExtDict['DPT'][Counter])
    ExtDict['DPTAslr'].append(ExtDict['DPTA'][Counter])
    ExtDict['SHUslr'].append(ExtDict['SHU'][Counter])
    ExtDict['SHUAslr'].append(ExtDict['SHUA'][Counter])
    ExtDict['VAPslr'].append(ExtDict['VAP'][Counter])
    ExtDict['VAPAslr'].append(ExtDict['VAPA'][Counter])
    ExtDict['CRHslr'].append(ExtDict['CRH'][Counter])
    ExtDict['CRHAslr'].append(ExtDict['CRHA'][Counter])
    ExtDict['CWBslr'].append(ExtDict['CWB'][Counter])
    ExtDict['CWBAslr'].append(ExtDict['CWBA'][Counter])
    ExtDict['DPDslr'].append(ExtDict['DPD'][Counter])
    ExtDict['DPDAslr'].append(ExtDict['DPDA'][Counter])
    
    # VARtbc already set to originals, add slr adjustment to them
    # At this point tbs is the same as slr though so just set to skr values
    # For now this is all zero so I've commented it out.
#    ExtDict['ATtbc'][Counter] = ExtDict['ATslr'][Counter]
#    ExtDict['ATAtbc'][Counter] = ExtDict['ATAslr'][Counter]
#    ExtDict['DPTtbc'][Counter] = ExtDict['DPTslr'][Counter]
#    ExtDict['DPTAtbc'][Counter] = ExtDict['DPTAslr'][Counter]
#    ExtDict['SHUtbc'][Counter] = ExtDict['SHUslr'][Counter]
#    ExtDict['SHUAtbc'][Counter] = ExtDict['SHUAslr'][Counter]
#    ExtDict['VAPtbc'][Counter] = ExtDict['VAPslr'][Counter]
#    ExtDict['VAPAtbc'][Counter] = ExtDict['VAPAslr'][Counter]
#    ExtDict['CRHtbc'][Counter] = ExtDict['CRHslr'][Counter]
#    ExtDict['CRHAtbc'][Counter] = ExtDict['CRHAslr'][Counter]
#    ExtDict['CWBtbc'][Counter] = ExtDict['CWBslr'][Counter]
#    ExtDict['CWBAtbc'][Counter] = ExtDict['CWBAslr'][Counter]
#    ExtDict['DPDtbc'][Counter] = ExtDict['DPDslr'][Counter]
#    ExtDict['DPDAtbc'][Counter] = ExtDict['DPDAslr'][Counter]

    # Append uncSLR
    UncDict['ATuncSLR'].append(0.0)
    UncDict['ATAuncSLR'].append(0.0)
    UncDict['DPTuncSLR'].append(0.0)
    UncDict['DPTAuncSLR'].append(0.0)
    UncDict['SHUuncSLR'].append(0.0)
    UncDict['SHUAuncSLR'].append(0.0)
    UncDict['VAPuncSLR'].append(0.0)
    UncDict['VAPAuncSLR'].append(0.0)
    UncDict['CRHuncSLR'].append(0.0)
    UncDict['CRHAuncSLR'].append(0.0)
    UncDict['CWBuncSLR'].append(0.0)
    UncDict['CWBAuncSLR'].append(0.0)
    UncDict['DPDuncSLR'].append(0.0)
    UncDict['DPDAuncSLR'].append(0.0)

    return ExtDict,UncDict

#*****************************************************************************
# ApplyScreenAdjUnc
#*****************************************************************************
def ApplyScreenAdjUnc(ExtDict,UncDict,Counter,ClimP):

    '''
    ExtDict = dictionary of orig AND adjusted values
    UncDict = dicitonary of uncertainty values
    Counter = loop number for finding right original ob   
    ClimP = climatological pentad mean SLP from nearest 1x1 gridbox to ob for humidity calculation 

    EOT/EOH: 
    Assume unaspirated or unwhirled: = 'UNA'
     - None = Non 
     - Screen = S
     - Ship's Screen = SN
     - Ventilated Screen = VS ??? Not sure about this one.
    Assume aspirated or whirled: = 'ASP'
     - Aspirated = A
     - Whirled = W
     - Sling = SL
     - Ship's Sling = SG
     - Unscreened = US 
    PT:
    ships = 0, 1, 2, 3, 4, 5 = U55
    buoys = 6(moored), 8(ice) = ASP
    platforms = 9(ice), 10(oceanographic), 15 (fixed ocean) = ASP
    
    Obtain exposure information from EOH or EOT or estimate exposure - assume Buoys and platforma are suitably ventilated screens, previously used the
    Josey et al., 1999 apply 30% of adjustment to ships with no info to represent that ~3rd of obs are not ventilated.

    Apply 3.4% q adjustment to all obs with a screened/unventilated exposure and
    Apply a 55% of 3.4% q adjustment to obs with no exposure information
    If its 2015 (a period with NO metadata) then grow the (3.4*0.55)*1.14 to account for unavoidable shift in adjustment
    (this is the ratio of the mean adjustment to 2014 (lots of metadata) / mean adjustment to 2015 (no metadata))
    Convert across other humidity variables. DO this to orig and solar corrected obs. Berry and Kent 2011.
    
    Residual Uncertainty in the adjustment is 0.2 g/kg according to Berry and Kent 2011. Strange that its not a percentage too.
    Geographical and Temporal differences remain: 
         ~0.1g/kg +ve bias (UNA still too moist) 1973-1980, -ve bias ~-0.1 g/kg 1980+ peaking to -0.2 g/kg 1988 and 2002 
	 (only assessed to 2002)
	 ~-0.1 g/kg -ve bias 40-60N, 20S and below, ~0.1 g/kg +ve bias 0 to 20S 
    
    '''
    # Set the values to adjust 
    # Use the 3.4 % reduction in q documented adjustment factor from Berry and Kent 2011
    ScnAdjustment = 3.4
    FullAdjFactor = (100. - ScnAdjustment) / 100. # should be 0.966
    # Use 55% as the average percentage of ships with EOH metadata that are poorly ventilated
    PctPoorlyAsp = 0.55
    UnkAdjFactor = (100. - (ScnAdjustment * PctPoorlyAsp)) / 100. # should be 0.9813
    
    # Set the values for when the metadata drop out
    # First year where there are no metadata
    EndofMetaData = 2015
    # Factor to grow the adjustments (last year of metadata mean adjustment / first year of no metadata mean adjustment)
    GrowFactor = 1.14
    GrowUnkAdjFactor = (100. - ((ScnAdjustment * PctPoorlyAsp) * GrowFactor)) / 100. # should be 0.9787
    
    # FIRST SORT OUT THE EXPOSURE OR ESTIMATED EXPOSURE
    
    # Choice 1. If EOH exists then use this
    if (ExtDict['EOH'][Counter] != 'Non'):
        # if its a screen or ship's screen then it needs an adjustment
	if ((ExtDict['EOH'][Counter] == 'S  ') | (ExtDict['EOH'][Counter] == 'SN ') | (ExtDict['EOH'][Counter] == 'VS ')):
	    # Fill in (append) the Estimated Exposure accordingly
	    ExtDict['ESTE'].append('UNA')
	    UncDict['ESTE'].append('UNA')
        # otherwise its either an aspirated instrument, a ventilated screen, a whirly one, a sling, a ship's sling or an unscreened one and so it doesn't need an adjustment
	else:
	    # Fill in (append) the Estimated Exposure accordingly
	    ExtDict['ESTE'].append('ASP')
	    UncDict['ESTE'].append('ASP')

    # Choice 2. If EOH doesn't exist but EOT exists then use this
    elif ((ExtDict['EOH'][Counter] == 'Non') & (ExtDict['EOT'][Counter] != 'Non')):
        # if its a screen or ship's screen then it needs an adjustment
	if ((ExtDict['EOT'][Counter] == 'S  ') | (ExtDict['EOT'][Counter] == 'SN ') | (ExtDict['EOT'][Counter] == 'VS ')):
	    # Fill in (append) the Estimated Exposure accordingly
	    ExtDict['ESTE'].append('UNA')
	    UncDict['ESTE'].append('UNA')
        # otherwise its either an aspirated instrument, a ventilated screen, a whirly one, a sling, a ship's sling or an unscreened one and so it doesn't need an adjustment
	else:
	    # Fill in (append) the Estimated Exposure accordingly
	    ExtDict['ESTE'].append('ASP')
	    UncDict['ESTE'].append('ASP')
	    
    # Choice 3a. If neither EOH or EOT exists then base it on the PT (buoys and platforms = ASP)
    elif (ExtDict['PT'][Counter] > 5):
        # if its a buoy or platform then it needs an adjustment
	# Fill in (append) the Estimated Exposure accordingly
	ExtDict['ESTE'].append('ASP')
	UncDict['ESTE'].append('ASP')
	
    # Choice 3b. If neither EOH or EOT exists then base it on the PT (ships have 55% adjustment applied = U55)	
    else:
	ExtDict['ESTE'].append('U55')
	UncDict['ESTE'].append('U55')
	
    # Now for ESTE = UNA or U55 apply 3.4% decrease to SHU and roll out to anomalies and other variables already solar adjusted

    # NO CHANGE TO AT so append VARscn with original, no need to add anything to VARtbc
    ExtDict['ATscn'].append(ExtDict['AT'][Counter])
    ExtDict['ATAscn'].append(ExtDict['ATA'][Counter])
    UncDict['ATuncSCN'].append(0.0)
    UncDict['ATAuncSCN'].append(0.0)
    
    # If the ob doesn't need adjustment then set the values and uncertainties
    # In these cases - no need to add anythign to VARtbc
    if (ExtDict['ESTE'][Counter] == 'ASP'):
        ExtDict['SHUscn'].append(ExtDict['SHU'][Counter])
        ExtDict['SHUAscn'].append(ExtDict['SHUA'][Counter])
        ExtDict['DPTscn'].append(ExtDict['DPT'][Counter])
        ExtDict['DPTAscn'].append(ExtDict['DPTA'][Counter])
        ExtDict['VAPscn'].append(ExtDict['VAP'][Counter])
        ExtDict['VAPAscn'].append(ExtDict['VAPA'][Counter])
        ExtDict['CRHscn'].append(ExtDict['CRH'][Counter])
        ExtDict['CRHAscn'].append(ExtDict['CRHA'][Counter])
        ExtDict['CWBscn'].append(ExtDict['CWB'][Counter])
        ExtDict['CWBAscn'].append(ExtDict['CWBA'][Counter])
        ExtDict['DPDscn'].append(ExtDict['DPD'][Counter])
        ExtDict['DPDAscn'].append(ExtDict['DPDA'][Counter])

        UncDict['DPTuncSCN'].append(0.0)
        UncDict['DPTAuncSCN'].append(0.0)
        UncDict['SHUuncSCN'].append(0.0)
        UncDict['SHUAuncSCN'].append(0.0)
        UncDict['VAPuncSCN'].append(0.0)
        UncDict['VAPAuncSCN'].append(0.0)
        UncDict['CRHuncSCN'].append(0.0)
        UncDict['CRHAuncSCN'].append(0.0)
        UncDict['CWBuncSCN'].append(0.0)
        UncDict['CWBAuncSCN'].append(0.0)
        UncDict['DPDuncSCN'].append(0.0)
        UncDict['DPDAuncSCN'].append(0.0)
    else:
    # APPLY!   
    # In these cases we need to apply to original value to fill in VARscn and also apply to VARtbc
    # NOTE: The uncSCN is the amount assessed for its part of tbc!!! So the final value that we will most likely use
    # I could save a second uncertainty for just the scn applied to the original data but its getting VERY BIG already 
    # NOTE: We need to establish the change in DPT first - Td can be calculated from vap
        t = ExtDict['ATtbc'][Counter]
        t_orig = ExtDict['AT'][Counter]
	if (ExtDict['ESTE'][Counter] == 'UNA'):
	    # Apply full adjustment 100 - 3.4 = 96.6
	    q_adj = ExtDict['SHUtbc'][Counter] * FullAdjFactor
	    q_adj_orig = ExtDict['SHU'][Counter] * FullAdjFactor
        else:
	    # For values up to 2015 where there are metadata - WILL NEED TO CHANGE IN FUTURE!!!
	    if (ExtDict['YR'][Counter] < EndofMetaData):
	        # Apply 55% of adjustment
	        # 3.4 * 0.55 = 1.87, 100 - 1.87 = 98.13
	        q_adj = ExtDict['SHUtbc'][Counter] * UnkAdjFactor
	        q_adj_orig = ExtDict['SHU'][Counter] * UnkAdjFactor
	    
	    # Catch any values from 2015 where there are no metadata - WILL NEED TO CHANGE IN FUTURE!!!
	    else:
	        # Apply 55% * growfactor of adjustment
	        # 3.4 * 0.55 * 1.14 = 2.1318, 100 - 2.1318 = 97.87
	        q_adj = ExtDict['SHUtbc'][Counter] * GrowUnkAdjFactor
	        q_adj_orig = ExtDict['SHU'][Counter] * GrowUnkAdjFactor
	
	ExtDict['SHUscn'].append(q_adj_orig)
        ExtDict['SHUAscn'].append(ExtDict['SHUA'][Counter] - (ExtDict['SHU'][Counter] - q_adj_orig))
        ExtDict['SHUAtbc'][Counter] = ExtDict['SHUAtbc'][Counter] - (ExtDict['SHUtbc'][Counter] - q_adj)
	ExtDict['SHUtbc'][Counter] = q_adj
	q_unc = 0.2 # apply same uncertainty in both cases
        UncDict['SHUuncSCN'].append(q_unc)
        UncDict['SHUAuncSCN'].append(q_unc)

        # Convert t and q adjustments to adjustments for other humidity variables   
        
	# Get vapour pressure from specific humidity
	e_adj = ch.vap_from_sh(q_adj,ClimP,roundit=False)
	e_adj_orig = ch.vap_from_sh(q_adj_orig,ClimP,roundit=False)
        ExtDict['VAPscn'].append(e_adj_orig) # hope this works
        ExtDict['VAPAscn'].append(ExtDict['VAPA'][Counter] - (ExtDict['VAP'][Counter] - e_adj_orig))
        ExtDict['VAPAtbc'][Counter] = ExtDict['VAPAtbc'][Counter] - (ExtDict['VAPtbc'][Counter] - e_adj)
	ExtDict['VAPtbc'][Counter] = e_adj
	e_unc = ch.vap_from_sh(q_adj+q_unc,ClimP,roundit=False) - e_adj
        UncDict['VAPuncSCN'].append(e_unc)
        UncDict['VAPAuncSCN'].append(e_unc)
	
        # Get dew point temperature from vapour pressure (use at too to check for wet bulb <=0)
        dpt_adj = ch.td_from_vap(e_adj,ClimP,t,roundit=False)
        dpt_adj_orig = ch.td_from_vap(e_adj_orig,ClimP,t_orig,roundit=False)
        ExtDict['DPTscn'].append(dpt_adj_orig) # hope this works
        ExtDict['DPTAscn'].append(ExtDict['DPTA'][Counter] - (ExtDict['DPT'][Counter] - dpt_adj_orig))
        ExtDict['DPTAtbc'][Counter] = ExtDict['DPTAtbc'][Counter] - (ExtDict['DPTtbc'][Counter] - dpt_adj)
	ExtDict['DPTtbc'][Counter] = dpt_adj
	dpt_unc = ch.td_from_vap(e_adj+e_unc,ClimP,t,roundit=False) - dpt_adj
        UncDict['DPTuncSCN'].append(dpt_unc)
        UncDict['DPTAuncSCN'].append(dpt_unc)
        
	# Get wet bulb temperature from vapour pressure and dew point temperature and air temperature
        cwb_adj = ch.wb(dpt_adj,t,ClimP,roundit=False)
        cwb_adj_orig = ch.wb(dpt_adj_orig,t_orig,ClimP,roundit=False)
        ExtDict['CWBscn'].append(cwb_adj_orig)
        ExtDict['CWBAscn'].append(ExtDict['CWBA'][Counter] - (ExtDict['CWB'][Counter] - cwb_adj_orig))
        ExtDict['CWBAtbc'][Counter] = ExtDict['CWBAtbc'][Counter] - (ExtDict['CWBtbc'][Counter] - cwb_adj)
	ExtDict['CWBtbc'][Counter] = cwb_adj
        cwb_unc = ch.wb(dpt_adj+dpt_unc,t,ClimP,roundit=False) - cwb_adj
        UncDict['CWBuncSCN'].append(cwb_unc)
        UncDict['CWBAuncSCN'].append(cwb_unc)

	# Get relative humidity from dew point temperature and temperature
        crh_adj = ch.rh(dpt_adj,t,ClimP,roundit=False)
        crh_adj_orig = ch.rh(dpt_adj_orig,t_orig,ClimP,roundit=False)
        ExtDict['CRHscn'].append(crh_adj_orig)
        ExtDict['CRHAscn'].append(ExtDict['CRHA'][Counter] - (ExtDict['CRH'][Counter] - crh_adj_orig))
        ExtDict['CRHAtbc'][Counter] = ExtDict['CRHAtbc'][Counter] - (ExtDict['CRHtbc'][Counter] - crh_adj)
	ExtDict['CRHtbc'][Counter] = crh_adj
        crh_unc = ch.rh(dpt_adj+dpt_unc,t,ClimP,roundit=False) - crh_adj
        UncDict['CRHuncSCN'].append(crh_unc)
        UncDict['CRHAuncSCN'].append(crh_unc)
        
	# Get dew point depression from temperautre and dew point depression (THIS ONE GOES OPPOSITE DIRECTION TO OTHERS!)
        dpd_adj = ch.dpd(dpt_adj,t,roundit=False)   
        dpd_adj_orig = ch.dpd(dpt_adj_orig,t_orig,roundit=False)   
        ExtDict['DPDscn'].append(dpd_adj_orig)
        ExtDict['DPDAscn'].append(ExtDict['DPDA'][Counter] - (ExtDict['DPD'][Counter] - dpd_adj_orig)) # - -ve = + so should still work
        ExtDict['DPDAtbc'][Counter] = ExtDict['DPDAtbc'][Counter] - (ExtDict['DPDtbc'][Counter] - dpd_adj)
	ExtDict['DPDtbc'][Counter] = dpd_adj
        dpd_unc = ch.dpd(dpt_adj-dpt_unc,t,roundit=False) - dpd_adj # SHOULD MAKE THIS POSITIVE!!
        UncDict['DPDuncSCN'].append(dpd_unc)
        UncDict['DPDAuncSCN'].append(dpd_unc)
	
        # Now cross-check t and dpt_adj [and crh_adj and dpd_adj] - no supersaturation allowed!
        if ((t - dpt_adj) < 0.):
	    # force 100% rh limit by adjusting t to dpt_adj, preserving humidity??? - give it dpt_unc
	    # Sort out anomaly first before changing the actual
            ExtDict['ATAtbc'][Counter] = ExtDict['ATAtbc'][Counter] - (ExtDict['ATtbc'][Counter] - ExtDict['DPTtbc'][Counter])
            ExtDict['ATtbc'][Counter] = ExtDict['DPTtbc'][Counter] # DON't THINK THIS IS A COPY ISSUE - TESTED AND IT ONLY SEEMS TO AFFECT WHOLE ARRAYS!
	    UncDict['ATuncSCN'][Counter] = dpt_unc
            UncDict['ATAuncSCN'][Counter] = dpt_unc
	    # recalculate affected variables = which will all be at saturation: cwb = at, rh = 100, dpd = 0
	    # leave uncertainties as they are
            cwb_adj = ExtDict['ATtbc'][Counter]
            ExtDict['CWBAtbc'][Counter] = ExtDict['CWBAtbc'][Counter] - (ExtDict['CWBtbc'][Counter] - cwb_adj)
            ExtDict['CWBtbc'][Counter] = ExtDict['ATtbc'][Counter]
            crh_adj = 100.0
            ExtDict['CRHAtbc'][Counter] = ExtDict['CRHAtbc'][Counter] - (ExtDict['CRHtbc'][Counter] - crh_adj)
            ExtDict['CRHtbc'][Counter] = crh_adj
            dpd_adj = 0.0
            ExtDict['DPDAtbc'][Counter] = ExtDict['DPDAtbc'][Counter] - (ExtDict['DPDtbc'][Counter] - dpd_adj)
            ExtDict['DPDtbc'][Counter] = dpd_adj

        # Now cross-check t_orig and dpt_adj_orig [and crh_adj_orig and dpd_adj_orig] - no supersaturation allowed!
        if ((t_orig - dpt_adj_orig) < 0.):
	    # force 100% rh limit by adjusting t to dpt_adj, preserving humidity??? - give it dpt_unc
	    # Sort out anomaly first before changing the actual
            ExtDict['ATAscn'][Counter] = ExtDict['ATA'][Counter] - (ExtDict['AT'][Counter] - ExtDict['DPTscn'][Counter])
            ExtDict['ATscn'][Counter] = ExtDict['DPTscn'][Counter]
	    # recalculate affected variables = which will all be at saturation: cwb = at, rh = 100, dpd = 0
	    # leave uncertainties as they are
            cwb_adj = ExtDict['ATscn'][Counter]
            ExtDict['CWBAscn'][Counter] = ExtDict['CWBA'][Counter] - (ExtDict['CWB'][Counter] - cwb_adj)
            ExtDict['CWBscn'][Counter] = cwb_adj
            crh_adj = 100.0
            ExtDict['CRHAscn'][Counter] = ExtDict['CRHA'][Counter] - (ExtDict['CRH'][Counter] - crh_adj)
            ExtDict['CRHscn'][Counter] = crh_adj
            dpd_adj = 0.0
            ExtDict['DPDAscn'][Counter] = ExtDict['DPDA'][Counter] - (ExtDict['DPD'][Counter] - dpd_adj)
            ExtDict['DPDscn'][Counter] = dpd_adj

    return ExtDict, UncDict

#************************************************************************************************************
# EstimateHeight
#************************************************************************************************************
def EstimateHeight(ExtDict,Counter):

    '''
    This function is called from ApplyHeightAdjUnc.
    It works out a height of hygrometer and returns it along with an uncertainty switch depending on the source of the height
    INPUTS:
    ExtDict = dictionary of all obs and metadata and adjustments to date
    Counter = pointer to the ob of interest
    OUTPUTS:
    EstHeightH = estimated height of hygrometer
    EstHeightA = estimated height of anemometer (or provided)
    EstUnc = allocated uncertainty amount
    
    If PT = ship (0,1,2,3,4,5) - only really 5 that we have both HOB/HOT and HOA/HOP info
    1) ESTH = HOT: height of thermomenter in m (preferred) UNLESS IT IS SILLY (e.g., < 2m) - unc = 0.1*adj
    2) ESTH = HOB: height of barometer in m (second choice) UNLESS IT IS SILLY (e.g., < 2m) - unc = 0.1*adj
    3) ESTH = HOP: height of visual obs platform in m (third choice) UNLESS IT IS SILLY (e.g., < 2m) - unc = 0.1*adj   
       THERE ARE SOME IN JAN 1973 at 1m (~106200-106220)
    4) ESTH = HOA-10: height of anemometer in m converted UNLESS IT IS SILLY (e.g., < 2m) - unc = 0.85*adj
    5) ESTH = 17-22m so 17. + (nmonths*0.0149m) from Jan 1973 to Dec 2000 - based on HOB reaching and mostly staying above 22m - HOP missing 
       Maxes out at 22m / January 2001!!!
       Kent et al., 2007, Berry and Kent, 2011 say 16 to 24m but that most likely covers from 1971-2007 so 17 is consistent
    IF PT = buoy (6,8) no height info so assume 4m HOP and 5m HOA - unc = 0.85*adj
    ESTH = 4 (NBDC gives height as 4 for most listed) http://www.ndbc.noaa.gov/bht.shtml
    IF PT = platform (9,10,15) (no height info so do not apply adjustment - ESTH = 999 - unc = (T-SST)/2., (q-q0)/2
    
    IF adjustment cannot be calculated - unc = (T-SST)/2., (q-q0)/2
    IF adjustment cannot be calculated and SST is not present/failed QC - 
    unc = 0.1 for AT (10m at DALR), q*0.007 (7% per 1 deg so 0.7 per 0.1 deg)    
    
    '''

    # Prescribed heights (of thermomenters and anemometers) for buoys and platforms
    PBuoy = 4.
    PBuoyHOA = 5.
    PPlatform = 999.	# was 20 but now do not apply
    PPlatformHOA = 999. # was 30 but now do not apply
        
    # Increments for estimating height by YR and MN 
    StHeight = 17. # was 16
    EdHeight = 22. # was 24
    StYr = 1973 # assume January
    EdYr = 2001 # assume December 2000 (was Dec 2006 so 2007)
    MnInc = (EdHeight / StHeight) / (((EdYr) - StYr) * 12.) # should be 0.0149 - was ~0.02
        
    # proportion of adjustment to apply as uncertainty depending on estimate type:
    calc_height = 1 # default is VERY UNCERTAIN!
    actual_height = 0.1 # actual height
    estimated_height =  0.85 # estimated height (ship) or prescribed height (buoy) was 0.5
    no_adjustment = 999 # either its a platform or an adjustment can't be applied

    # ENSURE THAT ESTH IS A FLOAT
    # First check if its a buoy or platform
    if (ExtDict['PT'][Counter] > 5):
        # If its a buoy apply height of 4m http://www.ndbc.noaa.gov/bht.shtml
	if ((ExtDict['PT'][Counter] == 6) | (ExtDict['PT'][Counter] == 8)):
            # Fill in (append) the Estimated Height accordingly
	    EstHeightH = float(PBuoy)
	    EstHeightA = float(PBuoyHOA) # http://www.ndbc.noaa.gov/bht.shtml
	    EstUnc = estimated_height
    # Now check if its a platform (will be removed next time around)
	else:
            # Fill in (append) the Estimated Height accordingly
	    EstHeightH = float(PPlatform)
	    EstHeightA = float(PPlatformHOA)
	    EstUnc = no_adjustment
    # Or its a ship then get a height
    else:
        # Choice 1. If HOB or HOT exists then use this - UNLESS THEY ARE SILLY (< 2m)
        if (ExtDict['HOT'][Counter] > 2.):
            # Fill in (append) the Estimated Height accordingly
	    EstHeightH = float(ExtDict['HOT'][Counter])
	    EstUnc = actual_height
        # Choice 2. If HOB or HOT exists then use this - UNLESS THEY ARE SILLY (< 2m)
        elif (ExtDict['HOB'][Counter] > 2.):
            # Fill in (append) the Estimated Height accordingly
	    EstHeightH = float(ExtDict['HOB'][Counter])
	    EstUnc = actual_height
        # Choice 3. If HOP exists then use this - UNLESS THEY ARE SILLY (< 2m)
        elif (ExtDict['HOP'][Counter] > 2.):
            # Fill in (append) the Estimated Height accordingly
	    EstHeightH = float(ExtDict['HOP'][Counter])
	    EstUnc = actual_height
        # Choice 4. If HOA is available then estimate - UNLESS THEY ARE SILLY (< 12m) 12 because 12-10 = 2!
        elif (ExtDict['HOA'][Counter] > 12.):
            EstHeightH = float(ExtDict['HOA'][Counter] - 10.)
	    EstUnc = estimated_height
        # Choice 5. Prescribe a height based on YR and MN (there should only be ships left by now
        else:
            # if YR >= 2001 (EdYr) then apply fixed height EdHeight
	    if (ExtDict['YR'][Counter] >= EdYr):
	        # Fill in (append) the Estimated Height accordingly
	        EstHeightH = float(EdHeight)
	        EstUnc = calc_height
            # if YR < 1973 then apply fixed height StHeight
	    elif (ExtDict['YR'][Counter] < StYr): # There aren't any years before this but maybe in the future?    
	        # Fill in (append) the Estimated Height accordingly
	        EstHeightH = float(StHeight)
	        EstUnc = calc_height
	    # Work out StHeight+MnInc depending on YR and MN
	    else:
	        NMonths = ((ExtDict['YR'][Counter] - StYr) * 12) + ExtDict['MO'][Counter]
	        # Fill in (append) the Estimated Height accordingly
	        EstHeightH = float(StHeight + (NMonths * MnInc))
	        EstUnc = calc_height

        # Check if HOA exists and is greater than 2m, if it does not then HOA = ESTH+10
        if (ExtDict['HOA'][Counter] > 2.):
            EstHeightA = float(ExtDict['HOA'][Counter])
	# IF HOA does not exist or is <= than 2.
	else:    
	    EstHeightA = float(EstHeightH + 10.)

    # Test output
#    print('Platform: ',ExtDict['PT'][Counter])
#    print('HOB/HOT/HOP/HOA: ',ExtDict['HOB'][Counter],ExtDict['HOT'][Counter],ExtDict['HOP'][Counter],ExtDict['HOA'][Counter])
#    print('ESTH/HOA/UNC: ',EstHeightH, EstHeightA, EstUnc)
#    pdb.set_trace()

    return EstHeightH,EstHeightA,EstUnc
#************************************************************************************************************
# GetNOCSHeight
#************************************************************************************************************
def GetNOCSHeight(ExtDict,Counter):
    '''
    This function is called from ApplyHeightAdjUnc.
    It matches the UID of the ob and pulls the prescribed height from NOCS

    INPUTS:
    ExtDict = dictionary of all obs and metadata and adjustments to date
    Counter = pointer to the ob of interest
    OUTPUTS:
    EstHeightH = estimated height of hygrometer
    EstHeightA = estimated height of anemometer (or provided)
    EstUnc = allocated uncertainty amount

    I don't think NOCS includes buoys or platforms so we only do this for ships
    Buoys are treated as in EstimateHeight - ESTH = 4, HOA = 5, unc = 0.85*adj
    Platforms are treated as in EstimateHeight - ESTH = 999, no adj applied, unc = (T-SST)/2., (q-q0)/2
    Uncertainty is associated as follows:
    
    If PT = ship (0,1,2,3,4,5) - only really 5 that we have both HOB/HOT and HOA/HOP info
    1) ESTH = HOT: height of thermomenter in m (preferred) UNLESS IT IS SILLY (e.g., < 2m) - unc = 0.1*adj
    2) ESTH = HOB: height of barometer in m (second choice) UNLESS IT IS SILLY (e.g., < 2m) - unc = 0.1*adj
    3) ESTH = HOP: height of visual obs platform in m (third choice) UNLESS IT IS SILLY (e.g., < 2m) - unc = 0.1*adj   
       THERE ARE SOME IN JAN 1973 at 1m (~106200-106220)
    4) ESTH = HOA-10: height of anemometer in m converted UNLESS IT IS SILLY (e.g., < 2m) - unc = 0.85*adj
    5) ESTH = 17-22m so 17. + (nmonths*0.0149m) from Jan 1973 to Dec 2000 - based on HOB reaching and mostly staying above 22m - HOP missing 
       Maxes out at 22m / January 2001!!!
       Kent et al., 2007, Berry and Kent, 2011 say 16 to 24m but that most likely covers from 1971-2007 so 17 is consistent
    IF PT = buoy (6,8) no height info so assume 4m HOP and 5m HOA - unc = 0.85*adj
    ESTH = 4 (NBDC gives height as 4 for most listed) http://www.ndbc.noaa.gov/bht.shtml
    IF PT = platform (9,10,15) (no height info so do not apply adjustment - ESTH = 999 - unc = (T-SST)/2., (q-q0)/2
    
    IF adjustment cannot be calculated - unc = (T-SST)/2., (q-q0)/2
    IF adjustment cannot be calculated and SST is not present/failed QC - 
    unc = 0.1 for AT (10m at DALR), q*0.007 (7% per 1 deg so 0.7 per 0.1 deg)
    
    
    '''
    MonArr = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']

    # Prescribed heights (of thermomenters and anemometers) for buoys and platforms
    PBuoy = 4.
    PBuoyHOA = 5.
    PPlatform = 999.	# was 20 but now do not apply
    PPlatformHOA = 999. # was 30 but now do not apply
                
    # proportion of adjustment to apply as uncertainty depending on estimate type:
    calc_height = 1 # default is VERY UNCERTAIN!
    actual_height = 0.1 # actual height
    estimated_height =  0.85 # estimated height (ship) or prescribed height (buoy) was 0.5
    no_adjustment = 999 # either its a platform or an adjustment can't be applied

    # ENSURE THAT ESTH IS A FLOAT
    # First check if its a buoy or platform
    if (ExtDict['PT'][Counter] > 5):
        # If its a buoy apply height of 4m http://www.ndbc.noaa.gov/bht.shtml
	if ((ExtDict['PT'][Counter] == 6) | (ExtDict['PT'][Counter] == 8)):
            # Fill in (append) the Estimated Height accordingly
	    EstHeightH = float(PBuoy)
	    EstHeightA = float(PBuoyHOA) # http://www.ndbc.noaa.gov/bht.shtml
	    EstUnc = estimated_height
    # Now check if its a platform (will be removed next time around)
	else:
            # Fill in (append) the Estimated Height accordingly
	    EstHeightH = float(PPlatform)
	    EstHeightA = float(PPlatformHOA)
	    EstUnc = no_adjustment
    # Or its a ship then get a height from NOCS
    else:
        # Look up the NOCS file for this YR and MN
	EstHeightH = float(ExtDict['HOT'][Counter])
	EstUnc = actual_height
	EstUnc = estimated_height
	EstUnc = calc_height

        # Check if HOA exists and is greater than 2m, if it does not then HOA = ESTH+10
        if (ExtDict['HOA'][Counter] > 2.):
            EstHeightA = float(ExtDict['HOA'][Counter])
	# IF HOA does not exist or is <= than 2.
	else:    
	    EstHeightA = float(EstHeightH + 10.)

    # Test output
#    print('Platform: ',ExtDict['PT'][Counter])
#    print('HOB/HOT/HOP/HOA: ',ExtDict['HOB'][Counter],ExtDict['HOT'][Counter],ExtDict['HOP'][Counter],ExtDict['HOA'][Counter])
#    print('ESTH/HOA/UNC: ',EstHeightH, EstHeightA, EstUnc)
#    pdb.set_trace()

    return EstHeightH,EstHeightA,EstUnc
#************************************************************************************************************
# ApplyHeightAdjUnc
#************************************************************************************************************
def ApplyHeightAdjUnc(ExtDict,UncDict,Counter,ClimP,ChooseLocal):

    '''
    ExtDict = dictionary of orig AND adjusted values
    UncDict = dicitonary of uncertainty values
    Counter = loop number for finding right original ob   
    ClimP = climatological pentad mean SLP from nearest 1x1 gridbox to ob for humidity calculation 
    
    This function calls for either an estimated height from EstimateHeight or a NOCS provided Height from GetNOCSHeight
    
    For EstimateHeight:
    If PT = ship (0,1,2,3,4,5) - only really 5 that we have both HOB/HOT and HOA/HOP info
    1) ESTH = HOT: height of thermomenter in m (preferred) UNLESS IT IS SILLY (e.g., < 2m) - unc = 0.1*adj
    2) ESTH = HOB: height of barometer in m (second choice) UNLESS IT IS SILLY (e.g., < 2m) - unc = 0.1*adj
    3) ESTH = HOP: height of visual obs platform in m (third choice) UNLESS IT IS SILLY (e.g., < 2m) - unc = 0.1*adj   
       THERE ARE SOME IN JAN 1973 at 1m (~106200-106220)
    4) ESTH = HOA-10: height of anemometer in m converted UNLESS IT IS SILLY (e.g., < 2m) - unc = 0.85*adj
    5) ESTH = 17-22m so 17. + (nmonths*0.0149m) from Jan 1973 to Dec 2000 - based on HOB reaching and mostly staying above 22m - HOP missing 
       Maxes out at 22m / January 2001!!!
       Kent et al., 2007, Berry and Kent, 2011 say 16 to 24m but that most likely covers from 1971-2007 so 17 is consistent
    IF PT = buoy (6,8) no height info so assume 4m HOP and 5m HOA - unc = 0.85*adj
    ESTH = 4 (NBDC gives height as 4 for most listed) http://www.ndbc.noaa.gov/bht.shtml
    IF PT = platform (9,10,15) (no height info so do not apply adjustment - ESTH = 999 - unc = (T-SST)/2., (q-q0)/2
    
    For GetNOCSHeight:
    Matches up the UIDs and uses the NOCS prescribed heights from
    1) METADATA ? - unc = 
    2) Linear height estimate 17-24m? - unc = 
    
    
    IF adjustment cannot be calculated - unc = (T-SST)/2., (q-q0)/2
    IF adjustment cannot be calculated and SST is not present/failed QC - 
    unc = 0.1 for AT (10m at DALR), q*0.007 (7% per 1 deg so 0.7 per 0.1 deg)
    
    IF SST is missing or invalid and we have to use AT or forced limits (-2.0, 40) to height adjust
    then unc = adjustment or 0.1 deg, 0.007*q WHICHEVER IS LARGEST!!!
    
    HeightCorrect.py 
    Use height info, 
        SST (or AT if missing or failed buddy/clim/freeze), 
	ClimP (not observed SLP), 
	u (or 0.5m if < 0.5, 6 (moderate) if missing or > 100m/s)
    to create an estimated height adjusted value. Do this to orig and solar/screen corrected obs.
    
    Other humidity variables are converted too - with a check for supersaturation and T adjusted to == DPT if there is an issues
    
    Derive uncertainties (1 sigma!):
     - imperfect calculations? difficult to quantify
     - imperfect height estimation? lengthy to redo height ajdustment for different scenarios?
     - one way to say that this is VERY uncertain would be to use the magnitude of the adjustment compared to the original value
     - For obs with actual HOT or HOB or HOP - use 10% of adjustment (unc in calculation)
     - For obs with estimated from HOA or buoys - use 75% of adjustment + 10% 
     - For obs with estimated from linear function - use 90% of adjustment + 10% 
     - For platforms or non-calculable adjustments - use (T-SST)/2., (q-q0)/2
     - LETS DO THIS FOR NOW
     - LATER COULD BASE IT ON RMSE OR 2Sd OF LINEAR EQ FIT?
          
     Looks like HOB and HOT and HOP are not identical - but there is really not much in it.
     HOB mean = 22.48, sd = 9.13, HOT mean = 22.21, sd = 5.58. Differences and equations relating to HOA and HOP are different.
     See HeightMetaDataStats_ships_OBSclim2NBC_I300_OCT2016.txt
    '''
    
#    # Prescribed heights (of thermomenters and anemometers) for buoys and platforms
#    PBuoy = 4.
#    PBuoyHOA = 5.
#    PPlatform = 999.	# was 20 but now do not apply
#    PPlatformHOA = 999. # was 30 but now do not apply
#        
#    # Increments for estimating height by YR and MN 
#    StHeight = 17. # was 16
#    EdHeight = 22. # was 24
#    StYr = 1973 # assume January
#    EdYr = 2001 # assume December 2000 (was Dec 2006 so 2007)
#    MnInc = (EdHeight / StHeight) / (((EdYr) - StYr) * 12.) # should be 0.0149 - was ~0.02
#    
#    # FIRST SORT OUT THE HEIGHT (m) OR ESTIMATED HEIGHT
# #   # We also need to estimate HOA if it doesn't exist
# #   HOA = ExtDict['HOA'][Counter] # This could well be zero at this point
#    
#    # proportion of adjustment to apply as uncertainty depending on estimate type:
#    unc_estimate = 1 # default is VERY UNCERTAIN!
#    actual_height = 0.1 # actual height
#    estimated_height =  0.85 # estimated height (ship) or prescribed height (buoy) was 0.5
#    no_adjustment = 999 # either its a platform or an adjustment can't be applied

    # Catch to ensure larger unceratinty when there is no valid SST
    noSST_estimate = False # no valid SST so AT or forced limits (-2.0, 40) used
    # If no valid SST then SST = AT so no adjustment applied to AT and v uncertain to q etc
    # Extra variable to apply large uncertainties when no adjustment can be made
    no_adjustment = 999 # either its a platform or an adjustment can't be applied

#    # ENSURE THAT ESTH IS A FLOAT
#    # First check if its a buoy or platform
#    if (ExtDict['PT'][Counter] > 5):
#        # If its a buoy apply height of 4m http://www.ndbc.noaa.gov/bht.shtml
#	if ((ExtDict['PT'][Counter] == 6) | (ExtDict['PT'][Counter] == 8)):
#            # Fill in (append) the Estimated Height accordingly
#	    ExtDict['ESTH'].append(float(PBuoy))
#	    UncDict['ESTH'].append(float(PBuoy))
#	    HOA = float(PBuoyHOA) # http://www.ndbc.noaa.gov/bht.shtml
#	    unc_estimate = estimated_height
#    # Now check if its a platform (will be removed next time around)
#	else:
#            # Fill in (append) the Estimated Height accordingly
#	    ExtDict['ESTH'].append(float(PPlatform))
#	    UncDict['ESTH'].append(float(PPlatform))
#	    HOA = float(PPlatformHOA)
#	    unc_estimate = no_adjustment
#    # Or its a ship then get a height
#    else:
#        # Choice 1. If HOB or HOT exists then use this - UNLESS THEY ARE SILLY (< 2m)
#        if (ExtDict['HOT'][Counter] > 2.):
#            # Fill in (append) the Estimated Height accordingly
#	    ExtDict['ESTH'].append(float(ExtDict['HOT'][Counter]))
#	    UncDict['ESTH'].append(float(ExtDict['HOT'][Counter]))
#	    unc_estimate = actual_height
#        # Choice 2. If HOB or HOT exists then use this - UNLESS THEY ARE SILLY (< 2m)
#        elif (ExtDict['HOB'][Counter] > 2.):
#            # Fill in (append) the Estimated Height accordingly
#	    ExtDict['ESTH'].append(float(ExtDict['HOB'][Counter]))
#	    UncDict['ESTH'].append(float(ExtDict['HOB'][Counter]))
#	    unc_estimate = actual_height
#        # Choice 3. If HOP exists then use this - UNLESS THEY ARE SILLY (< 2m)
#        elif (ExtDict['HOP'][Counter] > 2.):
#            # Fill in (append) the Estimated Height accordingly
#	    ExtDict['ESTH'].append(float(ExtDict['HOP'][Counter]))
#	    UncDict['ESTH'].append(float(ExtDict['HOP'][Counter]))
#	    unc_estimate = actual_height
#        # Choice 4. If HOA is available then estimate - UNLESS THEY ARE SILLY (< 12m) 12 because 12-10 = 2!
#        elif (ExtDict['HOA'][Counter] > 12.):
#            ExtDict['ESTH'].append(float(ExtDict['HOA'][Counter] - 10.))
#	    UncDict['ESTH'].append(float(ExtDict['HOA'][Counter] - 10.))
#	    unc_estimate = estimated_height
#        # Choice 5. Prescribe a height based on YR and MN (there should only be ships left by now
#        else:
#            # if YR >= 2001 (EdYr) then apply fixed height EdHeight
#	    if (ExtDict['YR'][Counter] >= EdYr):
#	        # Fill in (append) the Estimated Height accordingly
#	        ExtDict['ESTH'].append(float(EdHeight))
#	        UncDict['ESTH'].append(float(EdHeight))
#	        #unc_estimate = unc_estimate
#            # if YR < 1973 then apply fixed height StHeight
#	    elif (ExtDict['YR'][Counter] < StYr): # There aren't any years before this but maybe in the future?    
#	        # Fill in (append) the Estimated Height accordingly
#	        ExtDict['ESTH'].append(float(StHeight))
#	        UncDict['ESTH'].append(float(StHeight))
#	        #unc_estimate = unc_estimate
#	    # Work out StHeight+MnInc depending on YR and MN
#	    else:
#	        NMonths = ((ExtDict['YR'][Counter] - StYr) * 12) + ExtDict['MO'][Counter]
#	        # Fill in (append) the Estimated Height accordingly
#	        ExtDict['ESTH'].append(float(StHeight + (NMonths * MnInc)))
#	        UncDict['ESTH'].append(float(StHeight + (NMonths * MnInc)))
#	        #unc_estimate = unc_estimate
#
#        # Check if HOA exists and is greater than 2m, if it does not then HOA = ESTH+10
#        if (ExtDict['HOA'][Counter] > 2.):
#            HOA = float(ExtDict['HOA'][Counter])
#	# IF HOA does not exist or is <= than 2.
#	else:    
#	    HOA = float(ExtDict['ESTH'][Counter] + 10.)
#
#    # Test output
#    print('Platform: ',ExtDict['PT'][Counter])
#    print('HOB/HOT/HOP/HOA: ',ExtDict['HOB'][Counter],ExtDict['HOT'][Counter],ExtDict['HOP'][Counter],ExtDict['HOA'][Counter])
#    print('ESTH/HOA: ',ExtDict['ESTH'][Counter], HOA)
##    pdb.set_trace()
 
    # If ChooseHeight == 'local' then call EstimateHeight
    if (ChooseLocal == 'local'):
        EstHeightH,EstHeightA,EstUnc = EstimateHeight(ExtDict,Counter)
	ExtDict['ESTH'].append(EstHeightH)
	UncDict['ESTH'].append(EstHeightH)
	HOA = EstHeightA
	unc_estimate = EstUnc
    
    # Else if ChooseLocal == 'localNOCS' then call GetNOCSHeight
    elif (ChooseLocal == 'localNOCS'):
        EstHeightH,EstHeightA,EstUnc = GetNOCSHeight(ExtDict,Counter)
	ExtDict['ESTH'].append(EstHeightH)
	UncDict['ESTH'].append(EstHeightH)
	HOA = EstHeightA
	unc_estimate = EstUnc    
    
    # Else something is amiss
    else:
        print('No ChooseLocal/LocalType info!')
	pdb.set_trace()
       
    # NOW obtain the height correction for AT and SHU (USING SST, U, ClimP and ESTH) and also for the other variables
    # Do not need to pull through the HeightDict so use _
 
    # Order of vars: sst,at,shu,u,zu,zt,zq,dpt=(-99.9),vap=(-99.9),crh=(-99.9),cwb=(-99.9),dpd=(-99.9),climp=(-99.9)
    # The derived adjustments for other variables also include a check for supersaturation and an adjustment to AT=DPT if that happens

    # Only apply if not dealing with platforms! (will be removed next time around) OR ESTH is already 10m!!!
    if ((ExtDict['ESTH'][Counter] < 999) & (ExtDict['ESTH'][Counter] != 10)):
    
        # First test for a valid SST (not missing or failing clim/freeze QC)
	# Note the < -2.0 will catch both missing values -32768 and freezing flags
	# If it is missing or invalid then use AT
	# However, AT could be way below valid SSTs (-2.0 to 40 deg C?)
	# So force these upper and lower limits
	# Regardless - change unc to no_adjustment which means a large uncertainty will be applied
	if ((ExtDict['SST'][Counter] < -2.0) | (ExtDict['SST'][Counter] > 40.) | \
	     (ExtDict['SSTclim'][Counter] > 0)): # 1 = fail, 8 = not applied 
	    MySSTtbc = ExtDict['ATtbc'][Counter]
	    MySSTorig = ExtDict['AT'][Counter]
	    
	    # Now double check this is still valid
	    if (MySSTtbc < -2.0):
	        MySSTtbc = -2.0
	    elif (MySSTtbc > 40.):
	        MySSTtbc = 40.

	    # Now double check this is still valid
	    if (MySSTorig < -2.0):
	        MySSTorig = -2.0
	    elif (MySSTorig > 40.):
	        MySSTorig = 40.
		
	    # Either way force the uncertainty to be large
	    noSST_estimate = True
	
	# If its ok then pass to MySST
	else:
	    MySSTtbc = ExtDict['SST'][Counter]	
	    MySSTorig = ExtDict['SST'][Counter]	
	
        # We're most interested in the combined bias corrections but we're assessing combined and HGT only seperately
	# This means that we could potentially have an adjustment value for one but it may fail for the other
	# We should do the combined one first and it if fails, not try to do the HGT only, if HGT only fails then ok

        # Do this for the VARtbc values
#        print("TBC: ",HOA, ExtDict['ESTH'][Counter])
#        print(ExtDict['SST'][Counter],ExtDict['ATtbc'][Counter],ExtDict['SHUtbc'][Counter],ExtDict['W'][Counter],HOA,ExtDict['ESTH'][Counter],ExtDict['ESTH'][Counter],
#              ExtDict['DPTtbc'][Counter],ExtDict['VAPtbc'][Counter],ExtDict['CRHtbc'][Counter],ExtDict['CWBtbc'][Counter],ExtDict['DPDtbc'][Counter],ClimP)
        AdjDict,_ = hc.run_heightcorrection_final(MySSTtbc,
                                                  ExtDict['ATtbc'][Counter],
					          ExtDict['SHUtbc'][Counter],
					          ExtDict['W'][Counter],
					          HOA,
					          ExtDict['ESTH'][Counter],
					          ExtDict['ESTH'][Counter],
					          dpt=ExtDict['DPTtbc'][Counter],
					          vap=ExtDict['VAPtbc'][Counter],
					          crh=ExtDict['CRHtbc'][Counter],
					          cwb=ExtDict['CWBtbc'][Counter],
					          dpd=ExtDict['DPDtbc'][Counter],
					          climp=ClimP)

        # Double check to make sure some sensible values have come out - in some cases there is non-convergence where height cannot be adjusted.
        # In these cases - apply no height correction. Uncertainty should be large so is set to no_adjustment to be estimated later.
        # In other cases where SHU is VERY small to begin with (most likely screwy!) e.g. Jan 1973 ob 145622 shu = 0.1 this leads to -ve adjusted values
        # and NaNs. I have added a catch for this in HeightCorrect.py so it now returns -99,9 in those cases.
        # In other cases where AT is >>40 but SST ~8 (e.g. April 1974 ob 118659) we have at_10m>100! We can't have that!
	# There is a check that at_10m > -80 and < 65.
	# NOTE all uncertainties are set based on tbc as these are then used to create total uncertainty
        if (AdjDict['at_10m'] > -99.):					      
            # Now copy the new adjustments to VARtbc, apply to the anomalies, and obtain the uncertainty estimate on the adjustment applied
            # Anomalies need to be sorted out first
#            print('SENSIBLE TBC VALUES: ',AdjDict)
    
            ATdiff = ExtDict['ATtbc'][Counter] - AdjDict['at_10m']
	    ExtDict['ATAtbc'][Counter] = ExtDict['ATAtbc'][Counter] - ATdiff
            UncDict['ATuncHGT'].append(abs(ATdiff) * unc_estimate)
            UncDict['ATAuncHGT'].append(UncDict['ATuncHGT'][Counter])
            ExtDict['ATtbc'][Counter] = AdjDict['at_10m']
	    DPTdiff = ExtDict['DPTtbc'][Counter] - AdjDict['dpt_10m']
            ExtDict['DPTAtbc'][Counter] = ExtDict['DPTAtbc'][Counter] - DPTdiff
            UncDict['DPTuncHGT'].append(abs(DPTdiff) * unc_estimate)
            UncDict['DPTAuncHGT'].append(UncDict['DPTuncHGT'][Counter])
            ExtDict['DPTtbc'][Counter] = AdjDict['dpt_10m']
	    SHUdiff = ExtDict['SHUtbc'][Counter] - AdjDict['shu_10m']
            ExtDict['SHUAtbc'][Counter] = ExtDict['SHUAtbc'][Counter] - SHUdiff
            UncDict['SHUuncHGT'].append(abs(SHUdiff) * unc_estimate)
            UncDict['SHUAuncHGT'].append(UncDict['SHUuncHGT'][Counter])
            ExtDict['SHUtbc'][Counter] = AdjDict['shu_10m']
	    VAPdiff = ExtDict['VAPtbc'][Counter] - AdjDict['vap_10m']
            ExtDict['VAPAtbc'][Counter] = ExtDict['VAPAtbc'][Counter] - VAPdiff
            UncDict['VAPuncHGT'].append(abs(VAPdiff) * unc_estimate)
            UncDict['VAPAuncHGT'].append(UncDict['VAPuncHGT'][Counter])
            ExtDict['VAPtbc'][Counter] = AdjDict['vap_10m']
	    CRHdiff = ExtDict['CRHtbc'][Counter] - AdjDict['crh_10m']
            ExtDict['CRHAtbc'][Counter] = ExtDict['CRHAtbc'][Counter] - CRHdiff
            UncDict['CRHuncHGT'].append(abs(CRHdiff) * unc_estimate)
            UncDict['CRHAuncHGT'].append(UncDict['CRHuncHGT'][Counter])
            ExtDict['CRHtbc'][Counter] = AdjDict['crh_10m']
	    CWBdiff = ExtDict['CWBtbc'][Counter] - AdjDict['cwb_10m']
            ExtDict['CWBAtbc'][Counter] = ExtDict['CWBAtbc'][Counter] - CWBdiff
            UncDict['CWBuncHGT'].append(abs(CWBdiff) * unc_estimate)
            UncDict['CWBAuncHGT'].append(UncDict['CWBuncHGT'][Counter])
            ExtDict['CWBtbc'][Counter] = AdjDict['cwb_10m']
	    DPDdiff = ExtDict['DPDtbc'][Counter] - AdjDict['dpd_10m']
            ExtDict['DPDAtbc'][Counter] = ExtDict['DPDAtbc'][Counter] - DPDdiff
            UncDict['DPDuncHGT'].append(abs(DPDdiff) * unc_estimate)
            UncDict['DPDAuncHGT'].append(UncDict['DPDuncHGT'][Counter])
            ExtDict['DPDtbc'][Counter] = AdjDict['dpd_10m']    
	    
	    # If this is a noSST_estimate scenario (noSST_estimate == True)
	    # then check uncertainty is the larger
	    # of either adjustment magnitude or 0.1 deg, 0.007*q
	    # Uncertainty will have already been set based on ESTH type
	    # NOTE UNCERTAINTIES ARE ALREADY SET SO USE COUNTER RATHER THAN APPEND!!!
	    if (noSST_estimate):
	    
#	        print('SILLY SST: ',ExtDict['SST'][Counter],ExtDict['SSTclim'][Counter],MySSTtbc, MySSTorig)
	        
		# Test AT
		if (abs(ATdiff) >= 0.1):    
	            
		    # Apply adjustment magnitude as uncertainty in T 
	            UncDict['ATuncHGT'][Counter] = abs(ATdiff)
                    UncDict['ATAuncHGT'][Counter] = abs(ATdiff)
		
		else:

		    # Assume uncertainty in T is 10m diff at DALR = 0.1degC (worst case scenario)
	            UncDict['ATuncHGT'][Counter] = 0.1
                    UncDict['ATAuncHGT'][Counter] = 0.1
		
		    
		# Test SHUuncHGT
		if (abs(SHUdiff) >= (ExtDict['SHUtbc'][Counter] * 0.007)):
		    
		    # Apply adjustment magnitude as uncertainty in SHU 
	            UncDict['SHUuncHGT'][Counter] = abs(SHUdiff)
                    UncDict['SHUAuncHGT'][Counter] = abs(SHUdiff)

                else:

		    # Assume uncertainty in SHU is 10m diff at DALR = 0.1 degC although this would mean that there is no moisture and so no change in q!
	            UncDict['SHUuncHGT'][Counter] = ExtDict['SHUtbc'][Counter] * 0.007 # should be 0.7% of q
                    UncDict['SHUAuncHGT'][Counter] = ExtDict['SHUtbc'][Counter] * 0.007

	        # Now apply these to the other variables;
                # Get vapour pressure from specific humidity
                UpperVal_vap = ch.vap_from_sh(ExtDict['SHUtbc'][Counter] + UncDict['SHUuncHGT'][Counter],ClimP,roundit=False)
	        LowerVal_vap = ch.vap_from_sh(ExtDict['SHUtbc'][Counter],ClimP,roundit=False) # NOW SHOULD BE LOWER
	        UncDict['VAPuncHGT'][Counter] = UpperVal_vap - LowerVal_vap
                UncDict['VAPAuncHGT'][Counter] = UpperVal_vap - LowerVal_vap

                # Get dew point temperature from vapour pressure (use at too to check for wet bulb <=0)
                UpperVal_dpt = ch.td_from_vap(UpperVal_vap,ClimP,ExtDict['ATtbc'][Counter],roundit=False)
	        LowerVal_dpt = ch.td_from_vap(LowerVal_vap,ClimP,ExtDict['ATtbc'][Counter],roundit=False)
	        UncDict['DPTuncHGT'][Counter] = UpperVal_dpt - LowerVal_dpt
                UncDict['DPTAuncHGT'][Counter] = UpperVal_dpt - LowerVal_dpt

                # Get wet bulb temperature from vapour pressure and dew point temperature and air temperature
                UpperVal_cwb = ch.wb(UpperVal_dpt,ExtDict['ATtbc'][Counter],ClimP,roundit=False)
	        LowerVal_cwb = ch.wb(LowerVal_dpt,ExtDict['ATtbc'][Counter],ClimP,roundit=False)
	        UncDict['CWBuncHGT'][Counter] = abs(UpperVal_cwb - LowerVal_cwb) # SHOULDN'T NEED abs BUT JUST IN CASE
                UncDict['CWBAuncHGT'][Counter] = abs(UpperVal_cwb - LowerVal_cwb)

                # Get relative humidity from dew point temperature and temperature
                UpperVal_crh = ch.rh(UpperVal_dpt,ExtDict['ATtbc'][Counter],ClimP,roundit=False)
	        LowerVal_crh = ch.rh(LowerVal_dpt,ExtDict['ATtbc'][Counter],ClimP,roundit=False)
	        UncDict['CRHuncHGT'][Counter] = abs(UpperVal_crh - LowerVal_crh)
                UncDict['CRHAuncHGT'][Counter] = abs(UpperVal_crh - LowerVal_crh)

                # Get dew point depression from temperautre and dew point depression
                UpperVal_dpd = ch.dpd(UpperVal_dpt,ExtDict['ATtbc'][Counter],roundit=False)
	        LowerVal_dpd = ch.dpd(LowerVal_dpt,ExtDict['ATtbc'][Counter],roundit=False)
	        UncDict['DPDuncHGT'][Counter] = abs(UpperVal_dpd - LowerVal_dpd)
                UncDict['DPDAuncHGT'][Counter] = abs(UpperVal_dpd - LowerVal_dpd)
	    
	    # So we have a 'good' value for tbc so now we should try calculating for hc (HGT only)
            # Do this for the ORIGINAL values
#            print("Original: ",HOA, ExtDict['ESTH'][Counter])
#            print(ExtDict['SST'][Counter],ExtDict['AT'][Counter],ExtDict['SHU'][Counter],ExtDict['W'][Counter],HOA,ExtDict['ESTH'][Counter],ExtDict['ESTH'][Counter],
#                  ExtDict['DPT'][Counter],ExtDict['VAP'][Counter],ExtDict['CRH'][Counter],ExtDict['CWB'][Counter],ExtDict['DPD'][Counter],ClimP)
            AdjDict,_ = hc.run_heightcorrection_final(MySSTorig,
                                                      ExtDict['AT'][Counter],
					              ExtDict['SHU'][Counter],
					              ExtDict['W'][Counter],
					              HOA,
					              ExtDict['ESTH'][Counter],
					              ExtDict['ESTH'][Counter],
					              dpt=ExtDict['DPT'][Counter],
					              vap=ExtDict['VAP'][Counter],
					              crh=ExtDict['CRH'][Counter],
					              cwb=ExtDict['CWB'][Counter],
					              dpd=ExtDict['DPD'][Counter],
					              climp=ClimP)
					      
            # Double check to make sure some sensible values have come out - in some cases there is non-convergence where height cannot be adjusted.
            # In these cases - apply no height correction. Uncertainty should be large but we've already set it based on tbc so we don't need to here.
            # In other cases where SHU is VERY small to begin with (most likely screwy!) e.g. Jan 1973 ob 145622 shu = 0.1 this leads to -ve adjusted values
            # and NaNs. I have added a catch for this in HeightCorrect.py so it now returns -99,9 in those cases.
            # In other cases where AT is >>40 but SST ~8 (e.g. April 1974 ob 118659) we have at_10m>100! We can't have that!
	    # There is a check that at_10m > -80 and < 65.
            if (AdjDict['at_10m'] > -99.):

#                print('SENSIBLE ORIG VALUES: ',AdjDict)

                # Then append the new adjusted variables, apply to the anomalies - NO uncertainty estimate to hc only!!! only assessing for tbc!!!
                ExtDict['AThc'].append(AdjDict['at_10m'])
                ExtDict['ATAhc'].append(ExtDict['ATA'][Counter] - (ExtDict['AT'][Counter] - AdjDict['at_10m']))
                ExtDict['DPThc'].append(AdjDict['dpt_10m'])
                ExtDict['DPTAhc'].append(ExtDict['DPTA'][Counter] - (ExtDict['DPT'][Counter] - AdjDict['dpt_10m']))
                ExtDict['SHUhc'].append(AdjDict['shu_10m'])
                ExtDict['SHUAhc'].append(ExtDict['SHUA'][Counter] - (ExtDict['SHU'][Counter] - AdjDict['shu_10m']))
                ExtDict['VAPhc'].append(AdjDict['vap_10m'])
                ExtDict['VAPAhc'].append(ExtDict['VAPA'][Counter] - (ExtDict['VAP'][Counter] - AdjDict['vap_10m']))
                ExtDict['CRHhc'].append(AdjDict['crh_10m'])
                ExtDict['CRHAhc'].append(ExtDict['CRHA'][Counter] - (ExtDict['CRH'][Counter] - AdjDict['crh_10m']))
                ExtDict['CWBhc'].append(AdjDict['cwb_10m'])
                ExtDict['CWBAhc'].append(ExtDict['CWBA'][Counter] - (ExtDict['CWB'][Counter] - AdjDict['cwb_10m']))
                ExtDict['DPDhc'].append(AdjDict['dpd_10m'])
                ExtDict['DPDAhc'].append(ExtDict['DPDA'][Counter] - (ExtDict['DPD'][Counter] - AdjDict['dpd_10m']))
            else:
	    
#                print('SILLY ORIG VALUES')
	        #pdb.set_trace()

                # Then append the original variables, apply to the anomalies 
                ExtDict['AThc'].append(ExtDict['AT'][Counter])
                ExtDict['ATAhc'].append(ExtDict['ATA'][Counter])
                ExtDict['DPThc'].append(ExtDict['DPT'][Counter])
                ExtDict['DPTAhc'].append(ExtDict['DPTA'][Counter])
                ExtDict['SHUhc'].append(ExtDict['SHU'][Counter])
                ExtDict['SHUAhc'].append(ExtDict['SHUA'][Counter])
                ExtDict['VAPhc'].append(ExtDict['VAP'][Counter])
                ExtDict['VAPAhc'].append(ExtDict['VAPA'][Counter])
                ExtDict['CRHhc'].append(ExtDict['CRH'][Counter])
                ExtDict['CRHAhc'].append(ExtDict['CRHA'][Counter])
                ExtDict['CWBhc'].append(ExtDict['CWB'][Counter])
                ExtDict['CWBAhc'].append(ExtDict['CWBA'][Counter])
                ExtDict['DPDhc'].append(ExtDict['DPD'][Counter])
                ExtDict['DPDAhc'].append(ExtDict['DPDA'][Counter])
	    
        else:
               
#	    print('SILLY TBC VALUES')
	    #pdb.set_trace()
            
	    # If no adjustment can be applied then still apply uncertainty in value. 
	    # Do this along with other instances of no_adjustment 
	    unc_estimate = no_adjustment
	    
	    # No need to do anything to the tbc avlues - there is no change from the previous process
	    # We do need to set the hc values to the original variables though.
            ExtDict['AThc'].append(ExtDict['AT'][Counter])
            ExtDict['ATAhc'].append(ExtDict['ATA'][Counter])
            ExtDict['DPThc'].append(ExtDict['DPT'][Counter])
            ExtDict['DPTAhc'].append(ExtDict['DPTA'][Counter])
            ExtDict['SHUhc'].append(ExtDict['SHU'][Counter])
            ExtDict['SHUAhc'].append(ExtDict['SHUA'][Counter])
            ExtDict['VAPhc'].append(ExtDict['VAP'][Counter])
            ExtDict['VAPAhc'].append(ExtDict['VAPA'][Counter])
            ExtDict['CRHhc'].append(ExtDict['CRH'][Counter])
            ExtDict['CRHAhc'].append(ExtDict['CRHA'][Counter])
            ExtDict['CWBhc'].append(ExtDict['CWB'][Counter])
            ExtDict['CWBAhc'].append(ExtDict['CWBA'][Counter])
            ExtDict['DPDhc'].append(ExtDict['DPD'][Counter])
            ExtDict['DPDAhc'].append(ExtDict['DPDA'][Counter])

	    # Set uncertainties to 0.0 to catch the ESTH == 10 case. These are then overwritten below in the case of unc_estimate == 999
            UncDict['ATuncHGT'].append(0.0)
            UncDict['ATAuncHGT'].append(0.0)
            UncDict['DPTuncHGT'].append(0.0)
            UncDict['DPTAuncHGT'].append(0.0)
            UncDict['SHUuncHGT'].append(0.0)
            UncDict['SHUAuncHGT'].append(0.0)
            UncDict['VAPuncHGT'].append(0.0)
            UncDict['VAPAuncHGT'].append(0.0)
            UncDict['CRHuncHGT'].append(0.0)
            UncDict['CRHAuncHGT'].append(0.0)
            UncDict['CWBuncHGT'].append(0.0)
            UncDict['CWBAuncHGT'].append(0.0)
            UncDict['DPDuncHGT'].append(0.0)
            UncDict['DPDAuncHGT'].append(0.0)
        
    # If ESTH is 999 then its a platform or if its 10 then its already at desired height so we're not applying any adjustments and need to pass values as they are to ExtDict	    
    else:	    
        ExtDict['AThc'].append(ExtDict['AT'][Counter])
        ExtDict['ATAhc'].append(ExtDict['ATA'][Counter])
        ExtDict['DPThc'].append(ExtDict['DPT'][Counter])
        ExtDict['DPTAhc'].append(ExtDict['DPTA'][Counter])
        ExtDict['SHUhc'].append(ExtDict['SHU'][Counter])
        ExtDict['SHUAhc'].append(ExtDict['SHUA'][Counter])
        ExtDict['VAPhc'].append(ExtDict['VAP'][Counter])
        ExtDict['VAPAhc'].append(ExtDict['VAPA'][Counter])
        ExtDict['CRHhc'].append(ExtDict['CRH'][Counter])
        ExtDict['CRHAhc'].append(ExtDict['CRHA'][Counter])
        ExtDict['CWBhc'].append(ExtDict['CWB'][Counter])
        ExtDict['CWBAhc'].append(ExtDict['CWBA'][Counter])
        ExtDict['DPDhc'].append(ExtDict['DPD'][Counter])
        ExtDict['DPDAhc'].append(ExtDict['DPDA'][Counter])
	
	# Set uncertainties to 0.0 to catch the ESTH == 10 case. These are then overwritten below in the case of unc_estimate == 999
        UncDict['ATuncHGT'].append(0.0)
        UncDict['ATAuncHGT'].append(0.0)
        UncDict['DPTuncHGT'].append(0.0)
        UncDict['DPTAuncHGT'].append(0.0)
        UncDict['SHUuncHGT'].append(0.0)
        UncDict['SHUAuncHGT'].append(0.0)
        UncDict['VAPuncHGT'].append(0.0)
        UncDict['VAPAuncHGT'].append(0.0)
        UncDict['CRHuncHGT'].append(0.0)
        UncDict['CRHAuncHGT'].append(0.0)
        UncDict['CWBuncHGT'].append(0.0)
        UncDict['CWBAuncHGT'].append(0.0)
        UncDict['DPDuncHGT'].append(0.0)
        UncDict['DPDAuncHGT'].append(0.0)

    # Now get uncertainty estimates in the case where no adjustment has been applied (platform or unresolved equation)
    if (unc_estimate == 999):	  
        # This is a convoluted application of abs(T-SST)/2. and abs(q-q0)/2. rolled out to all variables  
        # If there is no SST then we cannot get difference between surface values
	# - assume unc in T of worst case scenario DALR 0.1deg C (change in 10m height)
	
	# If SST is present and valid then do the ob-surface / 2 thing
	if ((ExtDict['SST'][Counter] >= -2.0) & (ExtDict['SST'][Counter] <= 40.) & (ExtDict['SSTclim'][Counter] == 0)):
	    # Get surface values using function in height correct - requires SST to be present
	    # t0 is SST
	    # q0 is 0.98 * q(SST)
	    u0,t0,q0 = hc.get_surface_values(ExtDict['SST'][Counter])

	    # Assume uncertainty in T is abs(T - t0) 2.
	    UncDict['ATuncHGT'][Counter] = abs(ExtDict['ATtbc'][Counter] - t0)/2.
	    # Same for anomaly - would be so many degrees above or below what it is?
            UncDict['ATAuncHGT'][Counter] = abs(ExtDict['ATtbc'][Counter] - t0)/2.

	    # Assume uncertainty in  is 10m diff at DALR = 0.1degC
	    UncDict['SHUuncHGT'][Counter] = abs(ExtDict['SHUtbc'][Counter] - q0)/2.
            UncDict['SHUAuncHGT'][Counter] = abs(ExtDict['SHUtbc'][Counter] - q0)/2.
	    
	    # Now apply these to the other variables;
            # Get vapour pressure from specific humidity
            UpperVal_vap = ch.vap_from_sh(ExtDict['SHUtbc'][Counter],ClimP,roundit=False)
	    LowerVal_vap = ch.vap_from_sh(q0,ClimP,roundit=False) # NOT NECESSARILY A LOWER VALUE!!! LOWER IN HEIGHT
	    UncDict['VAPuncHGT'][Counter] = abs(UpperVal_vap - LowerVal_vap)/2.
            UncDict['VAPAuncHGT'][Counter] = abs(UpperVal_vap - LowerVal_vap)/2.

            # Get dew point temperature from vapour pressure (use at too to check for wet bulb <=0)
            UpperVal_dpt = ch.td_from_vap(UpperVal_vap,ClimP,ExtDict['ATtbc'][Counter],roundit=False)
	    LowerVal_dpt = ch.td_from_vap(LowerVal_vap,ClimP,t0,roundit=False)
	    UncDict['DPTuncHGT'][Counter] = abs(UpperVal_dpt - LowerVal_dpt)/2.
            UncDict['DPTAuncHGT'][Counter] = abs(UpperVal_dpt - LowerVal_dpt)/2.
 
            # Get wet bulb temperature from vapour pressure and dew point temperature and air temperature
            UpperVal_cwb = ch.wb(UpperVal_dpt,ExtDict['ATtbc'][Counter],ClimP,roundit=False)
	    LowerVal_cwb = ch.wb(LowerVal_dpt,t0,ClimP,roundit=False)
	    UncDict['CWBuncHGT'][Counter] = abs(UpperVal_cwb - LowerVal_cwb)/2.
            UncDict['CWBAuncHGT'][Counter] = abs(UpperVal_cwb - LowerVal_cwb)/2.
 
            # Get relative humidity from dew point temperature and temperature
            UpperVal_crh = ch.rh(UpperVal_dpt,ExtDict['ATtbc'][Counter],ClimP,roundit=False)
	    LowerVal_crh = ch.rh(LowerVal_dpt,t0,ClimP,roundit=False)
	    UncDict['CRHuncHGT'][Counter] = abs(UpperVal_crh - LowerVal_crh)/2.
            UncDict['CRHAuncHGT'][Counter] = abs(UpperVal_crh - LowerVal_crh)/2.
 
            # Get dew point depression from temperautre and dew point depression
            UpperVal_dpd = ch.dpd(UpperVal_dpt,ExtDict['ATtbc'][Counter],roundit=False)
	    LowerVal_dpd = ch.dpd(LowerVal_dpt,t0,roundit=False)
	    UncDict['DPDuncHGT'][Counter] = abs(UpperVal_dpd - LowerVal_dpd)/2.
            UncDict['DPDAuncHGT'][Counter] = abs(UpperVal_dpd - LowerVal_dpd)/2.
	
	# If there is no SST or its invalid then we're totally guessing
	# Yuk - had thought about DALR/SALR for 10m but its tricky to derive through the variables
	# Could go with a percentage but then how does that work with T?
	# Lets go with DALR (maximum expected change in T) and then assume saturation for respective rate of change in absolute humidity
	# So - ~7% increase in q or e for 1deg rise in t = 0.7% for 0.1 change in T
	# This is all a bit horrible
	else:
	
	    # Assume uncertainty in T is 10m diff at DALR = 0.1degC (worst case scenario)
	    UncDict['ATuncHGT'][Counter] = 0.1
            UncDict['ATAuncHGT'][Counter] = 0.1

	    # Assume uncertainty in SHU is 10m diff at DALR = 0.1 degC although this would mean that there is no moisture and so no change in q!
	    UncDict['SHUuncHGT'][Counter] = ExtDict['SHU'][Counter] * 0.007 # should be 0.7% of q
            UncDict['SHUAuncHGT'][Counter] = ExtDict['SHU'][Counter] * 0.007

	    # Now apply these to the other variables;
            # Get vapour pressure from specific humidity
            UpperVal_vap = ch.vap_from_sh(ExtDict['SHUtbc'][Counter] + UncDict['SHUuncHGT'][Counter],ClimP,roundit=False)
	    LowerVal_vap = ch.vap_from_sh(ExtDict['SHUtbc'][Counter],ClimP,roundit=False) # NOW SHOULD BE LOWER
	    UncDict['VAPuncHGT'][Counter] = UpperVal_vap - LowerVal_vap
            UncDict['VAPAuncHGT'][Counter] = UpperVal_vap - LowerVal_vap

            # Get dew point temperature from vapour pressure (use at too to check for wet bulb <=0)
            UpperVal_dpt = ch.td_from_vap(UpperVal_vap,ClimP,ExtDict['ATtbc'][Counter],roundit=False)
	    LowerVal_dpt = ch.td_from_vap(LowerVal_vap,ClimP,ExtDict['ATtbc'][Counter],roundit=False)
	    UncDict['DPTuncHGT'][Counter] = UpperVal_dpt - LowerVal_dpt
            UncDict['DPTAuncHGT'][Counter] = UpperVal_dpt - LowerVal_dpt

            # Get wet bulb temperature from vapour pressure and dew point temperature and air temperature
            UpperVal_cwb = ch.wb(UpperVal_dpt,ExtDict['ATtbc'][Counter],ClimP,roundit=False)
	    LowerVal_cwb = ch.wb(LowerVal_dpt,ExtDict['ATtbc'][Counter],ClimP,roundit=False)
	    UncDict['CWBuncHGT'][Counter] = abs(UpperVal_cwb - LowerVal_cwb) # SHOULDN'T NEED abs BUT JUST IN CASE
            UncDict['CWBAuncHGT'][Counter] = abs(UpperVal_cwb - LowerVal_cwb)

            # Get relative humidity from dew point temperature and temperature
            UpperVal_crh = ch.rh(UpperVal_dpt,ExtDict['ATtbc'][Counter],ClimP,roundit=False)
	    LowerVal_crh = ch.rh(LowerVal_dpt,ExtDict['ATtbc'][Counter],ClimP,roundit=False)
	    UncDict['CRHuncHGT'][Counter] = abs(UpperVal_crh - LowerVal_crh)
            UncDict['CRHAuncHGT'][Counter] = abs(UpperVal_crh - LowerVal_crh)

            # Get dew point depression from temperautre and dew point depression
            UpperVal_dpd = ch.dpd(UpperVal_dpt,ExtDict['ATtbc'][Counter],roundit=False)
	    LowerVal_dpd = ch.dpd(LowerVal_dpt,ExtDict['ATtbc'][Counter],roundit=False)
	    UncDict['DPDuncHGT'][Counter] = abs(UpperVal_dpd - LowerVal_dpd)
            UncDict['DPDAuncHGT'][Counter] = abs(UpperVal_dpd - LowerVal_dpd)
	    
    
#    print('Check the outputs: ',Counter)
#    pdb.set_trace()
    
    return ExtDict,UncDict

#************************************************************************************************************
# ApplyMeasUnc
#************************************************************************************************************
def ApplyMeasUnc(UncDict,Counter,ClimP):
    '''
    Based on the measurement uncertainty described for HadISDH.land in Willett et al., (2014)
		
    For psychormeters we can assume 0.3 deg C wetbulb depession for 2 sigma - so 0.15 for 1 sigma!!!
    For dry bulb assume 0.2 deg C measurement error for 1 sigma from Brohan et al., 2006
    The uncertainty in RH depends on the dry bulb temperature
    For RH sensors this is approximatly 2% at 10% RH and 2.5% at 98% RH - so not a massive change depending on RH
    For 1 sigma this scales out as:
    -50 deg C = 15% 0 deg C = 2.75% RH, 50 deg = 0.8% RH	- 
    -50 = 15%
    -40 = 15%
    -30 = 15%
    -20 = 10%
    -10 = 5%
      0 = 2.75%
     10 = 1.8%
     20 = 1.35%
     30 = 1.1%
     40 = 0.95%
     50+ = 0.8% 
     
     So 1 sigma = [15,15,15,10,5,2.75,1.8,1.35,1.1,0.95,0.8] 

    give all 40-50 1.4%
    give all 0-10 6%  (apply upwards bin)
    USED Michael de Podesta's spread sheet with eq. (ice and wet) from Buck 1981 (my thesis ch 2)

    '''
    # AT bins to guide uncertainty in terms of RH
    t_bins = np.array([-40,-30,-20,-10,0,10,20,30,40,50,100])	# degrees C
    
    # 1 sigma uncertainty in RH corresponding to t_bins
    rh_unc_bins = np.array([15,15,15,10,5,2.75,1.8,1.35,1.1,0.95,0.8]) 

    # 1 sigma uncertainty in AT
    t_unc = 0.2

    # 1 sigma uncertaint in CWB
    tw_unc = 0.15
    
    # For AT and CWB - simple
    UncDict['ATuncM'].append(t_unc)
    UncDict['ATAuncM'].append(t_unc)
    UncDict['CWBuncM'].append(tw_unc)
    UncDict['CWBAuncM'].append(tw_unc)
		
    # The rest require an AT dependent amount of RH
    TheBin = np.where(t_bins > UncDict['ATtbc'][Counter])[0]
   
    # Assess for CRH first: compare CRHtbc with CRHtbc+rh_unc(TheBin)
    # If this goes above 100% RH then we're going to end up with very small uncertainties if we fix to 100%rh
    # No Cap at Rh 100% - could assess in the other direction (-ve) but this should equal the same thing?
    rh_unc = rh_unc_bins[TheBin[0]]
    UncDict['CRHuncM'].append(rh_unc) 
    UncDict['CRHAuncM'].append(rh_unc) 
   
    # Compare (VAPtbc+rh_unc) - VAPtbc to get VAP uncertainty e = ((RH+RHunc)/100.)*e_sat 
    e_unc = (((UncDict['CRHtbc'][Counter] + rh_unc) / 100.) * ch.vap(UncDict['ATtbc'][Counter],UncDict['ATtbc'][Counter],ClimP,roundit=False)) - UncDict['VAPtbc'][Counter] 
    UncDict['VAPuncM'].append(e_unc)
    UncDict['VAPAuncM'].append(e_unc)
   
    # Compare (SHUtbc+e_unc) - SHUtbc to get SHU uncertainty
    q_unc = ch.sh_from_vap(UncDict['VAPtbc'][Counter]+e_unc,ClimP,roundit=False) - UncDict['SHUtbc'][Counter]		
    UncDict['SHUuncM'].append(q_unc)
    UncDict['SHUAuncM'].append(q_unc)

    # Compare (DPTtbc+e_unc) - DPTtbc to get DPT uncertainty
    dpt_unc = ch.td_from_vap(UncDict['VAPtbc'][Counter]+e_unc,ClimP,UncDict['ATtbc'][Counter],roundit=False) - UncDict['DPTtbc'][Counter]
    UncDict['DPTuncM'].append(dpt_unc)
    UncDict['DPTAuncM'].append(dpt_unc)

    # Compare DPDtbc+dpt_unc - DPDtbc to get DPD_uncertainty
    dpd_unc = (UncDict['DPDtbc'][Counter]+dpt_unc) - UncDict['DPDtbc'][Counter]
    UncDict['DPDuncM'].append(dpd_unc)
    UncDict['DPDAuncM'].append(dpd_unc)
    
    return UncDict

#************************************************************************************************************
# ApplyRoundUnc
#************************************************************************************************************
def ApplyRoundUnc(UncDict,ExtDict,Counter,ClimP):
    '''
    There is a tendency for many obs, especially DPT to be recorded only to a whole number. For DPT this is most common in the early period prior to 1982 and especially prior to 1980.
    There are many Decks with a high percentage of 0.0s (much much higher >2x) than the other decimals even in the later record though.
    We have no idea whether these are rounded, truncated, ceiling'd etc. For AT there is also a higher % of 0.5s and sometimes 0.2s and 0.8s - Fahrenheit conversion???
    
    We have assessed tracks where 0.0s are very common and also Decks/Years.
    
    We can apply an uncertainty of 0.5/SQRT(3) deg C to any ob that is likely to be part of a whole number Deck/track for AT and/ or DPT.
    
    The combined uncertainty can then be rolled out to th other variables. When both AT and DPT are rounded this error could be very large or very small though.
    
    Apply UNCround uncertainty of 0.5/SQRT(3) deg C to AT / DPT if the ATround or DPTround flag is set to 1. (> 50% of trk with at least
    24 obs are .0s) 
    OR if AT or DPT is .0 and fits into one of these YR/Deck categories: (0s = max frequency and > 1.25 * mean of others - PlotDecimalFreq_APR2016.py) 
    
    ICOADS.3.0.0 based on DeckStatsROUNDDPT_1.25_I300_all_OBSclim2NBC_OCT2016.txt
    Deck years with frequency 0s > 1.25 * mean frequency(all other decimals)
    1973         555 666         732 735                                     888 889             926
    1974                         732 735                                     888 889             926
    1975                         732 735                                     888 889             926
    1976                         732 735                                     888 889
    1977                         732 735                                     888 889             926 927  
    1978                         732 735     749                 849 850     888 889                 927
    1979     254                 732 735     749                 849         888 889             926 927    
    1980                         732 735                                     888 889 892     896 926 927
    1981                         732 735                                     888 889 892     896 926 927
    1982     254                 732 735                                         889 892     896 926 927
    1983     254                 732 735                                         889 892     896 926 927
    1984                         732 735                                         889 892     896 926 927
    1985     254                 732 735                                         889 892     896 926 927
    1986     254                 732 735                                     888 889 892     896 926 927	
    1987 233 254                 732 735                                     888 889 892         926 927	
    1988                         732 735                                     888 889 892 893 896 926
    1989                                                                     888 889 892         926 927
    1990                             735                                     888 889 892         926 927
    1991                                                                     888 889 892 893     926 927
    1992                                         781                         888 889 892 893 896 926
    1993                                                                     888 889 892 893 896 926
    1994                                                                     888 889 892         926 927
    1995                                                                 874 888 889 892 893 896 926 927
    1996                             735                                 874 888     892     896 926 927
    1997                                                                 874 888     892     896 926 927   
    1998                                             792 793                                     926 927
    1999                                             792                                         926 927 992
    2000                 700                         792                                         926 927 992
    2001                 700 708                     792                                         926 927 992	  
    2002                                             792                                         926 927 992 993
    2003                     708                     792                                         926 927 992 993   
    2004                     708                     792                                             927 992
    2005                 700 708                     792 793                                         927 992 993    
    2006                 700 708                     792                                             927 992
    2007                     708         740         792 793                                         927 992 993
    2008                 700 708                     792 793                                         927 992 993
    2009                     708                     792                                             927 992
    2010                     708                     792                                             927 992 993
    2011                     708                     792                                             927 992 993
    2012                     708                     792                                             927 992 993
    2013                                             792                                                 992 993
    2014                                             792     794         874                             992 993
    2015                                             792                                                 992

    233 = [187]
    254 = [1979,1982,1983,1985,1986,1987]
    555 = [1973]
    666 = [1973]
    700 = [2000,2001,2005,2006,2008]
    708 = [2001,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    732 = [1973,1974,1975,1976,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988]
    735 = [1973,1974,1975,1976,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1990,1996]
    740 = [2007]
    749 = [1978,1979]
    781 = [1992]
    792 = [1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
    793 = [1998,2005,2007,2008]
    794 = [2014]
    849 = [1978,1979]
    850 = [1978]
    874 = [1995,1996,1997,2014]
    888 = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    889 = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995]
    892 = [1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    893 = [1988,1991,1992,1993,1995]
    896 = [1980,1981,1982,1983,1984,1985,1986,1988,1992,1993,1995,1996,1997]
    926 = [1973,1974,1975,1977,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003]
    927 = [1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1989,1990,1991,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    992 = [1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
    993 = [2002,2003,2005,2007,2008,2010,2011,2012,2013,2014]

    ICOADS.3.0.0 based on DeckStatsROUNDAT_1.25_I300_all_OBSclim2NBC_OCT2016.txt
    Deck years with frequency 0s > 1.25 * mean frequency(all other decimals)
    AT: 0.5s also an issue to T but ignoring that for now. 555 all 0.5 in 1973!
    1973 128     223                 254 255         720 732                                         888 889             898 900 926 927 928 
    1974 128     223                 254 255         720 732 735                                     888 889             898 900 926 927 928
    1975 128     223                 254 255         720 732                                         888 889                 900 926 927 
    1976 128     223                 254             720 732 735                                     888 889                 900 926 927 
    1977 128     223 224             254             720 732 735                                     888 889                 900 926 927
    1978 128     223     229         254             720 732 735 749                 849 850         888 889                 900 926 927 
    1979         223     229         254 255         720 732 735 749                 849 850         888 889                 900 926 927 
    1980         223     229         254             720 732 735                                     888 889 892     896         926 927
    1981         223     229         254             720 732 735                                     888 889 892     896         926 927
    1982                     233     254             720 732 735                                             892     896         926 927
    1983                     233 239 254                 732         781                                     892     896         926 927
    1984                     233     254                 732 735                                         889 892     896         926 927
    1985                     233     254             720 732                                                 892     896         926 927
    1986                     233 239 254                 732         781                             888     892     896         926 927
    1987                     233 239 254                 732 735                                     888     892 893 896         926 927 
    1988                     233 239 254                 732 735     781                             888     892 893 896         926 927
    1989                     233 239 254                 732         781                             888 889 892 893             926 927 
    1990                     233 239 254                 732         781                             888 889 892 893             926 927 
    1991                         239 254                             781                             888     892 893             926 927
    1992                     233 239 254                     735     781                             888     892 893 896         926 927 
    1993                     233 239 254                             781                             888     892 893 896         926 927
    1994                     233     254                                                             888     892     896         926 927
    1995     144                                                                             874     888     892 893             926 927
    1996                                                                                     874     888     892     896         926 927
    1997                                                                                     874     888     892     896         926 927
    1998                                                                 792                                                     926 927
    1999                                                                 792                                                     926 927     992
    2000                                     700                         792                                                     926 927     992 
    2001                                     700                         792                                                     926 927     992 
    2002                                     700                         792                                                     926 927     992 993
    2003                                     700                         792                                                     926 927     992 
    2004                                     700                         792                                                     926 927     992 
    2005                                     700                         792 793                                                 926 927     992 993
    2006                                     700                         792                                                     926 927     992 
    2007                                     700                         792 793                                                 926 927     992 993
    2008                                     700 708                     792 793                                                 926 927     992 993
    2009                                     700                         792                                                     926 927     992 993
    2010                                     700                         792                                                     926 927     992 993
    2011                                     700 708                     792                                                     926 927     992 993
    2012                                     700                         792                     875                             926 927     992 993
    2013                                                                 792                     875                             926         992 993 
    2014                                                                 792     794         874 875                             926         992 993
    2015                                                                 792                                                                 992

    128 = [1973,1974,1975,1976,1977,1978]
    144 = [1995]
    223 = [1973,1974,1975,1976,1977,1978,1979,1980,1981]
    224 = [1977]
    229 = [1978,1979,1980,1981]
    233 = [1982,1983,1984,1985,1986,1987,1988,1989,1990,1992,1993,1994]
    239 = [1983,1986,1987,1988,1989,1990,1991,1992,1993]
    254 = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994]
    255 = [1973,1974,1975,1979]
    700 = [2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    708 = [2008,2011]
    720 = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1985]
    732 = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990]
    735 = [1974,1976,1977,1978,1979,1980,1981,1982,1984, 1987,1988,1992]
    749 = [1978,1979]
    781 = [1983,1986,1988,1989,1990,1991,1992,1993]
    792 = [1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
    793 = [2005,2007,2008]
    794 = [2014]
    849 = [1978,1979]
    850 = [1978,1979]
    874 = [1995,1996,1997,2014]
    875 = [2012,2013,2014]
    888 = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    889 = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1984,1989,1990]
    892 = [1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    893 = [1987,1988,1989,1990,1991,1992,1993,1995]
    896 = [1980,1981,1982,1983,1984,1985,1986,1987,1988,1992,1993,1994,1996,1997]
    898 = [1973,1974]
    900 = [1973,1974,1975,1976,1977,1978,1979]
    926 = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014]
    927 = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    928 = [1973,1974]
    992 = [1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
    993 = [2002,2005,2007,2008,2009,2010,2011,2012,2013,2014]
    
    ICOADS.3.0.0 based on DeckStatsROUNDDPT_1.25_I300_all_OBSclim2NBC_OCT2016.txt
    Deck years with frequency 0s >= 2.0 * mean frequency(all other decimals)
    1973     555 666     732 735                 888 889
    1974                 732 735                 888 889
    1975                 732 735                 888 889
    1976                 732 735                 888 889
    1977                 732 735                 888 889
    1978                 732 735 749     849     888 889
    1979                 732 735         849     888 889
    1980                 732 735                 888 889 892 896
    1981                 732 735                 888 889 892 896
    1982                 732 735                         892 896
    1983                 732 735                         892 896
    1984                 732 735                     889 892
    1985                 732 735                     889 892
    1986 254                 735                 888 889 892
    1987                                         888 889 892
    1988                                         888 889 892
    1989                                         888 889 892
    1990                                         888 889 892
    1991                                         888 889 892
    1992                                         888 889 892
    1993                                         888 889 892 896
    1994                                         888 889 892
    1995                                     874 888 889 892 896     927
    1996                                     874 888     892 896     927
    1997                                     874 888     892 896 926 927
    1998                             792                         926 927 
    1999                             792                         926 927 992
    2000                             792                             927 992
    2001             708             792                             927 992
    2002                             792                             927 992
    2003             708             792                             927 992
    2004             708             792                             927 992
    2005             708             792                             927 992
    2006             708             792                             927 992
    2007             708             792                             927 992
    2008             708             792                             927 992
    2009             708             792                             927 992
    2010             708             792                             927 992
    2011             708             792                             927 992
    2012             708             792                             927 992
    2013                             792                                     993 
    2014 
    2015 

    DPT_dict[254] = [1986]
    DPT_dict[555] = [1973]
    DPT_dict[666] = [1973]
    DPT_dict[708] = [2001,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    DPT_dict[732] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985]
    DPT_dict[735] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986]
    DPT_dict[749] = [1978]
    DPT_dict[792] = [1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013]
    DPT_dict[849] = [1978,1979]
    DPT_dict[874] = [1995,1996,1997]
    DPT_dict[888] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    DPT_dict[889] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995]
    DPT_dict[892] = [1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    DPT_dict[896] = [1980,1981,1982,1983,1993,1995,1996,1997]
    DPT_dict[926] = [1997,1998,1999]
    DPT_dict[927] = [1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    DPT_dict[992] = [1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    DPT_dict[993] = [2013]

    ICOADS.3.0.0 based on DeckStatsROUNDAT_1.25_I300_all_OBSclim2NBC_OCT2016.txt
    Deck years with frequency 0s >= 2.0 * mean frequency(all other decimals)
    1973 128 223             254 255     732                                 888             900 926 927
    1974 128 223             254 255     732                                 888         898 900 926 927 928
    1975 128 223             254 255     732                                 888             900 926 927
    1976 128 223             254         732                                 888             900 926 927
    1977 128 223             254         732                                 888             900 926 927
    1978 128 223 229         254         732 749             849 850         888             900 926 927
    1979     223 229         254 255     732 749             849 850         888             900 926 927
    1980     223 229         254         732                                 888 892 896         926 927
    1981     223             254         732                                 888 892 896         926 927
    1982             233     254         732                                     892 896         926 927
    1983             233 239 254         732                                     892 896         926 927
    1984             233     254         732                                     892             926 927
    1985             233     254         732                                     892             926 927
    1986             233 239 254         732     781                         888 892             926 927
    1987             233     254         732                                 888 892             926 927
    1988             233     254         732     781                         888 892             926 927
    1989             233     254         732     781                         888 892             926 927
    1990             233 239 254         732     781                         888 892             926 927
    1991                     254                 781                         888 892             926 927
    1992             233     254                 781                         888 892             926 927
    1993             233     254                 781                         888 892 896         926 927
    1994             233     254                                             888 892 896         926 927
    1995                                                             874     888 892             926 927
    1996                                                             874     888 892 896         926 927
    1997                                                             874     888 892 896         926 927
    1998                                             792                                         926 927
    1999                                             792                                         926 927    992
    2000                             700             792                                         926 927    992
    2001                             700             792                                         926 927    992
    2002                                             792                                         926 927    992
    2003                                             792                                         926 927    992
    2004                                             792                                         926 927    992
    2005                                             792                                         926 927    992
    2006                                             792                                         926 927    992
    2007                                             792 793                                     926 927    992
    2008                             700             792                                         926 927    992 993
    2009                                             792                                         926 927    992 993
    2010                                             792                                         926 927    992 993
    2011                                             792                                         926 927    992 993
    2012                                             792                 875                     926 927    992 993
    2013                                             792                 875                     926        992 993
    2014                                             792             874 875                     926        992
    2015                                             792                                                    992

    AT_dict[128] = [1973,1974,1975,1976,1977,1978]
    AT_dict[223] = [1973,1974,1975,1976,1977,1978,1979,1980,1981]
    AT_dict[229] = [1978,1979,1980]
    AT_dict[233] = [1982,1983,1984,1985,1986,1987,1988,1989,1990,1992,1993,1994]
    AT_dict[239] = [1983,1986,1990]
    AT_dict[254] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994]
    AT_dict[255] = [1973,1974,1975,1979]
    AT_dict[700] = [2000,2001,2008]
    AT_dict[732] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990]
    AT_dict[749] = [1978,1979]
    AT_dict[781] = [1986,1988,1989,1990,1991,1992,1993]
    AT_dict[792] = [1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
    AT_dict[793] = [2007]
    AT_dict[849] = [1978,1979]
    AT_dict[850] = [1978,1979]
    AT_dict[874] = [1995,1996,1997,2014]
    AT_dict[875] = [2012,2013,2014]
    AT_dict[888] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    AT_dict[892] = [1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    AT_dict[896] = [1980,1981,1982,1983,1993,1994,1996,1997]
    AT_dict[898] = [1974]
    AT_dict[900] = [1973,1974,1975,1976,1977,1978,1979]
    AT_dict[926] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014]
    AT_dict[927] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    AT_dict[928] = [1974]
    AT_dict[992] = [1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
    AT_dict[993] = [2008,2009,2010,2011,2012,2013]
    

    '''
    
    # Set up uncertainty value to be applied
    RoundUnc = 0.5 / np.sqrt(3.)
    RoundUncComb = 1. / np.sqrt(3.)
    
    # Set up look up table for DPT Yr/Decks THESE ARE OLD ONES FOR ICOADS.2.5.1 ERAclimNBC
    DPT_dict = dict([])
    # >1.25
    #DPT_dict[233] = [187]
    #DPT_dict[254] = [1979,1982,1983,1985,1986,1987]
    #DPT_dict[555] = [1973]
    #DPT_dict[666] = [1973]
    #DPT_dict[700] = [2000,2001,2005,2006,2008]
    #DPT_dict[708] = [2001,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    #DPT_dict[732] = [1973,1974,1975,1976,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988]
    #DPT_dict[735] = [1973,1974,1975,1976,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1990,1996]
    #DPT_dict[740] = [2007]
    #DPT_dict[749] = [1978,1979]
    #DPT_dict[781] = [1992]
    #DPT_dict[792] = [1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
    #DPT_dict[793] = [1998,2005,2007,2008]
    #DPT_dict[794] = [2014]
    #DPT_dict[849] = [1978,1979]
    #DPT_dict[850] = [1978]
    #DPT_dict[874] = [1995,1996,1997,2014]
    #DPT_dict[888] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    #DPT_dict[889] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995]
    #DPT_dict[892] = [1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    #DPT_dict[893] = [1988,1991,1992,1993,1995]
    #DPT_dict[896] = [1980,1981,1982,1983,1984,1985,1986,1988,1992,1993,1995,1996,1997]
    #DPT_dict[926] = [1973,1974,1975,1977,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003]
    #DPT_dict[927] = [1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1989,1990,1991,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    #DPT_dict[992] = [1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
    #DPT_dict[993] = [2002,2003,2005,2007,2008,2010,2011,2012,2013,2014]
    # >=2.0
    DPT_dict[254] = [1986]
    DPT_dict[555] = [1973]
    DPT_dict[666] = [1973]
    DPT_dict[708] = [2001,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    DPT_dict[732] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985]
    DPT_dict[735] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986]
    DPT_dict[749] = [1978]
    DPT_dict[792] = [1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013]
    DPT_dict[849] = [1978,1979]
    DPT_dict[874] = [1995,1996,1997]
    DPT_dict[888] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    DPT_dict[889] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995]
    DPT_dict[892] = [1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    DPT_dict[896] = [1980,1981,1982,1983,1993,1995,1996,1997]
    DPT_dict[926] = [1997,1998,1999]
    DPT_dict[927] = [1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    DPT_dict[992] = [1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    DPT_dict[993] = [2013]
    
    # Set up look up table for AT Yr/Decks THESE ARE OLD ONES FOR ICOADS.2.5.1 ERAclimNBC
    AT_dict = dict([])
    # >1.25
    #AT_dict[128] = [1973,1974,1975,1976,1977,1978]
    #AT_dict[144] = [1995]
    #AT_dict[223] = [1973,1974,1975,1976,1977,1978,1979,1980,1981]
    #AT_dict[224] = [1977]
    #AT_dict[229] = [1978,1979,1980,1981]
    #AT_dict[233] = [1982,1983,1984,1985,1986,1987,1988,1989,1990,1992,1993,1994]
    #AT_dict[239] = [1983,1986,1987,1988,1989,1990,1991,1992,1993]
    #AT_dict[254] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994]
    #AT_dict[255] = [1973,1974,1975,1979]
    #AT_dict[700] = [2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    #AT_dict[708] = [2008,2011]
    #AT_dict[720] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1985]
    #AT_dict[732] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990]
    #AT_dict[735] = [1974,1976,1977,1978,1979,1980,1981,1982,1984, 1987,1988,1992]
    #AT_dict[749] = [1978,1979]
    #AT_dict[781] = [1983,1986,1988,1989,1990,1991,1992,1993]
    #AT_dict[792] = [1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
    #AT_dict[793] = [2005,2007,2008]
    #AT_dict[794] = [2014]
    #AT_dict[849] = [1978,1979]
    #AT_dict[850] = [1978,1979]
    #AT_dict[874] = [1995,1996,1997,2014]
    #AT_dict[875] = [2012,2013,2014]
    #AT_dict[888] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    #AT_dict[889] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1984,1989,1990]
    #AT_dict[892] = [1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    #AT_dict[893] = [1987,1988,1989,1990,1991,1992,1993,1995]
    #AT_dict[896] = [1980,1981,1982,1983,1984,1985,1986,1987,1988,1992,1993,1994,1996,1997]
    #AT_dict[898] = [1973,1974]
    #AT_dict[900] = [1973,1974,1975,1976,1977,1978,1979]
    #AT_dict[926] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014]
    #AT_dict[927] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    #AT_dict[928] = [1973,1974]
    #AT_dict[992] = [1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
    #AT_dict[993] = [2002,2005,2007,2008,2009,2010,2011,2012,2013,2014]
    # >= 2.0
    AT_dict[128] = [1973,1974,1975,1976,1977,1978]
    AT_dict[223] = [1973,1974,1975,1976,1977,1978,1979,1980,1981]
    AT_dict[229] = [1978,1979,1980]
    AT_dict[233] = [1982,1983,1984,1985,1986,1987,1988,1989,1990,1992,1993,1994]
    AT_dict[239] = [1983,1986,1990]
    AT_dict[254] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994]
    AT_dict[255] = [1973,1974,1975,1979]
    AT_dict[700] = [2000,2001,2008]
    AT_dict[732] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990]
    AT_dict[749] = [1978,1979]
    AT_dict[781] = [1986,1988,1989,1990,1991,1992,1993]
    AT_dict[792] = [1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
    AT_dict[793] = [2007]
    AT_dict[849] = [1978,1979]
    AT_dict[850] = [1978,1979]
    AT_dict[874] = [1995,1996,1997,2014]
    AT_dict[875] = [2012,2013,2014]
    AT_dict[888] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    AT_dict[892] = [1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997]
    AT_dict[896] = [1980,1981,1982,1983,1993,1994,1996,1997]
    AT_dict[898] = [1974]
    AT_dict[900] = [1973,1974,1975,1976,1977,1978,1979]
    AT_dict[926] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014]
    AT_dict[927] = [1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
    AT_dict[928] = [1974]
    AT_dict[992] = [1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
    AT_dict[993] = [2008,2009,2010,2011,2012,2013]
        
    # Look up - TEST THE ORIGINAL VALUE!!!!! - Make sure a VARuncR is set in all cases to 0.0 or 0.5
    # First - has it had an ATround set to 1?
    # Second - check if its a .0
    # AND - is it in an offending Deck?
    # AND - is it in an offending YR?
    if (UncDict['ATround'][Counter] == 1): 
       
        # It ticks either category so append VARuncR accordingly
#        print('Found an ATround')
	UncDict['ATuncR'].append(RoundUnc)
	UncDict['ATAuncR'].append(RoundUnc)

    # Now check if its a .0 and from an offending deck
    # given it some leaway for floating point shenannigans - numbers only recorded to one decimal place anyway
    elif ((abs(ExtDict['AT'][Counter] - np.floor(ExtDict['AT'][Counter])) < 0.05) & \
	  (UncDict['DCK'][Counter] in AT_dict)):

	# This AT is a ROUND!!!
        if (UncDict['YR'][Counter] in AT_dict[UncDict['DCK'][Counter]]):
#            print('Found an AT DCK round')
	    UncDict['ATuncR'].append(RoundUnc)
	    UncDict['ATAuncR'].append(RoundUnc)

        # Otherwise it isn't    
	else:
	    UncDict['ATuncR'].append(0.0)
	    UncDict['ATAuncR'].append(0.0)

    # Otherwise it isn't    
    else:
	UncDict['ATuncR'].append(0.0)
	UncDict['ATAuncR'].append(0.0)
	    	
    # First - has it had an DPTround set to 1?
    # Second - check if its a .0
    # AND - is it in an offending Deck?
    # AND - is it in an offending YR?
    if (UncDict['DPTround'][Counter] == 1):

        # It has so append VARuncR accordingly
#        print('Found a DPTround')
	UncDict['DPTuncR'].append(RoundUnc)
	UncDict['DPTAuncR'].append(RoundUnc)

    # Now check if its a .0 and from an offending deck
    # given it some leaway for floating point shenannigans - numbers only recorded to one decimal place anyway
    elif ((abs(ExtDict['DPT'][Counter] - np.floor(ExtDict['DPT'][Counter])) < 0.05) & \
	  (UncDict['DCK'][Counter] in DPT_dict)):

        # This DPT is a ROUND!!!
	if (UncDict['YR'][Counter] in DPT_dict[UncDict['DCK'][Counter]]):    
#            print('Found a DPT DCK round')
	    UncDict['DPTuncR'].append(RoundUnc)
	    UncDict['DPTAuncR'].append(RoundUnc)
            
	# Otherwise it isn't    
	else:
	    UncDict['DPTuncR'].append(0.0)
	    UncDict['DPTAuncR'].append(0.0)
 
    # Otherwise it isn't    
    else:
	UncDict['DPTuncR'].append(0.0)
	UncDict['DPTAuncR'].append(0.0)
    
    # Now append either a 0.0 VARuncR to other variables or an equivalent derived from AT and DPT 
    # VAP, SHU do not depend on AT
    # CRH, CWB and DPD depend on AT and DPT
    UncDict['VAPuncR'].append(0.0)
    UncDict['VAPAuncR'].append(0.0)
    UncDict['SHUuncR'].append(0.0)
    UncDict['SHUAuncR'].append(0.0)
    UncDict['CRHuncR'].append(0.0)
    UncDict['CRHAuncR'].append(0.0)
    UncDict['CWBuncR'].append(0.0)
    UncDict['CWBAuncR'].append(0.0)
    UncDict['DPDuncR'].append(0.0)
    UncDict['DPDAuncR'].append(0.0)

    # If the DPTuncR is set then do some calculating
    if (UncDict['DPTuncR'][Counter] > 0.0):
    
        # For VAP (only depends on DPT) derive from DPT
	# Ok so AT is used to get a provisional wet bulb to test for ice bulb - not including uncertainty in this bit.
        e_unc = ch.vap((UncDict['DPTtbc'][Counter] + RoundUnc),UncDict['ATtbc'][Counter],ClimP,roundit=False) - UncDict['VAPtbc'][Counter]
        UncDict['VAPuncR'][Counter] = e_unc
        UncDict['VAPAuncR'][Counter] = e_unc
        
	# For SHU (only depends on DPT) derive from VAP
        q_unc = ch.sh_from_vap((UncDict['VAPtbc'][Counter] + e_unc),ClimP,roundit=False) - UncDict['SHUtbc'][Counter]
        UncDict['SHUuncR'][Counter] = q_unc
        UncDict['SHUAuncR'][Counter] = q_unc
	
	# If ATuncR is also set then apply both
	if (UncDict['ATuncR'][Counter] > 0.0):
	    
	    # For CRH (depends on both DPT and AT) derive from DPT and AT in opposing directions to maximise
	    crh_unc = abs(ch.rh((UncDict['DPTtbc'][Counter] - RoundUnc),(UncDict['ATtbc'][Counter] + RoundUnc),ClimP,roundit=False) - UncDict['CRHtbc'][Counter])
            UncDict['CRHuncR'][Counter] = crh_unc
            UncDict['CRHAuncR'][Counter] = crh_unc	    
	    
	    # For CWB (depends on both DPT and AT) derive from DPT and AT
	    cwb_unc = abs(ch.wb((UncDict['DPTtbc'][Counter] - RoundUnc),(UncDict['ATtbc'][Counter] + RoundUnc),ClimP,roundit=False) - UncDict['CWBtbc'][Counter])
            UncDict['CWBuncR'][Counter] = cwb_unc
            UncDict['CWBAuncR'][Counter] = cwb_unc	    
	    
	    # For DPD (depends on both DPT and AT)derive from DPT and AT
            UncDict['DPDuncR'][Counter] = RoundUncComb
            UncDict['DPDAuncR'][Counter] = RoundUncComb	    

	# Only DPT is set 
	else:

	    # For CRH (depends on both DPT and AT) derive from DPT and AT in opposing directions to maximise
	    crh_unc = abs(ch.rh((UncDict['DPTtbc'][Counter] - RoundUnc),UncDict['ATtbc'][Counter],ClimP,roundit=False) - UncDict['CRHtbc'][Counter])
            UncDict['CRHuncR'][Counter] = crh_unc
            UncDict['CRHAuncR'][Counter] = crh_unc	    

	    # For CWB (depends on both DPT and AT) derive from DPT and AT
	    cwb_unc = abs(ch.wb((UncDict['DPTtbc'][Counter] - RoundUnc),UncDict['ATtbc'][Counter],ClimP,roundit=False) - UncDict['CWBtbc'][Counter])
            UncDict['CWBuncR'][Counter] = cwb_unc
            UncDict['CWBAuncR'][Counter] = cwb_unc	    
	    
	    # For DPD (depends on both DPT and AT) derive from DPT and AT
            UncDict['DPDuncR'][Counter] = RoundUnc
            UncDict['DPDAuncR'][Counter] = RoundUnc	    	

    # If the DPTuncR is not set but the ATuncR is then do some calculating	
    elif (UncDict['ATuncR'][Counter] > 0.0):	

	# For CRH (depends on both DPT and AT) derive from DPT and AT in opposing directions to maximise
	crh_unc = abs(ch.rh(UncDict['DPTtbc'][Counter],(UncDict['ATtbc'][Counter] + RoundUnc),ClimP,roundit=False) - UncDict['CRHtbc'][Counter])
        UncDict['CRHuncR'][Counter] = crh_unc
        UncDict['CRHAuncR'][Counter] = crh_unc  	
	
	# For CWB (depends on both DPT and AT) derive from DPT and AT
	cwb_unc = abs(ch.wb(UncDict['DPTtbc'][Counter],(UncDict['ATtbc'][Counter] + RoundUnc),ClimP,roundit=False) - UncDict['CWBtbc'][Counter])
        UncDict['CWBuncR'][Counter] = cwb_unc
        UncDict['CWBAuncR'][Counter] = cwb_unc  	
	
	# For DPD (depends on both DPT and AT) derive from DPT and AT
        UncDict['DPDuncR'][Counter] = RoundUnc
        UncDict['DPDAuncR'][Counter] = RoundUnc	
       
    return UncDict
    
#**********************************************************************************
# MAIN
#**********************************************************************************

def main(argv):
    # INPUT PARAMETERS AS STRINGS!!!!
    year1 = '1973' 
    year2 = '1973'
    month1 = '01' # months must be 01, 02 etc
    month2 = '01'
    typee = 'ERAclimBC'

    try:
        opts, args = getopt.getopt(argv, "hi:",
	                           ["year1=","year2=","month1=","month2=","typee="])
    except getopt.GetoptError:
        print 'Usage (as strings) PlotMetaData_APR2016.py --year1 <1973> --year2 <1973> '+\
	      '--month1 <01> --month2 <12> --typee <ERAclimBC>'
	sys.exit(2)

    for opt, arg in opts:
        if opt == "--year1":
            try:
                year1 = arg
            except:
                sys.exit("Failed: year1 not an integer")
        elif opt == "--year2":
            try:
                year2 = arg
            except:
                sys.exit("Failed: year2 not an integer")
        elif opt == "--month1":
            try:
                month1 = arg
            except:
                sys.exit("Failed: month1 not an integer")
        elif opt == "--month2":
            try:
                month2 = arg
            except:
                sys.exit("Failed: month2 not an integer")
        elif opt == "--typee":
            try:
                typee = arg
            except:
                sys.exit("Failed: typee not a string")

    assert year1 != -999 and year2 != -999, "Year not specified."

    print(year1, year2, month1, month2, typee)
    
    # Open the SLP climatology netCDF file and read in the data
    InSLP = Dataset(SLPClimFilee)
    SLPField = InSLP.variables['p2m_clims'][:] # This is a 73 pentad, 180 lats, 360 lons array

    # Loop through the months
    for yy in range((int(year2)+1)-int(year1)):
        for mm in range((int(month2)+1)-int(month1)):
            print(str(yy+int(year1)),'{:02}'.format(mm+int(month1)))
    
            # Read in the new_suite QC'd MDS data
            TheOrigDict = mrw.ReadMDSstandard("{:4d}".format(yy+int(year1)),"{:02}".format(mm+int(month1)),typee)
            nobs = len(TheOrigDict['shipid'])
	    print(nobs)
	    
	    # Set up TheExtDict to fill/append - provide TheOrigDict to fill in metadata, original values and VARtbc
	    TheExtDict = mrw.MakeExtDict(TheOrigDict)
	    
	    # Set up TheUncDict to fill/append - provide TheExtDict to fill in metadata
	    TheUncDict = mrw.MakeUncDict(TheExtDict)
#	    pdb.set_trace()
	    
            # BIAS CORRECTIONS
            # Loop through each ob
	    for oo in range(nobs):
	        
		# FIRST CHECK THE OB IS VALID OR IT WILL SCREW UP THINGS BIG TIME.
		# THESE BAD OBS SHOULD BE REMOVED DURING QC (AND WILL BE IN FUTURE RUNS!!!)
		# e.g., Jan 1982 ob 44450 AT =99.5
		# ALSO some SHU == 0.0 which is highly unlikely over ocean and totally
		# screws with the adjustments so have also screend for these
		if ((TheExtDict['AT'][oo] < -80.) | (TheExtDict['AT'][oo] > 65.) | 
		    (TheExtDict['DPT'][oo] < -80) | (TheExtDict['DPT'][oo] > 65.) |
		    (int(round(TheExtDict['SHU'][oo]*10.)) == 0)):
		    # Fill in everything as an empty and then move to next iteration of the loop
		    TheExtDict,TheUncDict = FillABad(TheExtDict,TheUncDict,oo)
		    print("Found a Screwy! ",oo,TheExtDict['AT'][oo],TheExtDict['DPT'][oo],TheExtDict['SHU'][oo])
		    continue
		
	        # Pull out the nearest 1x1 pentad climatological SLP for this ob
		#print(oo,TheExtDict['LAT'][oo],TheExtDict['LON'][oo],TheExtDict['MO'][oo],TheExtDict['DY'][oo])
		ClimP = GetClimSLP(SLPField,TheExtDict['LAT'][oo],TheExtDict['LON'][oo],TheExtDict['MO'][oo],TheExtDict['DY'][oo])

                # Now we have a climatological P recalculate shu,vap,crh,cwb and dpd so that we're working with non-rounded values
		# This should hopefully avoid strange things when propogating adjustments and uncertainties through the humidity
		# values which can result in increase/decrease situations because of the rounding
		TheExtDict,TheUncDict = ReCalcHums(TheExtDict,TheUncDict,ClimP,oo)
		
                # Pretend to apply a solar corrections - this may be applied later.
		# Apply to VARslr and add to VARtbc
                TheExtDict,TheUncDict = ApplySolarAdjUnc(TheExtDict,TheUncDict,oo,ClimP)
#		# TEST
#		print("Test Output SLR: ",oo)
#		print(TheExtDict['SHU'][oo],TheExtDict['SHUslr'][oo],TheExtDict['SHUtbc'][oo],TheUncDict['SHUuncSLR'][oo])
#		print(TheExtDict['SHUA'][oo],TheExtDict['SHUAslr'][oo],TheExtDict['SHUAtbc'][oo],TheUncDict['SHUAuncSLR'][oo])

                # Obtain exposure information from EOH or EOT or estimate exposure - assume Buoys and platforma are unventilated screens, 
		# Could use the Josey et al., 1999 apply 30% of adjustment to ships with no info to represent that ~3rd of obs are not ventilated.
		# HOWEVER, assessment of I300 looks more lik 55% of all obs with EOH info are poorly ventilated
                # Apply 3.4% q adjustment to all obs with a screened/unventilated exposure and a 55% of 3.4% to obs with no exposure or
                # estimated exposure and convert across other humidity variables. DO this to orig and solar corrected obs.
		# Apply a catch for 2015 where ALL metadata drops out to avoid big jump in adjustment - grow (3.4*0.55)*1.14
		# This is the ratio of 2014 mean adjustment (with metadata) / 2015 mean adjustment (no metadata)
		# Apply to VARscn and add to VARtbc
                TheExtDict,TheUncDict = ApplyScreenAdjUnc(TheExtDict,TheUncDict,oo,ClimP)
		# TEST
#		print("Test Output SCN: ",oo, TheExtDict['ESTE'][oo])
#		print('Original SLR SCN HGT TBC uncSCN')
#		print('SHU: ',TheExtDict['SHU'][oo],TheExtDict['SHUslr'][oo],TheExtDict['SHUscn'][oo],TheExtDict['SHUtbc'][oo],TheUncDict['SHUuncSCN'][oo])
#		print('SHUA: ',TheExtDict['SHUA'][oo],TheExtDict['SHUAslr'][oo],TheExtDict['SHUAscn'][oo],TheExtDict['SHUAtbc'][oo],TheUncDict['SHUAuncSCN'][oo])
#		print('CRH: ',TheExtDict['CRH'][oo],TheExtDict['CRHslr'][oo],TheExtDict['CRHscn'][oo],TheExtDict['CRHtbc'][oo],TheUncDict['CRHuncSCN'][oo])
#		print('CRHA: ',TheExtDict['CRHA'][oo],TheExtDict['CRHAslr'][oo],TheExtDict['CRHAscn'][oo],TheExtDict['CRHAtbc'][oo],TheUncDict['CRHAuncSCN'][oo])
#		print('DPT: ',TheExtDict['DPT'][oo],TheExtDict['DPTslr'][oo],TheExtDict['DPTscn'][oo],TheExtDict['DPTtbc'][oo],TheUncDict['DPTuncSCN'][oo])
#		print('DPTA: ',TheExtDict['DPTA'][oo],TheExtDict['DPTAslr'][oo],TheExtDict['DPTAscn'][oo],TheExtDict['DPTAtbc'][oo],TheUncDict['DPTAuncSCN'][oo])
#	        pdb.set_trace()

                # Obtain height info from HOB/HOT or estimate height from HOP (almost the same!??? - linear equation) or estimate height from 
                # HOA (linear equation) or estimate height based on platform (ship = 16 to 24 scaling linearly every month between ~16m in 
                # 1973 to ~24m by 2006 (Kent et al., 2007 in: Berry and Kent, 2011), buoy = assume 4m instrument height (howmany?, platform 
                # = 30m?)
                # Use height info, SST (or AT), SLP (or climP), u (or 0.5m if < 0.5, ~3 if missing?) to create an estimated height adjusted 
                # value. Do this to orig and solar/screen corrected obs.
		# Apply to VARhc and add to VARtbc
#		if (oo == 2512):
#		    print(TheExtDict['SST'][oo],TheExtDict['AT'][oo],TheExtDict['SHU'][oo],TheExtDict['W'][oo],TheExtDict['HOA'][oo],TheExtDict['HOB'][oo],TheExtDict['HOT'][oo],TheExtDict['DPT'][oo],TheExtDict['VAP'][oo],TheExtDict['CRH'][oo],TheExtDict['CWB'][oo],TheExtDict['DPD'][oo],ClimP)
#		    print(TheExtDict['SST'][oo],TheExtDict['ATtbc'][oo],TheExtDict['SHUtbc'][oo],TheExtDict['W'][oo],TheExtDict['HOA'][oo],TheExtDict['HOB'][oo],TheExtDict['HOT'][oo],TheExtDict['DPTtbc'][oo],TheExtDict['VAPtbc'][oo],TheExtDict['CRHtbc'][oo],TheExtDict['CWBtbc'][oo],TheExtDict['DPDtbc'][oo],ClimP)
#                    pdb.set_trace()
		TheExtDict,TheUncDict = ApplyHeightAdjUnc(TheExtDict,TheUncDict,oo,ClimP,LocalType)
		# TEST
#		print("Test Output HGT: ",oo)
#		print('Original SLR SCN HGT TBC uncHGT')
#		print('SHU: ',TheExtDict['SHU'][oo],TheExtDict['SHUslr'][oo],TheExtDict['SHUscn'][oo],TheExtDict['SHUhc'][oo],TheExtDict['SHUtbc'][oo],TheUncDict['SHUuncHGT'][oo])
#		print('SHUA: ',TheExtDict['SHUA'][oo],TheExtDict['SHUAslr'][oo],TheExtDict['SHUAscn'][oo],TheExtDict['SHUAhc'][oo],TheExtDict['SHUAtbc'][oo],TheUncDict['SHUAuncHGT'][oo])
#		print('CRH: ',TheExtDict['CRH'][oo],TheExtDict['CRHslr'][oo],TheExtDict['CRHscn'][oo],TheExtDict['CRHhc'][oo],TheExtDict['CRHtbc'][oo],TheUncDict['CRHuncHGT'][oo])
#		print('CRHA: ',TheExtDict['CRHA'][oo],TheExtDict['CRHAslr'][oo],TheExtDict['CRHAscn'][oo],TheExtDict['CRHAhc'][oo],TheExtDict['CRHAtbc'][oo],TheUncDict['CRHAuncHGT'][oo])
#		print('DPT: ',TheExtDict['DPT'][oo],TheExtDict['DPTslr'][oo],TheExtDict['DPTscn'][oo],TheExtDict['DPThc'][oo],TheExtDict['DPTtbc'][oo],TheUncDict['DPTuncHGT'][oo])
#		print('DPTA: ',TheExtDict['DPTA'][oo],TheExtDict['DPTAslr'][oo],TheExtDict['DPTAscn'][oo],TheExtDict['DPTAhc'][oo],TheExtDict['DPTAtbc'][oo],TheUncDict['DPTAuncHGT'][oo])
#		print('AT: ',TheExtDict['AT'][oo],TheExtDict['ATslr'][oo],TheExtDict['ATscn'][oo],TheExtDict['AThc'][oo],TheExtDict['ATtbc'][oo],TheUncDict['ATuncHGT'][oo])
#		print('ATA: ',TheExtDict['ATA'][oo],TheExtDict['ATAslr'][oo],TheExtDict['ATAscn'][oo],TheExtDict['ATAhc'][oo],TheExtDict['ATAtbc'][oo],TheUncDict['ATAuncHGT'][oo])
#	        if ((TheUncDict['SHUuncHGT'][oo] == 0.0) & (TheExtDict['ESTH'][oo] != 10)): # could test AT but when there isn't an SST SST is set to AT so no height adjustment will be made to AT
#		# This was triggered when HOH was actually 10m so no adjustment was applied and therefore no uncertainty!
#		    pdb.set_trace()
		
		# Now that we have applied all of the bias corrections append the completed VARtbc from ExtDict into those in UncDict
		TheUncDict['ATtbc'].append(TheExtDict['ATtbc'][oo])
		TheUncDict['ATAtbc'].append(TheExtDict['ATAtbc'][oo])
		TheUncDict['DPTtbc'].append(TheExtDict['DPTtbc'][oo])
		TheUncDict['DPTAtbc'].append(TheExtDict['DPTAtbc'][oo])
		TheUncDict['SHUtbc'].append(TheExtDict['SHUtbc'][oo])
		TheUncDict['SHUAtbc'].append(TheExtDict['SHUAtbc'][oo])
		TheUncDict['VAPtbc'].append(TheExtDict['VAPtbc'][oo])
		TheUncDict['VAPAtbc'].append(TheExtDict['VAPAtbc'][oo])
		TheUncDict['CRHtbc'].append(TheExtDict['CRHtbc'][oo])
		TheUncDict['CRHAtbc'].append(TheExtDict['CRHAtbc'][oo])
		TheUncDict['CWBtbc'].append(TheExtDict['CWBtbc'][oo])
		TheUncDict['CWBAtbc'].append(TheExtDict['CWBAtbc'][oo])
		TheUncDict['DPDtbc'].append(TheExtDict['DPDtbc'][oo])
		TheUncDict['DPDAtbc'].append(TheExtDict['DPDAtbc'][oo])
		
		# Measurement Uncertainty - apply as for HadISDH.land---------------------------------------------------------------------------------
#	        if (oo >= 111300):
#                    print(oo,TheExtDict['ATtbc'][oo])
#		    pdb.set_trace()
		TheUncDict = ApplyMeasUnc(TheUncDict,oo,ClimP)
		# TEST
#		print("Test Output uncM: ",oo)
#		print(TheUncDict['ATuncM'][oo],TheUncDict['DPTuncM'][oo],TheUncDict['SHUuncM'][oo],TheUncDict['VAPuncM'][oo],TheUncDict['CRHuncM'][oo],TheUncDict['CWBuncM'][oo],TheUncDict['DPDuncM'][oo])
#		print(TheUncDict['ATAuncM'][oo],TheUncDict['DPTAuncM'][oo],TheUncDict['SHUAuncM'][oo],TheUncDict['VAPAuncM'][oo],TheUncDict['CRHAuncM'][oo],TheUncDict['CWBAuncM'][oo],TheUncDict['DPDAuncM'][oo])
#	        pdb.set_trace()
		
		# Rounding Uncertainty
		TheUncDict = ApplyRoundUnc(TheUncDict,TheExtDict,oo,ClimP)		
		# TEST
#		print("Test Output uncR: ",oo)
#		print('AT DPT SHU VAP CRH CWB DPD')
#		print(TheUncDict['ATuncR'][oo],TheUncDict['DPTuncR'][oo],TheUncDict['SHUuncR'][oo],TheUncDict['VAPuncR'][oo],TheUncDict['CRHuncR'][oo],TheUncDict['CWBuncR'][oo],TheUncDict['DPDuncR'][oo])
#		print(TheUncDict['ATAuncR'][oo],TheUncDict['DPTAuncR'][oo],TheUncDict['SHUAuncR'][oo],TheUncDict['VAPAuncR'][oo],TheUncDict['CRHAuncR'][oo],TheUncDict['CWBAuncR'][oo],TheUncDict['DPDAuncR'][oo])
#	        if (TheUncDict['SHUuncR'][oo] > 0.0):
#		    pdb.set_trace()
		
		# Combine the uncertainties assuming uncorrelated WRONG WRONG WRONG DIDILLY WRONG WRONG
		TheUncDict['ATuncT'].append(np.sqrt(TheUncDict['ATuncSLR'][oo]**2 + TheUncDict['ATuncSCN'][oo]**2 + TheUncDict['ATuncHGT'][oo]**2 + TheUncDict['ATuncR'][oo]**2 + TheUncDict['ATuncM'][oo]**2))
		TheUncDict['ATAuncT'].append(np.sqrt(TheUncDict['ATAuncSLR'][oo]**2 + TheUncDict['ATAuncSCN'][oo]**2 + TheUncDict['ATAuncHGT'][oo]**2 + TheUncDict['ATAuncR'][oo]**2 + TheUncDict['ATAuncM'][oo]**2))
		TheUncDict['DPTuncT'].append(np.sqrt(TheUncDict['DPTuncSLR'][oo]**2 + TheUncDict['DPTuncSCN'][oo]**2 + TheUncDict['DPTuncHGT'][oo]**2 + TheUncDict['DPTuncR'][oo]**2 + TheUncDict['DPTuncM'][oo]**2))
		TheUncDict['DPTAuncT'].append(np.sqrt(TheUncDict['DPTAuncSLR'][oo]**2 + TheUncDict['DPTAuncSCN'][oo]**2 + TheUncDict['DPTAuncHGT'][oo]**2 + TheUncDict['DPTAuncR'][oo]**2 + TheUncDict['DPTAuncM'][oo]**2))
		TheUncDict['SHUuncT'].append(np.sqrt(TheUncDict['SHUuncSLR'][oo]**2 + TheUncDict['SHUuncSCN'][oo]**2 + TheUncDict['SHUuncHGT'][oo]**2 + TheUncDict['SHUuncR'][oo]**2 + TheUncDict['SHUuncM'][oo]**2))
		TheUncDict['SHUAuncT'].append(np.sqrt(TheUncDict['SHUAuncSLR'][oo]**2 + TheUncDict['SHUAuncSCN'][oo]**2 + TheUncDict['SHUAuncHGT'][oo]**2 + TheUncDict['SHUAuncR'][oo]**2 + TheUncDict['SHUAuncM'][oo]**2))
		TheUncDict['VAPuncT'].append(np.sqrt(TheUncDict['VAPuncSLR'][oo]**2 + TheUncDict['VAPuncSCN'][oo]**2 + TheUncDict['VAPuncHGT'][oo]**2 + TheUncDict['VAPuncR'][oo]**2 + TheUncDict['VAPuncM'][oo]**2))
		TheUncDict['VAPAuncT'].append(np.sqrt(TheUncDict['VAPAuncSLR'][oo]**2 + TheUncDict['VAPAuncSCN'][oo]**2 + TheUncDict['VAPAuncHGT'][oo]**2 + TheUncDict['VAPAuncR'][oo]**2 + TheUncDict['VAPAuncM'][oo]**2))
		TheUncDict['CRHuncT'].append(np.sqrt(TheUncDict['CRHuncSLR'][oo]**2 + TheUncDict['CRHuncSCN'][oo]**2 + TheUncDict['CRHuncHGT'][oo]**2 + TheUncDict['CRHuncR'][oo]**2 + TheUncDict['CRHuncM'][oo]**2))
		TheUncDict['CRHAuncT'].append(np.sqrt(TheUncDict['CRHAuncSLR'][oo]**2 + TheUncDict['CRHAuncSCN'][oo]**2 + TheUncDict['CRHAuncHGT'][oo]**2 + TheUncDict['CRHAuncR'][oo]**2 + TheUncDict['CRHAuncM'][oo]**2))
		TheUncDict['CWBuncT'].append(np.sqrt(TheUncDict['CWBuncSLR'][oo]**2 + TheUncDict['CWBuncSCN'][oo]**2 + TheUncDict['CWBuncHGT'][oo]**2 + TheUncDict['CWBuncR'][oo]**2 + TheUncDict['CWBuncM'][oo]**2))
		TheUncDict['CWBAuncT'].append(np.sqrt(TheUncDict['CWBAuncSLR'][oo]**2 + TheUncDict['CWBAuncSCN'][oo]**2 + TheUncDict['CWBAuncHGT'][oo]**2 + TheUncDict['CWBAuncR'][oo]**2 + TheUncDict['CWBAuncM'][oo]**2))
		TheUncDict['DPDuncT'].append(np.sqrt(TheUncDict['DPDuncSLR'][oo]**2 + TheUncDict['DPDuncSCN'][oo]**2 + TheUncDict['DPDuncHGT'][oo]**2 + TheUncDict['DPDuncR'][oo]**2 + TheUncDict['DPDuncM'][oo]**2))
		TheUncDict['DPDAuncT'].append(np.sqrt(TheUncDict['DPDAuncSLR'][oo]**2 + TheUncDict['DPDAuncSCN'][oo]**2 + TheUncDict['DPDAuncHGT'][oo]**2 + TheUncDict['DPDAuncR'][oo]**2 + TheUncDict['DPDAuncM'][oo]**2))
		# TEST
#		print("Test Output uncT: ",oo)
#		print('AT DPT SHU VAP CRH CWB DPD')
#		print(TheUncDict['ATuncT'][oo],TheUncDict['DPTuncT'][oo],TheUncDict['SHUuncT'][oo],TheUncDict['VAPuncT'][oo],TheUncDict['CRHuncT'][oo],TheUncDict['CWBuncT'][oo],TheUncDict['DPDuncT'][oo])
#		print(TheUncDict['ATAuncT'][oo],TheUncDict['DPTAuncT'][oo],TheUncDict['SHUAuncT'][oo],TheUncDict['VAPAuncT'][oo],TheUncDict['CRHAuncT'][oo],TheUncDict['CWBAuncT'][oo],TheUncDict['DPDAuncT'][oo])
#	        if (oo == 145621):
#		    pdb.set_trace()

#                if (TheExtDict['ESTE'][oo] != 'U55'):
#                if ((TheExtDict['ESTE'][oo] != 'U55') & (TheExtDict['ESTE'][oo] != 'ASP')):
#                if ((TheExtDict['HOB'][oo] < 0) & ((TheExtDict['HOT'][oo] > 0) | (TheExtDict['HOP'][oo] > 0) | (TheExtDict['HOA'][oo] > 0))):
#                if ((TheExtDict['HOB'][oo] < 0) & ((TheExtDict['HOT'][oo] > 0) | (TheExtDict['HOP'][oo] > 0))):
#                if ((TheExtDict['HOT'][oo] > 0) | (TheExtDict['HOP'][oo] > 0)):
#		    pdb.set_trace()

            # Make sure typee is now BC instead of NBC
	    newtypee = typee[0:7]+typee[8:]
	    LenTypee = len(typee)
	    newtypee = typee[0:(LenTypee-3)]+typee[(LenTypee-2):]+LocalType
	    #pdb.set_trace()
	    
	    # Write out extendeds
            mrw.WriteMDSextended("{:4d}".format(yy+int(year1)),"{:02}".format(mm+int(month1)),newtypee,TheExtDict)
#	    pdb.set_trace()

            # Write out uncertainties
            mrw.WriteMDSuncertainty("{:4d}".format(yy+int(year1)),"{:02}".format(mm+int(month1)),newtypee,TheUncDict)
# 	    pdb.set_trace()

    print("And were done!")
 
if __name__ == '__main__':
    
    main(sys.argv[1:])
