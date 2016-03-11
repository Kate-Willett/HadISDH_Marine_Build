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

import utils
import plot_qc_diagnostics

plots = True
# Constants in CAPS

DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/beta/"
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
grid_lons = np.arange(-180, 180 + DELTA_LON, DELTA_LON)

'''
Get (3) hourly, 1 x 1 grid fields

Then rescale to daily/pentad/monthly and 5 x 5 fields
'''


# spin through years and months to read files
for year in [1973]: # range(START_YEAR, END_YEAR):

    for month in [12]: # (range(12) + 1):

        grid_hours = np.arange(0, 24 * calendar.monthrange(year, month)[1], DELTA_HOUR)

        # set up the array
        month_grid = np.ma.zeros([len(OBS_ORDER),len(grid_hours),len(grid_lats), len(grid_lons)], fill_value = mdi)
        month_grid.mask = np.ones([len(OBS_ORDER),len(grid_hours),len(grid_lats), len(grid_lons)])


        # RD - I've had to copy this from Extended_IMMA.py
        #      And it was difficult given extra spaces in the format statements
        #      Not flexible or reliable.  Can we do better?
        fields = (9+1,\
                      8,8,8,8,8,8,8,\
                      8,8,8,8,8,\
                      8,8,8,8,8,8,8,8,8,8,8,8,\
                      8,8,8,8,8,8,\
                      5,3,3,3,8,3,8,3,8,3,8,4,\
                      3,4,4,3,2,3,5,5,5,5,5,7+1,\
                      10,10,10,10,9)

        # process the monthly file
        filename = "new_suite_{}{}_newclimSDlimit.txt".format(year, month)
        raw_data, raw_obs, raw_meta, raw_qc = utils.read_qc_data(filename, DATA_LOCATION, fields)

        # can do subselections here, on all 4 outputs.



        # extract observation details
        lats, lons, years, months, days, hours = utils.process_platform_obs(raw_data)

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
                if variable.name in ["dew_point_temperature", "specific_humidity", "relative_humidity"]:
                    raw_input("To do")

                    plot_qc_diagnostics.actuals_vs_lat(variable, lats, raw_obs[:, obs.column], raw_qc)

                if variable.name in ["dew_point_temperature_anomalies", "specific_humidity_anomalies", "relative_humidity_anomalies"]:
                    raw_input("To do")

                    plot_qc_diagnostics.anomalies_vs_lat(variable, lats, raw_obs[:, obs.column], raw_qc)
            

        # discretise hours
        hours = utils.make_index(hours, DELTA_HOUR, multiplier = 100)


        # get the hours since start of month
        hours_since = ((days - 1) * 24) + (hours * DELTA_HOUR)

        # convert raw_obs array
        raw_obs = raw_obs.astype(int)

        # discretise lats/lons
        lat_index = utils.make_index(lats, DELTA_LAT, multiplier = 100)
        lon_index = utils.make_index(lons, DELTA_LON, multiplier = 100)

        lat_index += ((len(grid_lats)-1)/2) # and as -ve indices are unhelpful, roll by offsetting by most westward
        lon_index += ((len(grid_lons)-1)/2) #    or most southerly so that (0,0) is (-90,-180)

        # NOTE - ALWAYS GIVING TOP-RIGHT OF BOX TO GIVE < HARD LIMIT (as opposed to <=)
          
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
                        month_grid[:, gh, lt, ln] = np.mean(raw_obs[locs, :], axis = 0)
                        month_grid.mask [:, gh, lt, ln] = False # unset the mask

            # if timestamp > 12: break

        # have one month of gridded data.

        utils.netcdf_write(month_grid, OBS_ORDER, grid_lats, grid_lons, grid_hours, year, month)
            
