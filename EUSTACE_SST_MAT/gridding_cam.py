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

import grid_utils as utils


plots = True
# Constants in CAPS

DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/beta/"
START_YEAR = 1973
END_YEAR = dt.datetime.now().year - 1

OBS_ORDER = ["MAT","MAT_AN","SST","SST_AN","SLP","DPT","DPT_AN","SHU","SHU_AN","VAP","VAP_AN","CRH","CRH_AN","CWB","CWB_AN","DPD","DPD_AN", "DSVS"]

mdi = -9999

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

        month_grid = np.ma.zeros([len(OBS_ORDER),len(grid_hours),len(grid_lats), len(grid_lons)])

        month_grid.fill(mdi)
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
        filename = "new_suite_{}{}_constantP.txt".format(year, month)
        raw_data, raw_obs, raw_meta, raw_qc = utils.read_qc_data(filename, DATA_LOCATION, fields)


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
            

        # discretise hours
        hours = utils.make_index(hours, DELTA_HOUR, multiplier = 100)


        # get the hours since start of month
        hours_since = ((days - 1) * 24) + (hours * DELTA_HOUR)

        # convert raw_obs array
        raw_obs = raw_obs.astype(int)

        # discretise lats/lons
        lat_index = utils.make_index(lats, DELTA_LAT, multiplier = 100)
        lon_index = utils.make_index(lons, DELTA_LON, multiplier = 100)

        
                      
        # this is the gridding bit!
        for gh in grid_hours:
            print gh
            for lt in grid_lats:
                for ln in grid_lons:

                    # find where the matches are
                    locs1, = np.where(np.logical_and(lat_index == lt, lon_index == ln))
                    locs2, = np.where(hours_since[locs1] == gh)

                    locs = locs1[locs2]
                    
                    if locs.shape[0] > 0:
                        month_grid[:, gh, lt, ln] = np.mean(raw_obs[locs, :], axis = 0)
                        month_grid.mask [:, gh, lt, ln] = False # unset the mask

            end = dt.datetime.now()

            if gh > 12:
                break

        # have one month of gridded data.

        utils.netcdf_write(month_grid, grid_lats, grid_lons, hours_since, year, month)
            
