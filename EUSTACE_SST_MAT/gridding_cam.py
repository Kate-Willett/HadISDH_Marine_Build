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
# 1x1 monthly - no longer goes through this step
5x5 monthly

and also 5x5 monthly calculated directly from the 1x1 daily data.  

These later grids are available for all, day- and night-time periods (any mixtures are assigned to daytime) and also using strict and relaxed completeness criteria.

This can work with raw, QC only, bias corrected, bias corrected height only, bias corrected instrument only, ship only, and each individual uncertainty field.
Gridded uncertainties will account for correlation over the gridbox in the individual quantities only. This will not be possible for uncTOT. Total uncertainty (with correlation) 
will have to be calculated by combining all gridded individual uncertainties.

-----------------------
LIST OF MODULES
-----------------------
utils.py
set_paths_and_vars.py - set file paths and some universal variables.
plot_qc_diagnostics.py - to output plots of clean obs vs all
MDS_RWtools.py - for the file format


-----------------------
DATA
-----------------------
Input data stored in:
/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/

Exact folder set by "OUTROOT" - as depends on bias correction.

-----------------------
HOW TO RUN THE CODE
-----------------------
# for all data
python2.7 gridding_cam.py --suffix relax --period day --start_year YYYY --end_year YYYY --start_month MM --end_month MM

# for QC data only
python2.7 gridding_cam.py --suffix relax --period day --start_year YYYY --end_year YYYY --start_month MM --end_month MM --doQC (--ShipOnly)

# for BC data only
python2.7 gridding_cam.py --suffix relax --period day --start_year YYYY --end_year YYYY --start_month MM --end_month MM --doBCtotal (--doBCscn, --doBChgt, --doNOWHOLE) (--ShipOnly)

# for uncertainty data only
python2.7 gridding_cam.py --suffix relax --period day --start_year YYYY --end_year YYYY --start_month MM --end_month MM --doBCtotal --doUSLR (--doUSCN, --doUHGT, --doUR, --doUM, --doUC, --doUTOT) (--ShipOnly)

python2.7 gridding_cam.py --help 
will show all options

-----------------------
OUTPUT
-----------------------
# *** KATE ADDED:
First iteration reads in ERAclimNBC, does NOT include buddy QC flag, and outputs to GRIDSERAclimNBC:
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDSERAclimNBC/
Second iteration reads in OBSclim1NBC, does NOT include buddy QC flag, and outputs to GRIDSOBSclim1NBC:
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDSOBSclim1NBC/
Third iteration reads in OBSclim2NBC, DOES include buddy QC flag, and outpus to GRIDSOBSclim2NBC:
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDSOBSclim2NBC/
We then grid the bias corrected version of OBSclim2NBC so reads in from OBSclim2BC and outputs to GRIDSOBSclim2BC:
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDSOBSclim2BC/
THIS NOW INCLUDES OBS UNCERTAINTY!!!
We also grid up a noQC version for comparison but one that uses teh OBSclim2 base data (obs based climatology) 
so reads in from OBSclim2NBC and outputs to GRIDSOBSclim2noQC:
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDSOBSclim2noQC/

and the plots:
First iteration reads in ERAclimNBC, does NOT include buddy QC flag, and outputs to GRIDSERAclimNBC:
/project/hadobs2/hadisdh/marine/PLOTSERAclimNBC/
Second iteration reads in OBSclim1NBC, does NOT include buddy QC flag, and outputs to GRIDSOBSclim1NBC:
/project/hadobs2/hadisdh/marine/PLOTSOBSclim1NBC/
Third iteration reads in OBSclim2NBC, DOES include buddy QC flag, and outpus to GRIDSOBSclim2NBC:
/project/hadobs2/hadisdh/marine/PLOTSOBSclim2NBC/
We then grid the bias corrected version of OBSclim2NBC so reads in from OBSclim2BC and outputs to GRIDSOBSclim2BC:
/project/hadobs2/hadisdh/marine/PLOTSOBSclim2BC/
We also grid up a noQC version for comparison but one that uses teh OBSclim2 base data (obs based climatology) 
so reads in from OBSclim2NBC and outputs to GRIDSOBSclim2noQC:
/project/hadobs2/hadisdh/marine/PLOTSOBSclim2noQC/
#*** end

/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS2/

Plots to appear in 
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/PLOTS2/

# And everything linked to uncertainty (# UNC NEW)

-----------------------
VERSION/RELEASE NOTES
-----------------------

Version 4 (7 May 2020) Kate Willett
---------
 
Enhancements
This now does a NOWHOLE version which grids the BCtotal ShipOnly (optional) values that have not been given a whole number flag
 
Changes

Bug fixes


Version 3 (24 Sep 2018) Kate Willett
---------
 
Enhancements
This now reads in obs uncertainty for the BC versions and propgates these through the gridding.
This has to be done individually for each source though because it takes up too much memory.
 
Changes

Bug fixes


Version 2 (26 Sep 2016) Kate Willett
---------
 
Enhancements
This can now cope with three different types of QC in addition to existing:
doQC1it, doQC2it and doQC3it - for working with ERA, then OBS clims versions
It can also work with: 
  the full BC version - now doBCtotal,
  the height correction only - now doBCght
  the screen correction only - now doBCscn
I have also set this up to work with ship only data which required changes to utils.py and set_paths_and_vars.py
Look for # KATE modified
         ...
	 # end
 
Changes
STREAMLINED OUTPUTS
I have commented out the monthy 1x1s and monthly 5x5s from monthly 1x1s as these are no longer needed

MEAN OVER MEDIAN
I have hard coded in the MEAN for creating daily 1x1s and monthly 5x5s because I think this is more sensible
Look for # KATE MEDIAN WATCH

SWITCH OFF UNESSENTIAL OUTPUTS
I have added an internally operated switch - SwitchOutput - 1 = output all interim grids, 0 only output 5x5monthlies

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
import matplotlib
matplotlib.use('Agg') 
import calendar
import gc
import copy

import utils
import plot_qc_diagnostics
import MDS_RWtools as mds
import set_paths_and_vars
defaults = set_paths_and_vars.set()

# Kate MODIFIED
import pdb
# end

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

# what size grid (lat/lon/hour)
DELTA_LAT = 1
DELTA_LON = 1
DELTA_HOUR = 3

# set up the grid
grid_lats = np.arange(-90 + DELTA_LAT, 90 + DELTA_LAT, DELTA_LAT)
grid_lons = np.arange(-180 + DELTA_LON, 180 + DELTA_LON, DELTA_LON)

# KATE modified
# Make this 1 if you want to run in test mode - outputting all interim files and plots
# Make this 0 if you want to run in operational mode - only output 5x5 monthly files and plots
SwitchOutput = 0

# end


#************************************************************************
# KATE modified    
def do_gridding(suffix = "relax", start_year = defaults.START_YEAR, end_year = defaults.END_YEAR, start_month = 1, end_month = 12, 
                doQC = False, doQC1it = False, doQC2it = False, doQC3it = False, doSST_SLP = False, 
		doBC = False, doBCtotal = False, doBChgt = False, doBCscn = False, doNOWHOLE = False,
		doUSLR = False, doUSCN = False, doUHGT = False, doUR = False, doUM = False, doUC = False, doUTOT = False,
		ShipOnly = False):
#def do_gridding(suffix = "relax", start_year = defaults.START_YEAR, end_year = defaults.END_YEAR, start_month = 1, end_month = 12, doQC = False, doSST_SLP = False, doBC = False, doUncert = False):
# end
    '''
    Do the gridding, first to 3hrly 1x1, then to daily 1x1 and finally monthly 5x5

    :param str suffix: "relax" or "strict" criteria
    :param int start_year: start year to process
    :param int end_year: end year to process
    :param int start_month: start month to process
    :param int end_month: end month to process
    :param bool doQC: incorporate the QC flags or not
# KATE modified    
    :param bool doQC1it: incorporate the first iteration (no buddy) QC flags or not
    :param bool doQC2it: incorporate the second iteration (no buddy) QC flags or not
    :param bool doQC3it: incorporate the third iteration (buddy) QC flags or not
# end
    :param bool doSST_SLP: process additional variables or not
    :param bool doBC: work on the bias corrected data
# KATE modified    
    :param bool doBCtotal: work on the full bias corrected data and maybe uncertainty
    :param bool doBChgt: work on the height only bias corrected data
    :param bool doBCscn: work on the screen only bias corrected data
# end
    :param bool doNOWHOLE: work on the bias corrected data that doesn't have any whole number flags set
# UNC NEW
    :param bool doUSLR: work on BC and solar adj uncertainty with correlation
    :param bool doUSCN: work on BC and instrument adj uncertainty with correlation
    :param bool doUHGT: work on BC and height adj uncertainty with correlation
    :param bool doUR: work on BC and rounding uncertainty with no correlation
    :param bool doUM: work on BC and measurement uncertainty with no correlation
    :param bool doUC: work on BC and climatological uncertainty with no correlation
    :param bool doUTOT: work on BC and total uncertainty with no correlation
# KATE modified    
    :param bool ShipOnly: work on the ship platform type only data
# end

    :returns:
    '''
# KATE modified    
    settings = set_paths_and_vars.set(doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn, doNOWHOLE = doNOWHOLE, doQC = doQC, doQC1it = doQC1it, doQC2it = doQC2it, doQC3it = doQC3it, 
                                      doUSLR = doUSLR, doUSCN = doUSCN, doUHGT = doUHGT, doUR = doUR, doUM = doUM, doUC = doUC, doUTOT = doUTOT, ShipOnly = ShipOnly)
    #settings = set_paths_and_vars.set(doBC = doBC, doQC = doQC)
# end


# KATE modified  - added other BC options  
#    if doBC:
    if doBC | doBCtotal | doBChgt | doBCscn | doNOWHOLE:
# end
        fields = mds.TheDelimitersExt # extended (BC)
# UNC NEW
        if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
	    uncfields = mds.TheDelimitersUnc # uncertainty fields (BC)	
    else:
        fields = mds.TheDelimitersStd # Standard

# KATE modified  - added other BC options  
#    OBS_ORDER = utils.make_MetVars(settings.mdi, doSST_SLP = doSST_SLP, multiplier = True, doBC = doBC) # ensure that convert from raw format at writing stage with multiplier
    OBS_ORDER = utils.make_MetVars(settings.mdi, doSST_SLP = doSST_SLP, multiplier = True, doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn, doNOWHOLE = doNOWHOLE) # ensure that convert from raw format at writing stage with multiplier
# end

    # KW switching between 4 ('_strict') for climatology build and 2 for anomaly buily ('_relax') - added subscripts to files
    if suffix == "relax":
        N_OBS_DAY = 2 # KW ok for anomalies but this was meant to be 4 for dailies_all? and 2 for dailies_night/day?
        N_OBS_FRAC_MONTH = 0.3

    elif suffix == "strict":
        N_OBS_DAY = 4
        N_OBS_FRAC_MONTH = 0.3


    # flags to check on and values to allow through
# KATE modified
    if doQC1it | doQC2it:
        these_flags = {"ATclim":0,"ATrep":0,"DPTclim":0,"DPTssat":0,"DPTrep":0,"DPTrepsat":0}
    elif doNOWHOLE: # this should now pull through only those without rounding / whole number flags set
        these_flags = {"ATbud":0, "ATclim":0,"ATround":0,"ATrep":0,"DPTbud":0,"DPTclim":0,"DPTround":0,"DPTssat":0,"DPTrep":0,"DPTrepsat":0}    
    else:
        these_flags = {"ATbud":0, "ATclim":0,"ATrep":0,"DPTbud":0,"DPTclim":0,"DPTssat":0,"DPTrep":0,"DPTrepsat":0}    
    #these_flags = {"ATbud":0, "ATclim":0,"ATrep":0,"DPTbud":0,"DPTclim":0,"DPTssat":0,"DPTrep":0,"DPTrepsat":0}
# end

    # spin through years and months to read files
    for year in np.arange(start_year, end_year + 1): 

        for month in np.arange(start_month, end_month + 1):

            times = utils.TimeVar("time", "time since 1/{}/{} in hours".format(month, year), "hours", "time")

            grid_hours = np.arange(0, 24 * calendar.monthrange(year, month)[1], DELTA_HOUR)

            times.data = grid_hours

            # process the monthly file
# KATE modified  - added other BC options  
#            if doBC:
            if doBC | doBCtotal | doBChgt | doBCscn | doNOWHOLE:
# end
                filename = "new_suite_{}{:02d}_{}_extended.txt".format(year, month, settings.OUTROOT)
# UNC NEW
                if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
         	    uncfilename = "new_suite_{}{:02d}_{}_uncertainty.txt".format(year, month, settings.OUTROOT)		
            else:
                filename = "new_suite_{}{:02d}_{}.txt".format(year, month, settings.OUTROOT)

#            pdb.set_trace()
# KATE modified  - added other BC options  
#            raw_platform_data, raw_obs, raw_meta, raw_qc = utils.read_qc_data(filename, settings.ICOADS_LOCATION, fields, doBC = doBC)
            raw_platform_data, raw_obs, raw_meta, raw_qc = utils.read_qc_data(filename, settings.ICOADS_LOCATION, fields, doBC = doBC, 
	                                                   doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn, doNOWHOLE = doNOWHOLE, ShipOnly = ShipOnly)
# end
# UNC NEW
            if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT: # Read in the uncertainty info but only if we're doing a full BC run
	        
		unc_data = utils.read_unc_data(uncfilename, settings.ICOADS_LOCATION, uncfields, 
		                               doUSLR = doUSLR, doUSCN = doUSCN, doUHGT = doUHGT, doUR = doUR, doUM = doUM, doUC = doUC, doUTOT = doUTOT,
					       ShipOnly = ShipOnly)

            # extract observation details
            lats, lons, years, months, days, hours = utils.process_platform_obs(raw_platform_data)

            # test dates *KW - SHOULDN'T NEED THIS - ONLY OBS PASSING DATE CHECK ARE INCLUDED*
            #  *RD* - hasn't run yet but will leave it in just in case of future use.
            if not utils.check_date(years, year, "years", filename):
                sys.exit(1)
            if not utils.check_date(months, month, "months", filename):
                sys.exit(1)

# KATE modified - seems to be an error with missing global name plots so have changed to settings.plots
            # Choose this one to only output once per decade
	    #if settings.plots and (year in [1973, 1983, 1993, 2003, 2013]):
	    # Choose this one to output a plot for each month
            if settings.plots:
            #if plots and (year in [1973, 1983, 1993, 2003, 2013]):
# end
                # plot the distribution of hours

                import matplotlib.pyplot as plt

                plt.clf()
                plt.hist(hours, np.arange(-100,2500,100))
                plt.ylabel("Number of observations")
                plt.xlabel("Hours")
                plt.xticks(np.arange(-300, 2700, 300))
                plt.savefig(settings.PLOT_LOCATION + "obs_distribution_{}{:02d}_{}.png".format(year, month, suffix))


                # only for a few of the variables
                for variable in OBS_ORDER:
                    if variable.name in ["marine_air_temperature", "dew_point_temperature", "specific_humidity", "relative_humidity", "marine_air_temperature_anomalies", "dew_point_temperature_anomalies", "specific_humidity_anomalies", "relative_humidity_anomalies"]:

                        #plot_qc_diagnostics.values_vs_lat(variable, lats, raw_obs[:, variable.column], raw_qc, these_flags, settings.PLOT_LOCATION + "qc_actuals_{}_{}{:02d}_{}.png".format(variable.name, year, month, suffix), multiplier = variable.multiplier, doBC = doBC)
                        plot_qc_diagnostics.values_vs_lat_dist(variable, lats, raw_obs[:, variable.column], raw_qc, these_flags, \
			        settings.PLOT_LOCATION + "qc_actuals_{}_{}{:02d}_{}.png".format(variable.name, year, month, suffix), multiplier = variable.multiplier, \
# KATE modified  - added other BC options  
				doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn, doNOWHOLE = doNOWHOLE)
# end

            # QC sub-selection
	    
# KATE modified - added QC iterations but also think this needs to include the bias corrected versions because the QC flags need to be applied to those too.
# Not sure what was happening previously with the doBC run - any masking to QC'd obs?
            if doQC | doQC1it | doQC2it | doQC3it | doBC | doBCtotal | doBChgt | doBCscn | doNOWHOLE:
            #if doQC:
# end
                print "Using {} as flags".format(these_flags)
# KATE modified - BC options
#                mask = utils.process_qc_flags(raw_qc, these_flags, doBC = doBC)
                mask = utils.process_qc_flags(raw_qc, these_flags, doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn, doNOWHOLE = doNOWHOLE)
# end
		print "All Obs: ",len(mask)
		print "Good Obs: ",len(mask[np.where(mask == 0)])
		print "Bad Obs: ",len(mask[np.where(mask == 1)])
		#pdb.set_trace()
		

                complete_mask = np.zeros(raw_obs.shape)
                for i in range(raw_obs.shape[1]):
                    complete_mask[:,i] = mask
                clean_data = np.ma.masked_array(raw_obs, mask = complete_mask)
		del raw_obs
# UNC NEW
                if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT: #		    
		    unc_complete_mask = np.zeros(unc_data.shape)
		    for i in range(unc_data.shape[1]):
                        unc_complete_mask[:,i] = mask
		    unc_clean_data = np.ma.masked_array(unc_data, mask = unc_complete_mask)
		    del unc_data
		    gc.collect()
# end
            else:
                print "No QC flags selected"
                clean_data = np.ma.masked_array(raw_obs, mask = np.zeros(raw_obs.shape))
		del raw_obs
		gc.collect()


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
# UNC NEW 
            if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT: #
	        raw_month_grid, unc_grid, raw_month_n_obs, this_month_period = utils.grid_1by1_cam_unc(clean_data, unc_clean_data, \
		                                                                             raw_qc, hours_since, lat_index, lon_index, grid_hours, grid_lats, grid_lons, OBS_ORDER, settings.mdi, doMedian = settings.doMedian, \
											     doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn, \
											     doUSLR = doUSLR, doUSCN = doUSCN, doUHGT = doUHGT, doUR = doUR, doUM = doUM, doUC = doUC, doUTOT = doUTOT)
	        del clean_data
	        del unc_clean_data
		gc.collect()
		
	    else:	    
# KATE MEDIAN WATCH This is hard coded to doMedian (rather than settings.doMedian) - OK WITH MEDIAN HERE!!!
# KATE modified - to add settings.doMedian instead of just doMedian which seems to be consistent with the other bits and BC options
	        raw_month_grid, raw_month_n_obs, this_month_period = utils.grid_1by1_cam(clean_data, raw_qc, hours_since, lat_index, lon_index, \
	              grid_hours, grid_lats, grid_lons, OBS_ORDER, settings.mdi, doMedian = settings.doMedian, \
		      doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn, doNOWHOLE = doNOWHOLE)
	    #raw_month_grid, raw_month_n_obs, this_month_period = utils.grid_1by1_cam(clean_data, raw_qc, hours_since, lat_index, lon_index, grid_hours, grid_lats, grid_lons, OBS_ORDER, settings.mdi, doMedian = True, doBC = doBC)
# end
                del clean_data
		gc.collect()
            print "successfully read data into 1x1 3hrly grids"

            # create matching array size
            this_month_period = np.tile(this_month_period, (len(OBS_ORDER),1,1,1))

            for period in ["all", "day", "night"]:

                if period == "day":
                    this_month_grid = np.ma.masked_where(this_month_period == 1, raw_month_grid)
                    this_month_obs = np.ma.masked_where(this_month_period[0] == 1, raw_month_n_obs) # and take first slice to re-match the array size
# UNC NEW
                    if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT: #                        
		        unc_this_month_grid = np.ma.masked_where(this_month_period == 1, unc_grid)
                elif period == "night":
                    this_month_grid = np.ma.masked_where(this_month_period == 0, raw_month_grid)
                    this_month_obs = np.ma.masked_where(this_month_period[0] == 0, raw_month_n_obs) # and take first slice to re-match the array size
# UNC NEW
                    if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT: #                        
		        unc_this_month_grid = np.ma.masked_where(this_month_period == 0, unc_grid)
                else:
                    this_month_grid = copy.deepcopy(raw_month_grid)
                    this_month_obs = copy.deepcopy(raw_month_n_obs)
# UNC NEW
                    if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT: #                        
                        unc_this_month_grid = copy.deepcopy(unc_grid)
                       
                print('Set up period: ',period)
  
# KATE modified
                # If SwitchOutput == 1 then we're in test mode - output interim files!!!
		if (SwitchOutput == 1):
		    # have one month of gridded data.
                    out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_3hr_{}{:02d}_{}_{}.nc".format(year, month, period, suffix)              

                    utils.netcdf_write(out_filename, this_month_grid, np.zeros(this_month_obs.shape), this_month_obs, OBS_ORDER, grid_lats, grid_lons, times, frequency = "H")
		## have one month of gridded data.
                #out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_3hr_{}{:02d}_{}_{}.nc".format(year, month, period, suffix)              

                #utils.netcdf_write(out_filename, this_month_grid, np.zeros(this_month_obs.shape), this_month_obs, OBS_ORDER, grid_lats, grid_lons, times, frequency = "H")
# end
                # now average over time
                # Dailies
                daily_hours = grid_hours.reshape(-1, 24/DELTA_HOUR)

                shape = this_month_grid.shape
                this_month_grid = this_month_grid.reshape(shape[0], -1, 24/DELTA_HOUR, shape[2], shape[3])
                this_month_obs = this_month_obs.reshape(-1, 24/DELTA_HOUR, shape[2], shape[3])
# UNC NEW
                if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT: #                        
                    unc_this_month_grid = unc_this_month_grid.reshape(shape[0], -1, 24/DELTA_HOUR, shape[2], shape[3])

                print('Reshaped daily grids')

# KATE MEDIAN WATCH - settings.doMedian is generally set to True - I think we may want the MEAN HERE!!!
# KATE modified - to hard wire in MEAN here
                daily_grid = np.ma.mean(this_month_grid, axis = 2)
                #if settings.doMedian:
                #    daily_grid = np.ma.median(this_month_grid, axis = 2)
                #else:
                #    daily_grid = np.ma.mean(this_month_grid, axis = 2)
# end
                daily_grid.fill_value = settings.mdi

                # filter on number of observations/day
                n_hrs_per_day = np.ma.count(this_month_grid, axis = 2) 
                n_obs_per_day = np.ma.sum(this_month_obs, axis = 1) 

# UNC NEW
# PROPAGATE UNCERTAINTY IN THE MEAN np.sqrt(np.sum(np.power(arr,2.))) np.sqrt(np.ma.sum(np.ma.power(uncTOT_clean_data[locs, :][:, cols],2.), axis = 0))
# Use n_hrs_per_day because we're combining the already propagated uncertainties at the 1by1 3hr level, not from all individual obs
                # if its correlated (r=1) do it like this
		if doUSLR | doUSCN | doUHGT | doUC: #                        
# John K thinks it should be divude by N, not SQRT(N)
#                    unc_daily_grid = np.sqrt(np.ma.power(np.ma.sum(unc_this_month_grid, axis = 2),2.)) / np.sqrt(n_hrs_per_day)
                    unc_daily_grid = np.sqrt(np.ma.power(np.ma.sum(unc_this_month_grid, axis = 2),2.)) / n_hrs_per_day
                    unc_daily_grid.fill_value = settings.mdi

                # if its NOT correlated (r=0) do it like this
		if doUR | doUM | doUTOT: #                        
# John K thinks it should be divude by N, not SQRT(N)
#                    unc_daily_grid = np.sqrt(np.ma.sum(np.ma.power(unc_this_month_grid, 2.), axis = 2)) / np.sqrt(n_hrs_per_day)
                    unc_daily_grid = np.sqrt(np.ma.sum(np.ma.power(unc_this_month_grid, 2.), axis = 2)) / n_hrs_per_day
                    unc_daily_grid.fill_value = settings.mdi


                print('Built daily grids')

                if period == "all":
                    bad_locs = np.where(n_hrs_per_day < N_OBS_DAY) # at least 2 of possible 8 3-hourly values (6hrly data *KW OR AT LEAST 4 3HRLY OBS PRESENT*)
                else:
                    bad_locs = np.where(n_hrs_per_day < np.floor(N_OBS_DAY / 2.)) # at least 1 of possible 8 3-hourly values (6hrly data *KW OR AT LEAST 4 3HRLY OBS PRESENT*)              
                daily_grid.mask[bad_locs] = True
# UNC NEW
                if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT: #                        
                    unc_daily_grid.mask[bad_locs] = True

                print('Masked daily grids where few obs')

# KATE modified - added SwitchOutput to if loop
                if (SwitchOutput == 1) and settings.plots and (year in [1973, 1983, 1993, 2003, 2013]):
                #if settings.plots and (year in [1973, 1983, 1993, 2003, 2013]):
# end
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
                    plt.savefig(settings.PLOT_LOCATION + "n_grids_1x1_daily_{}{:02d}_{}_{}.png".format(year, month, period, suffix))

                    plt.clf()
                    plt.hist(n_obs_per_day.reshape(-1), bins = np.arange(-5,100,5),  log = True, rwidth=0.5)                 
                    plt.title("Total number of raw observations in each 1x1 daily grid box")
                    plt.xlabel("Number of raw observations")
                    plt.ylabel("Frequency (log scale)")
                    plt.savefig(settings.PLOT_LOCATION + "n_obs_1x1_daily_{}{:02d}_{}_{}.png".format(year, month, period, suffix))

                # clear up memory
                del this_month_grid
                del this_month_obs
# UNC NEW
                if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT: #                        
                    del unc_this_month_grid
		
                gc.collect()

# KATE modified
                # If SwitchOutput == 1 then we're in test mode - output interim files!!!
		if (SwitchOutput == 1):
                    # write dailies file
                    times.data = daily_hours[:,0]
                    out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_daily_{}{:02d}_{}_{}.nc".format(year, month, period, suffix)

                    utils.netcdf_write(out_filename, daily_grid, n_hrs_per_day[0], n_obs_per_day, OBS_ORDER, grid_lats, grid_lons, times, frequency = "D")
                #times.data = daily_hours[:,0]
                #out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_daily_{}{:02d}_{}_{}.nc".format(year, month, period, suffix)

                #utils.netcdf_write(out_filename, daily_grid, n_hrs_per_day[0], n_obs_per_day, OBS_ORDER, grid_lats, grid_lons, times, frequency = "D")
# end
                # Monthlies
                times.data = daily_hours[0,0]

# KATE modified - commenting out as we don't need this anymore
#                if settings.doMedian:
#                    monthly_grid = np.ma.median(daily_grid, axis = 1)
#                else:
#                    monthly_grid = np.ma.mean(daily_grid, axis = 1)
#
#                monthly_grid.fill_value = settings.mdi
#
#                # filter on number of observations/month
#                n_grids_per_month = np.ma.count(daily_grid, axis = 1) 
#                bad_locs = np.where(n_grids_per_month < calendar.monthrange(year, month)[1] * N_OBS_FRAC_MONTH) # 30% of possible daily values
#                monthly_grid.mask[bad_locs] = True
#
#                # number of raw observations
#                n_obs_per_month = np.ma.sum(n_obs_per_day, axis = 0)
#
#                if settings.plots and (year in [1973, 1983, 1993, 2003, 2013]):
#                    # plot the distribution of days
#
#                    plt.clf()
#                    plt.hist(n_obs_per_month.reshape(-1), bins = np.arange(-10,500,10),  log = True, rwidth=0.5)
#                    plt.title("Total number of raw observations in each 1x1 monthly grid box")
#                    plt.xlabel("Number of raw observations")
#                    plt.ylabel("Frequency (log scale)")
#                    plt.savefig(settings.PLOT_LOCATION + "n_obs_1x1_monthly_{}{:02d}_{}_{}.png".format(year, month, period, suffix))
#
#                    plt.clf()
#                    plt.hist(n_grids_per_month[0].reshape(-1), bins = np.arange(-2,40,2), align = "left",  log = True, rwidth=0.5)
#                    plt.axvline(x = calendar.monthrange(year, month)[1] * N_OBS_FRAC_MONTH, color="r")
#                    plt.title("Total number of 1x1 daily grids in each 1x1 monthly grid")
#                    plt.xlabel("Number of 1x1 daily grids")
#                    plt.ylabel("Frequency (log scale)")
#                    plt.savefig(settings.PLOT_LOCATION + "n_grids_1x1_monthly_{}{:02d}_{}_{}.png".format(year, month, period, suffix))
#
#                # write monthly 1x1 file
#                out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_1x1_monthly_{}{:02d}_{}_{}.nc".format(year, month, period, suffix)
#                utils.netcdf_write(out_filename, monthly_grid, n_grids_per_month[0], n_obs_per_month, OBS_ORDER, grid_lats, grid_lons, times, frequency = "M")
#            
#                # now to re-grid to coarser resolution
#                # KW # Here we may want to use the mean because its a large area but could be sparsely
#                #             populated with quite different climatologies so we want 
#                # the influence of the outliers (we've done our best to ensure these are good values) 
#
#                # go from monthly 1x1 to monthly 5x5 - retained as limited overhead
#                monthly_5by5, monthly_5by5_n_grids, monthly_5by5_n_obs, grid5_lats, grid5_lons = utils.grid_5by5(monthly_grid, n_obs_per_month, grid_lats, grid_lons, doMedian = settings.doMedian, daily = False)
#                out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_{}{:02d}_{}_{}.nc".format(year, month, period, suffix)
#
#                utils.netcdf_write(out_filename, monthly_5by5, monthly_5by5_n_grids, monthly_5by5_n_obs, OBS_ORDER, grid5_lats, grid5_lons, times, frequency = "M")
#
#                if settings.plots and (year in [1973, 1983, 1993, 2003, 2013]):
#                    # plot the distribution of days
#
#                    plt.clf()
#                    plt.hist(monthly_5by5_n_obs.reshape(-1), bins = np.arange(0,100,5), log = True, rwidth=0.5)
#                    plt.title("Total number of raw observations in each 5x5 monthly grid box")
#                    plt.xlabel("Number of raw observations")
#                    plt.ylabel("Frequency (log scale)")
#                    plt.savefig(settings.PLOT_LOCATION + "n_obs_5x5_monthly_{}{:02d}_{}_{}.png".format(year, month, period, suffix))
#
#                    plt.clf()
#                    plt.hist(monthly_5by5_n_grids.reshape(-1), bins = np.arange(-2,30,2), align = "left", log = True, rwidth=0.5)
#                    plt.axvline(x = 1, color="r")
#                    plt.title("Total number of 1x1 monthly grids in each 5x5 monthly grid")
#                    plt.xlabel("Number of 1x1 monthly grids")
#                    plt.ylabel("Frequency (log scale)")
#                    plt.savefig(settings.PLOT_LOCATION + "n_grids_5x5_monthly_{}{:02d}_{}_{}.png".format(year, month, period, suffix))
#
#                # clear up memory
#                del monthly_grid
#                del monthly_5by5
#                del monthly_5by5_n_grids
#                del monthly_5by5_n_obs
#                del n_grids_per_month
#                del n_obs_per_month
#                del n_hrs_per_day
#                gc.collect()
# end
                # go direct from daily 1x1 to monthly 5x5
# KATE MEDIAN WATCH - settings.doMedian is generally set to True - I think we may want the MEAN HERE!!!
# KATE modified - to hard wire in MEAN here
# UNC NEW
                if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT: #                        
                    monthly_5by5, unc_monthly_5by5, monthly_5by5_n_grids, monthly_5by5_n_obs, grid5_lats, grid5_lons = utils.grid_5by5_unc(daily_grid, unc_daily_grid, n_obs_per_day, grid_lats, grid_lons, doMedian = False, daily = True,
		                                                                                                                  doUSLR = doUSLR, doUSCN = doUSCN, doUHGT = doUHGT, doUR = doUR, doUM = doUM, doUC = doUC, doUTOT = doUTOT)
		else:
                    monthly_5by5, monthly_5by5_n_grids, monthly_5by5_n_obs, grid5_lats, grid5_lons = utils.grid_5by5(daily_grid, n_obs_per_day, grid_lats, grid_lons, doMedian = False, daily = True)
                #monthly_5by5, monthly_5by5_n_grids, monthly_5by5_n_obs, grid5_lats, grid5_lons = utils.grid_5by5(daily_grid, n_obs_per_day, grid_lats, grid_lons, doMedian = settings.doMedian, daily = True)
# end

                print('Done Monthly grids')

                out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_5x5_monthly_from_daily_{}{:02d}_{}_{}.nc".format(year, month, period, suffix)
 
# UNC NEW
                if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
		    if doUSLR:
		        uncS = 'uSLR'
                    elif doUSCN:
		        uncS = 'uSCN'			
                    elif doUHGT:
		        uncS = 'uHGT'			
                    elif doUR:
		        uncS = 'uR'			
                    elif doUM:
		        uncS = 'uM'			
                    elif doUC:
		        uncS = 'uC'			
                    elif doUTOT:
		        uncS = 'uTOT'			
                    out_filename = settings.DATA_LOCATION + settings.OUTROOT + "_{}_5x5_monthly_from_daily_{}{:02d}_{}_{}.nc".format(uncS, year, month, period, suffix)
		    utils.netcdf_write_unc(uncS, out_filename, unc_monthly_5by5, monthly_5by5_n_grids, monthly_5by5_n_obs, OBS_ORDER, grid5_lats, grid5_lons, times, frequency = "M", \
		                           doUSLR = doUSLR, doUSCN = doUSCN, doUHGT = doUHGT, doUR = doUR, doUM = doUM, doUC = doUC, doUTOT = doUTOT)
		else:
		    utils.netcdf_write(out_filename, monthly_5by5, monthly_5by5_n_grids, monthly_5by5_n_obs, OBS_ORDER, grid5_lats, grid5_lons, times, frequency = "M")

                

                if settings.plots and (year in [1973, 1983, 1993, 2003, 2013]):
                    # plot the distribution of days

                    plt.clf()
                    plt.hist(monthly_5by5_n_obs.reshape(-1), bins = np.arange(-10,1000,10),  log = True, rwidth=0.5)
                    plt.title("Total number of raw observations in each 5x5 monthly grid box")
                    plt.xlabel("Number of raw observations")
                    plt.ylabel("Frequency (log scale)")
                    plt.savefig(settings.PLOT_LOCATION + "n_obs_5x5_monthly_from_daily_{}{:02d}_{}_{}.png".format(year, month, period, suffix))


                    plt.clf()
                    plt.hist(monthly_5by5_n_grids.reshape(-1), bins = np.arange(-5,100,5), align = "left", log = True, rwidth=0.5)
                    plt.axvline(x = (0.3 * daily_grid.shape[0]), color="r")
                    plt.title("Total number of 1x1 daily grids in each 5x5 monthly grid")
                    plt.xlabel("Number of 1x1 daily grids")
                    plt.ylabel("Frequency (log scale)")

                    plt.savefig(settings.PLOT_LOCATION + "n_grids_5x5_monthly_from_daily_{}{:02d}_{}_{}.png".format(year, month, period, suffix))


                del daily_grid
                del monthly_5by5
                del n_obs_per_day
                del monthly_5by5_n_grids
                del monthly_5by5_n_obs
# UNC NEW
#		if doBCtotal:
                if doUSLR | doUSCN | doUHGT | doUR | doUM | doUC | doUTOT:
		    del unc_daily_grid
		    del unc_monthly_5by5
		
                gc.collect()

    return # do_gridding

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
    parser.add_argument('--start_month', dest='start_month', action='store', default = 1,
                        help='which month to start run, default = 1')
    parser.add_argument('--end_month', dest='end_month', action='store', default = 12,
                        help='which month to end run, default = 12')
# CANNOT BE MORE THAN ONE OF THE BELOW:
    parser.add_argument('--doQC', dest='doQC', action='store_true', default = False,
                        help='process the QC information, default = False')
# KATE modified
    parser.add_argument('--doQC1it', dest='doQC1it', action='store_true', default = False,
                        help='process the first iteration QC information without buddy check, default = False')
    parser.add_argument('--doQC2it', dest='doQC2it', action='store_true', default = False,
                        help='process the second iteration QC information without buddy check, default = False')
    parser.add_argument('--doQC3it', dest='doQC3it', action='store_true', default = False,
                        help='process the third iteration QC information with buddy check, default = False')
# end
    parser.add_argument('--doBC', dest='doBC', action='store_true', default = False,
                        help='process the bias corrected data, default = False')
# KATE modified
    parser.add_argument('--doBCtotal', dest='doBCtotal', action='store_true', default = False,
                        help='process the full bias corrected data, default = False')
    parser.add_argument('--doBChgt', dest='doBChgt', action='store_true', default = False,
                        help='process the height bias corrected data only, default = False')
    parser.add_argument('--doBCscn', dest='doBCscn', action='store_true', default = False,
                        help='process the screen bias corrected data only, default = False')
# end
    parser.add_argument('--doNOWHOLE', dest='doNOWHOLE', action='store_true', default = False,
                        help='process the total bias corrected data that has no whole number flag set, default = False')
# UNC NEW
# MUST SET doBCtotal for these to work:
    parser.add_argument('--doUSLR', dest='doUSLR', action='store_true', default = False,
                        help='process the solar adjustment uncertainty only with correlation, default = False')
    parser.add_argument('--doUSCN', dest='doUSCN', action='store_true', default = False,
                        help='process the instrument adjustment uncertainty only with correlation, default = False')
    parser.add_argument('--doUHGT', dest='doUHGT', action='store_true', default = False,
                        help='process the height adjustment uncertainty only with correlation, default = False')
    parser.add_argument('--doUR', dest='doUR', action='store_true', default = False,
                        help='process the rounding uncertainty only with no correlation, default = False')
    parser.add_argument('--doUM', dest='doUM', action='store_true', default = False,
                        help='process the measurement uncertainty only with no correlation, default = False')
    parser.add_argument('--doUC', dest='doUC', action='store_true', default = False,
                        help='process the climatological uncertainty only with correlation, default = False')
    parser.add_argument('--doUTOT', dest='doUTOT', action='store_true', default = False,
                        help='process the total uncertainty only - no correlation possible, default = False')
# end
# KATE modified
# THIS CAN RUN WITH ANY OF THE do???? arguments:
    parser.add_argument('--ShipOnly', dest='ShipOnly', action='store_true', default = False,
                        help='process the ship only platform type data, default = False')
# end
    args = parser.parse_args()


    do_gridding(suffix = str(args.suffix), start_year = int(args.start_year), end_year = int(args.end_year), \
                    start_month = int(args.start_month), end_month = int(args.end_month), \
# KATE modified
                    doQC = args.doQC, doQC1it = args.doQC1it, doQC2it = args.doQC2it, doQC3it = args.doQC3it, \
		    doBC = args.doBC, doBCtotal = args.doBCtotal, doBChgt = args.doBChgt, doBCscn = args.doBCscn, doNOWHOLE = args.doNOWHOLE, \
		    doUSLR = args.doUSLR, doUSCN = args.doUSCN, doUHGT = args.doUHGT, doUR = args.doUR, doUM = args.doUM, doUC = args.doUC, doUTOT = args.doUTOT, \
		    ShipOnly = args.ShipOnly)
                    #doQC = args.doQC, doBC = args.doBC)
# end

# END
# ************************************************************************
