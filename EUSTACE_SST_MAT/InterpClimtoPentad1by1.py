#!/usr/local/sci/bin/python
# PYTHON2.7
# 
# Author: Kate Willett
# Created: 11 Sep 2016
# Last update: 11 Sep 2016
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/EUSTACE_SST_MAT/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code reads in the monthly 5by5 climatology from the obs and converts 
# it to pentad 1by1
#
# ANNOYINGLY WE CANNOT ASSUME THAT IF A CLIM IS PRESENT AN SD IS ALSO PRESENT!!! 
# THESE SHOULD BE THE SAME BECAUSE SD IS THE SD OF ALL MONTHS GOING INTO THE CLIM!!! 
# NEED TO GET ROBERT TO LOOK AT THIS!!!
#
# 1) Fill in any individual missing 5by5 gridbox months in time with a 
#    month present before and after by giving it the MEAN of the two 
#    surrounding months for climatology and the MAXIMUM of the two 
#    surrounding months for stdev
#    Allow continuation December to January
#    Then go over again and fill any missing end points by previous point
#    and half of the difference to the next point to account for uncertainty
#    in that point not carrying on in the same direction
# 2) Fill in any individual missing 5by5 gridbox months 
#    in space that have at least two adjacent gridboxes (Including one at same latitude or both the latitude above/below) by giving it the 
#    MEAN of the surrounding months for climatology and the MAXIMUM of the 
#    surrounding months for stdev   
# 3) Interpolate smoothly across each 5by5 gridbox month to 
#    divide into the appropriate number of pentads in time in equal steps 
#    between the preceding and following 5by5 gridbox months, ensuring that 
#    the mean of the pentads is equal to the monthly value. If the candidate 
#    month is higher/lower than both preceding and following months then the 
#    middle pentad will take peak/trough. Same for clim and stdev.
# 4) Interpolate smoothly across each 5by5 gridbox pentad to 
#    divide into the 5 1by1 gridboxes in space, ensuring that the mean of 
#    all 1by1 pentad gridboxes is equal to the 5by5 pentad gridbox value. 
#    This will be done as smoothly as possible. Ideally (although 
#    arbitrarily) if the surrounding gridboxes are mostly higher/lower then 
#    the trough/peak will tend towards the middle 1by1 pentad gridbox 
#    within the 5by5. This will be quite complex though. Same for clim and 
#    stdev.
#
# NOTE:
# Tests allow for differences in coverage between climatologies and standard deviations although I would hope there are none
# Tests check for standard deviations going below zero (InterpTime, InterpSpace(shouldn't but check anyway) 
# - in this event the filled value is given the nearest non-zero value
# Tests check for q, e, RH and DPD going below zero (Climatology - InterpTime and InterpSpace) and RH going above 100
# - in this event the filled value is given the nearest non-zero value 
# There is an added mask which states if a value is real (1), time infilled (2) or space infilled (3)
#
# -----------------------
# LIST OF MODULES
# -----------------------
# inbuilt:
# import datetime as dt
## Folling two lines should be uncommented if using with SPICE or screen or /project
## import matplotlib
## matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import numpy as np
# from matplotlib.dates import date2num,num2date
# from datetime import datetime
# import sys, os
# import sys, getopt
# from scipy.optimize import curve_fit,fsolve,leastsq
# from scipy import pi,sqrt,exp
# from scipy.special import erf
# from scipy.interpolate import griddata # for interpolation in InterpSpace
# import scipy.stats
# from math import sqrt,pi
# import struct
# from netCDF4 import Dataset
# from netCDF4 import stringtoarr # for putting strings in as netCDF variables
# import pdb # pdb.set_trace() or c 
#
# -----------------------
# DATA
# -----------------------
# 
# OBS 1981-2010 clims:
# /project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS/ERAclimNBC_5x5_monthly_climatology_from_daily_both_relax.nc
#
# -----------------------
# HOW TO RUN THE CODE
# -----------------------
# make sure the file paths are ok - are we always using ERAclimNBC?
#
# python2.7 InterpClimtoPentad1by1.py
#
# python2.7 InterpClimtoPentad1by1.py --varee 'q' (and or --typee 'ERAclimNBC' 
#
# This runs the code which saves pentad 1by1 version of the climatology
#
# -----------------------
# OUTPUT
# -----------------------
# Pentad 1by1 climatologies
# /project/hadobs2/hadisdh/marine/otherdata/ERAclimNBC_1x1_pentad_climatology_from_5x5_monthly_both_relax.nc
# 
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
# 
# Version 1 (19 Sep 2016)
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
# Folling two lines should be uncommented if using with SPICE or screen or /project
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import matplotlib.cm as mpl_cm
import numpy as np
from matplotlib.dates import date2num,num2date
from mpl_toolkits.basemap import Basemap
from datetime import datetime
import sys, os
import sys, getopt
from scipy.optimize import curve_fit,fsolve,leastsq
from scipy import pi,sqrt,exp
from scipy.special import erf
from scipy.interpolate import griddata # for interpolation in InterpSpace
import scipy.stats
from math import sqrt,pi
import struct
from netCDF4 import Dataset
from netCDF4 import stringtoarr # for putting strings in as netCDF variables
import pdb # pdb.set_trace() or c 

#************************************************************************
# FUNCTIONS
#************************************************************************
# InfillTime
def InfillTime(WorkingArrClim, WorkingArrSD, TheMDI, TheMaskClim, TheMaskSD):
    ''' Take a 3D array: WorkingArr '''
    ''' Work through gridboxes lat and lon '''
    ''' Fill in any individual missing (Include December to January) 5by5 gridbox months in time with a ''' 
    ''' month present before and after by giving it the '''
    ''' MEAN of the two surrounding months for climatology '''
    ''' MAXIMUM of the two surrounding months for stdev '''
    ''' Conduct a second sweep to add points to loose ends - half preceding distance for Clim, Repeat value for SD '''
    ''' Block repeat extrapolation forward to avoid undue silliness '''
    ''' THIS FUNCTION DOES NOT ASSUME THAT DATA PRESENCE IS IDENTICAL FOR Clim and SD '''
    ''' I thought I had spotted differences in data presence but infill counts suggest not '''

    # A counter for the number of months infilled
    CountInfillsClim = 0
    CountInfillsSD = 0

    # an integer array indexing the time points
    pointsarr = np.array(range(len(WorkingArrClim[:,0,0])))

    # Loop through each longitude box
    for lln in range(len(WorkingArrClim[0,0,:])):
    
    # Loop through each latitude box
        for llt in range(len(WorkingArrClim[0,:,0])):
    
    # Work through all time periods from 1 to n-1 (starts at 0!) and include a check for December-January
    # Start with individual gaps, then loose ends
	    # Check there are some data present to play with
	    #print(llt,lln)
	    # BY THE WAY - TESTED WHETHER mdi within arrays == TheMDI in np.where test - they do!! Hurrah!
            if (len(np.where(WorkingArrClim[:,llt,lln] > TheMDI)[0]) > 1):

    # If there are at least 2 points then begin infilling
    # 1) Infill individual missing gaps 
		for mm in range(len(WorkingArrClim[:,0,0])):

		    # Get preceding and proceding points first
		    if (mm == 0): 
			preP = 11
                    else:
                        preP = mm-1
			    
                    if (mm == (len(WorkingArrClim[:,0,0])-1)):
                        postP = 0
                    else:
                        postP = mm+1     
		    
		    # Is the CLIM candidate missing? - then try to infill
		    if (WorkingArrClim[mm,llt,lln] == TheMDI):
		    
		    # Is there a value either side to interpolate?			    
		        if ((WorkingArrClim[preP,llt,lln] > TheMDI) & (WorkingArrClim[postP,llt,lln] > TheMDI)):
			    WorkingArrClim[mm,llt,lln] = np.mean([WorkingArrClim[[preP,postP],llt,lln]])
			    TheMaskClim[mm,llt,lln] = 2

                    # Increment the counter
                            CountInfillsClim = CountInfillsClim+1
			    #print('Fill Gap CLIM: ',mm, preP, postP, CountInfillsClim, WorkingArrClim[mm,llt,lln], WorkingArrClim[[preP,postP],llt,lln])
		            #pdb.set_trace()
			    # TESTING for 't' - this looks like it is working exactly as I intended

		    # Is the SD candidate missing? - then try to infill
		    if (WorkingArrSD[mm,llt,lln] == TheMDI):
		    
		    # Is there a value either side to interpolate?			    
		        if ((WorkingArrSD[preP,llt,lln] > TheMDI) & (WorkingArrSD[postP,llt,lln] > TheMDI)):
			    WorkingArrSD[mm,llt,lln] = np.max([WorkingArrSD[[preP,postP],llt,lln]])
			    TheMaskSD[mm,llt,lln] = 2

                    # Increment the counter
                            CountInfillsSD = CountInfillsSD+1
			    #print('Fill Gap SD: ',mm, preP, postP, CountInfillsSD, WorkingArrSD[mm,llt,lln], WorkingArrSD[[preP,postP],llt,lln])
		            #pdb.set_trace()
			    # TESTING for 't' - this looks like it is working exactly as I intended

    # 2) Tie up loose ends - where there are larger gaps we can add points if there are at least 2 valid points to one side
    # by projecting the rate of change/divided by 2 (divide by 2 to make a smaller projection because the point could go in any directions
    # Better to have a point that not to some extent?
    # Start with extrapolation forwards which has a catch on it to prevent multiple extrapolation
    # If no forwards extrapolation then look for backwards extrapolation - prevents multiple backwards extrapolation if actual values available for forwards
		# switches to catch repeated forwards extrapolation, 0 = carry on, 1 = already done it = stop!
		catchCLIM = 0
		catchSD = 0
		for mm in range(len(WorkingArrClim[:,0,0])):

		    # Get preceding and proceding points first
		    if (mm == 0): 
			preP = [len(WorkingArrClim[:,0,0])-2,len(WorkingArrClim[:,0,0])-1]
	            elif (mm == 1):
			preP = [len(WorkingArrClim[:,0,0])-1,0]
		    else:
			preP = [mm-2,mm-1]
			    
	            if (mm == (len(WorkingArrClim[:,0,0])-1)):
			postP = [0,1]
                    elif (mm == (len(WorkingArrClim[:,0,0])-2)):
			postP = [len(WorkingArrClim[:,0,0])-1,0]
		    else:
			postP = [mm+1,mm+2]     
		    
		    # Is the CLIM candidate missing? - then try to infill
		    if (WorkingArrClim[mm,llt,lln] == TheMDI):
		    
		    # Are there two values following to extrapolate a value forward? ONLY DO THIS ONCE IN A ROW!!!		    
		        if ((WorkingArrClim[preP[0],llt,lln] > TheMDI) & (WorkingArrClim[preP[1],llt,lln] > TheMDI) & (catchCLIM == 0)):
			    WorkingArrClim[mm,llt,lln] = WorkingArrClim[preP[1],llt,lln] + ((WorkingArrClim[preP[1],llt,lln] - WorkingArrClim[preP[0],llt,lln]) / 2.)
			    TheMaskClim[mm,llt,lln] = 2
			    catchCLIM = 1
			    #print('Extrapolate Forward CLIM: ',mm, preP, CountInfillsClim, WorkingArrClim[mm,llt,lln], WorkingArrClim[preP,llt,lln])
		            #pdb.set_trace()
			    # TESTING for 't' - this looks like it is working exactly as I intended
                    # Increment the counter
                            CountInfillsClim = CountInfillsClim+1

		    # Are there two values following to extrapolate a value back?			    
		        elif ((WorkingArrClim[postP[0],llt,lln] > TheMDI) & (WorkingArrClim[postP[1],llt,lln] > TheMDI)):
			    WorkingArrClim[mm,llt,lln] = WorkingArrClim[postP[0],llt,lln] - ((WorkingArrClim[postP[1],llt,lln] - WorkingArrClim[postP[0],llt,lln]) / 2.)
			    TheMaskClim[mm,llt,lln] = 2
			    #print('Extrapolate Back CLIM: ',mm, postP, CountInfillsClim, WorkingArrClim[mm,llt,lln], WorkingArrClim[postP,llt,lln])
		            #pdb.set_trace()
			    # TESTING for 't' - this looks like it is working exactly as I intended
                    # Increment the counter
                            CountInfillsClim = CountInfillsClim+1
		    
			    
		    # We can only reset catchCLIM if we have had a real value after extrapolation	
		    else:
			catchCLIM = 0    

		    # Is the SD candidate missing? - then try to infill
		    if (WorkingArrSD[mm,llt,lln] == TheMDI):

		    # Are there two values following to extrapolate a value forward? - actually for SD just use previous value but require two to keep same as CLIM ONLY DO THIS ONCE IN A ROW!!!		    
		        if ((WorkingArrSD[preP[0],llt,lln] > TheMDI) & (WorkingArrSD[preP[1],llt,lln] > TheMDI) & (catchSD == 0)):
			    WorkingArrSD[mm,llt,lln] = WorkingArrSD[preP[1],llt,lln]
			    TheMaskSD[mm,llt,lln] = 2
			    catchSD = 1
			    #print('Extrapolate Forward SD: ',mm, preP, CountInfillsSD, WorkingArrSD[mm,llt,lln], WorkingArrSD[preP,llt,lln])
		            #pdb.set_trace()
			    # TESTING for 't' - this looks like it is working exactly as I intended
                    # Increment the counter
                            CountInfillsSD = CountInfillsSD+1
		    
		    # Are there two values following to extrapolate a value back? - actually for SD just use next value but require two to keep same as CLIM			    
		        elif ((WorkingArrSD[postP[0],llt,lln] > TheMDI) & (WorkingArrSD[postP[1],llt,lln] > TheMDI)):
			    WorkingArrSD[mm,llt,lln] = WorkingArrSD[postP[0],llt,lln]
			    TheMaskSD[mm,llt,lln] = 2
			    #print('Extrapolate Back SD: ',mm, postP, CountInfillsSD, WorkingArrSD[mm,llt,lln], WorkingArrSD[postP,llt,lln])
		            #pdb.set_trace()
			    # TESTING for 't' - this looks like it is working exactly as I intended
                    # Increment the counter
                            CountInfillsSD = CountInfillsSD+1		    

		    # We can only reset catchSD if we have had a real value after extrapolation	
		    else:
			catchSD = 0    
			
    # Print out total number of infills
    print("Total number of InfillTimes CLIM SD: ",CountInfillsClim, CountInfillsSD)	
    # For 't' GRIDS3 15 Sep 2016 - added 510 for CLIM and 510 for SD extra months 	    
    
    #pdb.set_trace()
    return WorkingArrClim, WorkingArrSD, TheMaskClim, TheMaskSD
# TEST NOTES:
# HAPPY WITH THIS 16 Sep 2016

#************************************************************************
# InfillSpace
def InfillSpace(WorkingArrClim, WorkingArrSD, TheMDI, TheMaskClim, TheMaskSD):
    ''' Take a 3D array: WorkingArr '''
    ''' Work through the months, find missing gridboxes that have at least two adjacent present gridboxes '''
    ''' Fill in any individual missing 5by5 gridbox months in space with a ''' 
    ''' month present value from the surrounding gridboxes (at least one same-latitude box '''
    ''' or both lat above/below needed) by giving it the '''
    ''' MEAN of the 2+ surrounding gridboxes for climatology '''
    ''' MAXIMUM of the 2+ surrounding gridboxes for stdev '''
    ''' THIS FUNCTION DOES NOT ASSUME THAT DATA PRESENCE IS IDENTICAL FOR Clim and SD '''
    ''' I thought I had spotted differences in data presence but infill counts suggest not '''

    # A counter for the number of months infilled
    CountInfillsClim = 0
    CountInfillsSD = 0
    
    # Get Dimensions
    TotMons = len(WorkingArrClim[:,0,0]) # only 12 for a monthly climatology
    TotLons = len(WorkingArrClim[0,0,:])
    TotLats = len(WorkingArrClim[0,:,0])

    # Loop through the time points
    for mm in range(TotMons):
    
    # Loop through each longitude box
        for lln in range(TotLons):
	    # Get the surrounds POINTS if lln western or eastern most aor not and
	    if (lln == 0):
	        LGpoints = [TotLons-1,0,1]		    
	    elif (lln == TotLons-1):
	        LGpoints = [lln-1,lln,0]
	    else:
	        LGpoints = [lln-1,lln,lln+1]
    
    # Loop through each latitude box
            for llt in range(TotLats):
	        # Get the surrounds RANGE VALUES if llt northern most or southern most or not and
	        if (llt == 0):
	            LTspan = [0,llt+2]
		    BOXLTspan = [1,3]
	        elif (llt == TotLats-1):
	            LTspan = [llt-1,llt+1]
		    BOXLTspan = [0,2]
	        else:
	            LTspan = [llt-1,llt+2]
		    BOXLTspan = [0,3]
    
    # Work through all gridboxes first and last longs can wrap around. Lats cannot - -90 and +90 ob unlikely!
    # Is the box missing and if so are there at least two surrounding gridboxes present?
                #print(mm,lln,llt)
		if ((WorkingArrClim[mm,llt,lln] == TheMDI) | (WorkingArrSD[mm,llt,lln] == TheMDI)):

                    # We need SurroundsBoxes to be 3by3s (different to InfillSpace)
		    SurroundsClim = np.empty((3,3))
		    SurroundsClim.fill(TheMDI)
		    SurroundsSD = np.copy(SurroundsClim)
		    MaskSurroundsClim = np.copy(SurroundsClim)
		    MaskSurroundsSD = np.copy(SurroundsClim)
		    		
                    # Work through all gridboxes first and last longs can wrap around. Lats cannot - -90 and +90 ob unlikely!
				
		    # Pull out the Surrounds
		    # NOTE THAT MIXING SPANS AND POINTS CHANGES THE ARRAY DIMENSION ORDER
		    # So - arr[0,0:2,[2,3,4]] results in a 3 row 2 column array annoyingly
		    # I've tested np.transpose on this and that solves the problem
		    SurroundsClim[BOXLTspan[0]:BOXLTspan[1],:] = np.transpose(WorkingArrClim[mm,LTspan[0]:LTspan[1],LGpoints])    
		    SurroundsSD[BOXLTspan[0]:BOXLTspan[1],:] = np.transpose(WorkingArrSD[mm,LTspan[0]:LTspan[1],LGpoints])    
		    MaskSurroundsClim[BOXLTspan[0]:BOXLTspan[1],:] = np.transpose(TheMaskClim[mm,LTspan[0]:LTspan[1],LGpoints])    
		    MaskSurroundsSD[BOXLTspan[0]:BOXLTspan[1],:] = np.transpose(TheMaskSD[mm,LTspan[0]:LTspan[1],LGpoints])    
		    #print("Check the Surrounds are working")
		    #pdb.set_trace() # Checking the pulled out surrounds are working ok
		    # TESTING for 't' - this works fine

    # CLIM Check if the middle box is missing, if there are at least 2 boxes present (middle one is missing of course!), 
    # and if there is at least one box on the same latitude? OR a box on both latitude above and below
		    if ((len(np.where(MaskSurroundsClim == 1)[0]) >= 2) & (WorkingArrClim[mm,llt,lln] == TheMDI) & (len(np.where(SurroundsClim > TheMDI)[0]) >= 2) & 
		        ((len(np.where(SurroundsClim[1,:] > TheMDI)[0]) > 0) | 
			((len(np.where(SurroundsClim[0,:] > TheMDI)[0]) > 0) & (len(np.where(SurroundsClim[2,:] > TheMDI)[0]) > 0)))):
			
			#if ((llt == 6) & (lln >= 15)):
			#    print(lln,llt,mm)
			#    pdb.set_trace()
		    
    # Infill the clim with the MEAN of the 2+ surrounding points
    # Weight this towards the candidatelatitude
                        # Cannot np.mean() over an array of complete mdis or it returns NaN
			# So we have to do this bit by bit
			if (len(np.where(SurroundsClim[1,:] > TheMDI)[0]) > 0):
			    MyMeanArr = SurroundsClim[1,np.where(SurroundsClim[1,:] > TheMDI)[0]]
			else:
			    MyMeanArr = []
			if (len(np.where(SurroundsClim[0,:] > TheMDI)[0]) > 0):
			    MyMeanArr = np.append(MyMeanArr,np.mean(SurroundsClim[0,np.where(SurroundsClim[0,:] > TheMDI)[0]]))
			if (len(np.where(SurroundsClim[2,:] > TheMDI)[0]) > 0):
			    MyMeanArr = np.append(MyMeanArr,np.mean(SurroundsClim[2,np.where(SurroundsClim[2,:] > TheMDI)[0]]))
			    
	                WorkingArrClim[mm,llt,lln] = np.mean(MyMeanArr)
			TheMaskClim[mm,llt,lln] = 3
    		        #print('CLIM filled with mean of surrounds')
			#pdb.set_trace() # Explore the missing point to test infilling
			#TESTING for 't' - works as expected

    # Increment the counter
                        CountInfillsClim = CountInfillsClim+1

    # SD Check if the middle box is missing, if there are at least 2 boxes present (middle one is missing of course!)
    # and if there is at least one box on the same latitude? OR a box on both latitude above and below
		    if ((len(np.where(MaskSurroundsSD == 1)[0]) >= 2) & (WorkingArrSD[mm,llt,lln] == TheMDI) & (len(np.where(SurroundsSD > TheMDI)[0]) >= 2) & 
		        ((len(np.where(SurroundsSD[1,:] > TheMDI)[0]) > 0) | 
			((len(np.where(SurroundsSD[0,:] > TheMDI)[0]) > 0) & (len(np.where(SurroundsSD[2,:] > TheMDI)[0]) > 0)))):

    # Infill the SD with the MAXIMUM of the two surrounding points
	                WorkingArrSD[mm,llt,lln] = np.max(SurroundsSD[np.where(SurroundsSD > TheMDI)])
			TheMaskSD[mm,llt,lln] = 2
    		        #print('SD filled with max of surrounds')
    		        #pdb.set_trace() # Explore the missing point to test infilling
			#TESTING for 't' - works as expected

    # Increment the counter
                        CountInfillsSD = CountInfillsSD+1
		    
    # Print out total number of infills
    print("Total number of InfillSpaces CLIM SD: ",CountInfillsClim, CountInfillsSD)		    
    # For 't' GRIDS3 15 Sep 2016 - added 3526 for CLIM and 3526 for SD extra months 	
    # MANY OF THESE WILL BE ON LAND - MASK LATER!!!    
    
    #pdb.set_trace()
    return WorkingArrClim, WorkingArrSD, TheMaskClim, TheMaskSD
# TEST NOTES:
# Noting RIDICULOUS INFILLING RATES:
# The infilling propogates across using the infilled values to further infill.
# This is not desireable as essentially a value then becomes COMPLETELY independent of a real value
# Added a catch where there must be at least 1 REAL value Mask = 1 present for an infill to occur
# HAPPY WITH THIS 16 Sep 2016

#************************************************************************
# CompleteLinearPentads
def CompleteLinearPentads(nPTs,OldVal,HFwd,HBck):
    ''' Function for InterpTime to loop through the pentads and apply a linear '''
    ''' interpolated value from the monthly one '''

    # Set up output arrays
    NewArr = np.empty(nPTs,dtype='float')

    # Set up the nsteps and mid-points and loop through pentads either side
    nsteps = nPTs * 2
    MidPoint = nPTs / 2.
     
    # If the MidPoint is ?.5 then its an uneven number so the middle pentad takes the same value as the month value
    if (MidPoint - np.floor(MidPoint) == 0.5):
  	NewArr[np.int(np.floor(MidPoint))] = OldVal    

    # Get the gaps between each step (12 steps for 6 PTs, 14 steps for 7 PTs)
    StepWidthBck = (OldVal - HBck) / (nsteps / 2.)
    StepWidthFwd = (HFwd - OldVal) / (nsteps / 2.)

    for mp in range(np.int(np.floor(MidPoint))):
  	NewArr[mp] = HBck + (StepWidthBck * ((mp*2)+1))
	NewArr[nPTs-1-mp] = HFwd - (StepWidthFwd * ((mp*2)+1))

    #print("In CompleteLinearPentads")	
    #pdb.set_trace()	

    return NewArr
# TEST NOTES
# HAPPY - works for 6 and 7 PT months: 15 SEP 2016
#************************************************************************
# InterpTime
def InterpTime(WorkingArrClim, WorkingArrSD, NewWorkingArrClim, NewWorkingArrSD, TheMDI, PentadList, TheVar):
    ''' Take a 3D WorkingArr '''
    ''' Work through the gridboxes lat/long '''
    ''' Interpolate smoothly across each 5by5 gridbox month to ''' 
    ''' divide into the appropriate number of pentads in time in equal steps '''
    ''' between the preceding and following 5by5 gridbox months, ensuring that '''
    ''' the mean of the pentads is equal to the monthly value. If the candidate '''
    ''' month is higher/lower than both preceding and following months then the '''
    ''' middle pentad will take peak/trough. Same for clim and stdev. '''
    ''' DOES NOT ASSUME SAME COVERAGE FOR CLIM AND SD '''
    ''' Does not allow SD to go below zero '''
    ''' Does not allow Climatological q, e, RH or DPD to go below zero or RH to go above 100 '''
    
    # Loop through each longitude box
    for lln in range(len(WorkingArrClim[0,0,:])):
    
    # Loop through each latitude box
        for llt in range(len(WorkingArrClim[0,:,0])):

            # Set up pointers for new time elements
            StPT = 0
            EdPT = -1
    
    # Loop through each month
            BeginYear = 0
            for mm in range(len(WorkingArrClim[:,0,0])):
	    
    # Set up the start and end pentad for this month using PentadList
                StPT = EdPT+1            	    
                EdPT = StPT + (PentadList[mm]-1)
		# Consider these as pointers, not range extremities so StPT:(EdPT+1) is necessary
		#print(lln,llt,mm,StPT,EdPT,WorkingArrClim[mm,llt,lln],WorkingArrSD[mm,llt,lln])
		
    # If this value is non-missing then begin
                if ((WorkingArrClim[mm,llt,lln] > TheMDI) | ((WorkingArrSD[mm,llt,lln] > TheMDI))): # check for floating point accuracy >TheMDI+1?
		    BeginYear = 1
		    
		    # Sort out preM and postM pointers
		    if (mm == 0):
		        preM = len(WorkingArrClim[:,0,0])-1
	            else:
		        preM = mm-1
			
		    if (mm == len(WorkingArrClim[:,0,0])-1):
		        postM = 0
		    else:
		        postM = mm+1
		    		    
		    # CLIM If no surrounding months are present then apply flat pentads - amplitude and sign of curve depend on latitude!
		    if (WorkingArrClim[preM,llt,lln] == TheMDI) & (WorkingArrClim[postM,llt,lln] == TheMDI):
                        NewWorkingArrClim[StPT:(EdPT+1),llt,lln] = WorkingArrClim[mm,llt,lln] # shouldn't be an issue with copying
			#print("CLIM Test mm = 1-10, + and - month missing ",preM,postM)
			#pdb.set_trace() # Check we're correctly replicating the value across all points - may need to replicate

                    else:    
                    # If the previous and subsequent months are present interpolate linearly between the two
		    # However, if this month is higher/lower than both surrounding months then make it peak/trough - this 'should' work
		        if (WorkingArrClim[preM,llt,lln] > TheMDI) & (WorkingArrClim[postM,llt,lln] > TheMDI):
		    
		            # Work out the number of steps and half widths between candidate month and next, forward and back
		            nSteps = PentadList[mm] * 2 # should be 12 or 14
			    HalfWayForwardClim = WorkingArrClim[mm,llt,lln] + ((WorkingArrClim[postM,llt,lln] - WorkingArrClim[mm,llt,lln]) / 2.) # could be +ve or -ve
			    HalfWayBackClim = WorkingArrClim[mm,llt,lln] - ((WorkingArrClim[mm,llt,lln] - WorkingArrClim[preM,llt,lln]) / 2.) # could be +ve or -ve
			    # IF TheVAR = q, e, RH or DPD DOUBLE CHECK FOR -ve Clim HalfWays - force to half way between month value and zero
			    # Shouldn't be a problem unless we only have one neighbour month but double check anyway
			    if (TheVar in ['q','e','rh','dpd']):
			        if ((HalfWayForwardClim < 0) | (HalfWayBackClim < 0)):
			            print("Got a negative!, + and - present")
				    #pdb.set_trace()
			        if (HalfWayForwardClim < 0.):
			            HalfWayForwardClim = (WorkingArrClim[mm,llt,lln] - 0.) / 2.
			        if (HalfWayBackClim < 0.):
			            HalfWayBackClim = (WorkingArrClim[mm,llt,lln] - 0.) / 2.
		                # EXTRA CHECK FOR RH > 100.
			        if (TheVar == 'rh'):
			            if (HalfWayForwardClim > 100.):
			                HalfWayForwardClim = 100. - ((100 - WorkingArrClim[mm,llt,lln]) / 2.)
			            if (HalfWayBackClim > 100.):
			                HalfWayBackClim = 100 - ((100 - WorkingArrClim[mm,llt,lln]) / 2.)								
			    #print('HalfWay Points Clim: ',mm, HalfWayBackClim, WorkingArrClim[mm,llt,lln], HalfWayForwardClim)
			    #print("CLIM Test mm = 1-10, + and - month present ",preM,postM)
			    #pdb.set_trace() # Check all fo the halfwidths are working
		            #TESTING for 't' GRIDS3 - half widths are good.

		    # If the previous month only is present then interpolate linearly from that month (shouldn't set off this if above has already been triggered!)
		        elif (WorkingArrClim[preM,llt,lln] > TheMDI):

		            # Work out the number of steps and half widths between candidate month and next, forward and back
			    nSteps = PentadList[mm] * 2 # should be 12 or 14
			    HalfWayBackClim = WorkingArrClim[mm,llt,lln] - ((WorkingArrClim[mm,llt,lln] - WorkingArrClim[preM,llt,lln]) / 2.) # could be +ve or -ve
			    # Make the forward half symmetrical as we do not have any other information to go on
			    HalfWayForwardClim = WorkingArrClim[mm,llt,lln] + ((WorkingArrClim[mm,llt,lln] - WorkingArrClim[preM,llt,lln]) / 2.) # could be +ve or -ve
			    # IF TheVAR = q, e, RH or DPD DOUBLE CHECK FOR -ve Clim HalfWays - force to half way between month value and zero
			    # Shouldn't be a problem unless we only have one neighbour month but double check anyway
			    if (TheVar in ['q','e','rh','dpd']):
			        if ((HalfWayForwardClim < 0) | (HalfWayBackClim < 0)):
			            print("Got a negative!, + and - present")
				    #pdb.set_trace()
			        if (HalfWayForwardClim < 0.):
			            HalfWayForwardClim = (WorkingArrClim[mm,llt,lln] - 0.) / 2.
			        if (HalfWayBackClim < 0.):
			            HalfWayBackClim = (WorkingArrClim[mm,llt,lln] - 0.) / 2.
		                # EXTRA CHECK FOR RH > 100.
			        if (TheVar == 'rh'):
			            if (HalfWayForwardClim > 100.):
			                HalfWayForwardClim = 100. - ((100 - WorkingArrClim[mm,llt,lln]) / 2.)
			            if (HalfWayBackClim > 100.):
			                HalfWayBackClim = 100 - ((100 - WorkingArrClim[mm,llt,lln]) / 2.)				
			    #print('HalfWay Points Clim: ',mm, HalfWayBackClim, WorkingArrClim[mm,llt,lln], HalfWayForwardClim)
			    #print("CLIM Test mm = 1-10, - month present ",preM,postM)
			    #pdb.set_trace() # Check all fo the halfwidths are working
			    #TESTING for 't' GRIDS3 - half widths are good.

		    # If the subsequent month only is present then interpolate linearly towards that month
		        elif (WorkingArrClim[postM,llt,lln] > TheMDI):

		            # Work out the number of steps and half widths between candidate month and next, forward and back
			    nSteps = PentadList[mm] * 2 # should be 12 or 14
			    HalfWayForwardClim = WorkingArrClim[mm,llt,lln] + ((WorkingArrClim[postM,llt,lln] - WorkingArrClim[mm,llt,lln]) / 2.) # could be +ve or -ve
			    # Make the back half symmetrical as we do not have any other information to go on
			    HalfWayBackClim = WorkingArrClim[mm,llt,lln] - ((WorkingArrClim[postM,llt,lln] - WorkingArrClim[mm,llt,lln]) / 2.) # could be +ve or -ve
			    # IF TheVAR = q, e, RH or DPD DOUBLE CHECK FOR -ve Clim HalfWays - force to half way between month value and zero
			    # Shouldn't be a problem unless we only have one neighbour month but double check anyway
			    if (TheVar in ['q','e','rh','dpd']):
			        if ((HalfWayForwardClim < 0) | (HalfWayBackClim < 0)):
			            print("Got a negative!, + and - present")
				    #pdb.set_trace()
			        if (HalfWayForwardClim < 0.):
			            HalfWayForwardClim = (WorkingArrClim[mm,llt,lln] - 0.) / 2.
			        if (HalfWayBackClim < 0.):
			            HalfWayBackClim = (WorkingArrClim[mm,llt,lln] - 0.) / 2.
		                # EXTRA CHECK FOR RH > 100.
			        if (TheVar == 'rh'):
			            if (HalfWayForwardClim > 100.):
			                HalfWayForwardClim = 100. - ((100 - WorkingArrClim[mm,llt,lln]) / 2.)
			            if (HalfWayBackClim > 100.):
			                HalfWayBackClim = 100 - ((100 - WorkingArrClim[mm,llt,lln]) / 2.)				
			    #print('HalfWay Points Clim: ',mm, HalfWayBackClim, WorkingArrClim[mm,llt,lln], HalfWayForwardClim)
			    #print("CLIM Test mm = 1-10, + month present ",preM,postM)
			    #pdb.set_trace() # Check all fo the halfwidths are working
		            #TESTING for 't' GRIDS3 - half widths are good.

                        # Now call the CompleteLinearPentads function to fill in
			NewWorkingArrClim[StPT:(EdPT+1),llt,lln] = CompleteLinearPentads(PentadList[mm],
								       WorkingArrClim[mm,llt,lln],
								       HalfWayForwardClim,HalfWayBackClim)

			#print("CLIM Test mm = 1-10,have interpolated ")
			#pdb.set_trace() # Check we're correctly replicating the value across all points - may need to replicate
		        # TESTING for 't' GRIDS3 - it works!

		    # SD If no surrounding months are present then apply flat pentads - amplitude and sign of curve depend on latitude!
		    if (WorkingArrSD[preM,llt,lln] == TheMDI) & (WorkingArrSD[postM,llt,lln] == TheMDI):
                        NewWorkingArrSD[StPT:(EdPT+1),llt,lln] = WorkingArrSD[mm,llt,lln] # shouldn't be an issue with copying
			#print("SD Test mm = 1-10, + and - month missing ",preM,postM)
			#pdb.set_trace() # Check we're correctly replicating the value across all points - may need to replicate

                    else:    
                    # If the previous and subsequent months are present interpolate linearly between the two
		    # However, if this month is higher/lower than both surrounding months then make it peak/trough - this 'should' work
		        if (WorkingArrSD[preM,llt,lln] > TheMDI) & (WorkingArrSD[postM,llt,lln] > TheMDI):
		    
		            # Work out the number of steps and half widths between candidate month and next, forward and back
		            nSteps = PentadList[mm] * 2 # should be 12 or 14
			    HalfWayForwardSD = WorkingArrSD[mm,llt,lln] + ((WorkingArrSD[postM,llt,lln] - WorkingArrSD[mm,llt,lln]) / 2.) # could be +ve or -ve
			    HalfWayBackSD = WorkingArrSD[mm,llt,lln] - ((WorkingArrSD[mm,llt,lln] - WorkingArrSD[preM,llt,lln]) / 2.) # could be +ve or -ve
			    if ((HalfWayForwardSD < 0) | (HalfWayBackSD < 0)):
			        print("Got a negative!, - and + present")
				#pdb.set_trace()
			    # DOUBLE CHECK FOR -ve SD HalfWays - make equal to month value to be safe - better to be a bit too large?
			    if (HalfWayForwardSD < 0.):
			        HalfWayForwardSD = WorkingArrSD[mm,llt,lln]
			    if (HalfWayBackSD < 0.):
			        HalfWayBackSD = WorkingArrSD[mm,llt,lln]
			    #print('HalfWay Points SD: ',mm, HalfWayBackSD, WorkingArrSD[mm,llt,lln], HalfWayForwardSD)
			    #print("SD Test mm = 1-10, + and - month present ",preM,postM)
			    #pdb.set_trace() # Check all fo the halfwidths are working
		            #TESTING for 't' GRIDS3 - half widths are good.

		    # If the previous month only is present then interpolate linearly from that month (shouldn't set off this if above has already been triggered!)
		        elif (WorkingArrSD[preM,llt,lln] > TheMDI):

		            # Work out the number of steps and half widths between candidate month and next, forward and back
			    nSteps = PentadList[mm] * 2 # should be 12 or 14
			    HalfWayBackSD = WorkingArrSD[mm,llt,lln] - ((WorkingArrSD[mm,llt,lln] - WorkingArrSD[preM,llt,lln]) / 2.) # could be +ve or -ve
			    # Make the back half symmetrical as we do not have any other information to go on
			    HalfWayForwardSD = WorkingArrSD[mm,llt,lln] + ((WorkingArrSD[mm,llt,lln] - WorkingArrSD[preM,llt,lln]) / 2.) # could be +ve or -ve
			    if ((HalfWayForwardSD < 0) | (HalfWayBackSD < 0)):
			        print("Got a negative!, - present")
				#pdb.set_trace()
			    # DOUBLE CHECK FOR -ve SD HalfWays - make equal to month value to be safe - better to be a bit too large?
			    if (HalfWayForwardSD < 0.):
			        HalfWayForwardSD = WorkingArrSD[mm,llt,lln]
			    if (HalfWayBackSD < 0.):
			        HalfWayBackSD = WorkingArrSD[mm,llt,lln]
			    #print('HalfWay Points SD: ',mm, HalfWayBackSD, WorkingArrSD[mm,llt,lln], HalfWayForwardSD)
			    #print("SD Test mm = 1-10, - month present ",preM,postM)
			    #pdb.set_trace() # Check all fo the halfwidths are working
			    #TESTING for 't' GRIDS3 - half widths are good.

		    # If the subsequent month only is present then interpolate linearly towards that month
		        elif (WorkingArrSD[postM,llt,lln] > TheMDI):

		            # Work out the number of steps and half widths between candidate month and next, forward and back
			    nSteps = PentadList[mm] * 2 # should be 12 or 14
			    HalfWayForwardSD = WorkingArrSD[mm,llt,lln] + ((WorkingArrSD[postM,llt,lln] - WorkingArrSD[mm,llt,lln]) / 2.) # could be +ve or -ve
			    # Make the back half symmetrical as we do not have any other information to go on
			    HalfWayBackSD = WorkingArrSD[mm,llt,lln] - ((WorkingArrSD[postM,llt,lln] - WorkingArrSD[mm,llt,lln]) / 2.) # could be +ve or -ve
			    if ((HalfWayForwardSD < 0) | (HalfWayBackSD < 0)):
			        print("Got a negative!, + present")
				#pdb.set_trace()
			    # DOUBLE CHECK FOR -ve SD HalfWays - make equal to month value to be safe - better to be a bit too large?
			    if (HalfWayForwardSD < 0.):
			        HalfWayForwardSD = WorkingArrSD[mm,llt,lln]
			    if (HalfWayBackSD < 0.):
			        HalfWayBackSD = WorkingArrSD[mm,llt,lln]
			    #print('HalfWay Points SD: ',mm, HalfWayBackSD, WorkingArrSD[mm,llt,lln], HalfWayForwardSD)
			    #print("SD Test mm = 1-10, + month present ",preM,postM)
			    #pdb.set_trace() # Check all fo the halfwidths are working
		            #TESTING for 't' GRIDS3 - half widths are good.

                        # Now call the CompleteLinearPentads function to fill in
			NewWorkingArrSD[StPT:(EdPT+1),llt,lln] = CompleteLinearPentads(PentadList[mm],
								     WorkingArrSD[mm,llt,lln],
								     HalfWayForwardSD,HalfWayBackSD)

			#print("SD Test mm = 1-10,have interpolated")
			#pdb.set_trace() # Check we're correctly replicating the value across all points - may need to replicate
		        # TESTING for 't' GRIDS3 - it works!
			    
		        # TEST THIS - all new PTs and the mean of the PTs within a month!!!

                #if ((BeginYear == 1) & (mm == 11)):
		#    pdb.set_trace() # Look at annual cycle
		    
    return NewWorkingArrClim, NewWorkingArrSD
# TEST NOTES:
# Added a catch for negative SD halfwidths and negative CLIM halfwidths for q, e, RH (and > 100), DPD (shouldn't happen)
# HAPPY 16 SEP 2016 - still need double check for negative q,e,RH

#************************************************************************
# InterpSpace
def InterpSpace(WorkingArrClim, WorkingArrSD, NewWorkingArrClim, NewWorkingArrSD, TheMDI, TheVar):
    ''' Take a 3D WorkingArr '''
    ''' Work through the gridboxes lat/long/pentad '''
    ''' Interpolate smoothly across each 5by5 gridbox pentad to '''
    ''' divide into the 5 1by1 gridboxes in space, ensuring that the mean of '''
    ''' all 1by1 pentad gridboxes is equal to the 5by5 pentad gridbox value. '''
    ''' This will be done as smoothly as possible. Ideally (although '''
    ''' arbitrarily) if the surrounding gridboxes are mostly higher/lower then '''
    ''' the trough/peak will tend towards the middle 1by1 pentad gridbox '''
    ''' within the 5by5. This will be quite complex though. Same for clim and '''
    ''' stdev. '''
    ''' DOES NOT ASSUME SAME COVERAGE FOR CLIM AND SD '''
    ''' Does not allow SD to go below zero - it can't because all inital values are greater than zero '''
    ''' Does not allow Climatological q, e, RH or DPD to go below zero or RH to go above 100 - it can't because all initial values are ok'''

    # Set up pointers for new latitude and longitude elements
    StLt = 0
    EdLt = -1
    StLn = 0
    EdLn = -1

    # Get Dimensions
    TotMons = len(WorkingArrClim[:,0,0]) # only 12 for a monthly climatology
    TotLons = len(WorkingArrClim[0,0,:])
    TotLats = len(WorkingArrClim[0,:,0])

    # Centre points for a 9 box (3 by 3) square
    fullpoints = (np.reshape(np.array((0,0, 0,1, 0,2,
    				       1,0, 1,1, 1,2,
    				       2,0, 2,1, 2,2)),(9,2))*(1./3.))+(1./6.) # 1./6./, 0.5, 5./6

    # Centre newpoints for the middle of a 225 (15 by 15) box square - 25 points
    newpoints = (np.reshape(np.array((0,0, 0,1, 0,2, 0,3, 0,4,
    				      1,0, 1,1, 1,2, 1,3, 1,4,
    				      2,0, 2,1, 2,2, 2,3, 2,4,
    				      3,0, 3,1, 3,2, 3,3, 3,4,
                                      4,0, 4,1, 4,2, 4,3, 4,4)),(25,2))*(2./30.))+(11./30.) # 11/30,13/30,15/30,17/30,19/30
    
    # Loop through each longitude box
    for lln in range(len(WorkingArrClim[0,0,:])):
    # Set up the the start and end longitude for this gridbox
        StLn = EdLn+1
	EdLn = StLn+4
	# Consider these as pointers, not range extremities so StPT:(EdPT+1) is necessary

	# Get the surrounds POINTS if lln western or eastern most aor not and
	# Also identify the mid-point - always 1 even if at longitudinal extremeties
	if (lln == 0):
	    LGpoints = [TotLons-1,0,1]  	       
	elif (lln == TotLons-1):
	    LGpoints = [lln-1,lln,0]
	else:
	    LGpoints = [lln-1,lln,lln+1]

    # Set up pointers for new latitude and longitude elements
        StLt = 0
        EdLt = -1

    # Loop through each latitude box
        for llt in range(len(WorkingArrClim[0,:,0])):
    
    # Set up the the start and end latitude for this gridbox
            StLt = EdLt+1
	    EdLt = StLt+4
	    # Consider these as pointers, not range extremities so StPT:(EdPT+1) is necessary

	    # Get the surrounds RANGE VALUES if llt northern most or southern most or not and
	    if (llt == 0):
	        LTspan = [0,llt+2]
	        BOXLTspan = [1,3]
	    elif (llt == TotLats-1):
	        LTspan = [llt-1,llt+1]
	        BOXLTspan = [0,2]
	    else:
	        LTspan = [llt-1,llt+2]
	        BOXLTspan = [0,3]
	    
    # Loop through each pentad (73)
            for pp in range(len(WorkingArrClim[:,0,0])):
	    
	        #print(lln,llt,pp,StLt,EdLt,StLn,EdLn)

    # Does this gridbox have a value?
                if ((WorkingArrClim[pp,llt,lln] > TheMDI) | (WorkingArrSD[pp,llt,lln] > TheMDI)):

                    # We need SurroundsBoxes to be 3by3s (different to InfillSpace)
		    SurroundsClim = np.empty((3,3))
		    SurroundsClim.fill(TheMDI)
		    SurroundsSD = np.copy(SurroundsClim)
		
                    # Work through all gridboxes first and last longs can wrap around. Lats cannot - -90 and +90 ob unlikely!
		    # CHECK THAT WE ARE MATCHING TO FLOATING POINT ACCURACY AS THIS MAY NOT PRECISELY MATCH! <= TheMDI+1 to catch?
		
		    # Pull out the Surrounds
		    # NOTE THAT MIXING SPANS AND POINTS CHANGES THE ARRAY DIMENSION ORDER
		    # So - arr[0,0:2,[2,3,4]] results in a 3 row 2 column array annoyingly
		    # I've tested np.transpose on this and that solves the problem
		    SurroundsClim[BOXLTspan[0]:BOXLTspan[1],:] = np.transpose(WorkingArrClim[pp,LTspan[0]:LTspan[1],LGpoints])    
		    SurroundsSD[BOXLTspan[0]:BOXLTspan[1],:] = np.transpose(WorkingArrSD[pp,LTspan[0]:LTspan[1],LGpoints])   
		    #print("Check the Surrounds")
		    #pdb.set_trace() 
		
    # CLIM Are there at least two surrounding values that we need to bother interpolating between?
                    # Check if there are at least 3 boxes INCLUDING the middle one!
		    GotCount = np.where(SurroundsClim > TheMDI)			
		    if (len(GotCount[0]) >= 3):
		        
                        # Ok now it all gets a bit silly and complicated
		        # For the interpolation to work we need either all corners filled or all crosses
		        # Test which has most data presence and infill with mid-box value as necessary
		        # Then apply interpolation
		        CornersClim = SurroundsClim[[0,0,1,2,2],[0,2,1,0,2]]
		        CrossesClim = SurroundsClim[[0,1,1,1,2],[1,0,1,2,1]]
		        GotCorners = np.where(CornersClim > TheMDI)[0]
		        GotCrosses = np.where(CrossesClim > TheMDI)[0]
			#print("CLIM Have a look at the corners and crosses an counts")
			#pdb.set_trace()
			
			# If there are no missing data on either the Corners or Crosses then we can apply interpolation without incurring any NaNs
			if ((len(GotCorners) == 5) | (len(GotCrosses) == 5)):
			    points = (np.reshape(np.transpose(GotCount),(len(GotCount[0]),2))*(1./3.))+(1./6.) # 1./6./, 0.5, 5./6
			    valuesClim = SurroundsClim[GotCount] # only the points not missing
			    			     
			    NewWorkingArrClim[pp,StLt:(EdLt+1),StLn:(EdLn+1)] = np.reshape(griddata(points,valuesClim,newpoints,method='linear'),(5,5))
			    # CHECK THIS IS FILLING CORRECTLY
			    #print("CLIM No missing in either corners or clim - have a look")
			    #pdb.set_trace()
			
			# If neither is 'full' then we need to fill the fullest (or crosses if equal) to avoid NaNs - fill with middle-box value
			# Preference of working with crosses because same-latitude infilling is better than higher/lower latitude infilling
		        else:
			
		            # If there are more corners work with the corners
		            if (len(GotCorners) > len(GotCrosses)):
		                # Find any missing values (there have to be some or the above loop would have been triggered
				Misses = np.where(CornersClim == TheMDI)
				# Fill the misses with the mid-gridbox value
				CornersClim[Misses] = WorkingArrClim[pp,llt,lln]
				# Repopulate the Surrounds with Corners
				SurroundsClim[[0,0,1,2,2],[0,2,1,0,2]] = CornersClim
				#print("CLIM Not enough corners/crosses so try with corners - look")
				#pdb.set_trace()
		    
		            # If there are more or equal crosses then work with the crosses
		            else:
		                # Find any missing values (there have to be some or the above loop would have been triggered
				Misses = np.where(CrossesClim == TheMDI)
				# Fill the misses with the mid-gridbox value
				CrossesClim[Misses] = WorkingArrClim[pp,llt,lln]
				# Repopulate the Surrounds with Corners
				SurroundsClim[[0,1,1,1,2],[1,0,1,2,1]] = CrossesClim
				#print("CLIM Not enough corners/crosses so try with crosses - look")
				#pdb.set_trace()

                            # Now establish the points and values and infill       
			    GotCount = np.where(SurroundsClim > TheMDI)	
			    points = (np.reshape(np.transpose(GotCount),(len(GotCount[0]),2))*(1./3.))+(1./6.) # 1./6./, 0.5, 5./6
			    valuesClim = SurroundsClim[GotCount] # only the points not missing
			    			     
			    NewWorkingArrClim[pp,StLt:(EdLt+1),StLn:(EdLn+1)] = np.reshape(griddata(points,valuesClim,newpoints,method='linear'),(5,5))
			    # CHECK THIS IS FILLING CORRECTLY
			    #print("CLIM Filled from Missing in either corners or clim - have a look")
			    #pdb.set_trace()
    
    # No, ok just make the it identical across the new set of boxes as we have no information to go on
                    else:
		     	NewWorkingArrClim[pp,StLt:(EdLt+1),StLn:(EdLn+1)] = WorkingArrClim[pp,llt,lln]	
			#print("CLIM No surrounding values so do a flat repeat across")
			#pdb.set_trace()	


    # SD Are there at least two surrounding values that we need to bother interpolating between?
                    # Check if there are at least 3 boxes INCLUDING the middle one!
		    GotCount = np.where(SurroundsSD > TheMDI)			
		    if (len(GotCount[0]) >= 3):
		        
                        # Ok now it all gets a bit silly and complicated
		        # For the interpolation to work we need either all corners filled or all crosses
		        # Test which has most data presence and infill with mid-box value as necessary
		        # Then apply interpolation
		        CornersSD = SurroundsSD[[0,0,1,2,2],[0,2,1,0,2]]
		        CrossesSD = SurroundsSD[[0,1,1,1,2],[1,0,1,2,1]]
		        GotCorners = np.where(CornersSD > TheMDI)[0]
		        GotCrosses = np.where(CrossesSD > TheMDI)[0]
			#print("SD Have a look at the corners and crosses an counts")
			#pdb.set_trace()
			
			# If there are no missing data on either the Corners or Crosses then we can apply interpolation without incurring any NaNs
			# Preference of working with crosses because same-latitude infilling is better than higher/lower latitude infilling
			if ((len(GotCorners) == 5) | (len(GotCrosses) == 5)):
			    points = (np.reshape(np.transpose(GotCount),(len(GotCount[0]),2))*(1./3.))+(1./6.) # 1./6./, 0.5, 5./6
			    valuesSD = SurroundsSD[GotCount] # only the points not missing
			    			     
			    NewWorkingArrSD[pp,StLt:(EdLt+1),StLn:(EdLn+1)] = np.reshape(griddata(points,valuesSD,newpoints,method='linear'),(5,5))
			    # CHECK THIS IS FILLING CORRECTLY
			    #print("SD No missing in either corners or clim - have a look")
			    #pdb.set_trace()
			
			# If neither is 'full' then we need to fill the fullest (or crosses if equal) to avoid NaNs - fill with middle-box value
		        else:
			
		            # If there are more corners work with the corners
		            if (len(GotCorners) > len(GotCrosses)):
		                # Find any missing values (there have to be some or the above loop would have been triggered
				Misses = np.where(CornersSD == TheMDI)
				# Fill the misses with the mid-gridbox value
				CornersSD[Misses] = WorkingArrSD[pp,llt,lln]
				# Repopulate the Surrounds with Corners
				SurroundsSD[[0,0,1,2,2],[0,2,1,0,2]] = CornersSD
				#print("SD Not enough corners/crosses so try with corners - look")
				#pdb.set_trace()
		    
		            # If there are more or equal crosses then work with the crosses
		            else:
		                # Find any missing values (there have to be some or the above loop would have been triggered
				Misses = np.where(CrossesSD == TheMDI)
				# Fill the misses with the mid-gridbox value
				CrossesSD[Misses] = WorkingArrSD[pp,llt,lln]
				# Repopulate the Surrounds with Corners
				SurroundsSD[[0,1,1,1,2],[1,0,1,2,1]] = CrossesSD
				#print("SD Not enough corners/crosses so try with crosses - look")
				#pdb.set_trace()

                            # Now establish the points and values and infill       
			    GotCount = np.where(SurroundsSD > TheMDI)	
			    points = (np.reshape(np.transpose(GotCount),(len(GotCount[0]),2))*(1./3.))+(1./6.) # 1./6./, 0.5, 5./6
			    valuesSD = SurroundsSD[GotCount]
			    			     
			    NewWorkingArrSD[pp,StLt:(EdLt+1),StLn:(EdLn+1)] = np.reshape(griddata(points,valuesSD,newpoints,method='linear'),(5,5))
			    # CHECK THIS IS FILLING CORRECTLY
			    #print("SD Filled from Missing in either corners or clim - have a look")
			    #pdb.set_trace()
    
    # No, ok just make the it identical across the new set of boxes as we have no information to go on
                    else:
		     	NewWorkingArrSD[pp,StLt:(EdLt+1),StLn:(EdLn+1)] = WorkingArrSD[pp,llt,lln]
			#print("SD No surrounding values so do a flat repeat across")
			#pdb.set_trace()	
			
    # Last check to make sure all values that should be +ve are			
    if (len(NewWorkingArrSD[np.where((NewWorkingArrSD > TheMDI) & (NewWorkingArrSD < 0.))]) > 0):
        print("Found some negative standard deviations: ", len(NewWorkingArrSD[np.where(NewWorkingArrSD > TheMDI & NewWorkingArrSD < 0.)]))


    if ((TheVar in ['q','e','rh','dpd']) & (len(NewWorkingArrClim[np.where((NewWorkingArrClim > TheMDI) & (NewWorkingArrClim < 0.))]) > 0)):
        print("Found some negative standard deviations: ", len(NewWorkingArrClim[np.where(NewWorkingArrClim > TheMDI & NewWorkingArrClim < 0.)]))

    return NewWorkingArrClim, NewWorkingArrSD
# TEST NOTES
#>import numpy as np
#>from scipy.interpolate import griddata
#> x=1./6.                              
#> y=0.5
#> z=5./6.
#> points = np.reshape(np.array((x,x,y,x,z,x,x,y,y,y,z,y,x,z,y,z,z,z)),(9,2))
#> values = np.arange(9,dtype = 'float')
#> a=11./30.
#> b=13./30.
#> c=15./30.
#> d=17./30.
#> e=19./30.
#> newpoints = np.reshape(np.array((a,a,b,a,c,a,d,a,e,a,a,b,b,b,c,b,d,b,e,b,a,c,b,c,c,c,d,c,e,c,a,d,b,d,c,d,d,d,e,d,a,e,b,e,c,e,d,e,e,e)),(25,2))
#> moo = griddata(points,values,newpoints,method='linear')
#> np.reshape(values,(3,3))
#array([[ 0.,  1.,  2.],
#       [ 3.,  4.,  5.],
#       [ 6.,  7.,  8.]])
#> np.reshape(moo,(5,5))
#array([[ 2.4,  2.6,  2.8,  3. ,  3.2],
#       [ 3. ,  3.2,  3.4,  3.6,  3.8],
#       [ 3.6,  3.8,  4. ,  4.2,  4.4],
#       [ 4.2,  4.4,  4.6,  4.8,  5. ],
#       [ 4.8,  5. ,  5.2,  5.4,  5.6]])
#> np.mean(moo)
#3.9999999999999996
#> mooc = griddata(points,values,newpoints,method='cubic')
#array([[ 2.39999976,  2.5999998 ,  2.79999987,  2.99999992,  3.19999993],
#       [ 2.99999984,  3.19999988,  3.39999993,  3.59999997,  3.79999998],
#       [ 3.59999993,  3.79999996,  4.        ,  4.20000004,  4.40000005],
#       [ 4.19999998,  4.40000001,  4.60000005,  4.80000008,  5.00000009],
#       [ 4.79999999,  5.00000003,  5.20000007,  5.40000009,  5.6000001 ]])
#>np.mean(mooc)
#3.9999999730100173
# This looks like its doing what I want. How will it deal with missing data though?  Just provide the points/values of data present?
# 5 points: 1,3,4,5,7 IDENTICAL
#> subpoints = np.reshape(np.array((y,x,x,y,y,y,z,y,y,z)),(5,2))
#> subvalues = np.array((1.,3.,4.,5.,7.))
#> moocsub = griddata(subpoints,subvalues,newpoints,method='cubic')
#> np.reshape(moocsub,(5,5))
#array([[ 2.39999989,  2.59999993,  2.79999997,  3.        ,  3.20000001],
#       [ 2.99999993,  3.19999995,  3.39999998,  3.6       ,  3.80000001],
#       [ 3.59999997,  3.79999998,  4.        ,  4.20000001,  4.40000002],
#       [ 4.19999999,  4.4       ,  4.60000001,  4.80000002,  5.00000003],
#       [ 4.8       ,  5.        ,  5.20000002,  5.40000002,  5.60000002]])
#> moosub = griddata(subpoints,subvalues,newpoints,method='linear')
#> np.reshape(moosub,(5,5))
#array([[ 2.4,  2.6,  2.8,  3. ,  3.2],
#       [ 3. ,  3.2,  3.4,  3.6,  3.8],
#       [ 3.6,  3.8,  4. ,  4.2,  4.4],
#       [ 4.2,  4.4,  4.6,  4.8,  5. ],
#       [ 4.8,  5. ,  5.2,  5.4,  5.6]])
#  5 points: 0,2,4,6,8 NEAR IDENTICAL
#> subvalues = np.array((0.,2.,4.,6.,8.))
#> subpoints = np.reshape(np.array((x,x,z,x,y,y,x,z,z,z)),(5,2))
#> moocsub = griddata(subpoints,subvalues,newpoints,method='cubic')
#> moosub = griddata(subpoints,subvalues,newpoints,method='linear')
#> np.reshape(moocsub,(5,5))
#array([[ 2.39999996,  2.59999994,  2.79999994,  2.99999995,  3.19999996],
#       [ 2.99999999,  3.19999998,  3.39999997,  3.59999998,  3.79999998],
#       [ 3.60000001,  3.8       ,  4.        ,  4.2       ,  4.4       ],
#       [ 4.20000002,  4.40000002,  4.60000002,  4.80000002,  5.00000001],
#       [ 4.80000003,  5.00000003,  5.20000003,  5.40000003,  5.60000002]])
#> np.reshape(moosub,(5,5))
#array([[ 2.4,  2.6,  2.8,  3. ,  3.2],
#       [ 3. ,  3.2,  3.4,  3.6,  3.8],
#       [ 3.6,  3.8,  4. ,  4.2,  4.4],
#       [ 4.2,  4.4,  4.6,  4.8,  5. ],
#       [ 4.8,  5. ,  5.2,  5.4,  5.6]])
# 5 points: No right side points: 0,1,3,4,5 NANS=13
# 4 points: 2.,3.,4.,8. NANS=2
# SO - either we need a minimum of 5 points with at least one in each corner or cross or we accept some NANS
# Test which has more - corners or crosses
# copy middle box value to missing corners or crosses
# then apply linear interpolation - seems almost identical to cubic on this scale
#> 
# HAPPY 16 Sep 2016
#************************************************************************
# WriteNCCF
def WriteNCCF(FileName,TimeRes,Latitudes,Longitudes,ClimPoints,DataObject,DimObject,AttrObject,GlobAttrObject):
    ''' Sort out the date/times to write out and time bounds '''
    ''' Sort out clim bounds '''
    ''' Sort out lat and long bounds '''
    ''' Convert variables using the obtained scale_factor and add_offset: stored_var=int((var-offset)/scale) '''
    ''' Write to file, set up given dimensions, looping through all potential variables and their attributes, and then the provided dictionary of global attributes '''
    
    # Sort out date/times to write out
    # set up arrays for time period mid points and bounds
    TimPoints=np.empty(TimeRes)
    TimBounds=np.empty((TimeRes,2))   
    ClimBounds = np.empty((TimeRes,2),dtype='|S10')
    
    # make a date object for each time point and subtract start date
    StYear = ClimPoints[0]
    EdYear = StYear
    StartDate = datetime(StYear,1,1,0,0,0)	# January
    MonthDays = np.array([31,28,31,30,31,30,31,31,30,31,30,31])
    PentadDays = np.repeat(5,73)
    
    StMonth = 0
    EdMonth = 0
    ActEdMonth = 0
    StDay = 0
    EdDay = 1
    ActEdDay = 0
    ThisMonth = 0 # Only used for pentad resolution
	    
    # Loop through each increment to get midpoint and boundaries as a datetime object based on first year of climatology	
    for tt in range(TimeRes):

        # Set up months and days for monthly resolution
        if (TimeRes == 12):
	    
	    StMonth = tt+1
            EdMonth = StMonth + 1
	    ActEdMonth = StMonth+0
	    	    
	    StDay = 1 # Always day 1
	    EdDay = 1 # Always first day of the following month
            ActEdDay = MonthDays[tt]
	    
        # Set up times and days for pentad resolution
	elif (TimeRes == 73):
 
 	    StDay = EdDay+0
	    EdDay = StDay + 5 # Always first day of the following pentad
	    ActEdDay = StDay + 4
	    
	    # Catch EdDays that go over the number of days in the month
            if (EdDay > MonthDays[ThisMonth]):
	        EdDay = EdDay - MonthDays[ThisMonth]
		 
	    # Catch EdDays that go over the number of days in the month
            if (ActEdDay > MonthDays[ThisMonth]):
	        ActEdDay = ActEdDay - MonthDays[ThisMonth]

	    StMonth = ThisMonth+1
	        
	    if (EdDay > StDay):
	        EdMonth = StMonth+0
	    else:
	        EdMonth = StMonth+1
		ThisMonth = ThisMonth + 1

	    if (ActEdDay > StDay):
	        ActEdMonth = StMonth+0
	    else:
	        ActEdMonth = StMonth+1
	    
	# Catch for December!
	if (EdMonth == 13):
	    EdMonth = 1
	    EdYear = StYear+1

        # This shouldn't actually be a problem
	if (ActEdMonth == 13):
	    ActEdMonth = 1
	    
	#print(TimeRes, tt, StDay, EdDay, ActEdDay, StMonth, EdMonth, ActEdMonth)
		    
	TimPoints[tt]=(datetime(EdYear,EdMonth,EdDay,0,0,0)-datetime(StYear,StMonth,StDay,0,0,0)).days/2. + \
	              (datetime(StYear,StMonth,StDay,0,0,0)-StartDate).days
	TimBounds[tt,0]=(datetime(StYear,StMonth,StDay,0,0,0)-StartDate).days+1
	TimBounds[tt,1]=(datetime(EdYear,EdMonth,EdDay,0,0,0)-StartDate).days

	ClimBounds[tt,0] = str(ClimPoints[0])+'-'+str(StMonth)+'-'+str(StDay)
	ClimBounds[tt,1] = str(ClimPoints[1])+'-'+str(ActEdMonth)+'-'+str(ActEdDay)

        #print(TimPoints[tt],TimBounds[tt,0],TimBounds[tt,1],ClimBounds[tt,0],ClimBounds[tt,1])
	
    nTims = TimeRes	
		
    # Sort out LatBounds and LonBounds
    LatBounds = np.empty((len(Latitudes),2),dtype='float')
    LonBounds = np.empty((len(Longitudes),2),dtype='float')
	
    LatBounds[:,0] = Latitudes - ((Latitudes[1]-Latitudes[0])/2.)
    LatBounds[:,1] = Latitudes + ((Latitudes[1]-Latitudes[0])/2.)

    LonBounds[:,0] = Longitudes - ((Longitudes[1]-Longitudes[0])/2.)
    LonBounds[:,1] = Longitudes + ((Longitudes[1]-Longitudes[0])/2.)	
	
    #pdb.set_trace()
    
    # Create a new netCDF file - have tried zlib=True,least_significant_digit=3 (and 1) - no difference
    ncfw=Dataset(FileName,'w',format='NETCDF4_CLASSIC') # need to try NETCDF4 and also play with compression but test this first
    
    # Write out the global attributes
    if ('description' in GlobAttrObject):
        ncfw.description = GlobAttrObject['description']
	#print(GlobAttrObject['description'])
	
    if ('File_created' in GlobAttrObject):
        ncfw.File_created = GlobAttrObject['File_created']

    if ('Title' in GlobAttrObject):
        ncfw.Title = GlobAttrObject['Title']

    if ('Institution' in GlobAttrObject):
        ncfw.Institution = GlobAttrObject['Institution']

    if ('History' in GlobAttrObject):
        ncfw.History = GlobAttrObject['History']

    if ('Licence' in GlobAttrObject):
        ncfw.Licence = GlobAttrObject['Licence']

    if ('Project' in GlobAttrObject):
        ncfw.Project = GlobAttrObject['Project']

    if ('Processing_level' in GlobAttrObject):
        ncfw.Processing_level = GlobAttrObject['Processing_level']

    if ('Acknowledgement' in GlobAttrObject):
        ncfw.Acknowledgement = GlobAttrObject['Acknowledgement']

    if ('Source' in GlobAttrObject):
        ncfw.Source = GlobAttrObject['Source']

    if ('Comment' in GlobAttrObject):
        ncfw.Comment = GlobAttrObject['Comment']

    if ('References' in GlobAttrObject):
        ncfw.References = GlobAttrObject['References']

    if ('Creator_name' in GlobAttrObject):
        ncfw.Creator_name = GlobAttrObject['Creator_name']

    if ('Creator_email' in GlobAttrObject):
        ncfw.Creator_email = GlobAttrObject['Creator_email']

    if ('Version' in GlobAttrObject):
        ncfw.Version = GlobAttrObject['Version']

    if ('doi' in GlobAttrObject):
        ncfw.doi = GlobAttrObject['doi']

    if ('Conventions' in GlobAttrObject):
        ncfw.Conventions = GlobAttrObject['Conventions']

    if ('netcdf_type' in GlobAttrObject):
        ncfw.netcdf_type = GlobAttrObject['netcdf_type']
	
    # Loop through and set up the dimension names and quantities
    for vv in range(len(DimObject[0])):
        ncfw.createDimension(DimObject[0][vv],DimObject[1][vv])
	
    # Go through each dimension and set up the variable and attributes for that dimension if needed
    for vv in range(len(DimObject)-2): # ignore first two elements of the list but count all other dictionaries
        print(DimObject[vv+2]['var_name'])
	
	# NOt 100% sure this works in a loop with overwriting
	# initiate variable with name, type and dimensions
	MyVar = ncfw.createVariable(DimObject[vv+2]['var_name'],DimObject[vv+2]['var_type'],DimObject[vv+2]['var_dims'])
        
	# Apply any other attributes
        if ('standard_name' in DimObject[vv+2]):
	    MyVar.standard_name = DimObject[vv+2]['standard_name']
	    
        if ('long_name' in DimObject[vv+2]):
	    MyVar.long_name = DimObject[vv+2]['long_name']
	    
        if ('units' in DimObject[vv+2]):
	    MyVar.units = DimObject[vv+2]['units']
		   	 
        if ('axis' in DimObject[vv+2]):
	    MyVar.axis = DimObject[vv+2]['axis']

        if ('calendar' in DimObject[vv+2]):
	    MyVar.calendar = DimObject[vv+2]['calendar']

        if ('start_year' in DimObject[vv+2]):
	    MyVar.start_year = DimObject[vv+2]['start_year']

        if ('end_year' in DimObject[vv+2]):
	    MyVar.end_year = DimObject[vv+2]['end_year']

        if ('start_month' in DimObject[vv+2]):
	    MyVar.start_month = DimObject[vv+2]['start_month']

        if ('end_month' in DimObject[vv+2]):
	    MyVar.end_month = DimObject[vv+2]['end_month']

        if ('bounds' in DimObject[vv+2]):
	    MyVar.bounds = DimObject[vv+2]['bounds']

        if ('climatology' in DimObject[vv+2]):
	    MyVar.climatology = DimObject[vv+2]['climatology']

        if ('point_spacing' in DimObject[vv+2]):
	    MyVar.point_spacing = DimObject[vv+2]['point_spacing']
	
	# Provide the data to the variable
        if (DimObject[vv+2]['var_name'] == 'time'):
	    MyVar[:] = TimPoints

        if (DimObject[vv+2]['var_name'] == 'bounds_time'):
	    MyVar[:,:] = TimBounds

        if (DimObject[vv+2]['var_name'] == 'month'):
	    for mm in range(12):
	        MyVar[mm,:] = stringtoarr(MonthName[mm],10)

        if (DimObject[vv+2]['var_name'] == 'climbounds'):
	    for mm in range(12):
	        MyVar[mm,0,:] = stringtoarr(ClimBounds[mm,0],10)
	        MyVar[mm,1,:] = stringtoarr(ClimBounds[mm,1],10)

        if (DimObject[vv+2]['var_name'] == 'latitude'):
	    MyVar[:] = Latitudes

        if (DimObject[vv+2]['var_name'] == 'bounds_lat'):
	    MyVar[:,:] = LatBounds

        if (DimObject[vv+2]['var_name'] == 'longitude'):
	    MyVar[:] = Longitudes

        if (DimObject[vv+2]['var_name'] == 'bounds_lon'):
	    MyVar[:,:] = LonBounds

    # Go through each variable and set up the variable attributes
    for vv in range(len(AttrObject)): # ignore first two elements of the list but count all other dictionaries

        print(AttrObject[vv]['var_name'])

        # NOt 100% sure this works in a loop with overwriting
	# initiate variable with name, type and dimensions
	MyVar = ncfw.createVariable(AttrObject[vv]['var_name'],AttrObject[vv]['var_type'],AttrObject[vv]['var_dims'],fill_value = AttrObject[vv]['_FillValue'])
        
	# Apply any other attributes
        if ('standard_name' in AttrObject[vv]):
	    MyVar.standard_name = AttrObject[vv]['standard_name']
	    
        if ('long_name' in AttrObject[vv]):
	    MyVar.long_name = AttrObject[vv]['long_name']
	    
        if ('cell_methods' in AttrObject[vv]):
	    MyVar.cell_methods = AttrObject[vv]['cell_methods']
	    
        if ('comment' in AttrObject[vv]):
	    MyVar.comment = AttrObject[vv]['comment']
	    
        if ('units' in AttrObject[vv]):
	    MyVar.units = AttrObject[vv]['units']
		   	 
        if ('axis' in AttrObject[vv]):
	    MyVar.axis = AttrObject[vv]['axis']

        if ('add_offset' in AttrObject[vv]):
	    MyVar.add_offset = AttrObject[vv]['add_offset']

        if ('scale_factor' in AttrObject[vv]):
	    MyVar.scale_factor = AttrObject[vv]['scale_factor']

        if ('valid_min' in AttrObject[vv]):
	    MyVar.valid_min = AttrObject[vv]['valid_min']

        if ('valid_max' in AttrObject[vv]):
	    MyVar.valid_max = AttrObject[vv]['valid_max']

        if ('missing_value' in AttrObject[vv]):
	    MyVar.missing_value = AttrObject[vv]['missing_value']

#        if ('_FillValue' in AttrObject[vv]):
#	    MyVar._FillValue = AttrObject[vv]['_FillValue']

        if ('reference_period' in AttrObject[vv]):
	    MyVar.reference_period = AttrObject[vv]['reference_period']

        if ('ancillary_variables' in AttrObject[vv]):
	    MyVar.ancillary_variables = AttrObject[vv]['ancillary_variables']
	
	# Provide the data to the variable - depending on howmany dimensions there are
        if (len(AttrObject[vv]['var_dims']) == 1):
	    MyVar[:] = DataObject[vv]
	    
        if (len(AttrObject[vv]['var_dims']) == 2):
	    MyVar[:,:] = DataObject[vv]
	    
        if (len(AttrObject[vv]['var_dims']) == 3):
	    MyVar[:,:,:] = DataObject[vv]
	    
	    
    ncfw.close()
   
    return # WriteNCCF

# TEST NOTES
# HAPPY 19 Sep 2016
#************************************************************************
# Main
#************************************************************************

def main(argv):
    # INPUT PARAMETERS AS STRINGS!!!! WITH ''
    typee = 'ERAclimNBC'
    varee = 't' # t, tw, td, q, rh, e, dpd

    try:
        opts, args = getopt.getopt(argv, "hi:",
	                           ["typee=","varee="])
    except getopt.GetoptError:
        print 'Usage (as strings) InterpClimtoPentad1by1.py --typee <ERAclimNBC> --varee <t>'
	sys.exit(2)

    for opt, arg in opts:
        if opt == "--typee":
            try:
                typee = arg
            except:
                sys.exit("Failed: typee not a string")
        if opt == "--varee":
            try:
                varee = arg
            except:
                sys.exit("Failed: typee not a string")

    print(typee, varee)
#    pdb.set_trace()
    			
    mdi=-1e30
    
    # Editables:
    version = 'beta1'
    StClim = 1981
    EdClim = 2010
    nMonths = 12
    nPentads = 73
    nLons1 = 360
    nLats1 = 180
    nLons5 = 72
    nLats5 = 36

    # How many pentads (or other) in each month (or other)?
    PentadList = [6,6,6,6,6,6,6,7,6,6,6,6]
        
    # Find the variable name VarName[varee]
    VarName = dict([['t','marine_air_temperature'],
     	            ['td','dew_point_temperature'],
     	            ['tw','wet_bulb_temperature'],
     	            ['q','specific_humidity'],
     	            ['rh','relative_humidity'],
     	            ['e','vapor_pressure'],
     	            ['dpd','dew_point_depression']])
					   
    # Create a Dictionary of Dictionaries to store variable info
    VarDict = dict([['t',dict([['short_name','t2m'],
                               ['longer_name','air temperature'],
                               ['units','deg C']])],
                    ['td',dict([['short_name','td2m'],
		                ['longer_name','dew point temperature'],
				['units','deg C']])],
		    ['tw',dict([['short_name','tw2m'],
		                ['longer_name','wet bulb temperature'],
				['units','deg C']])],
		    ['q',dict([['short_name','q2m'],
		                ['longer_name','specific humidity'],
				['units','g/kg']])],
		    ['rh',dict([['short_name','rh2m'],
		                ['longer_name','relative humidity'],
				['units','%rh']])],
		    ['e',dict([['short_name','e2m'],
		                ['longer_name','vapour pressure'],
				['units','hPa']])],
		    ['dpd',dict([['short_name','dpd2m'],
		                ['longer_name','dew point depression'],
				['units','deg C']])]])
    
    					   
    INDIR = '/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/'
    InOBSclim = 'GRIDS3/RES5BY5/ERAclimNBC_5x5_monthly_climatology_from_daily_both_relax.nc'
    InOBSsd = 'GRIDS3/RES5BY5/ERAclimNBC_5x5_monthly_stdev_from_daily_both_relax.nc'
#    InOBSclim = 'GRIDS_noQC/ERAclimNBC_5x5_monthly_climatology_from_daily_both_relax.nc'
#    InOBSsd = 'GRIDS_noQC/ERAclimNBC_5x5_monthly_stdev_from_daily_both_relax.nc'
    
    OUTDIR = '/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/'
    OutOBS1 = 'GRIDS3/RES5BY5/'+VarDict[varee]['short_name']+'_ERAclimNBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    OutOBS5 = 'GRIDS3/RES5BY5/'+VarDict[varee]['short_name']+'_ERAclimNBC_5x5_monthly_climatology_stdev_from_daily_both_relax_INFILLED.nc'
#    OutOBS1 = 'GRIDS_noQC/'+VarDict[varee]['short_name']+'_ERAclimNBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
#    OutOBS5 = 'GRIDS_noQC/'+VarDict[varee]['short_name']+'_ERAclimNBC_5x5_monthly_climatology_stdev_from_daily_both_relax_INFILLED.nc'

#    OUTDIR = '/data/local/hadkw/HADCRUH2/MARINE/otherdata/'
#    OutOBS1 = VarDict[varee]['short_name']+'_ERAclimNBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
#    OutOBS5 = VarDict[varee]['short_name']+'_ERAclimNBC_5x5_monthly_climatology_stdev_from_daily_both_relax_INFILLED.nc'
    
    # create arrays for lats/lons
    lats1 = np.arange(180,0,-1)-90.5
    lons1 = np.arange(0,360,1)-179.5
    longrid1,latgrid1 = np.meshgrid(lons1,lats1) # latgrid should have latitudes repeated along each row of longitude
    lats5 = np.arange(180,0,-5)-87.5
    lons5 = np.arange(0,360,5)-177.5
    longrid5,latgrid5 = np.meshgrid(lons5,lats5) # latgrid should have latitudes repeated along each row of longitude

    # Set up all of the overly detailed stuff to write out for the NetCDF file
   # DimObject list
    DimObjectList=[['time','characters','latitude','longitude','bound_pairs'],
	           [nMonths,10,nLats5,nLons5,2],		# Change the first element of this to 73 for final write out.
    	           dict([('var_type','f4'),
    		         ('var_name','time'),
    		         ('var_dims',('time',)),
    		         ('standard_name','time'),
    		         ('long_name','time'),
    		         ('units','days since '+str(StClim)+'-1-1 00:00:00'),
    		         ('axis','T'),
    		         ('bounds','bounds_time')]),
    	           dict([('var_type','i4'),
    		         ('var_name','bounds_time'),
    		         ('var_dims',('time','bound_pairs',)), 
    		         ('standard_name','time'),
    		         ('long_name','time period boundaries')]),
    	           dict([('var_type','S1'),
    		         ('var_name','climbounds'),
    		         ('var_dims',('time','bound_pairs','characters')), 
    		         ('long_name','climatology period boundaries')]),
    	           dict([('var_type','f4'),
    		         ('var_name','latitude'),
    		         ('var_dims',('latitude',)), 
    		         ('standard_name','latitude'),
    		         ('long_name','gridbox centre latitude'),
    		         ('units','degrees_north'),
    		         ('point_spacing','even'),
    		         ('bounds','bounds_lat')]),
    	           dict([('var_type','f4'),
    		         ('var_name','bounds_lat'),
    		         ('var_dims',('latitude','bound_pairs',)), 
    		         ('standard_name','latitude'),
    		         ('long_name','latitude gridbox boundaries')]),
    	           dict([('var_type','f4'),
    		         ('var_name','longitude'),
    		         ('var_dims',('longitude',)), 
    		         ('standard_name','longitude'),
    		         ('long_name','gridbox centre longitude'),
    		         ('units','degrees_east'),
    		         ('point_spacing','even'),
    		         ('bounds','bounds_lon')]),
    	           dict([('var_type','f4'),
    		         ('var_name','bounds_lon'),
    		         ('var_dims',('longitude','bound_pairs',)), 
    		         ('standard_name','longitude'),
    		         ('long_name','longitude gridbox boundaries')])]

    # Set up Global Attributes for  List of Lists
    Description = 'HadISDH-marine INFILLED climatological (1981-2010) MONTHLY mean and standard deviation \
surface '+VarDict[varee]['longer_name']+' climate monitoring product from 1973 onwards on 5deg by 5deg gridded resolution.'
    Title = 'HadISDH-marine INFILLED climatological (1981-2010) MONTHLY mean and standard deviation \
surface '+VarDict[varee]['longer_name']+' climate monitoring product.' 		
    Institution = 'Met Office Hadley Centre (UK), National Oceanography Centre (NOC)'
    History = 'See Willett et al., (in prep) REFERENCE for more information. \
See www.metoffice.gov.uk/hadobs/hadisdh/ for more information and related data and figures. \
Follow @metofficeHadOBS to keep up to date with Met Office Hadley Centre HadOBS dataset developements. \
See hadisdh.blogspot.co.uk for HadISDH updates, bug fixes and explorations.'
    # Non-commercial license
    Licence = 'HadISDH is distributed under the Non-Commercial Government Licence: \
http://www.nationalarchives.gov.uk/doc/non-commercial-government-licence/non-commercial-government-licence.htm. \
The data are freely available for any non-comercial use with attribution to the data providers. Please cite \
Willett et al.,(in prep) and Woodruff et al., (2011) with a link to the REFERENCES provided in the REFERENCE attribute.'
    # Open Government License
    #Licence = 'HadISDH is distributed under the Open Government Licence: \
    #http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/. \
    #The data are freely available for use with attribution to the data providers. Please cite \
    #Willett et al.,(2014) with a link to the REFERENCE provided in the REFERENCE attribute.'
    Project = 'HadOBS: Met Office Hadley Centre Climate Monitoring Data-product www.metoffice.gov.uk/hadobs'
    Processing_level = 'Hourly marine ship/buoy/platform data selected for length and continuity, quality controlled, \
buddy checked, averaged to monthly means, and then averaged over 5deg gridboxes and then over the \
1981-2010 climatology period. Climatological standard deviations are of all climatology \
contributing gridbox months. Some missing data are infilled over time and space where there \
are near-by gridbox month climatologies.' 
    Acknowledgement = 'Kate Willett, Robert Dunn, John Kennedy and David Parker were supported by the Joint BEIS/Defra \
Met Office Hadley Centre Climate Programme (GA01101). David Berry - NERC.'
    Source = 'ICOADS 2.5.0 and 2.5.1 and near real time updates for 2015.'
    Comment = ''
    References = 'Willett, K. M., R. J. H. Dunn, J. Kennedy, D. I. Berry and D. E. Parker, in prep & \
Woodruff, S.D., S.J. Worley, S.J. Lubker, Z. Ji, J.E. Freeman, D.I. Berry, P. Brohan, \
E.C. Kent, R.W. Reynolds, S.R. Smith, and C. Wilkinson, 2011: ICOADS Release 2.5: \
Extensions and enhancements to the surface marine meteorological archive. Int. J. \
Climatol. (CLIMAR-III Special Issue), 31, 951-967 (doi:10.1002/joc.2103).'
    Creator_name = 'Kate Willett'
    Creator_email = 'kate.willett@metoffice.gov.uk'
    Conventions = 'CF-1.6'
    netCDF_type = 'NETCDF4_CLASSIC'

    # AttrObject list
    AttrObjectList=[dict([('var_type','f4'),
			  ('var_name',VarDict[varee]['short_name']+'_clims'),
			  ('var_dims',('time','latitude','longitude',)), 
			  ('long_name','near surface (~2m) '+VarDict[varee]['longer_name']+' climatology'),
			  ('cell_methods','time: mean (interval: 1 period comment: over 30 year climatology period) area: mean where ocean (obs within gridbox)'),
			  ('comment','gridbox mean of period mean from obs'),
			  ('units',VarDict[varee]['units']),
			  ('missing_value',mdi),
			  ('_FillValue',mdi),
			  ('reference_period',str(StClim)+', '+str(EdClim))]),
	            dict([('var_type','f4'),
			  ('var_name',VarDict[varee]['short_name']+'_stdevs'),
			  ('var_dims',('time','latitude','longitude',)), 
			  ('long_name','near surface (~2m) '+VarDict[varee]['longer_name']+' climatological standard deviation'),
			  ('cell_methods','time: stdev (interval: 1 period comment: over 30 year climatology period) area: mean where ocean (obs within gridbox)'),
			  ('comment','period stdev from obs of gridbox period mean CHECK'),
			  ('units',VarDict[varee]['units']),
			  ('missing_value',mdi),
			  ('_FillValue',mdi)]),
	            dict([('var_type','i4'),
			  ('var_name','source_mask_clims'),
			  ('var_dims',('time','latitude','longitude',)), 
			  ('long_name','source of gridbox value for climatologies'),
			  ('comment','1 = real value, 2 = interpolated from time periods before/after, 3 = interpolated from surrounding gridboxes'),
			  ('units','1'),
			  ('missing_value',0),
			  ('_FillValue',0)]),  
	            dict([('var_type','i4'),
			  ('var_name','source_mask_stdevs'),
			  ('var_dims',('time','latitude','longitude',)), 
			  ('long_name','source of gridbox value for stdevs'),
			  ('comment','1 = real value, 2 = interpolated from time periods before/after, 3 = interpolated from surrounding gridboxes'),
			  ('units','1'),
			  ('missing_value',0),
			  ('_FillValue',0)])]  

    # Set up Global Attribute List of Lists
    GlobAttrObjectList=dict([['File_created',datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')], # Is there a call for time stamping?
			     ['Description',Description],
			     ['Title',Title], 
			     ['Institution',Institution],
			     ['History',History], 
			     ['Licence',Licence],
			     ['Project', Project],
			     ['Processing_level',Processing_level],
			     ['Acknowledgement',Acknowledgement],
			     ['Source',Source],
			     ['Comment',''],
			     ['References',References],
			     ['Creator_name',Creator_name],
			     ['Creator_email',Creator_email],
			     ['Version',version],
			     ['doi',''], # This needs to be filled in
			     ['Conventions',Conventions],
			     ['netCDF_type',netCDF_type]]) 
						   
    # read in OBS ncs [time, lat, lon]
    # THESE FILES HAVE THEIR LATS FROM 92.5!!! to -82.5!!!
    # THIS NEEDS SORTING IN ROBERT'S CODE!!!
    print(INDIR+InOBSclim, ' ',VarName[varee])
    clim = Dataset(INDIR+InOBSclim)
    OBS = np.array(clim.variables[VarName[varee]][:])
#    OBS = OBS[:,::-1,:] # flips the rows (lats)

    clim = Dataset(INDIR+InOBSsd)
    OBSsd = np.array(clim.variables[VarName[varee]][:])
#    OBSsd = OBSATsd[:,::-1,:] # flips the rows (lats)
    
    del clim
    # pdb.set_trace() TESTED - READS IN FINE! np.shape(OBS) = 12, 36, 72 which matches expected months, latitudes, longitudes 
    
    # Set up a mask to store info on where each value comes from
    OBSmask5 = np.zeros_like(OBS)
    OBSmask5sd = np.zeros_like(OBSsd)
    # Make all present data values 1s
    OBSmask5[np.where(OBS > mdi)] = 1
    OBSmask5sd[np.where(OBSsd > mdi)] = 1
    
    # 1) Infill months in time InfillTime
    # Use original arrays
    OBS,OBSsd,OBSmask5,OBSmask5sd = InfillTime(OBS,OBSsd,mdi,OBSmask5,OBSmask5sd)
    
    # 2) Infill grids in space InfillSpace
    # Use original arrays
    OBS,OBSsd,OBSmask5,OBSmask5sd = InfillSpace(OBS,OBSsd,mdi,OBSmask5,OBSmask5sd)

    # Write this version out to netCDF, WITH THE MASK!
    TimeRes = nMonths # monthly at this point
    DataObject=[]
    DataObject.append(OBS)
    DataObject.append(OBSsd)
    DataObject.append(OBSmask5)
    DataObject.append(OBSmask5sd)

    WriteNCCF(OUTDIR+OutOBS5,TimeRes,lats5,lons5,[StClim,EdClim],DataObject,DimObjectList,AttrObjectList,GlobAttrObjectList)
    
    # 3) Interp to pentads in time InterpPentads
    
    # Create new 5x5 pentad array and delete 5x5 monthly
    NewOBS =  np.empty((nPentads,nLats5,nLons5),dtype='float')
    NewOBS.fill(mdi)
    NewOBSsd = np.copy(NewOBS)

    NewOBS,NewOBSsd = InterpTime(OBS, OBSsd, NewOBS, NewOBSsd, mdi, PentadList, varee)

    # Clean up
    OBS = []
    OBSsd = []
    
    # 4) Interp to 1x1s in space Interp1x1s

    # Create new 1x1 pentad array and delete 1x1 pentad
    NewNewOBS = np.empty((nPentads,nLats1,nLons1),dtype='float')
    NewNewOBS.fill(mdi)
    NewNewOBSsd = np.copy(NewNewOBS)

    NewNewOBS,NewNewOBSsd = InterpSpace(NewOBS, NewOBSsd, NewNewOBS, NewNewOBSsd, mdi, varee)

    # Clean up
    NewOBS = []
    NewOBSsd = []

    # Translate OBSmask5 to OBSmask1
    # Set up a mask to store info on where each value comes from
    OBSmask1 = np.zeros_like(NewNewOBS)
    OBSmask1sd = np.zeros_like(NewNewOBSsd)

    # Translate the 5by5 values across to 1by1
    StPP = 0
    EdPP = 0
    StLt = 0
    EdLt = 0
    StLn = 0
    EdLn = 0
    for lln in range(nLons5):
        StLn = EdLn + 0
	EdLn = StLn + 5 # must be +1 i.e. 0:5 to get full range allocation for 5 boxes
        StLt = 0
        EdLt = 0
        for llt in range (nLats5):
	    StLt = EdLt + 0
	    EdLt = StLt + 5 # must be +1 i.e. 0:5 to get full range allocation for 5 boxes
            StPP = 0
            EdPP = 0
	    for mm in range(nMonths):
	        StPP = EdPP + 0
		EdPP = StPP + PentadList[mm] # must be +1 i.e. 0:6 to get full range allocation for 6 pentads
	        
		OBSmask1[StPP:EdPP,StLt:EdLt,StLn:EdLn] = OBSmask5[mm,llt,lln]
	        OBSmask1sd[StPP:EdPP,StLt:EdLt,StLn:EdLn] = OBSmask5sd[mm,llt,lln]
		#pdb.set_trace()
		
    # Write out to netCDF
    # Tweak dims and global attributes relating to time period to be specific about pentads
    DimObjectList[1]=[nPentads,10,nLats1,nLons1,2]		# Change 0,2,3 elements for pentads, nLats1, nLons1

    GlobAttrObjectList['Description'] = 'HadISDH-marine INFILLED climatological (1981-2010) PENTAD mean and standard deviation \
surface '+VarDict[varee]['longer_name']+' climate monitoring product from 1973 onwards on 1deg by 1deg gridded resolution.'
    GlobAttrObjectList['Title'] = 'HadISDH-marine INFILLED climatological (1981-2010) PENTAD mean and standard deviation \
surface '+VarDict[varee]['longer_name']+' climate monitoring product.'		
    GlobAttrObjectList['Processing_level'] = 'Hourly marine ship/buoy/platform data selected for length and continuity, quality controlled, \
buddy checked, averaged to monthly means, and then averaged over 5deg gridboxes and then over the \
1981-2010 climatology period. Climatological standard deviations are of all climatology \
contributing gridbox months. Some missing data are infilled over time and space where there \
are near-by gridbox month climatologies. These monthly 5deg boxes are interpolated down to pentad \
1deg boxes.' 
    
    TimeRes = nPentads # monthly at this point
    DataObject=[]
    DataObject.append(NewNewOBS)
    DataObject.append(NewNewOBSsd)
    DataObject.append(OBSmask1)
    DataObject.append(OBSmask1sd)

    WriteNCCF(OUTDIR+OutOBS1,TimeRes,lats1,lons1,[StClim,EdClim],DataObject,DimObjectList,AttrObjectList,GlobAttrObjectList)
    
    #pdb.set_trace()

if __name__ == '__main__':
    
    main(sys.argv[1:])


# TEST NOTES
# Looks like some infilled climatologies using space may be a bit screwy if they use other latitudes e.g., lon=0,lat=6
# 	- Could say we'll only use longitudinal neighbours to provide an average - SENSIBLE
#	- Could increase the SD of the infilled box to represent the uncertainty???
#	- Could really do with a mask of infilled values locations
# Could increase InfillTime by allowing end points to be filled if there are two months on one side to provide a tendency? 
#	- this is a little dodgy as the actual value could go in the other direction - better than no value?
# Could complete seasonal cycles with at least 8 points by fitting a sine curve? So much room for error though and fiddly: 
# - but not too bad: http://stackoverflow.com/questions/16716302/how-do-i-fit-a-sine-curve-to-my-data-with-pylab-and-numpy
#
# Need a mask where boxes are identified as real (1) time filled (2) or space filled (3)
# It WORKS!

# Need to write out to files now

# HAPPY 19 Sep 2016
#************************************************************************
