#!/usr/local/sci/bin/python2.7
#*****************************
#
# apply 5x5 climatology to 5x5 monthly fields
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
Takes annual 5x5 monthly fields and makes a pentad climatology over 1981-2010 (default).

Can work with 5x5 monthly fields created from daily or monthly data and using relaxed or strict completeness
settings according to commandline switches.  

-----------------------
LIST OF MODULES
-----------------------
utils.py

-----------------------
DATA
-----------------------
Input data and output data stored in:
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS2/

Requires 5x5 monthly grids - either calculated from daily or monthly data

-----------------------
HOW TO RUN THE CODE
-----------------------
python2.7 make_5x5monthly_climatology.py --suffix relax --period day --daily

python2.7 make_5x5monthly_climatology.py --help 
will show all options

-----------------------
OUTPUT
-----------------------
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS2/

Plots to appear in 
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/PLOTS2/

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
import argparse
import matplotlib
matplotlib.use('Agg') 
import calendar
import netCDF4 as ncdf
import copy

import utils
import set_paths_and_vars
defaults = set_paths_and_vars.set()


OBS_ORDER = utils.make_MetVars(defaults.mdi, multiplier = False) 

# what size grid (lat/lon)
DELTA_LAT = 5
DELTA_LON = 5

# set up the grid
grid_lats = np.arange(-90 + DELTA_LAT, 90 + DELTA_LAT, DELTA_LAT)
grid_lons = np.arange(-180 + DELTA_LAT, 180 + DELTA_LON, DELTA_LON)


# subroutine start
#*********************************************
def apply_climatology(suffix = "relax", period = "both", daily = False, doQC = False, doBC = False):
    '''
    Apply monthly 5x5 climatology

    :param str suffix: "relax" or "strict" criteria
    :param str period: which period to do day/night/both?
    :param bool daily: run in 1x1 daily --> 5x5 monthly data
    :param bool doQC: incorporate the QC flags or not
    :param bool doBC: work on the bias corrected data

    :returns:
    '''
    settings = set_paths_and_vars.set(doBC = doBC, doQC = doQC)


    if suffix == "relax":
        N_YEARS_PRESENT = 10 # number of years present to calculate climatology
    elif suffix == "strict":
        N_YEARS_PRESENT = 15 # number of years present to calculate climatology


    print "Do daily: {}".format(daily)

    # set filenames
    if daily:
        climfilename = settings.DATA_LOCATION + "{}_5x5_monthly_climatology_from_daily_{}_{}.nc".format(settings.OUTROOT, period, suffix)
        obsfilename = settings.DATA_LOCATION + "{}_5x5_monthly_from_daily_{}_{}.nc".format(settings.OUTROOT, period, suffix)
    else:
        climfilename = settings.DATA_LOCATION + "{}_5x5_monthly_climatology_{}_{}.nc".format(settings.OUTROOT, period, suffix)
        obsfilename = settings.DATA_LOCATION + "{}_5x5_monthly_from_daily_{}_{}.nc".format(settings.OUTROOT, period, suffix)

    # load netCDF files
    clim_file = ncdf.Dataset(climfilename,'r', format='NETCDF4')
    obs_file = ncdf.Dataset(obsfilename,'r', format='NETCDF4')

    # simple - use a list and append
    all_anoms = []

    # spin through all variables
    for v, var in enumerate(OBS_ORDER):
        print var.name
        
        obs = obs_file.variables[var.name][:]
        clims = clim_file.variables[var.name][:]

        anomalies = obs - np.tile(clims, (obs.shape[0]/12.,1,1)) # make to same shape

        all_anoms += [anomalies]

    # finished - convert list to array
    all_anoms = np.ma.array(all_anoms)

    # extract remaining information to copy across
    n_obs = obs_file.variables["n_obs"][:]
    n_grids = obs_file.variables["n_grids"][:]

    # set up the time object and axis
    intimes = obs_file.variables["time"]
    times = utils.TimeVar("time", intimes.long_name, intimes.units, intimes.standard_name)
    times.data = intimes[:]

    # write file
    if daily:
        out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_anomalies_from_daily_{}_{}.nc".format(period, suffix)
    else:
        out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_anomalies_{}_{}.nc".format(period, suffix)

    if period == "both":
        utils.netcdf_write(out_filename, all_anoms, n_grids, n_obs, OBS_ORDER, grid_lats[::-1], grid_lons, times, frequency = "Y")
    else:
        utils.netcdf_write(out_filename, all_anoms, n_grids, n_obs, OBS_ORDER, grid_lats, grid_lons, times, frequency = "Y")

    return # apply_climatology


#************************************************************************
if __name__=="__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--suffix', dest='suffix', action='store', default = "relax",
                        help='"relax" or "strict" completeness, default = relax')
    parser.add_argument('--period', dest='period', action='store', default = "both",
                        help='which period to run for (day/night/all), default = "both"')
    parser.add_argument('--daily', dest='daily', action='store_true', default = False,
                        help='run on 1x1 daily --> 5x5 monthly data (rather than 1x1 monthly --> 5x5 monthly), default = False')
    parser.add_argument('--doQC', dest='doQC', action='store_true', default = False,
                        help='process the QC information, default = False')
    parser.add_argument('--doBC', dest='doBC', action='store_true', default = False,
                        help='process the bias corrected data, default = False')
    args = parser.parse_args()


    apply_climatology(suffix = str(args.suffix), period = str(args.period), daily = args.daily, doQC = args.doQC, doBC = args.doBC)

# END
# ************************************************************************

