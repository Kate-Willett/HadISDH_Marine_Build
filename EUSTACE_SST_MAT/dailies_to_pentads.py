#!/usr/local/sci/bin/python2.7
#*****************************
#
# convert dailies to pentads
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
Takes daily data and creates pentads.  

-----------------------
LIST OF MODULES
-----------------------
utils.py

-----------------------
DATA
-----------------------
Input data and output data stored in:
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS2/

Requires daily grids.

-----------------------
HOW TO RUN THE CODE
-----------------------
python2.7 dailies_to_pentads.py --suffix relax --period day --start_year YYYY --end_year YYYY

python2.7 dailies_to_pentads.py --help 
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
import gc

import utils
import set_paths_and_vars
defaults = set_paths_and_vars.set()


N_OBS = 1 # data on at least one day of the pentad

# what size grid (lat/lon)
DELTA_LAT = 1
DELTA_LON = 1

# set up the grid
grid_lats = np.arange(-90 + DELTA_LAT, 90 + DELTA_LAT, DELTA_LAT)
grid_lons = np.arange(-180 + DELTA_LAT, 180 + DELTA_LON, DELTA_LON)

#************************************************************************
def do_conversion(start_year = defaults.START_YEAR, end_year = defaults.END_YEAR, period = "all", doBC = False, doQC = True):
    '''
    Convert dailies to pentads 1x1

    :param int start_year: start year to process
    :param int end_year: end year to process
    :param str period: which period to do day/night/all?
    :param bool doBC: work on the bias corrected data
    :param bool doQC: incorporate the QC flags or not


    :returns:
    '''
    settings = set_paths_and_vars.set(doBC = doBC, doQC = doQC)

    OBS_ORDER = utils.make_MetVars(settings.mdi, multiplier = False)

    for year in np.arange(start_year, end_year + 1): 

        # set up empty data array
        all_dailies = np.ma.zeros([len(OBS_ORDER), utils.days_in_year(year), len(grid_lats), len(grid_lons)])
        all_dailies.mask = np.zeros([len(OBS_ORDER), utils.days_in_year(year), len(grid_lats), len(grid_lons)])
        all_dailies.fill_value = settings.mdi

        all_n_obs = np.zeros([utils.days_in_year(year), len(grid_lats), len(grid_lons)])

        year_start = dt.datetime(year, 1, 1, 0, 0)

        for month in np.arange(12) + 1:
            print year, month

            month_start = utils.day_of_year(year, month)
            month_end = month_start + calendar.monthrange(year, month)[1]

            filename = "{}/{}_1x1_daily_{}{:02d}_{}.nc".format(settings.DATA_LOCATION, settings.OUTROOT, year, month, period)

            ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

            for v, var in enumerate(OBS_ORDER):

                if month == 12:
                    # run to end of year if december
                    all_dailies[v, month_start:, :, :] = ncdf_file.variables[var.name][:]
                else:
                    all_dailies[v, month_start:month_end, :, :] = ncdf_file.variables[var.name][:]

            # now get number of observations
            if month == 12:
                all_n_obs[month_start:, :, :] = ncdf_file.variables["n_obs"][:]
            else:
                all_n_obs[month_start:month_end, :, :] = ncdf_file.variables["n_obs"][:]


        if calendar.isleap(year):
            assert all_dailies.shape[1] == 366

            # extract 6-day pentad
            incl_feb29th = all_dailies[:, 55:61, :, :]

            # remove the data of Feb 29th from array
            # np.ma.delete doesn't exist, so have to copy mask separately
            mask = all_dailies.mask
            all_dailies = np.delete(all_dailies, 59, 1) 
            mask = np.delete(mask, 59, 1)
            all_dailies = np.ma.array(all_dailies, mask = mask)
            del mask

            # number of observations
            incl_feb29th_n_obs = all_n_obs[55:61, :, :]
            all_n_obs = np.delete(all_n_obs, 59, 0)         

        else:
            assert all_dailies.shape[1] == 365

        shape = all_dailies.shape
        all_dailies = all_dailies.reshape(shape[0], -1, 5, shape[-2], shape[-1])

        n_days_per_pentad = np.ma.count(all_dailies, axis = 2) 

        if settings.doMedian:
            pentad_grid = utils.bn_median(all_dailies, axis = 2)
        else:
            pentad_grid = np.ma.mean(all_dailies, axis = 2)

        # clear up memory
        del all_dailies
        gc.collect()

        all_n_obs = all_n_obs.reshape(-1, 5, shape[-2], shape[-1])
        all_n_obs = np.sum(all_n_obs, axis = 1)

        pentad_grid.mask[n_days_per_pentad < N_OBS] = True # mask where fewer than 2 days have values # KW THIS IS ACTUALLY 2 - WHICH I THINK IS GOOD


        # the pentad containing feb 29th is the 11th in the year
        if calendar.isleap(year):
            #  overwrite this with the me(di)an of a 6-day pentad
            if settings.doMedian:
                pentad_grid[:, 11, :, :] = utils.bn_median(incl_feb29th, axis = 1)
            else:
                pentad_grid[:, 11, :, :] = np.ma.mean(incl_feb29th, axis = 1)


            feb_n_days_per_pentad = np.ma.count(incl_feb29th, axis = 1)
            pentad_grid.mask[:, 11, :, :][feb_n_days_per_pentad < N_OBS] = True 
            n_days_per_pentad[:, 11, :, :] = feb_n_days_per_pentad

            all_n_obs[11, :, :] = np.sum(incl_feb29th_n_obs, axis = 0)

            print "processed Feb 29th"
                
        times = utils.TimeVar("time", "time since 1/1/{} in hours".format(year), "hours", "time")
        times.data = np.arange(0, pentad_grid.shape[1]) * 5 * 24

        out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_pentad_{}_{}.nc".format(year, period)
            
        utils.netcdf_write(out_filename, pentad_grid, n_days_per_pentad[0], all_n_obs, OBS_ORDER, grid_lats, grid_lons, times, frequency = "P")

        del pentad_grid
        del all_n_obs
        del n_days_per_pentad
        gc.collect()

    return # do_conversion
    
#************************************************************************
if __name__=="__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_year', dest='start_year', action='store', default = defaults.START_YEAR,
                        help='which year to start run, default = 1973')
    parser.add_argument('--end_year', dest='end_year', action='store', default = defaults.END_YEAR,
                        help='which year to end run, default = present')
    parser.add_argument('--period', dest='period', action='store', default = "all",
                        help='which period to run for (day/night/all), default = "all"')
    args = parser.parse_args()


    print "relax/strict not yet coded up - exiting"

    sys.exit()

    do_conversion(start_year = int(args.start_year), end_year = int(args.end_year), period = str(args.period))

# END
# ************************************************************************
