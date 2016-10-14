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
#  - plots, HOP vs HOA, HOA vs HOT, HOA vs HOB, HOP vs HOB, HOP vs HOT with lines of best fit
#  - prints, number and % where HOP and HOA present, HOA and HOT present, HOA and HOB present, HOP and HOB present, HOP and HOT present, print equation for fit
#  - plots, HOA - HOP, HOA - HOT, HOA - HOB, HOP - HOB and HOP - HOT with
#  - prints, mean and standard deviation of difference series
#  - plots, LOV vs HOT, LOV vs HOB with lines of best fit
#  - prints, number and % where LOV and HOB present, where LOV and HOT present and equations for fit
#  - plots, LOV / HOT, LOV / HOB
#  - prints, mean and standard deviation of ratios
#
# This program creates two figures (pngs - can output eps if line is uncommented) and a text file that is appended to with each run
# Ideally You would run for each year
#  
# -----------------------
# LIST OF MODULES
# -----------------------
# inbuilt:
# import datetime as dt
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
# import MDS_RWtools as MDStool
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
# python2.7 PLotMetaData_APR2016 --year1 2000 --year2 2000 --month1 01 --month2 12 --typee ERAclimNBC
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
# Version 2 (13 October 2016)
# ---------
#  
# Enhancements
#  
# Changes
# Instrument Exposure
# This now has A (aspirated) on its own and merges VS (ventilated screen) with S (screen) and SN (ships screen)
#  
# Bug fixes
# The missing %) has been fixed 
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
# So there really isn't much information for buoys or platforms (or many ships other than PT=5)
# A tiny number of buoys say they have height info - height = 74m - UNLIKELY!!!
# No platforms have height info
# Some buoys have exposure info - all info says US (unscreened) - therefore shouldn't need a bias correction?
# No platgorms have exposure info
#
#************************************************************************
#                                 START
#************************************************************************
#import datetime as dt
import matplotlib
# use the Agg environment to generate an image rather than outputting to screen
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
#from matplotlib.dates import date2num,num2date
import sys, os
import sys, getopt
#from scipy.optimize import curve_fit,fsolve,leastsq
#from scipy import pi,sqrt,exp
#from scipy.special import erf
#import scipy.stats
#from math import sqrt,pi
#import struct
import pdb # pdb.set_trace() or c 

#from LinearTrends import MedianPairwise 
import MDS_RWtools as MDStool

# changeable variables
# Which month/year is this being run?
nowmon = 'OCT'
nowyear = '2016'

# Which ICOADS source are you using - check MDS_RWtools.py!!!
source = 'I300'

#************************************************************************
# Main
#************************************************************************

def main(argv):
    # INPUT PARAMETERS AS STRINGS!!!!
    year1 = '2000' 
    year2 = '2000'
    month1 = '01' # months must be 01, 02 etc
    month2 = '12'
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
	      '--month1 <01> --month2 <12>'
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

#    OUTDIR = '/data/local/hadkw/HADCRUH2/MARINE/'
    OUTDIR = ''
    OutTypeFil = 'IMAGES/InstrTypeMetaDataDiags_'+switch+'_'+typee+'_'+year1+year2+month1+month2+'_'+source+'_'+nowmon+nowyear
    OutInstrFil = 'IMAGES/InstrumentMetaDataDiags_'+switch+'_'+typee+'_'+year1+year2+month1+month2+'_'+source+'_'+nowmon+nowyear
    OutHeightFil = 'IMAGES/HeightMetaDataDiags_'+switch+'_'+typee+'_'+year1+year2+month1+month2+'_'+source+'_'+nowmon+nowyear
    OutTypeText = 'LISTS/InstrTypeMetaDataStats_'+switch+'_'+typee+'_'+source+'_'+nowmon+nowyear+'.txt'
    OutInstrumentText = 'LISTS/InstrumentMetaDataStats_'+switch+'_'+typee+'_'+source+'_'+nowmon+nowyear+'.txt'
    OutHeightText = 'LISTS/HeightMetaDataStats_'+switch+'_'+typee+'_'+source+'_'+nowmon+nowyear+'.txt'
    
    # create empty arrays for data bundles
    nobs=0 # we're looking at all obs, not just those with 'good' data
    LATbun = []
    EOTbun = []
    TOHbun = []
    EOHbun = []
    LOVbun = []
    HOTbun = []
    HOBbun = []
    HOAbun = []
    HOPbun = []

    # loop through each month, read in data, keep metadata needed
    for yy in range((int(year2)+1)-int(year1)):
        for mm in range((int(month2)+1)-int(month1)):
            print(str(yy+int(year1)),' ','{:02}'.format(mm+int(month1)))

            MDSdict=MDStool.ReadMDSstandard(str(yy+int(year1)),'{:02}'.format(mm+int(month1)), typee)

	    if (nobs == 0):
	        if (switch == 'all'):
	            LATbun = MDSdict['LAT']
	            EOTbun = MDSdict['EOT']
	            TOHbun = MDSdict['TOH']
	            EOHbun = MDSdict['EOH']
	            LOVbun = MDSdict['LOV']
	            HOTbun = MDSdict['HOT']
	            HOBbun = MDSdict['HOB']
	            HOAbun = MDSdict['HOA']
	            HOPbun = MDSdict['HOP']
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
	            LATbun = MDSdict['LAT'][pointers]
	            EOTbun = MDSdict['EOT'][pointers]
	            TOHbun = MDSdict['TOH'][pointers]
	            EOHbun = MDSdict['EOH'][pointers]
	            LOVbun = MDSdict['LOV'][pointers]
	            HOTbun = MDSdict['HOT'][pointers]
	            HOBbun = MDSdict['HOB'][pointers]
	            HOAbun = MDSdict['HOA'][pointers]
	            HOPbun = MDSdict['HOP'][pointers]
            else:
	        if (switch == 'all'):
	            LATbun = np.append(LATbun,MDSdict['LAT'])
	            EOTbun = np.append(EOTbun,MDSdict['EOT'])
	            TOHbun = np.append(TOHbun,MDSdict['TOH'])
	            EOHbun = np.append(EOHbun,MDSdict['EOH'])
	            LOVbun = np.append(LOVbun,MDSdict['LOV'])
	            HOTbun = np.append(HOTbun,MDSdict['HOT'])
	            HOBbun = np.append(HOBbun,MDSdict['HOB'])
	            HOAbun = np.append(HOAbun,MDSdict['HOA'])
	            HOPbun = np.append(HOPbun,MDSdict['HOP'])
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
	            LATbun = np.append(LATbun,MDSdict['LAT'][pointers])
	            EOTbun = np.append(EOTbun,MDSdict['EOT'][pointers])
	            TOHbun = np.append(TOHbun,MDSdict['TOH'][pointers])
	            EOHbun = np.append(EOHbun,MDSdict['EOH'][pointers])
	            LOVbun = np.append(LOVbun,MDSdict['LOV'][pointers])
	            HOTbun = np.append(HOTbun,MDSdict['HOT'][pointers])
	            HOBbun = np.append(HOBbun,MDSdict['HOB'][pointers])
	            HOAbun = np.append(HOAbun,MDSdict['HOA'][pointers])
	            HOPbun = np.append(HOPbun,MDSdict['HOP'][pointers])
	
            if (switch == 'all'):
	        nobs = nobs + len(MDSdict['LAT'])
	    else:
	        nobs = nobs + len(MDSdict['LAT'][pointers])
	        
	    MDSdict = 0 # clear out
	
    # set up generall plotting stuff
    # set up dimensions and plot - this is a 2 by 2 plot
    #  - plots, TOH by latitude where 1 = hygristor, 2 = chilled mirror, 3 = other, C = capacitance, E = electric, H = hair hygrometer, P = psychrometer, T = torsion
    #  - prints, number and % of obs with TOH present, and in the categories
    plt.clf()
    fig=plt.figure(figsize=(6,8)) 
    ax=plt.axes([0.1,0.1,0.85,0.7])
    plt.xlim(0,9)
    plt.ylim(-91,91)
    plt.xlabel('Instrument Type Category')
    plt.ylabel('Latitude')
    locs = ax.get_xticks().tolist()
    labels=[x.get_text() for x in ax.get_xticklabels()]
    labels[1] = '1'
    labels[2] = '2'
    labels[3] = '3'
    labels[4] = 'C'
    labels[5] = 'E'
    labels[6] = 'H'
    labels[7] = 'P'
    labels[8] = 'T'
    ax.set_xticks(locs)
    ax.set_xticklabels(labels)
    gotTOHs = np.where(TOHbun != 'No')[0]
    Hgot1s = np.where(np.char.strip(TOHbun) == '1')[0]
    Hgot2s = np.where(np.char.strip(TOHbun) == '2')[0]
    Hgot3s = np.where(np.char.strip(TOHbun) == '3')[0]
    HgotCs = np.where(np.char.strip(TOHbun) == 'C')[0]
    HgotEs = np.where(np.char.strip(TOHbun) == 'E')[0]
    HgotHs = np.where(np.char.strip(TOHbun) == 'H')[0]
    HgotPs = np.where(np.char.strip(TOHbun) == 'P')[0]
    HgotTs = np.where(np.char.strip(TOHbun) == 'T')[0]
    Hgot1spct = 0.
    Hgot2spct = 0.
    Hgot3spct = 0.
    HgotCspct = 0.
    HgotEspct = 0.
    HgotHspct = 0.
    HgotPspct = 0.
    HgotTspct = 0.
    Hgotspct = 0.
    if (nobs > 0):
	Hgotspct = (len(gotTOHs)/float(nobs))*100
    if (len(Hgot1s) > 0):
	Hgot1spct = (len(Hgot1s)/float(len(gotTOHs)))*100
	plt.scatter(np.repeat(1,len(Hgot1s)),LATbun[Hgot1s],c='grey',marker='o',linewidth=0.,s=12)
    if (len(Hgot2s) > 0):
	Hgot2spct = (len(Hgot2s)/float(len(gotTOHs)))*100
	plt.scatter(np.repeat(2,len(Hgot2s)),LATbun[Hgot2s],c='red',marker='o',linewidth=0.,s=12)
    if (len(Hgot3s) > 0):
	Hgot3spct = (len(Hgot3s)/float(len(gotTOHs)))*100
	plt.scatter(np.repeat(3,len(Hgot3s)),LATbun[Hgot3s],c='orange',marker='o',linewidth=0.,s=12)
    if (len(HgotCs) > 0):
	HgotCspct = (len(HgotCs)/float(len(gotTOHs)))*100
	plt.scatter(np.repeat(4,len(HgotCs)),LATbun[HgotCs],c='gold',marker='o',linewidth=0.,s=12)
    if (len(HgotEs) > 0):
	HgotEspct = (len(HgotEs)/float(len(gotTOHs)))*100
	plt.scatter(np.repeat(5,len(HgotEs)),LATbun[HgotEs],c='green',marker='o',linewidth=0.,s=12)
    if (len(HgotHs) > 0):
	HgotHspct = (len(HgotHs)/float(len(gotTOHs)))*100
	plt.scatter(np.repeat(6,len(HgotHs)),LATbun[HgotHs],c='blue',marker='o',linewidth=0.,s=12)
    if (len(HgotPs) > 0):
	HgotPspct = (len(HgotPs)/float(len(gotTOHs)))*100
	plt.scatter(np.repeat(7,len(HgotPs)),LATbun[HgotPs],c='indigo',marker='o',linewidth=0.,s=12)
    if (len(HgotTs) > 0):
	HgotTspct = (len(HgotTs)/float(len(gotTOHs)))*100
	plt.scatter(np.repeat(8,len(HgotTs)),LATbun[HgotTs],c='violet',marker='o',linewidth=0.,s=12)
    plt.annotate('TOH: '+str(len(gotTOHs))+' ('+"{:5.2f}".format(Hgotspct)+'%)',xy=(0.05,1.21),xycoords='axes fraction',size=12,color='black')
    plt.annotate('1: '+str(len(Hgot1s))+' ('+"{:5.2f}".format(Hgot1spct)+'%)',xy=(0.05,1.16),xycoords='axes fraction',size=12,color='grey')
    plt.annotate('2: '+str(len(Hgot2s))+' ('+"{:5.2f}".format(Hgot2spct)+'%)',xy=(0.05,1.11),xycoords='axes fraction',size=12,color='red')
    plt.annotate('3: '+str(len(Hgot3s))+' ('+"{:5.2f}".format(Hgot3spct)+'%)',xy=(0.05,1.06),xycoords='axes fraction',size=12,color='orange')
    plt.annotate('C: '+str(len(HgotCs))+' ('+"{:5.2f}".format(HgotCspct)+'%)',xy=(0.05,1.01),xycoords='axes fraction',size=12,color='gold')
    plt.annotate('E: '+str(len(HgotEs))+' ('+"{:5.2f}".format(HgotEspct)+'%)',xy=(0.55,1.16),xycoords='axes fraction',size=12,color='green')
    plt.annotate('H: '+str(len(HgotHs))+' ('+"{:5.2f}".format(HgotHspct)+'%)',xy=(0.55,1.11),xycoords='axes fraction',size=12,color='blue')
    plt.annotate('P: '+str(len(HgotPs))+' ('+"{:5.2f}".format(HgotPspct)+'%)',xy=(0.55,1.06),xycoords='axes fraction',size=12,color='indigo')
    plt.annotate('T: '+str(len(HgotTs))+' ('+"{:5.2f}".format(HgotTspct)+'%)',xy=(0.55,1.01),xycoords='axes fraction',size=12,color='violet')
    #plt.tight_layout()
    
#    plt.savefig(OUTDIR+OutTypeFil+".eps")
    plt.savefig(OUTDIR+OutTypeFil+".png")

    # Write out stats to file (append!)
    filee=open(OUTDIR+OutTypeText,'a+')
    filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(nobs)+\
							  ' TOH: '+'{:8d}'.format(len(gotTOHs))+' ('+"{:5.2f}".format(Hgotspct)+\
							  '%) 1: '+'{:8d}'.format(len(Hgot1s))+' ('+"{:5.2f}".format(Hgot1spct)+\
							 '%) 2: '+'{:8d}'.format(len(Hgot2s))+' ('+"{:5.2f}".format(Hgot2spct)+\
							 '%) 3: '+'{:8d}'.format(len(Hgot3s))+' ('+"{:5.2f}".format(Hgot3spct)+\
							 '%) C: '+'{:8d}'.format(len(HgotCs))+' ('+"{:5.2f}".format(HgotCspct)+\
							 '%) E: '+'{:8d}'.format(len(HgotEs))+' ('+"{:5.2f}".format(HgotEspct)+\
							  '%) H: '+'{:8d}'.format(len(HgotHs))+' ('+"{:5.2f}".format(HgotHspct)+\
							 '%) P: '+'{:8d}'.format(len(HgotPs))+' ('+"{:5.2f}".format(HgotPspct)+\
							 '%) T: '+'{:8d}'.format(len(HgotTs))+' ('+"{:5.2f}".format(HgotTspct)+\
							 '%)\n'))
    filee.close()
#    pdb.set_trace()
    
    #  - plots, EOT/EOH by latitude where 1 = none, 2 = aspirated/ventilated (A/VS), 3 = whirled (SG/SL/W), 4 = screen not aspirated (S/SN), 5 = unscreend (US)
    #  - prints, number and % of obs with EOT and EOH present, and in the categories
    plt.clf()
    fig=plt.figure(figsize=(6,8)) 
    plt1=plt.axes([0.1,0.1,0.85,0.7])
    plt.xlim(0,6)
    plt.ylim(-91,91)
    plt.xlabel('Exposure Category')
    plt.ylabel('Latitude')
    gotEOTs = np.where(EOTbun != 'Non')[0]
    Tgot1s = np.where(EOTbun == 'Non')[0]
    Tgot2s = np.where((EOTbun == 'A  '))[0]
    Tgot3s = np.where((EOTbun == 'SG ') | (EOTbun == 'SL ') | (EOTbun == 'W  '))[0]
    Tgot4s = np.where((EOTbun == 'S  ') | (EOTbun == 'SN ') | (EOTbun == 'VS '))[0]
    Tgot5s = np.where(EOTbun == 'US ')[0]
    pctTgots = 0.
    pctTgot2s = 0.
    pctTgot3s = 0.
    pctTgot4s = 0.
    pctTgot5s = 0.    
    if (nobs > 0):
	pctTgots = (len(gotEOTs)/float(nobs))*100
    if (len(Tgot2s) > 0):
	pctTgot2s = (len(Tgot2s)/float(len(gotEOTs)))*100
    if (len(Tgot3s) > 0):
	pctTgot3s = (len(Tgot3s)/float(len(gotEOTs)))*100
    if (len(Tgot4s) > 0):
	pctTgot4s = (len(Tgot4s)/float(len(gotEOTs)))*100
    if (len(Tgot5s) > 0):
	pctTgot5s = (len(Tgot5s)/float(len(gotEOTs)))*100    
    plt.scatter(np.repeat(0.9,len(Tgot1s)),LATbun[Tgot1s],c='grey',marker='o',linewidth=0.,s=12)
    plt.scatter(np.repeat(1.9,len(Tgot2s)),LATbun[Tgot2s],c='red',marker='o',linewidth=0.,s=12)
    plt.scatter(np.repeat(2.9,len(Tgot3s)),LATbun[Tgot3s],c='orange',marker='o',linewidth=0.,s=12)
    plt.scatter(np.repeat(3.9,len(Tgot4s)),LATbun[Tgot4s],c='blue',marker='o',linewidth=0.,s=12)
    plt.scatter(np.repeat(4.9,len(Tgot5s)),LATbun[Tgot5s],c='violet',marker='o',linewidth=0.,s=12)
    #plt.annotate('EOT: '+str(len(gotEOTs))+' ('+"{:5.2f}".format((len(gotEOTs)/float(nobs))*100)+'%)',xy=(0.55,0.94),xycoords='axes fraction',size=10)
    #plt.annotate('A/VS(2): '+str(len(Tgot2s))+' ('+"{:5.2f}".format((len(Tgot2s)/float(len(gotEOTs)))*100)+'%)',xy=(0.55,0.90),xycoords='axes fraction',size=10)
    #plt.annotate('SG/SL/W(3): '+str(len(Tgot3s))+' ('+"{:5.2f}".format((len(Tgot3s)/float(len(gotEOTs)))*100)+'%)',xy=(0.55,0.86),xycoords='axes fraction',size=10)
    #plt.annotate('S/SN(4): '+str(len(Tgot4s))+' ('+"{:5.2f}".format((len(Tgot4s)/float(len(gotEOTs)))*100)+'%)',xy=(0.55,0.82),xycoords='axes fraction',size=10)
    #plt.annotate('US(5): '+str(len(Tgot5s))+' ('+"{:5.2f}".format((len(Tgot5s)/float(len(gotEOTs)))*100)+'%)',xy=(0.55,0.78),xycoords='axes fraction',size=10)
    plt.annotate('EOT: '+str(len(gotEOTs))+' ('+"{:5.2f}".format(pctTgots)+'%)',xy=(0.05,1.21),xycoords='axes fraction',size=12,color='grey')
    plt.annotate('A: '+str(len(Tgot2s))+' ('+"{:5.2f}".format(pctTgot2s)+'%)',xy=(0.05,1.16),xycoords='axes fraction',size=12,color='red')
    plt.annotate('SG/SL/W: '+str(len(Tgot3s))+' ('+"{:5.2f}".format(pctTgot3s)+'%)',xy=(0.05,1.11),xycoords='axes fraction',size=12,color='orange')
    plt.annotate('S/SN/VS: '+str(len(Tgot4s))+' ('+"{:5.2f}".format(pctTgot4s)+'%)',xy=(0.05,1.06),xycoords='axes fraction',size=12,color='blue')
    plt.annotate('US: '+str(len(Tgot5s))+' ('+"{:5.2f}".format(pctTgot5s)+'%)',xy=(0.05,1.01),xycoords='axes fraction',size=12,color='violet')
    gotEOHs = np.where(EOHbun != 'Non')[0]
    Hgot1s = np.where(EOHbun == 'Non')[0]
    Hgot2s = np.where((EOHbun == 'A  '))[0]
    Hgot3s = np.where((EOHbun == 'SG ') | (EOHbun == 'SL ') | (EOHbun == 'W  '))[0]
    Hgot4s = np.where((EOHbun == 'S  ') | (EOHbun == 'SN ') | (EOHbun == 'VS '))[0]
    Hgot5s = np.where(EOHbun == 'US ')[0]
    pctHgots = 0.
    pctHgot2s = 0.
    pctHgot3s = 0.
    pctHgot4s = 0.
    pctHgot5s = 0.    
    if (nobs > 0):
	pctHgots = (len(gotEOHs)/float(nobs))*100
    if (len(Hgot2s) > 0):
	pctHgot2s = (len(Hgot2s)/float(len(gotEOHs)))*100
    if (len(Hgot3s) > 0):
	pctHgot3s = (len(Hgot3s)/float(len(gotEOHs)))*100
    if (len(Hgot4s) > 0):
	pctHgot4s = (len(Hgot4s)/float(len(gotEOHs)))*100
    if (len(Hgot5s) > 0):
	pctHgot5s = (len(Hgot5s)/float(len(gotEOHs)))*100    
    plt.scatter(np.repeat(1.1,len(Hgot1s)),LATbun[Hgot1s],c='grey',marker='o',linewidth=0.,s=12)
    plt.scatter(np.repeat(2.1,len(Hgot2s)),LATbun[Hgot2s],c='red',marker='o',linewidth=0.,s=12) 
    plt.scatter(np.repeat(3.1,len(Hgot3s)),LATbun[Hgot3s],c='orange',marker='o',linewidth=0.,s=12)
    plt.scatter(np.repeat(4.1,len(Hgot4s)),LATbun[Hgot4s],c='blue',marker='o',linewidth=0.,s=12)
    plt.scatter(np.repeat(5.1,len(Hgot5s)),LATbun[Hgot5s],c='violet',marker='o',linewidth=0.,s=12)
    #plt.annotate('EOH: '+str(len(gotEOHs))+' ('+"{:5.2f}".format((len(gotEOHs)/float(nobs))*100)+'%)',xy=(0.55,0.74),xycoords='axes fraction',size=10)
    #plt.annotate('A/VS(2): '+str(len(Hgot2s))+' ('+"{:5.2f}".format((len(Hgot2s)/float(len(gotEOHs)))*100)+'%)',xy=(0.55,0.70),xycoords='axes fraction',size=10)
    #plt.annotate('SG/SL/W(3): '+str(len(Hgot3s))+' ('+"{:5.2f}".format((len(Hgot3s)/float(len(gotEOHs)))*100)+'%)',xy=(0.55,0.66),xycoords='axes fraction',size=10)
    #plt.annotate('S/SN(4): '+str(len(Hgot4s))+' ('+"{:5.2f}".format((len(Hgot4s)/float(len(gotEOHs)))*100)+'%)',xy=(0.55,0.62),xycoords='axes fraction',size=10)
    #plt.annotate('US(5): '+str(len(Hgot5s))+' ('+"{:5.2f}".format((len(Hgot5s)/float(len(gotEOHs)))*100)+'%)',xy=(0.55,0.58),xycoords='axes fraction',size=10)
    plt.annotate('EOH: '+str(len(gotEOHs))+' ('+"{:5.2f}".format(pctHgots)+'%)',xy=(0.55,1.21),xycoords='axes fraction',size=12,color='grey')
    plt.annotate('A: '+str(len(Hgot2s))+' ('+"{:5.2f}".format(pctHgot2s)+'%)',xy=(0.55,1.16),xycoords='axes fraction',size=12,color='red')
    plt.annotate('SG/SL/W: '+str(len(Hgot3s))+' ('+"{:5.2f}".format(pctHgot3s)+'%)',xy=(0.55,1.11),xycoords='axes fraction',size=12,color='orange')
    plt.annotate('S/SN/VS: '+str(len(Hgot4s))+' ('+"{:5.2f}".format(pctHgot4s)+'%)',xy=(0.55,1.06),xycoords='axes fraction',size=12,color='blue')
    plt.annotate('US: '+str(len(Hgot5s))+' ('+"{:5.2f}".format(pctHgot5s)+'%)',xy=(0.55,1.01),xycoords='axes fraction',size=12,color='violet')
    #plt.annotate('a)',xy=(0.03,0.94),xycoords='axes fraction',size=12)

#    plt.savefig(OUTDIR+OutInstrFil+".eps")
    plt.savefig(OUTDIR+OutInstrFil+".png")

    # Write out stats to file (append!)
    filee=open(OUTDIR+OutInstrumentText,'a+')
    filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(nobs)+\
							  ' EOH: '+'{:8d}'.format(len(gotEOHs))+' ('+"{:5.2f}".format(pctHgots)+\
							  '%) A: '+'{:8d}'.format(len(Hgot2s))+' ('+"{:5.2f}".format(pctHgot2s)+\
							 '%) SG/SL/W: '+'{:8d}'.format(len(Hgot3s))+' ('+"{:5.2f}".format(pctHgot3s)+\
							 '%) S/SN/VS: '+'{:8d}'.format(len(Hgot4s))+' ('+"{:5.2f}".format(pctHgot4s)+\
							 '%) US: '+'{:8d}'.format(len(Hgot5s))+' ('+"{:5.2f}".format(pctHgot5s)+\
							 '%) EOT: '+'{:8d}'.format(len(gotEOTs))+' ('+"{:5.2f}".format(pctTgots)+\
							  '%) A: '+'{:8d}'.format(len(Tgot2s))+' ('+"{:5.2f}".format(pctTgot2s)+\
							 '%) SG/SL/W: '+'{:8d}'.format(len(Tgot3s))+' ('+"{:5.2f}".format(pctTgot3s)+\
							 '%) S/SN/VS: '+'{:8d}'.format(len(Tgot4s))+' ('+"{:5.2f}".format(pctTgot4s)+\
							 '%) US: '+'{:8d}'.format(len(Tgot5s))+' ('+"{:5.2f}".format(pctTgot5s)+\
							 '%)\n'))
    filee.close()

    xpos=[0.1, 0.6,0.1,0.6,0.1,0.6]
    ypos=[0.7,0.7,0.37,0.37,0.04,0.04]
    xfat=[0.37,0.37,0.37,0.37,0.37,0.37]
    ytall=[0.28,0.28,0.28,0.28,0.28,0.28]

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	   #6,18

   #  - plots, HOB, HOT, HOA, HOP, LOV (second axis?) by latitude
   #  - prints, number and % of obs with HOB, HOT, HOA, HOP and LOV
    axarr[0].set_position([xpos[0],ypos[0],xfat[0],ytall[0]])
    axarr[0].set_xlim(0,60)
    axarr[0].set_ylim(-91,91)
    axarr[0].set_xlabel('Height (m)/Lenth (m/10.)')
    axarr[0].set_ylabel('Latitude')
    pctHOBs = 0.
    pctHOTs = 0.
    pctHOAs = 0.
    pctHOPs = 0.
    pctLOVs = 0.    
    gotHOBs = np.where(HOBbun > 0)[0]
    if (len(gotHOBs) > 0):
        axarr[0].scatter(HOBbun[gotHOBs]+0.,LATbun[gotHOBs],c='grey',marker='o',linewidth=0.,s=1)
        pctHOBs = (len(gotHOBs)/float(nobs))*100
    gotHOTs = np.where(HOTbun > 0)[0]
    if (len(gotHOTs) > 0):
        axarr[0].scatter(HOTbun[gotHOTs]+0.1,LATbun[gotHOTs],c='red',marker='o',linewidth=0.,s=1)
        pctHOTs = (len(gotHOTs)/float(nobs))*100
    gotHOAs = np.where(HOAbun > 0)[0]
    if (len(gotHOAs) > 0):
        axarr[0].scatter(HOAbun[gotHOAs]+0.2,LATbun[gotHOAs],c='orange',marker='o',linewidth=0.,s=1)
        pctHOAs = (len(gotHOAs)/float(nobs))*100
    gotHOPs = np.where(HOPbun > 0)[0]
    if (len(gotHOPs) > 0):
        axarr[0].scatter(HOPbun[gotHOPs]+0.3,LATbun[gotHOPs],c='blue',marker='o',linewidth=0.,s=1)
        pctHOPs = (len(gotHOPs)/float(nobs))*100
    gotLOVs = np.where(LOVbun > 0)[0]
    if (len(gotLOVs) > 0):
        axarr[0].scatter((LOVbun[gotLOVs]/10.)+0.4,LATbun[gotLOVs],c='violet',marker='o',linewidth=0.,s=1)
        pctLOVs = (len(gotLOVs)/float(nobs))*100
    axarr[0].annotate('a)',xy=(0.03,0.94),xycoords='axes fraction',size=12)
    #axarr[0].annotate('HOB: '+str(len(gotHOBs))+' ('+"{:5.2f}".format(pctHOBs)+'%)',xy=(0.5,0.18),xycoords='axes fraction',size=10,color='grey')
    #axarr[0].annotate('HOT: '+str(len(gotHOTs))+' ('+"{:5.2f}".format(pctHOTs)+'%)',xy=(0.5,0.14),xycoords='axes fraction',size=10,color='red')
    #axarr[0].annotate('HOA: '+str(len(gotHOAs))+' ('+"{:5.2f}".format(pctHOAs)+'%)',xy=(0.5,0.1),xycoords='axes fraction',size=10,color='orange')
    #axarr[0].annotate('HOP: '+str(len(gotHOPs))+' ('+"{:5.2f}".format(pctHOPs)+'%)',xy=(0.5,0.06),xycoords='axes fraction',size=10,color='blue')
    #axarr[0].annotate('LOV: '+str(len(gotLOVs))+' ('+"{:5.2f}".format(pctLOVs)+'%)',xy=(0.5,0.02),xycoords='axes fraction',size=10,color='violet')
    axarr[0].annotate('HOB: '+"{:5.2f}".format(pctHOBs)+'%',xy=(0.6,0.18),xycoords='axes fraction',size=10,color='grey')
    axarr[0].annotate('HOT: '+"{:5.2f}".format(pctHOTs)+'%',xy=(0.6,0.14),xycoords='axes fraction',size=10,color='red')
    axarr[0].annotate('HOA: '+"{:5.2f}".format(pctHOAs)+'%',xy=(0.6,0.1),xycoords='axes fraction',size=10,color='orange')
    axarr[0].annotate('HOP: '+"{:5.2f}".format(pctHOPs)+'%',xy=(0.6,0.06),xycoords='axes fraction',size=10,color='blue')
    axarr[0].annotate('LOV: '+"{:5.2f}".format(pctLOVs)+'%',xy=(0.6,0.02),xycoords='axes fraction',size=10,color='violet')

    #  - plots histogram HOB, HOT, HOA, HOP, LOV (second axis?
    #  - prints, mean and sd of HOB, HOT, HOA, HOP and LOV
    axarr[1].set_position([xpos[1],ypos[1],xfat[1],ytall[1]])
    axarr[1].set_xlim(0,60)
    #axarr[1].set_ylim(0,5000) # let it do its own thing here
    axarr[1].set_xlabel('Height/Lenth (m)')
    axarr[1].set_ylabel('Frequency')
    binsies = np.arange(0,61,1) # a range of bins from left most to right most point
    meanHOBs = -99.9
    meanHOTs = -99.9
    meanHOAs = -99.9
    meanHOPs = -99.9
    meanLOVs = -99.9
    sdHOBs = -99.9
    sdHOTs = -99.9
    sdHOAs = -99.9
    sdHOPs = -99.9
    sdLOVs = -99.9
    if (len(gotHOBs) > 0):
        HOBhist = np.histogram(HOBbun[gotHOBs],binsies) # produces a two D array, second dim as 401 points, first has 400
        axarr[1].plot(HOBhist[1][0:60]+0.5,HOBhist[0],c='grey')
	meanHOBs = np.mean(HOBbun[gotHOBs])
	sdHOBs = np.std(HOBbun[gotHOBs])
        axarr[1].annotate('HOB: '+"{:5.1f}".format(meanHOBs)+', '+"{:5.1f}".format(sdHOBs),xy=(0.6,0.94),xycoords='axes fraction',size=10,color='grey')
    if (len(gotHOTs) > 0):
        HOThist = np.histogram(HOTbun[gotHOTs],binsies) # produces a two D array, second dim as 401 points, first has 400
        axarr[1].plot(HOThist[1][0:60]+0.5,HOThist[0],c='red')
	meanHOTs = np.mean(HOTbun[gotHOTs])
	sdHOTs = np.std(HOTbun[gotHOTs])
        axarr[1].annotate('HOT: '+"{:5.1f}".format(meanHOTs)+', '+"{:5.1f}".format(sdHOTs),xy=(0.6,0.90),xycoords='axes fraction',size=10,color='red')
    if (len(gotHOAs) > 0):
        HOAhist = np.histogram(HOAbun[gotHOAs],binsies) # produces a two D array, second dim as 401 points, first has 400
        axarr[1].plot(HOAhist[1][0:60]+0.5,HOAhist[0],c='orange')
	meanHOAs = np.mean(HOAbun[gotHOAs])
	sdHOAs = np.std(HOAbun[gotHOAs])
        axarr[1].annotate('HOA: '+"{:5.1f}".format(meanHOAs)+', '+"{:5.1f}".format(sdHOAs),xy=(0.6,0.86),xycoords='axes fraction',size=10,color='orange') 
    if (len(gotHOPs) > 0):
        HOPhist = np.histogram(HOPbun[gotHOPs],binsies) # produces a two D array, second dim as 401 points, first has 400
        axarr[1].plot(HOPhist[1][0:60]+0.5,HOPhist[0],c='blue')
	meanHOPs = np.mean(HOPbun[gotHOPs])
	sdHOPs = np.std(HOPbun[gotHOPs])
        axarr[1].annotate('HOP: '+"{:5.1f}".format(meanHOPs)+', '+"{:5.1f}".format(sdHOPs),xy=(0.6,0.82),xycoords='axes fraction',size=10,color='blue')
    if (len(gotLOVs) > 0):
        LOVhist = np.histogram(LOVbun[gotLOVs]/10.,binsies) # produces a two D array, second dim as 401 points, first has 400
        axarr[1].plot(LOVhist[1][0:60]+0.5,LOVhist[0],c='violet')
	meanLOVs = np.mean(LOVbun[gotLOVs])
	sdLOVs = np.std(LOVbun[gotLOVs])
        axarr[1].annotate('LOV: '+"{:5.1f}".format(meanLOVs)+', '+"{:5.1f}".format(sdLOVs),xy=(0.6,0.78),xycoords='axes fraction',size=10,color='violet')
    
    axarr[1].annotate('b)',xy=(0.03,0.94),xycoords='axes fraction',size=12)

    #  - plots, HOA vs HOP, HOA vs HOT, HOA vs HOB, HOP vs HOB, HOP vs HOT with lines of best fit
    #  - prints, number and % where HOA and HOP present, HOA and HOT present, HOA and HOB present, HOP and HOB present, HOP and HOT present, print equation for fit
    axarr[2].set_position([xpos[2],ypos[2],xfat[2],ytall[2]])
    axarr[2].set_xlim(0,60)
    axarr[2].set_ylim(0,60)
    axarr[2].set_ylabel('Thermometer/Barmometer Height (m)')
    axarr[2].set_xlabel('Anemometer/Visual Obs Platform Height (m)')
    pctHOAPs = 0.
    pctHOABs = 0.
    pctHOATs = 0.
    pctHOPBs = 0.
    pctHOPTs = 0.
    fitsAP = [-99.9,-99.9]
    fitsAB = [-99.9,-99.9]
    fitsAT = [-99.9,-99.9]
    fitsPB = [-99.9,-99.9]
    fitsPT = [-99.9,-99.9]    
    gotHOAPs = np.where((HOAbun > 0) & (HOPbun > 0))[0]
    if (len(gotHOAPs) > 0):
        axarr[2].scatter(HOAbun[gotHOAPs],HOPbun[gotHOAPs],c='black',marker='o',linewidth=0.,s=2)
        fitsAP = np.polyfit(HOAbun[gotHOAPs],HOPbun[gotHOAPs],1)
	# Get RMSE of residuals from line of best fit
	RMSE_AP = np.sqrt(np.mean((HOPbun[gotHOAPs] - fitsAP[0]*HOAbun[gotHOAPs]+fitsAP[1])**2))
	pctHOAPs = (len(gotHOAPs)/float(nobs))*100
        axarr[2].plot(HOAbun[gotHOAPs],fitsAP[0]*HOAbun[gotHOAPs]+fitsAP[1],c='black')
        #axarr[2].annotate('HOBHOA: '+str(len(gotHOABs))+' ('+"{:5.2f}".format(pctHOABs)+'%), '+"{:5.2f}".format(fitsAB[0])+', '+"{:5.2f}".format(fitsAB[1])+' ('+"{:6.2f}".format(RMSE_AB)+')',xy=(0.1,0.94),xycoords='axes fraction',size=10,color='grey') 
        axarr[2].annotate('HOPHOA: '+"{:5.2f}".format(pctHOAPs)+'%, '+"{:5.2f}".format(fitsAP[0])+', '+"{:5.2f}".format(fitsAP[1])+' ('+"{:6.2f}".format(RMSE_AP)+')',xy=(0.1,0.78),xycoords='axes fraction',size=10,color='black') 
    gotHOABs = np.where((HOAbun > 0) & (HOBbun > 0))[0]
    if (len(gotHOABs) > 0):
        axarr[2].scatter(HOAbun[gotHOABs],HOBbun[gotHOABs],c='grey',marker='o',linewidth=0.,s=2)
        fitsAB = np.polyfit(HOAbun[gotHOABs],HOBbun[gotHOABs],1)
	# Get RMSE of residuals from line of best fit
	RMSE_AB = np.sqrt(np.mean((HOBbun[gotHOABs] - fitsAB[0]*HOAbun[gotHOABs]+fitsAB[1])**2))
	pctHOABs = (len(gotHOABs)/float(nobs))*100
        axarr[2].plot(HOAbun[gotHOABs],fitsAB[0]*HOAbun[gotHOABs]+fitsAB[1],c='grey')
        #axarr[2].annotate('HOBHOA: '+str(len(gotHOABs))+' ('+"{:5.2f}".format(pctHOABs)+'%), '+"{:5.2f}".format(fitsAB[0])+', '+"{:5.2f}".format(fitsAB[1])+' ('+"{:6.2f}".format(RMSE_AB)+')',xy=(0.1,0.94),xycoords='axes fraction',size=10,color='grey') 
        axarr[2].annotate('HOBHOA: '+"{:5.2f}".format(pctHOABs)+'%, '+"{:5.2f}".format(fitsAB[0])+', '+"{:5.2f}".format(fitsAB[1])+' ('+"{:6.2f}".format(RMSE_AB)+')',xy=(0.1,0.94),xycoords='axes fraction',size=10,color='grey') 
    gotHOATs = np.where((HOAbun > 0) & (HOTbun > 0))[0]
    if (len(gotHOATs) > 0):
        axarr[2].scatter(HOAbun[gotHOATs],HOTbun[gotHOATs],c='red',marker='o',linewidth=0.,s=2)
        fitsAT = np.polyfit(HOAbun[gotHOATs],HOTbun[gotHOATs],1)
	RMSE_AT = np.sqrt(np.mean((HOTbun[gotHOATs] - fitsAT[0]*HOAbun[gotHOATs]+fitsAT[1])**2))
	pctHOATs = (len(gotHOATs)/float(nobs))*100
        axarr[2].plot(HOAbun[gotHOATs],fitsAT[0]*HOAbun[gotHOATs]+fitsAT[1],c='red')
        #axarr[2].annotate('HOTHOA: '+str(len(gotHOATs))+' ('+"{:5.2f}".format(pctHOATs)+'%), '+"{:5.2f}".format(fitsAT[0])+', '+"{:5.2f}".format(fitsAT[1])+' ('+"{:6.2f}".format(RMSE_AT)+')',xy=(0.1,0.90),xycoords='axes fraction',size=10,color='red')
        axarr[2].annotate('HOTHOA: '+"{:5.2f}".format(pctHOATs)+'%, '+"{:5.2f}".format(fitsAT[0])+', '+"{:5.2f}".format(fitsAT[1])+' ('+"{:6.2f}".format(RMSE_AT)+')',xy=(0.1,0.90),xycoords='axes fraction',size=10,color='red')
    gotHOPBs = np.where((HOPbun > 0) & (HOBbun > 0))[0]
    if (len(gotHOPBs) > 0):
        axarr[2].scatter(HOPbun[gotHOPBs],HOBbun[gotHOPBs],c='orange',marker='o',linewidth=0.,s=2)
        fitsPB = np.polyfit(HOPbun[gotHOPBs],HOBbun[gotHOPBs],1)
	RMSE_PB = np.sqrt(np.mean((HOBbun[gotHOPBs] - fitsPB[0]*HOPbun[gotHOPBs]+fitsPB[1])**2))
	pctHOPBs = (len(gotHOPBs)/float(nobs))*100
        axarr[2].plot(HOPbun[gotHOPBs],fitsPB[0]*HOPbun[gotHOPBs]+fitsPB[1],c='orange')
        #axarr[2].annotate('HOBHOP: '+str(len(gotHOPBs))+' ('+"{:5.2f}".format(pctHOPBs)+'%), '+"{:5.2f}".format(fitsPB[0])+', '+"{:5.2f}".format(fitsPB[1])+' ('+"{:6.2f}".format(RMSE_PB)+')',xy=(0.1,0.86),xycoords='axes fraction',size=10,color='orange')
        axarr[2].annotate('HOBHOP: '+"{:5.2f}".format(pctHOPBs)+'%, '+"{:5.2f}".format(fitsPB[0])+', '+"{:5.2f}".format(fitsPB[1])+' ('+"{:6.2f}".format(RMSE_PB)+')',xy=(0.1,0.86),xycoords='axes fraction',size=10,color='orange')
    gotHOPTs = np.where((HOPbun > 0) & (HOTbun > 0))[0]
    if (len(gotHOPTs) > 0):
        axarr[2].scatter(HOPbun[gotHOPTs],HOTbun[gotHOPTs],c='blue',marker='o',linewidth=0.,s=2)
        fitsPT = np.polyfit(HOPbun[gotHOPTs],HOTbun[gotHOPTs],1)
	RMSE_PT = np.sqrt(np.mean((HOTbun[gotHOPTs] - fitsPT[0]*HOPbun[gotHOPTs]+fitsPT[1])**2))
	pctHOPTs = (len(gotHOPTs)/float(nobs))*100
        axarr[2].plot(HOPbun[gotHOPTs],fitsPT[0]*HOPbun[gotHOPTs]+fitsPT[1],c='blue')
        #axarr[2].annotate('HOTHOP: '+str(len(gotHOPTs))+' ('+"{:5.2f}".format(pctHOPTs)+'%), '+"{:5.2f}".format(fitsPT[0])+', '+"{:5.2f}".format(fitsPT[1])+' ('+"{:6.2f}".format(RMSE_PT)+')',xy=(0.1,0.82),xycoords='axes fraction',size=10,color='blue')
        axarr[2].annotate('HOTHOP: '+"{:5.2f}".format(pctHOPTs)+'%, '+"{:5.2f}".format(fitsPT[0])+', '+"{:5.2f}".format(fitsPT[1])+' ('+"{:6.2f}".format(RMSE_PT)+')',xy=(0.1,0.82),xycoords='axes fraction',size=10,color='blue')
    axarr[2].annotate('c)',xy=(0.03,0.94),xycoords='axes fraction',size=12)

    #  - plots differences HOA - HOT, HOA - HOB, HOP - HOB, HOP - HOT with lines of best fit
    #  - prints, mean and std of difference HOA and HOT present, HOA and HOB present, HOP and HOB present, HOP and HOT present, print equation for fit
    axarr[3].set_position([xpos[3],ypos[3],xfat[3],ytall[3]])
    axarr[3].set_xlim(0,60)
    axarr[3].set_ylim(0,60)
    axarr[3].set_xlabel('Anemometer/Visual Obs Platform Height (m)')
    #axarr[3].set_xlabel('Thermometer/Barmometer Height (m)')
    axarr[3].set_ylabel('Height Difference (m)')
    meanHOAPs = -99.9
    meanHOABs = -99.9
    meanHOATs = -99.9
    meanHOPBs = -99.9
    meanHOPTs = -99.9
    sdHOAPs = -99.9
    sdHOABs = -99.9
    sdHOATs = -99.9
    sdHOPBs = -99.9
    sdHOPTs = -99.9    
    if (len(gotHOAPs) > 0):
        axarr[3].scatter(HOAbun[gotHOAPs],HOAbun[gotHOAPs]-HOPbun[gotHOAPs],c='black',marker='o',linewidth=0.,s=2)
        meanHOAPs = np.mean(HOAbun[gotHOAPs]-HOPbun[gotHOAPs])
	sdHOAPs = np.std(HOAbun[gotHOAPs]-HOPbun[gotHOAPs])
	axarr[3].annotate('HOPHOA: '+"{:5.1f}".format(meanHOAPs)+', '+"{:5.1f}".format(sdHOAPs),xy=(0.5,0.78),xycoords='axes fraction',size=10,color='black')
    if (len(gotHOABs) > 0):
        axarr[3].scatter(HOAbun[gotHOABs],HOAbun[gotHOABs]-HOBbun[gotHOABs],c='grey',marker='o',linewidth=0.,s=2)
        meanHOABs = np.mean(HOAbun[gotHOABs]-HOBbun[gotHOABs])
	sdHOABs = np.std(HOAbun[gotHOABs]-HOBbun[gotHOABs])
	axarr[3].annotate('HOBHOA: '+"{:5.1f}".format(meanHOABs)+', '+"{:5.1f}".format(sdHOABs),xy=(0.5,0.94),xycoords='axes fraction',size=10,color='grey')
    if (len(gotHOATs) > 0):
        axarr[3].scatter(HOAbun[gotHOATs],HOAbun[gotHOATs]-HOTbun[gotHOATs],c='red',marker='o',linewidth=0.,s=2)
        meanHOATs = np.mean(HOAbun[gotHOATs]-HOTbun[gotHOATs])
	sdHOATs = np.std(HOAbun[gotHOATs]-HOTbun[gotHOATs])
        axarr[3].annotate('HOTHOA: '+"{:5.1f}".format(meanHOATs)+', '+"{:5.1f}".format(sdHOATs),xy=(0.5,0.90),xycoords='axes fraction',size=10,color='red')
    if (len(gotHOPBs) > 0):
        axarr[3].scatter(HOPbun[gotHOPBs],HOPbun[gotHOPBs]-HOBbun[gotHOPBs],c='orange',marker='o',linewidth=0.,s=2)
        meanHOPBs = np.mean(HOPbun[gotHOPBs]-HOBbun[gotHOPBs])
	sdHOPBs = np.std(HOPbun[gotHOPBs]-HOBbun[gotHOPBs])
        axarr[3].annotate('HOBHOP: '+"{:5.1f}".format(meanHOPBs)+', '+"{:5.1f}".format(sdHOPBs),xy=(0.5,0.86),xycoords='axes fraction',size=10,color='orange')
    if (len(gotHOPTs) > 0):
        axarr[3].scatter(HOPbun[gotHOPTs],HOPbun[gotHOPTs]-HOTbun[gotHOPTs],c='blue',marker='o',linewidth=0.,s=2)
        meanHOPTs = np.mean(HOPbun[gotHOPTs]-HOTbun[gotHOPTs])
	sdHOPTs = np.std(HOPbun[gotHOPTs]-HOTbun[gotHOPTs])
        axarr[3].annotate('HOTHOP: '+"{:5.1f}".format(meanHOPTs)+', '+"{:5.1f}".format(sdHOPTs),xy=(0.5,0.82),xycoords='axes fraction',size=10,color='blue')
    axarr[3].annotate('d)',xy=(0.03,0.94),xycoords='axes fraction',size=12)

    #  - plots, LOV vs HOT, LOV vs HOB with lines of best fit
    #  - prints, number and % where LOV and HOB present, where LOV and HOT present and equations for fit
    axarr[4].set_position([xpos[4],ypos[4],xfat[4],ytall[4]])
    axarr[4].set_ylim(0,60)
    axarr[4].set_xlim(0,500)
    axarr[4].set_ylabel('Thermometer/Barmometer Height (m)')
    axarr[4].set_xlabel('Length of Vessell (m)')
    pctHOBLs = 0.
    pctHOTLs = 0.
    fitsLB = [-99.9, -99.9]
    fitsLT = [-99.9, -99.9]
    gotHOBLs = np.where((LOVbun > 0) & (HOBbun > 0))[0]
    if (len(gotHOBLs) > 0):
        axarr[4].scatter(LOVbun[gotHOBLs],HOBbun[gotHOBLs],c='grey',marker='o',linewidth=0.,s=1)
        fitsLB = np.polyfit(LOVbun[gotHOBLs],HOBbun[gotHOBLs],1)
	RMSE_LB = np.sqrt(np.mean((LOVbun[gotHOBLs] - fitsLB[0]*LOVbun[gotHOBLs]+fitsLB[1])**2))
	pctHOBLs = (len(gotHOBLs)/float(nobs))*100
        axarr[4].plot(LOVbun[gotHOBLs],fitsLB[0]*LOVbun[gotHOBLs]+fitsLB[1],c='grey')
        #axarr[4].annotate('HOBLOV: '+str(len(gotHOBLs))+' ('+"{:5.2f}".format(pctHOBLs)+'%), '+"{:5.2f}".format(fitsLB[0])+', '+"{:5.2f}".format(fitsLB[1])' ('+"{:6.2f}".format(RMSE_LB)+')',xy=(0.1,0.94),xycoords='axes fraction',size=10,color='grey')
        axarr[4].annotate('HOBLOV: '+"{:5.2f}".format(pctHOBLs)+'%, '+"{:5.2f}".format(fitsLB[0])+', '+"{:5.2f}".format(fitsLB[1])+' ('+"{:6.2f}".format(RMSE_LB)+')',xy=(0.1,0.94),xycoords='axes fraction',size=10,color='grey')
    gotHOTLs = np.where((LOVbun > 0) & (HOTbun > 0))[0]
    if (len(gotHOTLs) > 0):
        axarr[4].scatter(LOVbun[gotHOTLs],HOTbun[gotHOTLs],c='red',marker='o',linewidth=0.,s=1)
        fitsLT = np.polyfit(LOVbun[gotHOTLs],HOTbun[gotHOTLs],1)
	RMSE_LT = np.sqrt(np.mean((LOVbun[gotHOTLs] - fitsLT[0]*LOVbun[gotHOTLs]+fitsLT[1])**2))
	pctHOTLs = (len(gotHOTLs)/float(nobs))*100
        axarr[4].plot(LOVbun[gotHOTLs],fitsLT[0]*LOVbun[gotHOTLs]+fitsLT[1],c='red')
        #axarr[4].annotate('HOTLOV: '+str(len(gotHOTLs))+' ('+"{:5.2f}".format(pctHOTLs)+'%), '+"{:5.2f}".format(fitsLT[0])+', '+"{:5.2f}".format(fitsLT[1])' ('+"{:6.2f}".format(RMSE_LT)+')',xy=(0.1,0.90),xycoords='axes fraction',size=10,color='red')
        axarr[4].annotate('HOTLOV: '+"{:5.2f}".format(pctHOTLs)+'%, '+"{:5.2f}".format(fitsLT[0])+', '+"{:5.2f}".format(fitsLT[1])+' ('+"{:6.2f}".format(RMSE_LT)+')',xy=(0.1,0.90),xycoords='axes fraction',size=10,color='red')
    axarr[4].annotate('e)',xy=(0.03,0.94),xycoords='axes fraction',size=12)

    #  - plots ratio LOV / HOT, LOV / HOB with lines of best fit
    #  - prints, mean and std where LOV and HOB present, where LOV and HOT present and equations for fit
    axarr[5].set_position([xpos[5],ypos[5],xfat[5],ytall[5]])
    axarr[5].set_xlim(0,500)
    axarr[5].set_ylim(0,50)
    axarr[5].set_xlabel('Length of Vessell (m)')
    axarr[5].set_ylabel('Ratio: Vessell Length to Instrument Height')
    meanHOBLs = -99.9
    meanHOTLs = -99.9
    sdHOBLs = -99.9
    sdHOTLs = -99.9
    if (len(gotHOBLs) > 0):
        axarr[5].scatter(LOVbun[gotHOBLs],LOVbun[gotHOBLs]/np.array(HOBbun[gotHOBLs],dtype=float),c='grey',marker='o',linewidth=0.,s=2)
        meanHOBLs = np.mean(LOVbun[gotHOBLs]/np.array(HOBbun[gotHOBLs],dtype=float))
	sdHOBLs = np.std(LOVbun[gotHOBLs]-np.array(HOBbun[gotHOBLs],dtype=float))
	axarr[5].annotate('HOBLOV: '+"{:5.1f}".format(meanHOBLs)+', '+"{:5.1f}".format(sdHOBLs),xy=(0.5,0.94),xycoords='axes fraction',size=10,color='grey')
    if (len(gotHOTLs) > 0):
        axarr[5].scatter(LOVbun[gotHOTLs],LOVbun[gotHOTLs]/np.array(HOTbun[gotHOTLs],dtype=float),c='red',marker='o',linewidth=0.,s=2)
        meanHOTLs = np.mean(LOVbun[gotHOTLs]/np.array(HOTbun[gotHOTLs],dtype=float))
	sdHOTLs = np.std(LOVbun[gotHOTLs]-np.array(HOTbun[gotHOTLs],dtype=float))
        axarr[5].annotate('HOTLOV: '+"{:5.1f}".format(np.mean(LOVbun[gotHOTLs]/np.array(HOTbun[gotHOTLs],dtype=float)))+', '+"{:5.1f}".format(np.std(LOVbun[gotHOTLs]-np.array(HOTbun[gotHOTLs],dtype=float))),xy=(0.5,0.90),xycoords='axes fraction',size=10,color='red')
    axarr[5].annotate('f)',xy=(0.03,0.94),xycoords='axes fraction',size=12)

    # save plots as eps and png
#    plt.savefig(OUTDIR+OutHeightFil+".eps")
    plt.savefig(OUTDIR+OutHeightFil+".png")

    # Write out stats to file (append!)
    filee=open(OUTDIR+OutHeightText,'a+')
    print(fitsAB)
    filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(nobs)+\
                                                          ' HOB: '+'{:8d}'.format(len(gotHOBs))+' ('+"{:5.2f}".format(pctHOBs)+'%) '+"{:5.1f}".format(meanHOBs)+' '+"{:5.1f}".format(sdHOBs)+\
                                                          ' HOT: '+'{:8d}'.format(len(gotHOTs))+' ('+"{:5.2f}".format(pctHOTs)+'%) '+"{:5.1f}".format(meanHOTs)+' '+"{:5.1f}".format(sdHOTs)+\
							  ' HOA: '+'{:8d}'.format(len(gotHOAs))+' ('+"{:5.2f}".format(pctHOAs)+'%) '+"{:5.1f}".format(meanHOAs)+' '+"{:5.1f}".format(sdHOAs)+\
							  ' HOP: '+'{:8d}'.format(len(gotHOPs))+' ('+"{:5.2f}".format(pctHOPs)+'%) '+"{:5.1f}".format(meanHOPs)+' '+"{:5.1f}".format(sdHOPs)+\
							  ' LOV: '+'{:8d}'.format(len(gotLOVs))+' ('+"{:5.2f}".format(pctLOVs)+'%) '+"{:5.1f}".format(meanLOVs)+' '+"{:5.1f}".format(sdLOVs)+\
                                                          ' HOPHOA: '+'{:8d}'.format(len(gotHOAPs))+' ('+"{:5.2f}".format(pctHOAPs)+'%) '+\
							              "{:6.2f}".format(fitsAP[0])+' '+"{:6.2f}".format(fitsAP[1])+' '+\
                                			              "{:5.1f}".format(meanHOAPs)+' '+"{:5.1f}".format(sdHOAPs)+\
                                                          ' HOBHOA: '+'{:8d}'.format(len(gotHOABs))+' ('+"{:5.2f}".format(pctHOABs)+'%) '+\
							              "{:6.2f}".format(fitsAB[0])+' '+"{:6.2f}".format(fitsAB[1])+' '+\
                                			              "{:5.1f}".format(meanHOABs)+' '+"{:5.1f}".format(sdHOABs)+\
                                                          ' HOTHOA: '+'{:8d}'.format(len(gotHOATs))+' ('+"{:5.2f}".format(pctHOATs)+'%) '+\
							              "{:6.2f}".format(fitsAT[0])+' '+"{:6.2f}".format(fitsAT[1])+' '+\
							              "{:5.1f}".format(meanHOATs)+' '+"{:5.1f}".format(sdHOATs)+\
						          ' HOBHOP: '+'{:8d}'.format(len(gotHOPBs))+' ('+"{:5.2f}".format(pctHOPBs)+'%) '+\
							              "{:6.2f}".format(fitsPB[0])+' '+"{:6.2f}".format(fitsPB[1])+' '+\
							              "{:5.1f}".format(meanHOPBs)+' '+"{:5.1f}".format(sdHOPBs)+\
							  ' HOTHOP: '+'{:8d}'.format(len(gotHOPTs))+' ('+"{:5.2f}".format(pctHOPTs)+'%) '+\
							              "{:6.2f}".format(fitsPT[0])+' '+"{:6.2f}".format(fitsPT[1])+' '+\
							              "{:5.1f}".format(meanHOPTs)+' '+"{:5.1f}".format(sdHOPTs)+\
							  ' HOBLOV: '+'{:8d}'.format(len(gotHOBLs))+' ('+"{:5.2f}".format(pctHOBLs)+'%) '+\
							              "{:6.2f}".format(fitsLB[0])+' '+"{:6.2f}".format(fitsLB[1])+' '+\
							              "{:5.1f}".format(meanHOBLs)+' '+"{:5.1f}".format(sdHOBLs)+\
							  ' HOTLOV: '+'{:8d}'.format(len(gotHOTLs))+' ('+"{:5.2f}".format(pctHOTLs)+'%) '+\
							              "{:6.2f}".format(fitsLT[0])+' '+"{:6.2f}".format(fitsLT[1])+' '+\
							              "{:5.1f}".format(meanHOTLs)+' '+"{:5.1f}".format(sdHOTLs)+\
                                                          '\n'))
    filee.close()

    #pdb.set_trace()

if __name__ == '__main__':
    
    main(sys.argv[1:])




#************************************************************************
