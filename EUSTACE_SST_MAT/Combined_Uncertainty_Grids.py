# python 3
# 
# Author: Kate Willett
# Created: 18 January 2019
# Last update: 19 January 2019
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/EUSTACE_SST_MAT/	
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code creates the combined obs uncertainty, gridbox sampling uncertainty
# and full (sampling + obs) uncertainty for each gridbox
#
# Uncertainties are assessed as 1 sigma and outoput as 1 sigma!!!!
#
# NOTE THAT IT ALSO REFORMATS THE DATA TO BE ONE FILE PER VARIABLE WITH ALL RELATED FIELDS WITHIN!!!
# 
# The sampling uncertainty follows the methodology applied for HadISDH-land which
# in turn follows Jones et al., 1999
#
# Willett, K. M., Williams Jr., C. N., Dunn, R. J. H., Thorne, P. W., Bell, 
# S., de Podesta, M., Jones, P. D., and Parker D. E., 2013: HadISDH: An 
# updated land surface specific humidity product for climate monitoring. 
# Climate of the Past, 9, 657-677, doi:10.5194/cp-9-657-2013. 
#
# Jones, P. D., Osborn, T. J., and Briffa, K. R.: Estimating sampling errors in large-scale temperature averages, J. Climate, 10, 2548-2568, 1997
#
# -----------------------
# LIST OF MODULES
# -----------------------
# import os
# import datetime as dt
# import numpy as np
# import sys, getopt
# import math
# from math import sin, cos, sqrt, atan2, radians
# import scipy.stats
# import matplotlib.pyplot as plt
# matplotlib.use('Agg') 
# import calendar
# import gc
# import netCDF4 as ncdf
# import copy
# import pdb
#
# Kate:
# from ReadNetCDF import GetGrid
# from ReadNetCDF import GetGrid4
# import gridbox_sampling_uncertainty as gsu
#
# INTERNAL:
# 
# 
# -----------------------
# DATA
# -----------------------
# Land Sea mask of 5x5 grids
# /project/hadobs2/hadisdh/marine/otherdata/new_coverpercentjul08.nc
#
# Bias Corrected actual and renormalised anomalies
# actual values:
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocal/OBSclim2BClocal_5x5_monthly_from_daily_*_relax.nc
# anomaly values:
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocal/OBSclim2BClocal_5x5_monthly_renorm19812010_anomalies_from_daily_*_relax.nc
# uncertainty:
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocal/OBSclim2BClocal_u*_5x5_monthly_from_daily_*_relax.nc
#
# Bias Corrected SHIP only actual and renormalised anomalies
# actual values:
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocalship/OBSclim2BClocal_5x5_monthly_from_daily_*_relax.nc
# anomaly values:
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocalship/OBSclim2BClocal_5x5_monthly_renorm19812010_anomalies_from_daily_*_relax.nc
# uncertainty:
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocalship/OBSclim2BClocal_u*_5x5_monthly_from_daily_*_relax.nc
# 
# -----------------------
# HOW TO RUN THE CODE
# -----------------------
# Annoyingly it looks like hadobs user can't access the module load scitools for some reason so I have to run from hadkw.
# This means some faffing around with saving files as hadkw then copying them over to project/hadobs2/ as hadobs
# Maybe after a test run I can run this on spice which should allow python 3 use?
#
# module load scitools/experimental-current
# python Combined_Uncertainty_Grids.py --year1 1973 --year2 2017 --month1 01 --month2 --12  --timing both (day, night) --platform ship (all)
# Not written this yet - prefer it to be a seperate file
# --Reformat flag outputs the data by variable with all related fields in it. We may want this as stand alone but I'm thinking its too big to run all in one go.
# 
# -----------------------
# OUTPUT
# -----------------------
# 1 sigma uncertainty!!!
#
# Files are temporarily saved to /TMPSAVE/ within the run directory to be copied later
#
# uOBS, uSAMP (usbarSQ, urbar), uFULL
# Bias Corrected
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocal/OBSclim2BClocal_uOBS_5x5_monthly_from_daily_*_relax.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocal/OBSclim2BClocal_uSAMP_5x5_monthly_from_daily_*_relax.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocal/OBSclim2BClocal_usbarSQ_5x5_monthly_from_daily_*_relax.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocal/OBSclim2BClocal_urbar_5x5_monthly_from_daily_*_relax.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocal/OBSclim2BClocal_uFULL_5x5_monthly_from_daily_*_relax.nc
#
# Bias Corrected SHIP only
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocalship/OBSclim2BClocal_uOBS_5x5_monthly_from_daily_*_relax.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocalship/OBSclim2BClocal_uSAMP_5x5_monthly_from_daily_*_relax.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocalship/OBSclim2BClocal_usbarSQ_5x5_monthly_from_daily_*_relax.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocalship/OBSclim2BClocal_urbar_5x5_monthly_from_daily_*_relax.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocalship/OBSclim2BClocal_uFULL_5x5_monthly_from_daily_*_relax.nc
# 
# VARIABLE BASED FIELDS ????
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/MONITORING/HadISDH.marineq.1.0.0.2017f_BCship5by5_anoms8110_<nowmon><nowyear>_cf.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/MONITORING/HadISDH.marineRH.1.0.0.2017f_BCship5by5_anoms8110_<nowmon><nowyear>_cf.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/MONITORING/HadISDH.marinee.1.0.0.2017f_BCship5by5_anoms8110_<nowmon><nowyear>_cf.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/MONITORING/HadISDH.marineT.1.0.0.2017f_BCship5by5_anoms8110_<nowmon><nowyear>_cf.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/MONITORING/HadISDH.marineTd.1.0.0.2017f_BCship5by5_anoms8110_<nowmon><nowyear>_cf.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/MONITORING/HadISDH.marineTw.1.0.0.2017f_BCship5by5_anoms8110_<nowmon><nowyear>_cf.nc
# /project/hadobs2/hadisdh/marine/ICOADS.3.0.0/MONITORING/HadISDH.marineDPD.1.0.0.2017f_BCship5by5_anoms8110_<nowmon><nowyear>_cf.nc
#
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
# 
# Version 1 (18 January 2018)
# ---------
#  
# Enhancements
#  
# Changes
#  
# Bug fixes
#  
# -----------------------
# OTHER INFORMATION
# -----------------------
# This builds on original IDL code written for HadISDH-land by Kate Willett calp_samplingerrorJUL2012_nofill.pro
#
################################################################################################################
# IMPORTS:
import os
import datetime as dt
import numpy as np
import sys, getopt
import math
from math import sin, cos, sqrt, atan2, radians
import scipy.stats
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import calendar
import gc
import netCDF4 as ncdf
import copy
import pdb

# Kate:
from ReadNetCDF import GetGrid
from ReadNetCDF import GetGrid4
import gridbox_sampling_uncertainty as gsu

################################################################################################################
# SUBROUTINES #
##################################################
# get_pseudo_stations #
##################################################
def get_pseudo_stations(NGridsArr,Nlats,Nlons,TheMDI):
    ''' 
    NGridsArr: times, lats, lons, of number of grids of 1x1 dailies going into each month
    Nlats: number of latitude boxes
    Nlons: number of longitude boxes
    TheMDI: missing data indicator

    # Work out mean n_stations (speaudo) per gridbox (month and over whole period) to pass to sampling uncertainty
    # This is tricky - n_obs and n_grids could be far larger than n_stations within a 5by5 gridbox.
    # I could use the number of potential 1by1 grids in a 5by5 - so 25 - this could be an over estimate in some cases
    # I could just use the n_grids but this is the number of 1by1 daily grids going into the monthly - 25*30 = 750 maximum
    # Using n_obs is harder to guage, especially in the buoy ERA
    # Maybe for well sampled gridboxes (600+ daily 1by1 grids within a month) I use 25 and scale appropriately depending on n_grids
    # Yes - sounds like a plan
    # I'm generally getting fewer than 100 grids per month
    # use np.linspace to get 25 steps from 1 to 600 such that the largest bin has 25 pseudo n_stations and the smallest has 1
    # Make sure that grids with NO DATA have 0 '''
    
    Pseudo_station_bins = np.round(np.linspace(25,600,24)) # integer array from 25 to 600 in 24 steps
    Pseudo_station_bins = np.append(Pseudo_station_bins,6000) # now 25 elements with a huge 6000 at the end to catch all 
    Pseudo_station_counts = np.arange(1,26) # integer array from 1 to 25
    
    Ntims = len(NGridsArr[:,0,0])
    
    MeanNPointsArr = np.zeros((Nlats,Nlons),dtype = int) # mean number of pseudo stations over the whole sampling period
    NPointsArr = np.zeros((Ntims,Nlats,Nlons),dtype = int) # mean number of pseudo stations per month
    
    for lt in range(Nlats):
        for ln in range(Nlons):
        
            Gots = np.where(NGridsArr[:,lt,ln] > 0)[0]
            if (len(Gots) > 0):
                MeanGrids = np.mean(NGridsArr[Gots,lt,ln])
                MeanNPointsArr[lt,ln] = Pseudo_station_counts[np.where(Pseudo_station_bins > np.ceil(MeanGrids))[0][0]] 		 
     
                # Also take the same approach for each month individually
                for m,Mpt in enumerate(Gots):
		
                    MeanGrids = np.mean(NGridsArr[Mpt,lt,ln])
                    NPointsArr[Mpt,lt,ln] = Pseudo_station_counts[np.where(Pseudo_station_bins > np.ceil(MeanGrids))[0][0]] 
		    	    		   
    #print("Check the pseudo station bit")
    # This works ok
    #pdb.set_trace()

    return MeanNPointsArr, NPointsArr

##################################################
# calc_total_obs_unc #
##################################################
def calc_total_obs_unc(TheURArr,TheUCArr,TheUMArr,TheUSCNArr,TheUHGTArr,TheNLats,TheNLons,TheMDI):
    '''Combines all obs uncertainty sources in quadrature for the gridbox
    TheURArr: times, lat, lon array of whole number uncertainty with TheMDI missing data
    TheUCArr: times, lat, lon array of climatology uncertainty with TheMDI missing data
    TheUMArr: times, lat, lon array of measurement uncertainty with TheMDI missing data
    TheUSCNArr: times, lat, lon array of non-ventilated instrument adjustment uncertainty with TheMDI missing data
    TheUHGTArr: times, lat, lon array of height adjustment uncertainty with TheMDI missing data
    TheNLats: scalar of number of gridbox latitude centres from SOUTH to NORTH???
    TheNLons: scalar of number of gridbox longitude centres from WEST to EAST???
    TheMDI: scalar missing data ID
    
    RETURNS:
    TheTotObsUncArr: times, lat, lon array of total obs uncertainty with TheMDI missing data'''

    # What is the times total?
    TheNTims = len(TheURArr[:,0,0])
    
    # Set up the array to hold the total obs uncertainties
    # No really necessary but good to see what we are working with
    TheTotObsUncArr = np.empty((TheNTims,TheNLats,TheNLons),dtype = float)
    TheTotObsUncArr.fill(TheMDI)

    # np arrays can have element wise operations so we do not need to loop - hurray!
    # set all Uncs MDIs to 0 so that 0**2 won't impact the combination
    TheURArr[np.where(TheURArr == TheMDI)] = 0
    TheUCArr[np.where(TheUCArr == TheMDI)] = 0
    TheUMArr[np.where(TheUMArr == TheMDI)] = 0
    TheUSCNArr[np.where(TheUSCNArr == TheMDI)] = 0
    TheUHGTArr[np.where(TheUHGTArr == TheMDI)] = 0

    # Combine in quadrature
    TheTotObsUncArr = np.sqrt(TheURArr**2 + TheUCArr**2 + TheUMArr**2 + TheUHGTArr**2 + TheUSCNArr**2)    

    # Convert all 0 values to TheMDI - hope floating points don't do anything silly
    TheTotObsUncArr[np.where(TheTotObsUncArr == 0.)] = TheMDI
    
#    print("Test TheTotObsUncArr!")
#    pdb.set_trace()
    
    return TheTotObsUncArr

##################################################
# calc_full_unc #
##################################################
def calc_full_unc(TheUOBSArr,TheUSAMPArr,TheNLats,TheNLons,TheMDI):
    '''Combines all total obs uncertainty and sampling uncertainty sources in quadrature for the gridbox
    TheUOBSArr: times, lat, lon array of whole number uncertainty with TheMDI missing data
    TheUSAMPArr: times, lat, lon array of climatology uncertainty with TheMDI missing data
    TheNLats: scalar of number of gridbox latitude centres from SOUTH to NORTH???
    TheNLons: scalar of number of gridbox longitude centres from WEST to EAST???
    TheMDI: scalar missing data ID
    This is all set up for 1 sigma uncertainty
    
    RETURNS:
    TheFullUncArr: times, lat, lon array of total obs uncertainty with TheMDI missing data'''

    # What is the times total?
    TheNTims = len(TheUOBSArr[:,0,0])
    
    # Set up the array to hold the full uncertainties
    # No really necessary but good to see what we are working with
    TheFullUncArr = np.empty((TheNTims,TheNLats,TheNLons),dtype = float)
    TheFullUncArr.fill(TheMDI)

    # np arrays can have element wise operations so we do not need to loop - hurray!
    # set all Uncs MDIs to 0 so that 0**2 won't impact the combination
    TheUOBSArr[np.where(TheUOBSArr == TheMDI)] = 0
    TheUSAMPArr[np.where(TheUSAMPArr == TheMDI)] = 0

    # Combine in quadrature
    TheFullUncArr = np.sqrt(TheUOBSArr**2 + TheUSAMPArr**2)    

    # Convert all 0 values to TheMDI - hope floating points don't do anything silly
    TheFullUncArr[np.where(TheFullUncArr == 0.)] = TheMDI
    TheUOBSArr[np.where(TheUOBSArr == 0)] = TheMDI
    TheUSAMPArr[np.where(TheUSAMPArr == 0)] = TheMDI
    
#    print("Test TheFullUncArr!")
#    pdb.set_trace()
    
    return TheFullUncArr

##################################################
# Write_Netcdf_Variable_Unc #
##################################################
def Write_Netcdf_Variable_Unc(uSource,outfile, var, vlong, vstandard, vunit, unc_data, TheMDI):
    '''
    This is basically a tweak of the utils.py version but set up to work here
    
    Create the netcdf variable
    :param str uSource: name of uncertainty source    
    :param obj outfile: output file object
    :param list var: variable name
    :param list vlong: long variable name
    :param list vstandard: standard variable name
    :param str vunit: unit of variable
    :param np array unc_data: times, lats, lons uncertainty data to write
    
    '''

    # For sbarSQ adn SAMP there will be an n_grids variable which needs to be treated differently
    if (var == 'n_grids'):

        # Create the Variable but rbar and sbarSQ do not have a time dimension
        if (uSource != 'sbarSQ'):
            nc_var = outfile.createVariable(var, np.dtype('int'), ('time','latitude','longitude',), zlib = True, fill_value = -1) # with compression
        else:
            nc_var = outfile.createVariable(uSource, np.dtype('int'), ('latitude','longitude',), zlib = True, fill_value = -1) # with compression
    
        nc_var.long_name = 'Number of pseudo stations within gridbox'
        nc_var.standard_name = 'Number of pseudo station grids'
    
        nc_var.units = vunit
        nc_var.missing_value = -1
    
        # We're not using masked arrays here - hope that' snot a problem
        nc_var.valid_min = np.min(unc_data[np.where(unc_data > -1)]) 
        nc_var.valid_max = np.max(unc_data[np.where(unc_data > -1)]) 

    # For all other variables...
    else:     
    
        # Create the Variable but rbar and sbarSQ do not have a time dimension
        if (uSource != 'rbar') & (uSource != 'sbarSQ'):
             nc_var = outfile.createVariable(var+'_'+uSource, np.dtype('float64'), ('time','latitude','longitude',), zlib = True, fill_value = TheMDI) # with compression
        else:
            nc_var = outfile.createVariable(var+'_'+uSource, np.dtype('float64'), ('latitude','longitude',), zlib = True, fill_value = TheMDI) # with compression
    
        if uSource == 'SAMP':
            nc_var.long_name = vlong+' GRIDBOX SAMPLING uncertainty (1 sigma)'
            nc_var.standard_name = vstandard+' sampling uncertainty'
        elif uSource == 'sbarSQ':
            nc_var.long_name = vlong+' GRIDBOX mean station variance'
            nc_var.standard_name = vstandard+' mean station variance'
        elif uSource == 'rbar':
            nc_var.long_name = vlong+' GRIDBOX mean intersite correlation'
            nc_var.standard_name = vstandard+' mean intersite correlation'
        elif uSource == 'OBS':
            nc_var.long_name = vlong+' TOTAL OBSERVATION uncertainty (1 sigma)'
            nc_var.standard_name = vstandard+' total obs uncertainty'
        elif uSource == 'FULL':
            nc_var.long_name = vlong+' FULL uncertainty (1 sigma)'
            nc_var.standard_name = vstandard+' full uncertainty'
    
        nc_var.units = vunit
        nc_var.missing_value = TheMDI
    
        # We're not using masked arrays here - hope that' snot a problem
        nc_var.valid_min = np.min(unc_data[np.where(unc_data != TheMDI)]) 
        nc_var.valid_max = np.max(unc_data[np.where(unc_data != TheMDI)]) 
        
    nc_var[:] = unc_data
    
#    print("Testing netCDF output to find why its putting MDI as 0",var)
#    print(unc_data[0,0:10,0:5])
#    pdb.set_trace()
        
    return # write_netcdf_variable_unc
    
###################################################################
# Write_NetCDF_Unc #
###################
def Write_NetCDF_Unc(uSource, filename, data_abs, data_anoms, lats, lons, time, variables_abs, variables_anoms, long_abs, long_anoms, standard_abs, standard_anoms, unitsarr,TheMDI): 

    '''
    This is basically a copy of utils.py version but tweaked to work here
    
    Write the relevant fields out to a netCDF file.
    
    :param str uSource: name of uncertainty source
    :param str filename: output filename              
    :param list of np arrays data_abs: the uncertainty data array for anomalies [times, lats, lons] for each variable
    :param list of np arrays data_anoms: the whole uncertainty data array for actuals [times, lats, lons] for each variable
    :param array lats: the latitudes
    :param array lons: the longitudes
    :param array time: the times as TimeVar object
    :param list variables_abs: the actual variables in order to output
    :param list variables_anoms: the anomaly variables in order to output
    :param list long_abs: the actual variables long name in order to output
    :param list long_anoms: the anomaly variables long name in order to output
    :param list standard_abs: the actual variables standard name in order to output
    :param list standard_anoms: the anomaly variables standard name in order to output
    :param list unitsarr: the variable units in order to output
    :param float TheMDI: the missing data indicator

    '''
    
    # remove file
    if os.path.exists(filename):
        os.remove(filename)

    outfile = ncdf.Dataset(filename,'w', format='NETCDF4')

    # Set up dimensions - with time only for SAMP, FULL and OBS
    if (uSource != 'rbar') & (uSource != 'sbarSQ'):
        time_dim = outfile.createDimension('time',len(time))
    lat_dim = outfile.createDimension('latitude',len(lats)) # as TRC of box edges given, size = # box centres to be written
    lon_dim = outfile.createDimension('longitude',len(lons))
    
    #***********
    # set up basic variables linked to dimensions
    # make time variable
    if (uSource != 'rbar') & (uSource != 'sbarSQ'):
        nc_var = outfile.createVariable('time', np.dtype('int'), ('time'), zlib = True) # with compression!!!
        nc_var.long_name = "time since 1/1/1973 in months"
        nc_var.units = "months"
        nc_var.standard_name = "time"
        nc_var[:] = time
    
    # make latitude variable
    nc_var = outfile.createVariable('latitude', np.dtype('float32'), ('latitude'), zlib = True) # with compression!!!
    nc_var.long_name = "latitude"
    nc_var.units = "degrees north"
    nc_var.standard_name = "latitude"
    nc_var[:] = lats
    

    # make longitude variable
    nc_var = outfile.createVariable('longitude', np.dtype('float32'), ('longitude'), zlib = True) # with compression!!!
    nc_var.long_name = "longitude"
    nc_var.units = "degrees east"
    nc_var.standard_name = "longitude"
    nc_var[:] = lons

    #***********
    # create variables actuals - makes 1 sigma:
#    print("Test data again for MDI")
    for v in range(len(variables_abs)):
        var = variables_abs[v]
        print(v, var)      
        Write_Netcdf_Variable_Unc(uSource, outfile, var, long_abs[v], standard_abs[v], unitsarr[v], data_abs[v], TheMDI)

    # create variables anomalies - makes 1 sigma:
    for v in range(len(variables_anoms)):
        var = variables_anoms[v]
        print(v, var)
        Write_Netcdf_Variable_Unc(uSource, outfile, var, long_anoms[v], standard_anoms[v], unitsarr[v], data_anoms[v], TheMDI)

    # Global Attributes 
    
    # Read these from file
    attr_file = os.path.join(os.getcwd(), "attributes.dat")

    try:
        with open(attr_file,'r') as infile:        
            lines = infile.readlines()
        
    except IOError:
        print("Attributes file not found at " + attr_file)
        raise IOError
    
    attributes = {}
    
    for line in lines:
        split_line = line.split()
        
        attributes[split_line[0]] = " ".join(split_line[1:])    
    
    # Set the attributes
    for attr in attributes:
        
        outfile.__setattr__(attr, attributes[attr])
 
    outfile.date_created = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d, %H:%M")
    outfile.Conventions = 'CF-1.5' 
    outfile.Metadata_Conventions = 'Unidata Dataset Discovery v1.0,CF Discrete Sampling Geometries Conventions'
    outfile.featureType = 'gridded'
    
    outfile.close()

    return # Write_NetCDF_Unc
    
################################################################################################################
# MAIN #
################################################################################################################
def main(argv):
    # INPUT PARAMETERS AS STRINGS??? DOESN@T SEEM TO MATTER
    year1 = '1973' 
    year2 = '2017'
    month1 = '01' # months must be 01, 02 etc
    month2 = '12'
    timings = 'both' # 'day','night'
    platform = 'ship' # 'all'

    try:
        opts, args = getopt.getopt(argv, "hi:",
	                           ["year1=","year2=","month1=","month2=","timings=","platform="])
    except getopt.GetoptError:
        print('Usage (as strings) Combined_Uncertainty_Grids.py --year1 <1973> --year2 <2017> '+\
	      '--month1 <01> --month2 <12> --timings <both> --platform <ship>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == "--year1":
            try:
                year1 = arg
            except:
                sys.exit("Failed: year1 not an integer")
        elif opt == "--year2":
            try:
                year2 = arg
            except:
                sys.exit("Failed: year2 not an integer")
        elif opt == "--month1":
            try:
                month1 = arg
            except:
                sys.exit("Failed: month1 not an integer")
        elif opt == "--month2":
            try:
                month2 = arg
            except:
                sys.exit("Failed: month2 not an integer")
        elif opt == "--timings":
            try:
                timings = arg
            except:
                sys.exit("Failed: timings not a string")
        elif opt == "--platform":
            try:
                platform = arg
            except:
                sys.exit("Failed: platform not a string")

    assert year1 != -999 and year2 != -999, "Year not specified."

    print(year1, year2, month1, month2, timings, platform)

    # Set up this run files, directories and dates/clims: years, months, ship or all

    VarList = ['marine_air_temperature','dew_point_temperature','specific_humidity','vapor_pressure','relative_humidity','wet_bulb_temperature','dew_point_depression','n_grids'] # This is the ReadInfo
    VarLong = ['Marine Air Temperature','Dew Point Temperature','Specific Humidity','Vapor Pressure','Relative Humidity','Wet Bulb Temperature','Dew Point Depression','n_grids'] # This is the ReadInfo
    VarStandard = ['marine air temperature','dew point temperature','specific humidity','vapor pressure','relative humidity','wet bulb temperature','dew point depression','n_grids'] # This is the ReadInfo
    AnomsVarList = [i+'_anomalies' for i in VarList[0:7]]
    AnomsVarList.append(VarList[7])
    AnomsVarLong = [i+' Anomalies' for i in VarLong[0:7]]
    AnomsVarStandard = [i+' anomalies' for i in VarStandard[0:7]]
    var_loop = ['T','Td','q','e','RH','Tw','DPD']
    units_loop = ['degrees C','degrees C','g/ke','hPa','%rh','degrees C','degrees C','standard']

#    var_loop = ['T']
    
    # gridbox_sampling_uncertainty.calc_sampling_unc IsMarine switch
    IsMarine = True # In this code this should always be True!!!
    
    # Missing Data Indicator
    MDI = -1e30
    
    # Input and Output directory:
    if platform == 'ship':
        WorkingDir = '/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocalship/'
    else:
        WorkingDir = '/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/GRIDSOBSclim2BClocal/'

    # Input Files
    FilAnoms = 'OBSclim2BClocal_5x5_monthly_renorm19812010_anomalies_from_daily_'+timings+'_relax.nc'
    FilAbs = 'OBSclim2BClocal_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUR = 'OBSclim2BClocal_uR_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUC = 'OBSclim2BClocal_uC_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUM = 'OBSclim2BClocal_uM_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUSCN = 'OBSclim2BClocal_uSCN_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUHGT = 'OBSclim2BClocal_uHGT_5x5_monthly_from_daily_'+timings+'_relax.nc'

    # Output Files
#    # If running as hadobs
#    OutFilUTotObs = WorkingDir+'OBSclim2BClocal_uOBS_5x5_monthly_from_daily_'+timings+'_relax.nc'
#    OutFilUSamp = WorkingDir+'OBSclim2BClocal_uSAMP_5x5_monthly_from_daily_'+timings+'_relax.nc'
#    OutFilUsbarSQ = WorkingDir+'OBSclim2BClocal_usbarSQ_5x5_monthly_from_daily_'+timings+'_relax.nc'
#    OutFilUrbar = WorkingDir+'OBSclim2BClocal_urbar_5x5_monthly_from_daily_'+timings+'_relax.nc'
#    OutFilUFull = WorkingDir+'OBSclim2BClocal_uFULL_5x5_monthly_from_daily_'+timings+'_relax.nc'
    # If running as hadkw
    OutFilUTotObs = 'TMPDIR/OBSclim2BClocal_uOBS_5x5_monthly_from_daily_'+timings+'_relax.nc'
    OutFilUSamp = 'TMPDIR/OBSclim2BClocal_uSAMP_5x5_monthly_from_daily_'+timings+'_relax.nc'
    OutFilUsbarSQ = 'TMPDIR/OBSclim2BClocal_usbarSQ_5x5_monthly_from_daily_'+timings+'_relax.nc'
    OutFilUrbar = 'TMPDIR/OBSclim2BClocal_urbar_5x5_monthly_from_daily_'+timings+'_relax.nc'
    OutFilUFull = 'TMPDIR/OBSclim2BClocal_uFULL_5x5_monthly_from_daily_'+timings+'_relax.nc'
    
    # Set up necessary dates - dates for output are just counts of months from 0 to 54?...
    StYr = int(year1)
    EdYr = int(year2)
    Ntims = ((EdYr + 1) - StYr) * 12
    TimesArr = np.arange(Ntims) # months since January 1973 

    # Set up empty lists to store numpy arrays of the uncertainties
    SampUncAnomsList = []
    SampUncAbsList = []
    sbarSQAnomsList = []
    sbarSQAbsList = []
    rbarAnomsList = []
    rbarAbsList = []

    TotObsUncAnomsList = []
    TotObsUncAbsList = []

    FullUncAnomsList = []
    FullUncAbsList = []

#########
    # Work on Sampling Uncertainty
    
# If we're struggling for memory then loop through each variable - this will change the format to be one file per variable now
# Otherwise I'll write a seperate program to reformat the files to match HadISDH-land. They will have to be reformatted again for CEDA

    # ANOMALIES
    
    print("Working on sampling uncertainty anomalies...")
       
    # Open necessary files to get all variables, n_obs, anomaly values, lats, lons - hopefully this doesn't use too much memory
    Filee = WorkingDir+FilAnoms
    LatInfo = ['latitude']
    LonInfo = ['longitude']
    TmpDataList, LatList, LonList = GetGrid4(Filee,AnomsVarList,LatInfo,LonInfo)
    # This comes out as:
    # TmpDataList: a list of np arrays (times, lats{87.5N to 87.5S], lons[-177.5W to 177.5E])
    # LatList: an NLats np array of lats centres (87.5N to 87.5S)
    # LonList: an NLons np array of lons centres (87.5N to 87.5S)
    
    # Get lat and lon counts
    NLats = len(LatList)
    NLons = len(LonList)
    
    # Work out mean n_stations (speaudo) per gridbox (month and over whole period) to pass to sampling uncertainty
    MeanNPointsArr, NPointsArr = get_pseudo_stations(TmpDataList[7],NLats,NLons, MDI)
    #pdb.set_trace()
        
    # Loop through each variable
    for v,var in enumerate(var_loop):
    
        print("Working on ... ",var)
        # Calculate the sampling uncertainty - make this stand alone so that it can be called by HadISDH-land!!!
        SESQArr, rbarArr, sbarSQArr = gsu.calc_sampling_unc(TmpDataList[v],LatList,LonList,MeanNPointsArr,NPointsArr,MDI,IsMarine)
        SampUncAnomsList.append(SESQArr)
        sbarSQAnomsList.append(sbarSQArr)
        rbarAnomsList.append(rbarArr)

#    # Append MeanNPointsArr to sbarSQAnomsList and NPointsArr to SampUncAnomsList
#    SampUncAnomsList.append(NPointsArr)
#    sbarSQAnomsList.append(MeanNPointsArr)

    # Clean up
    del TmpDataList
#    print('Test Sampling Uncertainty Anoms:')
#    pdb.set_trace()

    # ABSOLUTES - THIS MAY NOT PROVIDE ANYTHING SENSIBLE

    print("Working on sampling uncertainty anomalies...")
    
    # Open necessary files to get all variables, n_obs, anomaly values, lats, lons - hopefully this doesn't use too much memory
    Filee = WorkingDir+FilAbs
    LatInfo = ['latitude']
    LonInfo = ['longitude']
    TmpDataList, LatList, LonList = GetGrid4(Filee,VarList,LatInfo,LonInfo)
    # This comes out as:
    # TmpDataList: a list of np arrays (times, lats{87.5N to 87.5S], lons[-177.5W to 177.5E])
    # LatList: an NLats np array of lats centres (87.5N to 87.5S)
    # LonList: an NLons np array of lons centres (87.5N to 87.5S)
    
    # Pseudo station same for anoms and abs so no need to redo    
    
    # Loop through each variable
    for v,var in enumerate(var_loop):
    
        print("Working on ... ",var)
        # Calculate the sampling uncertainty - make this stand alone so that it can be called by HadISDH-land!!!
        SESQArr, rbarArr, sbarSQArr = gsu.calc_sampling_unc(TmpDataList[v],LatList,LonList,MeanNPointsArr,NPointsArr,MDI,IsMarine)
        SampUncAbsList.append(SESQArr)
        sbarSQAbsList.append(sbarSQArr)
        rbarAbsList.append(rbarArr)

    # Reset MeanNPointsArr and NPointsArr to 0 = -1
    MeanNPointsArr[np.where(MeanNPointsArr == 0)] = -1
    NPointsArr[np.where(NPointsArr == 0)] = -1
    
    # Append int arrays of MeanNPointsArr to sbarSQAbsList and NPointsArr to SampUncAbsList
    SampUncAbsList.append(NPointsArr.astype(int))
    sbarSQAbsList.append(MeanNPointsArr.astype(int))

    # Clean up
    del TmpDataList
#    print('Test Sampling Uncertainty Abs:')
#    pdb.set_trace()

############

    # Work on Total Obs uncertainty

    # ANOMALIES

    print("Working on total obs uncertainty anoms...")

    # Open necessary files to get all variables uncertainties, lats, lons - hopefully this doesn't use too much memory
    Filee = WorkingDir+FilUR
    LatInfo = ['latitude']
    LonInfo = ['longitude']
    URAnomsVarList = [i+'_uR' for i in AnomsVarList[0:7]]
    URAnomsVarList.append(AnomsVarList[7])
    URDataList, LatList, LonList = GetGrid4(Filee,URAnomsVarList[0:7],LatInfo,LonInfo)
    # This comes out as:
    # TmpDataList: a list of np arrays (times, lats{87.5N to 87.5S], lons[-177.5W to 177.5E])
    # LatList: an NLats np array of lats centres (87.5N to 87.5S)
    # LonList: an NLons np array of lons centres (87.5N to 87.5S)

    Filee = WorkingDir+FilUC
    UCAnomsVarList = [i+'_uC' for i in AnomsVarList[0:7]]
    UCAnomsVarList.append(AnomsVarList[7])
    UCDataList, LatList, LonList = GetGrid4(Filee,UCAnomsVarList[0:7],LatInfo,LonInfo)

    Filee = WorkingDir+FilUM
    UMAnomsVarList = [i+'_uM' for i in AnomsVarList[0:7]]
    UMAnomsVarList.append(AnomsVarList[7])
    UMDataList, LatList, LonList = GetGrid4(Filee,UMAnomsVarList[0:7],LatInfo,LonInfo)

    Filee = WorkingDir+FilUSCN
    USCNAnomsVarList = [i+'_uSCN' for i in AnomsVarList[0:7]]
    USCNAnomsVarList.append(AnomsVarList[7])
    USCNDataList, LatList, LonList = GetGrid4(Filee,USCNAnomsVarList[0:7],LatInfo,LonInfo)

    Filee = WorkingDir+FilUHGT
    UHGTAnomsVarList = [i+'_uHGT' for i in AnomsVarList[0:7]]
    UHGTAnomsVarList.append(AnomsVarList[7])
    UHGTDataList, LatList, LonList = GetGrid4(Filee,UHGTAnomsVarList[0:7],LatInfo,LonInfo)

    # Loop through each variable
    for v,var in enumerate(var_loop):

        print("Working on ... ",var)    
        # Get total obs uncertainty - Combine the obs uncertainty sources across the gridbox
        TotObsUnc = calc_total_obs_unc(URDataList[v],UCDataList[v],UMDataList[v],USCNDataList[v],UHGTDataList[v],NLats,NLons,MDI)
        TotObsUncAnomsList.append(TotObsUnc)    
    
    # Clean Up
    del URDataList
    del UCDataList
    del UMDataList
    del USCNDataList
    del UHGTDataList

#    print('Test Total Obs Uncertainty Anoms:')
#    pdb.set_trace()
    
    # ABSOLUTES

    print("Working on total obs uncertainty anoms...")
    
    # Open necessary files to get all variables uncertainties, lats, lons - hopefully this doesn't use too much memory
    Filee = WorkingDir+FilUR
    LatInfo = ['latitude']
    LonInfo = ['longitude']
    URVarList = [i+'_uR' for i in VarList[0:7]]
    URVarList.append(VarList[7])
    URDataList, LatList, LonList = GetGrid4(Filee,URVarList[0:7],LatInfo,LonInfo)
    # This comes out as:
    # TmpDataList: a list of np arrays (times, lats{87.5N to 87.5S], lons[-177.5W to 177.5E])
    # LatList: an NLats np array of lats centres (87.5N to 87.5S)
    # LonList: an NLons np array of lons centres (87.5N to 87.5S)

    Filee = WorkingDir+FilUC
    UCVarList = [i+'_uC' for i in VarList[0:7]]
    UCVarList.append(VarList[7])
    UCDataList, LatList, LonList = GetGrid4(Filee,UCVarList[0:7],LatInfo,LonInfo)

    Filee = WorkingDir+FilUM
    UMVarList = [i+'_uM' for i in VarList[0:7]]
    UMVarList.append(VarList[7])
    UMDataList, LatList, LonList = GetGrid4(Filee,UMVarList[0:7],LatInfo,LonInfo)

    Filee = WorkingDir+FilUSCN
    USCNVarList = [i+'_uSCN' for i in VarList[0:7]]
    USCNVarList.append(VarList[7])
    USCNDataList, LatList, LonList = GetGrid4(Filee,USCNVarList[0:7],LatInfo,LonInfo)

    Filee = WorkingDir+FilUHGT
    UHGTVarList = [i+'_uHGT' for i in VarList[0:7]]
    UHGTVarList.append(VarList[7])
    UHGTDataList, LatList, LonList = GetGrid4(Filee,UHGTVarList[0:7],LatInfo,LonInfo)

    # Loop through each variable
    for v,var in enumerate(var_loop):
    
        print("Working on ... ",var)    
        # Get total obs uncertainty - Combine the obs uncertainty sources across the gridbox
        TotObsUnc = calc_total_obs_unc(URDataList[v],UCDataList[v],UMDataList[v],USCNDataList[v],UHGTDataList[v],NLats,NLons,MDI)
        TotObsUncAbsList.append(TotObsUnc)    
    
    # Clean Up
    del URDataList
    del UCDataList
    del UMDataList
    del USCNDataList
    del UHGTDataList

#    print('Test Total Obs Uncertainty Anoms:')
#    pdb.set_trace()

##############

    # Work on Full Uncertainty

    # ANOMALIES

    print("Working on full uncertainty anoms...")

    # Loop through each variable
    for v,var in enumerate(var_loop):
    
        print("Working on ... ",var)    
        # Get full uncertainty - Combine the obs and sampling uncertainties across the gridbox
        FullUnc = calc_full_unc(TotObsUncAnomsList[v],SampUncAnomsList[v],NLats,NLons,MDI)
        FullUncAnomsList.append(FullUnc)    

#    print('Test Full Uncertainty Anoms:')
#    pdb.set_trace()

    # ABSOLUTES

    print("Working on full uncertainty anoms...")

    # Loop through each variable
    for v,var in enumerate(var_loop):
    
        print("Working on ... ",var)    
        # Get full uncertainty - Combine the obs and sampling uncertainties across the gridbox
        FullUnc = calc_full_unc(TotObsUncAbsList[v],SampUncAbsList[v],NLats,NLons,MDI)
        FullUncAbsList.append(FullUnc)    

#    print('Test Full Uncertainty Abs:')
#    pdb.set_trace()

##############

    # Write out as 1 sigma!!!!!
    
#    print("Test for whether missing values are still MDI")
#    pdb.set_trace()
    
    # Write out sampling uncertainty - this has three components which are written seperately.
    # For testing I'm just running temperature VarList[0], AnomsVarList[0] but this should be [0:7] for all but SAMP and sbarSQ (all of VarList  to include n_grids)
    Write_NetCDF_Unc('SAMP',OutFilUSamp,SampUncAbsList,SampUncAnomsList,LatList,LonList,TimesArr,
                     VarList,AnomsVarList[0:7],VarLong,AnomsVarLong,VarStandard,AnomsVarStandard,units_loop,MDI)
    Write_NetCDF_Unc('sbarSQ',OutFilUsbarSQ,sbarSQAbsList,sbarSQAnomsList,LatList,LonList,TimesArr,
                     VarList,AnomsVarList[0:7],VarLong,AnomsVarLong,VarStandard,AnomsVarStandard,units_loop,MDI)
    Write_NetCDF_Unc('rbar',OutFilUrbar,rbarAbsList,rbarAnomsList,LatList,LonList,TimesArr,
                     VarList[0:7],AnomsVarList[0:7],VarLong[0:7],AnomsVarLong,VarStandard[0:7],AnomsVarStandard,units_loop[0:7],MDI)

    # Write out total obs uncertainty
    Write_NetCDF_Unc('OBS',OutFilUTotObs,TotObsUncAbsList,TotObsUncAnomsList,LatList,LonList,TimesArr,
                     VarList[0:7],AnomsVarList[0:7],VarLong[0:7],AnomsVarLong,VarStandard[0:7],AnomsVarStandard,units_loop[0:7],MDI)

    # Write out full uncertainty
    Write_NetCDF_Unc('FULL',OutFilUFull,FullUncAbsList,FullUncAnomsList,LatList,LonList,TimesArr,VarList[0:7],AnomsVarList[0:7],
                     VarLong[0:7],AnomsVarLong,VarStandard[0:7],AnomsVarStandard,units_loop[0:7],MDI)

#########

    print('And we are done!')

if __name__ == '__main__':
    
    main(sys.argv[1:])
