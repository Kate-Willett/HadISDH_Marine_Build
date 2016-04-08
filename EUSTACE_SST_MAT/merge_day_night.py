#!/usr/local/sci/bin/python2.7
#*****************************
#
# merge _day and _night netCDF files 
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

import utils

doMedian = False

START_YEAR = 1973
END_YEAR = dt.datetime.now().year - 1

# Constants in CAPS
OUTROOT = "ERAclimNBC"

DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS/"
OUT_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS/"
PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS/"

mdi = -1.e30
OBS_ORDER = utils.make_MetVars(mdi, multiplier = False)


#************************************************************************
def do_merge(fileroot):
    '''
    Merge the _day and _night files

    Do a np.ma.mean or median for the data and a sum for the n_obs and n_grids

    Output with a _both suffix

    :param str fileroot: root for filenames
    '''

    # spin through both periods
    for p, period in enumerate(["day", "night"]):
        print period
        
        # go through the variables
        for v, var in enumerate(OBS_ORDER):

            print "   {}".format(var.name)

            ncdf_file = ncdf.Dataset("{}_{}.nc".format(fileroot, period),'r', format='NETCDF4')

            if v == 0 and p == 0:

                shape = list(ncdf_file.variables[var.name][:].shape)
                shape.insert(0, len(OBS_ORDER)+2) # add all the variables
                shape.insert(0, 2) # insert extra dimension to allow day + night

                all_data = np.ma.zeros(shape)

                all_data[p, v] = ncdf_file.variables[var.name][:]


                # get lats/lons of box centres
                lat_centres = ncdf_file.variables["latitude"]
                latitudes = lat_centres + (lat_centres[1] - lat_centres[0])/2.

                lon_centres = ncdf_file.variables["longitude"]
                longitudes = lon_centres + (lon_centres[1] - lon_centres[0])/2.

                # get times - make a dummy object and then populate attributes
                times = utils.TimeVar("time", "time since 1/{}/{} in hours".format(1, 1973), "hours", "time")

                times.long_name = ncdf_file.variables["time"].long_name
                times.standard_name = ncdf_file.variables["time"].standard_name
                times.long_name = ncdf_file.variables["time"].long_name
                times.units = ncdf_file.variables["time"].units

                times.data = ncdf_file.variables["time"][:]

            else:
                all_data[p, v] = ncdf_file.variables[var.name][:]

        # and get n_obs and n_grids
        all_data[p, -2] = ncdf_file.variables["n_grids"][:]
        all_data[p, -1] = ncdf_file.variables["n_obs"][:]

    # invert latitudes
    latitudes = latitudes[::-1]
    all_data = all_data[:,:,:,::-1,:]

    # got all the info, now merge
    if doMedian:
        merged_data = utils.bn_median(all_data[:, :len(OBS_ORDER)], axis = 0)
    else:
        merged_data = np.ma.mean(all_data[:, :len(OBS_ORDER)], axis = 0)

    # and process the grids and observations (split off here so have incorporated latitude inversion)
    n_grids = np.ma.sum(all_data[:, -2], axis = 0)
    n_obs = np.ma.sum(all_data[:, -1], axis = 0)

    # write the output file
    utils.netcdf_write("{}_{}.nc".format(fileroot, "both"), merged_data, n_grids, n_obs, OBS_ORDER, latitudes, longitudes, times, frequency = "P")

    return # do_merge


#************************************************************************
def get_fileroot(climatology = False, do3hr = False, monthly = [], daily = False):
    '''
    Get the filename root depending on switches

    :param bool climatology: for pentad climatology files
    :param bool do3hr: run for pentad climatology files created from 3hrly data
    :param list monthly: if list not empty then set as [YYYY, MM] to run for 5x5 monthly data
    :param bool daily: run for monthly grids created from 1x1 daily
    '''


    if climatology and monthly != []:
        print "Cannot run both for Climatology files and for Monthly files"
        raise RuntimeError

    if climatology:
        if do3hr:
            fileroot = DATA_LOCATION + OUTROOT + "_1x1_pentad_climatology_from_3hrly"
        else:
            fileroot = DATA_LOCATION + OUTROOT + "_1x1_pentad_climatology"


    elif monthly != []:
        if daily:
            fileroot = DATA_LOCATION + OUTROOT + "_5x5_monthly_from_daily_{}{:02d}".format(monthly[0], monthly[1])
        else:
            fileroot = DATA_LOCATION + OUTROOT + "_5x5_monthly_{}{:02d}".format(monthly[0], monthly[1])
             
    return fileroot # get_fileroot



#************************************************************************
def set_up_merge(clims = False, months = False, start_year = START_YEAR, end_year = END_YEAR, start_month = 1, end_month = 12):
    '''
    Obtain file roots and set processes running
    
    :param bool clims: run the climatologies
    :param bool months: run the climatologies
    :param int start_year: start year to process
    :param int end_year: end year to process
    :param int start_month: start month to process
    :param int end_month: end month to process
    '''
    

    if clims:
        print "Processing Climatologies"
        
        fileroot = get_fileroot(climatology = True)
        do_merge(fileroot)
        
        fileroot = get_fileroot(climatology = True, do3hr = True)
        do_merge(fileroot)


    if months:
        print "Processing Monthly Files"

        start_year = START_YEAR
        end_year = END_YEAR
        start_month = 1
        end_month = 12

        for year in np.arange(start_year, end_year + 1): 

            for month in np.arange(start_month, end_month + 1):

                fileroot = get_fileroot(monthly = [year, month])
                do_merge(fileroot)

                fileroot = get_fileroot(monthly = [year, month], daily = True)
                do_merge(fileroot)


    return # set_up_merge

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
    parser.add_argument('--clims', dest='clims', action='store_true', default = False,
                        help='run climatology merge, default = False')
    parser.add_argument('--months', dest='months', action='store_true', default = False,
                        help='run monthly merge, default = False')
 
    args = parser.parse_args()


    set_up_merge(clims = args.clims, months = args.months, start_year = int(args.start_year), end_year = int(args.end_year), \
                    start_month = int(args.start_month), end_month = int(args.end_month))

# END
# ************************************************************************
