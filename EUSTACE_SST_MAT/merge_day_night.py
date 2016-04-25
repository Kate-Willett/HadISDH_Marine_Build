#!/usr/local/sci/bin/python2.7
#*****************************
#
# merge _day and _night netCDF files 
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
Merge outputs from _day and _night to create _both.  An alternative approach to the _all files


-----------------------
LIST OF MODULES
-----------------------
utils.py

-----------------------
DATA
-----------------------
Input data stored in:
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS2


-----------------------
HOW TO RUN THE CODE
-----------------------
python2.7 merge_day_night.py --suffix relax --clims --months --start_year YYYY --end_year YYYY --start_month MM --end_month MM

python2.7 gridding_cam.py --help 
will show all options

--clims - run for the climatologies
--months - run for the monthly files (will need years and months)

-----------------------
OUTPUT
-----------------------
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS2/

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

import utils
import set_paths_and_vars
defaults = set_paths_and_vars.set()

#************************************************************************
def do_merge(fileroot, mdi, suffix = "relax", clims = False, doMedian = False):
    '''
    Merge the _day and _night files

    Do a np.ma.mean or median for the data and a sum for the n_obs and n_grids

    Output with a _both suffix

    :param str fileroot: root for filenames
    :param flt mdi: missing data indicator
    :param str suffix: "relax" or "strict" criteria
    :param bool clims: if climatologies then don't try and process anomalies.
    '''

    OBS_ORDER = utils.make_MetVars(mdi, multiplier = False)

    if clims:
        # KW make OBS_ORDER only the actual variables - remove anomalies
        NEWOBS_ORDER = []
        for v, var in enumerate(OBS_ORDER):
            if "anomalies" not in var.name:
                NEWOBS_ORDER.append(var)
        del OBS_ORDER
        OBS_ORDER = np.copy(NEWOBS_ORDER)
        del NEWOBS_ORDER     


    # spin through both periods
    for p, period in enumerate(["day", "night"]):
        print period
        
        # go through the variables
        for v, var in enumerate(OBS_ORDER):

            print "   {}".format(var.name)

            ncdf_file = ncdf.Dataset("{}_{}_{}.nc".format(fileroot, period, suffix),'r', format='NETCDF4')

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
    n_obs.fill_value = -1
    n_grids.fill_value = -1

    # write the output file
    utils.netcdf_write("{}_{}_{}.nc".format(fileroot, "both", suffix), merged_data, n_grids, n_obs, OBS_ORDER, latitudes, longitudes, times, frequency = "P")

    # test distribution of obs with grid boxes
    outfile = file("{}_{}_{}.txt".format(fileroot.split("/")[-1], "both", suffix), "w")
    utils.boxes_with_n_obs(outfile, n_obs, merged_data[0], "")


    return # do_merge


#************************************************************************
def get_fileroot(settings, climatology = False, pentads = False, months = [], do3hr = True, time = [], daily = True):
    '''
    Get the filename root depending on switches

    :param Settings settings: settings object for paths
    :param bool climatology: for pentad climatology files
    :param bool pentads: for annual pentad files
    :param bool months: for monthly files
    :param bool do3hr: run for pentad climatology files created from 3hrly data
    :param list monthly: pass in [YYYY] or [YYYY, MM] for pentad or monthly files
    :param bool daily: run for monthly grids created from 1x1 daily
    '''


    if climatology and months != []:
        print "Cannot run both for Climatology files and for Monthly files"
        raise RuntimeError

    if climatology:
        if do3hr:
            fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_pentad_climatology_from_3hrly"
        else:
            fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_pentad_climatology"

    elif pentads:
        if do3hr:
            fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_pentad_from_3hrly_{}".format(time[0])
        else:
            fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_pentad_{}".format(time[0])

    elif months != []:
        if daily:
            fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_from_daily_{}{:02d}".format(time[0], time[1])
        else:
            fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_{}{:02d}".format(time[0], time[1])
             

    return fileroot # get_fileroot



#************************************************************************
def set_up_merge(suffix = "relax", clims = False, months = False, pentads = False, start_year = START_YEAR, end_year = END_YEAR, start_month = 1, end_month = 12, doQC = False, doBC = False):
    '''
    Obtain file roots and set processes running
    
    :param str suffix: "relax" or "strict" criteria
    :param bool clims: run the climatologies
    :param bool months: run the climatologies
    :param bool pentads: run the annual pentads
    :param int start_year: start year to process
    :param int end_year: end year to process
    :param int start_month: start month to process
    :param int end_month: end month to process
    :param bool doQC: incorporate the QC flags or not
    :param bool doBC: work on the bias corrected data
    '''
    
    settings = set_paths_and_vars.set(doBC = doBC, doQC = doQC)

    if clims:
        print "Processing Climatologies"
        
#        fileroot = get_fileroot(settings, climatology = True)
#        do_merge(fileroot, settings.mdi, suffix, doMedian = settings.doMedian)
        
        fileroot = get_fileroot(settings, climatology = True, do3hr = True)
        do_merge(fileroot, settings.mdi, suffix, clims = True, doMedian = settings.doMedian)

    if pentads:
        print "Processing Pentads"
        
#        fileroot = get_fileroot(settings, pentads = True)
#        do_merge(fileroot, settings.mdi, suffix, doMedian = settings.doMedian)
        
        for year in np.arange(start_year, end_year + 1): 
            print year
            fileroot = get_fileroot(settings, pentads = True, do3hr = True, time = [year])
            do_merge(fileroot, settings.mdi, suffix, doMedian = settings.doMedian)

    if months:
        print "Processing Monthly Files"

        start_year = START_YEAR
        end_year = END_YEAR
        start_month = 1
        end_month = 12

        for year in np.arange(start_year, end_year + 1): 
            print year

            for month in np.arange(start_month, end_month + 1):
                print "  {}".format(month)

#                fileroot = get_fileroot(settings, months = True, time = [year, month])
#                do_merge(fileroot, settings.mdi, suffix, doMedian = settings.doMedian)

                fileroot = get_fileroot(settings, months = True, time = [year, month], daily = True)
                do_merge(fileroot, settings.mdi, suffix, doMedian = settings.doMedian)


    return # set_up_merge

#************************************************************************
if __name__=="__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--suffix', dest='suffix', action='store', default = "relax",
                        help='"relax" or "strict" completeness, default = relax')
    parser.add_argument('--clims', dest='clims', action='store_true', default = False,
                        help='run climatology merge, default = False')
    parser.add_argument('--months', dest='months', action='store_true', default = False,
                        help='run monthly merge, default = False')
    parser.add_argument('--pentads', dest='pentads', action='store_true', default = False,
                        help='run pentad merge, default = False')
    parser.add_argument('--start_year', dest='start_year', action='store', default = defaults.START_YEAR,
                        help='which year to start run, default = 1973')
    parser.add_argument('--end_year', dest='end_year', action='store', default = defaults.END_YEAR,
                        help='which year to end run, default = present')
    parser.add_argument('--start_month', dest='start_month', action='store', default = 1,
                        help='which month to start run, default = 1')
    parser.add_argument('--end_month', dest='end_month', action='store', default = 12,
                        help='which month to end run, default = 12')
    parser.add_argument('--doQC', dest='doQC', action='store_true', default = False,
                        help='process the QC information, default = False')
    parser.add_argument('--doBC', dest='doBC', action='store_true', default = False,
                        help='process the bias corrected data, default = False')
    args = parser.parse_args()


    set_up_merge(suffix = str(args.suffix), clims = args.clims, months = args.months, pentads = args.pentads, \
                     start_year = int(args.start_year), end_year = int(args.end_year), \
                     start_month = int(args.start_month), end_month = int(args.end_month), doQC = args.doQC, doBC = args.doBC)

# END
# ************************************************************************
