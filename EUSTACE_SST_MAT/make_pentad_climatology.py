#!/usr/local/sci/bin/python2.7
#*****************************
#
# calculate climatology from pentads
#
# KW Edited this to ignore anomalies
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
Takes annual pentad fields and makes a pentad climatology over 1981-2010 (default).

Can work with pentads created from daily or 3hrly data and using relaxed or strict completeness
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

Requires pentad grids - either calculated from daily or 3hrly data.

-----------------------
HOW TO RUN THE CODE
-----------------------
python2.7 make_pentad_climatology.py --suffix relax --period day --do3hr

python2.7 make_pentad_climatology.py --help 
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

import utils
from set_paths_and_vars import *

OBS_ORDER = utils.make_MetVars(mdi, multiplier = False)
# KW make OBS_ORDER only the actual variables - remove anomalies
NEWOBS_ORDER = []
for v, var in enumerate(OBS_ORDER):
    if "anomalies" not in var.name:
        NEWOBS_ORDER.append(var)
del OBS_ORDER
OBS_ORDER = np.copy(NEWOBS_ORDER)
del NEWOBS_ORDER     

# what size grid (lat/lon)
DELTA_LAT = 1
DELTA_LON = 1

# set up the grid
grid_lats = np.arange(-90 + DELTA_LAT, 90 + DELTA_LAT, DELTA_LAT)
grid_lons = np.arange(-180 + DELTA_LAT, 180 + DELTA_LON, DELTA_LON)

# subroutine start
#*********************************************
def calculate_climatology(suffix = "relax", start_year = 1981, end_year = 2010, period = "both", do3hr = False):
    '''
    Make 1x1 pentad climatology

    :param str suffix: "relax" or "strict" criteria
    :param int start_year: start year to process
    :param int end_year: end year to process
    :param str period: which period to do day/night/both?
    :param bool do3hr: run on 3hr --> pentad data

    :returns:
    '''
    if suffix == "relax":
        N_YEARS_PRESENT = 10 # number of years present to calculate climatology
    elif suffix == "strict":
        N_YEARS_PRESENT = 15 # number of years present to calculate climatology


    print "Do 3hrly: {}".format(do3hr)

    N_YEARS = end_year - start_year + 1

    # read in each variable - memory issues

    all_clims = np.ma.zeros([len(OBS_ORDER), 73, len(grid_lats), len(grid_lons)])
    # KW - why set up as np.ones?
    all_clims.mask = np.zeros([len(OBS_ORDER), 73, len(grid_lats), len(grid_lons)])

    all_stds = np.ma.zeros([len(OBS_ORDER), 73, len(grid_lats), len(grid_lons)])
    all_stds.mask = np.zeros([len(OBS_ORDER), 73, len(grid_lats), len(grid_lons)])
    
    # KW no mask??? I've set one with fill_value as -1 - should the mask be .zeros or .ones though?
    all_n_obs = np.ma.zeros([N_YEARS, 73, len(grid_lats), len(grid_lons)])
    all_n_obs.mask = np.zeros([N_YEARS, 73, len(grid_lats), len(grid_lons)])
    all_n_obs.fill_value = -1
    
    for v, var in enumerate(OBS_ORDER):
	    
        print var.name

        # number of pentads = 365/5 = 73
        # set up empty data array
        all_pentads = np.ma.zeros([N_YEARS, 73, len(grid_lats), len(grid_lons)])
	# sets up a mask of 'False' = not masked!
        all_pentads.mask = np.zeros([N_YEARS, 73, len(grid_lats), len(grid_lons)])
        all_pentads.fill_value = mdi

        # read in relevant years
        for y, year in enumerate(np.arange(start_year, end_year + 1)): 

            print year

            if do3hr:
                filename = DATA_LOCATION + "{}_1x1_pentad_from_3hrly_{}_{}_{}.nc".format(OUTROOT, year, period, suffix)
 
            else:
                filename = DATA_LOCATION + "{}_1x1_pentad_{}_{}_{}.nc".format(OUTROOT, year, period, suffix)

            ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

            all_pentads[y, :, :, :] = ncdf_file.variables[var.name][:]

            if v == 0:
                all_n_obs[y, :, :, :] = ncdf_file.variables["n_obs"][:]

        # years x pentads x lats x lons
        n_grids = np.ma.count(all_pentads, axis = 0)

        # collapse down the years
        if doMedian:
            all_clims[v, :, :, :] = utils.bn_median(all_pentads, axis = 0)
        else:
            all_clims[v, :, :, :] = np.ma.mean(all_pentads, axis = 0)

        all_stds[v, :, :, :] = np.ma.std(all_pentads, axis = 0)

        # mask where fewer than 50% of years have data
        locs = np.ma.where(n_grids < N_YEARS_PRESENT)
        all_clims[v, :, :, :].mask[locs] = True
        # KW should probably mask stdev too - although unmasked it does show the potential coverage
        all_stds[v, :, :, :].mask[locs] = True

        if plots and v == 0:
            import matplotlib.pyplot as plt
            plt.clf()
            plt.hist(n_grids.reshape(-1), bins = np.arange(-1,32), align = "left", log = True, rwidth=0.5)
            plt.axvline(x = N_YEARS_PRESENT-0.5, color = "r")       
            plt.title("Number of years present in each pentad")
            plt.xlabel("Number of years (max = 30)")
            plt.ylabel("Frequency (log scale)")
            plt.savefig(PLOT_LOCATION + "pentad_clims_n_years_{}_{}_{}.png".format(year, period, suffix))

            
    # now process number of observations (KW all_n_obs wasn't a masked array - so have set it up as one - BUT not really convinced this 
    # is working as it should. No import numpy.ma?        
    all_obs = np.ma.sum(all_n_obs, axis = 0)

    # set up time array
    times = utils.TimeVar("time", "time since 1/1/{} in days".format(1), "days", "time")
    times.data = np.arange(0, 73) * 5

    # write files
    if do3hr:
        out_filename = DATA_LOCATION + OUTROOT + "_1x1_pentad_climatology_from_3hrly_{}_{}.nc".format(period, suffix)
    else:
        out_filename = DATA_LOCATION + OUTROOT + "_1x1_pentad_climatology_{}_{}.nc".format(period, suffix)

    utils.netcdf_write(out_filename, all_clims, n_grids, all_obs, OBS_ORDER, grid_lats, grid_lons, times, frequency = "P")

    if do3hr:
        out_filename = DATA_LOCATION + OUTROOT + "_1x1_pentad_stdev_from_3hrly_{}_{}.nc".format(period, suffix)
    else:
       out_filename = DATA_LOCATION + OUTROOT + "_1x1_pentad_stdev_{}_{}.nc".format(period, suffix)

    utils.netcdf_write(out_filename, all_stds, n_grids, all_obs, OBS_ORDER, grid_lats, grid_lons, times, frequency = "P")

    # test distribution of obs with grid boxes
    if do3hr:
        outfile = file(OUTROOT + "_1x1_pentad_climatology_from_3hrly_{}_{}.txt".format(period, suffix), "w")
    else:
        outfile = file(OUTROOT + "_1x1_pentad_climatology_{}_{}.txt".format(period, suffix), "w")

    utils.boxes_with_n_obs(outfile, all_obs, all_clims[0], N_YEARS_PRESENT)

    return # calculate_climatology

#************************************************************************
if __name__=="__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--suffix', dest='suffix', action='store', default = "relax",
                        help='"relax" or "strict" completeness, default = relax')
    parser.add_argument('--start_year', dest='start_year', action='store', default = 1981,
                        help='which year to start run, default = 1981')
    parser.add_argument('--end_year', dest='end_year', action='store', default = 2010,
                        help='which year to end run, default = 2010')
    parser.add_argument('--period', dest='period', action='store', default = "both",
                        help='which period to run for (day/night/all), default = "both"')
    parser.add_argument('--do3hr', dest='do3hr', action='store_true', default = False,
                        help='run on 3hr --> pentad data (rather than daily --> pentad), default = False')
    args = parser.parse_args()


    calculate_climatology(suffix = str(args.suffix), start_year = int(args.start_year), end_year = int(args.end_year), period = str(args.period), do3hr = args.do3hr)

# END
# ************************************************************************
