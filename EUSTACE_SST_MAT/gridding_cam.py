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

plots = True
doQC = True
doMonthlies = True
doPentads = False

# Constants in CAPS

DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/beta/"
#PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS/"

START_YEAR = 1973
END_YEAR = dt.datetime.now().year - 1

mdi = -9999
OBS_ORDER = utils.make_MetVars(mdi)

# what size grid (lat/lon/hour)
DELTA_LAT = 1
DELTA_LON = 1
DELTA_HOUR = 3

# set up the grid
grid_lats = np.arange(-90, 90 + DELTA_LAT, DELTA_LAT)
grid_lat_centres = grid_lats[1:] - DELTA_LAT/2.

grid_lons = np.arange(-180, 180 + DELTA_LON, DELTA_LON)
grid_lon_centres = grid_lons[1:] - DELTA_LON/2.


'''
Get (3) hourly, 1 x 1 grid fields

Then rescale to daily/pentad/monthly and then to 5 x 5 fields
'''


# spin through years and months to read files
for year in [1973]: # range(START_YEAR, END_YEAR):

    for month in [12]: # (range(12) + 1):

        grid_hours = np.arange(0, 24 * calendar.monthrange(year, month)[1], DELTA_HOUR)

        # RD - adapted MDS_basic_Kate.py to allow this call
        fields = mds.TheDelimiters

        # process the monthly file
        filename = "new_suite_{}{}_tinyclim.txt".format(year, month)
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
            plt.savefig("obs_distribution_{}_{}.png".format(year, month))

            
            # only for a few of the variables
            for variable in OBS_ORDER:
                if variable.name in ["dew_point_temperature", "specific_humidity", "relative_humidity", "dew_point_temperature_anomalies", "specific_humidity_anomalies", "relative_humidity_anomalies"]:

                    plot_qc_diagnostics.values_vs_lat(variable, lats, raw_obs[:, variable.column], raw_qc, "qc_actuals_{}_{}_{}.png".format(variable.name, year, month), multiplier = variable.multiplier)

            
        # QC sub-selection
        if doQC:
            print "Using ALL QC FLAGS"
            mask = utils.process_qc_flags(raw_qc)

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
          
        # set up the array
        this_month_grid = np.ma.zeros([len(OBS_ORDER),len(grid_hours),len(grid_lats), len(grid_lons)], fill_value = mdi)
        this_month_grid.mask = np.ones([len(OBS_ORDER),len(grid_hours),len(grid_lats), len(grid_lons)])
        # this is the gridding bit!
        for gh, timestamp in enumerate(grid_hours):
            print "Hours since 1/{}/{} 00:00 = {}".format(month, year, timestamp)
            for lt, glat in enumerate(grid_lats):
                for ln, glon in enumerate(grid_lons):

                    # find where the matches are
                    locs1, = np.where(np.logical_and(lat_index == lt, lon_index == ln))
                    locs2, = np.where(hours_since[locs1] == timestamp)

                    locs = locs1[locs2]
                    
                    if locs.shape[0] > 0:
                        this_month_grid[:, gh, lt, ln] = np.mean(clean_data[locs, :], axis = 0)
                        this_month_grid.mask [:, gh, lt, ln] = False # unset the mask

            if timestamp > 12: break

        # have one month of gridded data.
        utils.netcdf_write("out_test_1x1_3hr_{}_{}.nc".format(year, month), \
                               this_month_grid, OBS_ORDER, grid_lats, grid_lons, grid_hours, year, month)

        # now average over time
        # Dailies

        daily_hours = grid_hours.reshape(-1, 24/DELTA_HOUR)
        this_month_grid = this_month_grid.reshape(this_month_grid.shape[0], -1, 24/DELTA_HOUR, this_month_grid.shape[2], this_month_grid.shape[3])
        #         variables x days x timepoints x lats x lons

        n_obs_per_day = np.ma.count(this_month_grid, axis = 2) # not used as yet.
        daily_grid = np.ma.mean(this_month_grid, axis = 2)
        
        # clear up memory
        del this_month_grid
        gc.collect()

        utils.netcdf_write("out_test_1x1_daily_{}_{}.nc".format(year, month), \
                               daily_grid, OBS_ORDER, grid_lats, grid_lons, daily_hours[:,0], year, month)

        # Pentads
        if doPentads:
            print "need to write the code"
            print "  How to do this for individual months..."

        # Monthlies
        elif doMonthlies:
            
            n_obs_per_month = np.ma.count(daily_grid, axis = 1) # not used as yet.
            monthly_grid = np.ma.mean(daily_grid, axis = 1)

            utils.netcdf_write("out_test_1x1_monthly_{}_{}.nc".format(year, month), \
                               monthly_grid, OBS_ORDER, grid_lats, grid_lons, daily_hours[0,0], year, month)

            # clear up memory
            del daily_grid
            gc.collect()

        
            
        # now to re-grid to coarser resolution
