#!/usr/local/sci/bin/python
# PYTHON2.7
# 
# Author: Kate Willett
# Created: 23 April 2016
# Last update: 23 April 2016
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/EUSTACE_SST_MAT/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code reads in the ICOADS data output from QC using MDS_basic_KATE and
# pulls out the numbers of obs and numbers of obs passing qc and no pbs in each
# platform type
#
# creates a list for later plotting
#
# makes up a plot for each year too - maybe
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
# python2.7 MakeObsCountList_APR2016.py --year1 '1973' --year2 '1973' --month1 '01' --month2 '01' --typee 'ERAclimNBC'
#
# This runs the code, outputs the plots and stops mid-process so you can then interact with the
# data. 
# 
# -----------------------
# OUTPUT
# -----------------------
# some plots:
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/PTTypeMetaDataDiags_all_ERAclimNBC_y1y2m1m2_APR2016.png
#
# a text file of stats
# /data/local/hadkw/HADCRUH2/MARINE/LISTS/PTTypeMetaDataStats_all_ERAclimNBC_APR2016.txt
# 
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
# 
# Version 1 (23 April 2016)
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
import MDS_RWtools as mrw

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

    try:
        opts, args = getopt.getopt(argv, "hi:",
	                           ["year1=","year2=","month1=","month2=","typee="])
    except getopt.GetoptError:
        print 'Usage (as strings) MakeObsCountList_APR2016.py --year1 <1973> --year2 <1973> '+\
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

    assert year1 != -999 and year2 != -999, "Year not specified."

    print(year1, year2, month1, month2, typee)
#    pdb.set_trace()
    					   
    #INDIR = '/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/ERAclimNBC/'
    #INFIL = 'new_suite_'
    #INEXT = '_'+typee+'.txt'

#    OUTDIR = '/data/local/hadkw/HADCRUH2/MARINE/'
    OUTDIR = ''
    OutTypeFil = 'IMAGES/PTTypeMetaDataDiags_'+typee+'_'+year1+year2+month1+month2+'_APR2016'
    OutTypeText = 'LISTS/PTTypeMetaDataStats_'+typee+'_APR2016.txt'
    OutTypeTextD = 'LISTS/PTTypeMetaDataStatsDAY_'+typee+'_APR2016.txt'
    OutTypeTextN = 'LISTS/PTTypeMetaDataStatsNIGHT_'+typee+'_APR2016.txt'
    OutTypeGText = 'LISTS/PTTypeGOODMetaDataStats_'+typee+'_APR2016.txt'
    OutTypeGTextD = 'LISTS/PTTypeGOODMetaDataStatsDAY_'+typee+'_APR2016.txt'
    OutTypeGTextN = 'LISTS/PTTypeGOODMetaDataStatsNIGHT_'+typee+'_APR2016.txt'
    OutQCFil = 'IMAGES/QCMetaDataDiags_'+typee+'_'+year1+year2+month1+month2+'_APR2016'
    OutQCText = 'LISTS/QCMetaDataStats_'+typee+'_APR2016.txt'
    OutQCTextD = 'LISTS/QCMetaDataStatsDAY_'+typee+'_APR2016.txt'
    OutQCTextN = 'LISTS/QCMetaDataStatsNIGHT_'+typee+'_APR2016.txt'
    
    # create empty arrays for data bundles
    nobs=0 # we're looking at all obs, not just those with 'good' data
    nobsQC=0 # we're looking at all obs, not just those with 'good' data
    LATbun = []
    PTbun = []
    QCday = []
    QCtrk = []
    QCdate1= []
    QCdate2= []
    QCpos = []
    QCblklst = []
    QCdup = []
    QCATbud = []
    QCATclim = []
    QCATround = []
    QCATrep = []
    QCDPTbud = []
    QCDPTclim = []
    QCDPTssat = []
    QCDPTround = []
    QCDPTrep = []
    QCDPTrepsat = []

    # loop through each month, read in data, keep metadata needed
    for yy in range((int(year2)+1)-int(year1)):
        for mm in range((int(month2)+1)-int(month1)):
            print(str(yy+int(year1)),' ','{:02}'.format(mm+int(month1)))

            MDSdict=mrw.ReadMDSstandard(str(yy+int(year1)),'{:02}'.format(mm+int(month1)), typee)

	    if (nobs == 0):
	        LATbun = MDSdict['LAT']
                PTbun = MDSdict['PT']
                QCday = MDSdict['day']
                QCtrk = MDSdict['trk']
                QCdate1= MDSdict['date1']
                QCdate2= MDSdict['date2']
                QCpos = MDSdict['pos']
                QCblklst = MDSdict['blklst']
                QCdup = MDSdict['dup']
                QCATbud = MDSdict['ATbud']
                QCATclim = MDSdict['ATclim']
                QCATround = MDSdict['ATround']
                QCATrep = MDSdict['ATrep']
                QCDPTbud = MDSdict['DPTbud']
                QCDPTclim = MDSdict['DPTclim']
                QCDPTssat = MDSdict['DPTssat']
                QCDPTround = MDSdict['DPTround']
                QCDPTrep = MDSdict['DPTrep']
                QCDPTrepsat = MDSdict['DPTrepsat']

            else:
	        LATbun = np.append(LATbun,MDSdict['LAT'])
                PTbun = np.append(PTbun,MDSdict['PT'])
                QCday = np.append(QCday,MDSdict['day'])
                QCtrk = np.append(QCtrk,MDSdict['trk'])
                QCdate1= np.append(QCdate1,MDSdict['date1'])
                QCdate2= np.append(QCdate2,MDSdict['date2'])
                QCpos = np.append(QCpos,MDSdict['pos'])
                QCblklst = np.append(QCblklst,MDSdict['blklst'])
                QCdup = np.append(QCdup,MDSdict['dup'])
                QCATbud = np.append(QCATbud,MDSdict['ATbud'])
                QCATclim = np.append(QCATclim,MDSdict['ATclim'])
                QCATround = np.append(QCATround,MDSdict['ATround'])
                QCATrep = np.append(QCATrep,MDSdict['ATrep'])
                QCDPTbud = np.append(QCDPTbud,MDSdict['DPTbud'])
                QCDPTclim = np.append(QCDPTclim,MDSdict['DPTclim'])
                QCDPTssat = np.append(QCDPTssat,MDSdict['DPTssat'])
                QCDPTround = np.append(QCDPTround,MDSdict['DPTround'])
                QCDPTrep = np.append(QCDPTrep,MDSdict['DPTrep'])
                QCDPTrepsat = np.append(QCDPTrepsat,MDSdict['DPTrepsat'])
	
	    nobs = nobs + len(MDSdict['LAT'])
	        
	    MDSdict = 0 # clear out

    # Set up day and night pointers
    DayPts = np.where(QCday == 1)[0]
    Dnobs = len(DayPts)
    NightPts = np.where(QCday == 0)[0]
    Nnobs = len(NightPts)
    
    # Get good pointers
    gotGOODs = np.where((QCtrk == 0) & (QCATbud == 0) & (QCATclim == 0) & (QCATrep == 0) & (QCDPTbud == 0) & (QCDPTclim == 0) & (QCDPTrep == 0) & (QCDPTssat == 0) & (QCDPTrepsat == 0))[0]
    ngoods=len(gotGOODs)
    DgotGOODs = np.where((QCtrk[DayPts] == 0) & (QCATbud[DayPts] == 0) & (QCATclim[DayPts] == 0) & (QCATrep[DayPts] == 0) & (QCDPTbud[DayPts] == 0) & (QCDPTclim[DayPts] == 0) & (QCDPTrep[DayPts] == 0) & (QCDPTssat[DayPts] == 0) & (QCDPTrepsat[DayPts] == 0))[0]
    Dngoods = len(DgotGOODs)
    NgotGOODs = np.where((QCtrk[NightPts] == 0) & (QCATbud[NightPts] == 0) & (QCATclim[NightPts] == 0) & (QCATrep[NightPts] == 0) & (QCDPTbud[NightPts] == 0) & (QCDPTclim[NightPts] == 0) & (QCDPTrep[NightPts] == 0) & (QCDPTssat[NightPts] == 0) & (QCDPTrepsat[NightPts] == 0))[0]
    Nngoods=len(NgotGOODs)

    # Just goods
    gotPTs = np.where(PTbun[gotGOODs] <= 15)[0]
    got0s = np.where(PTbun[gotGOODs] == 0)[0]
    got1s = np.where(PTbun[gotGOODs] == 1)[0]
    got2s = np.where(PTbun[gotGOODs] == 2)[0]
    got3s = np.where(PTbun[gotGOODs] == 3)[0]
    got4s = np.where(PTbun[gotGOODs] == 4)[0]
    got5s = np.where(PTbun[gotGOODs] == 5)[0]
    got6s = np.where(PTbun[gotGOODs] == 6)[0]
    got8s = np.where(PTbun[gotGOODs] == 8)[0]
    got9s = np.where(PTbun[gotGOODs] == 9)[0]
    got10s = np.where(PTbun[gotGOODs] == 10)[0]
    got15s = np.where(PTbun[gotGOODs] == 15)[0]
    got0spct = 0.
    got1spct = 0.
    got2spct = 0.
    got3spct = 0.
    got4spct = 0.
    got5spct = 0.
    got6spct = 0.
    got8spct = 0.
    got9spct = 0.
    got10spct = 0.
    got15spct = 0.
    gotspct = 0.
    if (nobs > 0):
        gotspct = (len(gotPTs)/float(ngoods))*100
    if (len(got0s) > 0):
        got0spct = (len(got0s)/float(len(gotPTs)))*100
    if (len(got1s) > 0):
        got1spct = (len(got1s)/float(len(gotPTs)))*100
    if (len(got2s) > 0):
        got2spct = (len(got2s)/float(len(gotPTs)))*100
    if (len(got3s) > 0):
        got3spct = (len(got3s)/float(len(gotPTs)))*100
    if (len(got4s) > 0):
        got4spct = (len(got4s)/float(len(gotPTs)))*100
    if (len(got5s) > 0):
        got5spct = (len(got5s)/float(len(gotPTs)))*100
        print(len(got5s))
    if (len(got6s) > 0):
        got6spct = (len(got6s)/float(len(gotPTs)))*100
    if (len(got8s) > 0):
        got8spct = (len(got8s)/float(len(gotPTs)))*100
    if (len(got9s) > 0):
        got9spct = (len(got9s)/float(len(gotPTs)))*100
    if (len(got10s) > 0):
        got10spct = (len(got10s)/float(len(gotPTs)))*100
    if (len(got15s) > 0):
        got15spct = (len(got15s)/float(len(gotPTs)))*100

    # DAY
    DgotPTs = np.where(PTbun[DgotGOODs] <= 15)[0]
    Dgot0s = np.where(PTbun[DgotGOODs] == 0)[0]
    Dgot1s = np.where(PTbun[DgotGOODs] == 1)[0]
    Dgot2s = np.where(PTbun[DgotGOODs] == 2)[0]
    Dgot3s = np.where(PTbun[DgotGOODs] == 3)[0]
    Dgot4s = np.where(PTbun[DgotGOODs] == 4)[0]
    Dgot5s = np.where(PTbun[DgotGOODs] == 5)[0]
    Dgot6s = np.where(PTbun[DgotGOODs] == 6)[0]
    Dgot8s = np.where(PTbun[DgotGOODs] == 8)[0]
    Dgot9s = np.where(PTbun[DgotGOODs] == 9)[0]
    Dgot10s = np.where(PTbun[DgotGOODs] == 10)[0]
    Dgot15s = np.where(PTbun[DgotGOODs] == 15)[0]
    Dgot0spct = 0.
    Dgot1spct = 0.
    Dgot2spct = 0.
    Dgot3spct = 0.
    Dgot4spct = 0.
    Dgot5spct = 0.
    Dgot6spct = 0.
    Dgot8spct = 0.
    Dgot9spct = 0.
    Dgot10spct = 0.
    Dgot15spct = 0.
    Dgotspct = 0.
    if (nobs > 0):
        Dgotspct = (len(DgotPTs)/float(Dngoods))*100
    if (len(Dgot0s) > 0):
        Dgot0spct = (len(Dgot0s)/float(len(DgotPTs)))*100
    if (len(Dgot1s) > 0):
        Dgot1spct = (len(Dgot1s)/float(len(DgotPTs)))*100
    if (len(Dgot2s) > 0):
        Dgot2spct = (len(Dgot2s)/float(len(DgotPTs)))*100
    if (len(Dgot3s) > 0):
        Dgot3spct = (len(Dgot3s)/float(len(DgotPTs)))*100
    if (len(Dgot4s) > 0):
        Dgot4spct = (len(Dgot4s)/float(len(DgotPTs)))*100
    if (len(Dgot5s) > 0):
        Dgot5spct = (len(Dgot5s)/float(len(DgotPTs)))*100
    if (len(Dgot6s) > 0):
        Dgot6spct = (len(Dgot6s)/float(len(DgotPTs)))*100
    if (len(Dgot8s) > 0):
        Dgot8spct = (len(Dgot8s)/float(len(DgotPTs)))*100
    if (len(Dgot9s) > 0):
        Dgot9spct = (len(Dgot9s)/float(len(DgotPTs)))*100
    if (len(Dgot10s) > 0):
        Dgot10spct = (len(Dgot10s)/float(len(DgotPTs)))*100
    if (len(Dgot15s) > 0):
        Dgot15spct = (len(Dgot15s)/float(len(DgotPTs)))*100

    NgotPTs = np.where(PTbun[NgotGOODs] <= 15)[0]
    Ngot0s = np.where(PTbun[NgotGOODs] == 0)[0]
    Ngot1s = np.where(PTbun[NgotGOODs] == 1)[0]
    Ngot2s = np.where(PTbun[NgotGOODs] == 2)[0]
    Ngot3s = np.where(PTbun[NgotGOODs] == 3)[0]
    Ngot4s = np.where(PTbun[NgotGOODs] == 4)[0]
    Ngot5s = np.where(PTbun[NgotGOODs] == 5)[0]
    Ngot6s = np.where(PTbun[NgotGOODs] == 6)[0]
    Ngot8s = np.where(PTbun[NgotGOODs] == 8)[0]
    Ngot9s = np.where(PTbun[NgotGOODs] == 9)[0]
    Ngot10s = np.where(PTbun[NgotGOODs] == 10)[0]
    Ngot15s = np.where(PTbun[NgotGOODs] == 15)[0]
    Ngot0spct = 0.
    Ngot1spct = 0.
    Ngot2spct = 0.
    Ngot3spct = 0.
    Ngot4spct = 0.
    Ngot5spct = 0.
    Ngot6spct = 0.
    Ngot8spct = 0.
    Ngot9spct = 0.
    Ngot10spct = 0.
    Ngot15spct = 0.
    Ngotspct = 0.
    if (nobs > 0):
        Ngotspct = (len(NgotPTs)/float(Nngoods))*100
    if (len(Ngot0s) > 0):
        Ngot0spct = (len(Ngot0s)/float(len(NgotPTs)))*100
    if (len(Ngot1s) > 0):
        Ngot1spct = (len(Ngot1s)/float(len(NgotPTs)))*100
    if (len(Ngot2s) > 0):
        Ngot2spct = (len(Ngot2s)/float(len(NgotPTs)))*100
    if (len(Ngot3s) > 0):
        Ngot3spct = (len(Ngot3s)/float(len(NgotPTs)))*100
    if (len(Ngot4s) > 0):
        Ngot4spct = (len(Ngot4s)/float(len(NgotPTs)))*100
    if (len(Ngot5s) > 0):
        Ngot5spct = (len(Ngot5s)/float(len(NgotPTs)))*100
    if (len(Ngot6s) > 0):
        Ngot6spct = (len(Ngot6s)/float(len(NgotPTs)))*100
    if (len(Ngot8s) > 0):
        Ngot8spct = (len(Ngot8s)/float(len(NgotPTs)))*100
    if (len(Ngot9s) > 0):
        Ngot9spct = (len(Ngot9s)/float(len(NgotPTs)))*100
    if (len(Ngot10s) > 0):
        Ngot10spct = (len(Ngot10s)/float(len(NgotPTs)))*100
    if (len(Ngot15s) > 0):
        Ngot15spct = (len(Ngot15s)/float(len(NgotPTs)))*100

    # Write out stats to file (append!)
    filee=open(OUTDIR+OutTypeGText,'a+')
    filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(ngoods)+\
                                                          ' PT: '+'{:8d}'.format(len(gotPTs))+' ('+"{:5.2f}".format(gotspct)+\
                                                          '%) 0: '+'{:8d}'.format(len(got0s))+' ('+"{:5.2f}".format(got0spct)+\
                                                          '%) 1: '+'{:8d}'.format(len(got1s))+' ('+"{:5.2f}".format(got1spct)+\
							  '%) 2: '+'{:8d}'.format(len(got2s))+' ('+"{:5.2f}".format(got2spct)+\
							  '%) 3: '+'{:8d}'.format(len(got3s))+' ('+"{:5.2f}".format(got3spct)+\
							  '%) 4: '+'{:8d}'.format(len(got4s))+' ('+"{:5.2f}".format(got4spct)+\
							  '%) 5: '+'{:8d}'.format(len(got5s))+' ('+"{:5.2f}".format(got5spct)+\
                                                          '%) 6: '+'{:8d}'.format(len(got6s))+' ('+"{:5.2f}".format(got6spct)+\
							  '%) 8: '+'{:8d}'.format(len(got8s))+' ('+"{:5.2f}".format(got8spct)+\
							  '%) 9: '+'{:8d}'.format(len(got9s))+' ('+"{:5.2f}".format(got9spct)+\
							  '%) 10: '+'{:8d}'.format(len(got10s))+' ('+"{:5.2f}".format(got10spct)+\
							  '%) 15: '+'{:8d}'.format(len(got15s))+' ('+"{:5.2f}".format(got15spct)+\
							  '%)\n'))
    filee.close()

    filee=open(OUTDIR+OutTypeGTextD,'a+')
    filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(Dngoods)+\
                                                          ' PT: '+'{:8d}'.format(len(DgotPTs))+' ('+"{:5.2f}".format(Dgotspct)+\
                                                          '%) 0: '+'{:8d}'.format(len(Dgot0s))+' ('+"{:5.2f}".format(Dgot0spct)+\
                                                          '%) 1: '+'{:8d}'.format(len(Dgot1s))+' ('+"{:5.2f}".format(Dgot1spct)+\
							  '%) 2: '+'{:8d}'.format(len(Dgot2s))+' ('+"{:5.2f}".format(Dgot2spct)+\
							  '%) 3: '+'{:8d}'.format(len(Dgot3s))+' ('+"{:5.2f}".format(Dgot3spct)+\
							  '%) 4: '+'{:8d}'.format(len(Dgot4s))+' ('+"{:5.2f}".format(Dgot4spct)+\
							  '%) 5: '+'{:8d}'.format(len(Dgot5s))+' ('+"{:5.2f}".format(Dgot5spct)+\
                                                          '%) 6: '+'{:8d}'.format(len(Dgot6s))+' ('+"{:5.2f}".format(Dgot6spct)+\
							  '%) 8: '+'{:8d}'.format(len(Dgot8s))+' ('+"{:5.2f}".format(Dgot8spct)+\
							  '%) 9: '+'{:8d}'.format(len(Dgot9s))+' ('+"{:5.2f}".format(Dgot9spct)+\
							  '%) 10: '+'{:8d}'.format(len(Dgot10s))+' ('+"{:5.2f}".format(Dgot10spct)+\
							  '%) 15: '+'{:8d}'.format(len(Dgot15s))+' ('+"{:5.2f}".format(Dgot15spct)+\
							  '%)\n'))
    filee.close()

    filee=open(OUTDIR+OutTypeGTextN,'a+')
    filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(Nngoods)+\
                                                          ' PT: '+'{:8d}'.format(len(NgotPTs))+' ('+"{:5.2f}".format(Ngotspct)+\
                                                          '%) 0: '+'{:8d}'.format(len(Ngot0s))+' ('+"{:5.2f}".format(Ngot0spct)+\
                                                          '%) 1: '+'{:8d}'.format(len(Ngot1s))+' ('+"{:5.2f}".format(Ngot1spct)+\
							  '%) 2: '+'{:8d}'.format(len(Ngot2s))+' ('+"{:5.2f}".format(Ngot2spct)+\
							  '%) 3: '+'{:8d}'.format(len(Ngot3s))+' ('+"{:5.2f}".format(Ngot3spct)+\
							  '%) 4: '+'{:8d}'.format(len(Ngot4s))+' ('+"{:5.2f}".format(Ngot4spct)+\
							  '%) 5: '+'{:8d}'.format(len(Ngot5s))+' ('+"{:5.2f}".format(Ngot5spct)+\
                                                          '%) 6: '+'{:8d}'.format(len(Ngot6s))+' ('+"{:5.2f}".format(Ngot6spct)+\
							  '%) 8: '+'{:8d}'.format(len(Ngot8s))+' ('+"{:5.2f}".format(Ngot8spct)+\
							  '%) 9: '+'{:8d}'.format(len(Ngot9s))+' ('+"{:5.2f}".format(Ngot9spct)+\
							  '%) 10: '+'{:8d}'.format(len(Ngot10s))+' ('+"{:5.2f}".format(Ngot10spct)+\
							  '%) 15: '+'{:8d}'.format(len(Ngot15s))+' ('+"{:5.2f}".format(Ngot15spct)+\
							  '%)\n'))
    filee.close()


	
    # set up generall plotting stuff
    # set up dimensions and plot - this is a 2 by 2 plot
    #  - plots, TOH by latitude where 1 = hygristor, 2 = chilled mirror, 3 = other, C = capacitance, E = electric, H = hair hygrometer, P = psychrometer, T = torsion
    #  - prints, number and % of obs with TOH present, and in the categories
    plt.clf()
    fig=plt.figure(figsize=(6,8)) 
    ax=plt.axes([0.1,0.1,0.85,0.7])
    plt.xlim(-1,11)
    plt.ylim(-91,91)
    plt.xlabel('Platform Type Category')
    plt.ylabel('Latitude')
    locs = ax.get_xticks().tolist()
    locs = np.arange(-1,12,1.) 
    ax.set_xticks(locs)
    labels=[x.get_text() for x in ax.get_xticklabels()]
    labels[1] = '0'
    labels[2] = '1'
    labels[3] = '2'
    labels[4] = '3'
    labels[5] = '4'
    labels[6] = '5'
    labels[7] = '6'
    labels[8] = '8'
    labels[9] = '9'
    labels[10] = '10'
    labels[11] = '15'
    ax.set_xticklabels(labels)
    gotPTs = np.where(PTbun <= 15)[0]
    got0s = np.where(PTbun == 0)[0]
    got1s = np.where(PTbun == 1)[0]
    got2s = np.where(PTbun == 2)[0]
    got3s = np.where(PTbun == 3)[0]
    got4s = np.where(PTbun == 4)[0]
    got5s = np.where(PTbun == 5)[0]
    got6s = np.where(PTbun == 6)[0]
    got8s = np.where(PTbun == 8)[0]
    got9s = np.where(PTbun == 9)[0]
    got10s = np.where(PTbun == 10)[0]
    got15s = np.where(PTbun == 15)[0]
    got0spct = 0.
    got1spct = 0.
    got2spct = 0.
    got3spct = 0.
    got4spct = 0.
    got5spct = 0.
    got6spct = 0.
    got8spct = 0.
    got9spct = 0.
    got10spct = 0.
    got15spct = 0.
    gotspct = 0.
    if (nobs > 0):
        gotspct = (len(gotPTs)/float(nobs))*100
    if (len(got0s) > 0):
        got0spct = (len(got0s)/float(len(gotPTs)))*100
        plt.scatter(np.repeat(0,len(got0s)),LATbun[got0s],c='hotpink',marker='o',linewidth=0.,s=12)
    if (len(got1s) > 0):
        got1spct = (len(got1s)/float(len(gotPTs)))*100
        plt.scatter(np.repeat(1,len(got1s)),LATbun[got1s],c='deeppink',marker='o',linewidth=0.,s=12)
    if (len(got2s) > 0):
        got2spct = (len(got2s)/float(len(gotPTs)))*100
        plt.scatter(np.repeat(2,len(got2s)),LATbun[got2s],c='red',marker='o',linewidth=0.,s=12)
    if (len(got3s) > 0):
        got3spct = (len(got3s)/float(len(gotPTs)))*100
        plt.scatter(np.repeat(3,len(got3s)),LATbun[got3s],c='darkorange',marker='o',linewidth=0.,s=12)
    if (len(got4s) > 0):
        got4spct = (len(got4s)/float(len(gotPTs)))*100
        plt.scatter(np.repeat(4,len(got4s)),LATbun[got4s],c='gold',marker='o',linewidth=0.,s=12)
    if (len(got5s) > 0):
        got5spct = (len(got5s)/float(len(gotPTs)))*100
        print(len(got5s))
        plt.scatter(np.repeat(5,len(got5s)),LATbun[got5s],c='grey',marker='o',linewidth=0.,s=12)
    if (len(got6s) > 0):
        got6spct = (len(got6s)/float(len(gotPTs)))*100
        plt.scatter(np.repeat(6,len(got6s)),LATbun[got6s],c='limegreen',marker='o',linewidth=0.,s=12)
    if (len(got8s) > 0):
        got8spct = (len(got8s)/float(len(gotPTs)))*100
        plt.scatter(np.repeat(7,len(got8s)),LATbun[got8s],c='olivedrab',marker='o',linewidth=0.,s=12)
    if (len(got9s) > 0):
        got9spct = (len(got9s)/float(len(gotPTs)))*100
        plt.scatter(np.repeat(8,len(got9s)),LATbun[got9s],c='blue',marker='o',linewidth=0.,s=12)
    if (len(got10s) > 0):
        got10spct = (len(got10s)/float(len(gotPTs)))*100
        plt.scatter(np.repeat(9,len(got10s)),LATbun[got10s],c='indigo',marker='o',linewidth=0.,s=12)
    if (len(got15s) > 0):
        got15spct = (len(got15s)/float(len(gotPTs)))*100
        plt.scatter(np.repeat(10,len(got15s)),LATbun[got15s],c='violet',marker='o',linewidth=0.,s=12)

    # DAY
    DgotPTs = np.where(PTbun[DayPts] <= 15)[0]
    Dgot0s = np.where(PTbun[DayPts] == 0)[0]
    Dgot1s = np.where(PTbun[DayPts] == 1)[0]
    Dgot2s = np.where(PTbun[DayPts] == 2)[0]
    Dgot3s = np.where(PTbun[DayPts] == 3)[0]
    Dgot4s = np.where(PTbun[DayPts] == 4)[0]
    Dgot5s = np.where(PTbun[DayPts] == 5)[0]
    Dgot6s = np.where(PTbun[DayPts] == 6)[0]
    Dgot8s = np.where(PTbun[DayPts] == 8)[0]
    Dgot9s = np.where(PTbun[DayPts] == 9)[0]
    Dgot10s = np.where(PTbun[DayPts] == 10)[0]
    Dgot15s = np.where(PTbun[DayPts] == 15)[0]
    Dgot0spct = 0.
    Dgot1spct = 0.
    Dgot2spct = 0.
    Dgot3spct = 0.
    Dgot4spct = 0.
    Dgot5spct = 0.
    Dgot6spct = 0.
    Dgot8spct = 0.
    Dgot9spct = 0.
    Dgot10spct = 0.
    Dgot15spct = 0.
    Dgotspct = 0.
    if (nobs > 0):
        Dgotspct = (len(DgotPTs)/float(Dnobs))*100
    if (len(Dgot0s) > 0):
        Dgot0spct = (len(Dgot0s)/float(len(DgotPTs)))*100
        plt.scatter(np.repeat(-0.2,len(Dgot0s)),LATbun[DayPts[Dgot0s]],c='hotpink',marker='o',linewidth=0.,s=12)
    if (len(Dgot1s) > 0):
        Dgot1spct = (len(Dgot1s)/float(len(DgotPTs)))*100
        plt.scatter(np.repeat(0.8,len(Dgot1s)),LATbun[DayPts[Dgot1s]],c='deeppink',marker='o',linewidth=0.,s=12)
    if (len(Dgot2s) > 0):
        Dgot2spct = (len(Dgot2s)/float(len(DgotPTs)))*100
        plt.scatter(np.repeat(1.8,len(Dgot2s)),LATbun[DayPts[Dgot2s]],c='red',marker='o',linewidth=0.,s=12)
    if (len(Dgot3s) > 0):
        Dgot3spct = (len(Dgot3s)/float(len(DgotPTs)))*100
        plt.scatter(np.repeat(2.8,len(Dgot3s)),LATbun[DayPts[Dgot3s]],c='darkorange',marker='o',linewidth=0.,s=12)
    if (len(Dgot4s) > 0):
        Dgot4spct = (len(Dgot4s)/float(len(DgotPTs)))*100
        plt.scatter(np.repeat(3.8,len(Dgot4s)),LATbun[DayPts[Dgot4s]],c='gold',marker='o',linewidth=0.,s=12)
    if (len(Dgot5s) > 0):
        Dgot5spct = (len(Dgot5s)/float(len(DgotPTs)))*100
        plt.scatter(np.repeat(4.8,len(Dgot5s)),LATbun[DayPts[Dgot5s]],c='grey',marker='o',linewidth=0.,s=12)
    if (len(Dgot6s) > 0):
        Dgot6spct = (len(Dgot6s)/float(len(DgotPTs)))*100
        plt.scatter(np.repeat(5.8,len(Dgot6s)),LATbun[DayPts[Dgot6s]],c='limegreen',marker='o',linewidth=0.,s=12)
    if (len(Dgot8s) > 0):
        Dgot8spct = (len(Dgot8s)/float(len(DgotPTs)))*100
        plt.scatter(np.repeat(6.8,len(Dgot8s)),LATbun[DayPts[Dgot8s]],c='olivedrab',marker='o',linewidth=0.,s=12)
    if (len(Dgot9s) > 0):
        Dgot9spct = (len(Dgot9s)/float(len(DgotPTs)))*100
        plt.scatter(np.repeat(7.8,len(Dgot9s)),LATbun[DayPts[Dgot9s]],c='blue',marker='o',linewidth=0.,s=12)
    if (len(Dgot10s) > 0):
        Dgot10spct = (len(Dgot10s)/float(len(DgotPTs)))*100
        plt.scatter(np.repeat(8.8,len(Dgot10s)),LATbun[DayPts[Dgot10s]],c='indigo',marker='o',linewidth=0.,s=12)
    if (len(Dgot15s) > 0):
        Dgot15spct = (len(Dgot15s)/float(len(DgotPTs)))*100
        plt.scatter(np.repeat(9.8,len(Dgot15s)),LATbun[DayPts[Dgot15s]],c='violet',marker='o',linewidth=0.,s=12)

    NgotPTs = np.where(PTbun[NightPts] <= 15)[0]
    Ngot0s = np.where(PTbun[NightPts] == 0)[0]
    Ngot1s = np.where(PTbun[NightPts] == 1)[0]
    Ngot2s = np.where(PTbun[NightPts] == 2)[0]
    Ngot3s = np.where(PTbun[NightPts] == 3)[0]
    Ngot4s = np.where(PTbun[NightPts] == 4)[0]
    Ngot5s = np.where(PTbun[NightPts] == 5)[0]
    Ngot6s = np.where(PTbun[NightPts] == 6)[0]
    Ngot8s = np.where(PTbun[NightPts] == 8)[0]
    Ngot9s = np.where(PTbun[NightPts] == 9)[0]
    Ngot10s = np.where(PTbun[NightPts] == 10)[0]
    Ngot15s = np.where(PTbun[NightPts] == 15)[0]
    Ngot0spct = 0.
    Ngot1spct = 0.
    Ngot2spct = 0.
    Ngot3spct = 0.
    Ngot4spct = 0.
    Ngot5spct = 0.
    Ngot6spct = 0.
    Ngot8spct = 0.
    Ngot9spct = 0.
    Ngot10spct = 0.
    Ngot15spct = 0.
    Ngotspct = 0.
    if (nobs > 0):
        Ngotspct = (len(NgotPTs)/float(Nnobs))*100
    if (len(Ngot0s) > 0):
        Ngot0spct = (len(Ngot0s)/float(len(NgotPTs)))*100
        plt.scatter(np.repeat(0.2,len(Ngot0s)),LATbun[NightPts[Ngot0s]],c='hotpink',marker='o',linewidth=0.,s=12)
    if (len(Ngot1s) > 0):
        Ngot1spct = (len(Ngot1s)/float(len(NgotPTs)))*100
        plt.scatter(np.repeat(1.2,len(Ngot1s)),LATbun[NightPts[Ngot1s]],c='deeppink',marker='o',linewidth=0.,s=12)
    if (len(Ngot2s) > 0):
        Ngot2spct = (len(Ngot2s)/float(len(NgotPTs)))*100
        plt.scatter(np.repeat(2.2,len(Ngot2s)),LATbun[NightPts[Ngot2s]],c='red',marker='o',linewidth=0.,s=12)
    if (len(Ngot3s) > 0):
        Ngot3spct = (len(Ngot3s)/float(len(NgotPTs)))*100
        plt.scatter(np.repeat(3.2,len(Ngot3s)),LATbun[NightPts[Ngot3s]],c='darkorange',marker='o',linewidth=0.,s=12)
    if (len(Ngot4s) > 0):
        Ngot4spct = (len(Ngot4s)/float(len(NgotPTs)))*100
        plt.scatter(np.repeat(4.2,len(Ngot4s)),LATbun[NightPts[Ngot4s]],c='gold',marker='o',linewidth=0.,s=12)
    if (len(Ngot5s) > 0):
        Ngot5spct = (len(Ngot5s)/float(len(NgotPTs)))*100
        plt.scatter(np.repeat(5.2,len(Ngot5s)),LATbun[NightPts[Ngot5s]],c='grey',marker='o',linewidth=0.,s=12)
    if (len(Ngot6s) > 0):
        Ngot6spct = (len(Ngot6s)/float(len(NgotPTs)))*100
        plt.scatter(np.repeat(6.2,len(Ngot6s)),LATbun[NightPts[Ngot6s]],c='limegreen',marker='o',linewidth=0.,s=12)
    if (len(Ngot8s) > 0):
        Ngot8spct = (len(Ngot8s)/float(len(NgotPTs)))*100
        plt.scatter(np.repeat(7.2,len(Ngot8s)),LATbun[NightPts[Ngot8s]],c='olivedrab',marker='o',linewidth=0.,s=12)
    if (len(Ngot9s) > 0):
        Ngot9spct = (len(Ngot9s)/float(len(NgotPTs)))*100
        plt.scatter(np.repeat(8.2,len(Ngot9s)),LATbun[NightPts[Ngot9s]],c='blue',marker='o',linewidth=0.,s=12)
    if (len(Ngot10s) > 0):
        Ngot10spct = (len(Ngot10s)/float(len(NgotPTs)))*100
        plt.scatter(np.repeat(9.2,len(Ngot10s)),LATbun[NightPts[Ngot10s]],c='indigo',marker='o',linewidth=0.,s=12)
    if (len(Ngot15s) > 0):
        Ngot15spct = (len(Ngot15s)/float(len(NgotPTs)))*100
        plt.scatter(np.repeat(10.2,len(Ngot15s)),LATbun[NightPts[Ngot15s]],c='violet',marker='o',linewidth=0.,s=12)
    plt.annotate('PT: '+str(len(gotPTs))+' ('+"{:6.2f}".format(gotspct)+'%), '+str(len(DgotPTs))+' ('+"{:6.2f}".format(Dgotspct)+'%), '+str(len(NgotPTs))+' ('+"{:6.2f}".format(Ngotspct)+'%)',xy=(0.01,1.26),xycoords='axes fraction',size=7,color='black')
    plt.annotate('0: '+str(len(got0s))+' ('+"{:6.2f}".format(got0spct)+'%), '+str(len(Dgot0s))+' ('+"{:6.2f}".format(Dgot0spct)+'%), '+str(len(Ngot0s))+' ('+"{:6.2f}".format(Ngot0spct)+'%)',xy=(0.01,1.22),xycoords='axes fraction',size=7,color='hotpink')
    plt.annotate('1: '+str(len(got1s))+' ('+"{:6.2f}".format(got1spct)+'%), '+str(len(Dgot1s))+' ('+"{:6.2f}".format(Dgot1spct)+'%), '+str(len(Ngot1s))+' ('+"{:6.2f}".format(Ngot1spct)+'%)',xy=(0.01,1.18),xycoords='axes fraction',size=7,color='deeppink')
    plt.annotate('2: '+str(len(got2s))+' ('+"{:6.2f}".format(got2spct)+'%), '+str(len(Dgot2s))+' ('+"{:6.2f}".format(Dgot2spct)+'%), '+str(len(Ngot2s))+' ('+"{:6.2f}".format(Ngot2spct)+'%)',xy=(0.01,1.14),xycoords='axes fraction',size=7,color='red')
    plt.annotate('3: '+str(len(got3s))+' ('+"{:6.2f}".format(got3spct)+'%), '+str(len(Dgot3s))+' ('+"{:6.2f}".format(Dgot3spct)+'%), '+str(len(Ngot3s))+' ('+"{:6.2f}".format(Ngot3spct)+'%)',xy=(0.01,1.10),xycoords='axes fraction',size=7,color='darkorange')
    plt.annotate('4: '+str(len(got4s))+' ('+"{:6.2f}".format(got4spct)+'%), '+str(len(Dgot4s))+' ('+"{:6.2f}".format(Dgot4spct)+'%), '+str(len(Ngot4s))+' ('+"{:6.2f}".format(Ngot4spct)+'%)',xy=(0.01,1.06),xycoords='axes fraction',size=7,color='gold')
    plt.annotate('5: '+str(len(got5s))+' ('+"{:6.2f}".format(got5spct)+'%), '+str(len(Dgot5s))+' ('+"{:6.2f}".format(Dgot5spct)+'%), '+str(len(Ngot5s))+' ('+"{:6.2f}".format(Ngot5spct)+'%)',xy=(0.01,1.02),xycoords='axes fraction',size=7,color='grey')
    plt.annotate('6: '+str(len(got6s))+' ('+"{:6.2f}".format(got6spct)+'%), '+str(len(Dgot6s))+' ('+"{:6.2f}".format(Dgot6spct)+'%), '+str(len(Ngot6s))+' ('+"{:6.2f}".format(Ngot6spct)+'%)',xy=(0.51,1.22),xycoords='axes fraction',size=7,color='limegreen')
    plt.annotate('8: '+str(len(got8s))+' ('+"{:6.2f}".format(got8spct)+'%), '+str(len(Dgot8s))+' ('+"{:6.2f}".format(Dgot8spct)+'%), '+str(len(Ngot8s))+' ('+"{:6.2f}".format(Ngot8spct)+'%)',xy=(0.51,1.18),xycoords='axes fraction',size=7,color='olivedrab')
    plt.annotate('9: '+str(len(got9s))+' ('+"{:6.2f}".format(got9spct)+'%), '+str(len(Dgot9s))+' ('+"{:6.2f}".format(Dgot9spct)+'%), '+str(len(Ngot9s))+' ('+"{:6.2f}".format(Ngot9spct)+'%)',xy=(0.51,1.14),xycoords='axes fraction',size=7,color='blue')
    plt.annotate('10: '+str(len(got10s))+' ('+"{:6.2f}".format(got10spct)+'%), '+str(len(Dgot10s))+' ('+"{:6.2f}".format(Dgot10spct)+'%), '+str(len(Ngot10s))+' ('+"{:6.2f}".format(Ngot10spct)+'%)',xy=(0.51,1.10),xycoords='axes fraction',size=7,color='indigo')
    plt.annotate('15: '+str(len(got15s))+' ('+"{:6.2f}".format(got15spct)+'%), '+str(len(Dgot15s))+' ('+"{:6.2f}".format(Dgot15spct)+'%), '+str(len(Ngot15s))+' ('+"{:6.2f}".format(Ngot15spct)+'%)',xy=(0.51,1.06),xycoords='axes fraction',size=7,color='violet')
    #plt.tight_layout()
    
#    plt.savefig(OUTDIR+OutTypeFil+".eps")
    plt.savefig(OUTDIR+OutTypeFil+".png")

    # Write out stats to file (append!)
    filee=open(OUTDIR+OutTypeText,'a+')
    filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(nobs)+\
                                                          ' PT: '+'{:8d}'.format(len(gotPTs))+' ('+"{:5.2f}".format(gotspct)+\
                                                          '%) 0: '+'{:8d}'.format(len(got0s))+' ('+"{:5.2f}".format(got0spct)+\
                                                          '%) 1: '+'{:8d}'.format(len(got1s))+' ('+"{:5.2f}".format(got1spct)+\
							  '%) 2: '+'{:8d}'.format(len(got2s))+' ('+"{:5.2f}".format(got2spct)+\
							  '%) 3: '+'{:8d}'.format(len(got3s))+' ('+"{:5.2f}".format(got3spct)+\
							  '%) 4: '+'{:8d}'.format(len(got4s))+' ('+"{:5.2f}".format(got4spct)+\
							  '%) 5: '+'{:8d}'.format(len(got5s))+' ('+"{:5.2f}".format(got5spct)+\
                                                          '%) 6: '+'{:8d}'.format(len(got6s))+' ('+"{:5.2f}".format(got6spct)+\
							  '%) 8: '+'{:8d}'.format(len(got8s))+' ('+"{:5.2f}".format(got8spct)+\
							  '%) 9: '+'{:8d}'.format(len(got9s))+' ('+"{:5.2f}".format(got9spct)+\
							  '%) 10: '+'{:8d}'.format(len(got10s))+' ('+"{:5.2f}".format(got10spct)+\
							  '%) 15: '+'{:8d}'.format(len(got15s))+' ('+"{:5.2f}".format(got15spct)+\
							  '%)\n'))
    filee.close()

    filee=open(OUTDIR+OutTypeTextD,'a+')
    filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(Dnobs)+\
                                                          ' PT: '+'{:8d}'.format(len(DgotPTs))+' ('+"{:5.2f}".format(Dgotspct)+\
                                                          '%) 0: '+'{:8d}'.format(len(Dgot0s))+' ('+"{:5.2f}".format(Dgot0spct)+\
                                                          '%) 1: '+'{:8d}'.format(len(Dgot1s))+' ('+"{:5.2f}".format(Dgot1spct)+\
							  '%) 2: '+'{:8d}'.format(len(Dgot2s))+' ('+"{:5.2f}".format(Dgot2spct)+\
							  '%) 3: '+'{:8d}'.format(len(Dgot3s))+' ('+"{:5.2f}".format(Dgot3spct)+\
							  '%) 4: '+'{:8d}'.format(len(Dgot4s))+' ('+"{:5.2f}".format(Dgot4spct)+\
							  '%) 5: '+'{:8d}'.format(len(Dgot5s))+' ('+"{:5.2f}".format(Dgot5spct)+\
                                                          '%) 6: '+'{:8d}'.format(len(Dgot6s))+' ('+"{:5.2f}".format(Dgot6spct)+\
							  '%) 8: '+'{:8d}'.format(len(Dgot8s))+' ('+"{:5.2f}".format(Dgot8spct)+\
							  '%) 9: '+'{:8d}'.format(len(Dgot9s))+' ('+"{:5.2f}".format(Dgot9spct)+\
							  '%) 10: '+'{:8d}'.format(len(Dgot10s))+' ('+"{:5.2f}".format(Dgot10spct)+\
							  '%) 15: '+'{:8d}'.format(len(Dgot15s))+' ('+"{:5.2f}".format(Dgot15spct)+\
							  '%)\n'))
    filee.close()

    filee=open(OUTDIR+OutTypeTextN,'a+')
    filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(Nnobs)+\
                                                          ' PT: '+'{:8d}'.format(len(NgotPTs))+' ('+"{:5.2f}".format(Ngotspct)+\
                                                          '%) 0: '+'{:8d}'.format(len(Ngot0s))+' ('+"{:5.2f}".format(Ngot0spct)+\
                                                          '%) 1: '+'{:8d}'.format(len(Ngot1s))+' ('+"{:5.2f}".format(Ngot1spct)+\
							  '%) 2: '+'{:8d}'.format(len(Ngot2s))+' ('+"{:5.2f}".format(Ngot2spct)+\
							  '%) 3: '+'{:8d}'.format(len(Ngot3s))+' ('+"{:5.2f}".format(Ngot3spct)+\
							  '%) 4: '+'{:8d}'.format(len(Ngot4s))+' ('+"{:5.2f}".format(Ngot4spct)+\
							  '%) 5: '+'{:8d}'.format(len(Ngot5s))+' ('+"{:5.2f}".format(Ngot5spct)+\
                                                          '%) 6: '+'{:8d}'.format(len(Ngot6s))+' ('+"{:5.2f}".format(Ngot6spct)+\
							  '%) 8: '+'{:8d}'.format(len(Ngot8s))+' ('+"{:5.2f}".format(Ngot8spct)+\
							  '%) 9: '+'{:8d}'.format(len(Ngot9s))+' ('+"{:5.2f}".format(Ngot9spct)+\
							  '%) 10: '+'{:8d}'.format(len(Ngot10s))+' ('+"{:5.2f}".format(Ngot10spct)+\
							  '%) 15: '+'{:8d}'.format(len(Ngot15s))+' ('+"{:5.2f}".format(Ngot15spct)+\
							  '%)\n'))
    filee.close()

    plt.clf()
    fig=plt.figure(figsize=(6,8)) 
    ax=plt.axes([0.1,0.1,0.85,0.7])
    plt.xlim(-1,11)
    plt.ylim(-91,91)
    plt.xlabel('QC Category')
    plt.ylabel('Latitude')
    locs = ax.get_xticks().tolist()
    # Ensure locs are -1 to 12, every integer
    locs = np.arange(-1,12,1.) 
    ax.set_xticks(locs)
    labels=[x.get_text() for x in ax.get_xticklabels()]
    labels[1] = 'trk'
    labels[2] = 'ATbud'
    labels[3] = 'ATclim'
    labels[4] = 'ATround'
    labels[5] = 'ATrep'
    labels[6] = 'DPTbud'
    labels[7] = 'DPTclim'
    labels[8] = 'DPTssat'
    labels[9] = 'DPTround'
    labels[10] = 'DPTrep'
    labels[11] = 'DPTrepsat'
    ax.set_xticklabels(labels,rotation='vertical')
    gotBADs = np.where((QCtrk == 1) | (QCATbud == 1) | (QCATclim == 1) | (QCATrep == 1) | (QCDPTbud == 1) | (QCDPTclim == 1) | (QCDPTrep == 1) | (QCDPTssat == 1) | (QCDPTrepsat == 1))[0]
    got0s = np.where(QCtrk == 1)[0]
    got1s = np.where(QCATbud == 1)[0]
    got2s = np.where(QCATclim == 1)[0]
    got3s = np.where(QCATround == 1)[0]
    got4s = np.where(QCATrep == 1)[0]
    got5s = np.where(QCDPTbud == 1)[0]
    got6s = np.where(QCDPTclim == 1)[0]
    got7s = np.where(QCDPTssat == 1)[0]
    got8s = np.where(QCDPTround == 1)[0]
    got9s = np.where(QCDPTrep == 1)[0]
    got10s = np.where(QCDPTrepsat == 1)[0]
    got0spct = 0.
    got1spct = 0.
    got2spct = 0.
    got3spct = 0.
    got4spct = 0.
    got5spct = 0.
    got6spct = 0.
    got7spct = 0.
    got8spct = 0.
    got9spct = 0.
    got10spct = 0.
    gotspct = 0.
    if (nobs > 0):
        gotspct = (len(gotBADs)/float(nobs))*100
    if (len(got0s) > 0):
        got0spct = (len(got0s)/float(nobs))*100
        plt.scatter(np.repeat(0,len(got0s)),LATbun[got0s],c='hotpink',marker='o',linewidth=0.,s=12)
    if (len(got1s) > 0):
        got1spct = (len(got1s)/float(nobs))*100
        plt.scatter(np.repeat(1,len(got1s)),LATbun[got1s],c='deeppink',marker='o',linewidth=0.,s=12)
    if (len(got2s) > 0):
        got2spct = (len(got2s)/float(nobs))*100
        plt.scatter(np.repeat(2,len(got2s)),LATbun[got2s],c='red',marker='o',linewidth=0.,s=12)
    if (len(got3s) > 0):
        got3spct = (len(got3s)/float(nobs))*100
        plt.scatter(np.repeat(3,len(got3s)),LATbun[got3s],c='darkorange',marker='o',linewidth=0.,s=12)
    if (len(got4s) > 0):
        got4spct = (len(got4s)/float(nobs))*100
        plt.scatter(np.repeat(4,len(got4s)),LATbun[got4s],c='gold',marker='o',linewidth=0.,s=12)
    if (len(got5s) > 0):
        got5spct = (len(got5s)/float(nobs))*100
        plt.scatter(np.repeat(5,len(got5s)),LATbun[got5s],c='grey',marker='o',linewidth=0.,s=12)
    if (len(got6s) > 0):
        got6spct = (len(got6s)/float(nobs))*100
        plt.scatter(np.repeat(6,len(got6s)),LATbun[got6s],c='limegreen',marker='o',linewidth=0.,s=12)
    if (len(got7s) > 0):
        got7spct = (len(got7s)/float(nobs))*100
        plt.scatter(np.repeat(7,len(got7s)),LATbun[got7s],c='violet',marker='o',linewidth=0.,s=12)
    if (len(got8s) > 0):
        got8spct = (len(got8s)/float(nobs))*100
        plt.scatter(np.repeat(8,len(got8s)),LATbun[got8s],c='olivedrab',marker='o',linewidth=0.,s=12)
    if (len(got9s) > 0):
        got9spct = (len(got9s)/float(nobs))*100
        plt.scatter(np.repeat(9,len(got9s)),LATbun[got9s],c='blue',marker='o',linewidth=0.,s=12)
    if (len(got10s) > 0):
        got10spct = (len(got10s)/float(nobs))*100
        plt.scatter(np.repeat(10,len(got10s)),LATbun[got10s],c='indigo',marker='o',linewidth=0.,s=12)

    # DAY
    DgotBADs = np.where((QCtrk[DayPts] == 1) | (QCATbud[DayPts] == 1) | (QCATclim[DayPts] == 1) | (QCATrep[DayPts] == 1) | (QCDPTbud[DayPts] == 1) | (QCDPTclim[DayPts] == 1) | (QCDPTrep[DayPts] == 1) | (QCDPTssat[DayPts] == 1) | (QCDPTrepsat[DayPts] == 1))[0]
    Dgot0s = np.where(QCtrk[DayPts] == 1)[0]
    Dgot1s = np.where(QCATbud[DayPts] == 1)[0]
    Dgot2s = np.where(QCATclim[DayPts] == 1)[0]
    Dgot3s = np.where(QCATround[DayPts] == 1)[0]
    Dgot4s = np.where(QCATrep[DayPts] == 1)[0]
    Dgot5s = np.where(QCDPTbud[DayPts] == 1)[0]
    Dgot6s = np.where(QCDPTclim[DayPts] == 1)[0]
    Dgot7s = np.where(QCDPTssat[DayPts] == 1)[0]
    Dgot8s = np.where(QCDPTround[DayPts] == 1)[0]
    Dgot9s = np.where(QCDPTrep[DayPts] == 1)[0]
    Dgot10s = np.where(QCDPTrepsat[DayPts] == 1)[0]
    Dgot0spct = 0.
    Dgot1spct = 0.
    Dgot2spct = 0.
    Dgot3spct = 0.
    Dgot4spct = 0.
    Dgot5spct = 0.
    Dgot6spct = 0.
    Dgot7spct = 0.
    Dgot8spct = 0.
    Dgot9spct = 0.
    Dgot10spct = 0.
    Dgotspct = 0.
    if (nobs > 0):
        Dgotspct = (len(DgotBADs)/float(Dnobs))*100
    if (len(Dgot0s) > 0):
        Dgot0spct = (len(Dgot0s)/float(Dnobs))*100
        plt.scatter(np.repeat(-0.2,len(Dgot0s)),LATbun[DayPts[Dgot0s]],c='hotpink',marker='o',linewidth=0.,s=12)
    if (len(Dgot1s) > 0):
        Dgot1spct = (len(Dgot1s)/float(Dnobs))*100
        plt.scatter(np.repeat(0.8,len(Dgot1s)),LATbun[DayPts[Dgot1s]],c='deeppink',marker='o',linewidth=0.,s=12)
    if (len(Dgot2s) > 0):
        Dgot2spct = (len(Dgot2s)/float(Dnobs))*100
        plt.scatter(np.repeat(1.8,len(Dgot2s)),LATbun[DayPts[Dgot2s]],c='red',marker='o',linewidth=0.,s=12)
    if (len(Dgot3s) > 0):
        Dgot3spct = (len(Dgot3s)/float(Dnobs))*100
        plt.scatter(np.repeat(2.8,len(Dgot3s)),LATbun[DayPts[Dgot3s]],c='darkorange',marker='o',linewidth=0.,s=12)
    if (len(Dgot4s) > 0):
        Dgot4spct = (len(Dgot4s)/float(Dnobs))*100
        plt.scatter(np.repeat(3.8,len(Dgot4s)),LATbun[DayPts[Dgot4s]],c='gold',marker='o',linewidth=0.,s=12)
    if (len(Dgot5s) > 0):
        Dgot5spct = (len(Dgot5s)/float(Dnobs))*100
        plt.scatter(np.repeat(4.8,len(Dgot5s)),LATbun[DayPts[Dgot5s]],c='grey',marker='o',linewidth=0.,s=12)
    if (len(Dgot6s) > 0):
        Dgot6spct = (len(Dgot6s)/float(Dnobs))*100
        plt.scatter(np.repeat(5.8,len(Dgot6s)),LATbun[DayPts[Dgot6s]],c='limegreen',marker='o',linewidth=0.,s=12)
    if (len(Dgot7s) > 0):
        Dgot7spct = (len(Dgot7s)/float(Dnobs))*100
        plt.scatter(np.repeat(6.8,len(Dgot7s)),LATbun[DayPts[Dgot7s]],c='violet',marker='o',linewidth=0.,s=12)
    if (len(Dgot8s) > 0):
        Dgot8spct = (len(Dgot8s)/float(Dnobs))*100
        plt.scatter(np.repeat(7.8,len(Dgot8s)),LATbun[DayPts[Dgot8s]],c='olivedrab',marker='o',linewidth=0.,s=12)
    if (len(Dgot9s) > 0):
        Dgot9spct = (len(Dgot9s)/float(Dnobs))*100
        plt.scatter(np.repeat(8.8,len(Dgot9s)),LATbun[DayPts[Dgot9s]],c='blue',marker='o',linewidth=0.,s=12)
    if (len(Dgot10s) > 0):
        Dgot10spct = (len(Dgot10s)/float(Dnobs))*100
        plt.scatter(np.repeat(9.8,len(Dgot10s)),LATbun[DayPts[Dgot10s]],c='indigo',marker='o',linewidth=0.,s=12)

    #NIGHT
    NgotBADs = np.where((QCtrk[NightPts] == 1) | (QCATbud[NightPts] == 1) | (QCATclim[NightPts] == 1) | (QCATrep[NightPts] == 1) | (QCDPTbud[NightPts] == 1) | (QCDPTclim[NightPts] == 1) | (QCDPTrep[NightPts] == 1) | (QCDPTssat[NightPts] == 1) | (QCDPTrepsat[NightPts] == 1))[0]
    Ngot0s = np.where(QCtrk[NightPts] == 1)[0]
    Ngot1s = np.where(QCATbud[NightPts] == 1)[0]
    Ngot2s = np.where(QCATclim[NightPts] == 1)[0]
    Ngot3s = np.where(QCATround[NightPts] == 1)[0]
    Ngot4s = np.where(QCATrep[NightPts] == 1)[0]
    Ngot5s = np.where(QCDPTbud[NightPts] == 1)[0]
    Ngot6s = np.where(QCDPTclim[NightPts] == 1)[0]
    Ngot7s = np.where(QCDPTssat[NightPts] == 1)[0]
    Ngot8s = np.where(QCDPTround[NightPts] == 1)[0]
    Ngot9s = np.where(QCDPTrep[NightPts] == 1)[0]
    Ngot10s = np.where(QCDPTrepsat[NightPts] == 1)[0]
    Ngot0spct = 0.
    Ngot1spct = 0.
    Ngot2spct = 0.
    Ngot3spct = 0.
    Ngot4spct = 0.
    Ngot5spct = 0.
    Ngot6spct = 0.
    Ngot7spct = 0.
    Ngot8spct = 0.
    Ngot9spct = 0.
    Ngot10spct = 0.
    Ngotspct = 0.
    if (nobs > 0):
        Ngotspct = (len(NgotBADs)/float(Nnobs))*100
    if (len(Ngot0s) > 0):
        Ngot0spct = (len(Ngot0s)/float(Nnobs))*100
        plt.scatter(np.repeat(0.2,len(Ngot0s)),LATbun[NightPts[Ngot0s]],c='hotpink',marker='o',linewidth=0.,s=12)
    if (len(Ngot1s) > 0):
        Ngot1spct = (len(Ngot1s)/float(Nnobs))*100
        plt.scatter(np.repeat(1.2,len(Ngot1s)),LATbun[NightPts[Ngot1s]],c='deeppink',marker='o',linewidth=0.,s=12)
    if (len(Ngot2s) > 0):
        Ngot2spct = (len(Ngot2s)/float(Nnobs))*100
        plt.scatter(np.repeat(2.2,len(Ngot2s)),LATbun[NightPts[Ngot2s]],c='red',marker='o',linewidth=0.,s=12)
    if (len(Ngot3s) > 0):
        Ngot3spct = (len(Ngot3s)/float(Nnobs))*100
        plt.scatter(np.repeat(3.2,len(Ngot3s)),LATbun[NightPts[Ngot3s]],c='darkorange',marker='o',linewidth=0.,s=12)
    if (len(Ngot4s) > 0):
        Ngot4spct = (len(Ngot4s)/float(Nnobs))*100
        plt.scatter(np.repeat(4.2,len(Ngot4s)),LATbun[NightPts[Ngot4s]],c='gold',marker='o',linewidth=0.,s=12)
    if (len(Ngot5s) > 0):
        Ngot5spct = (len(Ngot5s)/float(Nnobs))*100
        plt.scatter(np.repeat(5.2,len(Ngot5s)),LATbun[NightPts[Ngot5s]],c='grey',marker='o',linewidth=0.,s=12)
    if (len(Ngot6s) > 0):
        Ngot6spct = (len(Ngot6s)/float(Nnobs))*100
        plt.scatter(np.repeat(6.2,len(Ngot6s)),LATbun[NightPts[Ngot6s]],c='limegreen',marker='o',linewidth=0.,s=12)
    if (len(Ngot7s) > 0):
        Ngot7spct = (len(Ngot7s)/float(Nnobs))*100
        plt.scatter(np.repeat(7.2,len(Ngot7s)),LATbun[NightPts[Ngot7s]],c='violet',marker='o',linewidth=0.,s=12)
    if (len(Ngot8s) > 0):
        Ngot8spct = (len(Ngot8s)/float(Nnobs))*100
        plt.scatter(np.repeat(8.2,len(Ngot8s)),LATbun[NightPts[Ngot8s]],c='olivedrab',marker='o',linewidth=0.,s=12)
    if (len(Ngot9s) > 0):
        Ngot9spct = (len(Ngot9s)/float(Nnobs))*100
        plt.scatter(np.repeat(9.2,len(Ngot9s)),LATbun[NightPts[Ngot9s]],c='blue',marker='o',linewidth=0.,s=12)
    if (len(Ngot10s) > 0):
        Ngot10spct = (len(Ngot10s)/float(Nnobs))*100
        plt.scatter(np.repeat(10.2,len(Ngot10s)),LATbun[NightPts[Ngot10s]],c='indigo',marker='o',linewidth=0.,s=12)
    plt.annotate('BADs: '+str(len(gotBADs))+' ('+"{:5.2f}".format(gotspct)+'%), '+str(len(DgotBADs))+' ('+"{:5.2f}".format(Dgotspct)+'%), '+str(len(NgotBADs))+' ('+"{:5.2f}".format(Ngotspct)+'%)',xy=(0.01,1.26),xycoords='axes fraction',size=7,color='black')
    plt.annotate('trk: '+str(len(got0s))+' ('+"{:5.2f}".format(got0spct)+'%), '+str(len(Dgot0s))+' ('+"{:5.2f}".format(Dgot0spct)+'%), '+str(len(Ngot0s))+' ('+"{:5.2f}".format(Ngot0spct)+'%)',xy=(0.01,1.22),xycoords='axes fraction',size=7,color='hotpink')
    plt.annotate('ATbud: '+str(len(got1s))+' ('+"{:5.2f}".format(got1spct)+'%), '+str(len(Dgot1s))+' ('+"{:5.2f}".format(Dgot1spct)+'%), '+str(len(Ngot1s))+' ('+"{:5.2f}".format(Ngot1spct)+'%)',xy=(0.01,1.18),xycoords='axes fraction',size=7,color='deeppink')
    plt.annotate('ATclim: '+str(len(got2s))+' ('+"{:5.2f}".format(got2spct)+'%), '+str(len(Dgot2s))+' ('+"{:5.2f}".format(Dgot2spct)+'%), '+str(len(Ngot2s))+' ('+"{:5.2f}".format(Ngot2spct)+'%)',xy=(0.01,1.14),xycoords='axes fraction',size=7,color='red')
    plt.annotate('ATround: '+str(len(got3s))+' ('+"{:5.2f}".format(got3spct)+'%), '+str(len(Dgot3s))+' ('+"{:5.2f}".format(Dgot3spct)+'%), '+str(len(Ngot3s))+' ('+"{:5.2f}".format(Ngot3spct)+'%)',xy=(0.01,1.10),xycoords='axes fraction',size=7,color='darkorange')
    plt.annotate('ATrep: '+str(len(got4s))+' ('+"{:5.2f}".format(got4spct)+'%), '+str(len(Dgot4s))+' ('+"{:5.2f}".format(Dgot4spct)+'%), '+str(len(Ngot4s))+' ('+"{:5.2f}".format(Ngot4spct)+'%)',xy=(0.01,1.06),xycoords='axes fraction',size=7,color='gold')
    plt.annotate('DPTbud: '+str(len(got5s))+' ('+"{:5.2f}".format(got5spct)+'%), '+str(len(Dgot5s))+' ('+"{:5.2f}".format(Dgot5spct)+'%), '+str(len(Ngot5s))+' ('+"{:5.2f}".format(Ngot5spct)+'%)',xy=(0.01,1.02),xycoords='axes fraction',size=7,color='grey')
    plt.annotate('DPTclim: '+str(len(got6s))+' ('+"{:5.2f}".format(got6spct)+'%), '+str(len(Dgot6s))+' ('+"{:5.2f}".format(Dgot6spct)+'%), '+str(len(Ngot6s))+' ('+"{:5.2f}".format(Ngot6spct)+'%)',xy=(0.51,1.22),xycoords='axes fraction',size=7,color='limegreen')
    plt.annotate('DPTssat: '+str(len(got7s))+' ('+"{:5.2f}".format(got7spct)+'%), '+str(len(Dgot7s))+' ('+"{:5.2f}".format(Dgot7spct)+'%), '+str(len(Ngot7s))+' ('+"{:5.2f}".format(Ngot7spct)+'%)',xy=(0.51,1.18),xycoords='axes fraction',size=7,color='olivedrab')
    plt.annotate('DPTround: '+str(len(got8s))+' ('+"{:5.2f}".format(got8spct)+'%), '+str(len(Dgot8s))+' ('+"{:5.2f}".format(Dgot8spct)+'%), '+str(len(Ngot8s))+' ('+"{:5.2f}".format(Ngot8spct)+'%)',xy=(0.51,1.14),xycoords='axes fraction',size=7,color='blue')
    plt.annotate('DPTrep: '+str(len(got9s))+' ('+"{:5.2f}".format(got9spct)+'%), '+str(len(Dgot9s))+' ('+"{:5.2f}".format(Dgot9spct)+'%), '+str(len(Ngot9s))+' ('+"{:5.2f}".format(Ngot9spct)+'%)',xy=(0.51,1.10),xycoords='axes fraction',size=7,color='indigo')
    plt.annotate('DPTrepsat: '+str(len(got10s))+' ('+"{:5.2f}".format(got10spct)+'%), '+str(len(Dgot10s))+' ('+"{:5.2f}".format(Dgot10spct)+'%), '+str(len(Ngot10s))+' ('+"{:5.2f}".format(Ngot10spct)+'%)',xy=(0.51,1.06),xycoords='axes fraction',size=7,color='violet')
    #plt.tight_layout()
    
#    plt.savefig(OUTDIR+OutQCFil+".eps")
    plt.savefig(OUTDIR+OutQCFil+".png")

    # Write out stats to file (append!)
    filee=open(OUTDIR+OutQCText,'a+')
    filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(nobs)+\
                                                          ' BADs: '+'{:8d}'.format(len(gotBADs))+' ('+"{:5.2f}".format(gotspct)+\
                                                          '%) trk: '+'{:8d}'.format(len(got0s))+' ('+"{:5.2f}".format(got0spct)+\
                                                          '%) ATbud: '+'{:8d}'.format(len(got1s))+' ('+"{:5.2f}".format(got1spct)+\
							  '%) ATclim: '+'{:8d}'.format(len(got2s))+' ('+"{:5.2f}".format(got2spct)+\
							  '%) ATround: '+'{:8d}'.format(len(got3s))+' ('+"{:5.2f}".format(got3spct)+\
							  '%) ATrep: '+'{:8d}'.format(len(got4s))+' ('+"{:5.2f}".format(got4spct)+\
							  '%) DPTbud: '+'{:8d}'.format(len(got5s))+' ('+"{:5.2f}".format(got5spct)+\
                                                          '%) DPTclim: '+'{:8d}'.format(len(got6s))+' ('+"{:5.2f}".format(got6spct)+\
							  '%) DPTssat: '+'{:8d}'.format(len(got7s))+' ('+"{:5.2f}".format(got7spct)+\
							  '%) DPTround: '+'{:8d}'.format(len(got8s))+' ('+"{:5.2f}".format(got8spct)+\
							  '%) DPTrep: '+'{:8d}'.format(len(got9s))+' ('+"{:5.2f}".format(got9spct)+\
							  '%) DPTrepsat: '+'{:8d}'.format(len(got10s))+' ('+"{:5.2f}".format(got10spct)+\
							  '%)\n'))
    filee.close()

    filee=open(OUTDIR+OutQCTextD,'a+')
    filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(Dnobs)+\
                                                          ' BADs: '+'{:8d}'.format(len(DgotBADs))+' ('+"{:5.2f}".format(Dgotspct)+\
                                                          '%) trk: '+'{:8d}'.format(len(Dgot0s))+' ('+"{:5.2f}".format(Dgot0spct)+\
                                                          '%) ATbud: '+'{:8d}'.format(len(Dgot1s))+' ('+"{:5.2f}".format(Dgot1spct)+\
							  '%) ATclim: '+'{:8d}'.format(len(Dgot2s))+' ('+"{:5.2f}".format(Dgot2spct)+\
							  '%) ATround: '+'{:8d}'.format(len(Dgot3s))+' ('+"{:5.2f}".format(Dgot3spct)+\
							  '%) ATrep: '+'{:8d}'.format(len(Dgot4s))+' ('+"{:5.2f}".format(Dgot4spct)+\
							  '%) DPTbud: '+'{:8d}'.format(len(Dgot5s))+' ('+"{:5.2f}".format(Dgot5spct)+\
                                                          '%) DPTclim: '+'{:8d}'.format(len(Dgot6s))+' ('+"{:5.2f}".format(Dgot6spct)+\
							  '%) DPTssat: '+'{:8d}'.format(len(Dgot7s))+' ('+"{:5.2f}".format(Dgot7spct)+\
							  '%) DPTround: '+'{:8d}'.format(len(Dgot8s))+' ('+"{:5.2f}".format(Dgot8spct)+\
							  '%) DPTrep: '+'{:8d}'.format(len(Dgot9s))+' ('+"{:5.2f}".format(Dgot9spct)+\
							  '%) DPTrepsat: '+'{:8d}'.format(len(Dgot10s))+' ('+"{:5.2f}".format(Dgot10spct)+\
							  '%)\n'))
    filee.close()

    filee=open(OUTDIR+OutQCTextN,'a+')
    filee.write(str(year1+' '+year2+' '+month1+' '+month2+' NOBS: '+'{:8d}'.format(Nnobs)+\
                                                          ' BADs: '+'{:8d}'.format(len(NgotBADs))+' ('+"{:5.2f}".format(Ngotspct)+\
                                                          '%) trk: '+'{:8d}'.format(len(Ngot0s))+' ('+"{:5.2f}".format(Ngot0spct)+\
                                                          '%) ATbud: '+'{:8d}'.format(len(Ngot1s))+' ('+"{:5.2f}".format(Ngot1spct)+\
							  '%) ATclim: '+'{:8d}'.format(len(Ngot2s))+' ('+"{:5.2f}".format(Ngot2spct)+\
							  '%) ATround: '+'{:8d}'.format(len(Ngot3s))+' ('+"{:5.2f}".format(Ngot3spct)+\
							  '%) ATrep: '+'{:8d}'.format(len(Ngot4s))+' ('+"{:5.2f}".format(Ngot4spct)+\
							  '%) DPTbud: '+'{:8d}'.format(len(Ngot5s))+' ('+"{:5.2f}".format(Ngot5spct)+\
                                                          '%) DPTclim: '+'{:8d}'.format(len(Ngot6s))+' ('+"{:5.2f}".format(Ngot6spct)+\
							  '%) DPTssat: '+'{:8d}'.format(len(Ngot7s))+' ('+"{:5.2f}".format(Ngot7spct)+\
							  '%) DPTround: '+'{:8d}'.format(len(Ngot8s))+' ('+"{:5.2f}".format(Ngot8spct)+\
							  '%) DPTrep: '+'{:8d}'.format(len(Ngot9s))+' ('+"{:5.2f}".format(Ngot9spct)+\
							  '%) DPTrepsat: '+'{:8d}'.format(len(Ngot10s))+' ('+"{:5.2f}".format(Ngot10spct)+\
							  '%)\n'))
    filee.close()

    #pdb.set_trace()

if __name__ == '__main__':
    
    main(sys.argv[1:])




#************************************************************************
