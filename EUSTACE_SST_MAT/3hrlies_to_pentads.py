#!/usr/local/sci/bin/python2.7
#*****************************
#
# convert 3 hourly data to pentads
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
N_OBS = 2 # timestamps on at least 2 days in pentad
N_OBS_PENTAD = 4 # at least 4 timestamps in pentad


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
DELTA_HOUR = 3

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

    N_OBS_PER_DAY = 24/DELTA_HOUR

    for year in np.arange(start_year, end_year + 1): 

        all_pentads =  np.ma.zeros([len(OBS_ORDER), 73, len(grid_lats), len(grid_lons)])
        all_pentads.mask =  np.zeros([len(OBS_ORDER), 73, len(grid_lats), len(grid_lons)])

        for v, var in enumerate(OBS_ORDER):
            print var.name
        
            # set up empty data array
            var_3hrlys = np.ma.zeros([utils.days_in_year(year)*N_OBS_PER_DAY, len(grid_lats), len(grid_lons)])
            var_3hrlys.mask = np.ma.ones([utils.days_in_year(year)*N_OBS_PER_DAY, len(grid_lats), len(grid_lons)])
            var_3hrlys.fill_value = mdi

            year_start = dt.datetime(year, 1, 1, 0, 0)

            for month in np.arange(12) + 1:
                print year, month

                month_start = utils.day_of_year(year, month)
                month_end = month_start + calendar.monthrange(year, month)[1]

                filename = "{}/{}_1x1_3hr_{}{:02d}.nc".format(DATA_LOCATION, OUTROOT, year, month)

                ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

                if month == 12:
                    # run to end of year if december
                    var_3hrlys[month_start*N_OBS_PER_DAY:, :, :] = ncdf_file.variables[var.name][:]
                else:
                    var_3hrlys[month_start*N_OBS_PER_DAY:month_end*N_OBS_PER_DAY, :, :] = ncdf_file.variables[var.name][:]

            # reshape to days x 3hrly obs
            var_3hrlys = var_3hrlys.reshape(-1, N_OBS_PER_DAY, var_3hrlys.shape[1], var_3hrlys.shape[2])

            # process the leap-year if appropriate
            if calendar.isleap(year):
                assert var_3hrlys.shape[0] == 366

                # extract 6-day pentad
                incl_feb29th = var_3hrlys[55:61, :, :, :]

                # remove the data of Feb 29th from array
                # np.ma.delete doesn't exist, so have to copy mask separately
                mask = var_3hrlys.mask
                var_3hrlys = np.delete(var_3hrlys, 59, 0) 
                mask = np.delete(mask, 59, 0)
                var_3hrlys = np.ma.array(var_3hrlys, mask = mask)
                del mask

            else:
                assert var_3hrlys.shape[0] == 365


            # get pentadly values for each timestep
            shape = var_3hrlys.shape
            var_3hrlys = var_3hrlys.reshape(-1, 5, shape[-3], shape[-2], shape[-1])

            n_obs_per_timestamp = np.ma.count(var_3hrlys, axis = 1) 

            # get average at each timestamp across the pentad - so have N_OBS_PER_DAY values per pentad
            if doMedian:
                pentad_3hrly_grid = np.ma.median(var_3hrlys, axis = 1)
            else:
                pentad_3hrly_grid = np.ma.mean(var_3hrlys, axis = 1)

            pentad_3hrly_grid.mask[n_obs_per_timestamp < N_OBS] = True # mask where fewer than N_OBS days have values

            # clear up memory
            del n_obs_per_timestamp
            del var_3hrlys
            gc.collect()

            # the pentad containing feb 29th is the 11th in the year
            if calendar.isleap(year):
                #  overwrite this with the me(di)an of a 6-day pentad
                if doMedian:
                    pentad_3hrly_grid[11, :, :, :] = np.ma.median(incl_feb29th, axis = 0)
                else:
                    pentad_3hrly_grid[11, :, :, :] = np.ma.mean(incl_feb29th, axis = 0)


                n_obs_per_timestamp = np.ma.count(incl_feb29th, axis = 0)
                pentad_3hrly_grid.mask[11, :, :, :][n_obs_per_timestamp < N_OBS] = True

                print "processed Feb 29th"

            # get single pentad values
            n_obs_per_pentad = np.ma.count(pentad_3hrly_grid, axis = 1) 

            # get average at each timestamp across the pentad - so have N_OBS_PER_DAY values per pentad
            if doMedian:
                pentad_grid = np.ma.median(pentad_3hrly_grid, axis = 1)
            else:
                pentad_grid = np.ma.mean(pentad_3hrly_grid, axis = 1)

            pentad_grid.mask[n_obs_per_pentad < N_OBS_PENTAD] = True # mask where fewer than N_OBS_PENTAD hours have values
            
            all_pentads[v, :, :, :] = pentad_grid

            # clear up memory
            del n_obs_per_pentad
            del pentad_3hrly_grid
            del pentad_grid
            gc.collect()
                
        times = utils.TimeVar("time", "time since 1/1/{} in hours".format(year), "hours", "time")
        times.data = np.arange(0, all_pentads.shape[1]) * 5 * 24

        utils.netcdf_write(DATA_LOCATION + OUTROOT + "_1x1_pentad_from_3hrly_{}.nc".format(year), \
                               all_pentads, OBS_ORDER, grid_lats, grid_lons, times, frequency = "P")


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
