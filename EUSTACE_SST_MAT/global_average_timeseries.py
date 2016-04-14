#!/usr/local/sci/bin/python2.7
#*****************************
#
# Take monthly merged files and output global average timeseries
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
Take monthly merged ("_both") files and output global average timeseries

-----------------------
LIST OF MODULES
-----------------------
utils.py

-----------------------
DATA
-----------------------
Input data stored in:
/project/hadobs2/hadisdh/marine/GRIDS2/

Exact folder set by "OUTROOT" - as depends on bias correction.

-----------------------
HOW TO RUN THE CODE
-----------------------
python2.7 global_average_timeseries.py --suffix relax --period day --start_year YYYY --end_year YYYY --start_month MM --end_month MM

python2.7 global_average_timeseries.py --help 
will show all options

-----------------------
OUTPUT
-----------------------
Plots to appear in 
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/PLOTS2/

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
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import calendar
import gc
import netCDF4 as ncdf
import copy

import utils

#Constants in CAPS
OUTROOT = "ERAclimNBC"

DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS2/"
PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS2/"

mdi = -1.e30


START_YEAR = 1973


#***************************************
def mask_and_normalise_weights(cosines, data):
    '''
    Apply data mask to cosines and re-normalise.

    :param array cosines: single field of cosine(lat)s for entire grid
    :param array data: masked data from which to extract mask

    :returns: full_cosines - matched to coverage and time extent of data
    '''

    full_cosines=np.ma.array([cosines for y in range(data.shape[0])])

    full_cosines.mask = np.array([data.mask[y] for y in range(data.shape[0])])

    for y in range(data.shape[0]):
        full_cosines[y,:,:]=full_cosines[y,:,:]/np.sum(full_cosines[y,:,:])
    
    return full_cosines # mask_and_normalise_weights

#***************************************
def write_ncdf_ts(times, OBS_ORDER, filename, annual = False, monthly = False, do_zip = True):
    '''
    Code to output the timeseries as netCDF files.

    :param array times: out times in datetime format
    :param list OBS_ORDER: list of MetVars which include .adata and .mdata attributes for annual and monthly series
    :param str filename: output filename
    :param bool annual: annual timeseries
    :param bool monthly: monthly timeseries
    :param bool do_zip: apply internal compression

    :returns:
    '''


    if not annual and not monthly:
        print "must choose one of annual or monthly"
        return
    elif annual and monthly:
        print "must choose only one of annual or monthly"
        return
    
    outfile = ncdf.Dataset(filename,'w', format='NETCDF4')


    # sort the time dimension + variable
    time_dim = outfile.createDimension('time',len(times))
    time_units = "days since 1973-01-01 00:00:00"   
    nc_var = outfile.createVariable("time", np.dtype('int'), ('time'), zlib = do_zip)
    nc_var.long_name = "time"
    nc_var.units = time_units
    nc_var.standard_name = "time"
    times = ncdf.date2num(times, units = time_units, calendar = 'gregorian')
    nc_var[:] = times
 
    # write all other variables
    for v, var in enumerate(OBS_ORDER):
        nc_var = outfile.createVariable(var.name, var.dtype, ('time',), zlib = do_zip, fill_value = var.mdi)

        nc_var.long_name = var.long_name
        nc_var.units = var.units
        nc_var.missing_value = var.mdi
        nc_var.standard_name = var.standard_name
        if annual:
            nc_var[:] = var.adata
        elif monthly:
            nc_var[:] = var.mdata
            
    # final bits
    outfile.date_created = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d, %H:%M")
    outfile.Conventions = 'CF-1.5' 
    outfile.Metadata_Conventions = 'Unidata Dataset Discovery v1.0,CF Discrete Sampling Geometries Conventions'
    outfile.featureType = 'timeseries'
    
    outfile.close()

    return # write_ncdf_ts
#***************************************
#***************************************

# monthly -> annual
suffix = "relax"

watermarkstring="/".join(os.getcwd().split('/')[4:])+'/'+os.path.basename( __file__ )+"   "+dt.datetime.strftime(dt.datetime.now(), "%d-%b-%Y %H:%M")


for period in ["both", "day", "night"]:

    filename = "{}/{}_5x5_monthly_from_daily_{}_{}.nc".format(DATA_LOCATION, OUTROOT, period, suffix) 

    ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

    lat_centres = ncdf_file.variables["latitude"]
    lon_centres = ncdf_file.variables["longitude"]

    n_obs = utils.set_MetVar_attributes("n_obs", "Number of Observations", "Number of Observations", 1, -1, np.dtype("int16"), 0)
    OBS_ORDER = utils.make_MetVars(mdi, multiplier = False)
    OBS_ORDER += [n_obs]


    for v, var in enumerate(OBS_ORDER):
        print var.name


        var.data = ncdf_file.variables[var.name][:]

        # make annual and monthly timeseries

        mesh_lon, mesh_lat = np.meshgrid(lon_centres, lat_centres)
        cosines = np.cos(np.radians(mesh_lat))

        full_cosines = mask_and_normalise_weights(cosines, var.data)
        #masked weights now sum to one for each field

        if var.name == "n_obs":
            weighted_data = var.data
        else:
            weighted_data = var.data * full_cosines

        plot_values = np.zeros(weighted_data.shape[0])
        plot_times = []
        for y in range(weighted_data.shape[0]):

            plot_values[y] = np.ma.sum(weighted_data[y])

            plot_times += [dt.datetime(START_YEAR+(y/12), 1 + (y%12), 1, 0, 0)]

        # plot the monthly data
        plt.clf()
        plt.plot(plot_times, plot_values, "r-", label = "Monthly")

        var.mdata = plot_values
        monthly_times = plot_times

        # and annual
        plot_values = plot_values.reshape(-1, 12)
        
        if var.name != "n_obs":
            plot_values = np.mean(plot_values, axis = 1)
        else:
            plot_values = np.sum(plot_values, axis = 1)

        plot_times = [dt.datetime(START_YEAR+y, 7, 1) for y in range(plot_values.shape[0])]
        plt.plot(plot_times, plot_values, "b-", label = "Annual")

        var.adata = plot_values
        annual_times = plot_times

        # and prettify the plot
        plt.title(" ".join([x.capitalize() for x in var.name.split("_")]))
        plt.ylabel(var.units)
        plt.legend()
        plt.figtext(0.01,0.01,watermarkstring,size=6)

        plt.savefig("{}/{}_5x5_monthly_from_daily_{}_{}_ts.png".format(PLOT_LOCATION, OUTROOT, period, var.name))

    # clean up
    ncdf_file.close()
    del(weighted_data)
    del(full_cosines)
    gc.collect()

    # write output files
    filename = "{}/{}_5x5_monthly_from_daily_{}_{}_ts_annual.nc".format(DATA_LOCATION, OUTROOT, period, suffix) 
    if os.path.exists(filename):
        os.remove(filename)
    write_ncdf_ts(annual_times, OBS_ORDER, filename, annual = True, do_zip = True)

    filename = "{}/{}_5x5_monthly_from_daily_{}_{}_ts_monthly.nc".format(DATA_LOCATION, OUTROOT, period, suffix) 
    if os.path.exists(filename):
        os.remove(filename)
    write_ncdf_ts(monthly_times, OBS_ORDER, filename, monthly = True, do_zip = True)

    # clean up
    del(plot_values)
    del(plot_times)
    del(OBS_ORDER)
    gc.collect()

sys.exit()
# pentad -> annual


OBS_ORDER = utils.make_MetVars(mdi, multiplier = False)

for v, var in enumerate(OBS_ORDER):
    print var.name


    filename = "{}/{}_1x1_pentads_from_3hrly_{}_{}_{}.nc".format(DATA_LOCATION, OUTROOT, var.name, period, suffix) 

    ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

    lat_centres = ncdf_file.variables["latitude"]
    lon_centres = ncdf_file.variables["longitude"]

    data_shape = ncdf_file.variables[var.name][:].shape

    # pentads
    mesh_lon, mesh_lat = np.meshgrid(lon_centres, lat_centres)
    cosines = np.cos(np.radians(mesh_lat))

    plot_values = np.zeros(data_shape[0])
    plot_times = []
    year = copy.deepcopy(START_YEAR)

    for ts in range(data_shape[0]):

        data = ncdf_file.variables[var.name][ts]

        full_cosines = np.ma.array(cosines)
        full_cosines.mask = data.mask
        full_cosines = full_cosines / np.sum(full_cosines)

        weighted_data = data * full_cosines

        plot_values[ts] = np.ma.sum(weighted_data)

        if calendar.isleap(year) and  ((ts+1)*5)%365 > 60:
            # account for 6 day pentad in leap years
            plot_times += [dt.datetime(year, 1 , 1, 0, 0) + dt.timedelta(days = ((ts+1)*5)%365 + 1)]
        else:
            plot_times += [dt.datetime(year, 1 , 1, 0, 0) + dt.timedelta(days = ((ts+1)*5)%365)]

        print year, ts, plot_times[-1]

        if ((ts+1)*5)%365 == 0:
            year += 1
            


    plt.clf()
    plt.plot(plot_times, plot_values, "r-")
    plt.title(var.name)
    plt.ylabel(var.units)

    # annual

    plot_values = plot_values.reshape(-1, 73, data_shape[-2], data_shape[-1])
    plot_values = np.mean(plot_values, axis = 1)

    plt.plot(plot_times[36::73], plot_values, "b-")
    
    plt.savefig("{}/{}_pentads_all.png".format(PLOT_LOCATION, var.name))

    raw_input("check")

# END
# ************************************************************************
