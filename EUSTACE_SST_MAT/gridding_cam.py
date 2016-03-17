#!/usr/local/sci/bin/python2.7
#*****************************
#
# general Python gridding script
#
#
#************************************************************************

import os
import datetime as dt
import numpy as np
import sys
import argparse
import matplotlib
import calendar
import matplotlib.pyplot as plt
import gc

import utils
import plot_qc_diagnostics
import MDS_basic_KATE as mds

plots = False
doQC = True
doMonthlies = True
doPentads = False

# Constants in CAPS
OUTROOT = "ERAclimNBC"

DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)
OUT_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS/"
PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS/"

# test settings
#OUT_LOCATION=""
#PLOT_LOCATION=""

START_YEAR = 1973
END_YEAR = dt.datetime.now().year - 1

mdi = -1.e30
OBS_ORDER = utils.make_MetVars(mdi)

# what size grid (lat/lon/hour)
DELTA_LAT = 1
DELTA_LON = 1
DELTA_HOUR = 3

# set up the grid
grid_lats = np.arange(-90, 90 + DELTA_LAT, DELTA_LAT)
grid_lons = np.arange(-180, 180 + DELTA_LON, DELTA_LON)

# flags to check on and values to allow through
these_flags = {"ATbud":0, "ATclim":0,"ATrep":0,"DPTbud":0,"DPTclim":0,"DPTssat":0,"DPTrep":0,"DPTrepsat":0}

# RD - adapted MDS_basic_Kate.py to allow this call
fields = mds.TheDelimiters


# spin through years and months to read files
for year in [1973]: # range(START_YEAR, END_YEAR):


    for month in [1]: # (range(12) + 1):

        grid_hours = np.arange(0, 24 * calendar.monthrange(year, month)[1], DELTA_HOUR)
        grid_hours = np.arange(0, 24 , DELTA_HOUR)


        # process the monthly file
        filename = "new_suite_{}{:02d}_{}.txt".format(year, month, OUTROOT)
        raw_platform_data, raw_obs, raw_meta, raw_qc = utils.read_qc_data(filename, DATA_LOCATION, fields)

        # extract observation details
        lats, lons, years, months, days, hours = utils.process_platform_obs(raw_platform_data)

        # test dates
        if not utils.check_date(years, year, "years", filename):
            sys.exit(1)
        if not utils.check_date(months, month, "months", filename):
            sys.exit(1)

        if plots:
            # plot the distribution of hours

            plt.clf()
            plt.hist(hours, np.arange(-100,2500,100))
            plt.ylabel("Number of observations")
            plt.xlabel("Hours")
            plt.xticks(np.arange(-300, 2700, 300))
            plt.savefig(PLOT_LCATION + "obs_distribution_{}{:02d}.png".format(year, month))

            
            # only for a few of the variables
            for variable in OBS_ORDER:
                if variable.name in ["dew_point_temperature", "specific_humidity", "relative_humidity", "dew_point_temperature_anomalies", "specific_humidity_anomalies", "relative_humidity_anomalies"]:

                    plot_qc_diagnostics.values_vs_lat(variable, lats, raw_obs[:, variable.column], raw_qc, PLOT_LCATION + "qc_actuals_{}_{}{:02d}.png".format(variable.name, year, month), multiplier = variable.multiplier)

            
        # QC sub-selection
        if doQC:
            print "Using {} as flags".format(these_flags)
            mask = utils.process_qc_flags(raw_qc, these_flags)

            complete_mask = np.zeros(raw_obs.shape)
            for i in range(raw_obs.shape[1]):
                complete_mask[:,i] = mask
            clean_data = np.ma.masked_array(raw_obs, complete_mask)

        else:
            clean_data = np.ma.masked_array(raw_obs, mask = np.zeros(raw_obs.shape))


        # discretise hours
        hours = utils.make_index(hours, DELTA_HOUR, multiplier = 100)

        # get the hours since start of month
        hours_since = ((days - 1) * 24) + (hours * DELTA_HOUR)

        # discretise lats/lons
        lat_index = utils.make_index(lats, DELTA_LAT, multiplier = 100)
        lon_index = utils.make_index(lons, DELTA_LON, multiplier = 100)

        lat_index += ((len(grid_lats)-1)/2) # and as -ve indices are unhelpful, roll by offsetting by most westward
        lon_index += ((len(grid_lons)-1)/2) #    or most southerly so that (0,0) is (-90,-180)

        # NOTE - ALWAYS GIVING TOP-RIGHT OF BOX TO GIVE < HARD LIMIT (as opposed to <=)
        # do the gridding
        this_month_grid = utils.grid_1by1_cam(clean_data, hours_since, lat_index, lon_index, grid_hours, grid_lats, grid_lons, OBS_ORDER, mdi)

        # have one month of gridded data.
        utils.netcdf_write(OUT_LOCATION + OUTROOT + "_1x1_3hr_{}_{:02d}.nc".format(year, month), \
                               this_month_grid, OBS_ORDER, grid_lats, grid_lons, grid_hours, year, month, frequency = "H")

        # now average over time
        # Dailies
        daily_hours = grid_hours.reshape(-1, 24/DELTA_HOUR)
        this_month_grid = this_month_grid.reshape(this_month_grid.shape[0], -1, 24/DELTA_HOUR, this_month_grid.shape[2], this_month_grid.shape[3])

        n_obs_per_day = np.ma.count(this_month_grid, axis = 2) # not used as yet.
        daily_grid = np.ma.mean(this_month_grid, axis = 2)
        daily_grid.fill_value = mdi

        # clear up memory
        del this_month_grid
        gc.collect()

        utils.netcdf_write(OUT_LOCATION + OUTROOT + "_1x1_daily_{}{:02d}.nc".format(year, month), \
                               daily_grid, OBS_ORDER, grid_lats, grid_lons, daily_hours[:,0], year, month, frequency = "D")

        # Pentads
        if doPentads:
            print "need to write the code"
            print "  How to do this for individual months..."

        # Monthlies
        elif doMonthlies:
            
            n_obs_per_month = np.ma.count(daily_grid, axis = 1) # not used as yet.
            monthly_grid = np.ma.mean(daily_grid, axis = 1)
            monthly_grid.fill_value = mdi

            utils.netcdf_write(OUT_LOCATION + OUTROOT + "_1x1_monthly_{}{:02d}.nc".format(year, month), \
                               monthly_grid, OBS_ORDER, grid_lats, grid_lons, daily_hours[0,0], year, month, frequency = "M")

            # clear up memory
            del daily_grid
            gc.collect()

        
            
        # now to re-grid to coarser resolution
        monthly_5by5, grid5_lats, grid5_lons = utils.grid_5by5(monthly_grid, grid_lats, grid_lons)
        
        utils.netcdf_write(OUT_LOCATION + OUTROOT + "_5x5_monthly_{}{:02d}.nc".format(year, month), \
                               monthly_5by5, OBS_ORDER, grid5_lats, grid5_lons, daily_hours[0,0], year, month, frequency = "M")
