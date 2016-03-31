#!/usr/local/sci/bin/python2.7
#*****************************
#
# convert dailies to pentads
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

doMedian = False
N_OBS = 2


# Constants in CAPS
OUTROOT = "ERAclimNBC"

DATA_LOCATION = "/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS/"
PLOT_LOCATION = "/project/hadobs2/hadisdh/marine/PLOTS/"

START_YEAR = 1973
END_YEAR = dt.datetime.now().year - 1

mdi = -1.e30
OBS_ORDER = utils.make_MetVars(mdi, multiplier = False)

# what size grid (lat/lon)
DELTA_LAT = 1
DELTA_LON = 1

# set up the grid
grid_lats = np.arange(-90 + DELTA_LAT, 90 + DELTA_LAT, DELTA_LAT)
grid_lons = np.arange(-180 + DELTA_LAT, 180 + DELTA_LON, DELTA_LON)

#************************************************************************
def do_conversion(start_year = START_YEAR, end_year = END_YEAR):
    '''
    Convert dailies to pentads 1x1

    :param int start_year: start year to process
    :param int end_year: end year to process

    :returns:
    '''

    for year in np.arange(start_year, end_year + 1): 

        # set up empty data array
        all_dailies = np.ma.zeros([len(OBS_ORDER), utils.days_in_year(year), len(grid_lats), len(grid_lons)])
        all_dailies.mask = np.ma.zeros([len(OBS_ORDER), utils.days_in_year(year), len(grid_lats), len(grid_lons)])
        all_dailies.fill_value = mdi

        year_start = dt.datetime(year, 1, 1, 0, 0)

        for month in np.arange(12) + 1:
            print year, month

            month_start = utils.day_of_year(year, month)
            month_end = month_start + calendar.monthrange(year, month)[1]

            filename = "{}/{}_1x1_daily_{}{:02d}.nc".format(DATA_LOCATION, OUTROOT, year, month)

            ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

            for v, var in enumerate(OBS_ORDER):

                if month == 12:
                    # run to end of year if december
                    all_dailies[v, month_start:, :, :] = ncdf_file.variables[var.name][:]
                else:
                    all_dailies[v, month_start:month_end, :, :] = ncdf_file.variables[var.name][:]


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

        else:
            assert all_dailies.shape[1] == 365

        shape = all_dailies.shape
        all_dailies = all_dailies.reshape(shape[0], -1, 5, shape[-2], shape[-1])

        n_obs_per_pentad = np.ma.count(all_dailies, axis = 2) 

        if doMedian:
            pentad_grid = np.ma.median(all_dailies, axis = 2)
        else:
            pentad_grid = np.ma.mean(all_dailies, axis = 2)

        pentad_grid.mask[n_obs_per_pentad < N_OBS] = True # mask where fewer than 3 days have values # KW THIS IS ACTUALLY 2 - WHICH I THINK IS GOOD

        # clear up memory
        del all_dailies
        gc.collect()

        # the pentad containing feb 29th is the 11th in the year
        if calendar.isleap(year):
            #  overwrite this with the me(di)an of a 6-day pentad
            if doMedian:
                pentad_grid[:, 11, :, :] = np.ma.median(incl_feb29th, axis = 1)
            else:
                pentad_grid[:, 11, :, :] = np.ma.mean(incl_feb29th, axis = 1)


            n_obs_per_pentad = np.ma.count(incl_feb29th, axis = 1)
            pentad_grid.mask[:, 11, :, :][n_obs_per_pentad < N_OBS] = True 

            print "processed Feb 29th"
                
        times = utils.TimeVar("time", "time since 1/1/{} in hours".format(year), "hours", "time")
        times.data = np.arange(0, pentad_grid.shape[1]) * 5 * 24

        utils.netcdf_write(DATA_LOCATION + OUTROOT + "_1x1_pentad_{}.nc".format(year), \
                               pentad_grid, OBS_ORDER, grid_lats, grid_lons, times, frequency = "P")

        del n_obs_per_pentad
        del pentad_grid
        gc.collect()

    return # do_conversion
    
#************************************************************************
if __name__=="__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_year', dest='start_year', action='store', default = START_YEAR,
                        help='which year to start run, default = 1973')
    parser.add_argument('--end_year', dest='end_year', action='store', default = END_YEAR,
                        help='which year to end run, default = present')
    args = parser.parse_args()


    do_conversion(start_year = int(args.start_year), end_year = int(args.end_year))

# END
# ************************************************************************
