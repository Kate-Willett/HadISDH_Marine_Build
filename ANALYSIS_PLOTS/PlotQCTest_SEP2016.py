#!/usr/local/sci/bin/python
# PYTHON2.7
# 
# Author: Kate Willett
# Created: 22 Sep 2016
# Last update: 22 April 2016
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/ANALYSIS_PLOTS/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code loops through each year/month ascii file, pulls out the obs failing each test and then
# plots histograms of fails as % of total obs for that time period (left axis) total count (right axis):
#	- Absolute AT day for each year and decade, line per test
#	- Absolute AT night for each year and decade, line per test
#	- Absolute AT both for each year and decade, line per test
#	- Absolute DPT day for each year and decade, line per test
#	- Absolute DPT night for each year and decade, line per test
#	- Absolute DPT both for each year and decade, line per test
#	- Absolute SHU day for each year and decade, line per test
#	- Absolute SHU night for each year and decade, line per test
#	- Absolute SHU both for each year and decade, line per test
#	- Absolute CRH day for each year and decade, line per test
#	- Absolute CRH night for each year and decade, line per test
#	- Absolute CRH both for each year and decade, line per test
#	- Anomaly AT day for each year and decade, line per test
#	- Anomaly AT night for each year and decade, line per test
#	- Anomaly AT both for each year and decade, line per test
#	- Anomaly DPT day for each year and decade, line per test
#	- Anomaly DPT night for each year and decade, line per test
#	- Anomaly DPT both for each year and decade, line per test
#	- Anomaly SHU day for each year and decade, line per test
#	- Anomaly SHU night for each year and decade, line per test
#	- Anomaly SHU both for each year and decade, line per test
#	- Anomaly CRH day for each year and decade, line per test
#	- Anomaly CRH night for each year and decade, line per test
#	- Anomaly CRH both for each year and decade, line per test
#
# Its going to require a LOT of memory and take time.
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
# OLD import MDS_basic_KATE as MDStool
# import MDS_RWtools as mrw
#
# -----------------------
# DATA
# -----------------------
# /project/hadobs2/hadisdh/marine/ICOADS.2.5.1/ERAclimNBC/
# /project/hadobs2/hadisdh/marine/ICOADS.2.5.1/OBSclim1NBC/
# /project/hadobs2/hadisdh/marine/ICOADS.2.5.1/OBSclim2NBC/
#
# -----------------------
# HOW TO RUN THE CODE
# -----------------------
# check the desired bits are uncommented/commented (filepaths etc)
# Call key words for type (ERAclimNBC), year start and end, month start and end (default whole year) and variable
# Ideally we would run all vars together to save time but its just tooooooo big
#
# python2.7 PlotQCTest_SEP2016.py --year1 1973 --year2 1973 --month1 1 --month2 1 --typee ERAclimNBC --varee AT 
#
# This runs the code, outputs the plots
# 
# -----------------------
# OUTPUT
# -----------------------
# some plots:
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_DAY_Abs_AT_ERAclimNBC_1973_APR2016.png or 19731981 OBSclim1NBC, OBSclim2NBC
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_NIGHT_Abs_AT_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_BOTH_Abs_AT_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_DAY_Abs_DPT_ERAclimNBC_1973_APR2016.png or 19731981 OBSclim1NBC, OBSclim2NBC
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_NIGHT_Abs_DPT_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_BOTH_Abs_DPT_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_DAY_Abs_SHU_ERAclimNBC_1973_APR2016.png or 19731981 OBSclim1NBC, OBSclim2NBC
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_NIGHT_Abs_SHU_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_BOTH_Abs_SHU_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_DAY_Abs_CRH_ERAclimNBC_1973_APR2016.png or 19731981 OBSclim1NBC, OBSclim2NBC
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_NIGHT_Abs_CRH_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_BOTH_Abs_CRH_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_DAY_Anoms_AT_ERAclimNBC_1973_APR2016.png or 19731981 OBSclim1NBC, OBSclim2NBC
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_NIGHT_Anoms_AT_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_BOTH_Anoms_AT_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_DAY_Anoms_DPT_ERAclimNBC_1973_APR2016.png or 19731981 OBSclim1NBC, OBSclim2NBC
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_NIGHT_Anoms_DPT_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_BOTH_Anoms_DPT_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_DAY_Anoms_SHU_ERAclimNBC_1973_APR2016.png or 19731981 OBSclim1NBC, OBSclim2NBC
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_NIGHT_Anoms_SHU_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_BOTH_Anoms_SHU_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_DAY_Anoms_CRH_ERAclimNBC_1973_APR2016.png or 19731981 OBSclim1NBC, OBSclim2NBC
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_NIGHT_Anoms_CRH_ERAclimNBC_1973_APR2016.png or 19731981
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/SummaryHistQC_BOTH_Anoms_CRH_ERAclimNBC_1973_APR2016.png or 19731981
# 
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
# 
# Version 1 (22 AAeptember 2016)
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

#import MDS_basic_KATE as MDStool
import MDS_RWtools as mrw

#*************************************************************************
# PLOTQCTEST
#*************************************************************************
def PlotQCTest(FileName, WhichVar, WhichVals, WhichPlot, TotalObs, FailTrk, FailClimAT, FailBuddyAT, FailRepAT,
               FailClimDPT, FailBuddyDPT, FailRepDPT, FailRepSatDPT, FailSSatDPT):
    ''' FileName - director path and filename without .eps or .png '''
    ''' WhicVar - AT, DPT, SHU or CRH - so we know what units and titles to use '''
    ''' WhichVals - Abs or Anoms so we know what xtitles to use '''
    ''' WhichPlot - DAY, NIGHT or BOTH so we know what titles to use '''
    ''' TotalObs - Total number of ALL obs in period to calculate percentage frequencies '''
    ''' FailTrk...FailSSatDPT - the nRow by 2Col array (value,day=1) to plot '''
    ''' This code makes a png and/or eps of QC fail frequency by value (anomaly or absolute) '''
    ''' of the chosen variable (AT, DPT, SHU or CRH). '''
    ''' From this we hope to see whether there is a prevelance of low/high value removals '''
    ''' and whether over time there are distinct differences. '''
    ''' We can also compare the plots from different QC versions. '''

    # Which variable are we dealing with? Set up units and axes label strings
    VarStrDict = dict([['AT',['Air Temperature','$^{o}$C']],
                       ['DPT',['Dew Point Temperature','$^{o}$C']],
		       ['SHU',['Specific Humidity','g kg$^{-1}$']],
		       ['CRH',['Relative Humidity','%rh']]])
		       
    ThisVarName = VarStrDict[WhichVar][0]
    ThisVarUnit = VarStrDict[WhichVar][1]
    		       		       
    # Which value type are we dealing with? Set up axes label strings
    if (WhichVals == 'Abs'):
        ThisValType = ''
    else:
        ThisValType = 'anomalies (1981-2010)'	
    
    # Which time period are we dealing with? Set up pointers if necessary
    if (WhichPlot == 'DAY'):
        PlotMe = 0 # plot where it DOES NOT = 0(night)
    elif (WhichPlot == 'NIGHT'):
        PlotMe = 1 # plot where it DOES NOT = 1(day)
    else:
        PlotMe = 100 # plot where it DOES NOT = 100 (all values!)	 
    
    # Establish axes ranges using all elements that have a non-zero length
    xAxMIN = 1000 # a ridiculous value!
    xAxMAX = -1000 # a ridiculous value!
    y1AxMAX = 0 # a ridiculous value!
    
    if (len(FailTrk[np.where(FailTrk[:,1] != PlotMe)[0],0]) > 0):
        xAxMIN = np.min([xAxMIN,np.min(FailTrk[np.where(FailTrk[:,1] != PlotMe)[0],0])])
        xAxMAX = np.max([xAxMAX,np.max(FailTrk[np.where(FailTrk[:,1] != PlotMe)[0],0])])
    print(xAxMIN,xAxMAX)
	
    if (len(FailClimAT[np.where(FailClimAT[:,1] != PlotMe)[0],0]) > 0):
        xAxMIN = np.min([xAxMIN,np.min(FailClimAT[np.where(FailClimAT[:,1] != PlotMe)[0],0])])
        xAxMAX = np.max([xAxMAX,np.max(FailClimAT[np.where(FailClimAT[:,1] != PlotMe)[0],0])])
    print(xAxMIN,xAxMAX)
    
    if (len(FailBuddyAT[np.where(FailBuddyAT[:,1] != PlotMe)[0],0]) > 0):
        xAxMIN = np.min([xAxMIN,np.min(FailBuddyAT[np.where(FailBuddyAT[:,1] != PlotMe)[0],0])])
        xAxMAX = np.max([xAxMAX,np.max(FailBuddyAT[np.where(FailBuddyAT[:,1] != PlotMe)[0],0])])
    print(xAxMIN,xAxMAX)
     
    if (len(FailRepAT[np.where(FailRepAT[:,1] != PlotMe)[0],0]) > 0):
        xAxMIN = np.min([xAxMIN,np.min(FailRepAT[np.where(FailRepAT[:,1] != PlotMe)[0],0])])
        xAxMAX = np.max([xAxMAX,np.max(FailRepAT[np.where(FailRepAT[:,1] != PlotMe)[0],0])])
    print(xAxMIN,xAxMAX)
    
    if (len(FailClimDPT[np.where(FailClimDPT[:,1] != PlotMe)[0],0]) > 0): 
        xAxMIN = np.min([xAxMIN,np.min(FailClimDPT[np.where(FailClimDPT[:,1] != PlotMe)[0],0])])
        xAxMAX = np.max([xAxMAX,np.max(FailClimDPT[np.where(FailClimDPT[:,1] != PlotMe)[0],0])])
    print(xAxMIN,xAxMAX)
    
    if (len(FailBuddyDPT[np.where(FailBuddyDPT[:,1] != PlotMe)[0],0]) > 0): 
        xAxMIN = np.min([xAxMIN,np.min(FailBuddyDPT[np.where(FailBuddyDPT[:,1] != PlotMe)[0],0])])
        xAxMAX = np.max([xAxMAX,np.max(FailBuddyDPT[np.where(FailBuddyDPT[:,1] != PlotMe)[0],0])])
    print(xAxMIN,xAxMAX)
    
    if (len(FailRepDPT[np.where(FailRepDPT[:,1] != PlotMe)[0],0]) > 0):
        xAxMIN = np.min([xAxMIN,np.min(FailRepDPT[np.where(FailRepDPT[:,1] != PlotMe)[0],0])])
        xAxMAX = np.max([xAxMAX,np.max(FailRepDPT[np.where(FailRepDPT[:,1] != PlotMe)[0],0])])
    print(xAxMIN,xAxMAX)
    
    if (len(FailRepSatDPT[np.where(FailRepSatDPT[:,1] != PlotMe)[0],0]) > 0): 
        xAxMIN = np.min([xAxMIN,np.min(FailRepSatDPT[np.where(FailRepSatDPT[:,1] != PlotMe)[0],0])])
        xAxMAX = np.max([xAxMAX,np.max(FailRepSatDPT[np.where(FailRepSatDPT[:,1] != PlotMe)[0],0])])
    print(xAxMIN,xAxMAX)
    
    if (len(FailSSatDPT[np.where(FailSSatDPT[:,1] != PlotMe)[0],0]) > 0):
        xAxMIN = np.min([xAxMIN,np.min(FailSSatDPT[np.where(FailSSatDPT[:,1] != PlotMe)[0],0])])
        xAxMAX = np.max([xAxMAX,np.max(FailSSatDPT[np.where(FailSSatDPT[:,1] != PlotMe)[0],0])])
    print(xAxMIN,xAxMAX)

    # Make the X axes nice
    XHigh = np.ceil(xAxMAX * 1.1)		      
    XLow = np.floor(xAxMIN * 1.1)
        
    # Set up the plot
    gap= 0.04

    plt.clf()
    fig, ax1 = plt.subplots()    
    
    # Set up equally spaced histogram bins between min and max range (including end point as a value for 51 bins, 
    binsies = np.linspace(XLow,XHigh,51) # a range of bins from left most to right most point

    # For each QC flag plot a line as No. Obs on left axis and % of total obs on right axis	   
    i = 0
    ThisHist = np.histogram(FailTrk[np.where(FailTrk[:,1] != PlotMe)[0],0],binsies)
    HalfX = (ThisHist[1][1] - ThisHist[1][0]) / 2.
    ax1.plot(ThisHist[1][0:50]+HalfX,ThisHist[0],c='hotpink',linestyle='solid',linewidth=2) 
    meanHist = '{:6.2f}'.format(np.mean(FailTrk[np.where(FailTrk[:,1] != PlotMe)[0],0]))
    sdHist = '{:6.2f}'.format(np.std(FailTrk[np.where(FailTrk[:,1] != PlotMe)[0],0]))
    PctFail = '{:6.2f}'.format((len(FailTrk[np.where(FailTrk[:,1] != PlotMe)[0],0]) / np.float(TotalObs)) * 100.)+'%'
    ax1.annotate('track check ('+meanHist+', '+sdHist+', '+PctFail+')',xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='hotpink')
    if (len(FailTrk[np.where(FailTrk[:,1] != PlotMe)[0],0]) > 0):
        y1AxMAX = np.max([y1AxMAX,np.max(ThisHist[0])])
    print(y1AxMAX)
    
    i = 1
    ThisHist = np.histogram(FailClimAT[np.where(FailClimAT[:,1] != PlotMe)[0],0],binsies)
    HalfX = (ThisHist[1][1] - ThisHist[1][0]) / 2.
    ax1.plot(ThisHist[1][0:50]+HalfX,ThisHist[0],c='red',linestyle='solid',linewidth=2) 
    meanHist = '{:6.2f}'.format(np.mean(FailClimAT[np.where(FailClimAT[:,1] != PlotMe)[0],0]))
    sdHist = '{:6.2f}'.format(np.std(FailClimAT[np.where(FailClimAT[:,1] != PlotMe)[0],0]))
    PctFail = '{:6.2f}'.format((len(FailClimAT[np.where(FailClimAT[:,1] != PlotMe)[0],0]) / np.float(TotalObs)) * 100.)+'%'
    ax1.annotate('AT climatology ('+meanHist+', '+sdHist+', '+PctFail+')',xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='red')
    if (len(FailClimAT[np.where(FailClimAT[:,1] != PlotMe)[0],0]) > 0):
        y1AxMAX = np.max([y1AxMAX,np.max(ThisHist[0])])
    print(y1AxMAX)

    i = 2
    ThisHist = np.histogram(FailBuddyAT[np.where(FailBuddyAT[:,1] != PlotMe)[0],0],binsies)
    HalfX = (ThisHist[1][1] - ThisHist[1][0]) / 2.
    ax1.plot(ThisHist[1][0:50]+HalfX,ThisHist[0],c='darkorange',linestyle='solid',linewidth=2) 
    meanHist = '{:6.2f}'.format(np.mean(FailBuddyAT[np.where(FailBuddyAT[:,1] != PlotMe)[0],0]))
    sdHist = '{:6.2f}'.format(np.std(FailBuddyAT[np.where(FailBuddyAT[:,1] != PlotMe)[0],0]))
    PctFail = '{:6.2f}'.format((len(FailBuddyAT[np.where(FailBuddyAT[:,1] != PlotMe)[0],0]) / np.float(TotalObs)) * 100.)+'%'
    ax1.annotate('AT buddy ('+meanHist+', '+sdHist+', '+PctFail+')',xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='darkorange')
    if (len(FailBuddyAT[np.where(FailBuddyAT[:,1] != PlotMe)[0],0]) > 0):
        y1AxMAX = np.max([y1AxMAX,np.max(ThisHist[0])])
    print(y1AxMAX)
     
    i = 3
    ThisHist = np.histogram(FailRepAT[np.where(FailRepAT[:,1] != PlotMe)[0],0],binsies)
    HalfX = (ThisHist[1][1] - ThisHist[1][0]) / 2.
    ax1.plot(ThisHist[1][0:50]+HalfX,ThisHist[0],c='gold',linestyle='solid',linewidth=2) 
    meanHist = '{:6.2f}'.format(np.mean(FailRepAT[np.where(FailRepAT[:,1] != PlotMe)[0],0]))
    sdHist = '{:6.2f}'.format(np.std(FailRepAT[np.where(FailRepAT[:,1] != PlotMe)[0],0]))
    PctFail = '{:6.2f}'.format((len(FailRepAT[np.where(FailRepAT[:,1] != PlotMe)[0],0]) / np.float(TotalObs)) * 100.)+'%'
    ax1.annotate('AT repeat ('+meanHist+', '+sdHist+', '+PctFail+')',xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='gold')
    if (len(FailRepAT[np.where(FailRepAT[:,1] != PlotMe)[0],0]) > 0):
        y1AxMAX = np.max([y1AxMAX,np.max(ThisHist[0])])
    print(y1AxMAX)
    
    i = 4
    ThisHist = np.histogram(FailClimDPT[np.where(FailClimDPT[:,1] != PlotMe)[0],0],binsies)
    HalfX = (ThisHist[1][1] - ThisHist[1][0]) / 2.
    ax1.plot(ThisHist[1][0:50]+HalfX,ThisHist[0],c='grey',linestyle='solid',linewidth=2) 
    meanHist = '{:6.2f}'.format(np.mean(FailClimDPT[np.where(FailClimDPT[:,1] != PlotMe)[0],0]))
    sdHist = '{:6.2f}'.format(np.std(FailClimDPT[np.where(FailClimDPT[:,1] != PlotMe)[0],0]))
    PctFail = '{:6.2f}'.format((len(FailClimDPT[np.where(FailClimDPT[:,1] != PlotMe)[0],0]) / np.float(TotalObs)) * 100.)+'%'
    ax1.annotate('DPT climatology ('+meanHist+', '+sdHist+', '+PctFail+')',xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='grey')
    if (len(FailClimDPT[np.where(FailClimDPT[:,1] != PlotMe)[0],0]) > 0): 
        y1AxMAX = np.max([y1AxMAX,np.max(ThisHist[0])])
    print(y1AxMAX)
    
    i = 5
    ThisHist = np.histogram(FailBuddyDPT[np.where(FailBuddyDPT[:,1] != PlotMe)[0],0],binsies)
    HalfX = (ThisHist[1][1] - ThisHist[1][0]) / 2.
    ax1.plot(ThisHist[1][0:50]+HalfX,ThisHist[0],c='blue',linestyle='solid',linewidth=2) 
    meanHist = '{:6.2f}'.format(np.mean(FailBuddyDPT[np.where(FailBuddyDPT[:,1] != PlotMe)[0],0]))
    sdHist = '{:6.2f}'.format(np.std(FailBuddyDPT[np.where(FailBuddyDPT[:,1] != PlotMe)[0],0]))
    PctFail = '{:6.2f}'.format((len(FailBuddyDPT[np.where(FailBuddyDPT[:,1] != PlotMe)[0],0]) / np.float(TotalObs)) * 100.)+'%'
    ax1.annotate('DPT buddy ('+meanHist+', '+sdHist+', '+PctFail+')',xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='blue')
    if (len(FailBuddyDPT[np.where(FailBuddyDPT[:,1] != PlotMe)[0],0]) > 0): 
        y1AxMAX = np.max([y1AxMAX,np.max(ThisHist[0])])
    print(y1AxMAX)
    
    i = 6
    ThisHist = np.histogram(FailRepDPT[np.where(FailRepDPT[:,1] != PlotMe)[0],0],binsies)
    HalfX = (ThisHist[1][1] - ThisHist[1][0]) / 2.
    ax1.plot(ThisHist[1][0:50]+HalfX,ThisHist[0],c='limegreen',linestyle='solid',linewidth=2) 
    meanHist = '{:6.2f}'.format(np.mean(FailRepDPT[np.where(FailRepDPT[:,1] != PlotMe)[0],0]))
    sdHist = '{:6.2f}'.format(np.std(FailRepDPT[np.where(FailRepDPT[:,1] != PlotMe)[0],0]))
    PctFail = '{:6.2f}'.format((len(FailRepDPT[np.where(FailRepDPT[:,1] != PlotMe)[0],0]) / np.float(TotalObs)) * 100.)+'%'
    ax1.annotate('DPT repeat ('+meanHist+', '+sdHist+', '+PctFail+')',xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='limegreen')
    if (len(FailRepDPT[np.where(FailRepDPT[:,1] != PlotMe)[0],0]) > 0):
        y1AxMAX = np.max([y1AxMAX,np.max(ThisHist[0])])
    print(y1AxMAX)
    
    i = 7
    ThisHist = np.histogram(FailRepSatDPT[np.where(FailRepSatDPT[:,1] != PlotMe)[0],0],binsies)
    HalfX = (ThisHist[1][1] - ThisHist[1][0]) / 2.
    ax1.plot(ThisHist[1][0:50]+HalfX,ThisHist[0],c='olivedrab',linestyle='solid',linewidth=2) 
    meanHist = '{:6.2f}'.format(np.mean(FailRepSatDPT[np.where(FailRepSatDPT[:,1] != PlotMe)[0],0]))
    sdHist = '{:6.2f}'.format(np.std(FailRepSatDPT[np.where(FailRepSatDPT[:,1] != PlotMe)[0],0]))
    PctFail = '{:6.2f}'.format((len(FailRepSatDPT[np.where(FailRepSatDPT[:,1] != PlotMe)[0],0]) / np.float(TotalObs)) * 100.)+'%'
    ax1.annotate('DPT repeat saturation ('+meanHist+', '+sdHist+', '+PctFail+')',xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='olivedrab')
    if (len(FailRepSatDPT[np.where(FailRepSatDPT[:,1] != PlotMe)[0],0]) > 0): 
        y1AxMAX = np.max([y1AxMAX,np.max(ThisHist[0])])
    print(y1AxMAX)
    
    i = 8
    ThisHist = np.histogram(FailSSatDPT[np.where(FailSSatDPT[:,1] != PlotMe)[0],0],binsies)
    HalfX = (ThisHist[1][1] - ThisHist[1][0]) / 2.
    ax1.plot(ThisHist[1][0:50]+HalfX,ThisHist[0],c='indigo',linestyle='solid',linewidth=2) 
    meanHist = '{:6.2f}'.format(np.mean(FailSSatDPT[np.where(FailSSatDPT[:,1] != PlotMe)[0],0]))
    sdHist = '{:6.2f}'.format(np.std(FailSSatDPT[np.where(FailSSatDPT[:,1] != PlotMe)[0],0]))
    PctFail = '{:6.2f}'.format((len(FailSSatDPT[np.where(FailSSatDPT[:,1] != PlotMe)[0],0]) / np.float(TotalObs)) * 100.)+'%'
    ax1.annotate('DPT super saturation ('+meanHist+', '+sdHist+', '+PctFail+')',xy=(0.05,0.94-(i*gap)),xycoords='axes fraction',size=12,color='indigo')
    if (len(FailSSatDPT[np.where(FailSSatDPT[:,1] != PlotMe)[0],0]) > 0):
        y1AxMAX = np.max([y1AxMAX,np.max(ThisHist[0])])
    print(y1AxMAX)

    # Rationalies the Y axes ranges
    Y1Low = 0	# y1Ax is total number of obs so integer    
    Y2Low = 0. # y2Ax is percentage of ALL obs (TotalObs) so float		      
    y2AxMAX = (y1AxMAX / np.float(TotalObs)) *100.
		      
    # Now make the Y ranges 'nice'
    Y1High = np.ceil(y1AxMAX * 1.1)
    Y2High = (Y1High / np.float(TotalObs)) *100.
    		      
    # Establish the axes label strings
    y1AxLabel = 'Number of Obs with QC flag'
    y2AxLabel = 'Percentage of All Obs with QC flag'
    xAxLabel = ThisVarName+' '+ThisValType+' ('+ThisVarUnit+')'

    ax1.set_xlabel(xAxLabel)
    ax1.set_xlim(XLow,XHigh)
    ax1.set_ylabel(y1AxLabel)
    ax1.set_ylim(Y1Low,Y1High)
    ax2 = ax1.twinx()
    ax2.set_ylabel(y2AxLabel)
    ax2.set_ylim(Y2Low,Y2High)

    plt.tight_layout()

    #plt.savefig(FileName+".eps")
    plt.savefig(FileName+".png")

    return # PlotQCTest

#************************************************************************
# MAIN
#************************************************************************
def main(argv):
    # INPUT PARAMETERS AS STRINGS!!!!
    year1 = '1973' 
    year2 = '1973'
    month1 = '01' # months must be 01, 02 etc
    month2 = '12'
    typee = 'ERAclimNBC' # 'ERAclimNBC', 'OBSclim1NBC', 'OBSclim2NBC'
    varee = 'AT'	# 'AT','DPT','SHU','CRH'
    
    # TWEAK ME!!!!
    # What date stamp do you want on the files?
    nowmon = 'SEP'
    nowyear = '2016'

    try:
        opts, args = getopt.getopt(argv, "hi:",
	                           ["year1=","year2=","month1=","month2=","typee=","varee="])
    except getopt.GetoptError:
        print 'Usage (as strings) PlotQCTest_SEP2016.py --year1 <1973> --year2 <1973> '+\
	      '--month1 <01> --month2 <12> --typee <ERAclimNBC> --varee <AT>'
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
        elif opt == "--varee":
            try:
                varee = arg
            except:
                sys.exit("Failed: varee not a string")

    assert year1 != -999 and year2 != -999, "Year not specified."

    print(year1, year2, month1, month2, typee, varee)
#    pdb.set_trace()

    INDIR = '/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/'+typee+'/'
    INFIL = 'new_suite_'   # 199406_ERAclimNBC.txt.gz

    OUTDIR = '/data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/'
    OutPltAbsday =    'SummaryHistQC_DAY_Abs_'+varee+'_'+typee+'_'  #1973_SEP2016.png 
    OutPltAbsngt =    'SummaryHistQC_NIGHT_Abs_'+varee+'_'+typee+'_'
    OutPltAbs =       'SummaryHistQC_BOTH_Abs_'+varee+'_'+typee+'_'
    OutPltAnomsday =  'SummaryHistQC_DAY_Anoms_'+varee+'_'+typee+'_'
    OutPltAnomsngt =  'SummaryHistQC_NIGHT_Anoms_'+varee+'_'+typee+'_'
    OutPltAnoms =     'SummaryHistQC_BOTH_Anoms_'+varee+'_'+typee+'_'

    # Container arrays to store info for end of loop plot (may not have enough memory for ALL vars, Abs/Anoms and Day/Night/Both
    nObs = 0 # Total number of obs for period (good and bad)
    # The rest are set up in loop

    # Container arrays to store info for annual plot (may not have enough memory for ALL vars, Abs/Anoms and Day/Night/Both
    ANNnObs = 0 # Total number of obs for period (good and bad)
    # The rest are set up in loop
    
    # How many months to loop through?
    nYears = (int(year2) - int(year1)) + 1
    # Unless nYears is l assume months is nYears*12 - all months included
    if (nYears > 1):
        nMonths = nYears*12
    else:
        nMonths = (int(month2) - int(month1)) + 1
	    
    # Set up loop to go through month files of data
    # Output a plot at the end of each year and end of entire loop
    for ff in range(nMonths):
        
	# Which year and month to read in?
	ThisYear = int(year1) + (ff / 12) # This is an integer (not rounded - floor!) so 0-11/12 = 0, 12-23/12 = 1 etc
	ThisMonth = '{:02}'.format((ff - ((ff / 12) * 12)) + 1) 
	print(ThisYear, ThisMonth)
	
	# Read in the MDSdict and pick out desired variable values (abs and anoms) and QC flags
	FileName = INDIR+INFIL+str(ThisYear)+ThisMonth+'_'+typee+'.txt.gz'
	
        MDSdict=mrw.ReadMDSstandard(str(ThisYear), ThisMonth, typee)

	# Get the correct absolute and anomaly variables
	if (varee == 'AT'):
	    TheValsAbs = MDSdict['AT']
            TheValsAnoms = MDSdict['ATA']
	if (varee == 'DPT'):
            TheValsAbs = MDSdict['DPT']
            TheValsAnoms = MDSdict['DPTA']
	if (varee == 'SHU'):
            TheValsAbs = MDSdict['SHU']
            TheValsAnoms = MDSdict['SHUA']
	if (varee == 'CRH'):
            TheValsAbs = MDSdict['CRH']
            TheValsAnoms = MDSdict['CRHA']

	# Go through QC flags and populate ANNUAL Fail arrays accordingly
	# If we haven't set up the annual arrays yet then initialise
	if (ANNnObs == 0):

            ANNAbsFailTrk =       np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['trk'] == 1)],MDSdict['day'][np.where(MDSdict['trk'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['trk'] == 1)]))))
            ANNAbsFailClimAT =    np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['ATclim'] == 1)],MDSdict['day'][np.where(MDSdict['ATclim'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['ATclim'] == 1)]))))
            ANNAbsFailBuddyAT =   np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['ATbud'] == 1)],MDSdict['day'][np.where(MDSdict['ATbud'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['ATbud'] == 1)]))))
            ANNAbsFailRepAT =     np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['ATrep'] == 1)],MDSdict['day'][np.where(MDSdict['ATrep'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['ATrep'] == 1)]))))
            ANNAbsFailClimDPT =   np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['DPTclim'] == 1)],MDSdict['day'][np.where(MDSdict['DPTclim'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['DPTclim'] == 1)]))))
            ANNAbsFailBuddyDPT =  np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['DPTbud'] == 1)],MDSdict['day'][np.where(MDSdict['DPTbud'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['DPTbud'] == 1)]))))
            ANNAbsFailRepDPT =    np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['DPTrep'] == 1)],MDSdict['day'][np.where(MDSdict['DPTrep'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['DPTrep'] == 1)]))))
            ANNAbsFailRepSatDPT = np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['DPTrepsat'] == 1)],MDSdict['day'][np.where(MDSdict['DPTrepsat'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['DPTrepsat'] == 1)]))))
            ANNAbsFailSSatDPT =   np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['DPTssat'] == 1)],MDSdict['day'][np.where(MDSdict['DPTssat'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['DPTssat'] == 1)]))))
	    
            ANNAnomsFailTrk =       np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['trk'] == 1)],MDSdict['day'][np.where(MDSdict['trk'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['trk'] == 1)]))))
            ANNAnomsFailClimAT =    np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['ATclim'] == 1)],MDSdict['day'][np.where(MDSdict['ATclim'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['ATclim'] == 1)]))))
            ANNAnomsFailBuddyAT =   np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['ATbud'] == 1)],MDSdict['day'][np.where(MDSdict['ATbud'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['ATbud'] == 1)]))))
            ANNAnomsFailRepAT =     np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['ATrep'] == 1)],MDSdict['day'][np.where(MDSdict['ATrep'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['ATrep'] == 1)]))))
            ANNAnomsFailClimDPT =   np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['DPTclim'] == 1)],MDSdict['day'][np.where(MDSdict['DPTclim'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['DPTclim'] == 1)]))))
            ANNAnomsFailBuddyDPT =  np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['DPTbud'] == 1)],MDSdict['day'][np.where(MDSdict['DPTbud'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['DPTbud'] == 1)]))))
            ANNAnomsFailRepDPT =    np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['DPTrep'] == 1)],MDSdict['day'][np.where(MDSdict['DPTrep'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['DPTrep'] == 1)]))))
            ANNAnomsFailRepSatDPT = np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['DPTrepsat'] == 1)],MDSdict['day'][np.where(MDSdict['DPTrepsat'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['DPTrepsat'] == 1)]))))
            ANNAnomsFailSSatDPT =   np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['DPTssat'] == 1)],MDSdict['day'][np.where(MDSdict['DPTssat'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['DPTssat'] == 1)]))))

        # If we already have then just append
	else:

            ANNAbsFailTrk =	  np.append(ANNAbsFailTrk,np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['trk'] == 1)],MDSdict['day'][np.where(MDSdict['trk'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['trk'] == 1)])))),axis=0)
            ANNAbsFailClimAT =    np.append(ANNAbsFailClimAT,np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['ATclim'] == 1)],MDSdict['day'][np.where(MDSdict['ATclim'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['ATclim'] == 1)])))),axis=0)
            ANNAbsFailBuddyAT =   np.append(ANNAbsFailBuddyAT,np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['ATbud'] == 1)],MDSdict['day'][np.where(MDSdict['ATbud'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['ATbud'] == 1)])))),axis=0)
            ANNAbsFailRepAT =	  np.append(ANNAbsFailRepAT,np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['ATrep'] == 1)],MDSdict['day'][np.where(MDSdict['ATrep'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['ATrep'] == 1)])))),axis=0)
            ANNAbsFailClimDPT =   np.append(ANNAbsFailClimDPT,np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['DPTclim'] == 1)],MDSdict['day'][np.where(MDSdict['DPTclim'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['DPTclim'] == 1)])))),axis=0)
            ANNAbsFailBuddyDPT =  np.append(ANNAbsFailBuddyDPT,np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['DPTbud'] == 1)],MDSdict['day'][np.where(MDSdict['DPTbud'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['DPTbud'] == 1)])))),axis=0)
            ANNAbsFailRepDPT =    np.append(ANNAbsFailRepDPT,np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['DPTrep'] == 1)],MDSdict['day'][np.where(MDSdict['DPTrep'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['DPTrep'] == 1)])))),axis=0)
            ANNAbsFailRepSatDPT = np.append(ANNAbsFailRepSatDPT,np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['DPTrepsat'] == 1)],MDSdict['day'][np.where(MDSdict['DPTrepsat'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['DPTrepsat'] == 1)])))),axis=0)
            ANNAbsFailSSatDPT =   np.append(ANNAbsFailSSatDPT,np.transpose(np.reshape((TheValsAbs[np.where(MDSdict['DPTssat'] == 1)],MDSdict['day'][np.where(MDSdict['DPTssat'] == 1)]),(2,len(TheValsAbs[np.where(MDSdict['DPTssat'] == 1)])))),axis=0)
	    
            ANNAnomsFailTrk =	    np.append(ANNAnomsFailTrk,np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['trk'] == 1)],MDSdict['day'][np.where(MDSdict['trk'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['trk'] == 1)])))),axis=0)
            ANNAnomsFailClimAT =    np.append(ANNAnomsFailClimAT,np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['ATclim'] == 1)],MDSdict['day'][np.where(MDSdict['ATclim'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['ATclim'] == 1)])))),axis=0)
            ANNAnomsFailBuddyAT =   np.append(ANNAnomsFailBuddyAT,np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['ATbud'] == 1)],MDSdict['day'][np.where(MDSdict['ATbud'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['ATbud'] == 1)])))),axis=0)
            ANNAnomsFailRepAT =     np.append(ANNAnomsFailRepAT,np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['ATrep'] == 1)],MDSdict['day'][np.where(MDSdict['ATrep'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['ATrep'] == 1)])))),axis=0)
            ANNAnomsFailClimDPT =   np.append(ANNAnomsFailClimDPT,np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['DPTclim'] == 1)],MDSdict['day'][np.where(MDSdict['DPTclim'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['DPTclim'] == 1)])))),axis=0)
            ANNAnomsFailBuddyDPT =  np.append(ANNAnomsFailBuddyDPT,np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['DPTbud'] == 1)],MDSdict['day'][np.where(MDSdict['DPTbud'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['DPTbud'] == 1)])))),axis=0)
            ANNAnomsFailRepDPT =    np.append(ANNAnomsFailRepAT,np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['DPTrep'] == 1)],MDSdict['day'][np.where(MDSdict['DPTrep'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['DPTrep'] == 1)])))),axis=0)
            ANNAnomsFailRepSatDPT = np.append(ANNAnomsFailRepSatDPT,np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['DPTrepsat'] == 1)],MDSdict['day'][np.where(MDSdict['DPTrepsat'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['DPTrepsat'] == 1)])))),axis=0)
            ANNAnomsFailSSatDPT =   np.append(ANNAnomsFailSSatDPT,np.transpose(np.reshape((TheValsAnoms[np.where(MDSdict['DPTssat'] == 1)],MDSdict['day'][np.where(MDSdict['DPTssat'] == 1)]),(2,len(TheValsAnoms[np.where(MDSdict['DPTssat'] == 1)])))),axis=0)
	
	# Get total number of obs in this month year
	ANNnObs = ANNnObs + len(MDSdict['LAT'])
	        
        # Clear up some memory
	MDSdict = 0 # clear out

	# If end of year period then initialise end of year loop 
	if (ThisMonth == '12'):

	    # plot the annual period stuff
            PlotName = OUTDIR+OutPltAbsday+str(ThisYear)+'_'+nowmon+nowyear
	    PlotQCTest(PlotName,varee,'Abs','DAY',ANNnObs,ANNAbsFailTrk,
	                                              ANNAbsFailClimAT,ANNAbsFailBuddyAT,ANNAbsFailRepAT,
						      ANNAbsFailClimDPT,ANNAbsFailBuddyDPT,ANNAbsFailRepDPT,ANNAbsFailRepSatDPT,ANNAbsFailSSatDPT)
            PlotName = OUTDIR+OutPltAbsngt+str(ThisYear)+'_'+nowmon+nowyear
	    PlotQCTest(PlotName,varee,'Abs','NIGHT',ANNnObs,ANNAbsFailTrk,
	                                                ANNAbsFailClimAT,ANNAbsFailBuddyAT,ANNAbsFailRepAT,
						        ANNAbsFailClimDPT,ANNAbsFailBuddyDPT,ANNAbsFailRepDPT,ANNAbsFailRepSatDPT,ANNAbsFailSSatDPT)
            PlotName = OUTDIR+OutPltAbs+str(ThisYear)+'_'+nowmon+nowyear
	    PlotQCTest(PlotName,varee,'Abs','BOTH',ANNnObs,ANNAbsFailTrk,
	                                               ANNAbsFailClimAT,ANNAbsFailBuddyAT,ANNAbsFailRepAT,
						       ANNAbsFailClimDPT,ANNAbsFailBuddyDPT,ANNAbsFailRepDPT,ANNAbsFailRepSatDPT,ANNAbsFailSSatDPT)

            PlotName = OUTDIR+OutPltAnomsday+str(ThisYear)+'_'+nowmon+nowyear
	    PlotQCTest(PlotName,varee,'Anoms','DAY',ANNnObs,ANNAnomsFailTrk,
	                                              ANNAnomsFailClimAT,ANNAnomsFailBuddyAT,ANNAnomsFailRepAT,
						      ANNAnomsFailClimDPT,ANNAnomsFailBuddyDPT,ANNAnomsFailRepDPT,ANNAnomsFailRepSatDPT,ANNAnomsFailSSatDPT)
            PlotName = OUTDIR+OutPltAnomsngt+str(ThisYear)+'_'+nowmon+nowyear
	    PlotQCTest(PlotName,varee,'Anoms','NIGHT',ANNnObs,ANNAnomsFailTrk,
	                                              ANNAnomsFailClimAT,ANNAnomsFailBuddyAT,ANNAnomsFailRepAT,
						      ANNAnomsFailClimDPT,ANNAnomsFailBuddyDPT,ANNAnomsFailRepDPT,ANNAnomsFailRepSatDPT,ANNAnomsFailSSatDPT)
            PlotName = OUTDIR+OutPltAnoms+str(ThisYear)+'_'+nowmon+nowyear
	    PlotQCTest(PlotName,varee,'Anoms','BOTH',ANNnObs,ANNAnomsFailTrk,
	                                              ANNAnomsFailClimAT,ANNAnomsFailBuddyAT,ANNAnomsFailRepAT,
						      ANNAnomsFailClimDPT,ANNAnomsFailBuddyDPT,ANNAnomsFailRepDPT,ANNAnomsFailRepSatDPT,ANNAnomsFailSSatDPT)

	    # Initialise or add to whole period arrays
	    # No full period arrays initialised yet
	    if (nObs == 0):

                AbsFailTrk =	    np.copy(ANNAbsFailTrk)	
                AbsFailClimAT =     np.copy(ANNAbsFailClimAT)	 
                AbsFailBuddyAT =    np.copy(ANNAbsFailBuddyAT)   
                AbsFailRepAT =      np.copy(ANNAbsFailRepAT)	 
                AbsFailClimDPT =    np.copy(ANNAbsFailClimDPT) 
                AbsFailBuddyDPT =   np.copy(ANNAbsFailBuddyDPT)  
                AbsFailRepDPT =     np.copy(ANNAbsFailRepDPT)	 
                AbsFailRepSatDPT =  np.copy(ANNAbsFailRepSatDPT) 
                AbsFailSSatDPT =    np.copy(ANNAbsFailSSatDPT)  
                
		AnomsFailTrk =      np.copy(ANNAnomsFailTrk)	 
                AnomsFailClimAT =   np.copy(ANNAnomsFailClimAT)  
                AnomsFailBuddyAT =  np.copy(ANNAnomsFailBuddyAT) 
                AnomsFailRepAT =    np.copy(ANNAnomsFailRepAT)  
                AnomsFailClimDPT =  np.copy(ANNAnomsFailClimDPT)
                AnomsFailBuddyDPT = np.copy(ANNAnomsFailBuddyDPT)
                AnomsFailRepDPT =   np.copy(ANNAnomsFailRepDPT)  
                AnomsFailRepSatDPT = np.copy(ANNAnomsFailRepSatDPT) 
                AnomsFailSSatDPT =  np.copy(ANNAnomsFailSSatDPT)
	 
	    else:

                AbsFailTrk =	    np.append(AbsFailTrk,ANNAbsFailTrk,axis=0)   
                AbsFailClimAT =     np.append(AbsFailClimAT,ANNAbsFailClimAT,axis=0)	  
                AbsFailBuddyAT =    np.append(AbsFailBuddyAT,ANNAbsFailBuddyAT,axis=0)   
                AbsFailRepAT =      np.append(AbsFailRepAT,ANNAbsFailRepAT,axis=0)  
                AbsFailClimDPT =    np.append(AbsFailClimDPT,ANNAbsFailClimDPT,axis=0) 
                AbsFailBuddyDPT =   np.append(AbsFailBuddyDPT,ANNAbsFailBuddyDPT,axis=0)  
                AbsFailRepDPT =     np.append(AbsFailRepDPT,ANNAbsFailRepDPT,axis=0)	  
                AbsFailRepSatDPT =  np.append(AbsFailRepSatDPT,ANNAbsFailRepSatDPT,axis=0) 
                AbsFailSSatDPT =    np.append(AbsFailSSatDPT,ANNAbsFailSSatDPT,axis=0)  
                
		AnomsFailTrk =      np.append(AnomsFailTrk,ANNAnomsFailTrk,axis=0)  
                AnomsFailClimAT =   np.append(AnomsFailClimAT,ANNAnomsFailClimAT,axis=0)  
                AnomsFailBuddyAT =  np.append(AnomsFailBuddyAT,ANNAnomsFailBuddyAT,axis=0) 
                AnomsFailRepAT =    np.append(AnomsFailRepAT,ANNAnomsFailRepAT,axis=0)  
                AnomsFailClimDPT =  np.append(AnomsFailClimDPT,ANNAnomsFailClimDPT,axis=0)
                AnomsFailBuddyDPT = np.append(AnomsFailBuddyDPT,ANNAnomsFailBuddyDPT,axis=0)
                AnomsFailRepDPT =   np.append(AnomsFailRepDPT,ANNAnomsFailRepDPT,axis=0)  
                AnomsFailRepSatDPT = np.append(AnomsFailRepSatDPT,ANNAnomsFailRepSatDPT,axis=0) 
                AnomsFailSSatDPT =  np.append(AnomsFailSSatDPT,ANNAnomsFailSSatDPT,axis=0)
	    	
	    nObs = nObs + ANNnObs
	    
	    # Reset Annual arrays - or at least the nObs so that the initialise array loop is triggered.
	    ANNnObs = 0

        # If end of entire period (AND ENTIRE PERIOD IS NOT JUST ONE YEAR - ALREADY PLOTTED) then plot up and finish
        if (ff == nMonths-1):
            
	    # If this is a special sub-annual case then we'll have to plot the ANNarrays
	    if (ff < 11):
	        PlotName = OUTDIR+OutPltAbsday+year1+year2+'{:02}'.format(int(month1))+'{:02}'.format(int(month2))+'_'+nowmon+nowyear
	        PlotQCTest(PlotName,varee,'Abs','DAY',ANNnObs,ANNAbsFailTrk,
	                                              ANNAbsFailClimAT,ANNAbsFailBuddyAT,ANNAbsFailRepAT,
						      ANNAbsFailClimDPT,ANNAbsFailBuddyDPT,ANNAbsFailRepDPT,ANNAbsFailRepSatDPT,ANNAbsFailSSatDPT)
                PlotName = OUTDIR+OutPltAbsngt+year1+year2+'{:02}'.format(int(month1))+'{:02}'.format(int(month2))+'_'+nowmon+nowyear
	        PlotQCTest(PlotName,varee,'Abs','NIGHT',ANNnObs,ANNAbsFailTrk,
	                                                ANNAbsFailClimAT,ANNAbsFailBuddyAT,ANNAbsFailRepAT,
						        ANNAbsFailClimDPT,ANNAbsFailBuddyDPT,ANNAbsFailRepDPT,ANNAbsFailRepSatDPT,ANNAbsFailSSatDPT)
                PlotName = OUTDIR+OutPltAbs+year1+year2+'{:02}'.format(int(month1))+'{:02}'.format(int(month2))+'_'+nowmon+nowyear
	        PlotQCTest(PlotName,varee,'Abs','BOTH',ANNnObs,ANNAbsFailTrk,
	                                               ANNAbsFailClimAT,ANNAbsFailBuddyAT,ANNAbsFailRepAT,
						       ANNAbsFailClimDPT,ANNAbsFailBuddyDPT,ANNAbsFailRepDPT,ANNAbsFailRepSatDPT,ANNAbsFailSSatDPT)

                PlotName = OUTDIR+OutPltAnomsday+year1+year2+'{:02}'.format(int(month1))+'{:02}'.format(int(month2))+'_'+nowmon+nowyear
	        PlotQCTest(PlotName,varee,'Anoms','DAY',ANNnObs,ANNAnomsFailTrk,
	                                              ANNAnomsFailClimAT,ANNAnomsFailBuddyAT,ANNAnomsFailRepAT,
						      ANNAnomsFailClimDPT,ANNAnomsFailBuddyDPT,ANNAnomsFailRepDPT,ANNAnomsFailRepSatDPT,ANNAnomsFailSSatDPT)
                PlotName = OUTDIR+OutPltAnomsngt+year1+year2+'{:02}'.format(int(month1))+'{:02}'.format(int(month2))+'_'+nowmon+nowyear
	        PlotQCTest(PlotName,varee,'Anoms','NIGHT',ANNnObs,ANNAnomsFailTrk,
	                                              ANNAnomsFailClimAT,ANNAnomsFailBuddyAT,ANNAnomsFailRepAT,
						      ANNAnomsFailClimDPT,ANNAnomsFailBuddyDPT,ANNAnomsFailRepDPT,ANNAnomsFailRepSatDPT,ANNAnomsFailSSatDPT)
                PlotName = OUTDIR+OutPltAnoms+year1+year2+'{:02}'.format(int(month1))+'{:02}'.format(int(month2))+'_'+nowmon+nowyear
	        PlotQCTest(PlotName,varee,'Anoms','BOTH',ANNnObs,ANNAnomsFailTrk,
	                                              ANNAnomsFailClimAT,ANNAnomsFailBuddyAT,ANNAnomsFailRepAT,
						      ANNAnomsFailClimDPT,ANNAnomsFailBuddyDPT,ANNAnomsFailRepDPT,ANNAnomsFailRepSatDPT,ANNAnomsFailSSatDPT)
	    
	    # Else in all other cases - assume we only work in whole years!!!
	    # plot the annual period stuff 
            else:
	        PlotName = OUTDIR+OutPltAbsday+year1+year2+'{:02}'.format(int(month1))+'{:02}'.format(int(month2))+'_'+nowmon+nowyear
	        PlotQCTest(PlotName,varee,'Abs','DAY',nObs,AbsFailTrk,
	                                              AbsFailClimAT,AbsFailBuddyAT,AbsFailRepAT,
						      AbsFailClimDPT,AbsFailBuddyDPT,AbsFailRepDPT,AbsFailRepSatDPT,AbsFailSSatDPT)
                PlotName = OUTDIR+OutPltAbsngt+year1+year2+'{:02}'.format(int(month1))+'{:02}'.format(int(month2))+'_'+nowmon+nowyear
	        PlotQCTest(PlotName,varee,'Abs','NIGHT',nObs,AbsFailTrk,
	                                                AbsFailClimAT,AbsFailBuddyAT,AbsFailRepAT,
						        AbsFailClimDPT,AbsFailBuddyDPT,AbsFailRepDPT,AbsFailRepSatDPT,AbsFailSSatDPT)
                PlotName = OUTDIR+OutPltAbs+year1+year2+'{:02}'.format(int(month1))+'{:02}'.format(int(month2))+'_'+nowmon+nowyear
	        PlotQCTest(PlotName,varee,'Abs','BOTH',nObs,AbsFailTrk,
	                                               AbsFailClimAT,AbsFailBuddyAT,AbsFailRepAT,
						       AbsFailClimDPT,AbsFailBuddyDPT,AbsFailRepDPT,AbsFailRepSatDPT,AbsFailSSatDPT)

                PlotName = OUTDIR+OutPltAnomsday+year1+year2+'{:02}'.format(int(month1))+'{:02}'.format(int(month2))+'_'+nowmon+nowyear
	        PlotQCTest(PlotName,varee,'Anoms','DAY',nObs,AnomsFailTrk,
	                                              AnomsFailClimAT,AnomsFailBuddyAT,AnomsFailRepAT,
						      AnomsFailClimDPT,AnomsFailBuddyDPT,AnomsFailRepDPT,AnomsFailRepSatDPT,AnomsFailSSatDPT)
                PlotName = OUTDIR+OutPltAnomsngt+year1+year2+'{:02}'.format(int(month1))+'{:02}'.format(int(month2))+'_'+nowmon+nowyear
	        PlotQCTest(PlotName,varee,'Anoms','NIGHT',nObs,AnomsFailTrk,
	                                              AnomsFailClimAT,AnomsFailBuddyAT,AnomsFailRepAT,
						      AnomsFailClimDPT,AnomsFailBuddyDPT,AnomsFailRepDPT,AnomsFailRepSatDPT,AnomsFailSSatDPT)
                PlotName = OUTDIR+OutPltAnoms+year1+year2+'{:02}'.format(int(month1))+'{:02}'.format(int(month2))+'_'+nowmon+nowyear
	        PlotQCTest(PlotName,varee,'Anoms','BOTH',nObs,AnomsFailTrk,
	                                              AnomsFailClimAT,AnomsFailBuddyAT,AnomsFailRepAT,
						      AnomsFailClimDPT,AnomsFailBuddyDPT,AnomsFailRepDPT,AnomsFailRepSatDPT,AnomsFailSSatDPT)


    #pdb.set_trace()

    print("And were done")

if __name__ == '__main__':
    
    main(sys.argv[1:])

#************************************************************************
