#!/usr/local/sci/bin/python
# PYTHON2.7
# 
# Author: Kate Willett
# Created: 1 April 2016
# Last update: 1 April 2016
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/EUSTACE_SST_MAT/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code reads in the ICOADS data output from QC using MDS_basic_KATE and
# pulls out the height and instrument metadata to make diagnostic plots.
#
# Obs height as provided by HOT, HOB or possibly inferred from LOV, HOP or HOA.
# HOT and or HOB are not often present.
# Can we infer HOT/HOB from HOA or HOP of LOV?
# Generally, HOA is higher than HOP - not a clear relationship.
# Generally, HOA is ~12m higher than HOT or HOB but this needs to be tested across more months - does this change over time/latitude etc?
# Generally, LOV is ~10*HOT/HOB
# I'm now writing some code to read in groups of months, pull out LOV,HOA,HOP,HOT,HOB,PT - and also the type/exposure info TOT, EOT, TOH, EOH
#  - plots, EOT/EOH by latitude where 0 = none, 1 = aspirated/ventilated (A/VS), 2 = whirled (SG/SL/W), 3 = screen not aspirated (S/SN), 4 = unscreend (US)
#  - prints, number and % of obs with TOT, EOT, TOH and EOH present
#  - plots, HOB, HOT, HOA, HOP, LOV (second axis?) by latitude
#  - prints, number and % of obs with HOB, HOT, HOA, HOP and LOV
#  - plots, HOB, HOT, HOA, HOP, LOV histogram
#  - prints, mean and standard deviation
#  - plots, HOA vs HOT, HOA vs HOB, HOP vs HOB, HOP vs HOT with lines of best fit
#  - prints, number and % where HOA and HOT present, HOA and HOB present, HOP and HOB present, HOP and HOT present, print equation for fit
#  - plots, HOA - HOT, HOA - HOB, HOP - HOB and HOP - HOT with
#  - prints, mean and standard deviation of difference series
#  - plots, LOV vs HOT, LOV vs HOB with lines of best fit
#  - prints, number and % where LOV and HOB present, where LOV and HOT present and equations for fit
#  - plots, LOV / HOT, LOV / HOB
#  - prints, mean and standard deviation of ratios
#
# This program creates two figures (pngs - can output eps if line is uncommented) and a text file that is appended to with each run
# Ideally You would run for each year
#
# This program has a switch for:
# switch = 'all' # include all obs
# switch = 'ships' # include only ships with PT = 0, 1, 2, 3, 4, 5
# switch = 'buoys' # include only those obs with PT = 6(moored), 8(ice) 
# switch = 'platforms' # include only those obs with PT = 9(ice), 10(oceanographic), 15 (fixed ocean)
# Also now outputs total number of obs (in switch category)
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
# /project/hadobs2/hadisdh/marine/ICOADS.2.5.1/EARclimNBC/new_suite_197312_ERAclimNBC.txt
#
# -----------------------
# HOW TO RUN THE CODE
# -----------------------
# set up date cluster choices
# year1, year2, month1, month2
#
# python2.7 PLotMetaData_APR2016
#
# This runs the code, outputs the plots and stops mid-process so you can then interact with the
# data. 
# 
# -----------------------
# OUTPUT
# -----------------------
# some plots:
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/InstrumentMetaDataDiags_all_ERAclimNBC_y1y2m1m2_APR2016.png
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/HeightMetaDataDiags_all_ERAclimNBC_y1y2m1m2_APR2016.png
#
# a text file of stats
# /data/local/hadkw/HADCRUH2/MARINE/LISTS/InstrumentMetaDataStats_all_ERAclimNBC_APR2016.txt
# /data/local/hadkw/HADCRUH2/MARINE/LISTS/HeightMetaDataStats_all_ERAclimNBC_APR2016.txt
# 
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
# 
# Version 1 (1 April 2016)
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
import matplotlib
matplotlib.use('Agg')
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

#from LinearTrends import MedianPairwise 
import MDS_basic_KATE as MDStool

#************************************************************************
# Main
#************************************************************************

def main(argv):
    # TextOn = 1 means output stats to text file, 0 means plots only
    TextOn = 0
    
    # INPUT PARAMETERS AS STRINGS!!!!
    year1 = '2000' 
    year2 = '2000'
    month1 = '01' # months must be 01, 02 etc
    month2 = '01'
    typee = 'ERAclimNBC'

    # MANUAL SWITCH FOR PLATFORM TYPE
    # switch = 'all' # include all obs
    # switch = 'ships' # include only ships with PT = 0, 1, 2, 3, 4, 5 - can be ships0, ships1, ships2, ships3, ships4, ships5
    # switch = 'buoys' # include only those obs with PT = 6(moored), 8(ice) - can be buoys6, buoys8 (but very little point as no metadata!)
    # switch = 'platforms' # include only those obs with PT = 9(ice), 10(oceanographic), 15 (fixed ocean) NO METADATA!!!
    switch = 'all'

    try:
        opts, args = getopt.getopt(argv, "hi:",
	                           ["year1=","year2=","month1=","month2=","typee=","switch="])
    except getopt.GetoptError:
        print 'Usage (as strings) PlotMetaData_APR2016.py --year1 <1973> --year2 <1973> '+\
	      '--month1 <01> --month2 <12> --typee <ERAclimNBC> --switch <ships>'
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
        elif opt == "--switch":
            try:
                switch = arg
		print(arg,switch)
            except:
                switch = 'all'

    assert year1 != -999 and year2 != -999, "Year not specified."

    print(year1, year2, month1, month2, typee, switch)
#    pdb.set_trace()
    					   
    #INDIR = '/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/ERAclimNBC/'
    #INFIL = 'new_suite_'
    #INEXT = '_'+typee+'.txt'

    #OUTDIR = '/data/local/hadkw/HADCRUH2/MARINE/'
    OUTDIR = ''
    OutRoundsPltAT = 'IMAGES/DecimalFreqDiagsAT_'+switch+'_'+typee+'_'+year1+year2+month1+month2+'_APR2016'
    OutRoundsTxtAT = 'LISTS/DecimalFreqStatsAT_'+switch+'_'+typee+'_APR2016.txt'
    OutRoundsPltDPT = 'IMAGES/DecimalFreqDiagsDPT_'+switch+'_'+typee+'_'+year1+year2+month1+month2+'_APR2016'
    OutRoundsTxtDPT = 'LISTS/DecimalFreqStatsDPT_'+switch+'_'+typee+'_APR2016.txt'

    OutDecksTxt = 'LISTS/DeckStats_'+switch+'_'+typee+'_APR2016.txt'
    
    # create empty arrays for data bundles
    nobs=0 # we're looking at all obs, not just those with 'good' data
    ATbun = []
    DPTbun = []
    ATRbun = []
    DPTRbun = []
    DCKbun = []

    # loop through each month, read in data, keep metadata needed
    for yy in range((int(year2)+1)-int(year1)):
        for mm in range((int(month2)+1)-int(month1)):
            print(str(yy+int(year1)),' ','{:02}'.format(mm+int(month1)))

            MDSdict=MDStool.ReadMDSkate(str(yy+int(year1)),'{:02}'.format(mm+int(month1)), typee)

	    if (nobs == 0):
	        if (switch == 'all'):
	            ATbun = MDSdict['AT']
	            DPTbun = MDSdict['DPT']
	            ATRbun = MDSdict['ATround']
	            DPTRbun = MDSdict['DPTround']
	            DCKbun = MDSdict['DCK']
                else:
		    if (switch[0:5] == 'ships'):
		        if (switch == 'ships'):
		            pointers = np.where(MDSdict['PT'] <= 5)[0]
		        elif (switch == 'ships0'):
			    pointers = np.where(MDSdict['PT'] == 0)[0]
		        elif (switch == 'ships1'):
			    pointers = np.where(MDSdict['PT'] == 1)[0]
		        elif (switch == 'ships2'):
			    pointers = np.where(MDSdict['PT'] == 2)[0]
		        elif (switch == 'ships3'):
			    pointers = np.where(MDSdict['PT'] == 3)[0]
		        elif (switch == 'ships4'):
			    pointers = np.where(MDSdict['PT'] == 4)[0]
		        elif (switch == 'ships5'):
			    pointers = np.where(MDSdict['PT'] == 5)[0]
		    elif (switch == 'buoys'):
		        pointers = np.where((MDSdict['PT'] == 6) | (MDSdict['PT'] == 8))[0]
		    elif (switch == 'platforms'):
		        pointers = np.where(MDSdict['PT'] >= 9)[0] # ok because only 9, 10 or 15 should be present	
	            ATbun = MDSdict['AT'][pointers]
	            DPTbun = MDSdict['DPT'][pointers]
	            ATRbun = MDSdict['ATround'][pointers]
	            DPTRbun = MDSdict['DPTround'][pointers]
	            DCKbun = MDSdict['DCK'][pointers]
            else:
	        if (switch == 'all'):
	            ATbun = np.append(ATbun,MDSdict['AT'])
	            DPTbun = np.append(DPTbun,MDSdict['DPT'])
	            ATRbun = np.append(ATRbun,MDSdict['ATround'])
	            DPTRbun = np.append(DPTRbun,MDSdict['DPTround'])
	            DCKbun = np.append(DCKbun,MDSdict['DCK'])
                else:
		    if (switch[0:5] == 'ships'):
		        if (switch == 'ships'):
		            pointers = np.where(MDSdict['PT'] <= 5)[0]
		        elif (switch == 'ships0'):
			    pointers = np.where(MDSdict['PT'] == 0)[0]
		        elif (switch == 'ships1'):
			    pointers = np.where(MDSdict['PT'] == 1)[0]
		        elif (switch == 'ships2'):
			    pointers = np.where(MDSdict['PT'] == 2)[0]
		        elif (switch == 'ships3'):
			    pointers = np.where(MDSdict['PT'] == 3)[0]
		        elif (switch == 'ships4'):
			    pointers = np.where(MDSdict['PT'] == 4)[0]
		        elif (switch == 'ships5'):
			    pointers = np.where(MDSdict['PT'] == 5)[0]
		    elif (switch == 'buoys'):
		        pointers = np.where((MDSdict['PT'] == 6) | (MDSdict['PT'] == 8))[0]
		    elif (switch == 'platforms'):
		        pointers = np.where(MDSdict['PT'] >= 9)[0] # ok because only 9, 10 or 15 should be present	
	            ATbun = np.append(ATbun,MDSdict['AT'][pointers])
	            DPTbun = np.append(DPTbun,MDSdict['DPT'][pointers])
	            ATRbun = np.append(ATRbun,MDSdict['ATround'][pointers])
	            DPTRbun = np.append(DPTRbun,MDSdict['DPTround'][pointers])
	            DCKbun = np.append(DCKbun,MDSdict['DCK'][pointers])
	
            if (switch == 'all'):
	        nobs = nobs + len(MDSdict['AT'])
	    else:
	        nobs = nobs + len(MDSdict['AT'][pointers])
	        
	    MDSdict = 0 # clear out
	
    # set up generall plotting stuff
    # set up dimensions and plot - this is a 2 by 2 plot

    #  - plots, EOT/EOH by latitude where 1 = none, 2 = aspirated/ventilated (A/VS), 3 = whirled (SG/SL/W), 4 = screen not aspirated (S/SN), 5 = unscreend (US)
    #  - prints, number and % of obs with EOT and EOH present, and in the categories
    histeeALL = np.histogram(DPTbun-np.floor(DPTbun),np.arange(-0.05,1.05,0.1)) # or np.linspace(-0.05,0.95,11)

    UniqDecks = np.unique(DCKbun)
    gap= 0.03
    cols = ['red','orange','gold','green','blue','indigo','violet','red','orange','gold','green','blue','indigo','violet','red','orange','gold','green','blue','indigo','violet','red','orange','gold','green','blue','indigo','violet',]
    lins = ['-','-','-','-','-','-','-','--','--','--','--','--','--','--',':',':',':',':',':',':',':','-.','-.','-.','-.','-.','-.','-.']
    linstext = ['solid','solid','solid','solid','solid','solid','solid','dashed','dashed','dashed','dashed','dashed','dashed','dashed','dotted','dotted','dotted','dotted','dotted','dotted','dotted','dotdash','dotdash','dotdash','dotdash','dotdash','dotdash','dotdash']
    
    plt.clf()
    fig, ax1 = plt.subplots()
    ax1.plot(histeeALL[1][0:10]+0.05,histeeALL[0],c='black')
    ax1.set_xlabel('Decimal Places')
    ax1.set_ylabel('No. of Obs (ALL)', color='black')
    ax2 = ax1.twinx()
    for i,dck in enumerate(UniqDecks):
        histee = np.histogram(DPTbun[np.where(DCKbun == dck)[0]]-np.floor(DPTbun[np.where(DCKbun == dck)[0]]),np.arange(-0.05,1.05,0.1)) # or np.linspace(-0.05,0.95,11)
        ax2.plot(histee[1][0:10]+0.05,histee[0],c=cols[i],linestyle=lins[i],linewidth=2)
        PctRounds = 0.
        if (len(np.where((DCKbun == dck) & (DPTRbun == 1))[0]) > 0):
            PctRounds = (float(len(np.where((DCKbun == dck) & (DPTRbun == 1))[0]))/float(len(np.where(DCKbun == dck)[0])))*100.
        ax2.annotate("{:3d}".format(dck)+' '+linstext[i]+"{:6.2f}".format(PctRounds)+'%',xy=(0.65,0.96-(i*gap)),xycoords='axes fraction',size=10,color=cols[i])

    ax2.set_ylabel('No. of Obs (DECKS)', color='black')
    plt.tight_layout()

#    plt.savefig(OUTDIR+OutRoundsPltDPT+".eps")
    plt.savefig(OUTDIR+OutRoundsPltDPT+".png")

    if (TextOn == 1):
        # Write out stats to file (append!)
        filee=open(OUTDIR+OutRoundsTxtDPT,'a+')
        Pct0s = 0.
        Pct1s = 0.
        Pct2s = 0.
        Pct3s = 0.
        Pct4s = 0.
        Pct5s = 0.
        Pct6s = 0.
        Pct7s = 0.
        Pct8s = 0.
        Pct9s = 0.
        if (histeeALL[0][0] > 0):
	    Pct0s = (float(histeeALL[0][0])/float(nobs))*100.
        if (histeeALL[0][1] > 0):
	    Pct1s = (float(histeeALL[0][1])/float(nobs))*100.
        if (histeeALL[0][2] > 0):
	    Pct2s = (float(histeeALL[0][2])/float(nobs))*100.
        if (histeeALL[0][3] > 0):
	    Pct3s = (float(histeeALL[0][3])/float(nobs))*100.
        if (histeeALL[0][4] > 0):
	    Pct4s = (float(histeeALL[0][4])/float(nobs))*100.
        if (histeeALL[0][5] > 0):
	    Pct5s = (float(histeeALL[0][5])/float(nobs))*100.
        if (histeeALL[0][6] > 0):
	    Pct6s = (float(histeeALL[0][6])/float(nobs))*100.
        if (histeeALL[0][7] > 0):
	    Pct7s = (float(histeeALL[0][7])/float(nobs))*100.
        if (histeeALL[0][8] > 0):
	    Pct8s = (float(histeeALL[0][8])/float(nobs))*100.
        if (histeeALL[0][9] > 0):
	    Pct9s = (float(histeeALL[0][9])/float(nobs))*100.
        
        filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(nobs)+\
							  ' 0s '+'{:8d}'.format(histeeALL[0][0])+' ('+"{:6.2f}".format(Pct0s)+\
							  '%) 1s: '+'{:8d}'.format(histeeALL[0][1])+' ('+"{:6.2f}".format(Pct1s)+\
							  '%) 2s: '+'{:8d}'.format(histeeALL[0][2])+' ('+"{:6.2f}".format(Pct2s)+\
							  '%) 3s: '+'{:8d}'.format(histeeALL[0][3])+' ('+"{:6.2f}".format(Pct3s)+\
							  '%) 4s: '+'{:8d}'.format(histeeALL[0][4])+' ('+"{:6.2f}".format(Pct4s)+\
							  '%) 5s: '+'{:8d}'.format(histeeALL[0][5])+' ('+"{:6.2f}".format(Pct5s)+\
							  '%) 6s: '+'{:8d}'.format(histeeALL[0][6])+' ('+"{:6.2f}".format(Pct6s)+\
							  '%) 7s: '+'{:8d}'.format(histeeALL[0][7])+' ('+"{:6.2f}".format(Pct7s)+\
							  '%) 8s: '+'{:8d}'.format(histeeALL[0][8])+' ('+"{:6.2f}".format(Pct8s)+\
							  '%) 9s: '+'{:8d}'.format(histeeALL[0][9])+' ('+"{:6.2f}".format(Pct9s)+\
							 '%)\n'))
        filee.close()

    histeeALL = np.histogram(ATbun-np.floor(ATbun),np.arange(-0.05,1.05,0.1)) # or np.linspace(-0.05,0.95,11)

    plt.clf()
    fig, ax1 = plt.subplots()
    ax1.plot(histeeALL[1][0:10]+0.05,histeeALL[0],c='black')
    ax1.set_xlabel('Decimal Places')
    ax1.set_ylabel('No. of Obs (ALL)', color='black')
    ax2 = ax1.twinx()
    for i,dck in enumerate(UniqDecks):
        histee = np.histogram(ATbun[np.where(DCKbun == dck)[0]]-np.floor(ATbun[np.where(DCKbun == dck)[0]]),np.arange(-0.05,1.05,0.1)) # or np.linspace(-0.05,0.95,11)
        ax2.plot(histee[1][0:10]+0.05,histee[0],c=cols[i],linestyle=lins[i],linewidth=2)
        PctRounds = 0.
        if (len(np.where((DCKbun == dck) & (ATRbun == 1))[0]) > 0):
            PctRounds = (float(len(np.where((DCKbun == dck) & (ATRbun == 1))[0]))/float(len(np.where(DCKbun == dck)[0])))*100.
        ax2.annotate("{:3d}".format(dck)+' '+linstext[i]+"{:6.2f}".format(PctRounds)+'%',xy=(0.65,0.96-(i*gap)),xycoords='axes fraction',size=10,color=cols[i])

    ax2.set_ylabel('No. of Obs (DECKS)', color='black')
    plt.tight_layout()

#    plt.savefig(OUTDIR+OutRoundsPltAT+".eps")
    plt.savefig(OUTDIR+OutRoundsPltAT+".png")

    if (TextOn == 1):
        # Write out stats to file (append!)
        filee=open(OUTDIR+OutRoundsTxtAT,'a+')
        Pct0s = 0.
        Pct1s = 0.
        Pct2s = 0.
        Pct3s = 0.
        Pct4s = 0.
        Pct5s = 0.
        Pct6s = 0.
        Pct7s = 0.
        Pct8s = 0.
        Pct9s = 0.
        if (histeeALL[0][0] > 0):
	    Pct0s = (float(histeeALL[0][0])/float(nobs))*100.
        if (histeeALL[0][1] > 0):
	    Pct1s = (float(histeeALL[0][1])/float(nobs))*100.
        if (histeeALL[0][2] > 0):
	    Pct2s = (float(histeeALL[0][2])/float(nobs))*100.
        if (histeeALL[0][3] > 0):
	    Pct3s = (float(histeeALL[0][3])/float(nobs))*100.
        if (histeeALL[0][4] > 0):
	    Pct4s = (float(histeeALL[0][4])/float(nobs))*100.
        if (histeeALL[0][5] > 0):
	    Pct5s = (float(histeeALL[0][5])/float(nobs))*100.
        if (histeeALL[0][6] > 0):
	    Pct6s = (float(histeeALL[0][6])/float(nobs))*100.
        if (histeeALL[0][7] > 0):
	    Pct7s = (float(histeeALL[0][7])/float(nobs))*100.
        if (histeeALL[0][8] > 0):
	    Pct8s = (float(histeeALL[0][8])/float(nobs))*100.
        if (histeeALL[0][9] > 0):
	    Pct9s = (float(histeeALL[0][9])/float(nobs))*100.
        
        filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(nobs)+\
							  ' 0s '+'{:8d}'.format(histeeALL[0][0])+' ('+"{:6.2f}".format(Pct0s)+\
							  '%) 1s: '+'{:8d}'.format(histeeALL[0][1])+' ('+"{:6.2f}".format(Pct1s)+\
							  '%) 2s: '+'{:8d}'.format(histeeALL[0][2])+' ('+"{:6.2f}".format(Pct2s)+\
							  '%) 3s: '+'{:8d}'.format(histeeALL[0][3])+' ('+"{:6.2f}".format(Pct3s)+\
							  '%) 4s: '+'{:8d}'.format(histeeALL[0][4])+' ('+"{:6.2f}".format(Pct4s)+\
							  '%) 5s: '+'{:8d}'.format(histeeALL[0][5])+' ('+"{:6.2f}".format(Pct5s)+\
							  '%) 6s: '+'{:8d}'.format(histeeALL[0][6])+' ('+"{:6.2f}".format(Pct6s)+\
							  '%) 7s: '+'{:8d}'.format(histeeALL[0][7])+' ('+"{:6.2f}".format(Pct7s)+\
							  '%) 8s: '+'{:8d}'.format(histeeALL[0][8])+' ('+"{:6.2f}".format(Pct8s)+\
							  '%) 9s: '+'{:8d}'.format(histeeALL[0][9])+' ('+"{:6.2f}".format(Pct9s)+\
							 '%)\n'))
        filee.close()

    AllDcks = [' -1','128','144','223','224','229','233','234','239','254',
               '255','555','666','700','732','735','740','749','780','792',
	       '793','794','849','850','874','876','877','878','883','888',
	       '889','892','893','896','898','900','926','927','928','992',
	       '993','994','995']
    if (TextOn == 1):
        filee=open(OUTDIR+OutDecksTxt,'a+')
        output=''
        for i,dck in enumerate(AllDcks):
            TotDck = 0
	    PctDck = 0.
	    if (int(dck) in UniqDecks):
                TotDck = len(np.where(DCKbun == int(dck))[0])
	        PctDck = (float(TotDck)/float(nobs))*100.
	    output = output+' '+"{:3d}".format(int(dck))+': '+"{:8d}".format(TotDck)+' ('+"{:6.2f}".format(PctDck)+'%)'

            filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(nobs)+\
                                                             output+\
							     '\n'))
        filee.close()

    #pdb.set_trace()

if __name__ == '__main__':
    
    main(sys.argv[1:])




#************************************************************************
