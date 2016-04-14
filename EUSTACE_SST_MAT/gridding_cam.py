#!/usr/local/sci/bin/python2.7
#*****************************
#
# general Python gridding script
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
Converts raw ASCII hourly observations extracted from IMMA ICOADS format to 3 hrly 1x1 grids.  Then further consolidation to:

1x1 daily
1x1 monthly
5x5 monthly

and also 5x5 monthly calculated directly from the 1x1 daily data.  

These later grids are available for day- and night-time periods (any mixtures are assigned to daytime) and also using strict and relaxed completeness criteria.

-----------------------
LIST OF MODULES
-----------------------
utils.py
plot_qc_diagnostics.py - to output plots of clean obs vs all
MDS_basic_KATE.py - for the file format

-----------------------
DATA
-----------------------
Input data stored in:
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/

Exact folder set by "OUTROOT" - as depends on bias correction.

-----------------------
HOW TO RUN THE CODE
-----------------------
python2.7 gridding_cam.py --suffix relax --period day --start_year YYYY --end_year YYYY --start_month MM --end_month MM

python2.7 gridding_cam.py --help 
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
import matplotlib
matplotlib.use('Agg') 
import calendar
import gc
import copy

import utils
import plot_qc_diagnostics
import MDS_basic_KATE as mds

plots = True
doQC = True
doSST_SLP = False

doMedian = False
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

# Constants in CAPS
OUTROOT = "ERAclimNBC"

DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)
# KW Changed GRIDS to GRIDS2 adn PLOTS to PLOTS2 to make sure I don't write over what has been done already
OUT_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS2/"
PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS2/"

START_YEAR = 1973
END_YEAR = dt.datetime.now().year - 1

mdi = -1.e30
OBS_ORDER = utils.make_MetVars(mdi, doSST_SLP = doSST_SLP, multiplier = True) # ensure that convert from raw format at writing stage with multiplier

# what size grid (lat/lon/hour)
DELTA_LAT = 1
DELTA_LON = 1
DELTA_HOUR = 3

# set up the grid
grid_lats = np.arange(-90 + DELTA_LAT, 90 + DELTA_LAT, DELTA_LAT)
grid_lons = np.arange(-180 + DELTA_LON, 180 + DELTA_LON, DELTA_LON)

# RD - adapted MDS_basic_Kate.py to allow this call
fields = mds.TheDelimiters

#************************************************************************
def do_gridding(suffix = "relax", start_year = START_YEAR, end_year = END_YEAR, start_month = 1, end_month = 12, period = "all"):
    '''
    Do the gridding, first to 3hrly 1x1, then to daily 1x1 and finally monthly 1x1 and 5x5

    :param str suffix: "relax" or "strict" criteria
    :param int start_year: start year to process
    :param int end_year: end year to process
    :param int start_month: start month to process
    :param int end_month: end month to process
    :param str period: which period to do day/night/all?

    :returns:
    '''

    # KW switching between 4 ('_strict') for climatology build and 2 for anomaly buily ('_relax') - added subscripts to files
    if suffix == "relax":
        N_OBS_DAY = 2 # KW ok for anomalies but this was meant to be 4 for dailies_all? and 2 for dailies_night/day?
        N_OBS_FRAC_MONTH = 0.3

    elif suffix == "strict":
        N_OBS_DAY = 4
        N_OBS_FRAC_MONTH = 0.3


    # flags to check on and values to allow through
    these_flags = {"ATbud":0, "ATclim":0,"ATrep":0,"DPTbud":0,"DPTclim":0,"DPTssat":0,"DPTrep":0,"DPTrepsat":0}


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
            #  *RD* - hasn't run yet but will leave it in just in case of future use.
            if not utils.check_date(years, year, "years", filename):
                sys.exit(1)
            if not utils.check_date(months, month, "months", filename):
                sys.exit(1)

            if plots and (year in [1973, 1983, 1993, 2003, 2013]):
                # plot the distribution of hours

                import matplotlib.pyplot as plt

                plt.clf()
                plt.hist(hours, np.arange(-100,2500,100))
                plt.ylabel("Number of observations")
                plt.xlabel("Hours")
                plt.xticks(np.arange(-300, 2700, 300))
                plt.savefig(PLOT_LOCATION + "obs_distribution_{}{:02d}_{}.png".format(year, month, suffix))


                # only for a few of the variables
                for variable in OBS_ORDER:
                    if variable.name in ["dew_point_temperature", "specific_humidity", "relative_humidity", "dew_point_temperature_anomalies", "specific_humidity_anomalies", "relative_humidity_anomalies"]:

                        plot_qc_diagnostics.values_vs_lat(variable, lats, raw_obs[:, variable.column], raw_qc, these_flags, PLOT_LOCATION + "qc_actuals_{}_{}{:02d}_{}.png".format(variable.name, year, month, suffix), multiplier = variable.multiplier)
 

            # QC sub-selection
            if doQC:
                print "Using {} as flags".format(these_flags)
                mask = utils.process_qc_flags(raw_qc, these_flags)

                complete_mask = np.zeros(raw_obs.shape)
                for i in range(raw_obs.shape[1]):
                    complete_mask[:,i] = mask
                clean_data = np.ma.masked_array(raw_obs, mask = complete_mask)

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
            # extract the full grid, number of obs, and day/night flag
            raw_month_grid, raw_month_n_obs, this_month_period = utils.grid_1by1_cam(clean_data, raw_qc, hours_since, lat_index, lon_index, grid_hours, grid_lats, grid_lons, OBS_ORDER, mdi, doMedian = True)
            print "successfully read data into 1x1 3hrly grids"

            # create matching array size
            this_month_period = np.tile(this_month_period, (len(OBS_ORDER),1,1,1))

            for period in ["all", "day", "night"]:

                if period == "day":
                    this_month_grid = np.ma.masked_where(this_month_period == 1, raw_month_grid)
                    this_month_obs = np.ma.masked_where(this_month_period[0] == 1, raw_month_n_obs) # and take first slice to re-match the array size
                elif period == "night":
                    this_month_grid = np.ma.masked_where(this_month_period == 0, raw_month_grid)
                    this_month_obs = np.ma.masked_where(this_month_period[0] == 0, raw_month_n_obs) # and take first slice to re-match the array size
                else:
                    this_month_grid = copy.deepcopy(raw_month_grid)
                    this_month_obs = copy.deepcopy(raw_month_n_obs)
                    
                # have one month of gridded data.
                out_filename = OUT_LOCATION + OUTROOT + "_1x1_3hr_{}{:02d}_{}_{}.nc".format(year, month, period, suffix)              

                utils.netcdf_write(out_filename, this_month_grid, np.zeros(this_month_obs.shape), this_month_obs, OBS_ORDER, grid_lats, grid_lons, times, frequency = "H")

                # now average over time
                # Dailies
                daily_hours = grid_hours.reshape(-1, 24/DELTA_HOUR)

                shape = this_month_grid.shape
                this_month_grid = this_month_grid.reshape(shape[0], -1, 24/DELTA_HOUR, shape[2], shape[3])
                this_month_obs = this_month_obs.reshape(-1, 24/DELTA_HOUR, shape[2], shape[3])

                if doMedian:
                    daily_grid = np.ma.median(this_month_grid, axis = 2)
                else:
                    daily_grid = np.ma.mean(this_month_grid, axis = 2)
                daily_grid.fill_value = mdi

                # filter on number of observations/day
                n_hrs_per_day = np.ma.count(this_month_grid, axis = 2) 
                n_obs_per_day = np.ma.sum(this_month_obs, axis = 1) 

                if period == "all":
                    bad_locs = np.where(n_hrs_per_day < N_OBS_DAY) # at least 2 of possible 8 3-hourly values (6hrly data *KW OR AT LEAST 4 3HRLY OBS PRESENT*)
                else:
                    bad_locs = np.where(n_hrs_per_day < np.floor(N_OBS_DAY / 2.)) # at least 1 of possible 8 3-hourly values (6hrly data *KW OR AT LEAST 4 3HRLY OBS PRESENT*)              
                daily_grid.mask[bad_locs] = True

                if plots and (year in [1973, 1983, 1993, 2003, 2013]):
                    # plot the distribution of hours

                    plt.clf()
                    plt.hist(n_hrs_per_day.reshape(-1), bins = np.arange(-1,10), align = "left", log = True, rwidth=0.5)
                    if period == "all":
                        plt.axvline(x = N_OBS_DAY-0.5, color = "r")
                    else:
                        plt.axvline(x = np.floor(N_OBS_DAY / 2.)-0.5, color = "r")       

                    plt.title("Number of 1x1-3hrly in each 1x1-daily grid box")
                    plt.xlabel("Number of 3-hrly observations (max = 8)")
                    plt.ylabel("Frequency (log scale)")
                    plt.savefig(PLOT_LOCATION + "n_grids_1x1_daily_{}{:02d}_{}_{}.png".format(year, month, period, suffix))

                    plt.clf()
                    plt.hist(n_obs_per_day.reshape(-1), bins = np.arange(-5,100,5),  log = True, rwidth=0.5)                 
                    plt.title("Total number of raw observations in each 1x1 daily grid box")
                    plt.xlabel("Number of raw observations")
                    plt.ylabel("Frequency (log scale)")
                    plt.savefig(PLOT_LOCATION + "n_obs_1x1_daily_{}{:02d}_{}_{}.png".format(year, month, period, suffix))

                # clear up memory
                del this_month_grid
                del this_month_obs
                gc.collect()

                # write dailies file
                times.data = daily_hours[:,0]
                out_filename = OUT_LOCATION + OUTROOT + "_1x1_daily_{}{:02d}_{}_{}.nc".format(year, month, period, suffix)

                utils.netcdf_write(out_filename, daily_grid, n_hrs_per_day[0], n_obs_per_day, OBS_ORDER, grid_lats, grid_lons, times, frequency = "D")

                # Monthlies
                times.data = daily_hours[0,0]

                if doMedian:
                    monthly_grid = np.ma.median(daily_grid, axis = 1)
                else:
                    monthly_grid = np.ma.mean(daily_grid, axis = 1)

                monthly_grid.fill_value = mdi

                # filter on number of observations/month
                n_grids_per_month = np.ma.count(daily_grid, axis = 1) 
                bad_locs = np.where(n_grids_per_month < calendar.monthrange(year, month)[1] * N_OBS_FRAC_MONTH) # 30% of possible daily values
                monthly_grid.mask[bad_locs] = True

                # number of raw observations
                n_obs_per_month = np.ma.sum(n_obs_per_day, axis = 0)

                if plots and (year in [1973, 1983, 1993, 2003, 2013]):
                    # plot the distribution of days

                    plt.clf()
                    plt.hist(n_obs_per_month.reshape(-1), bins = np.arange(-10,500,10),  log = True, rwidth=0.5)
                    plt.title("Total number of raw observations in each 1x1 monthly grid box")
                    plt.xlabel("Number of raw observations")
                    plt.ylabel("Frequency (log scale)")
                    plt.savefig(PLOT_LOCATION + "n_obs_1x1_monthly_{}{:02d}_{}_{}.png".format(year, month, period, suffix))

                    plt.clf()
                    plt.hist(n_grids_per_month[0].reshape(-1), bins = np.arange(-2,40,2), align = "left",  log = True, rwidth=0.5)
                    plt.axvline(x = calendar.monthrange(year, month)[1] * N_OBS_FRAC_MONTH, color="r")
                    plt.title("Total number of 1x1 daily grids in each 1x1 monthly grid")
                    plt.xlabel("Number of 1x1 daily grids")
                    plt.ylabel("Frequency (log scale)")
                    plt.savefig(PLOT_LOCATION + "n_grids_1x1_monthly_{}{:02d}_{}_{}.png".format(year, month, period, suffix))

                # write monthly 1x1 file
                out_filename = OUT_LOCATION + OUTROOT + "_1x1_monthly_{}{:02d}_{}_{}.nc".format(year, month, period, suffix)
                utils.netcdf_write(out_filename, monthly_grid, n_grids_per_month[0], n_obs_per_month, OBS_ORDER, grid_lats, grid_lons, times, frequency = "M")
            
                # now to re-grid to coarser resolution
                # KW # Here we may want to use the mean because its a large area but could be sparsely
                #             populated with quite different climatologies so we want 
                # the influence of the outliers (we've done our best to ensure these are good values) 

                # go from monthly 1x1 to monthly 5x5 - retained as limited overhead
                monthly_5by5, monthly_5by5_n_grids, monthly_5by5_n_obs, grid5_lats, grid5_lons = utils.grid_5by5(monthly_grid, n_obs_per_month, grid_lats, grid_lons, doMedian = doMedian, daily = False)
                out_filename = OUT_LOCATION + OUTROOT + "_5x5_monthly_{}{:02d}_{}_{}.nc".format(year, month, period, suffix)

                utils.netcdf_write(out_filename, monthly_5by5, monthly_5by5_n_grids, monthly_5by5_n_obs, OBS_ORDER, grid5_lats, grid5_lons, times, frequency = "M")

                if plots and (year in [1973, 1983, 1993, 2003, 2013]):
                    # plot the distribution of days

                    plt.clf()
                    plt.hist(monthly_5by5_n_obs.reshape(-1), bins = np.arange(0,100,5), log = True, rwidth=0.5)
                    plt.title("Total number of raw observations in each 5x5 monthly grid box")
                    plt.xlabel("Number of raw observations")
                    plt.ylabel("Frequency (log scale)")
                    plt.savefig(PLOT_LOCATION + "n_obs_5x5_monthly_{}{:02d}_{}_{}.png".format(year, month, period, suffix))

                    plt.clf()
                    plt.hist(monthly_5by5_n_grids.reshape(-1), bins = np.arange(-2,30,2), align = "left", log = True, rwidth=0.5)
                    plt.axvline(x = 1, color="r")
                    plt.title("Total number of 1x1 monthly grids in each 5x5 monthly grid")
                    plt.xlabel("Number of 1x1 monthly grids")
                    plt.ylabel("Frequency (log scale)")
                    plt.savefig(PLOT_LOCATION + "n_grids_5x5_monthly_{}{:02d}_{}_{}.png".format(year, month, period, suffix))

                # clear up memory
                del monthly_grid
                del monthly_5by5
                del monthly_5by5_n_grids
                del monthly_5by5_n_obs
                del n_grids_per_month
                del n_obs_per_month
                del n_hrs_per_day
                gc.collect()

                # go direct from daily 1x1 to monthly 5x5
                monthly_5by5, monthly_5by5_n_grids, monthly_5by5_n_obs, grid5_lats, grid5_lons = utils.grid_5by5(daily_grid, n_obs_per_day, grid_lats, grid_lons, doMedian = doMedian, daily = True)

                out_filename = OUT_LOCATION + OUTROOT + "_5x5_monthly_from_daily_{}{:02d}_{}_{}.nc".format(year, month, period, suffix)
 
                utils.netcdf_write(out_filename, monthly_5by5, monthly_5by5_n_grids, monthly_5by5_n_obs, OBS_ORDER, grid5_lats, grid5_lons, times, frequency = "M")

                

                if plots and (year in [1973, 1983, 1993, 2003, 2013]):
                    # plot the distribution of days

                    plt.clf()
                    plt.hist(monthly_5by5_n_obs.reshape(-1), bins = np.arange(-10,1000,10),  log = True, rwidth=0.5)
                    plt.title("Total number of raw observations in each 5x5 monthly grid box")
                    plt.xlabel("Number of raw observations")
                    plt.ylabel("Frequency (log scale)")
                    plt.savefig(PLOT_LOCATION + "n_obs_5x5_monthly_from_daily_{}{:02d}_{}_{}.png".format(year, month, period, suffix))


                    plt.clf()
                    plt.hist(monthly_5by5_n_grids.reshape(-1), bins = np.arange(-5,100,5), align = "left", log = True, rwidth=0.5)
                    plt.axvline(x = (0.3 * daily_grid.shape[0]), color="r")
                    plt.title("Total number of 1x1 daily grids in each 5x5 monthly grid")
                    plt.xlabel("Number of 1x1 daily grids")
                    plt.ylabel("Frequency (log scale)")

                    plt.savefig(PLOT_LOCATION + "n_grids_5x5_monthly_from_daily_{}{:02d}_{}_{}.png".format(year, month, period, suffix))


                del daily_grid
                del monthly_5by5
                del n_obs_per_day
                del monthly_5by5_n_grids
                del monthly_5by5_n_obs
                gc.collect()

    return # do_gridding

#************************************************************************
if __name__=="__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--suffix', dest='suffix', action='store', default = "relax",
                        help='"relax" or "strict" completeness, default = relax')
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


    do_gridding(suffix = str(args.suffix), start_year = int(args.start_year), end_year = int(args.end_year), \
                    start_month = int(args.start_month), end_month = int(args.end_month), period = str(args.period))

# END
# ************************************************************************
