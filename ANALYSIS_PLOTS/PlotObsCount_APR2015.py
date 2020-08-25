#!/usr/local/sci/bin/python
# PYTHON2.7
# 
# Author: Kate Willett
# Created: 23 April 2016
# Last update: 23 April 2016
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/ANALYSIS_PLOTS/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code reads in lists of annual summaries for PT counts (before and after QC) and QC and day/night flags 
# and makes overview plots
#  
# -----------------------
# LIST OF MODULES
# -----------------------
# inbuilt:
# import datetime as dt
# import copy
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
# python2.7 PlotObsCount_APR2016.py
#
# This runs the code, outputs the plots
# 
# -----------------------
# OUTPUT
# -----------------------
# some plots:
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryPTall_ERAclimNBC_APR2016.png
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryPTallDAY_ERAclimNBC_APR2016.png
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryPTallNIGHT_ERAclimNBC_APR2016.png
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryPTgood_ERAclimNBC_APR2016.png
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryPTgoodDAY_ERAclimNBC_APR2016.png
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryPTgoodNIGHT_ERAclimNBC_APR2016.png
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryQCDAY_ERAclimNBC_APR2016.png
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryQCNIGHT_ERAclimNBC_APR2016.png
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
import copy
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

    return np.genfromtxt(FileName, dtype=typee,delimiter=delimee,encoding = 'latin-1') #comments=False) # ReadData


#************************************************************************
# Main
#************************************************************************
ICOADSV = 'I300'
THRESHV = '55'
ITV = 'OBSclim2NBC' # ERAclimNBC, OBSclim1NBC, OBSclim2NBC
NOWMON = 'JAN'
NOWYEAR = '2019'

StartYear = 1973
EndYear = 2018
NYears = (EndYear - StartYear)+1

INDIR = '/data/users/hadkw/WORKING_HADISDH/MARINE/LISTS/'
INFILPT = 'PTTypeMetaDataStats_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR+'.txt'
INFILPTD = 'PTTypeMetaDataStatsDAY_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR+'.txt'
INFILPTN = 'PTTypeMetaDataStatsNIGHT_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR+'.txt'
INFILPTG = 'PTTypeGOODMetaDataStats_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR+'.txt'
INFILPTGD = 'PTTypeGOODMetaDataStatsDAY_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR+'.txt'
INFILPTGN = 'PTTypeGOODMetaDataStatsNIGHT_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR+'.txt'
INFILQC = 'QCMetaDataStats_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR+'.txt'
INFILQCD = 'QCMetaDataStatsDAY_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR+'.txt'
INFILQCN = 'QCMetaDataStatsNIGHT_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR+'.txt'

OUTDIR = '/data/users/hadkw/WORKING_HADISDH/MARINE/IMAGES/'
OutPltPTG = 'SummaryPT_good_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR
OutPltPTGD = 'SummaryPT_DAYgood_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR
OutPltPTGN = 'SummaryPT_NIGHTgood_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR
OutPltPT = 'SummaryPT_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR
OutPltPTD = 'SummaryPT_DAY_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR
OutPltPTN = 'SummaryPT_NIGHT_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR
OutPltQC = 'SummaryQC_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR
OutPltQCD = 'SummaryQC_DAY_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR
OutPltQCN = 'SummaryQC_NIGHT_'+ITV+'_'+ICOADSV+'_'+THRESHV+'_'+NOWMON+NOWYEAR
# Read in Instrument file and populate lists

#typee = ("int","|S17","int","|S37","float","|S16","float","|S16","float","|S16","float","|S16","float","|S16","float",
#                            "|S16","float","|S16","float","|S16","float","|S17","float","|S17","float","|S2")
typee = ("int","|U17","int","|U37","float","|U16","float","|U16","float","|U16","float","|U16","float","|U16","float",
                            "|U16","float","|U16","float","|U16","float","|U17","float","|U17","float","|U2")

delimee = (4,17,9,37,5,16,5,16,5,16,5,16,5,16,5,
                  16,5,16,5,16,5,17,5,17,5,2)

# create empty arrays for instrument type data bundles
Yr = []
nobs = [] # we're looking at all obs, not just those with 'good' data
PT0s = []
PT1s = []
PT2s = []
PT3s = []
PT4s = []
PT5s = []
PT6s = []
PT8s = []
PT9s = []
PT10s = []
PT15s = []

RawData = ReadData(INDIR+INFILPT,typee, delimee)

Yr = np.array(RawData['f0'][0:NYears])
nobs = np.array(RawData['f2'][0:NYears])
PT0s = np.array(RawData['f4'][0:NYears])
PT1s = np.array(RawData['f6'][0:NYears])
PT2s = np.array(RawData['f8'][0:NYears])
PT3s = np.array(RawData['f10'][0:NYears])
PT4s = np.array(RawData['f12'][0:NYears])
PT5s = np.array(RawData['f14'][0:NYears])
PT6s = np.array(RawData['f16'][0:NYears])
PT8s = np.array(RawData['f18'][0:NYears])
PT9s = np.array(RawData['f20'][0:NYears])
PT10s = np.array(RawData['f22'][0:NYears])
PT15s = np.array(RawData['f24'][0:NYears])

# Makes zero values sub zero so that they are not plotted
gPT0s = np.where(PT0s > 0.)[0]
gPT1s = np.where(PT1s > 0.)[0]
gPT2s = np.where(PT2s > 0.)[0]
gPT3s = np.where(PT3s > 0.)[0]
gPT4s = np.where(PT4s > 0.)[0]
gPT5s = np.where(PT5s > 0.)[0]
gPT6s = np.where(PT6s > 0.)[0]
gPT8s = np.where(PT8s > 0.)[0]
gPT9s = np.where(PT9s > 0.)[0]
gPT10s = np.where(PT10s > 0.)[0]
gPT15s = np.where(PT15s > 0.)[0]

# Make plot of instrument types for EOT and EOH over time
gap= 0.04

#PT: 0=US Navy/unknown - usually ship, 1=merchant ship/foreign military, 2=ocean station vessel off station (or unknown loc), 
# 3=ocean station vessel on station, 4=lightship, 5=ship, 6=moored buiy, 7=drifting buoy, 8=ice buoy, 9=ice station, 
# 10=oceanographic station, 11=MBT (bathythermograph), 12=XBT (bathythermograph), 
# 13=Coastal-Marine Automated Network (C-MAN), 14=other coastal/island station, 15=fixed ocean platoform, 16=tide guage, 17=hi res CTD, 18=profiling float, 19=undulating oceanographic recorder, 10=auonomous pinneped bathythermograph (seal?),  21=glider

plt.clf()
fig, ax1 = plt.subplots()
ax1.tick_params(axis='y',direction='in',right=True)
ax1.plot(Yr,nobs,c='black',linestyle='solid',linewidth=2)
i=0
ax1.annotate("TOTAL",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='black')
latest = np.zeros(NYears)
oldlatest=copy.copy(latest)
latest = latest + PT0s
if (len(gPT0s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='hotpink',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='hotpink',edgecolor='none')
i=1
ax1.annotate("0 = US Navy/Unknown - usually ship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='hotpink')
oldlatest=copy.copy(latest)
latest = latest + PT1s
if (len(gPT1s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='deeppink',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='deeppink',edgecolor='none')
i=2
ax1.annotate("1 = merchant ship/foreign military",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='deeppink')
oldlatest=copy.copy(latest)
latest = latest + PT2s
if (len(gPT2s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='red',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='red',edgecolor='none')
i=3
ax1.annotate("2 = ocean vessel off station (or unknown location)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
#pdb.set_trace()
oldlatest=copy.copy(latest)
latest = latest + PT3s
if (len(gPT3s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='darkorange',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='darkorange',edgecolor='none')
#pdb.set_trace()
i=4
ax1.annotate("3 = ocean vessel on stations",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='darkorange')
oldlatest=copy.copy(latest)
latest = latest + PT4s
if (len(gPT4s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='gold',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='gold',edgecolor='none')
i=5
ax1.annotate("4 = lightship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
oldlatest=copy.copy(latest)
latest = latest + PT5s
if (len(gPT5s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='grey',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='grey',edgecolor='none')
i=6
ax1.annotate("5 = ship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')
oldlatest=copy.copy(latest)
latest = latest + PT6s
if (len(gPT6s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='limegreen',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='limegreen',edgecolor='none')
i=7
ax1.annotate("6 = moored buoy",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='limegreen')
oldlatest=copy.copy(latest)
latest = latest + PT8s
if (len(gPT8s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='olivedrab',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='olivedrab',edgecolor='none')
i=8
ax1.annotate("8 = ice buoy",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='olivedrab')
#oldlatest=copy.copy(latest)
#latest = latest + PT9s
#if (len(gPT9s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='blue',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='blue')
#i=9
#ax1.annotate("9 = ice station",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
#oldlatest=copy.copy(latest)
#latest = latest + PT10s
#if (len(gPT10s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='indigo',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='indigo')
#i=10
#ax1.annotate("10 = oceanographic stations",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
#oldlatest=copy.copy(latest)
#latest = latest + PT15s
#if (len(gPT15s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='violet',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='violet')
#i=11
#ax1.annotate("15 = fixed ocean platform",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')

ax1.set_xlabel('Year')
ax1.set_ylabel('No. of Obs (PT Type proportional)', color='black')
ax1.set_ylim(0,5000000)
ax1.set_xlim(StartYear-1,EndYear+1)

plt.tight_layout()

plt.savefig(OUTDIR+OutPltPT+".eps")
plt.savefig(OUTDIR+OutPltPT+".png")
#pdb.set_trace()

# create empty arrays for instrument type data bundles
Yr = []
nobs = [] # we're looking at all obs, not just those with 'good' data
PT0s = []
PT1s = []
PT2s = []
PT3s = []
PT4s = []
PT5s = []
PT6s = []
PT8s = []
PT9s = []
PT10s = []
PT15s = []

RawData = ReadData(INDIR+INFILPTD,typee, delimee)

Yr = np.array(RawData['f0'][0:NYears])
nobs = np.array(RawData['f2'][0:NYears])
PT0s = np.array(RawData['f4'][0:NYears])
PT1s = np.array(RawData['f6'][0:NYears])
PT2s = np.array(RawData['f8'][0:NYears])
PT3s = np.array(RawData['f10'][0:NYears])
PT4s = np.array(RawData['f12'][0:NYears])
PT5s = np.array(RawData['f14'][0:NYears])
PT6s = np.array(RawData['f16'][0:NYears])
PT8s = np.array(RawData['f18'][0:NYears])
PT9s = np.array(RawData['f20'][0:NYears])
PT10s = np.array(RawData['f22'][0:NYears])
PT15s = np.array(RawData['f24'][0:NYears])

# Makes zero values sub zero so that they are not plotted
gPT0s = np.where(PT0s > 0.)[0]
gPT1s = np.where(PT1s > 0.)[0]
gPT2s = np.where(PT2s > 0.)[0]
gPT3s = np.where(PT3s > 0.)[0]
gPT4s = np.where(PT4s > 0.)[0]
gPT5s = np.where(PT5s > 0.)[0]
gPT6s = np.where(PT6s > 0.)[0]
gPT8s = np.where(PT8s > 0.)[0]
gPT9s = np.where(PT9s > 0.)[0]
gPT10s = np.where(PT10s > 0.)[0]
gPT15s = np.where(PT15s > 0.)[0]

# Make plot of instrument types for EOT and EOH over time
gap= 0.04

#PT: 0=US Navy/unknown - usually ship, 1=merchant ship/foreign military, 2=ocean station vessel off station (or unknown loc), 
# 3=ocean station vessel on station, 4=lightship, 5=ship, 6=moored buiy, 7=drifting buoy, 8=ice buoy, 9=ice station, 
# 10=oceanographic station, 11=MBT (bathythermograph), 12=XBT (bathythermograph), 
# 13=Coastal-Marine Automated Network (C-MAN), 14=other coastal/island station, 15=fixed ocean platoform, 16=tide guage, 17=hi res CTD, 18=profiling float, 19=undulating oceanographic recorder, 10=auonomous pinneped bathythermograph (seal?),  21=glider

plt.clf()
fig, ax1 = plt.subplots()
ax1.tick_params(axis='y',direction='in',right=True)
ax1.plot(Yr,nobs,c='black',linestyle='solid',linewidth=2)
i=0
ax1.annotate("TOTAL DAY",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='black')
latest = np.zeros(NYears)
oldlatest=copy.copy(latest)
latest = latest + PT0s
if (len(gPT0s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='hotpink',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='hotpink',edgecolor='none')
i=1
ax1.annotate("0 = US Navy/Unknown - usually ship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='hotpink')
oldlatest=copy.copy(latest)
latest = latest + PT1s
if (len(gPT1s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='deeppink',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='deeppink',edgecolor='none')
i=2
ax1.annotate("1 = merchant ship/foreign military",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='deeppink')
oldlatest=copy.copy(latest)
latest = latest + PT2s
if (len(gPT2s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='red',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='red',edgecolor='none')
i=3
ax1.annotate("2 = ocean vessel off station (or unknown location)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
#pdb.set_trace()
oldlatest=copy.copy(latest)
latest = latest + PT3s
if (len(gPT3s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='darkorange',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='darkorange',edgecolor='none')
#pdb.set_trace()
i=4
ax1.annotate("3 = ocean vessel on stations",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='darkorange')
oldlatest=copy.copy(latest)
latest = latest + PT4s
if (len(gPT4s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='gold',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='gold',edgecolor='none')
i=5
ax1.annotate("4 = lightship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
oldlatest=copy.copy(latest)
latest = latest + PT5s
if (len(gPT5s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='grey',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='grey',edgecolor='none')
i=6
ax1.annotate("5 = ship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')
oldlatest=copy.copy(latest)
latest = latest + PT6s
if (len(gPT6s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='limegreen',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='limegreen',edgecolor='none')
i=7
ax1.annotate("6 = moored buoy",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='limegreen')
oldlatest=copy.copy(latest)
latest = latest + PT8s
if (len(gPT8s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='olivedrab',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='olivedrab',edgecolor='none')
i=8
ax1.annotate("8 = ice buoy",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='olivedrab')
#oldlatest=copy.copy(latest)
#latest = latest + PT9s
#if (len(gPT9s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='blue',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='blue')
#i=9
#ax1.annotate("9 = ice station",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
#oldlatest=copy.copy(latest)
#latest = latest + PT10s
#if (len(gPT10s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='indigo',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='indigo')
#i=10
#ax1.annotate("10 = oceanographic stations",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
#oldlatest=copy.copy(latest)
#latest = latest + PT15s
#if (len(gPT15s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='violet',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='violet')
#i=11
#ax1.annotate("15 = fixed ocean platform",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')

ax1.set_xlabel('Year')
ax1.set_ylabel('No. of Obs (PT Type proportional)', color='black')
ax1.set_ylim(0,5000000)
ax1.set_xlim(StartYear-1,EndYear+1)

plt.tight_layout()

plt.savefig(OUTDIR+OutPltPTD+".eps")
plt.savefig(OUTDIR+OutPltPTD+".png")

# create empty arrays for instrument type data bundles
Yr = []
nobs = [] # we're looking at all obs, not just those with 'good' data
PT0s = []
PT1s = []
PT2s = []
PT3s = []
PT4s = []
PT5s = []
PT6s = []
PT8s = []
PT9s = []
PT10s = []
PT15s = []

RawData = ReadData(INDIR+INFILPTN,typee, delimee)

Yr = np.array(RawData['f0'][0:NYears])
nobs = np.array(RawData['f2'][0:NYears])
PT0s = np.array(RawData['f4'][0:NYears])
PT1s = np.array(RawData['f6'][0:NYears])
PT2s = np.array(RawData['f8'][0:NYears])
PT3s = np.array(RawData['f10'][0:NYears])
PT4s = np.array(RawData['f12'][0:NYears])
PT5s = np.array(RawData['f14'][0:NYears])
PT6s = np.array(RawData['f16'][0:NYears])
PT8s = np.array(RawData['f18'][0:NYears])
PT9s = np.array(RawData['f20'][0:NYears])
PT10s = np.array(RawData['f22'][0:NYears])
PT15s = np.array(RawData['f24'][0:NYears])

# Makes zero values sub zero so that they are not plotted
gPT0s = np.where(PT0s > 0.)[0]
gPT1s = np.where(PT1s > 0.)[0]
gPT2s = np.where(PT2s > 0.)[0]
gPT3s = np.where(PT3s > 0.)[0]
gPT4s = np.where(PT4s > 0.)[0]
gPT5s = np.where(PT5s > 0.)[0]
gPT6s = np.where(PT6s > 0.)[0]
gPT8s = np.where(PT8s > 0.)[0]
gPT9s = np.where(PT9s > 0.)[0]
gPT10s = np.where(PT10s > 0.)[0]
gPT15s = np.where(PT15s > 0.)[0]

# Make plot of instrument types for EOT and EOH over time
gap= 0.04

#PT: 0=US Navy/unknown - usually ship, 1=merchant ship/foreign military, 2=ocean station vessel off station (or unknown loc), 
# 3=ocean station vessel on station, 4=lightship, 5=ship, 6=moored buiy, 7=drifting buoy, 8=ice buoy, 9=ice station, 
# 10=oceanographic station, 11=MBT (bathythermograph), 12=XBT (bathythermograph), 
# 13=Coastal-Marine Automated Network (C-MAN), 14=other coastal/island station, 15=fixed ocean platoform, 16=tide guage, 17=hi res CTD, 18=profiling float, 19=undulating oceanographic recorder, 10=auonomous pinneped bathythermograph (seal?),  21=glider

plt.clf()
fig, ax1 = plt.subplots()
ax1.tick_params(axis='y',direction='in',right=True)
ax1.plot(Yr,nobs,c='black',linestyle='solid',linewidth=2)
i=0
ax1.annotate("TOTAL NIGHT",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='black')
latest = np.zeros(NYears)
oldlatest=copy.copy(latest)
latest = latest + PT0s
if (len(gPT0s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='hotpink',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='hotpink',edgecolor='none')
i=1
ax1.annotate("0 = US Navy/Unknown - usually ship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='hotpink')
oldlatest=copy.copy(latest)
latest = latest + PT1s
if (len(gPT1s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='deeppink',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='deeppink',edgecolor='none')
i=2
ax1.annotate("1 = merchant ship/foreign military",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='deeppink')
oldlatest=copy.copy(latest)
latest = latest + PT2s
if (len(gPT2s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='red',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='red',edgecolor='none')
i=3
ax1.annotate("2 = ocean vessel off station (or unknown location)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
#pdb.set_trace()
oldlatest=copy.copy(latest)
latest = latest + PT3s
if (len(gPT3s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='darkorange',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='darkorange',edgecolor='none')
#pdb.set_trace()
i=4
ax1.annotate("3 = ocean vessel on stations",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='darkorange')
oldlatest=copy.copy(latest)
latest = latest + PT4s
if (len(gPT4s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='gold',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='gold',edgecolor='none')
i=5
ax1.annotate("4 = lightship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
oldlatest=copy.copy(latest)
latest = latest + PT5s
if (len(gPT5s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='grey',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='grey',edgecolor='none')
i=6
ax1.annotate("5 = ship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')
oldlatest=copy.copy(latest)
latest = latest + PT6s
if (len(gPT6s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='limegreen',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='limegreen',edgecolor='none')
i=7
ax1.annotate("6 = moored buoy",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='limegreen')
oldlatest=copy.copy(latest)
latest = latest + PT8s
if (len(gPT8s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='olivedrab',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='olivedrab',edgecolor='none')
i=8
ax1.annotate("8 = ice buoy",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='olivedrab')
#oldlatest=copy.copy(latest)
#latest = latest + PT9s
#if (len(gPT9s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='blue',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='blue')
#i=9
#ax1.annotate("9 = ice station",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
#oldlatest=copy.copy(latest)
#latest = latest + PT10s
#if (len(gPT10s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='indigo',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='indigo')
#i=10
#ax1.annotate("10 = oceanographic stations",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
#oldlatest=copy.copy(latest)
#latest = latest + PT15s
#if (len(gPT15s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='violet',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='violet')
#i=11
#ax1.annotate("15 = fixed ocean platform",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')

ax1.set_xlabel('Year')
ax1.set_ylabel('No. of Obs (PT Type proportional)', color='black')
ax1.set_ylim(0,5000000)
ax1.set_xlim(StartYear-1,EndYear+1)

plt.tight_layout()

plt.savefig(OUTDIR+OutPltPTN+".eps")
plt.savefig(OUTDIR+OutPltPTN+".png")

# create empty arrays for instrument type data bundles
Yr = []
nobs = [] # we're looking at all obs, not just those with 'good' data
PT0s = []
PT1s = []
PT2s = []
PT3s = []
PT4s = []
PT5s = []
PT6s = []
PT8s = []
PT9s = []
PT10s = []
PT15s = []

RawData = ReadData(INDIR+INFILPTG,typee, delimee)

Yr = np.array(RawData['f0'][0:NYears])
nobs = np.array(RawData['f2'][0:NYears])
PT0s = np.array(RawData['f4'][0:NYears])
PT1s = np.array(RawData['f6'][0:NYears])
PT2s = np.array(RawData['f8'][0:NYears])
PT3s = np.array(RawData['f10'][0:NYears])
PT4s = np.array(RawData['f12'][0:NYears])
PT5s = np.array(RawData['f14'][0:NYears])
PT6s = np.array(RawData['f16'][0:NYears])
PT8s = np.array(RawData['f18'][0:NYears])
PT9s = np.array(RawData['f20'][0:NYears])
PT10s = np.array(RawData['f22'][0:NYears])
PT15s = np.array(RawData['f24'][0:NYears])

# Makes zero values sub zero so that they are not plotted
gPT0s = np.where(PT0s > 0.)[0]
gPT1s = np.where(PT1s > 0.)[0]
gPT2s = np.where(PT2s > 0.)[0]
gPT3s = np.where(PT3s > 0.)[0]
gPT4s = np.where(PT4s > 0.)[0]
gPT5s = np.where(PT5s > 0.)[0]
gPT6s = np.where(PT6s > 0.)[0]
gPT8s = np.where(PT8s > 0.)[0]
gPT9s = np.where(PT9s > 0.)[0]
gPT10s = np.where(PT10s > 0.)[0]
gPT15s = np.where(PT15s > 0.)[0]

# Make plot of instrument types for EOT and EOH over time
gap= 0.04

#PT: 0=US Navy/unknown - usually ship, 1=merchant ship/foreign military, 2=ocean station vessel off station (or unknown loc), 
# 3=ocean station vessel on station, 4=lightship, 5=ship, 6=moored buiy, 7=drifting buoy, 8=ice buoy, 9=ice station, 
# 10=oceanographic station, 11=MBT (bathythermograph), 12=XBT (bathythermograph), 
# 13=Coastal-Marine Automated Network (C-MAN), 14=other coastal/island station, 15=fixed ocean platoform, 16=tide guage, 17=hi res CTD, 18=profiling float, 19=undulating oceanographic recorder, 10=auonomous pinneped bathythermograph (seal?),  21=glider

plt.clf()
fig, ax1 = plt.subplots()
ax1.tick_params(axis='y',direction='in',right=True)
ax1.plot(Yr,nobs,c='black',linestyle='solid',linewidth=2)
i=0
ax1.annotate("TOTAL GOOD",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='black')
latest = np.zeros(NYears)
oldlatest=copy.copy(latest)
latest = latest + PT0s
if (len(gPT0s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='hotpink',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='hotpink',edgecolor='none')
i=1
ax1.annotate("0 = US Navy/Unknown - usually ship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='hotpink')
oldlatest=copy.copy(latest)
latest = latest + PT1s
if (len(gPT1s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='deeppink',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='deeppink',edgecolor='none')
i=2
ax1.annotate("1 = merchant ship/foreign military",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='deeppink')
oldlatest=copy.copy(latest)
latest = latest + PT2s
if (len(gPT2s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='red',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='red',edgecolor='none')
i=3
ax1.annotate("2 = ocean vessel off station (or unknown location)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
#pdb.set_trace()
oldlatest=copy.copy(latest)
latest = latest + PT3s
if (len(gPT3s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='darkorange',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='darkorange',edgecolor='none')
#pdb.set_trace()
i=4
ax1.annotate("3 = ocean vessel on stations",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='darkorange')
oldlatest=copy.copy(latest)
latest = latest + PT4s
if (len(gPT4s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='gold',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='gold',edgecolor='none')
i=5
ax1.annotate("4 = lightship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
oldlatest=copy.copy(latest)
latest = latest + PT5s
if (len(gPT5s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='grey',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='grey',edgecolor='none')
i=6
ax1.annotate("5 = ship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')
oldlatest=copy.copy(latest)
latest = latest + PT6s
if (len(gPT6s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='limegreen',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='limegreen',edgecolor='none')
i=7
ax1.annotate("6 = moored buoy",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='limegreen')
oldlatest=copy.copy(latest)
latest = latest + PT8s
if (len(gPT8s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='olivedrab',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='olivedrab',edgecolor='none')
i=8
ax1.annotate("8 = ice buoy",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='olivedrab')
#oldlatest=copy.copy(latest)
#latest = latest + PT9s
#if (len(gPT9s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='blue',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='blue')
#i=9
#ax1.annotate("9 = ice station",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
#oldlatest=copy.copy(latest)
#latest = latest + PT10s
#if (len(gPT10s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='indigo',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='indigo')
#i=10
#ax1.annotate("10 = oceanographic stations",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
#oldlatest=copy.copy(latest)
#latest = latest + PT15s
#if (len(gPT15s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='violet',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='violet')
#i=11
#ax1.annotate("15 = fixed ocean platform",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')

ax1.set_xlabel('Year')
ax1.set_ylabel('No. of Obs (PT Type proportional)', color='black')
ax1.set_ylim(0,5000000)
ax1.set_xlim(StartYear-1,EndYear+1)

plt.tight_layout()

plt.savefig(OUTDIR+OutPltPTG+".eps")
plt.savefig(OUTDIR+OutPltPTG+".png")

# create empty arrays for instrument type data bundles
Yr = []
nobs = [] # we're looking at all obs, not just those with 'good' data
PT0s = []
PT1s = []
PT2s = []
PT3s = []
PT4s = []
PT5s = []
PT6s = []
PT8s = []
PT9s = []
PT10s = []
PT15s = []

RawData = ReadData(INDIR+INFILPTGD,typee, delimee)

Yr = np.array(RawData['f0'][0:NYears])
nobs = np.array(RawData['f2'][0:NYears])
PT0s = np.array(RawData['f4'][0:NYears])
PT1s = np.array(RawData['f6'][0:NYears])
PT2s = np.array(RawData['f8'][0:NYears])
PT3s = np.array(RawData['f10'][0:NYears])
PT4s = np.array(RawData['f12'][0:NYears])
PT5s = np.array(RawData['f14'][0:NYears])
PT6s = np.array(RawData['f16'][0:NYears])
PT8s = np.array(RawData['f18'][0:NYears])
PT9s = np.array(RawData['f20'][0:NYears])
PT10s = np.array(RawData['f22'][0:NYears])
PT15s = np.array(RawData['f24'][0:NYears])

# Makes zero values sub zero so that they are not plotted
gPT0s = np.where(PT0s > 0.)[0]
gPT1s = np.where(PT1s > 0.)[0]
gPT2s = np.where(PT2s > 0.)[0]
gPT3s = np.where(PT3s > 0.)[0]
gPT4s = np.where(PT4s > 0.)[0]
gPT5s = np.where(PT5s > 0.)[0]
gPT6s = np.where(PT6s > 0.)[0]
gPT8s = np.where(PT8s > 0.)[0]
gPT9s = np.where(PT9s > 0.)[0]
gPT10s = np.where(PT10s > 0.)[0]
gPT15s = np.where(PT15s > 0.)[0]

# Make plot of instrument types for EOT and EOH over time
gap= 0.04

#PT: 0=US Navy/unknown - usually ship, 1=merchant ship/foreign military, 2=ocean station vessel off station (or unknown loc), 
# 3=ocean station vessel on station, 4=lightship, 5=ship, 6=moored buiy, 7=drifting buoy, 8=ice buoy, 9=ice station, 
# 10=oceanographic station, 11=MBT (bathythermograph), 12=XBT (bathythermograph), 
# 13=Coastal-Marine Automated Network (C-MAN), 14=other coastal/island station, 15=fixed ocean platoform, 16=tide guage, 17=hi res CTD, 18=profiling float, 19=undulating oceanographic recorder, 10=auonomous pinneped bathythermograph (seal?),  21=glider

plt.clf()
fig, ax1 = plt.subplots()
ax1.tick_params(axis='y',direction='in',right=True)
ax1.plot(Yr,nobs,c='black',linestyle='solid',linewidth=2)
i=0
ax1.annotate("TOTAL GOOD DAY",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='black')
latest = np.zeros(NYears)
oldlatest=copy.copy(latest)
latest = latest + PT0s
if (len(gPT0s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='hotpink',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='hotpink',edgecolor='none')
i=1
ax1.annotate("0 = US Navy/Unknown - usually ship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='hotpink')
oldlatest=copy.copy(latest)
latest = latest + PT1s
if (len(gPT1s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='deeppink',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='deeppink',edgecolor='none')
i=2
ax1.annotate("1 = merchant ship/foreign military",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='deeppink')
oldlatest=copy.copy(latest)
latest = latest + PT2s
if (len(gPT2s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='red',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='red',edgecolor='none')
i=3
ax1.annotate("2 = ocean vessel off station (or unknown location)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
#pdb.set_trace()
oldlatest=copy.copy(latest)
latest = latest + PT3s
if (len(gPT3s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='darkorange',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='darkorange',edgecolor='none')
#pdb.set_trace()
i=4
ax1.annotate("3 = ocean vessel on stations",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='darkorange')
oldlatest=copy.copy(latest)
latest = latest + PT4s
if (len(gPT4s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='gold',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='gold',edgecolor='none')
i=5
ax1.annotate("4 = lightship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
oldlatest=copy.copy(latest)
latest = latest + PT5s
if (len(gPT5s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='grey',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='grey',edgecolor='none')
i=6
ax1.annotate("5 = ship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')
oldlatest=copy.copy(latest)
latest = latest + PT6s
if (len(gPT6s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='limegreen',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='limegreen',edgecolor='none')
i=7
ax1.annotate("6 = moored buoy",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='limegreen')
oldlatest=copy.copy(latest)
latest = latest + PT8s
if (len(gPT8s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='olivedrab',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='olivedrab',edgecolor='none')
i=8
ax1.annotate("8 = ice buoy",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='olivedrab')
#oldlatest=copy.copy(latest)
#latest = latest + PT9s
#if (len(gPT9s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='blue',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='blue')
#i=9
#ax1.annotate("9 = ice station",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
#oldlatest=copy.copy(latest)
#latest = latest + PT10s
#if (len(gPT10s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='indigo',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='indigo')
#i=10
#ax1.annotate("10 = oceanographic stations",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
#oldlatest=copy.copy(latest)
#latest = latest + PT15s
#if (len(gPT15s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='violet',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='violet')
#i=11
#ax1.annotate("15 = fixed ocean platform",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')

ax1.set_xlabel('Year')
ax1.set_ylabel('No. of Obs (PT Type proportional)', color='black')
ax1.set_ylim(0,5000000)
ax1.set_xlim(StartYear-1,EndYear+1)

plt.tight_layout()

plt.savefig(OUTDIR+OutPltPTGD+".eps")
plt.savefig(OUTDIR+OutPltPTGD+".png")

# create empty arrays for instrument type data bundles
Yr = []
nobs = [] # we're looking at all obs, not just those with 'good' data
PT0s = []
PT1s = []
PT2s = []
PT3s = []
PT4s = []
PT5s = []
PT6s = []
PT8s = []
PT9s = []
PT10s = []
PT15s = []

RawData = ReadData(INDIR+INFILPTGN,typee, delimee)

Yr = np.array(RawData['f0'][0:NYears])
nobs = np.array(RawData['f2'][0:NYears])
PT0s = np.array(RawData['f4'][0:NYears])
PT1s = np.array(RawData['f6'][0:NYears])
PT2s = np.array(RawData['f8'][0:NYears])
PT3s = np.array(RawData['f10'][0:NYears])
PT4s = np.array(RawData['f12'][0:NYears])
PT5s = np.array(RawData['f14'][0:NYears])
PT6s = np.array(RawData['f16'][0:NYears])
PT8s = np.array(RawData['f18'][0:NYears])
PT9s = np.array(RawData['f20'][0:NYears])
PT10s = np.array(RawData['f22'][0:NYears])
PT15s = np.array(RawData['f24'][0:NYears])

# Makes zero values sub zero so that they are not plotted
gPT0s = np.where(PT0s > 0.)[0]
gPT1s = np.where(PT1s > 0.)[0]
gPT2s = np.where(PT2s > 0.)[0]
gPT3s = np.where(PT3s > 0.)[0]
gPT4s = np.where(PT4s > 0.)[0]
gPT5s = np.where(PT5s > 0.)[0]
gPT6s = np.where(PT6s > 0.)[0]
gPT8s = np.where(PT8s > 0.)[0]
gPT9s = np.where(PT9s > 0.)[0]
gPT10s = np.where(PT10s > 0.)[0]
gPT15s = np.where(PT15s > 0.)[0]

# Make plot of instrument types for EOT and EOH over time
gap= 0.04

#PT: 0=US Navy/unknown - usually ship, 1=merchant ship/foreign military, 2=ocean station vessel off station (or unknown loc), 
# 3=ocean station vessel on station, 4=lightship, 5=ship, 6=moored buiy, 7=drifting buoy, 8=ice buoy, 9=ice station, 
# 10=oceanographic station, 11=MBT (bathythermograph), 12=XBT (bathythermograph), 
# 13=Coastal-Marine Automated Network (C-MAN), 14=other coastal/island station, 15=fixed ocean platoform, 16=tide guage, 17=hi res CTD, 18=profiling float, 19=undulating oceanographic recorder, 10=auonomous pinneped bathythermograph (seal?),  21=glider

plt.clf()
fig, ax1 = plt.subplots()
ax1.tick_params(axis='y',direction='in',right=True)
ax1.plot(Yr,nobs,c='black',linestyle='solid',linewidth=2)
i=0
ax1.annotate("TOTAL GOOD NIGHT",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='black')
latest = np.zeros(NYears)
oldlatest=copy.copy(latest)
latest = latest + PT0s
if (len(gPT0s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='hotpink',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='hotpink',edgecolor='none')
i=1
ax1.annotate("0 = US Navy/Unknown - usually ship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='hotpink')
oldlatest=copy.copy(latest)
latest = latest + PT1s
if (len(gPT1s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='deeppink',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='deeppink',edgecolor='none')
i=2
ax1.annotate("1 = merchant ship/foreign military",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='deeppink')
oldlatest=copy.copy(latest)
latest = latest + PT2s
if (len(gPT2s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='red',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='red',edgecolor='none')
i=3
ax1.annotate("2 = ocean vessel off station (or unknown location)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
#pdb.set_trace()
oldlatest=copy.copy(latest)
latest = latest + PT3s
if (len(gPT3s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='darkorange',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='darkorange',edgecolor='none')
#pdb.set_trace()
i=4
ax1.annotate("3 = ocean vessel on stations",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='darkorange')
oldlatest=copy.copy(latest)
latest = latest + PT4s
if (len(gPT4s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='gold',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='gold',edgecolor='none')
i=5
ax1.annotate("4 = lightship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
oldlatest=copy.copy(latest)
latest = latest + PT5s
if (len(gPT5s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='grey',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='grey',edgecolor='none')
i=6
ax1.annotate("5 = ship",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')
oldlatest=copy.copy(latest)
latest = latest + PT6s
if (len(gPT6s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='limegreen',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='limegreen',edgecolor='none')
i=7
ax1.annotate("6 = moored buoy",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='limegreen')
oldlatest=copy.copy(latest)
latest = latest + PT8s
if (len(gPT8s) > 0):
    #ax1.plot(Yr,(latest/100.)*nobs,c='olivedrab',linestyle='solid',linewidth=1)
    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='olivedrab',edgecolor='none')
i=8
ax1.annotate("8 = ice buoy",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='olivedrab')
#oldlatest=copy.copy(latest)
#latest = latest + PT9s
#if (len(gPT9s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='blue',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='blue')
#i=9
#ax1.annotate("9 = ice station",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
#oldlatest=copy.copy(latest)
#latest = latest + PT10s
#if (len(gPT10s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='indigo',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='indigo')
#i=10
#ax1.annotate("10 = oceanographic stations",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
#oldlatest=copy.copy(latest)
#latest = latest + PT15s
#if (len(gPT15s) > 0):
#    #ax1.plot(Yr,(latest/100.)*nobs,c='violet',linestyle='solid',linewidth=1)
#    ax1.fill_between(Yr,(oldlatest/100.)*nobs,(latest/100.)*nobs,facecolor='violet')
#i=11
#ax1.annotate("15 = fixed ocean platform",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')

ax1.set_xlabel('Year')
ax1.set_ylabel('No. of Obs (PT Type proportional)', color='black')
ax1.set_ylim(0,5000000)
ax1.set_xlim(StartYear-1,EndYear+1)

plt.tight_layout()

plt.savefig(OUTDIR+OutPltPTGN+".eps")
plt.savefig(OUTDIR+OutPltPTGN+".png")

#pdb.set_trace()

# Read in Instrument file and populate lists
typee = ("int","|S17","int","|S17","float","|S18","float","|S20","float","|S21","float","|S22","float","|S20","float",
                            "|S21","float","|S22","float","|S22","float","|S23","float","|S21","float","|S24","float","|S2")

delimee = (4,17,9,17,5,18,5,20,5,21,5,22,5,20,5,
                  21,5,22,5,22,5,23,5,21,5,24,5,2)

# create empty arrays for instrument type data bundles
Yr = []
nobs = [] # we're looking at all obs, not just those with 'good' data
PT0s = []
PT1s = []
PT2s = []
PT3s = []
PT4s = []
PT5s = []
PT6s = []
PT8s = []
PT9s = []
PT10s = []
PT15s = []

RawData = ReadData(INDIR+INFILQC,typee, delimee)

Yr = np.array(RawData['f0'][0:NYears])
nobs = np.array(RawData['f4'][0:NYears])
PT0s = np.array(RawData['f6'][0:NYears])
PT1s = np.array(RawData['f8'][0:NYears])
PT2s = np.array(RawData['f10'][0:NYears])
PT3s = np.array(RawData['f12'][0:NYears])
PT4s = np.array(RawData['f14'][0:NYears])
PT5s = np.array(RawData['f16'][0:NYears])
PT6s = np.array(RawData['f18'][0:NYears])
PT8s = np.array(RawData['f20'][0:NYears])
PT9s = np.array(RawData['f22'][0:NYears])
PT10s = np.array(RawData['f24'][0:NYears])
PT15s = np.array(RawData['f26'][0:NYears])

# Makes zero values sub zero so that they are not plotted
gPT0s = np.where(PT0s > 0.)[0]
gPT1s = np.where(PT1s > 0.)[0]
gPT2s = np.where(PT2s > 0.)[0]
gPT3s = np.where(PT3s > 0.)[0]
gPT4s = np.where(PT4s > 0.)[0]
gPT5s = np.where(PT5s > 0.)[0]
gPT6s = np.where(PT6s > 0.)[0]
gPT8s = np.where(PT8s > 0.)[0]
gPT9s = np.where(PT9s > 0.)[0]
gPT10s = np.where(PT10s > 0.)[0]
gPT15s = np.where(PT15s > 0.)[0]

# Make plot of instrument types for EOT and EOH over time
gap= 0.04

plt.clf()
fig, ax1 = plt.subplots()
ax1.tick_params(axis='y',direction='in',right=True)
plt.ylim(0,30.)
ax1.plot(Yr,nobs,c='black',linestyle='solid',linewidth=3)
i=0
ax1.annotate("BADs",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='black')
latest = np.zeros(NYears)
ax1.plot(Yr[gPT0s],PT0s[gPT0s],c='hotpink',linestyle='dotted',linewidth=2)
i=1
ax1.annotate("track check (dotted)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='hotpink')
ax1.plot(Yr[gPT1s],PT1s[gPT1s],c='deeppink',linestyle='dashed',linewidth=2)
i=2
#ax1.annotate("ATbud = buddy check (AT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='deeppink')
ax1.annotate("T buddy check (dashed)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='deeppink')
ax1.plot(Yr[gPT2s],PT2s[gPT2s],c='red',linestyle='dashed',linewidth=2)
i=3
#ax1.annotate("ATclim = climatology check (AT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
ax1.annotate("T climatology check (dashed)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
ax1.plot(Yr[gPT3s],PT3s[gPT3s],c='darkorange',linestyle='dotted',linewidth=2)
i=4
#ax1.annotate("ATround = rounding flag (AT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='darkorange')
ax1.annotate("T whole number flag (dotted)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='darkorange')
ax1.plot(Yr[gPT4s],PT4s[gPT4s],c='gold',linestyle='solid',linewidth=2)
i=5
#ax1.annotate("ATrep = repeated value check (AT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
ax1.annotate("T repeated value check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
ax1.plot(Yr[gPT5s],PT5s[gPT5s],c='grey',linestyle='solid',linewidth=2)
i=6
#ax1.annotate("DPTbud = buddy check (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')
ax1.annotate("Td buddy check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')
ax1.plot(Yr[gPT6s],PT6s[gPT6s],c='limegreen',linestyle='solid',linewidth=2)
i=7
#ax1.annotate("DPTclim = climatology check (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='limegreen')
ax1.annotate("Td climatology check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='limegreen')
ax1.plot(Yr[gPT8s],PT8s[gPT8s],c='olivedrab',linestyle='solid',linewidth=2)
i=8
#ax1.annotate("DPTssat = supersaturation (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='olivedrab')
ax1.annotate("Td supersaturation check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='olivedrab')
ax1.plot(Yr[gPT9s],PT9s[gPT9s],c='blue',linestyle='dotted',linewidth=2)
i=9
#ax1.annotate("DPTround = rounding flag (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
ax1.annotate("Td whole number flag (dotted)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
ax1.plot(Yr[gPT10s],PT10s[gPT10s],c='indigo',linestyle='solid',linewidth=2)
i=10
#ax1.annotate("DPTrep = repeated value (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
ax1.annotate("Td repeated value check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
ax1.plot(Yr[gPT15s],PT15s[gPT15s],c='violet',linestyle='solid',linewidth=2)
i=11
#ax1.annotate("DPTrepsat = repeated saturation check (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')
ax1.annotate("Td repeated saturation check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')

ax1.set_xlabel('Year')
ax1.set_ylabel('% of Obs with QC flag', color='black')
#ax1.set_ylim(0,3500000)
ax1.set_xlim(StartYear-1,EndYear+1)

plt.tight_layout()

plt.savefig(OUTDIR+OutPltQC+".eps")
plt.savefig(OUTDIR+OutPltQC+".png")

# create empty arrays for instrument type data bundles
Yr = []
nobs = [] # we're looking at all obs, not just those with 'good' data
PT0s = []
PT1s = []
PT2s = []
PT3s = []
PT4s = []
PT5s = []
PT6s = []
PT8s = []
PT9s = []
PT10s = []
PT15s = []

RawData = ReadData(INDIR+INFILQCD,typee, delimee)

Yr = np.array(RawData['f0'][0:NYears])
nobs = np.array(RawData['f4'][0:NYears])
PT0s = np.array(RawData['f6'][0:NYears])
PT1s = np.array(RawData['f8'][0:NYears])
PT2s = np.array(RawData['f10'][0:NYears])
PT3s = np.array(RawData['f12'][0:NYears])
PT4s = np.array(RawData['f14'][0:NYears])
PT5s = np.array(RawData['f16'][0:NYears])
PT6s = np.array(RawData['f18'][0:NYears])
PT8s = np.array(RawData['f20'][0:NYears])
PT9s = np.array(RawData['f22'][0:NYears])
PT10s = np.array(RawData['f24'][0:NYears])
PT15s = np.array(RawData['f26'][0:NYears])

# Makes zero values sub zero so that they are not plotted
gPT0s = np.where(PT0s > 0.)[0]
gPT1s = np.where(PT1s > 0.)[0]
gPT2s = np.where(PT2s > 0.)[0]
gPT3s = np.where(PT3s > 0.)[0]
gPT4s = np.where(PT4s > 0.)[0]
gPT5s = np.where(PT5s > 0.)[0]
gPT6s = np.where(PT6s > 0.)[0]
gPT8s = np.where(PT8s > 0.)[0]
gPT9s = np.where(PT9s > 0.)[0]
gPT10s = np.where(PT10s > 0.)[0]
gPT15s = np.where(PT15s > 0.)[0]

# Make plot of instrument types for EOT and EOH over time
gap= 0.04

plt.clf()
fig, ax1 = plt.subplots()
ax1.tick_params(axis='y',direction='in',right=True)
plt.ylim(0,30.)
ax1.plot(Yr,nobs,c='black',linestyle='solid',linewidth=3)
i=0
ax1.annotate("BADs DAY",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='black')
latest = np.zeros(NYears)
ax1.plot(Yr[gPT0s],PT0s[gPT0s],c='hotpink',linestyle='dotted',linewidth=2)
i=1
ax1.annotate("track check (dotted)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='hotpink')
ax1.plot(Yr[gPT1s],PT1s[gPT1s],c='deeppink',linestyle='dashed',linewidth=2)
i=2
#ax1.annotate("ATbud = buddy check (AT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='deeppink')
ax1.annotate("T buddy check (dashed)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='deeppink')
ax1.plot(Yr[gPT2s],PT2s[gPT2s],c='red',linestyle='dashed',linewidth=2)
i=3
#ax1.annotate("ATclim = climatology check (AT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
ax1.annotate("T climatology check (dashed)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
ax1.plot(Yr[gPT3s],PT3s[gPT3s],c='darkorange',linestyle='dotted',linewidth=2)
i=4
#ax1.annotate("ATround = rounding flag (AT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='darkorange')
ax1.annotate("T whole number flag (dotted)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='darkorange')
ax1.plot(Yr[gPT4s],PT4s[gPT4s],c='gold',linestyle='solid',linewidth=2)
i=5
#ax1.annotate("ATrep = repeated value check (AT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
ax1.annotate("T repeated value check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
ax1.plot(Yr[gPT5s],PT5s[gPT5s],c='grey',linestyle='solid',linewidth=2)
i=6
#ax1.annotate("DPTbud = buddy check (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')
ax1.annotate("Td buddy check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')
ax1.plot(Yr[gPT6s],PT6s[gPT6s],c='limegreen',linestyle='solid',linewidth=2)
i=7
#ax1.annotate("DPTclim = climatology check (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='limegreen')
ax1.annotate("Td climatology check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='limegreen')
ax1.plot(Yr[gPT8s],PT8s[gPT8s],c='olivedrab',linestyle='solid',linewidth=2)
i=8
#ax1.annotate("DPTssat = supersaturation (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='olivedrab')
ax1.annotate("Td supersaturation check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='olivedrab')
ax1.plot(Yr[gPT9s],PT9s[gPT9s],c='blue',linestyle='dotted',linewidth=2)
i=9
#ax1.annotate("DPTround = rounding flag (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
ax1.annotate("Td whole number flag (dotted)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
ax1.plot(Yr[gPT10s],PT10s[gPT10s],c='indigo',linestyle='solid',linewidth=2)
i=10
#ax1.annotate("DPTrep = repeated value (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
ax1.annotate("Td repeated value check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
ax1.plot(Yr[gPT15s],PT15s[gPT15s],c='violet',linestyle='solid',linewidth=2)
i=11
#ax1.annotate("DPTrepsat = repeated saturation check (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')
ax1.annotate("Td repeated saturation check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')

ax1.set_xlabel('Year')
ax1.set_ylabel('% of Obs with QC flag', color='black')
#ax1.set_ylim(0,3500000)
ax1.set_xlim(StartYear-1,EndYear+1)

plt.tight_layout()

plt.savefig(OUTDIR+OutPltQCD+".eps")
plt.savefig(OUTDIR+OutPltQCD+".png")

# create empty arrays for instrument type data bundles
Yr = []
nobs = [] # we're looking at all obs, not just those with 'good' data
PT0s = []
PT1s = []
PT2s = []
PT3s = []
PT4s = []
PT5s = []
PT6s = []
PT8s = []
PT9s = []
PT10s = []
PT15s = []

RawData = ReadData(INDIR+INFILQCN,typee, delimee)

Yr = np.array(RawData['f0'][0:NYears])
nobs = np.array(RawData['f4'][0:NYears])
PT0s = np.array(RawData['f6'][0:NYears])
PT1s = np.array(RawData['f8'][0:NYears])
PT2s = np.array(RawData['f10'][0:NYears])
PT3s = np.array(RawData['f12'][0:NYears])
PT4s = np.array(RawData['f14'][0:NYears])
PT5s = np.array(RawData['f16'][0:NYears])
PT6s = np.array(RawData['f18'][0:NYears])
PT8s = np.array(RawData['f20'][0:NYears])
PT9s = np.array(RawData['f22'][0:NYears])
PT10s = np.array(RawData['f24'][0:NYears])
PT15s = np.array(RawData['f26'][0:NYears])

# Makes zero values sub zero so that they are not plotted
gPT0s = np.where(PT0s > 0.)[0]
gPT1s = np.where(PT1s > 0.)[0]
gPT2s = np.where(PT2s > 0.)[0]
gPT3s = np.where(PT3s > 0.)[0]
gPT4s = np.where(PT4s > 0.)[0]
gPT5s = np.where(PT5s > 0.)[0]
gPT6s = np.where(PT6s > 0.)[0]
gPT8s = np.where(PT8s > 0.)[0]
gPT9s = np.where(PT9s > 0.)[0]
gPT10s = np.where(PT10s > 0.)[0]
gPT15s = np.where(PT15s > 0.)[0]

# Make plot of instrument types for EOT and EOH over time
gap= 0.04

plt.clf()
fig, ax1 = plt.subplots()
ax1.tick_params(axis='y',direction='in',right=True)
plt.ylim(0,30.)
ax1.plot(Yr,nobs,c='black',linestyle='solid',linewidth=3)
i=0
ax1.annotate("BADs NIGHT",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='black')
latest = np.zeros(NYears)
ax1.plot(Yr[gPT0s],PT0s[gPT0s],c='hotpink',linestyle='dotted',linewidth=2)
i=1
ax1.annotate("track check (dotted)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='hotpink')
ax1.plot(Yr[gPT1s],PT1s[gPT1s],c='deeppink',linestyle='dashed',linewidth=2)
i=2
#ax1.annotate("ATbud = buddy check (AT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='deeppink')
ax1.annotate("T buddy check (dashed)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='deeppink')
ax1.plot(Yr[gPT2s],PT2s[gPT2s],c='red',linestyle='dashed',linewidth=2)
i=3
#ax1.annotate("ATclim = climatology check (AT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
ax1.annotate("T climatology check (dashed)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
ax1.plot(Yr[gPT3s],PT3s[gPT3s],c='darkorange',linestyle='dotted',linewidth=2)
i=4
#ax1.annotate("ATround = rounding flag (AT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='darkorange')
ax1.annotate("T whole number flag (dotted)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='darkorange')
ax1.plot(Yr[gPT4s],PT4s[gPT4s],c='gold',linestyle='solid',linewidth=2)
i=5
#ax1.annotate("ATrep = repeated value check (AT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
ax1.annotate("T repeated value check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
ax1.plot(Yr[gPT5s],PT5s[gPT5s],c='grey',linestyle='solid',linewidth=2)
i=6
#ax1.annotate("DPTbud = buddy check (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')
ax1.annotate("Td buddy check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')
ax1.plot(Yr[gPT6s],PT6s[gPT6s],c='limegreen',linestyle='solid',linewidth=2)
i=7
#ax1.annotate("DPTclim = climatology check (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='limegreen')
ax1.annotate("Td climatology check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='limegreen')
ax1.plot(Yr[gPT8s],PT8s[gPT8s],c='olivedrab',linestyle='solid',linewidth=2)
i=8
#ax1.annotate("DPTssat = supersaturation (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='olivedrab')
ax1.annotate("Td supersaturation check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='olivedrab')
ax1.plot(Yr[gPT9s],PT9s[gPT9s],c='blue',linestyle='dotted',linewidth=2)
i=9
#ax1.annotate("DPTround = rounding flag (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
ax1.annotate("Td whole number flag (dotted)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
ax1.plot(Yr[gPT10s],PT10s[gPT10s],c='indigo',linestyle='solid',linewidth=2)
i=10
#ax1.annotate("DPTrep = repeated value (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
ax1.annotate("Td repeated value check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
ax1.plot(Yr[gPT15s],PT15s[gPT15s],c='violet',linestyle='solid',linewidth=2)
i=11
#ax1.annotate("DPTrepsat = repeated saturation check (DPT)",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')
ax1.annotate("Td repeated saturation check",xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='violet')

ax1.set_xlabel('Year')
ax1.set_ylabel('% of Obs with QC flag', color='black')
#ax1.set_ylim(0,3500000)
ax1.set_xlim(StartYear-1,EndYear+1)

plt.tight_layout()

plt.savefig(OUTDIR+OutPltQCN+".eps")
plt.savefig(OUTDIR+OutPltQCN+".png")

#pdb.set_trace()

print("And were done")

#************************************************************************
