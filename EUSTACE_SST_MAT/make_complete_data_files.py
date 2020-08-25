#!/usr/local/sci/bin/python2.7
#*****************************
#
# convert to complete dataset files (pentad and monthlies)
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
Takes pentad files and monthly files to make single dataset files.

NOTE: The hard coded start year is 1973. If the given start year is different to 1973 then the program opens an existing file to merge with.
      YOU WILL NEED TO CHANGE THE CODE IF YOU WANT TO CREATE A SEPERATE MERGED FILE THAT DOES NOT START IN 1973

-----------------------
LIST OF MODULES
-----------------------
utils.py

-----------------------
DATA
-----------------------
Input data and output data stored in:
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS2/

Requires pentad and 5x5 monthly grids 

-----------------------
HOW TO RUN THE CODE
-----------------------
# NOT CORRECT!!! python2.7 make_complete_data_files.py --suffix relax --period day --do3hr
 both
python2.7 make_complete_data_files.py --suffix relax --months --daily (if monthly_from_daily) --period both --start_year YYYY --end_year YYYY --start_month MM --end_month MM (OPTIONAL: one of --doQC, --doQC1it, --doQC2it, --doQC3it, --doBC)
 day
python2.7 make_complete_data_files.py --suffix relax --months --daily (if monthly_from_daily) --period day --start_year YYYY --end_year YYYY --start_month MM --end_month MM (OPTIONAL: one of --doQC, --doQC1it, --doQC2it, --doQC3it, --doBC)
 night
python2.7 make_complete_data_files.py --suffix relax --months --daily (if monthly_from_daily) --period night --start_year YYYY --end_year YYYY --start_month MM --end_month MM (OPTIONAL: one of --doQC, --doQC1it, --doQC2it, --doQC3it, --doBC)

both for uncertainty (must set --doBCtotal and --ShipOnly)
python2.7 make_complete_data_files.py --suffix relax --months --daily (if monthly_from_daily) --period both --start_year YYYY --end_year YYYY --start_month MM --end_month MM --doUSCN --doBCtotal --ShipOnly
for each of --doUHGT --doUC --doUR --doUM --doUTOT and if I ever get aroudn to it --doUSLR

python2.7 make_complete_data_files.py --help 
will show all options

-----------------------
OUTPUT
-----------------------
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS2/


-----------------------
VERSION/RELEASE NOTES
-----------------------

Version 4 (11 May 2020) Kate Willett
---------
 
Enhancements
This can now work with doNOWHOLE - a bias corrected run with no whole number flagged data
 
Changes
 
Bug fixes


Version 3 (29 Oct 2018) Kate Willett
---------
 
Enhancements
This can now work with either all months and years or append the latest. If the start year is not 1973 then it appends
This can now work with the uncertainty fields (full and append) - I'm keeping each file seperate at the moment - later I may make this code merge the uncertainty fields and data fields
 
Changes
 
Bug fixes

Version 2 (26 Sep 2016) Kate Willett
---------
 
Enhancements
This can now cope with the iterative approach (doQC1it, doQC2it, doQC3it in addition to doQC and doBC)
It can also cope with doBCtotal, doBChgt and doBCscn
It can cope with --ShipOnly options too.
Look for # KATE modified
         ...
	 # end
 
Changes
Currently this produces 'both' files from 87.5 to -87.5 latitude and 'day'/'night' files from -87.5 to 87.5 lat. I have added a loop to switch
the monthly day and night files to be 87.5 to -87.5 for consistency with 'both'. This means that downstream code may need to be changed!!!
 
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
import gc
import pdb

import utils
import set_paths_and_vars
defaults = set_paths_and_vars.set()

# need to merge the pentads (1x1) and the monthlies (5x5)

#************************************************************************
# KATE modified
def combine_files(suffix = "relax", pentads = False, do3hr = False, months = False, daily = False, start_year = defaults.START_YEAR, end_year = defaults.END_YEAR, start_month = 1, end_month = 12, period = "both", 
                  doQC = False, doQC1it = False, doQC2it = False, doQC3it = False, doBC = False, doBCtotal = False, doBChgt = False, doBCscn = False, doNOWHOLE = False,
# UNC NEW		  
		  doUSLR = False, doUSCN = False, doUHGT = False, doUR = False, doUM = False, doUC = False, doUTOT = False, ShipOnly = False):
#def combine_files(suffix = "relax", pentads = False, do3hr = False, months = False, daily = False, start_year = defaults.START_YEAR, end_year = defaults.END_YEAR, start_month = 1, end_month = 12, period = "both", doQC = False, doBC = False):
# end
    '''
    Combine the files, first the pentads 1x1, then the monthlies 5x5

    :param str suffix: "relax" or "strict" criteria
    :param bool pentads: run on pentads
    :param bool do3hr: run on pentads created from 3hrly data (if False then run on those from daily)
    :param bool months: run on 5x5 monthly data
    :param bool daily: run on monthlies created direct from dailies (if False the run on those from 1x1 monthlies)
    :param int start_year: start year to process
    :param int end_year: end year to process
    :param int start_month: start month to process
    :param int end_month: end month to process
    :param str period: which period to do day/night/both?
    :param bool doQC: incorporate the QC flags or not
# KATE modified
    :param bool doQC1it: incorporate the 1st iteration QC flags or not
    :param bool doQC2it: incorporate the 2nd iteration QC flags or not
    :param bool doQC3it: incorporate the 3rd iteration QC flags or not
# end
    :param bool doBC: work on the bias corrected data
# KATE modified
    :param bool doBCtotal: work on the bias corrected data
    :param bool doBChgt: work on the hieght only bias corrected data
    :param bool doBCscn: work on the screen only bias corrected data
# end
    :param bool doNOWHOLE: work on the bias corrected data with no whole number flagged data
# UNC NEW
    :param bool doUSLR: do solar adjustment uncertainties
    :param bool doUSCN: do instrument adjustment uncertainties
    :param bool doUHGT: do height adjustment uncertainties
    :param bool doUR: do rounding uncertainties
    :param bool doUM: do measurement uncertainties
    :param bool doUC: do climatology uncertainties
    :param bool doUTOT: do total uncertainties
# KATE modified
    :param bool ShipOnly: work on the sship platform type only data
# end

    :returns:
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

# KATE modified
    settings = set_paths_and_vars.set(doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn, doNOWHOLE = doNOWHOLE, doQC = doQC, doQC1it = doQC1it, doQC2it = doQC2it, doQC3it = doQC3it, 
                                      doUSLR = doUSLR, doUSCN = doUSCN, doUHGT = doUHGT, doUR = doUR, doUM = doUM, doUC = doUC, doUTOT = doUTOT, ShipOnly = ShipOnly)
    #settings = set_paths_and_vars.set(doBC = doBC, doQC = doQC)
    
    # I've added this to test if there is an existing file to merge with so that it is easy to do annual updates.
    DefaultStartYear = 1973
# end
    # pentads
    # NO UNC SET UP FOR PENTADS AS WE ONLY WORK WITH MONTHS NOW
    if pentads:

        OBS_ORDER = utils.make_MetVars(settings.mdi, multiplier = False)
        # KW make OBS_ORDER only the actual variables - remove anomalies
        NEWOBS_ORDER = []
        for v, var in enumerate(OBS_ORDER):
            if "anomalies" not in var.name:
                NEWOBS_ORDER.append(var)
        del OBS_ORDER
        OBS_ORDER = np.copy(NEWOBS_ORDER)
        del NEWOBS_ORDER     

        # set up the grids
        DELTA=1
        grid_lats = np.arange(-90+DELTA, 90+DELTA, DELTA)
        grid_lons = np.arange(-180+DELTA, 180+DELTA, DELTA)

        Nyears = end_year - start_year + 1

        # read in each variable - memory issues
        for v, var in enumerate(OBS_ORDER):

            print var.name

            all_pentads = np.ma.zeros((1, Nyears, 73, len(grid_lats), len(grid_lons)))
            all_pentads.mask = np.ones((1, Nyears, 73, len(grid_lats), len(grid_lons)))
            all_pentads.fill_value = settings.mdi

            n_obs = np.zeros((Nyears, 73, len(grid_lats), len(grid_lons)))
            n_grids = np.zeros((Nyears, 73, len(grid_lats), len(grid_lons)))


            for y, year in enumerate(np.arange(start_year, end_year + 1)):

                if do3hr:
                    filename = settings.DATA_LOCATION + "{}_1x1_pentad_from_3hrly_{}_{}_{}.nc".format(settings.OUTROOT, year, period, suffix)
                else:
                    filename = settings.DATA_LOCATION + "{}_1x1_pentad_{}_{}_{}.nc".format(settings.OUTROOT, year, period, suffix)

                ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

                time = ncdf_file.variables["time"]

                try:
                    assert time.long_name == "time since 1/1/{} in hours".format(year)

                except AssertionError:
                    print "time units are not as expected."
                    print "    expected time since 1/1/{} in hours".format(year)
                    print "    got {}".format(time.long_name)
                    sys.exit()

                all_pentads[0, y, :, :, :] = ncdf_file.variables[var.name][:]

                n_obs[y, :, :, :] = ncdf_file.variables["n_obs"][:]
                n_grids[y, :, :, :] = ncdf_file.variables["n_obs"][:]

                print year

                if y == 0 and period == "both":
                    lat_centres = ncdf_file.variables["latitude"]
# KATE modified - this results in lats that go from 92.5 to -82,5 or 90.5 to -88.5 so I've switched the + for a -
                    latitudes = lat_centres - (lat_centres[1] - lat_centres[0])/2.
                    #latitudes = lat_centres + (lat_centres[1] - lat_centres[0])/2.
# end
                    lon_centres = ncdf_file.variables["longitude"]
                    longitudes = lon_centres + (lon_centres[1] - lon_centres[0])/2.

                ncdf_file.close()

            all_pentads = all_pentads.reshape(1, -1, len(grid_lats), len(grid_lons))

            # sort the times
            times = utils.TimeVar("time", "time since 1/1/1973 in months", "months", "time")
            times.data = np.arange(all_pentads.shape[1])

            # and write file
            if do3hr:
                out_filename = settings.DATA_LOCATION + "{}_1x1_pentads_from_3hrly_{}_{}_{}.nc".format(settings.OUTROOT, var.name, period, suffix)
            else:
                out_filename = settings.DATA_LOCATION + "{}_1x1_pentads_{}_{}_{}.nc".format(settings.OUTROOT, var.name, period, suffix)

            if period == "both":
                utils.netcdf_write(out_filename, all_pentads, n_grids, n_obs, OBS_ORDER, latitudes, longitudes, times, frequency = "P", single = var)
            else:
                utils.netcdf_write(out_filename, all_pentads, n_grids, n_obs, OBS_ORDER, grid_lats, grid_lons, times, frequency = "P", single = var)


        # Reset the data holding arrays and objects

        del OBS_ORDER
        gc.collect()

    # months
    # UNC SET UP FOR MONTHS!!!
    if months:

        OBS_ORDER = utils.make_MetVars(settings.mdi, multiplier = False)
	
	# KATE ADDED:
	# Test to see if there is an existing merged file to combine with by looking at the given start year compared to the default of 1973
	# If it is different then open the existing file and rewrite it.
	# I'll rewrite it with _new just to check all is well
	if start_year != DefaultStartYear:
	
	    # We must merge with the existing file
# UNC NEW	    
	    # Check first whether we're working on uncertainty fields or not
	    if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
                if daily:
                    filename = settings.DATA_LOCATION + "{}_{}_5x5_monthly_from_daily_{}_{}.nc".format(settings.OUTROOT, uSource, period, suffix)
                else:
                    filename = settings.DATA_LOCATION + "{}_{}_5x5_monthly_{}_{}.nc".format(settings.OUTROOT, uSource, period, suffix)
	    
	    else:
                if daily:
                    filename = settings.DATA_LOCATION + "{}_5x5_monthly_from_daily_{}_{}.nc".format(settings.OUTROOT, period, suffix)
                else:
                    filename = settings.DATA_LOCATION + "{}_5x5_monthly_{}_{}.nc".format(settings.OUTROOT, period, suffix)

            ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

            time = ncdf_file.variables["time"]

            #try:
            #    assert time.long_name == "time since 1/{}/{} in hours".format(month, year)

            #except AssertionError:
            #    print "time units are not as expected."
            #    print "    expected time since 1/{}/{} in hours".format(month, year)
            #    print "    got {}".format(time.long_name)
            #    sys.exit()

            for v, var in enumerate(OBS_ORDER):

# UNC NEW	    
	        # Check first whether we're working on uncertainty fields or not because the var.name is different
	        if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
                    nc_var = ncdf_file.variables[var.name+"_"+uSource]
                else:
                    nc_var = ncdf_file.variables[var.name]

                try:
                    var.data = utils.ma_append(var.data, nc_var[:], axis = 0)

                    if v == 0:
                        n_obs = utils.ma_append(n_obs, ncdf_file.variables["n_obs"][:], axis = 0)
                        n_grids = utils.ma_append(n_grids, ncdf_file.variables["n_grids"][:], axis = 0)

                except AttributeError:
                    var.data = nc_var[:]
                    var.data.fill_value = nc_var.missing_value

                    if v == 0:
                        n_obs = ncdf_file.variables["n_obs"][:]
                        n_grids = ncdf_file.variables["n_grids"][:]

        # This should now just be appended to with the additional months

	    	

        #*****************************
        # monthlies
        for y, year in enumerate(np.arange(start_year, end_year + 1)): 
            print year

            for month in np.arange(start_month, end_month + 1):
                print "   {}".format(month)

# UNC NEW	    
	        # Check first whether we're working on uncertainty fields or not
	        if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
                    if daily:
                        filename = settings.DATA_LOCATION + "{}_{}_5x5_monthly_from_daily_{}{:02d}_{}_{}.nc".format(settings.OUTROOT, uSource, year, month, period, suffix)
                    else:
                        filename = settings.DATA_LOCATION + "{}_{}_5x5_monthly_{}{:02d}_{}_{}.nc".format(settings.OUTROOT, uSource, year, month, period, suffix)
	    
	        else:
                    if daily:
                        filename = settings.DATA_LOCATION + "{}_5x5_monthly_from_daily_{}{:02d}_{}_{}.nc".format(settings.OUTROOT, year, month, period, suffix)
                    else:
                        filename = settings.DATA_LOCATION + "{}_5x5_monthly_{}{:02d}_{}_{}.nc".format(settings.OUTROOT, year, month, period, suffix)

                #pdb.set_trace()
		ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

                time = ncdf_file.variables["time"]

                try:
                    assert time.long_name == "time since 1/{}/{} in hours".format(month, year)

                except AssertionError:
                    print "time units are not as expected."
                    print "    expected time since 1/{}/{} in hours".format(month, year)
                    print "    got {}".format(time.long_name)
                    sys.exit()

                for v, var in enumerate(OBS_ORDER):

# UNC NEW	    
	            # Check first whether we're working on uncertainty fields or not because the var.name is different
	            if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
                        nc_var = ncdf_file.variables[var.name+"_"+uSource]
                    else:
                        nc_var = ncdf_file.variables[var.name]

                    try:
                        var.data = utils.ma_append(var.data, nc_var[:], axis = 0)

                        if v == 0:
                            n_obs = utils.ma_append(n_obs, ncdf_file.variables["n_obs"][:], axis = 0)
                            n_grids = utils.ma_append(n_grids, ncdf_file.variables["n_grids"][:], axis = 0)

                    except AttributeError:
                        var.data = nc_var[:]
                        var.data.fill_value = nc_var.missing_value

                        if v == 0:
                            n_obs = ncdf_file.variables["n_obs"][:]
                            n_grids = ncdf_file.variables["n_grids"][:]


                if y == 0 and month == start_month and period == "both":
                    lat_centres = ncdf_file.variables["latitude"]
                    latitudes = lat_centres + (lat_centres[1] - lat_centres[0])/2.

                    lon_centres = ncdf_file.variables["longitude"]
                    longitudes = lon_centres + (lon_centres[1] - lon_centres[0])/2.

# KATE modified - added an extra loop so that we can flip the latitudes for day and night too
                if y == 0 and month == start_month and period != "both":
                    lat_centres = ncdf_file.variables["latitude"]
                    # THIS IS - RATHER THAN + READY TO FLIP THE LATS
		    latitudes = lat_centres - (lat_centres[1] - lat_centres[0])/2.

                    lon_centres = ncdf_file.variables["longitude"]
                    longitudes = lon_centres + (lon_centres[1] - lon_centres[0])/2.
# end                    
                ncdf_file.close()
            
        # write out into big array for netCDF file
        all_data = np.ma.zeros((len(OBS_ORDER), var.data.shape[0], var.data.shape[1], var.data.shape[2]))
        all_data.mask = np.zeros((len(OBS_ORDER), var.data.shape[0], var.data.shape[1], var.data.shape[2]))

        for v, var in enumerate(OBS_ORDER):
            all_data[v, :, :, :] = var.data

# KATE modified - switching the latitudes on day and night data for consistency with both
        if period == "day" or period == "night":
            # invert latitudes
            latitudes = latitudes[::-1]
            all_data = all_data[:,:,::-1,:] # variable, time, latitude, longitude
# end

        all_data.fill_value = var.data.fill_value

        # extra stuff for writing
# KATE modified - no longer need grid5 as we're using latitudes and longitudes
        #DELTA=5
        #grid5_lats = np.arange(-90+DELTA, 90+DELTA, DELTA)
        #grid5_lons = np.arange(-180+DELTA, 180+DELTA, DELTA)
# end
# KATE modified - START_YEAR not defined, should be start_year
# Test for start_year being different to DefaultStartYear here too - we want this to begin with the DefaultStartYear in the case of a merge
        if start_year != DefaultStartYear:
	    start_year = DefaultStartYear
        times = utils.TimeVar("time", "time since 1/1/{} in months".format(start_year), "months", "time")
        #times = utils.TimeVar("time", "time since 1/1/{} in months".format(START_YEAR), "months", "time")
# end
        times.data = np.arange(var.data.shape[0])

# UNC NEW	    
	# Check first whether we're working on uncertainty fields or not because the var.name is different
	if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
            # and write file
            if daily:
                out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_{}_5x5_monthly_from_daily_{}_{}_new.nc".format(uSource, period, suffix)
            else:
                out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_{}_5x5_monthly_{}_{}.nc".format(uSource, period, suffix)
        else:
	    # and write file
            if daily:
                out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_from_daily_{}_{}_new.nc".format(period, suffix)
            else:
                out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_{}_{}.nc".format(period, suffix)

# KATE modified - now always using latitudes and longitudes
# UNC NEW	    
	# Check first whether we're working on uncertainty fields or not because the var.name is different
	if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
	    utils.netcdf_write_unc(uSource, out_filename, all_data, n_grids, n_obs, OBS_ORDER, latitudes, longitudes, times, frequency = "Y",
	                           doUSLR = doUSLR, doUSCN = doUSCN, doUHGT = doUHGT, doUR = doUR, doUM = doUM, doUC = doUC, doUTOT = doUTOT)
	else:
	    utils.netcdf_write(out_filename, all_data, n_grids, n_obs, OBS_ORDER, latitudes, longitudes, times, frequency = "Y")
        #if period == "both":
        #    utils.netcdf_write(out_filename, all_data, n_grids, n_obs, OBS_ORDER, latitudes, longitudes, times, frequency = "Y")
        #else:
        #    utils.netcdf_write(out_filename, all_data, n_grids, n_obs, OBS_ORDER, grid5_lats, grid5_lons, times, frequency = "Y")
# end
        

    return # combine_files

#************************************************************************
if __name__=="__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--suffix', dest='suffix', action='store', default = "relax",
                        help='"relax" or "strict" completeness, default = relax')
    parser.add_argument('--pentads', dest='pentads', action='store_true', default = False,
                        help='run on pentads data, default = False')
    parser.add_argument('--do3hr', dest='do3hr', action='store_true', default = False,
                        help='run on 3hr --> pentad data (rather than daily --> pentad), default = False')
    parser.add_argument('--months', dest='months', action='store_true', default = False,
                        help='run 5x5 monthly data, default = False')
    parser.add_argument('--daily', dest='daily', action='store_true', default = False,
                        help='run on daily --> monthly data (rather than 1x1 monthly --> 5x5 monthly), default = False')
    parser.add_argument('--start_year', dest='start_year', action='store', default = defaults.START_YEAR,
                        help='which year to start run, default = 1973')
    parser.add_argument('--end_year', dest='end_year', action='store', default = defaults.END_YEAR,
                        help='which year to end run, default = present')
    parser.add_argument('--start_month', dest='start_month', action='store', default = 1,
                        help='which month to start run, default = 1')
    parser.add_argument('--end_month', dest='end_month', action='store', default = 12,
                        help='which month to end run, default = 12')
    parser.add_argument('--period', dest='period', action='store', default = "both",
                        help='which period to run for (day/night/both), default = "both"')
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
    parser.add_argument('--doNOWHOLE', dest='doNOWHOLE', action='store_true', default = False,
                        help='process the bias corrected data with whole number flagged data removed, default = False')
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
                        help='process the ship platform type data only, default = False')
# end
    args = parser.parse_args()


    combine_files(suffix = str(args.suffix), months = args.months, daily = args.daily, pentads = args.pentads, do3hr = args.do3hr, \
                      start_year = int(args.start_year), end_year = int(args.end_year), \
                      start_month = int(args.start_month), end_month = int(args.end_month), period = str(args.period),\
# KATE modified
                      doQC = args.doQC, doQC1it = args.doQC1it, doQC2it = args.doQC2it, doQC3it = args.doQC3it, \
		      doBC = args.doBC, doBCtotal = args.doBCtotal, doBChgt = args.doBChgt, doBCscn = args.doBCscn, doNOWHOLE = args.doNOWHOLE, \
# UNC NEW		      
		      doUSLR = args.doUSLR, doUSCN = args.doUSCN, doUHGT = args.doUHGT, doUR = args.doUR, doUM = args.doUM, doUC = args.doUC, doUTOT = args.doUTOT, \
		      ShipOnly = args.ShipOnly)
                      #doQC = args.doQC, doBC = args.doBC)
# end
