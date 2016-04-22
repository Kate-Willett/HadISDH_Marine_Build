#!/usr/local/sci/bin/python2.7
#*****************************
#
# Take monthly merged files and output global average timeseries
#
#
#************************************************************************
'''
Author: Robert Dunn
Created: March 2016
Last update: 12 April 2016
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
python2.7 timeseries_comparison_plots.py

-----------------------
OUTPUT
-----------------------
Plots to appear in 
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/PLOTS_comparison/

-----------------------
VERSION/RELEASE NOTES
-----------------------

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

    texty = 0.85
    for d in data:
        if d.label == "":
            # if no label (e.g. monthly)
            plt.plot(d.t, d.y.data, c = d.c, zorder = d.z, lw = d.lw)
               
        else:
            plt.plot(d.t, d.y.data, label = d.label, c = d.c, zorder = d.z, lw = d.lw)

            # annual - also want MPW slope
            slope, lower, upper = median_pairwise_slopes(d.t, d.y.data, d.y.mdi, sigma = 1.)
            slope_error = np.mean([(upper-slope), (slope-lower)])

            slope_years, slope_values = mpw_plot_points(slope, d.t, d.y.data)
            plt.plot(slope_years, slope_values, c = d.c, lw = 1)

            plt.text(0.03, texty, "{:6.2f} +/- {:6.3f} {} 10 yr".format(10.*slope, 10.*slope_error, d.y.units)+r'$^{-1}$', transform = ax.transAxes, color = d.c)
            texty -= 0.05

    plt.ylabel(d.y.units)

    plt.title(title)
    plt.legend()
    plt.savefig(PLOT_LOCATION + outname)

    return # do_plot

#***************************************
def get_data(filename):
    """
    Read in the netCDF data

    :param str filename: file to read in data from
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

    monthly = PlotData("", y, t, "", 'g', 1, 1)

    # annual

    nocs = nocs.reshape(-1, 12)
    nocs = np.mean(nocs, axis = 1)
    y = utils.set_MetVar_attributes("specific_humidity", "Specific humidity", "specific humidity", "g/kg", mdi, np.dtype('float64'), 8, multiplier = False)
    y.data = nocs

    t = t.reshape(-1, 12)
    t = t[:, 6]

    annual = PlotData("", y, t, "NOCS-q", 'DarkGreen', 10, 2)
    
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


mdi = -1.e30
OBS_ORDER = utils.make_MetVars(mdi, multiplier = False)
GRID_LOCATION = {"NBC" : "GRIDS3", "BC" : "GRIDS_BC", "QC" : "GRIDS3", "noQC" : "GRIDS_noQC"}
PLOT_LOCATION = "/project/hadobs2/hadisdh/marine/PLOTS_compare/"


suffix = "relax"

#***************************************
#***************************************
# Day versus Night
version = "_anomalies"
DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/"
correction = "NBC"

for v, var in enumerate(OBS_ORDER):
    if "anomalies" not in var.name:
        continue

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
                color = "lime"
            elif period == "day":
                color = "r"
            elif period == "night":
                color = "c"

            filename = "{}/{}/ERAclim{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 

            y, t = get_data(filename)

            label = "{}".format(period)

            if time_res == "annual":
                to_plot += [PlotData("", y, t, label, color, zorder, lw)]
            else:
                to_plot += [PlotData("", y, t, "", color, zorder, lw)]
                
    title = "{} - {}".format(" ".join([s.capitalize() for s in var.name.split("_")]), correction)

    if "specific_humidity" in var.name:
        nocs_m, nocs_a = read_nocs()
        to_plot += [nocs_m, nocs_a]
    do_plot(to_plot, title, "{}_{}_day-night-both.png".format(var.name, correction))


#***************************************
#***************************************
# QC vs noQC
version = "_anomalies"
DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/"
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

                filename = "{}/{}/ERAclim{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[qc], correction, version, period, suffix, time_res) 

                y, t = get_data(filename)

                label = "{}".format(qc)
                if qc == "QC":
                    if time_res == "annual":
                        color = "DarkRed"
                    else:
                        color = "r"
                elif qc == "noQC":
                    color = "k"
                    
                if time_res == "annual":
                    to_plot += [PlotData("", y, t, label, color, zorder, lw)]
                else:
                    to_plot += [PlotData("", y, t, "", color, zorder, lw)]

        
        title = "{} - {} - {}".format(" ".join([s.capitalize() for s in var.name.split("_")]), correction, period)

        if "specific_humidity" in var.name:
            nocs_m, nocs_a = read_nocs()
            to_plot += [nocs_m, nocs_a]
        do_plot(to_plot, title, "{}_{}_{}_QC-noQC.png".format(var.name, period, correction))


#***************************************
#***************************************
# BC vs NBC
version = "_anomalies"
DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/"

for v, var in enumerate(OBS_ORDER):
    if "anomalies" not in var.name:
        continue

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

            for correction in ["BC", "NBC"]:

                filename = "{}/{}/ERAclim{}_5x5_monthly{}_from_daily_{}_{}_ts_{}.nc".format(DATA_LOCATION, GRID_LOCATION[correction], correction, version, period, suffix, time_res) 

                y, t = get_data(filename)

                label = "{}".format(correction)
                if correction == "NBC":
                    if time_res == "annual":
                        color = "DarkRed"
                    else:
                        color = "r"
                else:
                    color = "k"
                    
                if time_res == "annual":
                    to_plot += [PlotData("", y, t, label, color, zorder, lw)]
                else:
                    to_plot += [PlotData("", y, t, "", color, zorder, lw)]

        
        title = "{} - {} - {}".format(" ".join([s.capitalize() for s in var.name.split("_")]), period, "QC")

        if "specific_humidity" in var.name:
            nocs_m, nocs_a = read_nocs()
            to_plot += [nocs_m, nocs_a]

        do_plot(to_plot, title, "{}_{}_BC-NBC.png".format(var.name, period))


