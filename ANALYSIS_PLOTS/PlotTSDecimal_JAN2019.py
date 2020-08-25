#!/usr/local/sci/bin/python
# PYTHON3
# 
# Author: Kate Willett
# Created: 07 Jan 2019
# Last update: 07 Jan 2019
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/EUSTACE_SST_MAT/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code reads in the list of frerquencies for AT and DPT for each decimal place for each year and plots
# a two panel time series with a line for each decimal 
#
# We are only really interested in 0 and 5 so for clarity the other numbers are the same colour.
#  
# -----------------------
# LIST OF MODULES
# -----------------------
# inbuilt:
# import datetime as dt
## Folling two lines should be uncommented if using with SPICE or screen
## import matplotlib
## matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import numpy as np
# from matplotlib.dates import date2num,num2date
# import sys, os
# import sys, getopt
# from scipy.optimize import curve_fit,fsolve,leastsq
# from scipy import pi,sqrt,exp
# from scipy.special import erf
# import scipy.stats
# from math import sqrt,pi
# import struct
# import pdb # pdb.set_trace() or c 
#
# Kates:
# import MDS_basic_KATE as MDStool
#
# -----------------------
# DATA
# -----------------------
# /data/local/hadkw/HADCRUH2/MARINE/LISTS/
#
# -----------------------
# HOW TO RUN THE CODE
# -----------------------
# check the desired bits are uncommented/commented (filepaths etc)
#
# # First load up python 3 which is currently:
# module load scitools/experimental-current
# python PlotTSDecimal_JAN2019.py
#
# This runs the code, outputs the plots
# 
# -----------------------
# OUTPUT
# -----------------------
# some plots:
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryDecimal_OBSclim2NBC_I300_55_JAN2019.png
# 
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
# 
# Version 1 (07 Jan 2019)
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
#************************************************************************
#                                 START
#************************************************************************
import datetime as dt
# Folling two lines should be uncommented if using with SPICE or screen
## import matplotlib
## matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import date2num,num2date
import sys, os
import sys, getopt
from scipy.optimize import curve_fit,fsolve,leastsq
from scipy import pi,sqrt,exp
from scipy.special import erf
import scipy.stats
from math import sqrt,pi
import struct
import pdb # pdb.set_trace() or c 

#*************************************************************************
# READDATA
#*************************************************************************
def ReadData(FileName,typee,delimee):
    ''' Use numpy genfromtxt reading to read in all rows from a complex array '''
    ''' Need to specify format as it is complex '''
    ''' outputs an array of tuples that in turn need to be subscripted by their names defaults f0...f8 '''

    return np.genfromtxt(FileName, dtype=typee,delimiter=delimee,comments=False) # ReadData


#************************************************************************
# Main
#************************************************************************
source  = 'I300_55' # ICOADS main source and threshold choice
switch  = 'ships' # 'all', 'ships', 'buoys'
ittype   = 'OBSclim2NBC' 
nowmon  = 'JAN'
nowyear = '2019'

StYr = 1973
EdYr = 2017
NYr = (EdYr-StYr)+1

INDIR    = '/data/local/hadkw/HADCRUH2/MARINE/LISTS/'
INFILAT  = 'DecimalFreqStatsAT_'+source+'_'+switch+'_'+ittype+'_'+nowmon+nowyear+'.txt'
INFILDPT = 'DecimalFreqStatsDPT_'+source+'_'+switch+'_'+ittype+'_'+nowmon+nowyear+'.txt'

OUTDIR = '/data/local/hadkw/HADCRUH2/MARINE/IMAGES/'
OutPlt = 'DecimalFreqTS2panel_'+source+'_'+switch+'_'+ittype+'_'+nowmon+nowyear

# create empty arrays for decimal data bundles
Yr   = []
nobs = [] # we're looking at all obs, not just those with 'good' data
AT0s = []
AT1s = []
AT2s = []
AT3s = []
AT4s = []
AT5s = []
AT6s = []
AT7s = []
AT8s = []
AT9s = []

DPT0s = []
DPT1s = []
DPT2s = []
DPT3s = []
DPT4s = []
DPT5s = []
DPT6s = []
DPT7s = []
DPT8s = []
DPT9s = []

#typee='unicode'
#typee = ('U4','U18',
#	 'U8','U14',
#	 'U6','U17',
#	 'U6','U17',
#	 'U6','U17',
#	 'U6','U17',
#	 'U6','U17',
#	 'U6','U17',
#	 'U6','U17',
#	 'U6','U17',
#	 'U6','U17',
#	 'U6','U17')
typee = ("int","|S5","|S3","|S3","|S7", # year
	 "int", 			# nobs
	 "|S4","int","|S2","float",	# 0
	 "|S7","int","|S2","float",	# 1
	 "|S7","int","|S2","float",	# 2
	 "|S7","int","|S2","float",	# 3
	 "|S7","int","|S2","float",	# 4
	 "|S7","int","|S2","float",	# 5
	 "|S7","int","|S2","float",	# 6
	 "|S7","int","|S2","float",	# 7
	 "|S7","int","|S2","float",	# 8
	 "|S7","int","|S2","float",	# 9
	 "|S2")

#delimee = (4,18,8,14,6,17,6,17,6,17,6,17,6,17,6,17,6,17,6,17,6,17,6,3)
delimee = (4,5,3,3,7,
	   8,
	   4,8,2,6,
	   7,8,2,6,
	   7,8,2,6,
	   7,8,2,6,
	   7,8,2,6,
	   7,8,2,6,
	   7,8,2,6,
	   7,8,2,6,
	   7,8,2,6,
	   7,8,2,6,
	   2)

#pdb.set_trace()

# Read in AT Decimal file and populate lists
RawData = ReadData(INDIR+INFILAT,typee,delimee)

Yr   = np.array(RawData['f0'][0:NYr])
nobs = np.array(RawData['f5'][0:NYr])
AT0s = np.array(RawData['f9'][0:NYr])
AT1s = np.array(RawData['f13'][0:NYr])
AT2s = np.array(RawData['f17'][0:NYr])
AT3s = np.array(RawData['f21'][0:NYr])
AT4s = np.array(RawData['f25'][0:NYr])
AT5s = np.array(RawData['f29'][0:NYr])
AT6s = np.array(RawData['f33'][0:NYr])
AT7s = np.array(RawData['f37'][0:NYr])
AT8s = np.array(RawData['f41'][0:NYr])
AT9s = np.array(RawData['f45'][0:NYr])

# Makes zero values sub zero so that they are not plotted
gAT0s = np.where(AT0s > 0.)[0]
gAT1s = np.where(AT1s > 0.)[0]
gAT2s = np.where(AT2s > 0.)[0]
gAT3s = np.where(AT3s > 0.)[0]
gAT4s = np.where(AT4s > 0.)[0]
gAT5s = np.where(AT5s > 0.)[0]
gAT6s = np.where(AT6s > 0.)[0]
gAT7s = np.where(AT7s > 0.)[0]
gAT8s = np.where(AT8s > 0.)[0]
gAT9s = np.where(AT9s > 0.)[0]

# Read in DPT Decimal file and populate lists
RawData = ReadData(INDIR+INFILDPT,typee, delimee)

# YEAR and NOBS should be identical to AT
DPT0s = np.array(RawData['f9'][0:NYr])
DPT1s = np.array(RawData['f13'][0:NYr])
DPT2s = np.array(RawData['f17'][0:NYr])
DPT3s = np.array(RawData['f21'][0:NYr])
DPT4s = np.array(RawData['f25'][0:NYr])
DPT5s = np.array(RawData['f29'][0:NYr])
DPT6s = np.array(RawData['f33'][0:NYr])
DPT7s = np.array(RawData['f37'][0:NYr])
DPT8s = np.array(RawData['f41'][0:NYr])
DPT9s = np.array(RawData['f45'][0:NYr])

# Makes zero values sub zero so thDPT they are not plotted
gDPT0s = np.where(DPT0s > 0.)[0]
gDPT1s = np.where(DPT1s > 0.)[0]
gDPT2s = np.where(DPT2s > 0.)[0]
gDPT3s = np.where(DPT3s > 0.)[0]
gDPT4s = np.where(DPT4s > 0.)[0]
gDPT5s = np.where(DPT5s > 0.)[0]
gDPT6s = np.where(DPT6s > 0.)[0]
gDPT7s = np.where(DPT7s > 0.)[0]
gDPT8s = np.where(DPT8s > 0.)[0]
gDPT9s = np.where(DPT9s > 0.)[0]

# Make plot of decimals for AT and DPT over time
gap= 0.04

# New two panel plot
plt.clf()
fig = plt.figure(figsize=(10,5))
ax1 = plt.axes([0.07,0.10,0.41,0.88]) # left, bottom, width, height

ax1.plot(Yr[gAT0s],AT0s[gAT0s],c = 'red',linestyle = 'solid',linewidth = 2)
ax1.plot(Yr[gAT1s],AT1s[gAT1s],c = 'black',linestyle = 'solid',linewidth = 2)
ax1.plot(Yr[gAT2s],AT2s[gAT2s],c = 'black',linestyle = 'solid',linewidth = 2)
ax1.plot(Yr[gAT3s],AT3s[gAT3s],c = 'black',linestyle = 'solid',linewidth = 2)
ax1.plot(Yr[gAT4s],AT4s[gAT4s],c = 'black',linestyle = 'solid',linewidth = 2)
ax1.plot(Yr[gAT5s],AT5s[gAT5s],c = 'blue',linestyle = 'solid',linewidth = 2)
ax1.plot(Yr[gAT6s],AT6s[gAT6s],c = 'black',linestyle = 'solid',linewidth = 2)
ax1.plot(Yr[gAT7s],AT7s[gAT7s],c = 'black',linestyle = 'solid',linewidth = 2)
ax1.plot(Yr[gAT8s],AT8s[gAT8s],c = 'black',linestyle = 'solid',linewidth = 2)
ax1.plot(Yr[gAT9s],AT9s[gAT9s],c = 'black',linestyle = 'solid',linewidth = 2)
ax1.set_xlabel('Year')
ax1.set_ylabel('% of Air Temperatures', color='black')
ax1.set_ylim(0,40)
ax1.set_xlim(StYr-1,EdYr+1)
ax1.annotate("a)",xy=(0.04,0.94),xycoords='axes fraction',size=14,color='black')

ax1.annotate("0s",xy=(0.94,0.90),xycoords='axes fraction',size=14,color='red',horizontalalignment='right')
ax1.annotate("5s",xy=(0.94,0.86),xycoords='axes fraction',size=14,color='blue',horizontalalignment='right')
ax1.annotate("Other",xy=(0.94,0.82),xycoords='axes fraction',size=14,color='black',horizontalalignment='right')

ax2 = plt.axes([0.57,0.10,0.41,0.88]) # left, bottom, width, height
ax2.set_ylabel('% of Dewpoint Temperatures', color='black')
ax2.set_xlabel('Year')
ax2.set_xlim(StYr-1,EdYr+1)
ax2.set_ylim(0,40)
ax2.plot(Yr[gDPT0s],DPT0s[gDPT0s],c = 'red',linestyle = 'solid',linewidth = 2)
ax2.plot(Yr[gDPT1s],DPT1s[gDPT1s],c = 'black',linestyle = 'solid',linewidth = 2)
ax2.plot(Yr[gDPT2s],DPT2s[gDPT2s],c = 'black',linestyle = 'solid',linewidth = 2)
ax2.plot(Yr[gDPT3s],DPT3s[gDPT3s],c = 'black',linestyle = 'solid',linewidth = 2)
ax2.plot(Yr[gDPT4s],DPT4s[gDPT4s],c = 'black',linestyle = 'solid',linewidth = 2)
ax2.plot(Yr[gDPT5s],DPT5s[gDPT5s],c = 'blue',linestyle = 'solid',linewidth = 2)
ax2.plot(Yr[gDPT6s],DPT6s[gDPT6s],c = 'black',linestyle = 'solid',linewidth = 2)
ax2.plot(Yr[gDPT7s],DPT7s[gDPT7s],c = 'black',linestyle = 'solid',linewidth = 2)
ax2.plot(Yr[gDPT8s],DPT8s[gDPT8s],c = 'black',linestyle = 'solid',linewidth = 2)
ax2.plot(Yr[gDPT9s],DPT9s[gDPT9s],c = 'black',linestyle = 'solid',linewidth = 2)

ax2.annotate("b)",xy=(0.94,0.94),xycoords='axes fraction',size=14,color='black',horizontalalignment='left')

ax2.annotate("0s",xy=(0.94,0.90),xycoords='axes fraction',size=14,color='red',horizontalalignment='right')
ax2.annotate("5s",xy=(0.94,0.86),xycoords='axes fraction',size=14,color='blue',horizontalalignment='right')
ax2.annotate("Other",xy=(0.94,0.82),xycoords='axes fraction',size=14,color='black',horizontalalignment='right')

#plt.tight_layout()

#plt.savefig(OUTDIR+OutPlt+".eps")
plt.savefig(OUTDIR+OutPlt+".png")


#pdb.set_trace()

print("And were done")

#************************************************************************
