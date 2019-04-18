# python 3
# 
# Author: Kate Willett
# Created: 25 January 2019
# Last update: 25 February 2019
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/EUSTACE_SST_MAT/	
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code creates the final NetCDF grids of HadISDH-marine for compatibility with HadISDH-land
# These will then need further conversion to ESGF/CEDA but can be easily blended with HadISDH-land and use the same post-processing code
#
# Uncertainties are now doubled to be output as 2 sigma!!!!
#
# NOTE THAT IT ALSO REFORMATS THE DATA TO BE ONE FILE PER VARIABLE WITH ALL RELATED FIELDS WITHIN!!!
#
# -----------------------
# LIST OF MODULES
# -----------------------
# import os
# import datetime as dt
# import numpy as np
# import sys
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
# from GetNiceTimes import MakeDaysSince
#
# INTERNAL:
# 
# 
# -----------------------
# DATA
# -----------------------
#
# Bias Corrected actuals and renormalised anomalies
# actual values - day, night, both:
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/GRIDSOBSclim2BClocal/OBSclim2BClocal_5x5_monthly_from_daily_*_relax.nc
# values - day, night, both:
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/GRIDSOBSclim2BClocal/OBSclim2BClocal_5x5_monthly_renorm19812010_anomalies_from_daily_*_relax.nc
# uncertainty - day, night, both - uHGT, uSCN, uC, uM, uR, uSAMP, uOBS, uFULL:
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/GRIDSOBSclim2BClocal/OBSclim2BClocal_u*_5x5_monthly_from_daily_*_relax.nc
# climatology values - day, night, both:
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/GRIDSOBSclim2BClocal/OBSclim2BClocal_5x5_monthly_climatology_from_daily_*_relax.nc
# stdev values - day, night, both:
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/GRIDSOBSclim2BClocal/OBSclim2BClocal_5x5_monthly_stdev_from_daily_*_relax.nc
#
# Bias Corrected SHIP only actuals and renormalised anomalies
# actual values - day, night, both:
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/GRIDSOBSclim2BClocalship/OBSclim2BClocal_5x5_monthly_from_daily_*_relax.nc
# values - day, night, both:
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/GRIDSOBSclim2BClocalship/OBSclim2BClocal_5x5_monthly_renorm19812010_anomalies_from_daily_*_relax.nc
# uncertainty - day, night, both - uHGT, uSCN, uC, uM, uR, uSAMP, uOBS, uFULL:
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/GRIDSOBSclim2BClocalship/OBSclim2BClocal_u*_5x5_monthly_from_daily_*_relax.nc
# climatology values - day, night, both:
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/GRIDSOBSclim2BClocalship/OBSclim2BClocal_5x5_monthly_climatology_from_daily_*_relax.nc
# stdev values - day, night, both:
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/GRIDSOBSclim2BClocalship/OBSclim2BClocal_5x5_monthly_stdev_from_daily_*_relax.nc
#
# List of attributes to apply to the output netCDF file - update this with version, dates, references etc.
# /project/hadobs2/hadisdh/marine/PROGS/Build/HadISDH_attributes.dat
# 
# -----------------------
# HOW TO RUN THE CODE
# -----------------------
# module load scitools/experimental-current
# python Create_HadISDHMarine_finalgrids.py --year1 1973 --year2 2017 --month1 01 --month2 --12  --timing both (day, night) --platform ship (all)
# 
# -----------------------
# OUTPUT
# -----------------------
# 2 sigma uncertainty!!!
#
# Bias Corrected - for each <var>
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/FINALGRIDS/HadISDH.marine<var>.1.0.0.2017f_BClocal5x5both_anoms8110_<MON><YEAR>_cf.nc
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/FINALGRIDS/HadISDH.marine<var>.1.0.0.2017f_BClocal5x5day_anoms8110_<MON><YEAR>_cf.nc
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/FINALGRIDS/HadISDH.marine<var>.1.0.0.2017f_BClocal5x5night_anoms8110_<MON><YEAR>_cf.nc
#
# Bias Corrected SHIP only - for each <var>
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/FINALGRIDS/HadISDH.marine<var>.1.0.0.2017f_BClocalSHIP5x5both_anoms8110_<MON><YEAR>_cf.nc
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/FINALGRIDS/HadISDH.marine<var>.1.0.0.2017f_BClocalSHIP5x5day_anoms8110_<MON><YEAR>_cf.nc
# /project/hadobs2/hadisdh/marine/ICOADS3.0.0/FINALGRIDS/HadISDH.marine<var>.1.0.0.2017f_BClocalSHIP5x5night_anoms8110_<MON><YEAR>_cf.nc
# 
#
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
# 
# Version 1 (25 January 2018)
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
# This builds on the writing out part of the original IDL code written for HadISDH-land by Kate Willett grid_HadISDHFLAT_JAN2015.pro 
# functions in here should be usable for HadISDH-land
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
from GetNiceTimes import MakeDaysSince

# Set up variables
NowMon = 'FEB'
NowYear = '2019'
ClimStart = 1981
ClimEnd = 2010
RefPeriod = str(ClimStart)+' to '+str(ClimEnd)
ClimPeriod = str(ClimStart)[2:4]+str(ClimEnd)[2:4]
Version = '1.0.0.2018f'

################################################################################################################
# SUBROUTINES #
##################################################
# Write_Netcdf_Variable_All #
##################################################
def Write_Netcdf_Variable_All(outfile, var, vlong, vunit, vaxis, RefPeriod, TheMDI, data_arr):
    '''
    This is basically a tweak of the utils.py version but set up to work here
    and to be consistent with HadISDH netCDF files.
    
    The lats are the opposite to HadISDH.land so I'm flipping them here.
    
    Create the netcdf variable
    :param obj outfile: output file object
    :param string var: variable name
    :param list vlong: long variable name
    :param list vstandard: standard variable name
    :param str vunit: unit of variable
    :param str RefPeriod: period of climatological reference   
    :param np array data_arr: times, lats, lons data to write
    
    '''
    # If there is no time dimension
    if (len(np.shape(data_arr)) == 2):
        nc_var = outfile.createVariable(var, np.dtype('float'), ('latitude','longitude',), zlib = True, fill_value = TheMDI) # with compression
    # If there is a time dimension
    else:
        if (len(data_arr[:,0,0]) > 12):
            nc_var = outfile.createVariable(var, np.dtype('float64'), ('time','latitude','longitude',), zlib = True, fill_value = TheMDI) # with compression
        else:
            nc_var = outfile.createVariable(var, np.dtype('float64'), ('month','latitude','longitude',), zlib = True, fill_value = TheMDI) # with compression

    nc_var.long_name = vlong
    nc_var.units = vunit
    nc_var.missing_value = TheMDI
    nc_var.reference_period = RefPeriod
    
    # We're not using masked arrays here - hope that's not a problem
    nc_var.valid_min = np.min(data_arr[np.where(data_arr != TheMDI)]) 
    nc_var.valid_max = np.max(data_arr[np.where(data_arr != TheMDI)]) 
    nc_var[:] = np.flip(data_arr,axis = 1)
        
    return # write_netcdf_variable_all
    
###################################################################
# Write_NetCDF_All #
###################
def Write_NetCDF_All(filename, data_vals, data_counts, clim_vals, clim_counts, 
                     uH_vals, uS_vals, uC_vals, uR_vals, uM_vals, uOBS_vals, uSAMP_vals, usbarSQ_vals, urbar_vals, uFULL_vals, 
                     lats, lons, start_year, end_year, RefPeriod, var_name, long_abs, long_anoms, standard_abs, standard_anoms, unit, TheMDI): 


    '''
    This is basically a copy of utils.py version but tweaked to work here and now be consistent with HadISDH.land files
    
    2 sigma uncertainties are passed in here and written out!!!
    
    Write the relevant fields out to a netCDF file.
    
    :param str filename: output filename  
    :param list of np arrays data_vals: the actuals and anomalies data array for [times, lats, lons]
    :param list of np arrays data_counts: the n_grids and n_obs data array for [times, lats, lons]
    :param list of np arrays clim_vals: the climatology and stdev data array for [times, lats, lons]
    :param list of np arrays clim_counts: the climatology n_grids and n_obs, nad stdev n_grids and n_obs data array for [times, lats, lons]
    :param list of np arrays uH_vals: the actuals and anomalies height uncertainty array for [times, lats, lons]
    :param list of np arrays uS_vals: the actuals and anomalies screen uncertainty array for [times, lats, lons]
    :param list of np arrays uC_vals: the actuals and anomalies climatology uncertainty array for [times, lats, lons]
    :param list of np arrays uR_vals: the actuals and anomalies whole number uncertainty array for [times, lats, lons]
    :param list of np arrays uM_vals: the actuals and anomalies measurement uncertainty array for [times, lats, lons]
    :param list of np arrays uOBS_vals: the actuals and anomalies total obs uncertainty array for [times, lats, lons]
    :param list of np arrays uSAMP_vals: the actuals and anomalies sampling uncertainty array for [times, lats, lons]
    :param list of np arrays usbarSQ_vals: the actuals and anomalies sbarSQ uncertainty array for [times, lats, lons]
    :param list of np arrays urbar_vals: the actuals and anomalies rbar uncertainty array for [times, lats, lons]
    :param list of np arrays uFULL_vals: the actuals and anomalies full uncertainty array for [times, lats, lons]
    :param array lats: the latitudes
    :param array lons: the longitudes
    :param int start_year: the start year
    :param int end_year: the end year
    :param string RefPeriod: the climatological reference period.
    :param string var_name: the anomaly variable name for the NetCDF file
    :param string long_abs: the actual variable long name
    :param string long_anoms: the anomaly variable long name
    :param string standard_abs: the actual variable standard name
    :param string standard_anoms: the anomaly variable standard name
    :param string unit: the variable units
    :param float TheMDI: the missing data indicator

    '''

    # remove file
    if os.path.exists(filename):
        os.remove(filename)

    outfile = ncdf.Dataset(filename,'w', format='NETCDF4')

    # Set up dimensions
    # Get times in terms of days since 1973-1-1 00:00:00
    DaysSince = MakeDaysSince(start_year,1,end_year,12,'month')
#    print('Test days since')
#    pdb.set_trace()
    time_dim = outfile.createDimension('time',len(DaysSince))
    month_dim = outfile.createDimension('month',12)
    lat_dim = outfile.createDimension('latitude',len(lats)) # as TRC of box edges given, size = # box centres to be written
    lon_dim = outfile.createDimension('longitude',len(lons))
    
    #***********
    # set up basic variables linked to dimensions
    # make time variable
    nc_var = outfile.createVariable('time', np.dtype('int'), ('time'), zlib = True) # with compression!!!
    nc_var.long_name = "time"
    nc_var.units = "days since 1973-1-1 00:00:00"
    nc_var.standard_name = "time"
    nc_var.start_year = str(start_year)
    nc_var.end_year = str(end_year)
    nc_var.start_month = '1'
    nc_var.end_month = '12'
    nc_var[:] = DaysSince

    # make month variable
    nc_var = outfile.createVariable('month', np.dtype('int'), ('month'), zlib = True) # with compression!!!
    nc_var.long_name = "month of year"
    nc_var.units = "month"
    nc_var.standard_name = "time in months"
    #nc_var.start_year = str(StartYear)
    #nc_var.end_year = str(EndYear)
    nc_var.start_month = '1'
    nc_var.end_month = '12'
    nc_var[:] = range(12)
    
    # make latitude variable
    nc_var = outfile.createVariable('latitude', np.dtype('float32'), ('latitude'), zlib = True) # with compression!!!
    nc_var.long_name = "latitude"
    nc_var.units = "degrees_north"
    nc_var.standard_name = "latitude"
    nc_var.point_spacing = "even"
    nc_var.axis = "X"
    # The lats are the opposite to HadISDH.land so I'm flipping them here.
    nc_var[:] = np.flip(lats)
    
    # make longitude variable
    nc_var = outfile.createVariable('longitude', np.dtype('float32'), ('longitude'), zlib = True) # with compression!!!
    nc_var.long_name = "longitude"
    nc_var.units = "degrees_east"
    nc_var.standard_name = "longitude"
    nc_var.point_spacing = "even"
    nc_var.axis = "X"
    nc_var[:] = lons

    #***********
    # create variables actuals
    Write_Netcdf_Variable_All(outfile, var_name+'_abs', long_abs, unit, 'T', RefPeriod, TheMDI, data_vals[0])
    # create variables anomalies
    Write_Netcdf_Variable_All(outfile, var_name+'_anoms', long_anoms, unit, 'T', RefPeriod, TheMDI, data_vals[1])
    # create variables n_grids
    Write_Netcdf_Variable_All(outfile, var_name+'_n_grids', 'Number of 1by1 daily grids within gridbox', 'standard', 'T', RefPeriod, -1, data_counts[0])
    # create variables n_obs
    Write_Netcdf_Variable_All(outfile, var_name+'_n_obs', 'Number of observations within gridbox', 'standard', 'T', RefPeriod, -1, data_counts[1])

    # create variables climatology
    Write_Netcdf_Variable_All(outfile, var_name+'_clims', 'Monthly climatological mean', unit, 'T', RefPeriod, TheMDI, clim_vals[0])
    # create variables climatololgy n_grids
    Write_Netcdf_Variable_All(outfile, var_name+'_clims_n_grids', 'Number of 1by1 daily grids within gridbox climatology', 'standard', 'T', RefPeriod, -1, clim_counts[0])
    # create variables climatology n_obs
    Write_Netcdf_Variable_All(outfile, var_name+'_clims_n_obs', 'Number of observations within gridbox climatology', 'standard', 'T', RefPeriod, -1, clim_counts[1])
    # create variables climatological stdev
    Write_Netcdf_Variable_All(outfile, var_name+'_clim_std', 'Monthly climatological standard deviation', unit, 'T', RefPeriod, TheMDI, clim_vals[1])
    # create variables climatological stdev n_grids
    Write_Netcdf_Variable_All(outfile, var_name+'_clim_std_n_grids', 'Number of 1by1 daily grids within gridbox climatological standard deviation', 'standard', 'T', RefPeriod, -1, clim_counts[2])
    # create variables climatological stdev n_obs
    Write_Netcdf_Variable_All(outfile, var_name+'_clim_std_n_obs', 'Number of observations within gridbox climatological standard deviation', 'standard', 'T', RefPeriod, -1, clim_counts[3])

    # create variables height unc actuals
    Write_Netcdf_Variable_All(outfile, var_name+'_abs_uHGT', long_abs+' height adjustment uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uH_vals[0])
    # create variables height unc anomalies
    Write_Netcdf_Variable_All(outfile, var_name+'_anoms_uHGT', long_anoms+' height adjustment uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uH_vals[1])
    # create variables screen unc actuals
    Write_Netcdf_Variable_All(outfile, var_name+'_abs_uSCN', long_abs+' non-ventilated instrument adjustment uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uS_vals[0])
    # create variables screen unc anomalies
    Write_Netcdf_Variable_All(outfile, var_name+'_anoms_uSCN', long_anoms+' non-ventilated instrument adjustment uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uS_vals[1])
    # create variables climatology unc actuals
    Write_Netcdf_Variable_All(outfile, var_name+'_abs_uC', long_abs+' climatology uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uC_vals[0])
    # create variables climatology unc anomalies
    Write_Netcdf_Variable_All(outfile, var_name+'_anoms_uC', long_anoms+' climatology uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uC_vals[1])
    # create variables whole number unc actuals
    Write_Netcdf_Variable_All(outfile, var_name+'_abs_uR', long_abs+' whole number uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uR_vals[0])
    # create variables whole number unc anomalies
    Write_Netcdf_Variable_All(outfile, var_name+'_anoms_uR', long_anoms+' whole number uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uR_vals[1])
    # create variables measurement unc actuals
    Write_Netcdf_Variable_All(outfile, var_name+'_abs_uM', long_abs+' measurement uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uM_vals[0])
    # create variables measurement unc anomalies
    Write_Netcdf_Variable_All(outfile, var_name+'_anoms_uM', long_anoms+' measurement uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uM_vals[1])

    # create variables total obs unc actuals
    Write_Netcdf_Variable_All(outfile, var_name+'_abs_uOBS', long_abs+' total observation uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uOBS_vals[0])
    # create variables total obs unc anomalies
    Write_Netcdf_Variable_All(outfile, var_name+'_anoms_uOBS', long_anoms+' total observation uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uOBS_vals[1])
    # create variables sampling unc actuals
    Write_Netcdf_Variable_All(outfile, var_name+'_abs_uSAMP', long_abs+' gridbox sampling uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uSAMP_vals[0])
    # create variables sampling unc n_grids
    Write_Netcdf_Variable_All(outfile, var_name+'_uSAMP_n_grids', long_abs+' gridbox sampling uncertainty number of pseudo-stations', unit, 'T', RefPeriod, -1, uSAMP_vals[2])
    # create variables samplins unc anomalies
    Write_Netcdf_Variable_All(outfile, var_name+'_anoms_uSAMP', long_anoms+' gridbox sampling uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uSAMP_vals[1])
    # create variables sampling unc sbarSQ actuals
    Write_Netcdf_Variable_All(outfile, var_name+'_abs_usbarSQ', long_abs+' gridbox mean station variance (sbarSQ for sampling uncertainty)', unit, 'T', RefPeriod, TheMDI, usbarSQ_vals[0])
    # create variables sampling unc sbarSQ n_grids
    Write_Netcdf_Variable_All(outfile, var_name+'_usbarSQ_n_grids', long_abs+' gridbox sampling uncertainty number of pseudo-stations', unit, 'T', RefPeriod, -1, usbarSQ_vals[2])
    # create variables sampling unc sbarSQ anomalies
    Write_Netcdf_Variable_All(outfile, var_name+'_anoms_usbarSQ', long_anoms+' gridbox mean station variance (sbarSQ for sampling uncertainty)', unit, 'T', RefPeriod, TheMDI, usbarSQ_vals[1])
    # create variables sampling unc rbar actuals
    Write_Netcdf_Variable_All(outfile, var_name+'_abs_urbar', long_abs+' gridbox mean intersite correlation (rbar for sampling uncertainty)', unit, 'T', RefPeriod, TheMDI, urbar_vals[0])
    # create variables sampling unc rbar anomalies
    Write_Netcdf_Variable_All(outfile, var_name+'_anoms_urbar', long_anoms+' gridbox mean intersite correlation (rbar for sampling uncertainty)', unit, 'T', RefPeriod, TheMDI, urbar_vals[1])
    # create variables FULL unc actuals
    Write_Netcdf_Variable_All(outfile, var_name+'_abs_uFULL', long_abs+' full gridbox uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uFULL_vals[0])
    # create variables FULL unc anomalies
    Write_Netcdf_Variable_All(outfile, var_name+'_anoms_uFULL', long_anoms+' full gridbox uncertainty (2 sigma)', unit, 'T', RefPeriod, TheMDI, uFULL_vals[1])

    # Global Attributes 
    
    # Read these from file
    attr_file = os.path.join(os.getcwd(), "HadISDH_attributes.dat")

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
 
    outfile.file_created = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d, %H:%M")
    outfile.Conventions = 'CF-1.5' 
    outfile.Metadata_Conventions = 'Unidata Dataset Discovery v1.0,CF Discrete Sampling Geometries Conventions'
    outfile.featureType = 'gridded'
    
    outfile.close()

    return # Write_NetCDF_All
    
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
        print('Usage (as strings) Create_HadISDHMarine_finalgrids.py --year1 <1973> --year2 <2017> '+\
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
    # Read in

    VarList = ['marine_air_temperature','dew_point_temperature','specific_humidity','vapor_pressure','relative_humidity','wet_bulb_temperature','dew_point_depression','n_grids','n_obs'] # This is the ReadInfo
    VarLong = ['Marine Air Temperature','Dew Point Temperature','Specific Humidity','Vapor Pressure','Relative Humidity','Wet Bulb Temperature','Dew Point Pepression'] # This is the ReadInfo
    VarLong = ['Monthly Mean '+i for i in VarLong]
    VarStandard = ['marine air temperarature','dew point temperature','specific humidity','vapor pressure','relative humidity','wet bulb temperature','dew point depression'] # This is the ReadInfo
    AnomsVarList = [i+'_anomalies' for i in VarList[0:7]]
#    AnomsVarList.append(VarList[7:9])
    AnomsVarLong = [i+' Anomalies' for i in VarLong]
    AnomsVarStandard = [i+' anomalies' for i in VarStandard]
    var_loop = ['T','Td','q','e','RH','Tw','DPD']
    var_loop_lower = ['t','td','q','e','rh','tw','dpd']
    units_loop = ['degrees C','degrees C','g/kg','hPa','%rh','degrees C','degrees C','standard','standard','standard']
        
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
    FilClim = 'OBSclim2BClocal_5x5_monthly_climatology_from_daily_'+timings+'_relax.nc'
    FilStd = 'OBSclim2BClocal_5x5_monthly_stdev_from_daily_'+timings+'_relax.nc'
    FilUR = 'OBSclim2BClocal_uR_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUC = 'OBSclim2BClocal_uC_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUM = 'OBSclim2BClocal_uM_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUSCN = 'OBSclim2BClocal_uSCN_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUHGT = 'OBSclim2BClocal_uHGT_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUOBS = 'OBSclim2BClocal_uOBS_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUSAMP = 'OBSclim2BClocal_uSAMP_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUsbarSQ = 'OBSclim2BClocal_usbarSQ_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUrbar = 'OBSclim2BClocal_urbar_5x5_monthly_from_daily_'+timings+'_relax.nc'
    FilUFULL = 'OBSclim2BClocal_uFULL_5x5_monthly_from_daily_'+timings+'_relax.nc'

    # Output File
#    # if running as hadobs
#    OutFilBit1 = WorkingDir+'HadISDH.marine' # add <var> from var_loop
    # if running as hadkw
    OutFilBit1 = 'TMPDIR/HadISDH.marine' # add <var> from var_loop
    if platform == 'ship': 
        OutFilBit2 = '.'+Version+'_BClocalSHIP5by5'+timings+'_anoms'+ClimPeriod+'_'+NowMon+NowYear+'_cf.nc'
    else:
        OutFilBit2 = '.'+Version+'_BClocal5by5'+timings+'_anoms'+ClimPeriod+'_'+NowMon+NowYear+'_cf.nc'
    
    # Set up necessary dates - dates for output are just counts of months from 0 to 54?...
    StYr = int(year1)
    EdYr = int(year2)
    Ntims = ((EdYr + 1) - StYr) * 12
    TimesArr = np.arange(Ntims) # months since January 1973 

#########
    # Loop through each variable to create the combined file
        
    # Which variable to loop through?
    for v,var in enumerate(var_loop):

        # Set up empty lists to store numpy arrays of actuals and anoms of each quantity - reset with each var initialisation
        ValuesList = [] # for actuals and anoms
        ValCountsList = [] # for n_grids and n_obs
        ClimStdCountsList = [] # for clim n_grids and n_obs then std n_grids and n_obs (these should be the same but may not be)
        ClimStdList = [] # for climatology and standard deviation

        HgtUncList = [] # for height uncertainty actuals and anoms
        ScnUncList = [] # for screen uncertainty actuals and anoms
        CUncList = [] # for climatology uncertainty actuals and anoms
        RUncList = [] # for whole number uncertainty actuals and anoms
        MUncList = [] # for measurement uncertainty actuals and anoms

        SampUncList = [] # for sampling uncertainty actuals and anoms
        sbarSQList = []
        rbarList = []

        TotObsUncList = [] # for total obs uncertainty acutals and anoms

        FullUncList = [] # for full uncertainty actuals and anoms.
    
        # Read in actuals, n grids and n_obs
        Filee = WorkingDir+FilAbs
        LatInfo = ['latitude']
        LonInfo = ['longitude']
        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v],VarList[7],VarList[8]],LatInfo,LonInfo)
        # This comes out as:
        # TmpDataList: a list of np arrays (times, lats{87.5N to 87.5S], lons[-177.5W to 177.5E])
        # LatList: an NLats np array of lats centres (87.5N to 87.5S)
        # LonList: an NLons np array of lons centres (87.5N to 87.5S)
    
        # Get lat and lon counts
        NLats = len(LatList)
        NLons = len(LonList)
    
        # Fill in lists
        ValuesList.append(TmpDataList[0]) # actuals
        ValCountsList.append(TmpDataList[1]) # n_grids
        ValCountsList.append(TmpDataList[2]) # n_obs
	    
        # Read in anomalies
        Filee = WorkingDir+FilAnoms
        LatInfo = ['latitude']
        LonInfo = ['longitude']
        TmpDataList, LatList, LonList = GetGrid4(Filee,[AnomsVarList[v]],LatInfo,LonInfo)
        
        # Fill in lists
        ValuesList.append(TmpDataList) # anomalies
    
        # Read in climatology and standard deviation
        Filee = WorkingDir+FilClim
        LatInfo = ['latitude']
        LonInfo = ['longitude']
        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v],VarList[7],VarList[8]],LatInfo,LonInfo)
        
        # Fill in lists
        ClimStdList.append(TmpDataList[0]) # climatology
        ClimStdCountsList.append(TmpDataList[1]) # n_grids
        ClimStdCountsList.append(TmpDataList[2]) # n_obs
    
        Filee = WorkingDir+FilStd
        LatInfo = ['latitude']
        LonInfo = ['longitude']
        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v],VarList[7],VarList[8]],LatInfo,LonInfo)
        
        # Fill in lists
        ClimStdList.append(TmpDataList[0]) # standard deviation
        ClimStdCountsList.append(TmpDataList[1]) # n_grids
        ClimStdCountsList.append(TmpDataList[2]) # n_obs

        # FROM HERE ON WE ARE DEALING WITH UNCERTAINTIES IN 1 SIGMA SO THESE NEED TO BE DOUBLED TO 2 SIGMA!!!
    
        # Read in observation height uncertainties
        Filee = WorkingDir+FilUHGT
        LatInfo = ['latitude']
        LonInfo = ['longitude']
        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v]+'_uHGT',AnomsVarList[v]+'_uHGT'],LatInfo,LonInfo)

        # Make these 2 sigma
        TmpDataList[0][np.where(TmpDataList[0] > MDI)] = 2. * TmpDataList[0][np.where(TmpDataList[0] > MDI)]
        TmpDataList[1][np.where(TmpDataList[1] > MDI)] = 2. * TmpDataList[1][np.where(TmpDataList[1] > MDI)]
        
        # Fill in lists
        HgtUncList.append(TmpDataList[0]) # actuals 
        HgtUncList.append(TmpDataList[1]) # anomalies 
    
        # Read in observation screen uncertainties
        Filee = WorkingDir+FilUSCN
        LatInfo = ['latitude']
        LonInfo = ['longitude']
        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v]+'_uSCN',AnomsVarList[v]+'_uSCN'],LatInfo,LonInfo)

        # Make these 2 sigma
        TmpDataList[0][np.where(TmpDataList[0] > MDI)] = 2. * TmpDataList[0][np.where(TmpDataList[0] > MDI)]
        TmpDataList[1][np.where(TmpDataList[1] > MDI)] = 2. * TmpDataList[1][np.where(TmpDataList[1] > MDI)]
        
        # Fill in lists
        ScnUncList.append(TmpDataList[0]) # actuals 
        ScnUncList.append(TmpDataList[1]) # anomalies 

        # Read in observation climatology uncertainties
        Filee = WorkingDir+FilUC
        LatInfo = ['latitude']
        LonInfo = ['longitude']
        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v]+'_uC',AnomsVarList[v]+'_uC'],LatInfo,LonInfo)

        # Make these 2 sigma
        TmpDataList[0][np.where(TmpDataList[0] > MDI)] = 2. * TmpDataList[0][np.where(TmpDataList[0] > MDI)]
        TmpDataList[1][np.where(TmpDataList[1] > MDI)] = 2. * TmpDataList[1][np.where(TmpDataList[1] > MDI)]
        
        # Fill in lists
        CUncList.append(TmpDataList[0]) # actuals 
        CUncList.append(TmpDataList[1]) # anomalies 

        # Read in observation whole number uncertainties
        Filee = WorkingDir+FilUR
        LatInfo = ['latitude']
        LonInfo = ['longitude']
        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v]+'_uR',AnomsVarList[v]+'_uR'],LatInfo,LonInfo)
        
        # Make these 2 sigma
        TmpDataList[0][np.where(TmpDataList[0] > MDI)] = 2. * TmpDataList[0][np.where(TmpDataList[0] > MDI)]
        TmpDataList[1][np.where(TmpDataList[1] > MDI)] = 2. * TmpDataList[1][np.where(TmpDataList[1] > MDI)]

        # Fill in lists
        RUncList.append(TmpDataList[0]) # actuals 
        RUncList.append(TmpDataList[1]) # anomalies 

        # Read in observation measurement uncertainties
        Filee = WorkingDir+FilUM
        LatInfo = ['latitude']
        LonInfo = ['longitude']
        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v]+'_uM',AnomsVarList[v]+'_uM'],LatInfo,LonInfo)
        
        # Make these 2 sigma
        TmpDataList[0][np.where(TmpDataList[0] > MDI)] = 2. * TmpDataList[0][np.where(TmpDataList[0] > MDI)]
        TmpDataList[1][np.where(TmpDataList[1] > MDI)] = 2. * TmpDataList[1][np.where(TmpDataList[1] > MDI)]

        # Fill in lists
        MUncList.append(TmpDataList[0]) # actuals 
        MUncList.append(TmpDataList[1]) # anomalies 
     
        # Read in gridbox uncertainties for total observation
        Filee = WorkingDir+FilUOBS
        LatInfo = ['latitude']
        LonInfo = ['longitude']
        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v]+'_OBS',AnomsVarList[v]+'_OBS'],LatInfo,LonInfo)
        
        # Make these 2 sigma
        TmpDataList[0][np.where(TmpDataList[0] > MDI)] = 2. * TmpDataList[0][np.where(TmpDataList[0] > MDI)]
        TmpDataList[1][np.where(TmpDataList[1] > MDI)] = 2. * TmpDataList[1][np.where(TmpDataList[1] > MDI)]

        # Fill in lists
        TotObsUncList.append(TmpDataList[0]) # actuals 
        TotObsUncList.append(TmpDataList[1]) # anomalies 

        # Read in gridbox uncertainties for sampling
        Filee = WorkingDir+FilUSAMP
        LatInfo = ['latitude']
        LonInfo = ['longitude']
        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v]+'_SAMP',AnomsVarList[v]+'_SAMP',VarList[7]],LatInfo,LonInfo)
        
        # Make these 2 sigma
        TmpDataList[0][np.where(TmpDataList[0] > MDI)] = 2. * TmpDataList[0][np.where(TmpDataList[0] > MDI)]
        TmpDataList[1][np.where(TmpDataList[1] > MDI)] = 2. * TmpDataList[1][np.where(TmpDataList[1] > MDI)]

        # Fill in lists
        SampUncList.append(TmpDataList[0]) # actuals 
        SampUncList.append(TmpDataList[1]) # anomalies 
        SampUncList.append(TmpDataList[2]) # n_grids 

        Filee = WorkingDir+FilUsbarSQ
        LatInfo = ['latitude']
        LonInfo = ['longitude']
#        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v]+'_sbarSQ',AnomsVarList[v]+'_sbarSQ','sbarSQ'],LatInfo,LonInfo)
        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v]+'_sbarSQ',AnomsVarList[v]+'_sbarSQ',VarList[7]],LatInfo,LonInfo)
        
        # Do not need to Make these 2 sigma

        # Fill in lists
        sbarSQList.append(TmpDataList[0]) # actuals 
        sbarSQList.append(TmpDataList[1]) # anomalies 
        sbarSQList.append(TmpDataList[2]) # n_grids 

        Filee = WorkingDir+FilUrbar
        LatInfo = ['latitude']
        LonInfo = ['longitude']
        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v]+'_rbar',AnomsVarList[v]+'_rbar'],LatInfo,LonInfo)
        
        # Do not need to Make these 2 sigma

        # Fill in lists
        rbarList.append(TmpDataList[0]) # actuals 
        rbarList.append(TmpDataList[1]) # anomalies 

        # Read in gridbox uncertainties for full
        Filee = WorkingDir+FilUFULL
        LatInfo = ['latitude']
        LonInfo = ['longitude']
        TmpDataList, LatList, LonList = GetGrid4(Filee,[VarList[v]+'_FULL',AnomsVarList[v]+'_FULL'],LatInfo,LonInfo)
        
        # Make these 2 sigma
        TmpDataList[0][np.where(TmpDataList[0] > MDI)] = 2. * TmpDataList[0][np.where(TmpDataList[0] > MDI)]
        TmpDataList[1][np.where(TmpDataList[1] > MDI)] = 2. * TmpDataList[1][np.where(TmpDataList[1] > MDI)]

        # Fill in lists
        FullUncList.append(TmpDataList[0]) # actuals 
        FullUncList.append(TmpDataList[1]) # anomalies 
        
##############
        # Write out combined file as 2 sigma!!!.

        Write_NetCDF_All(OutFilBit1+var_loop[v]+OutFilBit2,
                         ValuesList,ValCountsList,ClimStdList,ClimStdCountsList,
                         HgtUncList,ScnUncList,CUncList,RUncList,MUncList,TotObsUncList,SampUncList,sbarSQList,rbarList,FullUncList,
                         LatList,LonList,StYr,EdYr,RefPeriod,var_loop_lower[v],VarLong[v],AnomsVarLong[v],VarStandard[v],AnomsVarStandard[v],units_loop[v],MDI)

#########

    print('And we are done!')

if __name__ == '__main__':
    
    main(sys.argv[1:])
