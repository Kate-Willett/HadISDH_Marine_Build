#!/usr/local/sci/bin/python2.7
#*****************************
#
# convert to complete dataset files (pentad and monthlies)
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
import gc

import utils


#Constants in CAPS
OUTROOT = "ERAclimNBC"

DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS/"
PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS/"

START_YEAR = 1973
END_YEAR = dt.datetime.now().year - 1

mdi = -1.e30


# need to merge the pentads (1x1) and the monthlies (5x5)

#************************************************************************
def combine_files(start_year = START_YEAR, end_year = END_YEAR, start_month = 1, end_month = 12, period = "both"):

    OBS_ORDER = utils.make_MetVars(mdi, multiplier = False)
    '''
    Combine the files, first the pentads 1x1, then the monthlies 5x5

    :param int start_year: start year to process
    :param int end_year: end year to process
    :param int start_month: start month to process
    :param int end_month: end month to process
    :param str period: which period to do day/night/both?

    :returns:
    '''

    # pentads

    # set up the grids
    DELTA=1
    grid_lats = np.arange(-90+DELTA, 90+DELTA, DELTA)
    grid_lons = np.arange(-180+DELTA, 180+DELTA, DELTA)

    Nyears = end_year - start_year + 1
 
    # read in each variable - memory issues
    for v, var in enumerate(OBS_ORDER):

        print var.name
        
        all_pentads = np.ma.zeros((1, Nyears, 73, len(grid_lats), len(grid_lons)))
        all_pentads.mask = np.ones((1, Nyears, 73, len(grid_lats), len(grid_lons)))
        all_pentads.fill_value = mdi

        for y, year in enumerate(np.arange(start_year, end_year + 1)):

            if period == "both":
                filename = DATA_LOCATION + "{}_1x1_pentad_{}.nc".format(OUTROOT, year)
                # filename = DATA_LOCATION + "{}_1x1_pentad_from_3hrly_{}.nc".format(OUTROOT, year)
            else:
                filename = DATA_LOCATION + "{}_1x1_pentad_{}_{}.nc".format(OUTROOT, year, period)
                # filename = DATA_LOCATION + "{}_1x1_pentad_from_3hrly_{}_{}.nc".format(OUTROOT, year, perio

            ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

            time = ncdf_file.variables["time"]

            try:
                assert time.long_name == "time since 1/1/{} in hours".format(year)

            except AssertionError:
                print "time units are not as expected."
                print "    expected time since 1/1/{} in hours".format(year)
                print "    got {}".format(time.long_name)
                sys.exit()

            all_pentads[0, y, :, :, :] = ncdf_file.variables[var.name][:]

            ncdf_file.close()
            print year

        all_pentads = all_pentads.reshape(1, -1, len(grid_lats), len(grid_lons))

        # sort the times
        times = utils.TimeVar("time", "time since 1/1/1973 in months", "months", "time")
        times.data = np.arange(all_pentads.shape[1])

        # and write file
        if period == "both":
            DATA_LOCATION + OUTROOT + "_1x1_pentads_{}.nc".format(var.name)
        else:
            DATA_LOCATION + OUTROOT + "_1x1_pentads_{}_{}.nc".format(var.name, period)

        utils.netcdf_write(out_filename, all_pentads, OBS_ORDER, grid_lats, grid_lons, times, frequency = "P", single = var)


    # Reset the data holding arrays and objects

    del OBS_ORDER
    gc.collect()

    OBS_ORDER = utils.make_MetVars(mdi, multiplier = False)

    #*****************************
    # monthlies
    for y, year in enumerate(np.arange(start_year, end_year + 1)): 

        for month in np.arange(start_month, end_month + 1):

            if period == "both":
                filename = DATA_LOCATION + "{}_5x5_monthly_{}{:02d}.nc".format(OUTROOT, year, month)
            else:
                filename = DATA_LOCATION + "{}_5x5_monthly_{}{:02d}_{}.nc".format(OUTROOT, year, month, period)

            ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

            time = ncdf_file.variables["time"]

            try:
                assert time.long_name == "time since 1/{}/{} in hours".format(month, year)

            except AssertionError:
                print "time units are not as expected."
                print "    expected time since 1/{}/{} in hours".format(month, year)
                print "    got {}".format(time.long_name)
                sys.exit()

            for var in OBS_ORDER:

                nc_var = ncdf_file.variables[var.name]

                try:
                    var.data = np.ma.append(var.data, nc_var[:], axis = 0)

                except AttributeError:
                    var.data = nc_var[:]
                    var.data.fill_value = nc_var.missing_value


    # write out into big array for netCDF file
    all_data = np.ma.zeros((len(OBS_ORDER), var.data.shape[0], var.data.shape[1], var.data.shape[2]))
    all_data.mask = np.zeros((len(OBS_ORDER), var.data.shape[0], var.data.shape[1], var.data.shape[2]))

    for v, var in enumerate(OBS_ORDER):
        all_data[v, :, :, :] = var.data

    all_data.fill_value = var.data.fill_value
    
    # extra stuff for writing
    DELTA=5
    grid5_lats = np.arange(-90+DELTA, 90+DELTA, DELTA)
    grid5_lons = np.arange(-180+DELTA, 180+DELTA, DELTA)
    times = utils.TimeVar("time", "time since 1/1/{} in months".format(START_YEAR), "months", "time")
    times.data = np.arange(var.data.shape[0])

    # and write file
    if period == "both":
        out_filename = DATA_LOCATION + OUTROOT + "_5x5_monthly.nc"
    else:
        out_filename = DATA_LOCATION + OUTROOT + "_5x5_monthly_{}.nc".format(period)

    utils.netcdf_write(out_filename, all_data, OBS_ORDER, grid5_lats, grid5_lons, times, frequency = "Y")

    return # combine_files

#************************************************************************
if __name__=="__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_year', dest='start_year', action='store', default = START_YEAR,
                        help='which year to start run, default = 1973')
    parser.add_argument('--end_year', dest='end_year', action='store', default = END_YEAR,
                        help='which year to end run, default = present')
    parser.add_argument('--start_month', dest='start_month', action='store', default = 1,
                        help='which month to start run, default = 1')
    parser.add_argument('--end_month', dest='end_month', action='store', default = 12,
                        help='which month to end run, default = 12')
    parser.add_argument('--period', dest='period', action='store', default = "both",
                        help='which period to run for (day/night/both), default = "both"')
    args = parser.parse_args()


    combine_files(start_year = int(args.start_year), end_year = int(args.end_year), \
                    start_month = int(args.start_month), end_month = int(args.end_month), period = str(args.period))
