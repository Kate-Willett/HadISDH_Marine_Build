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

For uncertainty this assumes correlation of r=1 for SLR, SCN, HGT and C and no correlation (r=0) for R, M and TOT


-----------------------
LIST OF MODULES
-----------------------
utils.py

-----------------------
DATA
-----------------------
Input data stored in:
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2noQC/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSERAclimNBC/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim1NBC/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2NBC/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BCtotal/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BChgt/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BCinstr/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BCtotalship/

-----------------------
HOW TO RUN THE CODE
-----------------------
python2.7 merge_day_night.py --suffix relax --clims --months --start_year YYYY --end_year YYYY --start_month MM --end_month MM (OPTIONAL: one of --doQC1it, --doQC2it, --doQC3it, --doBCtotal, --doBCinstr, --doBChgt, + --ShipOnly)
Run for uncertainty (with BCtotal and ShipOnly)
python2.7 merge_day_night.py --suffix relax --months --start_year YYYY --end_year YYYY --start_month MM --end_month MM --doBCtotal --doUSCN --ShipOnly
 (--doUHGT, --doUR, --doUC, --doUM, --doUTOT, --doUSLR)


python2.7 gridding_cam.py --help 
will show all options

--clims - run for the climatologies
--months - run for the monthly files (will need years and months)

-----------------------
OUTPUT
-----------------------
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2noQC/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSERAclimNBC/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim1NBC/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2NBC/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BCtotal/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BChgt/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BCinstr/
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BCtotalship/

-----------------------
VERSION/RELEASE NOTES
-----------------------

Version 3 (9 Oct 2018) Kate Willett
---------
 
Enhancements
This now works with the uncertainty fields which are only present for --doBCtotal --ShipOnly
 
Changes
 
Bug fixes


Version 2 (26 Sep 2016) Kate Willett
---------
 
Enhancements
This can now work with the iterative approach which requires doQCit1, doQCit2 and doQCit3 to set the correct filepaths
It can also work with bias corrected grids which requires --doBCtotal, --doBChgt or --doBCscn
It can also work with --ShipOnly
Look for:
# KATE modified
...
# end
 
Changes
This hard wires the MEAN in places where I think that is sensible, despite settings.doMedian being set to True.
Look for # KATE MEDIAN WATCH
ACTUALLY - A TEST OF np.mean AND np.median ON A 2-ELEMENT ARRAY GIVES THE SAME ANSWER!!!!
 
Bug fixes
set_up_merge had issues with start_year = START_YEAR. I commented out the four time elements as these are all defined in the call
to function and do not need to be redefined here

The output latitudes were one box too high (92.5 to -82.5) so I switched the + for a - to solve this


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
import pdb

import utils
import set_paths_and_vars
defaults = set_paths_and_vars.set()

#************************************************************************
def do_merge(fileroot, mdi, suffix = "relax", clims = False, doMedian = False, TimeFreq = 'M',
# UNC NEW
             doUSLR = False, doUSCN = False, doUHGT = False, doUR = False, doUM = False, doUC = False, doUTOT = False):
    '''
    Merge the _day and _night files

    Do a np.ma.mean or median for the data and a sum for the n_obs and n_grids

    Output with a _both suffix

    :param str fileroot: root for filenames
    :param flt mdi: missing data indicator
    :param str suffix: "relax" or "strict" criteria
    :param bool clims: if climatologies then don't try and process anomalies.
    :param bool doMedian: switch to enforce use of median over means
    :param str TimeFreq: note to say which time resolution we're working with to write out - default M = monthly
# UNC NEW
    :param bool doUSLR: do solar adjustment uncertainties
    :param bool doUSCN: do instrument adjustment uncertainties
    :param bool doUHGT: do height adjustment uncertainties
    :param bool doUR: do rounding uncertainties
    :param bool doUM: do measurement uncertainties
    :param bool doUC: do climatology uncertainties
    :param bool doUTOT: do total uncertainties
    '''

# UNC NEW
    # If there is an uncertainty run set then set uSource to the name of hte uncertainty
    if doUSLR:
        uSource = 'uSLR'
    elif doUSCN:
        uSource = 'uSCN'
    elif doUHGT:
        uSource = 'uHGT'
    elif doUR:
        uSource = 'uR'
    elif doUM:
        uSource = 'uM'
    elif doUC:
        uSource = 'uC'
    elif doUTOT:
        uSource = 'uTOT'

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

                if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
		    shape = list(ncdf_file.variables[var.name+"_"+uSource][:].shape)
		else:
		    shape = list(ncdf_file.variables[var.name][:].shape)
                shape.insert(0, len(OBS_ORDER)+2) # add all the variables
                shape.insert(0, 2) # insert extra dimension to allow day + night

                all_data = np.ma.zeros(shape)

                if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
                    all_data[p, v] = ncdf_file.variables[var.name+"_"+uSource][:]
                else:
		    all_data[p, v] = ncdf_file.variables[var.name][:]

                # get lats/lons of box centres
                lat_centres = ncdf_file.variables["latitude"]
# KATE modified - this results in lats that go from 92.5 to -82,5 so I've switched the + for a -
                latitudes = lat_centres - (lat_centres[1] - lat_centres[0])/2.
                #latitudes = lat_centres + (lat_centres[1] - lat_centres[0])/2.
# end
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
                if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
                    all_data[p, v] = ncdf_file.variables[var.name+"_"+uSource][:]
                else:
		    all_data[p, v] = ncdf_file.variables[var.name][:]

        # and get n_obs and n_grids
        all_data[p, -2] = ncdf_file.variables["n_grids"][:]
        all_data[p, -1] = ncdf_file.variables["n_obs"][:]

    # invert latitudes
    latitudes = latitudes[::-1]
    all_data = all_data[:,:,:,::-1,:]

    # got all the info, now merge
    # If this is an uncertainty field then combine in quadrature with or without correlations
    if doMedian: # THIS IS A BIG PILE OF RUBBISH FOR UNCERTAINTY SO DON'T DO IT
# UNC NEW
        # Assumed correlating at r=1
        if doUSLR | doUSCN | doUHGT | doUC:
            merged_data = utils.bn_median(all_data[:, :len(OBS_ORDER)], axis = 0) / np.sqrt(np.ma.count(all_data[:, :len(OBS_ORDER)], axis = 0))
        # Assumed no correlation r=0
	elif doUR | doUM | doUTOT:
            merged_data = utils.bn_median(all_data[:, :len(OBS_ORDER)], axis = 0) / np.sqrt(np.ma.count(all_data[:, :len(OBS_ORDER)], axis = 0))
        else:
            merged_data = utils.bn_median(all_data[:, :len(OBS_ORDER)], axis = 0)
    else:
        # Assumed correlating at r=1
        if doUSLR | doUSCN | doUHGT | doUC:
            merged_data = np.sqrt(np.ma.power(np.ma.sum(all_data[:, :len(OBS_ORDER)], axis = 0),2.)) / np.sqrt(np.ma.count(all_data[:, :len(OBS_ORDER)], axis = 0))
#            print('Doing correlated mean combo:',merged_data)
#	    pdb.set_trace()
	# Assumed no correlation r=0
	elif doUR | doUM | doUTOT:
            merged_data = np.sqrt(np.ma.sum(np.ma.power(all_data[:, :len(OBS_ORDER)],2.), axis = 0)) / np.sqrt(np.ma.count(all_data[:, :len(OBS_ORDER)], axis = 0))
#            print('Doing uncorrelated mean combo:',merged_data)
#	    pdb.set_trace()
        else:
            merged_data = np.ma.mean(all_data[:, :len(OBS_ORDER)], axis = 0)
#            print('Doing flat mean combo:',merged_data)
#	    pdb.set_trace()

    # and process the grids and observations (split off here so have incorporated latitude inversion)
    n_grids = np.ma.sum(all_data[:, -2], axis = 0)
    n_obs = np.ma.sum(all_data[:, -1], axis = 0)
    n_obs.fill_value = -1
    n_grids.fill_value = -1

    # write the output file
# UNC NEW
    if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
        utils.netcdf_write_unc(uSource, "{}_{}_{}.nc".format(fileroot, "both", suffix), merged_data, n_grids, n_obs, OBS_ORDER, latitudes, longitudes, times, frequency = TimeFreq, \
	                       doUSLR = doUSLR, doUSCN = doUSCN, doUHGT = doUHGT, doUR = doUR, doUM = doUM, doUC = doUC, doUTOT = doUTOT)
    else:
        utils.netcdf_write("{}_{}_{}.nc".format(fileroot, "both", suffix), merged_data, n_grids, n_obs, OBS_ORDER, latitudes, longitudes, times, frequency = TimeFreq)

    # test distribution of obs with grid boxes
    outfile = file("{}_{}_{}.txt".format(fileroot.split("/")[-1], "both", suffix), "w")
    utils.boxes_with_n_obs(outfile, n_obs, merged_data[0], "")

    return # do_merge

#************************************************************************
def get_fileroot(settings, climatology = False, pentads = False, months = [], do3hr = True, time = [], daily = True, stdev = False,
# UNC NEW 
                 doUSLR = False, doUSCN = False, doUHGT = False, doUR = False, doUM = False, doUC = False, doUTOT = False):
    '''
    Get the filename root depending on switches

    :param Settings settings: settings object for paths
    :param bool climatology: for pentad climatology files
    :param bool pentads: for annual pentad files
    :param bool months: for monthly files
    :param bool do3hr: run for pentad climatology files created from 3hrly data
    :param list monthly: pass in [YYYY] or [YYYY, MM] for pentad or monthly files
    :param bool daily: run for monthly grids created from 1x1 daily
    :param bool stdev: run on the standard deviation files from climatology
# UNC NEW
    :param bool doUSLR: run for solar uncertainties
    :param bool doUSCN run for instrument uncertainties
    :param bool doUHGt: run for height uncertainties
    :param bool doUR: run for rounding uncertainties
    :param bool doUM: run for measurement uncertainties
    :param bool doUC: run for climatology uncertainties
    :param bool doUTOT: run for total uncertainties
    
    '''
# UNC NEW
    # If there is an uncertainty run set then set uSource to the name of hte uncertainty
    if doUSLR:
        uSource = 'uSLR'
    elif doUSCN:
        uSource = 'uSCN'
    elif doUHGT:
        uSource = 'uHGT'
    elif doUR:
        uSource = 'uR'
    elif doUM:
        uSource = 'uM'
    elif doUC:
        uSource = 'uC'
    elif doUTOT:
        uSource = 'uTOT'

    if climatology and months != []:
        print "Cannot run both for Climatology files and for Monthly files"
        raise RuntimeError

    if climatology:
        if do3hr:
            if stdev:
                fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_pentad_stdev_from_3hrly"
            else:
                fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_pentad_climatology_from_3hrly"
        else:
            if stdev:
                fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_pentad_stdev"
            else:
                fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_pentad_climatology"

    elif pentads:
        if do3hr:
            fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_pentad_from_3hrly_{}".format(time[0])
        else:
            fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_pentad_{}".format(time[0])

    elif months != []:
# UNC NEW
        if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
            if daily:
                fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_{}_5x5_monthly_from_daily_{}{:02d}".format(uSource, time[0], time[1])
            else:
                fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_{}_5x5_monthly_{}{:02d}".format(uSource, time[0], time[1])
        else:
	    if daily:
                fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_from_daily_{}{:02d}".format(time[0], time[1])
            else:
                fileroot = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_{}{:02d}".format(time[0], time[1])
                

    return fileroot # get_fileroot



#************************************************************************
# KATE modified
def set_up_merge(suffix = "relax", clims = False, months = False, pentads = False, start_year = defaults.START_YEAR, end_year = defaults.END_YEAR, start_month = 1, end_month = 12, 
                 doQC = False, doQC1it = False, doQC2it = False, doQC3it = False, doBC = False, doBCtotal = False, doBChgt = False, doBCscn = False, 
		 doUSLR = False, doUSCN = False, doUHGT = False, doUR = False, doUM = False, doUC = False, doUTOT = False, ShipOnly = False):
#def set_up_merge(suffix = "relax", clims = False, months = False, pentads = False, start_year = defaults.START_YEAR, end_year = defaults.END_YEAR, start_month = 1, end_month = 12, doQC = False, doBC = False):
# end
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
# KATE modified
    :param bool doQC1it: incorporate the QC flags or not
    :param bool doQC2it: incorporate the QC flags or not
    :param bool doQC3it: incorporate the QC flags or not
# end
# KATE modified
    :param bool doBCtotal: work on the total bias corrected data
    :param bool doBChgt: work on the height only bias corrected data
    :param bool doBCscn: work on the screen only bias corrected data
# end
    :param bool doBC: work on the bias corrected data
# UNC NEW
    :param bool doUSLR: work on solar adjustment uncertainty    
    :param bool doUSCN: work on instrument adjustment uncertainty    
    :param bool doUHGT: work on height adjustment uncertainty    
    :param bool doUR: work on rounding uncertainty    
    :param bool doUM: work on measurement uncertainty    
    :param bool doUM: work on climatology uncertainty    
    :param bool doUTOT: work on solar adjustment uncertainty    
# KATE modified
    :param bool ShipOnly: work on the ship only data
# end

# KATE modified    
    NOTE THAT I HAVE OVERWRITTEN settings.doMedian to force MEAN instead
# end
    '''
    
# KATE modified
    settings = set_paths_and_vars.set(doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn, doQC = doQC, doQC1it = doQC1it, doQC2it = doQC2it, doQC3it = doQC3it, \
                                      doUSLR = doUSLR, doUSCN = doUSCN, doUHGT = doUHGT, doUR = doUR, doUM = doUM, doUC = doUC, doUTOT = doUTOT, ShipOnly = ShipOnly)
    #settings = set_paths_and_vars.set(doBC = doBC, doQC = doQC)
# end
    if clims:
        print "Processing Climatologies"
	TimeFreq = 'C' # this is used when writing out netCDF file so needs to be passed to do_merge
        
#        fileroot = get_fileroot(settings, climatology = True)
#        do_merge(fileroot, settings.mdi, suffix, doMedian = settings.doMedian)
        
        fileroot = get_fileroot(settings, climatology = True, do3hr = True)
# KATE MEDIAN WATCH
# KATE modified - forcing MEAN 
        do_merge(fileroot, settings.mdi, suffix, clims = True, doMedian = False, TimeFreq = TimeFreq)
        #do_merge(fileroot, settings.mdi, suffix, clims = True, doMedian = settings.doMedian)
# end
        # and stdev
        print "Processing Standard Deviations"

        fileroot = get_fileroot(settings, climatology = True, do3hr = True, stdev = True)
# KATE MEDIAN WATCH
# KATE modified - forcing MEAN 
        do_merge(fileroot, settings.mdi, suffix, clims = True, doMedian = False, TimeFreq = TimeFreq)
        #do_merge(fileroot, settings.mdi, suffix, clims = True, doMedian = settings.doMedian)
# end

    if pentads:
        print "Processing Pentads"
	TimeFreq = 'P' # this is used when writing out netCDF file so needs to be passed to do_merge
        
#        fileroot = get_fileroot(settings, pentads = True)
#        do_merge(fileroot, settings.mdi, suffix, doMedian = settings.doMedian)
        
        for year in np.arange(start_year, end_year + 1): 
            print year
            fileroot = get_fileroot(settings, pentads = True, do3hr = True, time = [year])
# KATE MEDIAN WATCH
# KATE modified - forcing MEAN 
            do_merge(fileroot, settings.mdi, suffix, doMedian = False, TimeFreq = TimeFreq)
            #do_merge(fileroot, settings.mdi, suffix, doMedian = settings.doMedian)
# end
    if months:
        print "Processing Monthly Files"
	TimeFreq = 'M' # this is used when writing out netCDF file so needs to be passed to do_merge

# KATE modified - START_YEAR not defined - commented these out as they are all set in the call to function
        #start_year = START_YEAR
        #end_year = END_YEAR
        #start_month = 1
        #end_month = 12
# end
        for year in np.arange(start_year, end_year + 1): 
            print year

            for month in np.arange(start_month, end_month + 1):
                print "  {}".format(month)

#                fileroot = get_fileroot(settings, months = True, time = [year, month])
#                do_merge(fileroot, settings.mdi, suffix, doMedian = settings.doMedian)

                fileroot = get_fileroot(settings, months = True, time = [year, month], daily = True, \
# UNC NEW
		doUSLR = doUSLR, doUSCN = doUSCN, doUHGT = doUHGT, doUR = doUR, doUM = doUM, doUC = doUC, doUTOT = doUTOT)
# KATE MEDIAN WATCH
# KATE modified - forcing MEAN 
                do_merge(fileroot, settings.mdi, suffix, doMedian = False, TimeFreq = TimeFreq, \
# UNC NEW
		doUSLR = doUSLR, doUSCN = doUSCN, doUHGT = doUHGT, doUR = doUR, doUM = doUM, doUC = doUC, doUTOT = doUTOT)
                #do_merge(fileroot, settings.mdi, suffix, doMedian = settings.doMedian)
# end

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
                        help='process the height only bias corrected data, default = False')
# end
# UNC NEW - THESE MUST BE RUN WITH --doBCtotal and --ShipOnly
    parser.add_argument('--doUSCN', dest='doUSCN', action='store_true', default = False,
                        help='process the bias corrected data uncertainties for instrument adjustment, default = False')
    parser.add_argument('--doUHGT', dest='doUHGT', action='store_true', default = False,
                        help='process the bias corrected data uncertainties for height adjustment, default = False')
    parser.add_argument('--doUR', dest='doUR', action='store_true', default = False,
                        help='process the bias corrected data uncertainties for rounding, default = False')
    parser.add_argument('--doUM', dest='doUM', action='store_true', default = False,
                        help='process the bias corrected data uncertainties for measurement, default = False')
    parser.add_argument('--doUC', dest='doUC', action='store_true', default = False,
                        help='process the bias corrected data uncertainties for climatology, default = False')
    parser.add_argument('--doUTOT', dest='doUTOT', action='store_true', default = False,
                        help='process the bias corrected data uncertainties combined, default = False')
    parser.add_argument('--doUSLR', dest='doUSLR', action='store_true', default = False,
                        help='process the bias corrected data uncertainties for solar radiation, default = False')

# KATE modified
    parser.add_argument('--ShipOnly', dest='ShipOnly', action='store_true', default = False,
                        help='process the ship platform type only data, default = False')
# end
    args = parser.parse_args()


# KATE modified
# UNC NEW
    set_up_merge(suffix = str(args.suffix), clims = args.clims, months = args.months, pentads = args.pentads, \
                     start_year = int(args.start_year), end_year = int(args.end_year), \
                     start_month = int(args.start_month), end_month = int(args.end_month), \
		     doQC = args.doQC, doQC1it = args.doQC1it, doQC2it = args.doQC2it, doQC3it = args.doQC3it, \
		     doBC = args.doBC, doBCtotal = args.doBCtotal, doBChgt = args.doBChgt, doBCscn = args.doBCscn, \
		     doUSLR = args.doUSLR, doUSCN = args.doUSCN, doUHGT = args.doUHGT, doUR = args.doUR, doUM = args.doUM, doUC = args.doUC, doUTOT = args.doUTOT, \
		     ShipOnly = args.ShipOnly)
    #set_up_merge(suffix = str(args.suffix), clims = args.clims, months = args.months, pentads = args.pentads, \
    #                 start_year = int(args.start_year), end_year = int(args.end_year), \
    #                 start_month = int(args.start_month), end_month = int(args.end_month), doQC = args.doQC, doBC = args.doBC)
# end

# END
# ************************************************************************
