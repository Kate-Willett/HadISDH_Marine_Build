#!/usr/local/sci/bin/python2.7
#*****************************
#
# calculate climatology from pentads
#
#
#************************************************************************

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


doMedian = False

# Constants in CAPS
OUTROOT = "ERAclimNBC"

DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS/"
PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS/"

mdi = -1.e30
OBS_ORDER = utils.make_MetVars(mdi, multiplier = False)

# what size grid (lat/lon)
DELTA_LAT = 1
DELTA_LON = 1

# set up the grid
grid_lats = np.arange(-90 + DELTA_LAT, 90 + DELTA_LAT, DELTA_LAT)
grid_lons = np.arange(-180 + DELTA_LAT, 180 + DELTA_LON, DELTA_LON)



# subroutine start
#*********************************************
def calculate_climatology(start_year = 1981, end_year = 2010, period = "both", do3hr = False):
    '''
    Convert dailies to pentads 1x1

    :param int start_year: start year to process
    :param int end_year: end year to process
    :param str period: which period to do day/night/both?
    :param bool do3hr: run on 3hr --> pentad data

    :returns:
    '''
    print "Do 3hrly: {}".format(do3hr)

    N_YEARS = end_year - start_year + 1

    # read in each variable - memory issues

    all_clims = np.ma.zeros([len(OBS_ORDER), 73, len(grid_lats), len(grid_lons)])
    all_clims.mask = np.ones([len(OBS_ORDER), 73, len(grid_lats), len(grid_lons)])

    all_stds = np.ma.zeros([len(OBS_ORDER), 73, len(grid_lats), len(grid_lons)])
    all_stds.mask = np.ones([len(OBS_ORDER), 73, len(grid_lats), len(grid_lons)])

    for v, var in enumerate(OBS_ORDER):

        print var.name

        # number of pentads = 365/5 = 73
        # set up empty data array
        all_pentads = np.ma.zeros([N_YEARS, 73, len(grid_lats), len(grid_lons)])
        all_pentads.mask = np.ones([N_YEARS, 73, len(grid_lats), len(grid_lons)])
        all_pentads.fill_value = mdi

        # read in relevant years
        for y, year in enumerate(np.arange(start_year, end_year + 1)): 

            print year

            if period == "both":
                if do3hr:
                    filename = DATA_LOCATION + "{}_1x1_pentad_from_3hrly_{}.nc".format(OUTROOT, year)
                else:
                    filename = DATA_LOCATION + "{}_1x1_pentad_{}.nc".format(OUTROOT, year)
            else:
                if do3hr:
                    filename = DATA_LOCATION + "{}_1x1_pentad_from_3hrly_{}_{}.nc".format(OUTROOT, year, period)
                else:
                    filename = DATA_LOCATION + "{}_1x1_pentad_{}_{}.nc".format(OUTROOT, year, period)

            ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

            all_pentads[y, :, :, :] = ncdf_file.variables[var.name][:]


        # vars x years x pentads x lats x lons
        n_obs = np.ma.count(all_pentads, axis = 0)

        # collapse down the years
        if doMedian:
            all_clims[v, :, :, :] = utils.bn_median(all_pentads, axis = 0)
        else:
            all_clims[v, :, :, :] = np.ma.mean(all_pentads, axis = 0)

        all_stds[v, :, :, :] = np.ma.std(all_pentads, axis = 0)

        # mask where fewer than 50% of years have data
#        locs = np.ma.where(n_obs < N_YEARS*0.5)
#        all_clims[v, :, :, :].mask[locs] = True

    # set up time array
    times = utils.TimeVar("time", "time since 1/1/{} in days".format(1), "days", "time")
    times.data = np.arange(0, 73) * 5

    # write files
    if period == "both":
        if do3hr:
            out_filename = DATA_LOCATION + OUTROOT + "_1x1_pentad_climatology_from_3hrly.nc"
        else:
            out_filename = DATA_LOCATION + OUTROOT + "_1x1_pentad_climatology.nc"
    else:
        if do3hr:
            out_filename = DATA_LOCATION + OUTROOT + "_1x1_pentad_climatology_from_3hrly_{}.nc".format(period)
        else:
            out_filename = DATA_LOCATION + OUTROOT + "_1x1_pentad_climatology_{}.nc".format(period)

    utils.netcdf_write(out_filename, all_clims, OBS_ORDER, grid_lats, grid_lons, times, frequency = "P")

    if period == "both":
        if do3hr:
            out_filename = DATA_LOCATION + OUTROOT + "_1x1_pentad_stdev_from_3hrly.nc"
        else:
            out_filename = DATA_LOCATION + OUTROOT + "_1x1_pentad_stdev.nc"
    else:
        if do3hr:
            out_filename = DATA_LOCATION + OUTROOT + "_1x1_pentad_stdev_from_3hrly_{}.nc".format(period)
        else:
            out_filename = DATA_LOCATION + OUTROOT + "_1x1_pentad_stdev_{}.nc".format(period)

    utils.netcdf_write(out_filename, all_stds, OBS_ORDER, grid_lats, grid_lons, times, frequency = "P")

    return # calculate_climatology

#************************************************************************
if __name__=="__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_year', dest='start_year', action='store', default = 1981,
                        help='which year to start run, default = 1981')
    parser.add_argument('--end_year', dest='end_year', action='store', default = 2010,
                        help='which year to end run, default = 2010')
    parser.add_argument('--period', dest='period', action='store', default = "both",
                        help='which period to run for (day/night/both), default = "both"')
    parser.add_argument('--do3hr', dest='do3hr', action='store_true', default = "False",
                        help='run on 3hr --> pentad data (rather than daily --> pentad), default = False')
    args = parser.parse_args()


    calculate_climatology(start_year = int(args.start_year), end_year = int(args.end_year), period = str(args.period), do3hr = args.do3hr)

# 
