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
import matplotlib
matplotlib.use('Agg') 
import calendar
import gc

import utils
import plot_qc_diagnostics
import MDS_basic_KATE as mds

plots = False
doQC = True
doSST_SLP = False
doMedian = True
# KW #
# Use of median vs mean #
# Essentially we're using the average as a way of smoothing in time and space so ideally it would have influence from all viable values
# within that time/space period.
# The median might be better when we're first using the raw obs to create the 1x1 3 hrlies because we know that there may be some shockers in there.
# There is NO expectation that the values would be very similar or very different (not necessarily normally distributed)
# After that, we're averaging already smoothed values but missing data may make our resulting average skewed.
# There IS an expectation that the values would quite different across the diurnal cycle (quite possibly normally distributed)
# For dailies we could set up specific averaging routines depending on the sampling pattern
# e.g.,
#	All 8 3hrly 1x1s present = mean(0,3,6,9,12,15,18,21)
#	6 to 7 3hrly 1x1s present = interpolate between missing vals (if 3 to 18hrs missing), repeat 0=3 or 21=18 (if 0 or 21 hrs missing), mean(0,3,6,9,12,15,18,21)
#	5 or fewer 3hrly 1x1s present = mean(mean(0 to 9hrs),mean(12 to 21hrs)) or just mean(0 to 9hrs) or mean(12 to 21hrs) if either one of those results in 0/missing.
# a median of 5 values might give you 3 cool values and 2 warm, the 'average' would then be the cool value with no influence from the warmer daytime value (or vice versa)
# For pentad or monthlies I think the median or mean would be ok - and median might be safer.
# There is NO expectation that the values would be very similar or very different (not necessarily normally distributed) 
# For monthly 5x5s I think we should use the mean to make sure the influence of sparse obs are included.
# There IS an expectation that the values could quite different across a 500km2 area and 1 month (quite possibly, but not necessarily normally distributed)

doMonthlies = True
doPentads = False

N_OBS_FRAC_DAY = 0.5
N_OBS_FRAC_MONTH = 0.5

# Constants in CAPS
OUTROOT = "ERAclimNBC"

DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)
OUT_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS/"
PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS/"

START_YEAR = 1973
END_YEAR = dt.datetime.now().year - 1

mdi = -1.e30
OBS_ORDER = utils.make_MetVars(mdi, doSST_SLP = doSST_SLP)

# what size grid (lat/lon/hour)
DELTA_LAT = 1
DELTA_LON = 1
DELTA_HOUR = 3

# set up the grid
grid_lats = np.arange(-90 + DELTA_LAT, 90 + DELTA_LAT, DELTA_LAT)
grid_lons = np.arange(-180 + DELTA_LON, 180 + DELTA_LON, DELTA_LON)

# flags to check on and values to allow through
these_flags = {"ATbud":0, "ATclim":0,"ATrep":0,"DPTbud":0,"DPTclim":0,"DPTssat":0,"DPTrep":0,"DPTrepsat":0}

# RD - adapted MDS_basic_Kate.py to allow this call
fields = mds.TheDelimiters

#************************************************************************
def do_gridding(start_year = START_YEAR, end_year = END_YEAR, start_month = 1, end_month = 12):
    '''
    Do the gridding, first to 3hrly 1x1, then to daily 1x1 and finally monthly 1x1 and 5x5

    :param int start_year: start year to process
    :param int end_year: end year to process
    :param int start_month: start month to process
    :param int end_month: end month to process

    :returns:
    '''


    # spin through years and months to read files
    for year in np.arange(start_year, end_year + 1): 


        for month in np.arange(start_month, end_month + 1):

            times = utils.TimeVar("time", "time since 1/{}/{} in hours".format(month, year), "hours", "time")

            grid_hours = np.arange(0, 24 * calendar.monthrange(year, month)[1], DELTA_HOUR)

            times.data = grid_hours

            # process the monthly file
            filename = "new_suite_{}{:02d}_{}.txt".format(year, month, OUTROOT)
            raw_platform_data, raw_obs, raw_meta, raw_qc = utils.read_qc_data(filename, DATA_LOCATION, fields)

            # extract observation details
            lats, lons, years, months, days, hours = utils.process_platform_obs(raw_platform_data)

            # test dates *KW - SHOULDN'T NEED THIS - ONLY OBS PASSING DATE CHECK ARE INCLUDED*
            if not utils.check_date(years, year, "years", filename):
                sys.exit(1)
            if not utils.check_date(months, month, "months", filename):
                sys.exit(1)

            if plots:
                # plot the distribution of hours

                import matplotlib.pyplot as plt

                plt.clf()
                plt.hist(hours, np.arange(-100,2500,100))
                plt.ylabel("Number of observations")
                plt.xlabel("Hours")
                plt.xticks(np.arange(-300, 2700, 300))
                plt.savefig(PLOT_LOCATION + "obs_distribution_{}{:02d}.png".format(year, month))


                # only for a few of the variables
                for variable in OBS_ORDER:
                    if variable.name in ["dew_point_temperature", "specific_humidity", "relative_humidity", "dew_point_temperature_anomalies", "specific_humidity_anomalies", "relative_humidity_anomalies"]:

                        plot_qc_diagnostics.values_vs_lat(variable, lats, raw_obs[:, variable.column], raw_qc, PLOT_LOCATION + "qc_actuals_{}_{}{:02d}.png".format(variable.name, year, month), multiplier = variable.multiplier)


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
            utils.netcdf_write(OUT_LOCATION + OUTROOT + "_1x1_3hr_{}{:02d}.nc".format(year, month), \
                                   this_month_grid, OBS_ORDER, grid_lats, grid_lons, times, frequency = "H")

            # now average over time
            # Dailies
            daily_hours = grid_hours.reshape(-1, 24/DELTA_HOUR)

            shape = this_month_grid.shape
            this_month_grid = this_month_grid.reshape(shape[0], -1, 24/DELTA_HOUR, shape[2], shape[3])

            if doMedian:
                daily_grid = np.ma.median(this_month_grid, axis = 2)
            else:
                daily_grid = np.ma.mean(this_month_grid, axis = 2)
            daily_grid.fill_value = mdi

            # filter on number of observations/day
            n_obs_per_day = np.ma.count(this_month_grid, axis = 2) 
            bad_locs = np.where(n_obs_per_day < (24./DELTA_HOUR) * N_OBS_FRAC_DAY) # 50% of possible hourly values (6hrly data *KW OR AT LEAST 4 3HRLY OBS PRESENT*)
            daily_grid.mask[bad_locs] = True
            
            if plots:
                # plot the distribution of hours

                plt.clf()
                plt.hist(n_obs_per_day[0].reshape(-1), bins = np.arange(0,10)+0.5, align = "mid", log = True, rwidth=0.5)
                plt.savefig(PLOT_LOCATION + "n_obs_daily_{}{:02d}.png".format(year, month))

            # clear up memory
            del this_month_grid
            gc.collect()

            # write dailies file
            times.data = daily_hours[:,0]
            utils.netcdf_write(OUT_LOCATION + OUTROOT + "_1x1_daily_{}{:02d}.nc".format(year, month), \
                                   daily_grid, OBS_ORDER, grid_lats, grid_lons, times, frequency = "D")


            # Monthlies
            times.data = daily_hours[0,0]

            if doMedian:
                monthly_grid = np.ma.median(daily_grid, axis = 1)
            else:
                monthly_grid = np.ma.mean(daily_grid, axis = 1)

            monthly_grid.fill_value = mdi

            # filter on number of observations/month
            n_obs_per_month = np.ma.count(daily_grid, axis = 1) 
            bad_locs = np.where(n_obs_per_month < calendar.monthrange(year, month)[1] * N_OBS_FRAC_MONTH) # 50% of possible daily values
            ***KW*** BUG *** DO YOU MEAN monthly_grid.mask[bad_locs] = True 
	    daily_grid.mask[bad_locs] = True
            
            if plots:
                # plot the distribution of days

                plt.clf()
                plt.hist(n_obs_per_month[0].reshape(-1), bins = np.arange(0,calendar.monthrange(year, month)[1]+1,2)+0.5, align = "mid", log = True, rwidth=0.5)
                plt.savefig(PLOT_LOCATION + "n_obs_monthly_{}{:02d}.png".format(year, month))

            # write dailies file
            utils.netcdf_write(OUT_LOCATION + OUTROOT + "_1x1_monthly_{}{:02d}.nc".format(year, month), \
                               monthly_grid, OBS_ORDER, grid_lats, grid_lons, times, frequency = "M")

            # clear up memory
            del daily_grid
            gc.collect()



            # now to re-grid to coarser resolution
	    # KW # Here we may want to use the mean because its a large area but could be sparsely populated with quite different climatologies so we want 
	    # the influence of the outliers (we've done our best to ensure these are good values) 
            monthly_5by5, grid5_lats, grid5_lons = utils.grid_5by5(monthly_grid, grid_lats, grid_lons, doMedian = doMedian)

            utils.netcdf_write(OUT_LOCATION + OUTROOT + "_5x5_monthly_{}{:02d}.nc".format(year, month), \
                                   monthly_5by5, OBS_ORDER, grid5_lats, grid5_lons, times, frequency = "M")


    return # do_gridding

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
    args = parser.parse_args()


    do_gridding(start_year = int(args.start_year), end_year = int(args.end_year), \
                    start_month = int(args.start_month), end_month = int(args.end_month))

# END
# ************************************************************************
