#!/usr/local/sci/bin/python2.7
#*****************************
#
# convert 3 hourly data to pentads
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
Takes 3 hourly data and creates pentads.  First summing across the 5 days and then the 8 timestamps

-----------------------
LIST OF MODULES
-----------------------
utils.py

-----------------------
DATA
-----------------------
Input data and output data stored in:
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS2/

Requires 3hrly grids.

-----------------------
HOW TO RUN THE CODE
-----------------------
python2.7 3hrlies_to_pentads.py --suffix relax --period day --start_year YYYY --end_year YYYY

python2.7 3hrlies_to_pentads.py --help 
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

OBS_ORDER = utils.make_MetVars(defaults.mdi, multiplier = False)

# what size grid (lat/lon)
DELTA_LAT = 1
DELTA_LON = 1
DELTA_HOUR = 3

# set up the grid
grid_lats = np.arange(-90 + DELTA_LAT, 90 + DELTA_LAT, DELTA_LAT)
grid_lons = np.arange(-180 + DELTA_LAT, 180 + DELTA_LON, DELTA_LON)


#************************************************************************
def read_data(settings, suffix, name, year, grid_lats, grid_lons, period, N_OBS_PER_DAY):
    '''
    Read in the data from the netCDF files

    :param Settings settings: object to hold all filepaths etc.
    :param str suffix: used to determine whether using strict or relaxed criteria
    :param str name: variable name
    :param int year: year to read
    :param array grid_lats: latitudes
    :param array grid_lons: longitudes
    :param str period: which period (day/night/all)
    :param int N_OBS_PER_DAY: number of observation times per day

    :returns: var_3hrlys - array of 3hrly data for single variable
    '''

    if suffix == "relax":
        N_OBS_OVER_DAYS = 1
        N_OBS_OVER_PENTAD = 2

    elif suffix == "strict":
        N_OBS_OVER_DAYS = 2
        N_OBS_OVER_PENTAD = 4  


    # set up empty data array
    var_3hrlys = np.ma.zeros([utils.days_in_year(year)*N_OBS_PER_DAY, len(grid_lats), len(grid_lons)])
    var_3hrlys.mask = np.zeros([utils.days_in_year(year)*N_OBS_PER_DAY, len(grid_lats), len(grid_lons)])
    var_3hrlys.fill_value = settings.mdi
    
    year_start = dt.datetime(year, 1, 1, 0, 0)
    
    for month in np.arange(12) + 1:
        print year, month
        
        month_start = utils.day_of_year(year, month)
        month_end = month_start + calendar.monthrange(year, month)[1]
        
        filename = "{}/{}_1x1_3hr_{}{:02d}_{}_{}.nc".format(settings.DATA_LOCATION, settings.OUTROOT, year, month, period, suffix)
                
        ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')
        
        if month == 12:
            # run to end of year if december
            var_3hrlys[month_start*N_OBS_PER_DAY:, :, :] = ncdf_file.variables[name][:]
        else:
            var_3hrlys[month_start*N_OBS_PER_DAY:month_end*N_OBS_PER_DAY, :, :] = ncdf_file.variables[name][:]

    return var_3hrlys # read_data

#************************************************************************
def process_february(var_3hrlys, doMask = True):
    '''
    Process the set of 3hly obs that fall on 29th Feb.

    Store them, then remove from the main array.

    :param array var_3hrlys: array for 3hrly data for one variable
    :param bool doMask: process the mask (for data yes, for n_obs no)

    :returns: var_3hrlys, incl_feb29th - updated data and the Feb 29th obs.
    '''


    assert var_3hrlys.shape[0] == 366
    
    # extract 6-day pentad
    incl_feb29th = var_3hrlys[55:61, :, :, :]
    
    if doMask:
        # remove the data of Feb 29th from array
        # np.ma.delete doesn't exist, so have to copy mask separately
        mask = var_3hrlys.mask
    
    var_3hrlys = np.delete(var_3hrlys, 59, 0) 

    if doMask:
        mask = np.delete(mask, 59, 0)
        var_3hrlys = np.ma.array(var_3hrlys, mask = mask)
        del mask
    
    return var_3hrlys, incl_feb29th # process_february



#************************************************************************
def do_conversion(suffix = "relax", start_year = defaults.START_YEAR, end_year = defaults.END_YEAR, period = "all", doQC = False, doBC = False):
    '''
    Convert 3 hrlies to pentads 1x1

    First get pentad average of 3hrly values (so values at 0, 3, 6, ... averaged over 5 days)
    Then get average over the pentad.

    :param str suffix: "relax" or "strict" criteria
    :param int start_year: start year to process
    :param int end_year: end year to process
    :param str period: which period to do day/night/all?
    :param bool doQC: incorporate the QC flags or not
    :param bool doBC: work on the bias corrected data

    :returns:
    '''
    settings = set_paths_and_vars.set(doBC = doBC, doQC = doQC)


    # KW Added SUFFIX variable because all hourlies/dailies/monthlies now have suffix 'strict' (4/2 per daily/day-night) 
    # or 'relax' (2/1 per daily/day-night)
    if suffix == "relax":
        N_OBS_OVER_DAYS = 1 # at least 1 obs at this 3 hr timestamp from 5 days in pentad
        N_OBS_OVER_PENTAD = 2

    elif suffix == "strict":
        N_OBS_OVER_DAYS = 2
        N_OBS_OVER_PENTAD = 4  # at least 4 timestamps (of 8) in pentad, could be 2 for local 'relax' setting


    N_OBS_PER_DAY = 24/DELTA_HOUR

    for year in np.arange(start_year, end_year + 1): 

        all_pentads =  np.ma.zeros([len(OBS_ORDER), 73, len(grid_lats), len(grid_lons)])
        all_pentads.mask =  np.zeros([len(OBS_ORDER), 73, len(grid_lats), len(grid_lons)])

        # read in a years worth of 3hrly data
        for v, var in enumerate(OBS_ORDER):
            # arrays too massive to process all variables at once.
            print var.name
       
            var_3hrlys = read_data(settings, suffix, var.name, year, grid_lats, grid_lons, period, N_OBS_PER_DAY)

            # reshape to days x 3hrly obs (365(366),8,180,360)
            var_3hrlys = var_3hrlys.reshape(-1, N_OBS_PER_DAY, var_3hrlys.shape[1], var_3hrlys.shape[2])

            # process the leap-year if appropriate
            if calendar.isleap(year):
                var_3hrlys, incl_feb29th  = process_february(var_3hrlys, doMask = True)
            else:
                assert var_3hrlys.shape[0] == 365

            # get pentadly values for each timestep (73,5,8,180,360)
            shape = var_3hrlys.shape
            var_3hrlys = var_3hrlys.reshape(-1, 5, shape[-3], shape[-2], shape[-1]) # n_pentads x days x hrs x lat x lon

            n_days_per_timestamp = np.ma.count(var_3hrlys, axis = 1) # n_pentads x hrs x lat x lon

            # get average at each timestamp across the pentad - so have N_OBS_PER_DAY averaged values per pentad
            if settings.doMedian:
                pentad_3hrly_grid = utils.bn_median(var_3hrlys, axis = 1) # n_pentads x hrs x lat x lon
            else:
                pentad_3hrly_grid = np.ma.mean(var_3hrlys, axis = 1) # n_pentads x hrs x lat x lon

            pentad_3hrly_grid.mask[n_days_per_timestamp < N_OBS_OVER_DAYS] = True # mask where fewer than N_OBS_OVER_DAYS days have values
            
            # clear up memory
            del var_3hrlys
            gc.collect()

            # the pentad containing feb 29th is the 11th in the year (KW actually its the 12th, so the 11 in array speak which is what you have done)
            if calendar.isleap(year):
                #  overwrite this with the me(di)an of a 6-day pentad
                if settings.doMedian:
                    pentad_3hrly_grid[11, :, :, :] = utils.bn_median(incl_feb29th, axis = 0)
                else:
                    pentad_3hrly_grid[11, :, :, :] = np.ma.mean(incl_feb29th, axis = 0)

                feb_n_days_per_timestamp = np.ma.count(incl_feb29th, axis = 0)
                pentad_3hrly_grid.mask[11, :, :, :][feb_n_days_per_timestamp < N_OBS_OVER_DAYS] = True
                n_days_per_timestamp[11, :, :, :] = feb_n_days_per_timestamp

                print "processed Feb 29th"

            if settings.plots and v == 0:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.hist(n_days_per_timestamp.reshape(-1), bins = np.arange(-1,7), align = "left", log = True, rwidth=0.5)
                plt.axvline(x = N_OBS_OVER_DAYS-0.5, color = "r")       
                plt.title("Number of days with obs at each 3hrly timestamp (over entire year)")
                plt.xlabel("Number of days (max = 5)")
                plt.ylabel("Frequency (log scale)")
                plt.savefig(settings.PLOT_LOCATION + "pentads_n_days_{}_{}_{}.png".format(year, period, suffix))

            # get single pentad values
            n_hrs_per_pentad = np.ma.count(pentad_3hrly_grid, axis = 1) # get the number of pentad-hours present in each pentad
            n_grids_per_pentad = np.sum(n_days_per_timestamp, axis = 1) # get the number of 3hrly 1x1 grids included per pentad 1x1

            # get average at each timestamp across the pentad - so have N_OBS_PER_DAY values per pentad
            if settings.doMedian:
                pentad_grid = utils.bn_median(pentad_3hrly_grid, axis = 1)
            else:
                pentad_grid = np.ma.mean(pentad_3hrly_grid, axis = 1)

            if period == "all":
# KW are you sure this should be n_hrs_per_pentad and not n_grids_per_pentad here? I think it should
                pentad_grid.mask[n_hrs_per_pentad < N_OBS_OVER_PENTAD] = True # mask where fewer than N_OBS_OVER_PENTAD hours have values
            else:
# KW are you sure this should be n_hrs_per_pentad and not n_grids_per_pentad here? I think it should
                pentad_grid.mask[n_hrs_per_pentad < (N_OBS_OVER_PENTAD/2.)] = True # mask where fewer than N_OBS_OVER_PENTAD hours have values
            
            all_pentads[v, :, :, :] = pentad_grid

            # diagnostics plots of obs/grids per pentad
            if settings.plots and v == 0:
                plt.clf()
                plt.hist(n_hrs_per_pentad.reshape(-1), bins = np.arange(-1,10), align = "left", log = True, rwidth=0.5)
                if period == "all":
                    plt.axvline(x = N_OBS_OVER_PENTAD-0.5, color = "r")       
                else:
                    plt.axvline(x = (N_OBS_OVER_PENTAD/2.)-0.5, color = "r")       
                plt.title("Number of hrs with obs in each pentad (over entire year)")
                plt.xlabel("Number of days (max = 8)")
                plt.ylabel("Frequency (log scale)")
                plt.savefig(settings.PLOT_LOCATION + "pentads_n_hrs_{}_{}_{}.png".format(year, period, suffix))

            # clear up memory
            del pentad_3hrly_grid
            del pentad_grid
            gc.collect()

        # done all main variables.  Now for number of observations
        print "n_obs"
        n_obs = read_data(settings, suffix, "n_obs", year, grid_lats, grid_lons, period, N_OBS_PER_DAY)
	# KW so we've gone from 8*365hrs,lats,lons to 365,8,lats,lons
        n_obs = n_obs.reshape(-1, N_OBS_PER_DAY, n_obs.shape[1], n_obs.shape[2])
        if calendar.isleap(year):
            n_obs, incl_feb29th  = process_february(n_obs, doMask = True)
        else:
            assert n_obs.shape[0] == 365    

        shape = n_obs.shape
	# KW so we're now at pentads, 5days, 8hours, lats, lons
        n_obs = n_obs.reshape(-1, 5, shape[-3], shape[-2], shape[-1]) # pentads x days x hours x lat x lon
        
	# KW This should sum over the 5days leaving pentads, 8hrs, lats, lons
	# n_obs has -1 as missing data!!! So sum will not work properly
	# set up fill_value as -1
	n_obs.fill_value = -1
        n_obs_per_3hrly_pentad = np.ma.sum(n_obs, axis = 1)
        n_obs_per_3hrly_pentad.fill_value = -1

        if calendar.isleap(year):
            n_obs_per_3hrly_pentad[11, :, :, :] = np.ma.sum(incl_feb29th, axis = 0)

        n_obs_per_pentad = np.ma.sum(n_obs_per_3hrly_pentad, axis = 1)

        # and write out
        times = utils.TimeVar("time", "time since 1/1/{} in hours".format(year), "hours", "time")
        times.data = np.arange(0, all_pentads.shape[1]) * 5 * 24

        out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_pentad_from_3hrly_{}_{}_{}.nc".format(year, period, suffix)
        
        utils.netcdf_write(out_filename, all_pentads, n_grids_per_pentad, n_obs_per_pentad, OBS_ORDER, grid_lats, grid_lons, times, frequency = "P")


    return # do_conversion
    
#************************************************************************
if __name__=="__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--suffix', dest='suffix', action='store', default = "relax",
                        help='"relax" or "strict" completeness, default = relax')
    parser.add_argument('--start_year', dest='start_year', action='store', default = defaults.START_YEAR,
                        help='which year to start run, default = 1973')
    parser.add_argument('--end_year', dest='end_year', action='store', default = defaults.END_YEAR,
                        help='which year to end run, default = present')
    parser.add_argument('--period', dest='period', action='store', default = "all",
                        help='which period to run for (day/night/all), default = "all"')
    parser.add_argument('--doQC', dest='doQC', action='store_true', default = False,
                        help='process the QC information, default = False')
    parser.add_argument('--doBC', dest='doBC', action='store_true', default = False,
                        help='process the bias corrected data, default = False')
    args = parser.parse_args()


    do_conversion(suffix = str(args.suffix), start_year = int(args.start_year), end_year = int(args.end_year), period = str(args.period), doQC = args.doQC, doBC = args.doBC)

# END
# ************************************************************************
