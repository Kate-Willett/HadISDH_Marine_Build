#!/usr/local/sci/bin/python2.7
#*****************************
#
# Take monthly merged files and output global average timeseries
#
#
#************************************************************************
'''
Author: Robert Dunn and Kate Willett
Created: March 2016
Last update: 21 January 2019
Location: /project/hadobs2/hadisdh/marine/PROGS/Build

-----------------------
CODE PURPOSE AND OUTPUT
-----------------------
Create global average timeseries comparison plots 

For actuals and anomalies

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
tcp.compare_timings('all') # or 'ship'
# run QC noQC comparison for all or ship only
tcp.compare_QCraw('all') # or 'ship' (ship not set up yet for raw)
# run BC NBC comparison for all or ship only
tcp.compare_BCNBC('all') # or 'ship'
# run BC types comparison for all or ship only
tcp.compare_BCtype('all') # or 'ship' (ship not set up yet for all different BC types)
# run ship vs all comparison for dayQC, nightQC, bothQC, dayBC, nightBC, bothBC
tcp.compare_PTs('NBC') # or 'BClocal' 


-----------------------
OUTPUT
-----------------------
Plots to appear in 
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/PLOTS_comparison/
OLD: /project/hadobs2/hadisdh/marine/ICOADS.2.5.1/PLOTS_comparison/

-----------------------
VERSION/RELEASE NOTES
-----------------------

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

import utils

mdi = -1.e30
OBS_ORDER = utils.make_MetVars(mdi, multiplier = False)

n_obs = utils.set_MetVar_attributes("n_obs", "Number of Observations", "Number of Observations", 1, -1, np.dtype("int64"), 0)
OBS_ORDER += [n_obs]

GRID_LOCATION = {"NBC" : "GRIDSOBSclim2NBC", 
                 "BClocal" : "GRIDSOBSclim2BClocal", 
		 "QC" : "GRIDSOBSclim2NBC", 
		 "noQC" : "GRIDSOBSclim2noQC",
		 "BClocalHGT" : "GRIDSOBSclim2BClocalHGT", 
		 "BClocalINST" : "GRIDSOBSclim2BClocalINST"}
PLOT_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/PLOTS_comparison/"
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
    """    
    plt.clf()
    ax = plt.axes()

    if data[0].name == "n_obs":
        ax1 = ax
        ax2 = ax1.twinx()


    texty = 0.95
    for d in data:
        if d.label == "":
            # if no label (e.g. monthly)

            if d.name == "n_obs":
                ax1.plot(d.t, d.y.data/10000., c = d.c, zorder = d.z, lw = d.lw)
            else:
                plt.plot(d.t, d.y.data, c = d.c, zorder = d.z, lw = d.lw)

               
        else:
            if d.name == "n_obs":
                ax2.plot(d.t, d.y.data/10000., label = d.label, c = d.c, zorder = d.z, lw = d.lw)
            else:               
                plt.plot(d.t, d.y.data, label = d.label, c = d.c, zorder = d.z, lw = d.lw)

                # annual - also want MPW slope
                slope, lower, upper = median_pairwise_slopes(d.t, d.y.data, d.y.mdi, sigma = 1.)
                slope_error = np.mean([(upper-slope), (slope-lower)])

                slope_years, slope_values = mpw_plot_points(slope, d.t, d.y.data)
                plt.plot(slope_years, slope_values, c = d.c, lw = 1)

                plt.text(0.03, texty, "{:6.3f} +/- {:6.4f} {} 10 yr".format(10.*slope, 10.*slope_error, d.y.units)+r'$^{-1}$', transform = ax.transAxes, color = d.c)
                texty -= 0.05

    if d.name != "n_obs":
        plt.ylabel(d.y.units)
    else:
        ax1.set_ylabel("Monthly/10000")
        ax2.set_ylabel("Annual/10000")

    plt.title(title)
    plt.legend()
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

    ydata = ncdf_file.variables[var.name]
    times = ncdf_file.variables["time"] # days since 1973/1/1
    
    times = ncdf.num2date(times[:], units = times.units, calendar = 'gregorian')

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

    t = indata[:, 0]
    nocs = indata[:, -1]
    
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
def compare_timings(Ob_Type = 'all'):
    ''' Run the day, night, both comparison plot for NBC and then BClocal'''
    ''' Ob_Type = all, ship - default = all '''

    version = "_renorm19812010_anomalies"
    # OLD: version = "_anomalies"
    DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/"
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
                    color = "grey" #"lime"
                elif period == "day":
                    color = "darkorange" #"r"
                elif period == "night":
                    color = "darkblue" #"c"

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

        if "specific_humidity" in var.name:
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
                    color = "grey" #"lime"
                elif period == "day":
                    color = "darkorange" #"r"
                elif period == "night":
                    color = "darkblue" #"c"

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

        if "specific_humidity" in var.name:
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
def compare_QCraw(Ob_Type = 'all'):
    ''' Run the QC vs noQC comparison plot '''
    ''' Ob_Type = all, ship - default = all '''

    version = "_renorm19812010_anomalies"
    # OLD: version = "_anomalies"
    DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/"
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

            if "specific_humidity" in var.name:
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
def compare_BCNBC(Ob_Type = 'all'):
    ''' Run the BC vs NBC comparison plot '''
    ''' Ob_Type = all, ship - default = all '''

    version = "_renorm19812010_anomalies"
    #OLD: version = "_anomalies"
    DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/"
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

            if "specific_humidity" in var.name:
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
def compare_BCtype(Ob_Type = 'all'):
    ''' Run the BC types total, scn and hgt comparison plot '''
    ''' Ob_Type = 'all'. 'ship' - default = all '''

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

                for correction in ["NBC", "BClocal", "BClocalHGT", "BClocalINST"]:
		
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

                    label = "{}".format(correction)
                    if correction == "BClocal":
                        if time_res == "annual":
                            color = "black" #"DarkRed"
                        else:
                            color = "black" #"r"
                    elif correction == "BClocalHGT":
                        color = "darkorange" #"k"
                    elif correction == "BClocalINST":
                        color = "darkblue" #"k"
                    elif correction == "BClocalHGT":
                        color = "darkorange" #"k"
                    elif correction == "NBC":
                        color = "grey" #"k"
                    
                    if time_res == "annual":
                        to_plot += [PlotData(var.name, y, t, label, color, zorder, lw)]
                    else:
                        to_plot += [PlotData(var.name, y, t, "", color, zorder, lw)]

        
            title = "{} - {} - {}".format(" ".join([s.capitalize() for s in var.name.split("_")]), period, "QC")

            if "specific_humidity" in var.name:
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
def compare_PTs(Plot_Type = 'NBC'):
    ''' Run the platform (ship vs all) comparison plot '''
    ''' Plot_Type = 'NBC'. 'BClocal' - default = NBC  '''

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
                        color = "red" #"DarkRed"
                    elif Ob_Type == "all":
                        color = "black" #"k"
                    
                    if time_res == "annual":
                        to_plot += [PlotData(var.name, y, t, label, color, zorder, lw)]
                    else:
                        to_plot += [PlotData(var.name, y, t, "", color, zorder, lw)]

        
            title = "{} - {} - {}".format(" ".join([s.capitalize() for s in var.name.split("_")]), period, correction)

            if "specific_humidity" in var.name:
                nocs_m, nocs_a = read_nocs()
                to_plot += [nocs_m, nocs_a]

            do_plot(to_plot, title, "{}_{}_{}_ShipAll.png".format(var.name, period,Plot_Type))
