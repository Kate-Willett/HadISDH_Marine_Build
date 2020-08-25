#!/usr/local/sci/bin/python
# PYTHON2.7
# 
# Author: Kate Willett
# Created: 23 Aug 2018
# Last update: 23 August 2018
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/ANALYSIS_PLOTS/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code loops through each year/month ascii file for June and December in given range and plots 
# logarithmic distribution of all vs QC'd obs
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
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/ERAclimNBC/
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/OBSclim1NBC/
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/OBSclim2NBC/
#
# -----------------------
# HOW TO RUN THE CODE
# -----------------------
# check the desired bits are uncommented/commented (filepaths etc)
# Call key words for type (ERAclimNBC), year start and end, month start and end (default whole year) and variable
# Ideally we would run all vars together to save time but its just tooooooo big
#
# python2.7 PlotObsDistributions_AUG2018.py --year1 1973 --year2 1991 --typee ERAclimNBC --varee CRH 
#
# This runs the code, outputs the plots
# 
# -----------------------
# OUTPUT
# -----------------------
# some plots:
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryObsDist_DAY_Abs_CRH_ERAclimNBC_19731981 ERAclimNBC
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryObsDist_DAY_Anoms_CRH_ERAclimNBC_19731981 ERAclimNBC
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryObsDist_NIGHT_Abs_CRH_ERAclimNBC_19731981 ERAclimNBC
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryObsDist_NIGHT_Anoms_CRH_ERAclimNBC_19731981 ERAclimNBC
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryObsDist_BOTH_Abs_CRH_ERAclimNBC_19731981 ERAclimNBC
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/SummaryObsDist_BOTH_Anoms_CRH_ERAclimNBC_19731981 ERAclimNBC
# 
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
# 
# Version 1 (23 August 2018)
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
# Make y labels smaller, annotated text smaller with larger gaps
# Plot log and normal
# Do we see any spikes in RH values - e.g., 20%rh? I don't think we do really.
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
# PLOTDists
#*************************************************************************
def PlotObsDist(FileName, TheStYear,TheNYears,TheHisto,TheQCHisto,TheFHisto,TheVar,Binsies,TheXTitle,
                ThemeanHist,ThemeanQCHist,ThemeanFHist,ThesdHist,ThesdQCHist,ThesdFHist):
    ''' FileName - directory path and filename without .eps or .png '''
    ''' TheStYear - the start year '''
    ''' TheNYears - the totle number of years '''
    ''' TheHisto - The list of histograms of all data for this category '''
    ''' TheQCHisto - The list of histolgrams of qc'd data for this category '''
    ''' TheFHisto - the list of histograms of failing data for this category '''
    ''' TheVar - the name of the variable AT, DPT, SHU, CRH '''
    ''' Binsies - the bins for the histograms '''
    ''' TheXTitle - The start of the title for the x axis '''
    ''' This code makes a png and/or eps of QC fail frequency by value (anomaly or absolute) '''
    ''' of the chosen variable (AT, DPT, SHU or CRH). '''
    ''' From this we hope to see whether there is a prevelance of low/high value removals '''
    ''' and whether over time there are distinct differences. '''
    ''' We can also compare the plots from different QC versions. '''

    # set up fontsize and label gap size
    if (TheNYears > 4):
        fs=8
	gs=0.06
    else:
        fs=12
	gs=0.04
    
    # Which variable are we dealing with? Set up units and axes label strings
    VarStrDict = dict([['AT',['Air Temperature','$^{o}$C']],
                       ['DPT',['Dew Point Temperature','$^{o}$C']],
		       ['SHU',['Specific Humidity','g kg$^{-1}$']],
		       ['CRH',['Relative Humidity','%rh']]])
		       
    ThisVarName = VarStrDict[TheVar][0]
    ThisVarUnit = VarStrDict[TheVar][1]
    		       		           
    # Establish axes ranges using all elements that have a non-zero length
    #xAxMIN = 1000 # a ridiculous value!
    #xAxMAX = -1000 # a ridiculous value!
    
    #xAxMIN = np.min([xAxMIN,np.min(FailTrk[np.where(FailTrk[:,1] != PlotMe)[0],0])])
    #xAxMAX = np.max([xAxMAX,np.max(FailTrk[np.where(FailTrk[:,1] != PlotMe)[0],0])])

    # Make the X axes nice
    #XHigh = np.ceil(xAxMAX * 1.1)		      
    #XLow = np.floor(xAxMIN * 1.1)

    xLow = np.min(Binsies)
    xHigh = np.max(Binsies) 
    print(xHigh,xLow)
	
    #yAxMIN = 1000 # a ridiculous value!
    yAxMAX = 0 # a ridiculous value!
    
    #pdb.set_trace()
    #yAxMIN = np.min([xAxMIN,np.min(FailTrk[np.where(FailTrk[:,1] != PlotMe)[0],0])])
    yAxMAX = np.max([np.max(TheHisto[i][0]) for i in range(TheNYears)])

    # Make the Y axes nice
    yHigh = np.ceil(yAxMAX * 1.1)		      
    #yLow = np.floor(yAxMIN * 1.1)
    yLow = 0

    print(yHigh,yLow)

    HalfX = (Binsies[1]-Binsies[0]) / 2.
        
    # Set up the plot
    gap= gs

    xpos=[]
    ypos=[]
    xfat=[]
    ytall=[]
    totalyspace=0.95    # start 0.1 end 0.98, 80/5 = 16 for each plot
    totalxspace=0.84    # start 0.13 end 0.98
    ywidth = 0.95/TheNYears
    xwidth = 0.84
    for r in range(TheNYears):
        ypos.append(0.03+r*ywidth)
        xpos.append(0.13)
        xfat.append(xwidth)
        ytall.append(ywidth)
    print('Set up plot positions')

    plt.clf()
    fig, ax = plt.subplots(TheNYears,figsize=(5,15))    
    
    for yy in range(TheNYears):
        ax[yy].set_position([xpos[yy],ypos[yy],xfat[yy],ytall[yy]])
        print(xpos[yy],ypos[yy],xfat[yy],ytall[yy])

        ax[yy].set_xlim([xLow,xHigh])
        if (yy == 0):
	    ax[yy].set_xlabel(ThisVarName+' '+TheXTitle+'('+ThisVarUnit+')',fontsize=fs)
	else:
	    ax[yy].set_xticklabels([])
        ax[yy].set_ylabel('LOG(N. Obs) '+str('{:4d}'.format(int(TheStYear)+yy)),fontsize=fs)
	ax[yy].set_yscale('log')
	
        ax[yy].plot(Binsies[0:-1]+HalfX,TheHisto[yy][0],c='black',linestyle='solid',linewidth=2) 
        ax[yy].plot(Binsies[0:-1]+HalfX,TheQCHisto[yy][0],c='blue',linestyle='solid',linewidth=2) 
        ax[yy].plot(Binsies[0:-1]+HalfX,TheFHisto[yy][0],c='red',linestyle='solid',linewidth=2) 
#        ax[yy].semilogy(Binsies[0:-1]+HalfX,TheHisto[yy][0],c='black',linestyle='solid',linewidth=2) 
#        ax[yy].semilogy(Binsies[0:-1]+HalfX,TheQCHisto[yy][0],c='blue',linestyle='solid',linewidth=2) 
#        ax[yy].semilogy(Binsies[0:-1]+HalfX,TheFHisto[yy][0],c='red',linestyle='solid',linewidth=2) 
        #ax[yy].set_ylim([0,yHigh])
        PctFail = '{:4.1f}'.format((np.sum(TheFHisto[yy][0])/np.float(np.sum(TheHisto[yy][0]))) * 100.)+'%'
        ax[yy].annotate(str('All ('+'{:5.1f}'.format(ThemeanHist[yy])+', '+'{:5.1f}'.format(ThesdHist[yy])+')'),xy=(0.05,0.93-(0*gap)),xycoords='axes fraction',size=fs,color='black')
        ax[yy].annotate(str('QC Pass ('+'{:5.1f}'.format(ThemeanQCHist[yy])+', '+'{:5.1f}'.format(ThesdQCHist[yy])+')'),xy=(0.05,0.93-(1*gap)),xycoords='axes fraction',size=fs,color='blue')
        ax[yy].annotate(str('QC Fail ('+'{:5.1f}'.format(ThemeanFHist[yy])+', '+'{:5.1f}'.format(ThesdFHist[yy])+', '+PctFail+')'),xy=(0.05,0.93-(2*gap)),xycoords='axes fraction',size=fs,color='red')
	
    		      
    #plt.savefig(FileName+".eps")
#    plt.savefig(FileName+"_n.png")
    plt.savefig(FileName+".png")

    return # PlotQCTest

#************************************************************************
# MAIN
#************************************************************************
def main(argv):
    # INPUT PARAMETERS AS STRINGS!!!!
    year1 = '1973' 
    year2 = '1973'
#    month1 = '01' # months must be 01, 02 etc
#    month2 = '12'
    typee = 'ERAclimNBC' # 'ERAclimNBC', 'OBSclim1NBC', 'OBSclim2NBC'
    varee = 'AT'	# 'AT','DPT','SHU','CRH'
    
    # TWEAK ME!!!!
    # What date stamp do you want on the files?
    nowmon = 'AUG'
    nowyear = '2018'

    try:
        opts, args = getopt.getopt(argv, "hi:",
#	                           ["year1=","year2=","month1=","month2=","typee=","varee="])
	                           ["year1=","year2=","typee=","varee="])
    except getopt.GetoptError:
        print 'Usage (as strings) PlotQCTest_SEP2016.py --year1 <1973> --year2 <1973> --typee <ERAclimNBC> --varee <AT>'
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
#        elif opt == "--month1":
#            try:
#                month1 = arg
#            except:
#                sys.exit("Failed: month1 not an integer")
#        elif opt == "--month2":
#            try:
#                month2 = arg
#            except:
#                sys.exit("Failed: month2 not an integer")
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

    print(year1, year2, typee, varee)
#    print(year1, year2, month1, month2, typee, varee)
#    pdb.set_trace()

    INDIR = '/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/'+typee+'/'
    INFIL = 'new_suite_'   # 199406_ERAclimNBC.txt.gz

    OUTDIR = '/data/local/hadkw/HADCRUH2/MARINE/IMAGES/QCHISTS/'
    EndStr = varee+'_'+typee+'_'+str('{:4s}'.format(year1)+'{:4s}'.format(year2))+'_'+nowmon+nowyear
    OutPltAbsday =    'SummaryObsDist_DAY_Abs_I300_55_'
    OutPltAbsngt =    'SummaryObsDist_NIGHT_Abs_I300_55_'
    OutPltAbs =       'SummaryObsDist_BOTH_Abs_I300_55_'
    OutPltAnomsday =  'SummaryObsDist_DAY_Anoms_I300_55_'
    OutPltAnomsngt =  'SummaryObsDist_NIGHT_Anoms_I300_55_'
    OutPltAnoms =     'SummaryObsDist_BOTH_Anoms_I300_55_'
    
    # set up histogram bins for this variable
    AbsBinsDict = dict([('AT',(-40.,66.,1.)),
                     ('DPT',(-50.,51.,1.)),
		     ('SHU',(0.,51.,1.)),
		     ('CRH',(0.,101.,2.))])
    AnomsBinsDict = dict([('AT',(-30.,31.,1.)),
                     ('DPT',(-30.,31.,1.)),
		     ('SHU',(-20.,21.,1.)),
		     ('CRH',(-80.,81.,2.))])
    AbsBins = np.arange(AbsBinsDict[varee][0],AbsBinsDict[varee][1],AbsBinsDict[varee][2])
    AnomsBins = np.arange(AnomsBinsDict[varee][0],AnomsBinsDict[varee][1],AnomsBinsDict[varee][2])
    print('Test the bins for: ',varee)
    #pdb.set_trace()
    
    # Howmany years?
    NYears = (int(year2) - int(year1)) +1
    
    # Initialise lists for storing histograms
    HistoListAbs=[]
    HistoListAnoms=[]
    HistoListAbsD=[]
    HistoListAnomsD=[]
    HistoListAbsN=[]
    HistoListAnomsN=[]

    QCHistoListAbs=[]
    QCHistoListAnoms=[]
    QCHistoListAbsD=[]
    QCHistoListAnomsD=[]
    QCHistoListAbsN=[]
    QCHistoListAnomsN=[]

    FHistoListAbs=[]
    FHistoListAnoms=[]
    FHistoListAbsD=[]
    FHistoListAnomsD=[]
    FHistoListAbsN=[]
    FHistoListAnomsN=[]
    
    MeanHistAbsD=[]
    MeanHistAbsN=[]
    MeanHistAbs=[]
    MeanHistAnomsD=[]
    MeanHistAnomsN=[]
    MeanHistAnoms=[]
    
    MeanQCHistAbsD=[]
    MeanQCHistAbsN=[]
    MeanQCHistAbs=[]
    MeanQCHistAnomsD=[]
    MeanQCHistAnomsN=[]
    MeanQCHistAnoms=[]
    
    MeanFHistAbsD=[]
    MeanFHistAbsN=[]
    MeanFHistAbs=[]
    MeanFHistAnomsD=[]
    MeanFHistAnomsN=[]
    MeanFHistAnoms=[]
    
    SDHistAbsD=[]
    SDHistAbsN=[]
    SDHistAbs=[]
    SDHistAnomsD=[]
    SDHistAnomsN=[]
    SDHistAnoms=[]
    
    SDQCHistAbsD=[]
    SDQCHistAbsN=[]
    SDQCHistAbs=[]
    SDQCHistAnomsD=[]
    SDQCHistAnomsN=[]
    SDQCHistAnoms=[]
    
    SDFHistAbsD=[]
    SDFHistAbsN=[]
    SDFHistAbs=[]
    SDFHistAnomsD=[]
    SDFHistAnomsN=[]
    SDFHistAnoms=[]

    # Loop through each year
    for yy in range(NYears):
    
        # Read in June and then December for that year
	ThisMonth = ['06','12'] 
	
	for mm in ThisMonth:

	    # Read in the MDSdict and pick out desired variable values (abs and anoms) and QC flags
            FileName = INDIR+INFIL+str(int(year1)+yy)+mm+'_'+typee+'.txt.gz'
	
            MDSdict = mrw.ReadMDSstandard(str(int(year1)+yy), mm, typee)

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
	    
	    # Create histograms for all options   
	    # Append each histogram to the list 
	    HistoListAbs.append(np.histogram(TheValsAbs[np.where(MDSdict['trk'] == 0)],AbsBins))
	    HistoListAnoms.append(np.histogram(TheValsAnoms[np.where(MDSdict['trk'] == 0)],AnomsBins))
	    HistoListAbsD.append(np.histogram(TheValsAbs[np.where((MDSdict['trk'] == 0) & (MDSdict['day'] == 1))],AbsBins))
	    HistoListAnomsD.append(np.histogram(TheValsAnoms[np.where((MDSdict['trk'] == 0) & (MDSdict['day'] == 1))],AnomsBins))
	    HistoListAbsN.append(np.histogram(TheValsAbs[np.where((MDSdict['trk'] == 0) & (MDSdict['day'] == 0))],AbsBins))
	    HistoListAnomsN.append(np.histogram(TheValsAnoms[np.where((MDSdict['trk'] == 0) & (MDSdict['day'] == 0))],AnomsBins))

	    MeanHistAbs.append(np.mean(TheValsAbs[np.where(MDSdict['trk'] == 0)]))
	    MeanHistAnoms.append(np.mean(TheValsAnoms[np.where(MDSdict['trk'] == 0)]))
	    MeanHistAbsD.append(np.mean(TheValsAbs[np.where((MDSdict['trk'] == 0) & (MDSdict['day'] == 1))]))
	    MeanHistAnomsD.append(np.mean(TheValsAnoms[np.where((MDSdict['trk'] == 0) & (MDSdict['day'] == 1))]))
	    MeanHistAbsN.append(np.mean(TheValsAbs[np.where((MDSdict['trk'] == 0) & (MDSdict['day'] == 0))]))
	    MeanHistAnomsN.append(np.mean(TheValsAnoms[np.where((MDSdict['trk'] == 0) & (MDSdict['day'] == 0))]))

	    SDHistAbs.append(np.std(TheValsAbs[np.where(MDSdict['trk'] == 0)]))
	    SDHistAnoms.append(np.std(TheValsAnoms[np.where(MDSdict['trk'] == 0)]))
	    SDHistAbsD.append(np.std(TheValsAbs[np.where((MDSdict['trk'] == 0) & (MDSdict['day'] == 1))]))
	    SDHistAnomsD.append(np.std(TheValsAnoms[np.where((MDSdict['trk'] == 0) & (MDSdict['day'] == 1))]))
	    SDHistAbsN.append(np.std(TheValsAbs[np.where((MDSdict['trk'] == 0) & (MDSdict['day'] == 0))]))
	    SDHistAnomsN.append(np.std(TheValsAnoms[np.where((MDSdict['trk'] == 0) & (MDSdict['day'] == 0))]))

    	    QCHistoListAbs.append(np.histogram(TheValsAbs[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0))],AbsBins))
	    QCHistoListAnoms.append(np.histogram(TheValsAnoms[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) & 
                                                              (MDSdict['DPTssat'] == 0))],AnomsBins))
	    QCHistoListAbsD.append(np.histogram(TheValsAbs[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0) &
							      (MDSdict['day'] == 1))],AbsBins))
	    QCHistoListAnomsD.append(np.histogram(TheValsAnoms[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0) &
							      (MDSdict['day'] == 1))],AnomsBins))
	    QCHistoListAbsN.append(np.histogram(TheValsAbs[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0) &
							      (MDSdict['day'] == 0))],AbsBins))
	    QCHistoListAnomsN.append(np.histogram(TheValsAnoms[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0) &
							      (MDSdict['day'] == 0))],AnomsBins))

    	    MeanQCHistAbs.append(np.mean(TheValsAbs[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0))]))
	    MeanQCHistAnoms.append(np.mean(TheValsAnoms[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) & 
                                                              (MDSdict['DPTssat'] == 0))]))
	    MeanQCHistAbsD.append(np.mean(TheValsAbs[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0) &
							      (MDSdict['day'] == 1))]))
	    MeanQCHistAnomsD.append(np.mean(TheValsAnoms[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0) &
							      (MDSdict['day'] == 1))]))
	    MeanQCHistAbsN.append(np.mean(TheValsAbs[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0) &
							      (MDSdict['day'] == 0))]))
	    MeanQCHistAnomsN.append(np.mean(TheValsAnoms[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0) &
							      (MDSdict['day'] == 0))]))

	    SDQCHistAbs.append(np.std(TheValsAbs[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0))]))
	    SDQCHistAnoms.append(np.std(TheValsAnoms[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) & 
                                                              (MDSdict['DPTssat'] == 0))]))
	    SDQCHistAbsD.append(np.std(TheValsAbs[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0) &
							      (MDSdict['day'] == 1))]))
	    SDQCHistAnomsD.append(np.std(TheValsAnoms[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0) &
							      (MDSdict['day'] == 1))]))
	    SDQCHistAbsN.append(np.std(TheValsAbs[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0) &
							      (MDSdict['day'] == 0))]))
	    SDQCHistAnomsN.append(np.std(TheValsAnoms[np.where((MDSdict['trk'] == 0) & 
	                                                      (MDSdict['ATclim'] == 0) &
                                                              (MDSdict['ATbud'] == 0) &
                                                              (MDSdict['ATrep'] == 0) & 
                                                              (MDSdict['DPTclim'] == 0) &
                                                              (MDSdict['DPTbud'] == 0) &
                                                              (MDSdict['DPTrep'] == 0) &
                                                              (MDSdict['DPTrepsat'] == 0) &
                                                              (MDSdict['DPTssat'] == 0) &
							      (MDSdict['day'] == 0))]))

	    FHistoListAbs.append(np.histogram(TheValsAbs[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1))],AbsBins))
	    FHistoListAnoms.append(np.histogram(TheValsAnoms[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) | 
                                                              (MDSdict['DPTssat'] == 1))],AnomsBins))
	    FHistoListAbsD.append(np.histogram(TheValsAbs[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1) &
							      (MDSdict['day'] == 1))],AbsBins))
	    FHistoListAnomsD.append(np.histogram(TheValsAnoms[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1) &
							      (MDSdict['day'] == 1))],AnomsBins))
	    FHistoListAbsN.append(np.histogram(TheValsAbs[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1) &
							      (MDSdict['day'] == 0))],AbsBins))
	    FHistoListAnomsN.append(np.histogram(TheValsAnoms[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1) &
							      (MDSdict['day'] == 0))],AnomsBins))

	    MeanFHistAbs.append(np.mean(TheValsAbs[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1))]))
	    MeanFHistAnoms.append(np.mean(TheValsAnoms[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) | 
                                                              (MDSdict['DPTssat'] == 1))]))
	    MeanFHistAbsD.append(np.mean(TheValsAbs[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1) &
							      (MDSdict['day'] == 1))]))
	    MeanFHistAnomsD.append(np.mean(TheValsAnoms[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1) &
							      (MDSdict['day'] == 1))]))
	    MeanFHistAbsN.append(np.mean(TheValsAbs[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1) &
							      (MDSdict['day'] == 0))]))
	    MeanFHistAnomsN.append(np.mean(TheValsAnoms[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1) &
							      (MDSdict['day'] == 0))]))

	    SDFHistAbs.append(np.std(TheValsAbs[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1))]))
	    SDFHistAnoms.append(np.std(TheValsAnoms[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) | 
                                                              (MDSdict['DPTssat'] == 1))]))
	    SDFHistAbsD.append(np.std(TheValsAbs[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1) &
							      (MDSdict['day'] == 1))]))
	    SDFHistAnomsD.append(np.std(TheValsAnoms[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1) &
							      (MDSdict['day'] == 1))]))
	    SDFHistAbsN.append(np.std(TheValsAbs[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1) &
							      (MDSdict['day'] == 0))]))
	    SDFHistAnomsN.append(np.std(TheValsAnoms[np.where((MDSdict['trk'] == 1) | 
	                                                      (MDSdict['ATclim'] == 1) |
                                                              (MDSdict['ATbud'] == 1) |
                                                              (MDSdict['ATrep'] == 1) | 
                                                              (MDSdict['DPTclim'] == 1) |
                                                              (MDSdict['DPTbud'] == 1) |
                                                              (MDSdict['DPTrep'] == 1) |
                                                              (MDSdict['DPTrepsat'] == 1) |
                                                              (MDSdict['DPTssat'] == 1) &
							      (MDSdict['day'] == 0))]))
	        
            # Clear up some memory
	    MDSdict = 0 # clear out

    # Pass plot title for each (abs/anoms/day/night/both), year range, histogram, variable, bins to plotter - PlotObsDist
    PlotObsDist(OUTDIR+OutPltAbsday+EndStr,year1,NYears,HistoListAbsD,QCHistoListAbsD,FHistoListAbsD,varee,AbsBins,'Hourly Daytime ',
                MeanHistAbsD,MeanQCHistAbsD,MeanFHistAbsD,SDHistAbsD,SDQCHistAbsD,SDFHistAbsD)

    PlotObsDist(OUTDIR+OutPltAbsngt+EndStr,year1,NYears,HistoListAbsN,QCHistoListAbsN,FHistoListAbsN,varee,AbsBins,'Hourly Nighttime ',
                MeanHistAbsN,MeanQCHistAbsN,MeanFHistAbsN,SDHistAbsN,SDQCHistAbsN,SDFHistAbsN)

    PlotObsDist(OUTDIR+OutPltAbs+EndStr,year1,NYears,HistoListAbs,QCHistoListAbs,FHistoListAbs,varee,AbsBins,'Hourly ',
                MeanHistAbs,MeanQCHistAbs,MeanFHistAbs,SDHistAbs,SDQCHistAbs,SDFHistAbs)

    PlotObsDist(OUTDIR+OutPltAnomsday+EndStr,year1,NYears,HistoListAnomsD,QCHistoListAnomsD,FHistoListAnomsD,varee,AnomsBins,
                'Hourly Daytime Anomalies ',
                MeanHistAnomsD,MeanQCHistAnomsD,MeanFHistAnomsD,SDHistAnomsD,SDQCHistAnomsD,SDFHistAnomsD)

    PlotObsDist(OUTDIR+OutPltAnomsngt+EndStr,year1,NYears,HistoListAnomsN,QCHistoListAnomsN,FHistoListAnomsN,varee,AnomsBins,
                'Hourly Nighttime Anomalies ',
                MeanHistAnomsN,MeanQCHistAnomsN,MeanFHistAnomsN,SDHistAnomsN,SDQCHistAnomsN,SDFHistAnomsN)

    PlotObsDist(OUTDIR+OutPltAnoms+EndStr,year1,NYears,HistoListAnoms,QCHistoListAnoms,FHistoListAnoms,varee,AnomsBins,
                'Hourly Anomalies ',
                MeanHistAnoms,MeanQCHistAnoms,MeanFHistAnoms,SDHistAnoms,SDQCHistAnoms,SDFHistAnoms)

    #pdb.set_trace()

    print("And were done")

if __name__ == '__main__':
    
    main(sys.argv[1:])

#************************************************************************
