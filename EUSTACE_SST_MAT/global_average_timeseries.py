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
Take monthly merged files and output global average timeseries

For actuals and anomalies

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
python2.7 global_average_timeseries.py 

-----------------------
OUTPUT
-----------------------
Plots to appear in 
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/PLOTS2/

-----------------------
VERSION/RELEASE NOTES
-----------------------

Version 2 (29 September 2016) Kate Willett
---------
 
Enhancements
Can now cope with the three iteration approach
Look for # KATE modified
         ...
	 # end
 
Changes
 
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
import matplotlib.pyplot as plt
import calendar
import gc
import netCDF4 as ncdf
import copy

import utils
import set_paths_and_vars
defaults = set_paths_and_vars.set()

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
# KATE modified
def make_timeseries(suffix = "relax", doQC = False, doQC1it = False, doQC2it = False, doQC3it = False, doBC = False):
#def make_timeseries(suffix = "relax", doQC = False, doBC = False):
# end
    '''
    Make the timeseries - plots and netCDF files

    :param str suffix: "relax" or "strict" criteria
    :param bool doQC: incorporate the QC flags or not
# KATE modified
    :param bool doQC1it: incorporate the first iteration QC flags or not
    :param bool doQC2it: incorporate the second iteration QC flags or not
    :param bool doQC3it: incorporate the third iteration QC flags or not
# end
    :param bool doBC: work on the bias corrected data

    :returns:
    '''
# KATE modified
    settings = set_paths_and_vars.set(doBC = doBC, doQC = doQC, doQC1it = doQC1it, doQC2it = doQC2it, doQC3it = doQC3it)
    #settings = set_paths_and_vars.set(doBC = doBC, doQC = doQC)
# end

    print "Do QC = {}".format(doQC)
# KATE modified
    print "Do QC1it = {}".format(doQC1it)
    print "Do QC2it = {}".format(doQC2it)
    print "Do QC3it = {}".format(doQC3it)
# end
    print "Do BC = {}".format(doBC)


    # monthly -> annual

    watermarkstring="/".join(os.getcwd().split('/')[4:])+'/'+os.path.basename( __file__ )+"   "+dt.datetime.strftime(dt.datetime.now(), "%d-%b-%Y %H:%M")

    # run on the actuals (which include anomalies from ERA) and the anomalies (calculated from obs-actuals, but also include the anomalies from ERA)
# KATE modified to add new file name bit '_renorm19812010'
    for version in ["", "_renorm19812010_anomalies"]:
    #for version in ["", "_anomalies"]:
# end
        if version == "":
            print "5x5 monthly Standard"
        elif version == "_anomalies":
            print "5x5 monthly Anomalies"

        for period in ["both", "day", "night"]:
            print period

            filename = "{}/{}_5x5_monthly{}_from_daily_{}_{}.nc".format(settings.DATA_LOCATION, settings.OUTROOT, version, period, suffix) 

            print filename
	    ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

            lat_centres = ncdf_file.variables["latitude"]
            lon_centres = ncdf_file.variables["longitude"]

            n_obs = utils.set_MetVar_attributes("n_obs", "Number of Observations", "Number of Observations", 1, -1, np.dtype("int64"), 0)
            OBS_ORDER = utils.make_MetVars(settings.mdi, multiplier = False)
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

                    plot_times += [dt.datetime(settings.START_YEAR+(y/12), 1 + (y%12), 1, 0, 0)]

                # plot the monthly data
                plt.clf()
                plt.plot(plot_times, plot_values, "r-", label = "Monthly")

                var.mdata = plot_values
                monthly_times = plot_times

                # and annual
                plot_values = plot_values.reshape(-1, 12)

                if var.name != "n_obs":
                    plot_values = np.mean(plot_values, axis = 1)
                    plot_times = [dt.datetime(settings.START_YEAR+y, 7, 1) for y in range(plot_values.shape[0])]
                    plt.plot(plot_times, plot_values, "b-", label = "Annual")

                    plt.ylabel(var.units)


                else:
                    # if n_obs, then have second x-axis
                    plot_values = np.sum(plot_values, axis = 1)
                    plot_times = [dt.datetime(settings.START_YEAR+y, 7, 1) for y in range(plot_values.shape[0])]

                    # finish off first axis
                    ax1 = plt.gca()
                    ax1.set_ylabel("Monthly", color='r')
                    for tl in ax1.get_yticklabels():
                        tl.set_color('r')
                    
                    # add second axis
                    ax2 = ax1.twinx()
                    ax2.plot(plot_times, plot_values, "b-", label = "Annual")
                    ax2.set_ylabel("Annual", color='b')
                    for tl in ax2.get_yticklabels():
                        tl.set_color('b')
                   
                    

                var.adata = plot_values
                annual_times = plot_times

                # and prettify the plot
                plt.title(" ".join([x.capitalize() for x in var.name.split("_")]))
                if var.name != "n_obs": plt.legend()
                plt.figtext(0.01,0.01,watermarkstring,size=6)

                plt.savefig("{}/{}_5x5_monthly{}_from_daily_{}_{}_ts.png".format(settings.PLOT_LOCATION, settings.OUTROOT, version, period, var.name))

            # clean up
            ncdf_file.close()
            del(weighted_data)
            del(full_cosines)
            gc.collect()

            # write output files (annual and monthly)
            filename = "{}/{}_5x5_monthly{}_from_daily_{}_{}_ts_annual.nc".format(settings.DATA_LOCATION, settings.OUTROOT, version, period, suffix) 

            if os.path.exists(filename):
                os.remove(filename)
            write_ncdf_ts(annual_times, OBS_ORDER, filename, annual = True, do_zip = True)

            filename = "{}/{}_5x5_monthly{}_from_daily_{}_{}_ts_monthly.nc".format(settings.DATA_LOCATION, settings.OUTROOT, version, period, suffix) 

            if os.path.exists(filename):
                os.remove(filename)
            write_ncdf_ts(monthly_times, OBS_ORDER, filename, monthly = True, do_zip = True)

            # clean up
            del(plot_values)
            del(plot_times)
            del(OBS_ORDER)
            gc.collect()

    # not activated at present
    pentads = False
    if pentads:
        # pentad -> annual
        OBS_ORDER = utils.make_MetVars(settings.mdi, multiplier = False)

        for v, var in enumerate(OBS_ORDER):
            print var.name


            filename = "{}/{}_1x1_pentads_from_3hrly_{}_{}_{}.nc".format(settings.DATA_LOCATION, settings.OUTROOT, var.name, period, suffix) 

            ncdf_file = ncdf.Dataset(filename,'r', format='NETCDF4')

            lat_centres = ncdf_file.variables["latitude"]
            lon_centres = ncdf_file.variables["longitude"]

            data_shape = ncdf_file.variables[var.name][:].shape

            # pentads
            mesh_lon, mesh_lat = np.meshgrid(lon_centres, lat_centres)
            cosines = np.cos(np.radians(mesh_lat))

            plot_values = np.zeros(data_shape[0])
            plot_times = []
            year = copy.deepcopy(settings.START_YEAR)

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

            plt.savefig("{}/{}_pentads_all.png".format(settings.PLOT_LOCATION, var.name))

            raw_input("check")

    return # make_timeseries

#************************************************************************
if __name__=="__main__":

    
    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--suffix', dest='suffix', action='store', default = "relax",
                        help='"relax" or "strict" completeness, default = relax')
    parser.add_argument('--doQC', dest='doQC', action='store_true', default = False,
                        help='process the QC information, default = False')
# KATE modified
    parser.add_argument('--doQC1it', dest='doQC1it', action='store_true', default = False,
                        help='process the 1st iteration QC information, default = False')
    parser.add_argument('--doQC2it', dest='doQC2it', action='store_true', default = False,
                        help='process the 2nd iteration QC information, default = False')
    parser.add_argument('--doQC3it', dest='doQC3it', action='store_true', default = False,
                        help='process the 3rd iteration QC information, default = False')
# end
    parser.add_argument('--doBC', dest='doBC', action='store_true', default = False,
                        help='process the bias corrected data, default = False')
    args = parser.parse_args()


# KATE modified
    make_timeseries(suffix = str(args.suffix), doQC = args.doQC, doQC1it = args.doQC1it, doQC2it = args.doQC2it, doQC3it = args.doQC3it, doBC = args.doBC)
    #make_timeseries(suffix = str(args.suffix), doQC = args.doQC, doBC = args.doBC)
# end

# END
# ************************************************************************
