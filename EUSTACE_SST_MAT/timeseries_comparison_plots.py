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
Create global average timeseries comparison plots 

For actuals and anomalies

import timeseries_comparison_plots as tcp
* compare_fimings function:
# run day, night, both comparison for all or ship only, NBC and BClocal
compare_QCraw function
# run QC verses noQC comparison for all or ship only
compare_BCNBC
# run BC NBC comparison for all or ship only
* compare_BCtype
# run BC types comparison for all or ship only which includes NBC and noQC
* compare_PTs
# run ship vs all comparison for dayQC, nightQC, bothQC, dayBC, nightBC, bothBC - also has ERA-Interim on there and NOCs Trends are computed over common period.

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
# run day, night, both comparison for all or ship only (NBC and BClocal)
tcp.compare_timings('all',AddNOCS = False) # or 'ship' If AddNOCS is not set to false then NOCS will be plotted for specific humidity
# run QC noQC comparison for all or ship only
tcp.compare_QCraw('all',AddNOCS = False) # or 'ship' (ship not set up yet for raw) If AddNOCS is not set to false then NOCS will be plotted for specific humidity
# run BC NBC comparison for all or ship only
tcp.compare_BCNBC('all',AddNOCS = False) # or 'ship' If AddNOCS is not set to false then NOCS will be plotted for specific humidity
# run BC types comparison for all or ship only
tcp.compare_BCtype('all',AddNOCS = False) # or 'ship' (ship not set up yet for all different BC types) If AddNOCS is not set to false then NOCS will be plotted for specific humidity
# run ship vs all comparison for dayQC, nightQC, bothQC, dayBC, nightBC, bothBC
tcp.compare_PTs('NBC',AddNOCS = False, AddERA = False) # or 'BClocal' If AddNOCS or AddERA is not set to false then NOCS nad ERA will be plotted for specific humidity (rh, t and td for ERA too)

or with Python 3
module load scitools/default-current
import timeseries_comparison_plots as tcp


-----------------------
OUTPUT
-----------------------
Plots to appear in 
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/PLOTS_comparison/

-----------------------
VERSION/RELEASE NOTES
-----------------------

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

mdi = -1.e30
OBS_ORDER = utils.make_MetVars(mdi, multiplier = False)

n_obs = utils.set_MetVar_attributes("n_obs", "Number of Observations", "Number of Observations", 1, -1, np.dtype("int64"), 0)
OBS_ORDER += [n_obs]

# For SHIP only versions 'ship' needs to be appended onto these directories
GRID_LOCATION = {"NBC" : "GRIDSOBSclim2NBC", 
                 "BClocal" : "GRIDSOBSclim2BClocal", 
		 "QC" : "GRIDSOBSclim2NBC", 
		 "noQC" : "GRIDSOBSclim2noQC",
		 "BClocalHGT" : "GRIDSOBSclim2BClocalHGT", 
		 "BClocalINST" : "GRIDSOBSclim2BClocalINST"}
		 
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
    TimePointers = [0, (data[0].t[-1].year - 1973)+1] # this assumes first data object is annual HadISDH.marine!!!
    ERATimePointer = (data[0].t[-1].year - 1979)+1 
     
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
	
    texty = 0.05
#    texty = 0.95
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
                    slope, lower, upper = median_pairwise_slopes(d.t[0:ERATimePointer], d.y.data[0:ERATimePointer], d.y.mdi, sigma = 1.)
                    slope_error = np.mean([(upper-slope), (slope-lower)])

                    slope_years, slope_values = mpw_plot_points(slope, d.t[0:ERATimePointer], d.y.data[0:ERATimePointer])

                else:
                    # annual - also want MPW slope
                    slope, lower, upper = median_pairwise_slopes(d.t[TimePointers[0]:TimePointers[1]], d.y.data[TimePointers[0]:TimePointers[1]], d.y.mdi, sigma = 1.)
                    slope_error = np.mean([(upper-slope), (slope-lower)])

                    slope_years, slope_values = mpw_plot_points(slope, d.t[TimePointers[0]:TimePointers[1]], d.y.data[TimePointers[0]:TimePointers[1]])


                plt.plot(slope_years, slope_values, c = d.c, lw = 1)

#               plt.text(0.03, texty, "{:6.3f} +/- {:6.4f} {} 10 yr".format(10.*slope, 10.*slope_error, d.y.units)+r'$^{-1}$', transform = ax.transAxes, color = d.c)
# If its RH then plt.text in lower left else go in lower right
                if (title[0] == 'R'):
                    plt.text(0.03, texty, "{:6.3f} +/- {:6.4f} {} 10 yr".format(10.*slope, 10.*slope_error, d.y.units)+r'$^{-1}$', transform = ax.transAxes, color = d.c, ha = 'left')
                else:
                    plt.text(0.97, texty, "{:6.3f} +/- {:6.4f} {} 10 yr".format(10.*slope, 10.*slope_error, d.y.units)+r'$^{-1}$', transform = ax.transAxes, color = d.c, ha = 'right')
#                texty -= 0.05
                texty += 0.05

    if d.name != "n_obs":
        plt.ylabel(d.y.units)
    else:
        ax1.set_ylabel("Monthly/10000")
        ax2.set_ylabel("Annual/10000")

    plt.title(title)
    
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

    percentile_point = scipy.stats.norm.cdf(sigma)


    rank_upper=((dof+percentile_point*w)/2.)+1
    rank_lower=((dof-percentile_point*w)/2.)+1

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
    ''' Run the day, night, both comparison plot for NBC and then BClocal'''
    ''' Ob_Type = all, ship - default = all '''
    ''' AddNOCS = True - default = True so NOCS time series will be added for q '''

    version = "_renorm19812010_anomalies"
    # OLD: version = "_anomalies"
    DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.3.0.0"
    # OLD: DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/"
    
    correction = "NBC"

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
                    filename = "{}/{}/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 
                elif Ob_Type == 'ship':
                    filename = "{}/{}ship/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 
		
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

    correction = "BClocal"

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
                    filename = "{}/{}/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 
                elif Ob_Type == 'ship':
                    filename = "{}/{}ship/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 
		
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
    correction = "NBC"

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
                        filename = "{}/{}/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[qc], correction, version, period, suffix, time_res) 
                    elif Ob_Type == 'ship':
                        filename = "{}/{}ship/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[qc], correction, version, period, suffix, time_res) 
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
# BC vs NBC
def compare_BCNBC(Ob_Type = 'all', AddNOCS = True):
    ''' Run the BC vs NBC comparison plot '''
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

                for correction in ["BClocal", "NBC"]:

                    # KATE ADDED ship bit
                    if Ob_Type == 'all':
                        filename = "{}/{}/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 
	
                    elif Ob_Type == 'ship':
                        filename = "{}/{}ship/OBSclim2{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 
# OLD:                filename = "{}/{}/ERAclim{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 

                    y, t = get_data(filename,var)

                    label = "{}".format(correction)
                    if correction == "NBC":
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
                do_plot(to_plot, title, "{}_{}_BClocal-NBC.png".format(var.name, period))
            elif Ob_Type == 'ship':
                do_plot(to_plot, title, "{}_{}_BClocal-NBC_SHIP.png".format(var.name, period))

#***************************************
#***************************************
# KATE ADDED
# BCtotal vs BChgt vs BCscn
def compare_BCtype(Ob_Type = 'all',AddNOCS = True):
    ''' Run the BC types total, scn and hgt comparison plot  - which now also has NBC and noQC on it'''
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

                for correction in ["noQC", "NBC", "BClocal", "BClocalHGT", "BClocalINST"]:
		
		    # Catch for filenames which are either NBC or BClocal, not BClocalHGT or BClocalINST
                    if (correction != "NBC") & (correction != "noQC"):
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
                    if correction == "BClocal":
                        if time_res == "annual":
                            color = "black" #"DarkRed"
                        else:
                            color = "black" #"r"
                    elif correction == "BClocalHGT":
                        color = "cornflowerblue" #"k"
                    elif correction == "BClocalINST":
                        color = "b" #"k"
                    elif correction == "NBC":
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
                do_plot(to_plot, title, "{}_{}_BCtypes.png".format(var.name, period))
            elif Ob_Type == 'ship':
                do_plot(to_plot, title, "{}_{}_BCtypes_SHIP.png".format(var.name, period))

#***************************************
#***************************************
# KATE ADDED
# SHIP vs all for day, night, both, NBC, BClocal (could add noQC, BClocalHGT and BClocalINST later)
def compare_PTs(Plot_Type = 'NBC', AddNOCS = True, AddERA = True):
    ''' Run the platform (ship vs all) comparison plot '''
    ''' Plot_Type = 'NBC'. 'BClocal' - default = NBC  '''
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
                    if correction != "NBC":
                        ThisCorr = "BClocal"
                    else:
                        ThisCorr = correction

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
