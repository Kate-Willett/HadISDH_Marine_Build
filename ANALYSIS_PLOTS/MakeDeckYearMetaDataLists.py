#!/usr/local/sci/bin/python
# PYTHON2.7
# 
# Author: Kate Willett
# Created: 7 October 2016
# Last update: 7 October 2016
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/ANALYSIS_PLOTS/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code reads in the ICOADS data output from QC using MDS_RWtools.py and
# pulls out the height and instrument metadata to make lists of stats by year and by deck.
#
# I think we should do this on the OBSclim2NBC files because these could differ in number of obs compared to the 
# ERAclimNBC and OBSclim1NBC files - we're only outputting data that have a climatology!
#
# There is a file for each year with a line for each deck:  DeckYearMetaDataList_1973_ICOADS251.txt
# First Line = headers: 
# Deck, No. Obs, Pct. Obs, \
# No. Hgt, Pct Hgt, \
# MeanHOA, SDHOA, No. HOA, Pct. HOA, MeanHOP, SDHOP, No. HOP, Pct. HOP, MeanHOT, SDHOT, No. HOT, Pct. HOT, MeanHOB, SDHOB, No. HOB, Pct. HOB, \
# No. Exp, Pct Exp, \
# No. NoAsp, Pct. NoAsp, No. Asp, Pct. Asp (NoAsp = VS/S/SN, Asp = U/A/SG/SL/W)
# Second line = stats for ALL 
# In each following line - stats for each DECK:
# Deck Number 
# No. of obs in deck
# % of all obs in deck
# No. of obs with height info
# % of deck with Height Info
# Mean HOAs present
# SD HOAs present
# No. HOAs present
# % of deck (with some Height MetaData) with HOAs present
# Mean HOPs present
# SD HOPs present
# No. HOPs present
# % of deck (with some Height MetaData) with HOPs present
# Mean HOTs present
# SD HOTs present
# No. HOTs present
# % of deck (with some Height MetaData) with HOTs present
# Mean HOBs present
# SD HOBs present
# No. HOBs present
# % of deck (with some Height MetaData) with HOBs present
# No. of obs with Exposure info
# % of deck with Exposure Info
# No. NoAsp
# Pct. of deck (with some exposure MetaData) that are NoAsp
# No. Asp
# Pct. of deck (with some exposure MetaData) that are Asp
# One extra line for those obs with no deck just in case
#
# What about buoys and platforms? Do they share decks with ships?
# Do this for ALL, SHIP only, BUOY only and PLATFORM only
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
# import MDS_RWtools as mrw
#
# -----------------------
# DATA
# -----------------------
# /project/hadobs2/hadisdh/marine/ICOADS.2.5.1/OBSclim2NBC/new_suite_197301_OBSclim1NBC.txt
#
# -----------------------
# HOW TO RUN THE CODE
# -----------------------
#
# python2.7 MakeDeckYearMetaDataLists.py --year1 1973 --year2 1973 --month1 1 --month2 12 --switch all
# switch can be all, ships, buoys, platforms
#
# This runs the code, outputs the plots and stops mid-process so you can then interact with the
# data. 
# 
# -----------------------
# OUTPUT
# -----------------------
#
# a text file of stats
# /data/local/hadkw/HADCRUH2/MARINE/LISTS/DeckYearMetaDataStats_1973_ICOADS251_all_OBSclim2NBC_OCT2016.txt
# 
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
# 
# Version 1 (7 October 2016)
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

import MDS_RWtools as mrw

typee = 'OBSclim2NBC'
nowmon = 'AUG'
nowyear = '2018'


#************************************************************************
# Main
#************************************************************************

def main(argv):
    # INPUT PARAMETERS AS STRINGS!!!!
    year1 = '1973' 
    year2 = '1973'
    month1 = '01' # months must be 01, 02 etc
    month2 = '12'
    # switch = 'all' # include all obs
    # switch = 'ships' # include only ships with PT = 0, 1, 2, 3, 4, 5 - can be ships0, ships1, ships2, ships3, ships4, ships5
    # switch = 'buoys' # include only those obs with PT = 6(moored), 8(ice) - can be buoys6, buoys8 (but very little point as no metadata!)
    # switch = 'platforms' # include only those obs with PT = 9(ice), 10(oceanographic), 15 (fixed ocean) NO METADATA!!!
    switch = 'all'

    try:
        opts, args = getopt.getopt(argv, "hi:",
	                           ["year1=","year2=","month1=","month2=","switch="])
    except getopt.GetoptError:
        print 'Usage (as strings) PlotMetaData_APR2016.py --year1 <1973> --year2 <1973> '+\
	      '--month1 <01> --month2 <12> --switch <all>'
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
        elif opt == "--switch":
            try:
                switch = arg
            except:
                sys.exit("Failed: switch not a string")
 
    assert year1 != -999 and year2 != -999, "Year not specified."

    print(year1, year2, month1, month2, switch)
#    pdb.set_trace()
    					   

#    OUTDIR = '/data/local/hadkw/HADCRUH2/MARINE/'
    OUTDIR = ''
    OutFil = 'LISTS/DeckYearMetaDataStats_'+year1+year2+month1+month2+'_I300_55_'+switch+'_'+typee+'_'+nowmon+nowyear+'.txt'
#    OutFil = 'LISTS/DeckYearMetaDataStats_'+year1+year2+month1+month2+'_ICOADS251_'+switch+'_'+typee+'_'+nowmon+nowyear+'.txt'

    # create empty arrays for data bundles
    nobs=0 # we're looking at all obs, not just those with 'good' data
    DCKbun = []
    EOTbun = []
    #TOHbun = []
    EOHbun = []
    HOTbun = []
    HOBbun = []
    HOAbun = []
    HOPbun = []

    # loop through each month, read in data, keep metadata needed
    for yy in range((int(year2)+1)-int(year1)):
        for mm in range((int(month2)+1)-int(month1)):
            print(str(yy+int(year1)),' ','{:02}'.format(mm+int(month1)))

            MDSdict=mrw.ReadMDSstandard(str(yy+int(year1)),'{:02}'.format(mm+int(month1)), typee)

	    if (nobs == 0):
	        if (switch == 'all'):
	            DCKbun = MDSdict['DCK']
	            EOTbun = MDSdict['EOT']
	            #TOHbun = MDSdict['TOH']
	            EOHbun = MDSdict['EOH']
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
	            DCKbun = MDSdict['DCK'][pointers]
	            EOTbun = MDSdict['EOT'][pointers]
	            #TOHbun = MDSdict['TOH'][pointers]
	            EOHbun = MDSdict['EOH'][pointers]
	            HOTbun = MDSdict['HOT'][pointers]
	            HOBbun = MDSdict['HOB'][pointers]
	            HOAbun = MDSdict['HOA'][pointers]
	            HOPbun = MDSdict['HOP'][pointers]
            else:
	        if (switch == 'all'):
	            DCKbun = np.append(DCKbun,MDSdict['DCK'])
	            EOTbun = np.append(EOTbun,MDSdict['EOT'])
	            #TOHbun = np.append(TOHbun,MDSdict['TOH'])
	            EOHbun = np.append(EOHbun,MDSdict['EOH'])
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
	            DCKbun = np.append(DCKbun,MDSdict['DCK'][pointers])
	            EOTbun = np.append(EOTbun,MDSdict['EOT'][pointers])
	            #TOHbun = np.append(TOHbun,MDSdict['TOH'][pointers])
	            EOHbun = np.append(EOHbun,MDSdict['EOH'][pointers])
	            HOTbun = np.append(HOTbun,MDSdict['HOT'][pointers])
	            HOBbun = np.append(HOBbun,MDSdict['HOB'][pointers])
	            HOAbun = np.append(HOAbun,MDSdict['HOA'][pointers])
	            HOPbun = np.append(HOPbun,MDSdict['HOP'][pointers])
	
            if (switch == 'all'):
	        nobs = nobs + len(MDSdict['DCK'])
	    else:
	        nobs = nobs + len(MDSdict['DCK'][pointers])
	        
	    MDSdict = 0 # clear out

    # Write out stats to file (append!)
    filee=open(OUTDIR+OutFil,'a+')
    filee.write('DECK No. Obs Pc.Obs No. Hgt Pc.Hgt  MnHOA  SdHOA  No.HOA Pc.HOA  MnHOP  SdHOP  No.HOP Pc.HOP  MnHOT  SdHOT  No.HOT Pc.HOT  MnHOB  SdHOB  No.HOB Pc.HOB No. Exp Pc.Exp No.NASP PcNASP No. ASP Pc.ASP\n')

    # Get stats for ALL obs
    
    ASPpct = 0.
    NoASPpct = 0.
    TotExp = len(np.where(EOHbun != 'Non')[0])
    ASPgots = np.where((EOHbun == 'A  ') | (EOHbun == 'SG ') | (EOHbun == 'SL ') | (EOHbun == 'W  ') | (EOHbun == 'US '))[0]
    if (len(ASPgots) > 0):
        ASPpct = (len(ASPgots)/float(TotExp))*100.
    NoASPgots = np.where((EOHbun == 'VS ') | (EOHbun == 'S  ') | (EOHbun == 'SN '))[0]
    if (len(NoASPgots) > 0):
        NoASPpct = (len(NoASPgots)/float(TotExp))*100.

    HOApct = 0.
    HOPpct = 0.
    HOTpct = 0.
    HOBpct = 0.
    MnHOA = 0.
    MnHOP = 0.
    MnHOT = 0.
    MnHOB = 0.
    SdHOA = 0.
    SdHOP = 0.
    SdHOT = 0.
    SdHOB = 0.
    TotHeight = len(np.where((HOAbun > 0) | (HOPbun > 0) | (HOTbun > 0) | (HOBbun > 0))[0])
    HOAgots = np.where(HOAbun > 0)[0]
    if (len(HOAgots) > 0):
        HOApct = (len(HOAgots)/float(TotHeight))*100.
        MnHOA = np.mean(HOAbun[HOAgots])
	SdHOA = np.std(HOAbun[HOAgots])
    HOPgots = np.where(HOPbun > 0)[0]
    if (len(HOPgots) > 0):
        HOPpct = (len(HOPgots)/float(TotHeight))*100.
	MnHOP = np.mean(HOPbun[HOPgots])
	SdHOP = np.std(HOPbun[HOPgots])
    HOTgots = np.where(HOTbun > 0)[0]
    if (len(HOTgots) > 0):
        HOTpct = (len(HOTgots)/float(TotHeight))*100
	MnHOT = np.mean(HOTbun[HOTgots])
	SdHOT = np.std(HOTbun[HOTgots])
    HOBgots = np.where(HOBbun > 0)[0]
    if (len(HOBgots) > 0):
        HOBpct = (len(HOBgots)/float(TotHeight))*100
	MnHOB = np.mean(HOBbun[HOBgots])
	SdHOB = np.std(HOBbun[HOBgots])    

    filee.write(str(' ALL'+\
                '{:8d}'.format(nobs)+\
		' 100.00'+\
                '{:8d}'.format(TotHeight)+\
		'{:7.2f}'.format((TotHeight / float(nobs))*100.)+\
                '{:7.2f}'.format(MnHOA)+\
                '{:7.2f}'.format(SdHOA)+\
                '{:8d}'.format(len(HOAgots))+\
		'{:7.2f}'.format(HOApct)+\
                '{:7.2f}'.format(MnHOP)+\
                '{:7.2f}'.format(SdHOP)+\
                '{:8d}'.format(len(HOPgots))+\
		'{:7.2f}'.format(HOPpct)+\
                '{:7.2f}'.format(MnHOT)+\
                '{:7.2f}'.format(SdHOT)+\
                '{:8d}'.format(len(HOTgots))+\
		'{:7.2f}'.format(HOTpct)+\
                '{:7.2f}'.format(MnHOB)+\
                '{:7.2f}'.format(SdHOB)+\
                '{:8d}'.format(len(HOBgots))+\
		'{:7.2f}'.format(HOBpct)+\
                '{:8d}'.format(TotExp)+\
		'{:7.2f}'.format((TotExp / float(nobs))*100.)+\
                '{:8d}'.format(len(NoASPgots))+\
		'{:7.2f}'.format(NoASPpct)+\
                '{:8d}'.format(len(ASPgots))+\
		'{:7.2f}'.format(ASPpct)+
		'\n'))

    # Now work out how many unique decks we're dealing with, included missing deck '   ' and loop through each
    UniqDecks = np.unique(DCKbun)
    for i,dck in enumerate(UniqDecks):
    
        ThisDck = np.where(DCKbun == dck)[0]
	TotDck = len(ThisDck)
 
        ASPpct = 0.
        NoASPpct = 0.
        TotExp = len(np.where(EOHbun[ThisDck] != 'Non')[0])
        ASPgots = np.where((EOHbun[ThisDck] == 'A  ') | (EOHbun[ThisDck] == 'SG ') | (EOHbun[ThisDck] == 'SL ') | (EOHbun[ThisDck] == 'W  ') | (EOHbun[ThisDck] == 'US '))[0]
        if (len(ASPgots) > 0):
            ASPpct = (len(ASPgots)/float(TotExp))*100.
        NoASPgots = np.where((EOHbun[ThisDck] == 'VS ') | (EOHbun[ThisDck] == 'S  ') | (EOHbun[ThisDck] == 'SN '))[0]
        if (len(NoASPgots) > 0):
            NoASPpct = (len(NoASPgots)/float(TotExp))*100.

        HOApct = 0.
        HOPpct = 0.
        HOTpct = 0.
        HOBpct = 0.
        MnHOA = 0.
        MnHOP = 0.
        MnHOT = 0.
        MnHOB = 0.
        SdHOA = 0.
        SdHOP = 0.
        SdHOT = 0.
        SdHOB = 0.
        TotHeight = len(np.where((HOAbun[ThisDck] > 0) | (HOPbun[ThisDck] > 0) | (HOTbun[ThisDck] > 0) | (HOBbun[ThisDck] > 0))[0])
        HOAgots = np.where(HOAbun[ThisDck] > 0)[0]
        if (len(HOAgots) > 0):
            HOApct = (len(HOAgots)/float(TotHeight))*100.
            MnHOA = np.mean(HOAbun[ThisDck[HOAgots]])
	    SdHOA = np.std(HOAbun[ThisDck[HOAgots]])
        HOPgots = np.where(HOPbun[ThisDck] > 0)[0]
        if (len(HOPgots) > 0):
            HOPpct = (len(HOPgots)/float(TotHeight))*100.
	    MnHOP = np.mean(HOPbun[ThisDck[HOPgots]])
	    SdHOP = np.std(HOPbun[ThisDck[HOPgots]])
        HOTgots = np.where(HOTbun[ThisDck] > 0)[0]
        if (len(HOTgots) > 0):
            HOTpct = (len(HOTgots)/float(TotHeight))*100
	    MnHOT = np.mean(HOTbun[ThisDck[HOTgots]])
	    SdHOT = np.std(HOTbun[ThisDck[HOTgots]])
        HOBgots = np.where(HOBbun[ThisDck] > 0)[0]
        if (len(HOBgots) > 0):
            HOBpct = (len(HOBgots)/float(TotHeight))*100
	    MnHOB = np.mean(HOBbun[ThisDck[HOBgots]])
	    SdHOB = np.std(HOBbun[ThisDck[HOBgots]])    

        filee.write(str('{:4d}'.format(dck)+\
                '{:8d}'.format(TotDck)+\
                '{:7.2f}'.format((TotDck / float(nobs))*100.)+\
                '{:8d}'.format(TotHeight)+\
		'{:7.2f}'.format((TotHeight / float(TotDck))*100.)+\
                '{:7.2f}'.format(MnHOA)+\
                '{:7.2f}'.format(SdHOA)+\
                '{:8d}'.format(len(HOAgots))+\
		'{:7.2f}'.format(HOApct)+\
                '{:7.2f}'.format(MnHOP)+\
                '{:7.2f}'.format(SdHOP)+\
                '{:8d}'.format(len(HOPgots))+\
		'{:7.2f}'.format(HOPpct)+\
                '{:7.2f}'.format(MnHOT)+\
                '{:7.2f}'.format(SdHOT)+\
                '{:8d}'.format(len(HOTgots))+\
		'{:7.2f}'.format(HOTpct)+\
                '{:7.2f}'.format(MnHOB)+\
                '{:7.2f}'.format(SdHOB)+\
                '{:8d}'.format(len(HOBgots))+\
		'{:7.2f}'.format(HOBpct)+\
                '{:8d}'.format(TotExp)+\
		'{:7.2f}'.format((TotExp / float(TotDck))*100.)+\
                '{:8d}'.format(len(NoASPgots))+\
		'{:7.2f}'.format(NoASPpct)+\
                '{:8d}'.format(len(ASPgots))+\
		'{:7.2f}'.format(ASPpct)+
		'\n'))

	
    filee.close()

    #pdb.set_trace()

if __name__ == '__main__':
    
    main(sys.argv[1:])




#************************************************************************
