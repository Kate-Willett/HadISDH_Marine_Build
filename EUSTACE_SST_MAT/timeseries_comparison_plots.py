#!/usr/local/sci/bin/python3 hopefully
#*****************************
#
# Take monthly merged files and output global average timeseries
#
#
#************************************************************************
'''
Author: Robert Dunn and Kate Willett
Created: March 2016
Last update: 15 April 2019
Location: /project/hadobs2/hadisdh/marine/PROGS/Build

-----------------------
CODE PURPOSE AND OUTPUT
-----------------------
Create global average timeseries comparison plots from time series created by global_average_timeseries.py (whole globe NOT 70S to 70N)

For actuals and anomalies

import timeseries_comparison_plots as tcp
* compare_fimings function:
# run day, night, both comparison for all or ship only, noBA and BA
compare_QCraw function
# run QC verses noQC comparison for all or ship only
compare_BCNBC
# run BA noBA comparison for all or ship only
* compare_BCtype
# run BA types comparison for all or ship only which includes noBA and noQC
* compare_PTs
# run ship vs all comparison for dayQC, nightQC, bothQC, dayBA, nightBA, bothBA - also has ERA-Interim on there and NOCs Trends are computed over common period.
* compare_RH
# run noQC, BA and BA_no_whole for ship both data only to see if removing the whole number flagged data makes any difference
NOT THAT THIS DOESN'T HAVE PARTICULARLY AFFECTED DECKS REMOVED WHICH WOULD BE ANOTHER WAY OF DOING IT
-----------------------
LIST OF MODULES
-----------------------
utils.py

-----------------------
DATA
-----------------------
Input data stored in:
/project/hadobs2/hadisdh/marine/


-----------------------
HOW TO RUN THE CODE
-----------------------
# Old version: python2.7 timeseries_comparison_plots.py

python2.7
import timeseries_comparison_plots as tcp
# run day, night, both comparison for all or ship only (noBA and BA)
tcp.compare_timings('all',AddNOCS = False) # or 'ship' If AddNOCS is not set to false then NOCS will be plotted for specific humidity
# run QC noQC comparison for all or ship only
tcp.compare_QCraw('all',AddNOCS = False) # or 'ship' (ship not set up yet for raw) If AddNOCS is not set to false then NOCS will be plotted for specific humidity
# run BA noBA comparison for all or ship only
tcp.compare_BCNBC('all',AddNOCS = False) # or 'ship' If AddNOCS is not set to false then NOCS will be plotted for specific humidity
# run BA types comparison for all or ship only
tcp.compare_BCtype('all',AddNOCS = False) # or 'ship' (ship not set up yet for all different BA types) If AddNOCS is not set to false then NOCS will be plotted for specific humidity
# run ship vs all comparison for dayQC, nightQC, bothQC, dayBA, nightBA, bothBA
tcp.compare_PTs('noBA',AddNOCS = False, AddERA = False) # or 'BClocal' If AddNOCS or AddERA is not set to false then NOCS nad ERA will be plotted for specific humidity (rh, t and td for ERA too)
# run ship both RH comparison noQC, BA, BA_no_whole
tcp.compare_RH('both') # or 'day' or 'night' - only works for RH and only both at the moment

or with Python 3
module load scitools/default-current
import timeseries_comparison_plots as tcp

# For the paper
# run day, night, both comparison for ship only (BClocal used not NBC)
tcp.compare_timings('ship',AddNOCS = False) # or 'ship' If AddNOCS is not set to false then NOCS will be plotted for specific humidity
# run ship vs all comparison for dayBA, nightBA, bothBA
tcp.compare_PTs('BA',AddNOCS = True, AddERA = True) # or 'BClocal' If AddNOCS or AddERA is not set to false then NOCS nad ERA will be plotted for specific humidity (rh, t and td for ERA too)
# WILL NEED TO CHANGE TO ERA5 IF UPDATING BEYOND 2018
# run BA types comparison for ship
tcp.compare_BCtype('ship',AddNOCS = False) # or 'ship' (ship not set up yet for all different BC types) If AddNOCS is not set to false then NOCS will be plotted for specific humidity

-----------------------
OUTPUT
-----------------------
Plots to appear in 
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/PLOTS_comparison/

-----------------------
VERSION/RELEASE NOTES
-----------------------

Version 6 (11 May 2020)
---------
 
Enhancements
All trend text on plot now goes top down so is in the same order as the legend
RH now has trends from 1982 onwards shown as text on the plots in parentheses
All trends now only to 2 sig figures and st error to 3 sig figures
Now has a compare_RH plot
 
Changes
Now uses OLS with AR(1) Correction for serial correlation rather than median of pairwise slopes - requires LinearTrends.py!!!

Bug fixes
Fixed the median of pairwise slopes as it had an error and CI was too small
Now is 1.96*w which is 2.5th to 97.5th percentile slopes (weighted) so 95% confidence intervals


Version 5 (15 Apr 2019)
---------
 
Enhancements
compare_BCtyps now includes NBC and noQC and has BClocalHGT and BClocalINST in better colours
compare_PTs now has ERA-Interim added both complete and masked to SHIP (could do all)
 
Changes
Now python 3 - maybe - involves changing utils too though.
 
Bug fixes


Version 4 (21 Jan 2019)
---------
 
Enhancements
compare_timings now also plots BClocal as well as NBC
 
Changes
 
Bug fixes


Version 3 (19 Jan 2017)
---------
 
Enhancements
Can now compare ship vs all for NBC and BC
 
Changes
This is now set up as a library of programs to run different plots
so you need to call each plot type specifically.
 
Bug fixes


Version 2 (21 Dec 2016)
---------
 
Enhancements
 
Changes
Now works with ICOADS.3.0.0 filepaths and set ups
 
Bug fixes

Version 1 (release date)
---------
 
Enhancements
 
Changes
 
Bug fixes
 

-----------------------
OTHER INFORMATION
-----------------------
'''

import os
import datetime as dt
import numpy as np
import sys
import math
import scipy.stats
import matplotlib.pyplot as plt
import calendar
import gc
import netCDF4 as ncdf
import copy
import pdb

import utils
from LinearTrends import OLS_AR1Corr

mdi = -1.e30
OBS_ORDER = utils.make_MetVars(mdi, multiplier = False)

n_obs = utils.set_MetVar_attributes("n_obs", "Number of Observations", "Number of Observations", 1, -1, np.dtype("int64"), 0)
OBS_ORDER += [n_obs]

# For SHIP only versions 'ship' needs to be appended onto these directories
GRID_LOCATION = {"noBA" : "GRIDSOBSclim2NBC", 
                 "BA" : "GRIDSOBSclim2BClocal", 
		 "QC" : "GRIDSOBSclim2NBC", 
		 "noQC" : "GRIDSOBSclim2noQC",
		 "BA_HGT" : "GRIDSOBSclim2BClocalHGT", 
		 "BA_INST" : "GRIDSOBSclim2BClocalINST",
		 "BA_no_whole" : "GRIDSOBSclim2BClocal"}
		 
#PLOT_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/PLOTS_comparison/"
PLOT_LOCATION = "/data/users/hadkw/WORKING_HADISDH/MARINE/IMAGES/"
# OLD: GRID_LOCATION = {"NBC" : "GRIDS3", "BC" : "GRIDS_BC", "QC" : "GRIDS3", "noQC" : "GRIDS_noQC"}
# OLD: PLOT_LOCATION = "/project/hadobs2/hadisdh/marine/PLOTS_compare/"


suffix = "relax"

#*********************************************
class PlotData(object):
    """
    Class to hold all information for plotting easily
    """
    
    def __init__(self, name, y, t, label, c, z, lw):
        self.name = name
        self.y = y
        self.t = t
        self.label = label
        self.c = c
        self.z = z
        self.lw = lw

    def __str__(self):     
        return "variable: {}, {}, color = {}".format(self.name, self.label, self.c)

    __repr__ = __str__
   


#***************************************
def do_plot(data, title, outname):
    """
    Make and save the plot

    :param MetVar data: PlotData object containing all required inputs
    :param str title: plot title
    :param str outname: output filename
    
    If there is NOCS-q as a label then make times for all end in 2015
    If there is ERA-Interim or ERA-Interim MASKED as a label then make times for all start in 1979
    """    
    
#    pdb.set_trace()
    plt.clf()
    ax = plt.axes()

    if data[0].name == "n_obs":
        ax1 = ax
        ax2 = ax1.twinx()

    # Create a list of labels
    ListLabels = [i.label for i in data]
    ShortTrends = 0 # a switch to tell the code whether to fit shorter trends
    # Only want to plot data to end of 2018!!!!
    TimePointers = [0, (data[0].t[-1].year - 1973)+1] # this assumes first data object is annual HadISDH.marine!!!
    #TimePointers = [0, (data[0].t[-2].year - 1973)+1] # this assumes first data object is annual HadISDH.marine!!!
    ERATimePointer = (data[0].t[-1].year - 1979)+1 
    # Set up pointers for calculating RH trends 1982 to end for printing in parentheses on RH plots
    Post82RHPointer = [9, (data[0].t[-2].year - 1973)+1] # this assumes start of 1973 and data object is annual HadISDH.marine
    ERAPost82RHPointer = [3, (data[0].t[-1].year - 1979)+1] # this assumes start of 1973 and data object is annual HadISDH.marine
     
    # Find out if NOCS-q is in there and if so then only fit trends to 2015
    if ('NOCS-q' in ListLabels):
    
        ShortTrends = 1
	# Now create subset pointers to reduced time and data elements to end of 2015 only for the annual
        TimePointers[1] = 43 # 2015 - 1973 = 42 so + 1 = 43
        ERATimePointer =  37  # (2015 - 1979) + 1 = 37
    
    # Find out if ERA-Interim is in there and if so then only fit trends from 1979 onwards	
    if ('ERA-Interim' in ListLabels):

        ShortTrends = 1
	# Now create subset pointers to reduced time and data elements beginning in 1979 only for the annual
        TimePointers[0] = 6 # 1979 - 1973 = 6
	
#    texty = 0.02 # starting point for plotting text on plot
    texty = 0.22 # starts at top and works with max of 5 elements
#    pdb.set_trace()
    for d in data:
        print('Plotting: ',d.name)
        if d.label == "":
            print('Are we plotting monthly?')
            # if no label (e.g. monthly)

# DO YOU WANT MONTHLY?
#
#            if d.name == "n_obs":
#                ax1.plot(d.t, d.y.data/10000., c = d.c, zorder = d.z, lw = d.lw)
#            else:
#                plt.plot(d.t, d.y.data, c = d.c, zorder = d.z, lw = d.lw)

               
        else:
            if d.name == "n_obs":
                ax2.plot(d.t, d.y.data/10000., label = d.label, c = d.c, zorder = d.z, lw = d.lw)
            else:               
                plt.plot(d.t, d.y.data, label = d.label, c = d.c, zorder = d.z, lw = d.lw)


                # if its ERA then only need TimePointer[1] because the series starts in 1979
                if (d.label == 'ERA-Interim') | (d.label == 'ERA-Interim MASKED'):
                    # annual - also want MPW slope
                    #slope, lower, upper = median_pairwise_slopes(d.t[0:ERATimePointer], d.y.data[0:ERATimePointer], d.y.mdi, sigma = 1.)
                    #slope_error = np.mean([(upper-slope), (slope-lower)])
                    
		    # OLS with AR1 Correction
                    slopes = OLS_AR1Corr(d.y.data[0:ERATimePointer], d.y.mdi, 0.9)
                    slope = slopes[0]
                    slope_error = slopes[4]
                    
                    slope_years, slope_values = mpw_plot_points(slope, d.t[0:ERATimePointer], d.y.data[0:ERATimePointer])

# New bit for RH only
                    if (title[0] == 'R'):
                        #slopeRH, lowerRH, upperRH = median_pairwise_slopes(d.t[ERAPost82RHPointer[0]:ERAPost82RHPointer[1]], d.y.data[ERAPost82RHPointer[0]:ERAPost82RHPointer[1]], d.y.mdi, sigma = 1.)
                        #slope_errorRH = np.mean([(upperRH-slopeRH), (slopeRH-lowerRH)])

		        # OLS with AR1 Correction
                        slopesRH = OLS_AR1Corr(d.y.data[ERAPost82RHPointer[0]:ERAPost82RHPointer[1]], d.y.mdi, 0.9)
                        slopeRH = slopesRH[0]
                        slope_errorRH = slopesRH[4]

                else:
                    # annual - also want MPW slope
                    #slope, lower, upper = median_pairwise_slopes(d.t[TimePointers[0]:TimePointers[1]], d.y.data[TimePointers[0]:TimePointers[1]], d.y.mdi, sigma = 1.)
                    #slope_error = np.mean([(upper-slope), (slope-lower)])

		    # OLS with AR1 Correction
                    slopes = OLS_AR1Corr(d.y.data[TimePointers[0]:TimePointers[1]], d.y.mdi, 0.9)
                    slope = slopes[0]
                    slope_error = slopes[4]

                    slope_years, slope_values = mpw_plot_points(slope, d.t[TimePointers[0]:TimePointers[1]], d.y.data[TimePointers[0]:TimePointers[1]])

# New bit for RH only
                    if (title[0] == 'R'):
                        #slopeRH, lowerRH, upperRH = median_pairwise_slopes(d.t[Post82RHPointer[0]:Post82RHPointer[1]], d.y.data[Post82RHPointer[0]:Post82RHPointer[1]], d.y.mdi, sigma = 1.)
                        #slope_errorRH = np.mean([(upperRH-slopeRH), (slopeRH-lowerRH)])

		        # OLS with AR1 Correction
                        slopesRH = OLS_AR1Corr(d.y.data[Post82RHPointer[0]:Post82RHPointer[1]], d.y.mdi, 0.9)
                        slopeRH = slopesRH[0]
                        slope_errorRH = slopesRH[4]

                plt.plot(slope_years, slope_values, c = d.c, lw = 1)

#               plt.text(0.03, texty, "{:6.3f} +/- {:6.4f} {} 10 yr".format(10.*slope, 10.*slope_error, d.y.units)+r'$^{-1}$', transform = ax.transAxes, color = d.c)
# If its RH then plt.text in lower left else go in lower right
# Also if its RH then plot the text of the 1982+ trends in parentheses too
                if (title[0] == 'R'):
                    #plt.text(0.03, texty, "{:6.3f} +/- {:6.4f} {} 10 yr".format(10.*slope, 10.*slope_error, d.y.units)+r'$^{-1}$', transform = ax.transAxes, color = d.c, ha = 'left')
                    # Now has 1982+ trends  and only plots trends to 2 sig figs and st err to 3 sig figs too
                    plt.text(0.03, texty, "{:6.2f} +/- {:6.3f} ({:6.2f} +/- {:6.3f}) {} 10 yr".format(10.*slope, 10.*slope_error, 10.*slopeRH, 10.*slope_errorRH, d.y.units)+r'$^{-1}$', transform = ax.transAxes, color = d.c, ha = 'left')
                else:
                    #plt.text(0.97, texty, "{:6.3f} +/- {:6.4f} {} 10 yr".format(10.*slope, 10.*slope_error, d.y.units)+r'$^{-1}$', transform = ax.transAxes, color = d.c, ha = 'right')
                    # Now plots trends to 2 sig figs and st err to 3 sig figs
                    plt.text(0.97, texty, "{:6.2f} +/- {:6.3f} {} 10 yr".format(10.*slope, 10.*slope_error, d.y.units)+r'$^{-1}$', transform = ax.transAxes, color = d.c, ha = 'right')
                texty -= 0.05 # top downwards 
#                texty += 0.05 # bottom upwards

    if d.name != "n_obs":
        plt.ylabel(d.y.units)
    else:
        ax1.set_ylabel("Monthly/10000")
        ax2.set_ylabel("Annual/10000")

#    plt.title(title)
    
    # If its RH then plot legend in upper right, else plot in upper left
    if (title[0] == 'R'):
        plt.legend(loc = 'upper right')
    else:
        plt.legend(loc = 'upper left')
    plt.savefig(PLOT_LOCATION + outname)

    return # do_plot

#***************************************
def get_data(filename,var):
    """
    Read in the netCDF data

    :param str filename: file to read in data from
    :param dictionary var: dictionary of variable name to read in 
    :returns: ydata - MetVar object
              times - time data
    
    """

    ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')
    
    # For Python 3 set automatic masking to false as its screwing everything up
    ncdf_file.set_auto_mask(False)

    ydata = ncdf_file.variables[var.name]
    times = ncdf_file.variables["time"] # days since 1973/1/1
    
    #pdb.set_trace()
    times = ncdf.num2date(times[:], units = times.units, calendar = 'gregorian')
    # For some reason with Python3 this was falling over when reading in the monthly data
    # The times[:] in python2.7 is just a list but times[:] in python 3 is a masked array.
    #pdb.set_trace()

    # convert to MetVar from netCDF object
    ydata = utils.set_MetVar_attributes(var.name, ydata.long_name, ydata.standard_name, ydata.units, mdi, np.dtype('float64'), 0, multiplier = False)
    ydata.data = ncdf_file.variables[var.name][:]

    return ydata, times

#***************************************
def read_nocs():
    """
    Read the NOCS q datafile
    
    :returns: PlotData containing monthly and annual values
    """
    

    indata = np.genfromtxt("/project/hadobs2/hadisdh/marine/otherdata/NOCS_q_sotc2015.txt", dtype = str)
    
    # NOCS data starts in Jan 1971 so only read in from Jan 1973

    t = indata[24::, 0]
    nocs = indata[24::, -1]
    
    nocs = np.array([float(i) for i in nocs])

    y = utils.set_MetVar_attributes("relative_humidity", "Relative humidity", "relative humidity", "%rh", mdi, np.dtype('float64'), 8, multiplier = False)
    y.data = nocs

    t = np.array([dt.datetime.strptime(i, "%d-%b-%Y") for i in t])

    monthly = PlotData("", y, t, "", 'turquoise', 1, 1) #'g', 1, 1)

    # annual

    nocs = nocs.reshape(-1, 12)
    nocs = np.mean(nocs, axis = 1)
    y = utils.set_MetVar_attributes("specific_humidity", "Specific humidity", "specific humidity", "g/kg", mdi, np.dtype('float64'), 8, multiplier = False)
    y.data = nocs

    t = t.reshape(-1, 12)
    t = t[:, 6]

    annual = PlotData("", y, t, "NOCS-q", 'darkturquoise', 10, 2) #'DarkGreen', 10, 2)
    
    return monthly, annual  # read_nocs

#***************************************
def read_era(ERAVar = 'q'):
    """
    Read the ERA-Interim datafiles for q, RH, t and Td
    
    REMEMBER THAT THIS BEGINS IN 1979 SO NEEDS PADDING OUT BACK TO 1973
    
    :ERAVar = str of variable to read in q, rh, t, td
    
    :returns: PlotData containing monthly and annual values
    """
    
    # Get the BClocalSHIPboth MASKED \nd unmasked data
    # Read the monthly data into a numpy array of nMonths rows and year, global, nhem, trop, shem colums.
    indataMASK = np.genfromtxt("/project/hadobs2/hadisdh/marine/otherdata/"+ERAVar+"2m_5by5_monthly_anoms1981-2010_ERA-Interim_areaTS_19792018_MASK_marine_monthly.dat", dtype = str)
    indata = np.genfromtxt("/project/hadobs2/hadisdh/marine/otherdata/"+ERAVar+"2m_5by5_monthly_anoms1981-2010_ERA-Interim_areaTS_19792018_marine_monthly.dat", dtype = str)

    # Get the times - these are strings of YYYYMM
    t = indataMASK[1::, 0]
    # Get the global average values
    eraMASK = indataMASK[1::, 1]
    era = indata[1::, 1]
    
    # Convert the data to floats
    eraMASK = np.array([float(i) for i in eraMASK])
    era = np.array([float(i) for i in era])

    if (ERAVar == 'q'):
        y = utils.set_MetVar_attributes("specific_humidity", "Specific humidity", "specific humidity", "g/kg", mdi, np.dtype('float64'), 8, multiplier = False)
    elif (ERAVar == 'rh'):
        y = utils.set_MetVar_attributes("relative_humidity", "Relative humidity", "relative humidity", "%rh", mdi, np.dtype('float64'), 8, multiplier = False)
    elif (ERAVar == 't'):
        y = utils.set_MetVar_attributes("marine_air_temperature", "Marine air temperature", "marine air temperature", "degrees C", mdi, np.dtype('float64'), 8, multiplier = False)
    elif (ERAVar == 'td'):
        y = utils.set_MetVar_attributes("dew_point_temperature", "Dew point temperature", "dew point temperature", "degrees C", mdi, np.dtype('float64'), 8, multiplier = False)
    
    yMASK = copy.copy(y)
    y.data = era
    yMASK.data = eraMASK

    # Get datetime objects for each time point assuming middle of the month - so 15th or there abouts
    t = np.array([dt.datetime.strptime(i+'15', "%Y%m%d") for i in t])

    monthly = PlotData("", y, t, "", 'orchid', 1, 1) #'g', 1, 1)
    monthlyMASK = PlotData("", yMASK, t, "", 'm', 1, 1) #'g', 1, 1)

    # annual
    
#    pdb.set_trace()
    
    era = era.reshape(-1, 12)
    era = np.mean(era, axis = 1)
    eraMASK = eraMASK.reshape(-1, 12)
    eraMASK = np.mean(eraMASK, axis = 1)

    if (ERAVar == 'q'):
        y = utils.set_MetVar_attributes("specific_humidity", "Specific humidity", "specific humidity", "g/kg", mdi, np.dtype('float64'), 8, multiplier = False)
    elif (ERAVar == 'rh'):
        y = utils.set_MetVar_attributes("relative_humidity", "Relative humidity", "relative humidity", "%rh", mdi, np.dtype('float64'), 8, multiplier = False)
    elif (ERAVar == 't'):
        y = utils.set_MetVar_attributes("marine_air_temperature", "Marine air temperature", "marine air temperature", "degrees C", mdi, np.dtype('float64'), 8, multiplier = False)
    elif (ERAVar == 'td'):
        y = utils.set_MetVar_attributes("dew_point_temperature", "Dew point temperature", "dew point temperature", "degrees C", mdi, np.dtype('float64'), 8, multiplier = False)
    
    yMASK = copy.copy(y)
    y.data = era
    yMASK.data = eraMASK

    t = t.reshape(-1, 12) 
    # Set annual times as July?   
    t = t[:, 6]

    annual = PlotData("", y, t, "ERA-Interim", 'orchid', 10, 2) #'DarkGreen', 10, 2)
    annualMASK = PlotData("", yMASK, t, "ERA-Interim MASKED", 'm', 10, 2) #'DarkGreen', 10, 2)
    
    print('End of ERA read in')
#    pdb.set_trace()
    
    return monthly, monthlyMASK, annual, annualMASK  # read_nocs

#***************************************
def median_pairwise_slopes(xdata, ydata, mdi, sigma = 1.):
    '''
    Calculate the median of the pairwise slopes - assumes no missing values

    :param array xdata: x array
    :param array ydata: y array
    :param float mdi: missing data indicator
    :param float sigma: std range for upper/lower
    :returns: float of slope
    '''
    # run through all pairs, and obtain slope
    slopes=[]
    for i in range(len(xdata)):
        for j in range(i+1,len(xdata)):
            if ydata[i] >  mdi and ydata[j] > mdi:
                slopes+=[(ydata[j]-ydata[i])/(xdata[j].year-xdata[i].year)]

    mpw=np.median(np.array(slopes))

    # copied from median_pairwise.pro methodology (Mark McCarthy)
    slopes.sort()

    good_data=np.where(ydata != mdi)[0]

    n=len(ydata[good_data])

    dof=n*(n-1)/2
    w=math.sqrt(n*(n-1)*((2.*n)+5.)/18.)

    # THIS IS WRONG!!! gives 0.84 but should be 1.96
    # 1.96 pulls out the 2.5th and 97.5th percentiles so gives the 95% confidence interval
    #percentile_point = scipy.stats.norm.cdf(sigma)
    percentile_point = 1.96


    rank_upper=((dof+percentile_point*w)/2.)+1
    rank_lower=((dof-percentile_point*w)/2.) # +1 I DON'T THINK THIS NEEDS +1 as it shoudl be -1 and the int() floors it anyway!

    if rank_upper >= len(slopes): rank_upper=len(slopes)-1
    if rank_upper < 0: rank_upper=0
    if rank_lower < 0: rank_lower=0

    upper=slopes[int(rank_upper)]
    lower=slopes[int(rank_lower)]
    

    return mpw,lower,upper      # MedianPairwiseSlopes

#************************************************************************
def mpw_plot_points(slope, years, values):
    """
    Calculate start and end points for line describing MPW best fit

    :param float slope: line slope
    :param float array years: x-coordinates
    :param float array values: y-coordinates
    
    :returns: [[x1,x2], [y1,y1]]
    """
    

    mu_x=np.ma.mean(np.array([y.year for y in years]))
    mu_y=np.ma.mean(values)
    deltas=[]

    y1=slope*(years[0].year-mu_x)+mu_y
    y2=slope*(years[-1].year-mu_x)+mu_y
 
    return [years[0], years[-1]], [y1, y2] # mpw_plot_points

#***************************************
#***************************************
# Day versus Night
def compare_timings(Ob_Type = 'all', AddNOCS = True):
    ''' Run the day, night, both comparison plot for noBA and then BA'''
    ''' Ob_Type = all, ship - default = all '''
    ''' AddNOCS = True - default = True so NOCS time series will be added for q '''

    version = "_renorm19812010_anomalies"
    # OLD: version = "_anomalies"
    DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.3.0.0"
    # OLD: DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/"
    
    correction = "noBA"
    filecorrection = "NBC"

    for v, var in enumerate(OBS_ORDER):
    #    if "anomalies" not in var.name:
    #        continue

        to_plot = []

        for time_res in ["annual", "monthly"]:
            if time_res == "annual":
                zorder = 10
                lw = 2
            else:
                zorder = 1
                lw = 1

            for period in ["both", "day", "night"]:
                if period == "both":
                    color = "black" #"lime"
                elif period == "day":
                    color = "gold" #"r"
                elif period == "night":
                    color = "mediumslateblue" #"c"

                # KATE ADDED ship bit
                if Ob_Type == 'all':
                    filename = "{}/{}/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], filecorrection, version, period, suffix, time_res) 
                elif Ob_Type == 'ship':
                    filename = "{}/{}ship/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], filecorrection, version, period, suffix, time_res) 
		
# OLD:            filename = "{}/{}/ERAclim{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 

                print(filename,var)
                y, t = get_data(filename,var)

                label = "{}".format(period)

                if time_res == "annual":
                    to_plot += [PlotData(var.name, y, t, label, color, zorder, lw)]
                else:
                    to_plot += [PlotData(var.name, y, t, "", color, zorder, lw)]
                
        title = "{} - {}".format(" ".join([s.capitalize() for s in var.name.split("_")]), correction)

        # Kate add this bit to make inclusion of NOCS optional
        if (AddNOCS) & ("specific_humidity" in var.name):
            nocs_m, nocs_a = read_nocs()
            to_plot += [nocs_m, nocs_a]
        # KATE ADDED ship bit
        if Ob_Type == 'all':
            do_plot(to_plot, title, "{}_{}_day-night-both.png".format(var.name, correction))
        elif Ob_Type == 'ship':
            do_plot(to_plot, title, "{}_{}_day-night-both_SHIP.png".format(var.name, correction))

    correction = "BA"
    filecorrection = "BClocal"

    for v, var in enumerate(OBS_ORDER):
    #    if "anomalies" not in var.name:
    #        continue

        to_plot = []

        for time_res in ["annual", "monthly"]:
            if time_res == "annual":
                zorder = 10
                lw = 2
            else:
                zorder = 1
                lw = 1

            for period in ["both", "day", "night"]:
                if period == "both":
                    color = "black" #"lime"
                elif period == "day":
                    color = "gold" #"r"
                elif period == "night":
                    color = "mediumslateblue" #"c"

                # KATE ADDED ship bit
                if Ob_Type == 'all':
                    filename = "{}/{}/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], filecorrection, version, period, suffix, time_res) 
                elif Ob_Type == 'ship':
                    filename = "{}/{}ship/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], filecorrection, version, period, suffix, time_res) 
		
# OLD:            filename = "{}/{}/ERAclim{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 

                y, t = get_data(filename,var)

                label = "{}".format(period)

                if time_res == "annual":
                    to_plot += [PlotData(var.name, y, t, label, color, zorder, lw)]
                else:
                    to_plot += [PlotData(var.name, y, t, "", color, zorder, lw)]
                
        title = "{} - {}".format(" ".join([s.capitalize() for s in var.name.split("_")]), correction)

        # Kate add this bit to make inclusion of NOCS optional
        if (AddNOCS) & ("specific_humidity" in var.name):
            nocs_m, nocs_a = read_nocs()
            to_plot += [nocs_m, nocs_a]
        # KATE ADDED ship bit
        if Ob_Type == 'all':
            do_plot(to_plot, title, "{}_{}_day-night-both.png".format(var.name, correction))
        elif Ob_Type == 'ship':
            do_plot(to_plot, title, "{}_{}_day-night-both_SHIP.png".format(var.name, correction))


#***************************************
#***************************************
# QC vs noQC
def compare_QCraw(Ob_Type = 'all',AddNOCS = True):
    ''' Run the QC vs noQC comparison plot '''
    ''' Ob_Type = all, ship - default = all '''
    ''' AddNOCS = True - default = True so NOCS time series will be added for q '''

    version = "_renorm19812010_anomalies"
    # OLD: version = "_anomalies"
    DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.3.0.0"
    # OLD: DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/"
    correction = "noBA"
    filecorrection = "NBC"

    for v, var in enumerate(OBS_ORDER):

        # separate plots for both/day/night
        for period in ["both", "day", "night"]:
            to_plot = []

            for time_res in ["annual", "monthly"]:
                if time_res == "annual":
                    zorder = 10
                    lw = 2
                else:
                    zorder = 1
                    lw = 1

                for qc in ["QC", "noQC"]:

                    # KATE ADDED ship bit
                    if Ob_Type == 'all':
                        filename = "{}/{}/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[qc], filecorrection, version, period, suffix, time_res) 
                    elif Ob_Type == 'ship':
                        filename = "{}/{}ship/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[qc], filecorrection, version, period, suffix, time_res) 
# OLD:                filename = "{}/{}/ERAclim{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[qc], correction, version, period, suffix, time_res) 

                    y, t = get_data(filename,var)

                    label = "{}".format(qc)
                    if qc == "QC":
                        if time_res == "annual":
                            color = "grey" #"DarkRed"
                        else:
                            color = "r"
                    elif qc == "noQC":
                        color = "red" #"k"
                    
                    if time_res == "annual":
                        to_plot += [PlotData(var.name, y, t, label, color, zorder, lw)]
                    else:
                        to_plot += [PlotData(var.name, y, t, "", color, zorder, lw)]

        
            title = "{} - {} - {}".format(" ".join([s.capitalize() for s in var.name.split("_")]), correction, period)

            # Kate add this bit to make inclusion of NOCS optional
            if (AddNOCS) & ("specific_humidity" in var.name):
                nocs_m, nocs_a = read_nocs()
                to_plot += [nocs_m, nocs_a]
            # KATE ADDED ship bit
            if Ob_Type == 'all':
                do_plot(to_plot, title, "{}_{}_{}_QC-noQC.png".format(var.name, period, correction))
            elif Ob_Type == 'ship':
                do_plot(to_plot, title, "{}_{}_{}_QC-noQC_SHIP.png".format(var.name, period, correction))

#***************************************
#***************************************
# BA vs noBA
def compare_BCNBC(Ob_Type = 'all', AddNOCS = True):
    ''' Run the BA vs noBA comparison plot '''
    ''' Ob_Type = all, ship - default = all '''
    ''' AddNOCS = True - default = True so NOCS time series will be added for q '''

    version = "_renorm19812010_anomalies"
    #OLD: version = "_anomalies"
    DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.3.0.0"
    # OLD: DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/"

    for v, var in enumerate(OBS_ORDER):
    #    if "anomalies" not in var.name:
    #        continue

        # separate plots for both/day/night
        for period in ["both", "day", "night"]:
            to_plot = []

            for time_res in ["annual", "monthly"]:
                if time_res == "annual":
                    zorder = 10
                    lw = 2
                else:
                    zorder = 1
                    lw = 1

                for correction in ["BA", "noBA"]:

                    if (correction == "BA"):
                        filecorrection == "BClocal"
                    else:
                        filecorrection = "NBC"
		    
		    # KATE ADDED ship bit
                    if Ob_Type == 'all':
                        filename = "{}/{}/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], filecorrection, version, period, suffix, time_res) 
	
                    elif Ob_Type == 'ship':
                        filename = "{}/{}ship/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], filecorrection, version, period, suffix, time_res) 
# OLD:                filename = "{}/{}/ERAclim{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 

                    y, t = get_data(filename,var)

                    label = "{}".format(correction)
                    if correction == "noBA":
                        if time_res == "annual":
                            color = "grey" #"DarkRed"
                        else:
                            color = "grey" #"r"
                    else:
                        color = "black" #"k"
                    
                    if time_res == "annual":
                        to_plot += [PlotData(var.name, y, t, label, color, zorder, lw)]
                    else:
                        to_plot += [PlotData(var.name, y, t, "", color, zorder, lw)]

        
            title = "{} - {} - {}".format(" ".join([s.capitalize() for s in var.name.split("_")]), period, "QC")

            # Kate add this bit to make inclusion of NOCS optional
            if (AddNOCS) & ("specific_humidity" in var.name):
                nocs_m, nocs_a = read_nocs()
                to_plot += [nocs_m, nocs_a]

            # KATE ADDED ship bit
            if Ob_Type == 'all':
                do_plot(to_plot, title, "{}_{}_BA-noBA.png".format(var.name, period))
            elif Ob_Type == 'ship':
                do_plot(to_plot, title, "{}_{}_BA-noBA_SHIP.png".format(var.name, period))

#***************************************
#***************************************
# KATE ADDED
# BAtotal vs BAhgt vs BAscn
def compare_BCtype(Ob_Type = 'all',AddNOCS = True):
    ''' Run the BA types total, scn and hgt comparison plot  - which now also has NBC and noQC on it'''
    ''' Ob_Type = 'all'. 'ship' - default = all '''
    ''' AddNOCS = True - default = True so NOCS time series will be added for q '''
    

    version = "_renorm19812010_anomalies"
    #OLD: version = "_anomalies"
    DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.3.0.0"
    # OLD: DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/"

    for v, var in enumerate(OBS_ORDER):
    #    if "anomalies" not in var.name:
    #        continue

        # separate plots for both/day/night
        for period in ["both", "day", "night"]:
            to_plot = []

            for time_res in ["annual", "monthly"]:
                if time_res == "annual":
                    zorder = 10
                    lw = 2
                else:
                    zorder = 1
                    lw = 1

                for correction in ["noQC", "noBA", "BA", "BA_HGT", "BA_INST"]:
		
		    # Catch for filenames which are either NBC or BClocal, not BClocalHGT or BClocalINST
                    if (correction != "noBA") & (correction != "noQC"):
                        ThisCorr = "BClocal"
                    else:
                        ThisCorr = "NBC" #correction

                    if Ob_Type == 'all':
                        filename = "{}/{}/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], ThisCorr, version, period, suffix, time_res) 
                    elif Ob_Type == 'ship':
                        filename = "{}/{}ship/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], ThisCorr, version, period, suffix, time_res) 
# OLD:                filename = "{}/{}/ERAclim{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 

                    y, t = get_data(filename,var)

                    label = "{}".format(correction)
                    if correction == "BA":
                        if time_res == "annual":
                            color = "black" #"DarkRed"
                        else:
                            color = "black" #"r"
                    elif correction == "BA_HGT":
                        color = "cornflowerblue" #"k"
                    elif correction == "BA_INST":
                        color = "b" #"k"
                    elif correction == "noBA":
                        color = "grey" #"k"
                    elif correction == "noQC":
                        color = "red" #"k"
                    
                    if time_res == "annual":
                        to_plot += [PlotData(var.name, y, t, label, color, zorder, lw)]
                    else:
                        to_plot += [PlotData(var.name, y, t, "", color, zorder, lw)]

        
            title = "{} - {} - {}".format(" ".join([s.capitalize() for s in var.name.split("_")]), period, "QC")

            # Kate add this bit to make inclusion of NOCS optional
            if (AddNOCS) & ("specific_humidity" in var.name):
                nocs_m, nocs_a = read_nocs()
                to_plot += [nocs_m, nocs_a]

            if Ob_Type == 'all':
                do_plot(to_plot, title, "{}_{}_BAtypes.png".format(var.name, period))
            elif Ob_Type == 'ship':
                do_plot(to_plot, title, "{}_{}_BAtypes_SHIP.png".format(var.name, period))

#***************************************
#***************************************
# KATE ADDED
# SHIP vs all for day, night, both, noBA, BA (could add noQC, BA_HGT and BA_INST later)
def compare_PTs(Plot_Type = 'noBA', AddNOCS = True, AddERA = True):
    ''' Run the platform (ship vs all) comparison plot '''
    ''' Plot_Type = 'noBA'. 'BA' - default = noBA  '''
    ''' AddNOCS = True - default = True so NOCS time series will be added for q '''
    ''' AddERA = True - default = True so ERA time series will be added for q, rh, t and td '''

    version = "_renorm19812010_anomalies"
    #OLD: version = "_anomalies"
    DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.3.0.0"
    # OLD: DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/"
    
    correction = Plot_Type

    for v, var in enumerate(OBS_ORDER):
    #    if "anomalies" not in var.name:
    #        continue

        # separate plots for both/day/night
        for period in ["both", "day", "night"]:
            to_plot = []

            for time_res in ["annual", "monthly"]:
                if time_res == "annual":
                    zorder = 10
                    lw = 2
                else:
                    zorder = 1
                    lw = 1

                for Ob_Type in ["ship", "all"]: #, "BClocalHGT", "BClocalINST"]:
		
		    # Catch for filenames which are either NBC or BClocal, not BClocalHGT or BClocalINST
                    if correction != "noBA":
                        ThisCorr = "BClocal"
                    else:
                        ThisCorr = "NBC"

                    if Ob_Type == 'all':
                        filename = "{}/{}/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], ThisCorr, version, period, suffix, time_res) 
                    elif Ob_Type == 'ship':
                        filename = "{}/{}ship/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], ThisCorr, version, period, suffix, time_res) 
# OLD:                filename = "{}/{}/ERAclim{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 

                    y, t = get_data(filename,var)

                    label = "{}".format(Ob_Type)
                    if Ob_Type == "ship":
                        color = "black" #"DarkRed"
                    elif Ob_Type == "all":
                        color = "mediumseagreen" #"k"
                    
                    if time_res == "annual":
                        to_plot += [PlotData(var.name, y, t, label, color, zorder, lw)]
                    else:
                        to_plot += [PlotData(var.name, y, t, "", color, zorder, lw)]

        
            title = "{} - {} - {}".format(" ".join([s.capitalize() for s in var.name.split("_")]), period, correction)

            # Kate add this bit to make inclusion of NOCS optional
            if (AddNOCS) & ("specific_humidity" in var.name):
                nocs_m, nocs_a = read_nocs()
                to_plot += [nocs_m, nocs_a]

            if (AddERA) & ("specific_humidity" in var.name):
                era_m, era_m_mask, era_a, era_a_mask = read_era('q')
                to_plot += [era_m, era_a]
                to_plot += [era_m_mask, era_a_mask]

            if (AddERA) & ("relative_humidity" in var.name):
                era_m, era_m_mask, era_a, era_a_mask = read_era('rh')
                to_plot += [era_m, era_a]
                to_plot += [era_m_mask, era_a_mask]

            if (AddERA) & ("marine_air_temperature" in var.name):
                era_m, era_m_mask, era_a, era_a_mask = read_era('t')
                to_plot += [era_m, era_a]
                to_plot += [era_m_mask, era_a_mask]

            if (AddERA) & ("dew_point_temperature" in var.name):
                era_m, era_m_mask, era_a, era_a_mask = read_era('td')
                to_plot += [era_m, era_a]
                to_plot += [era_m_mask, era_a_mask]

            print("Making plot")
            do_plot(to_plot, title, "{}_{}_{}_ShipAll.png".format(var.name, period,Plot_Type))

#************************************************************************************************************
# SHIP  RH comparisons for noQC, BA and BA_no_whole (ship only)
def compare_RH(Plot_Type = 'both'):
    ''' Run the platform (ship vs all) comparison plot '''
    ''' Plot_Type = 'noBA'. 'BA' - default = noBA  '''
    ''' AddNOCS = True - default = True so NOCS time series will be added for q '''
    ''' AddERA = True - default = True so ERA time series will be added for q, rh, t and td '''

    version = "_renorm19812010_anomalies"
    #OLD: version = "_anomalies"
    DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.3.0.0"
    # OLD: DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/"
    
    correction = "WHOLE NUMBERS"
    period = Plot_Type
    Ob_Type = "ship"

    for v, var in enumerate(OBS_ORDER):

        if (var.name != "relative_humidity_anomalies"):
            continue

       # separate plots for both/day/night
        to_plot = []

        for Series in ["noQC", "BA", "BA_no_whole"]:
	    
            for time_res in ["annual", "monthly"]:
                if time_res == "annual":
                    zorder = 10
                    lw = 2
                else:
                    zorder = 1
                    lw = 1

	        # Catch for filenames which are either NBC or BClocal, not BClocalHGT or BClocalINST
                if (Series == "noQC"):
                    ThisCorr = "NBC"
                    FlagType = ""
                    color = "red"
                elif (Series == "BA"):
                    ThisCorr = "BClocal"
                    FlagType = ""
                    color = "black"
                elif (Series == "BA_no_whole"):
                    ThisCorr = "BClocal"
                    FlagType = "NOWHOLE"
                    color = "grey"
                
                filename = "{}/{}ship{}/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[Series], FlagType, ThisCorr, version, period, suffix, time_res) 
# OLD:                filename = "{}/{}/ERAclim{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 

                y, t = get_data(filename,var)

                label = "{}".format(Series)
                    
                if time_res == "annual":
                    to_plot += [PlotData(var.name, y, t, label, color, zorder, lw)]
                else:
                    to_plot += [PlotData(var.name, y, t, "", color, zorder, lw)]

        
            title = "{} - {} - {}".format(" ".join([s.capitalize() for s in var.name.split("_")]), period, correction)

            print("Making plot")
            do_plot(to_plot, title, "{}_{}_{}_RHComp.png".format(var.name, period,Plot_Type))
