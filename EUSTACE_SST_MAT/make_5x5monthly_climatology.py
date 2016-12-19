#!/usr/local/sci/bin/python2.7
#*****************************
#
# calculate climatology from 5x5 monthly fields
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
Takes annual 5x5 monthly fields and makes a pentad climatology over 1981-2010 (default).

Can work with 5x5 monthly fields created from daily or monthly data and using relaxed or strict completeness
settings according to commandline switches.  

-----------------------
LIST OF MODULES
-----------------------
utils.py

-----------------------
DATA
-----------------------
Input data and output data stored in:
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS2/

Requires 5x5 monthly grids - either calculated from daily or monthly data

-----------------------
HOW TO RUN THE CODE
-----------------------
python2.7 make_5x5monthly_climatology.py --suffix relax --start_year YYYY --end_year YYYY --period day --daily (OPTIONAL: one of --doQC, --doQC1it, --doQC2it, --doQC3it, --doBC)

python2.7 make_5x5monthly_climatology.py --help 
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

Version 2 (26 Sep 2016) Kate Willett
---------
 
Enhancements
This can now cope with the iterative approach (doQC1it, doQC2it, doQC3it in addition to doQC and doBC)
It can also cope with doBCtotal, doBChgt and doBCscn
This can also cope with --ShipOnly.
Look for # KATE modified
         ...
	 # end
 
Changes
Now assumes day and night are also 90 to -90 latitude for consistency with both
 
Bug fixes


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

import utils
import set_paths_and_vars
defaults = set_paths_and_vars.set()


OBS_ORDER = utils.make_MetVars(defaults.mdi, multiplier = False) 

# what size grid (lat/lon)
DELTA_LAT = 5
DELTA_LON = 5

# set up the grid
# KATE modified - flipped the lats to go 90 to -90
grid_lats = np.arange(90 - DELTA_LAT, -90 - DELTA_LAT, -DELTA_LAT)
#grid_lats = np.arange(-90 + DELTA_LAT, 90 + DELTA_LAT, DELTA_LAT)
# end
grid_lons = np.arange(-180 + DELTA_LAT, 180 + DELTA_LON, DELTA_LON)

# subroutine start
#*********************************************
# KATE modified
def calculate_climatology(suffix = "relax", start_year = 1981, end_year = 2010, period = "both", daily = False, 
                          doQC = False, doQC1it = False, doQC2it = False, doQC3it = False, 
			  doBC = False, doBCtotal = False, doBChgt = False, doBCscn = False,
			  ShipOnly = False):
#def calculate_climatology(suffix = "relax", start_year = 1981, end_year = 2010, period = "both", daily = False, doQC = False, doBC = False):
# end
    '''
    Make 5x5 monthly climatology

    :param str suffix: "relax" or "strict" criteria
    :param int start_year: start year to process
    :param int end_year: end year to process
    :param str period: which period to do day/night/both?
    :param bool daily: run in 1x1 daily --> 5x5 monthly data
    :param bool doQC: incorporate the QC flags or not
# KATE modified
    :param bool doQC1it: incorporate the 1st iteration QC flags or not
    :param bool doQC2it: incorporate the 2nd iteration QC flags or not
    :param bool doQC3it: incorporate the 3rd iteration QC flags or not
# end
    :param bool doBC: work on the bias corrected data
# KATE modified
    :param bool doBCtotal: work on the bias corrected data
    :param bool doBChgt: work on the height only bias corrected data
    :param bool doBCscn: work on the screen only bias corrected data
# end
# KATE modified
    :param bool ShipOnly: work on the ship platform only data
# end

    :returns:
    '''
# KATE modified
    settings = set_paths_and_vars.set(doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn, 
                                      doQC = doQC, doQC1it = doQC1it, doQC2it = doQC2it, doQC3it = doQC3it,
				      ShipOnly = ShipOnly)
    #settings = set_paths_and_vars.set(doBC = doBC, doQC = doQC)
# end

    if suffix == "relax":
        N_YEARS_PRESENT = 10 # number of years present to calculate climatology
    elif suffix == "strict":
        N_YEARS_PRESENT = 15 # number of years present to calculate climatology


    print "Do daily: {}".format(daily)

    N_YEARS = end_year - start_year + 1

    # read in each variable - memory issues

    all_clims = np.ma.zeros([len(OBS_ORDER), 12, len(grid_lats), len(grid_lons)])
    # KW - why set up as np.ones?
    all_clims.mask = np.zeros([len(OBS_ORDER), 12, len(grid_lats), len(grid_lons)])

    all_stds = np.ma.zeros([len(OBS_ORDER), 12, len(grid_lats), len(grid_lons)])
    all_stds.mask = np.zeros([len(OBS_ORDER), 12, len(grid_lats), len(grid_lons)])
    
    # KW no mask??? I've set one with fill_value as -1 - should the mask be .zeros or .ones though?
    all_n_obs = np.ma.zeros([N_YEARS * 12, len(grid_lats), len(grid_lons)])
    all_n_obs.mask = np.zeros([N_YEARS * 12, len(grid_lats), len(grid_lons)])
    all_n_obs.fill_value = -1
    
    if daily:
        filename = settings.DATA_LOCATION + "{}_5x5_monthly_from_daily_{}_{}.nc".format(settings.OUTROOT, period, suffix)
            
    else:
        filename = settings.DATA_LOCATION + "{}_5x5_monthly_{}_{}.nc".format(settings.OUTROOT, period, suffix)

    ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

    times = ncdf_file.variables["time"]
    data_start = int(times.long_name.split(" ")[2].split("/")[-1])
    clim_offset = (start_year - data_start) * 12
        
    for v, var in enumerate(OBS_ORDER):
	    
        print var.name

        # number of pentads = 365/5 = 73
        # set up empty data array
        all_months = np.ma.zeros([N_YEARS * 12, len(grid_lats), len(grid_lons)])
	# sets up a mask of 'False' = not masked!
        all_months.mask = np.zeros([N_YEARS * 12, len(grid_lats), len(grid_lons)])
        all_months.fill_value = settings.mdi

        all_months[:, :, :] = ncdf_file.variables[var.name][clim_offset:clim_offset + (30*12)]

        # months x lats x lons
        shape = all_months.shape
        all_months = all_months.reshape(-1, 12, shape[-2], shape[-1])

        n_grids = np.ma.count(all_months, axis = 0)

        # collapse down the years
# KATE MEDIAN WATCH
# KATE modified - forced to use MEAN
        all_clims[v, :, :, :] = np.ma.mean(all_months, axis = 0)
        #if settings.doMedian:
        #    all_clims[v, :, :, :] = utils.bn_median(all_months, axis = 0)
        #else:
        #    all_clims[v, :, :, :] = np.ma.mean(all_months, axis = 0)
# end
        all_stds[v, :, :, :] = np.ma.std(all_months, axis = 0)

        # mask where fewer than 50% of years have data
        locs = np.ma.where(n_grids < N_YEARS_PRESENT)
        all_clims[v, :, :, :].mask[locs] = True
        # KW should probably mask stdev too - although unmasked it does show the potential coverage
        all_stds[v, :, :, :].mask[locs] = True

        if settings.plots and v == 0:
            import matplotlib.pyplot as plt
            plt.clf()
            plt.hist(n_grids.reshape(-1), bins = np.arange(-1,32), align = "left", log = True, rwidth=0.5)
            plt.axvline(x = N_YEARS_PRESENT-0.5, color = "r")       
            plt.title("Number of years present in each pentad")
            plt.xlabel("Number of years (max = 30)")
            plt.ylabel("Frequency (log scale)")
            plt.savefig(settings.PLOT_LOCATION + "monthly_5x5_clims_n_years_{}_{}.png".format(period, suffix))

            
    # now process number of observations (KW all_n_obs wasn't a masked array - so have set it up as one - BUT not really convinced this 
    # is working as it should. No import numpy.ma?        
    all_n_obs[:, :, :] = ncdf_file.variables["n_obs"][clim_offset:clim_offset + (30*12)]
    all_n_obs = all_n_obs.reshape(-1, 12, shape[-2], shape[-1])
    all_obs = np.ma.sum(all_n_obs, axis = 0)

    # set up time array
    times = utils.TimeVar("time", "time since 1/1/{} in days".format(1), "days", "time")
    month_lengths = [calendar.monthrange(1, x + 1)[1] for x in range(12)]
    times.data = [sum(month_lengths[0:x]) for x in range(12)]

    # write files
    if daily:
        out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_climatology_from_daily_{}_{}.nc".format(period, suffix)
    else:
        out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_climatology_{}_{}.nc".format(period, suffix)

# KATE modified - only outputting 90 to -90 now and have changed grid_lats above
    utils.netcdf_write(out_filename, all_clims, n_grids, all_obs, OBS_ORDER, grid_lats, grid_lons, times, frequency = "Y")
    #if period == "both":
    #    utils.netcdf_write(out_filename, all_clims, n_grids, all_obs, OBS_ORDER, grid_lats[::-1], grid_lons, times, frequency = "Y")
    #else:
    #    utils.netcdf_write(out_filename, all_clims, n_grids, all_obs, OBS_ORDER, grid_lats, grid_lons, times, frequency = "Y")
# end
    if daily:
        out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_stdev_from_daily_{}_{}.nc".format(period, suffix)
    else:
        out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_stdev_{}_{}.nc".format(period, suffix)

# KATE modified - only outputting 90 to -90 now and have changed grid_lats above
    utils.netcdf_write(out_filename, all_stds, n_grids, all_obs, OBS_ORDER, grid_lats, grid_lons, times, frequency = "Y")
    #if period == "both":
    #    utils.netcdf_write(out_filename, all_stds, n_grids, all_obs, OBS_ORDER, grid_lats[::-1], grid_lons, times, frequency = "Y")
    #else:
    #    utils.netcdf_write(out_filename, all_stds, n_grids, all_obs, OBS_ORDER, grid_lats, grid_lons, times, frequency = "Y")
# end
    # test distribution of obs with grid boxes
    if daily:
        outfile = file(settings.OUTROOT + "_5x5_monthly_climatology_from_daily_{}_{}.txt".format(period, suffix), "w")
    else:
        outfile = file(settings.OUTROOT + "_5x5_monthly_climatology_{}_{}.txt".format(period, suffix), "w")
        
    utils.boxes_with_n_obs(outfile, all_obs, all_clims[0], N_YEARS_PRESENT)

    return # calculate_climatology

#************************************************************************
if __name__=="__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--suffix', dest='suffix', action='store', default = "relax",
                        help='"relax" or "strict" completeness, default = relax')
    parser.add_argument('--start_year', dest='start_year', action='store', default = 1981,
                        help='which year to start run, default = 1981')
    parser.add_argument('--end_year', dest='end_year', action='store', default = 2010,
                        help='which year to end run, default = 2010')
    parser.add_argument('--period', dest='period', action='store', default = "both",
                        help='which period to run for (day/night/all), default = "both"')
    parser.add_argument('--daily', dest='daily', action='store_true', default = False,
                        help='run on 1x1 daily --> 5x5 monthly data (rather than 1x1 monthly --> 5x5 monthly), default = False')
    parser.add_argument('--doQC', dest='doQC', action='store_true', default = False,
                        help='process the QC information, default = False')
# KATE modified
    parser.add_argument('--doQC1it', dest='doQC1it', action='store_true', default = False,
                        help='process the first iteration QC information, default = False')
    parser.add_argument('--doQC2it', dest='doQC2it', action='store_true', default = False,
                        help='process the second iteration QC information, default = False')
    parser.add_argument('--doQC3it', dest='doQC3it', action='store_true', default = False,
                        help='process the third iteration QC information, default = False')
# end
    parser.add_argument('--doBC', dest='doBC', action='store_true', default = False,
                        help='process the bias corrected data, default = False')
# KATE modified
    parser.add_argument('--doBCtotal', dest='doBCtotal', action='store_true', default = False,
                        help='process the bias corrected data, default = False')
    parser.add_argument('--doBChgt', dest='doBChgt', action='store_true', default = False,
                        help='process the height only bias corrected data, default = False')
    parser.add_argument('--doBCscn', dest='doBCscn', action='store_true', default = False,
                        help='process the screen only bias corrected data, default = False')
# end
# KATE modified
    parser.add_argument('--ShipOnly', dest='ShipOnly', action='store_true', default = False,
                        help='process the ship platform type only data, default = False')
# end
    args = parser.parse_args()

    print(' CHOSEN CLIMATOLOGY PERIOD MUST BE 30 YEARS: ',args.start_year,args.end_year)
    
    calculate_climatology(suffix = str(args.suffix), start_year = int(args.start_year), end_year = int(args.end_year), period = str(args.period), daily = args.daily, \
# KATE modified
                          doQC = args.doQC, doQC1it = args.doQC1it, doQC2it = args.doQC2it, doQC3it = args.doQC3it, \
			  doBC = args.doBC, doBCtotal = args.doBCtotal, doBChgt = args.doBChgt, doBCscn = args.doBCscn, \
			  ShipOnly = args.ShipOnly)
                          #doQC = args.doQC, doBC = args.doBC)
# end

# END
# ************************************************************************

