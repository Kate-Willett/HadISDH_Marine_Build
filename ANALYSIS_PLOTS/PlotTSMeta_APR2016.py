#!/usr/local/sci/bin/python
# PYTHON2.7
# 
# Author: Kate Willett
# Created: 21 April 2016
# Last update: 21 April 2016
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/EUSTACE_SST_MAT/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code reads in lists of annual summaries for instrument type and heights 
# and makes overview plots
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
# from LinearTrends import MedianPairwise - fits linear trend using Median Pairwise
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
# python2.7 PlotTSMeta_APR2016.py
#
# This runs the code, outputs the plots
# 
# -----------------------
# OUTPUT
# -----------------------
# some plots:
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryInstrumentExposure_ships_ERAclimNBC_APR2016.png
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryInstrumentType_ships_ERAclimNBC_APR2016.png
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryHeight_ships_ERAclimNBC_APR2016.png
# 
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
# 
# Version 1 (21 April 2016)
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

INDIR = '/data/local/hadkw/HADCRUH2/MARINE/LISTS/'
INFILH = 'HeightMetaDataStats_ships_OBSclim2NBC_I300_55_JAN2019.txt'
INFILIT = 'InstrTypeMetaDataStats_ships_OBSclim2NBC_I300_55_JAN2019.txt'
INFILIE = 'InstrumentMetaDataStats_ships_OBSclim2NBC_I300_55_JAN2019.txt'

OUTDIR = '/data/local/hadkw/HADCRUH2/MARINE/IMAGES/'
OutPltH = 'SummaryHeight2panel_ships_OBSclim2NBC_I300_55_JAN2019'
OutPltIE = 'SummaryInstrumentExposure_ships_OBSclim2NBC_I300_55_JAN2019'
OutPltIT = 'SummaryInstrumentType_ships_OBSclim2NBC_I300_55_JAN2019'
#OutPltI_EOT = 'SummaryInstrumentType_EOT_ships_ERAclimNBC_APR2016'
#OutPltI_EOH = 'SummaryInstrumentType_EOH_ships_ERAclimNBC_APR2016'

StYr = 1973
EdYr = 2017
NYr = (EdYr-StYr)+1

# create empty arrays for instrument type data bundles
Yr = []
nobs = [] # we're looking at all obs, not just those with 'good' data
TOHTOT = []
T1s = []
T2s = []
T3s = []
TCs = []
TEs = []
THs = []
TPs = []
TTs = []

# Read in Instrument file and populate lists
typee = ("int","|S17","int","|S16","float","|S16","float","|S16","float","|S16","float","|S16","float",
                            "|S16","float","|S16","float","|S16","float","|S16","float","|S2")

delimee = (4,17,9,16,5,16,5,16,5,16,5,16,5,
                  16,5,16,5,16,5,16,5,2)

RawData = ReadData(INDIR+INFILIT,typee, delimee)

Yr = np.array(RawData['f0'][0:NYr])
nobs = np.array(RawData['f2'][0:NYr])
TOHTOT = np.array(RawData['f4'][0:NYr])
T1s = np.array(RawData['f6'][0:NYr])
T2s = np.array(RawData['f8'][0:NYr])
T3s = np.array(RawData['f10'][0:NYr])
TCs = np.array(RawData['f12'][0:NYr])
TEs = np.array(RawData['f14'][0:NYr])
THs = np.array(RawData['f16'][0:NYr])
TPs = np.array(RawData['f18'][0:NYr])
TTs = np.array(RawData['f20'][0:NYr])

# Makes zero values sub zero so that they are not plotted
gTOHs = np.where(TOHTOT > 0.)[0]
gT1s = np.where(T1s > 0.)[0]
gT2s = np.where(T2s > 0.)[0]
gT3s = np.where(T3s > 0.)[0]
gTCs = np.where(TCs > 0.)[0]
gTEs = np.where(TEs > 0.)[0]
gTHs = np.where(THs > 0.)[0]
gTPs = np.where(TPs > 0.)[0]
gTTs = np.where(TTs > 0.)[0]

# Make plot of instrument types for EOT and EOH over time
gap= 0.04

plt.clf()
fig, ax1 = plt.subplots()
ax1.plot(Yr[gTOHs],TOHTOT[gTOHs],c='black',linestyle='solid',linewidth=3,marker = 'o')
i=0
ax1.annotate("TOTAL",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='black')
ax1.plot(Yr[gT1s],T1s[gT1s],c='red',linestyle='solid',linewidth=3,marker = 'o')
i=1
ax1.annotate("1 = hygristor",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
ax1.plot(Yr[gT2s],T2s[gT2s],c='orange',linestyle='solid',linewidth=3,marker = 'o')
i=2
ax1.annotate("2 = chilled mirror",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='orange')
ax1.plot(Yr[gT3s],T3s[gT3s],c='gold',linestyle='solid',linewidth=3,marker = 'o')
i=3
ax1.annotate("3 = other",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
ax1.plot(Yr[gTCs],TCs[gTCs],c='green',linestyle='solid',linewidth=3,marker = 'o')
i=4
ax1.annotate("C = capacitance",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='green')
ax1.plot(Yr[gTEs],TEs[gTEs],c='blue',linestyle='solid',linewidth=3,marker = 'o')
i=5
ax1.annotate("E = electric",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
ax1.plot(Yr[gTHs],THs[gTHs],c='indigo',linestyle='solid',linewidth=3,marker = 'o')
i=6
ax1.annotate("H = hair hygrometer",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
ax1.plot(Yr[gTPs],TPs[gTPs],c='violet',linestyle='solid',linewidth=3,marker = 'o')
i=7
ax1.annotate("P = psychrometer",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')
ax1.plot(Yr[gTTs],TTs[gTTs],c='grey',linestyle='solid',linewidth=3,marker = 'o')
i=8
ax1.annotate("T = torsion",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')

ax1.set_xlabel('Year')
ax1.set_ylabel('% of SHIP Obs with metadata', color='black')
ax1.set_ylim(0,100)
ax1.set_xlim(StYr-1,EdYr+1)

plt.tight_layout()

#plt.savefig(OUTDIR+OutPltIT+".eps")
plt.savefig(OUTDIR+OutPltIT+".png")


# create empty arrays for instrument type data bundles
Yr = []
nobs = [] # we're looking at all obs, not just those with 'good' data
EOHTOT = []
EOHA = []
EOHSGSLW = []
EOHSSNVS = []
EOHUS = []
EOTTOT = []
EOTA = []
EOTSGSLW = []
EOTSSNVS = []
EOTUS = []

# Read in Instrument file and populate lists
typee = ("int","|S17","int","|S16","float","|S16","float","|S22","float","|S22","float","|S17","float",
                            "|S18","float","|S16","float","|S22","float","|S22","float","|S17","float","|S2")

delimee = (4,17,9,16,5,16,5,22,5,22,5,17,5,
                  18,5,16,5,22,5,22,5,17,5,2)

RawData = ReadData(INDIR+INFILIE,typee, delimee)

Yr = np.array(RawData['f0'][0:NYr])
nobs = np.array(RawData['f2'][0:NYr])
EOHTOT = np.array(RawData['f4'][0:NYr])
EOHA = np.array(RawData['f6'][0:NYr])
EOHSGSLW = np.array(RawData['f8'][0:NYr])
EOHSSNVS = np.array(RawData['f10'][0:NYr])
EOHUS = np.array(RawData['f12'][0:NYr])
EOTTOT = np.array(RawData['f14'][0:NYr])
EOTA = np.array(RawData['f16'][0:NYr])
EOTSGSLW = np.array(RawData['f18'][0:NYr])
EOTSSNVS = np.array(RawData['f20'][0:NYr])
EOTUS = np.array(RawData['f22'][0:NYr])

# Makes zero values sub zero so that they are not plotted
gEOH = np.where(EOHTOT > 0.)[0]
gEOT = np.where(EOTTOT > 0.)[0]

# Make plot of instrument types for EOT and EOH over time
gap= 0.04

plt.clf()
fig, ax1 = plt.subplots()
ax1.plot(Yr[gEOH],EOHA[gEOH],c='red',linestyle='solid',linewidth=3,marker = 'o')
ax1.plot(Yr[gEOT],EOTA[gEOT],c='red',linestyle='dashed',linewidth=3,marker = 'o')
i=1
ax1.annotate("A = aspirated screen",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')

ax1.plot(Yr[gEOH],EOHSGSLW[gEOH],c='orange',linestyle='solid',linewidth=3,marker = 'o')
ax1.plot(Yr[gEOT],EOTSGSLW[gEOT],c='orange',linestyle='dashed',linewidth=3,marker = 'o')
i=2
ax1.annotate("SG/SL/W = ship's sling/sling/whirled",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='orange')

ax1.plot(Yr[gEOH],EOHSSNVS[gEOH],c='blue',linestyle='solid',linewidth=3,marker = 'o')
ax1.plot(Yr[gEOT],EOTSSNVS[gEOT],c='blue',linestyle='dashed',linewidth=3,marker = 'o')
i=3
ax1.annotate("S/SN/VS = screen/ship's screen/ventilated screen",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')

ax1.plot(Yr[gEOH],EOHUS[gEOH],c='violet',linestyle='solid',linewidth=3,marker = 'o')
ax1.plot(Yr[gEOT],EOTUS[gEOT],c='violet',linestyle='dashed',linewidth=3,marker = 'o')
i=4
ax1.annotate("US = unscreened",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')

ax1.set_xlabel('Year')
ax1.set_ylabel('% of SHIP Obs with metadata', color='black')
ax1.set_ylim(0,100)
ax1.set_xlim(StYr-1,EdYr+1)
ax1.plot(Yr[gEOH],EOHTOT[gEOH],c = 'black',linestyle = 'solid',linewidth = 3,marker = 'o')
ax1.plot(Yr[gEOT],EOTTOT[gEOT],c = 'black',linestyle = 'dashed',linewidth = 3,marker = 'o')
i=0
ax1.annotate("TOTAL",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='black')

plt.tight_layout()

#plt.savefig(OUTDIR+OutPltIE+".eps")
plt.savefig(OUTDIR+OutPltIE+".png")

# create empty arrays for instrument type data bundles
Yr = []
nobs = [] # we're looking at all obs, not just those with 'good' data
HOBTOT = []
HOBMN = []
HOBSD = []
HOTTOT = []
HOTMN = []
HOTSD = []
HOATOT = []
HOAMN = []
HOASD = []
HOPTOT = []
HOPMN = []
HOPSD = []

# Read in Instrument file and populate lists
typee = ("int","|S17","int","|S16","float","|S2","float","float",
                            "|S16","float","|S2","float","float",             
                            "|S16","float","|S2","float","float",             
                            "|S16","float","|S2","float","float","|S347")             

delimee = (4,17,9,16,5,2,6,6,
                  16,5,2,6,6,
		  16,5,2,6,6,
		  16,5,2,6,6,347)

RawData = ReadData(INDIR+INFILH,typee, delimee)

Yr = np.array(RawData['f0'][0:NYr])
nobs = np.array(RawData['f2'][0:NYr])
HOBTOT = np.array(RawData['f4'][0:NYr])
HOBMN = np.array(RawData['f6'][0:NYr])
HOBSD = np.array(RawData['f7'][0:NYr])
HOTTOT = np.array(RawData['f9'][0:NYr])
HOTMN = np.array(RawData['f11'][0:NYr])
HOTSD = np.array(RawData['f12'][0:NYr])
HOATOT = np.array(RawData['f14'][0:NYr])
HOAMN = np.array(RawData['f16'][0:NYr])
HOASD = np.array(RawData['f17'][0:NYr])
HOPTOT = np.array(RawData['f19'][0:NYr])
HOPMN = np.array(RawData['f21'][0:NYr])
HOPSD = np.array(RawData['f22'][0:NYr])

# Pointers for where there are non-zero values.
gHOB = np.where(HOBTOT > 0.)[0]
gHOT = np.where(HOTTOT > 0.)[0]
gHOA = np.where(HOATOT > 0.)[0]
gHOP = np.where(HOPTOT > 0.)[0]

# Make plot of instrument types for EOT and EOH over time

gap= 0.04

# Old 1 panel plot
#plt.clf()
#fig, ax1 = plt.subplots()
#ax1.plot(Yr[gHOB],HOBTOT[gHOB],c = 'red',linestyle = 'solid',linewidth = 2)
#ax1.plot(Yr[gHOT],HOTTOT[gHOT],c = 'orange',linestyle = 'solid',linewidth = 2)
#ax1.plot(Yr[gHOA],HOATOT[gHOA],c = 'blue',linestyle = 'solid',linewidth = 2)
#ax1.plot(Yr[gHOP],HOPTOT[gHOP],c = 'violet',linestyle = 'solid',linewidth = 2)
#ax1.set_xlabel('Year')
#ax1.set_ylabel('% of SHIP Obs (SOLID)', color='black')
#ax1.set_ylim(0,80)
#ax1.set_xlim(StYr-1,EdYr+1)
#ax2 = ax1.twinx()
#ax2.set_ylim(0,100)
#ax2.plot(Yr[gHOB],HOBMN[gHOB],c='red',linestyle='dashed',linewidth=2)
#ax2.plot(Yr[gHOB],HOBMN[gHOB]+HOBSD[gHOB],c='red',linestyle='dotted',linewidth=2)
#ax2.plot(Yr[gHOB],HOBMN[gHOB]-HOBSD[gHOB],c='red',linestyle='dotted',linewidth=2)
#i=0
#ax2.annotate("HOB = barometer height",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
#ax2.plot(Yr[gHOT],HOTMN[gHOT],c='orange',linestyle='dashed',linewidth=2)
#ax2.plot(Yr[gHOT],HOTMN[gHOT]+HOTSD[gHOT],c='orange',linestyle='dotted',linewidth=2)
#ax2.plot(Yr[gHOT],HOTMN[gHOT]-HOTSD[gHOT],c='orange',linestyle='dotted',linewidth=2)
#i=1
#ax2.annotate("HOT = thermometer height",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='orange')
#ax2.plot(Yr[gHOA],HOAMN[gHOA],c='blue',linestyle='dashed',linewidth=2)
#ax2.plot(Yr[gHOA],HOAMN[gHOA]+HOASD[gHOA],c='blue',linestyle='dotted',linewidth=2)
#ax2.plot(Yr[gHOA],HOAMN[gHOA]-HOASD[gHOA],c='blue',linestyle='dotted',linewidth=2)
#i=2
#ax2.annotate("HOA = anemometer height",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
#ax2.plot(Yr[gHOP],HOPMN[gHOP],c='violet',linestyle='dashed',linewidth=2)
#ax2.plot(Yr[gHOP],HOPMN[gHOP]+HOPSD[gHOP],c='violet',linestyle='dotted',linewidth=2)
#ax2.plot(Yr[gHOP],HOPMN[gHOP]-HOPSD[gHOP],c='violet',linestyle='dotted',linewidth=2)
#i=3
#ax2.annotate("HOP = visual observation height",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')
#
#ax2.set_ylabel('Mean (DASHED), 1 st dev (DOTTED) Height (m)', color='black')
#plt.tight_layout()
#
##plt.savefig(OUTDIR+OutPltH+".eps")
#plt.savefig(OUTDIR+OutPltH+".png")

# New two panel plot
plt.clf()
fig = plt.figure(figsize=(10,5))
ax1 = plt.axes([0.07,0.10,0.41,0.88]) # left, bottom, width, height

ax1.plot(Yr[gHOB],HOBTOT[gHOB],c = 'red',linestyle = 'solid',linewidth = 2)
ax1.plot(Yr[gHOT],HOTTOT[gHOT],c = 'orange',linestyle = 'solid',linewidth = 2)
ax1.plot(Yr[gHOA],HOATOT[gHOA],c = 'blue',linestyle = 'solid',linewidth = 2)
ax1.plot(Yr[gHOP],HOPTOT[gHOP],c = 'violet',linestyle = 'solid',linewidth = 2)
ax1.set_xlabel('Year')
ax1.set_ylabel('% of SHIP Obs (SOLID)', color='black')
ax1.set_ylim(0,80)
ax1.set_xlim(StYr-1,EdYr+1)
ax1.annotate("a)",xy=(0.04,0.94),xycoords='axes fraction',size=14,color='black')

ax2 = plt.axes([0.57,0.10,0.41,0.88]) # left, bottom, width, height
ax2.set_ylabel('Mean (solid), 1 st dev (dotted) Height (m)', color='black')
ax2.set_xlabel('Year')
ax2.set_xlim(StYr-1,EdYr+1)
ax2.set_ylim(0,70)
ax2.plot(Yr[gHOB],HOBMN[gHOB],c='red',linestyle='solid',linewidth=2)
# NOTE: By using alpha = 0.5 to make shading transparent we cannot save as eps!!! 
ax2.fill_between(Yr[gHOB],HOBMN[gHOB]+HOBSD[gHOB],HOBMN[gHOB]-HOBSD[gHOB],facecolor='red',edgecolor=None,alpha=0.15)
ax2.plot(Yr[gHOT],HOTMN[gHOT],c='orange',linestyle='solid',linewidth=2)
ax2.fill_between(Yr[gHOT],HOTMN[gHOT]+HOTSD[gHOT],HOTMN[gHOT]-HOTSD[gHOT],facecolor='orange',edgecolor=None,alpha=0.15)
ax2.plot(Yr[gHOA],HOAMN[gHOA],c='blue',linestyle='solid',linewidth=2)
ax2.fill_between(Yr[gHOA],HOAMN[gHOA]+HOASD[gHOA],HOAMN[gHOA]-HOASD[gHOA],facecolor='blue',edgecolor=None,alpha=0.15)
ax2.plot(Yr[gHOP],HOPMN[gHOP],c='violet',linestyle='solid',linewidth=2)
ax2.fill_between(Yr[gHOP],HOPMN[gHOP]+HOPSD[gHOP],HOPMN[gHOP]-HOPSD[gHOP],facecolor='violet',edgecolor=None,alpha=0.15)

ax2.plot(Yr[gHOB],HOBMN[gHOB]+HOBSD[gHOB],c='red',linestyle='dotted',linewidth=2)
ax2.plot(Yr[gHOB],HOBMN[gHOB]-HOBSD[gHOB],c='red',linestyle='dotted',linewidth=2)
ax2.plot(Yr[gHOT],HOTMN[gHOT]+HOTSD[gHOT],c='orange',linestyle='dotted',linewidth=2)
ax2.plot(Yr[gHOT],HOTMN[gHOT]-HOTSD[gHOT],c='orange',linestyle='dotted',linewidth=2)
ax2.plot(Yr[gHOA],HOAMN[gHOA]+HOASD[gHOA],c='blue',linestyle='dotted',linewidth=2)
ax2.plot(Yr[gHOA],HOAMN[gHOA]-HOASD[gHOA],c='blue',linestyle='dotted',linewidth=2)
ax2.plot(Yr[gHOP],HOPMN[gHOP]+HOPSD[gHOP],c='violet',linestyle='dotted',linewidth=2)
ax2.plot(Yr[gHOP],HOPMN[gHOP]-HOPSD[gHOP],c='violet',linestyle='dotted',linewidth=2)

ax2.annotate("b)",xy=(0.04,0.94),xycoords='axes fraction',size=14,color='black')

ax2.annotate("HOB: barometer height",xy=(0.04,0.90),xycoords='axes fraction',size=10,color='red')
ax2.annotate("HOT: thermometer height",xy=(0.04,0.86),xycoords='axes fraction',size=10,color='orange')
ax2.annotate("HOA: anemometer height",xy=(0.04,0.82),xycoords='axes fraction',size=10,color='blue')
ax2.annotate("HOP: visual observation height",xy=(0.04,0.78),xycoords='axes fraction',size=10,color='violet')

#plt.tight_layout()

#plt.savefig(OUTDIR+OutPltH+".eps")
plt.savefig(OUTDIR+OutPltH+".png")


#pdb.set_trace()

print("And were done")

#************************************************************************
