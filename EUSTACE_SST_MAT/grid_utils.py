#!/usr/local/sci/bin/python2.7
#*****************************
#
# general utilities & classes for Python gridding.
#
#
#************************************************************************

import os
import datetime as dt
import numpy as np
import sys
import argparse
import matplotlib
import struct
import netCDF4 as ncdf


#*********************************************
class MetVar(object):
    '''
    Bare bones class for meteorological variable
    '''
    
    def __init__(self, name, long_name):
        self.name = name
        self.long_name = long_name
        

    def __str__(self):     
        return "variable: {}, long_name: {}".format(self.name, self.long_name)

    __repr__ = __str__
   
   

#*****************************************************
def read_qc_data(filename, location, fieldwidths):
    """
    Read in the QC'd data and return
    Expects fixed field format

    http://stackoverflow.com/questions/4914008/efficient-way-of-parsing-fixed-width-files-in-python


    :param str filename: filename to read
    :param str location: location of file
    :param str fieldwidths: fixed field widths to use

    :returns: data - np.array of string data
    """

    fmtstring = ''.join('%ds' % f for f in fieldwidths)
    parse = struct.Struct(fmtstring).unpack_from

    platform_data = []
    platform_meta = []
    platform_obs = []
    platform_qc = []



    with open(os.path.join(location, filename), 'r') as infile:
        try:
            for line in infile:
                fields = parse(line)
                
                # now unpack and process
                
                platform_data += [fields[: 8]]
                platform_obs += [fields[8: 8+17]]
                platform_meta += [fields[8+17: 8+17+33]]
                platform_qc += [fields[8+17+33:]]
                

        except OSError:
            sys.exit()

    


    return np.array(platform_data), \
        np.array(platform_obs), \
        np.array(platform_meta), \
        np.array(platform_qc) # read_qc_data


#*****************************************************
def process_platform_obs(raw_data):
    '''
    Extract the lats, lons and timestamps of each obs
    '''

    # need to convert from string to float/int
    lats = np.array([float(x) for x in raw_data[:,2]])
    lons = np.array([float(x) for x in raw_data[:,3]])
    year = np.array([float(x) for x in raw_data[:,4]])
    month = np.array([int(x) for x in raw_data[:,5]])
    day = np.array([int(x) for x in raw_data[:,6]])
    hour = np.array([int(x) for x in raw_data[:,7]])

    return lats, lons, year, month, day, hour # process_platform_obs

#*****************************************************
def make_index(data, delta, multiplier = 100):
    '''
    Which box do the lats/lons sit in (makes the test an equality)

    :param array data: data to be processed
    :param array delta: dimension to discretise on
    :param int multiplier: if there is a scaling factor
    
    :returns: lat_index, lon_index
    '''
    
    dummy = data / (delta * multiplier)
    index = dummy.astype(int)

    return index # make_index


#*****************************************************
def check_date(date, test, name, filename):
    '''
    Test that data is for single year/month

    :param array date: years or months array
    :param int test: value to test against
    :param str name: name of date quantity for message
    :param str filename: filename that's been processed - for message

    '''

    unique = np.unique(date)
    if (len(unique) == 1) and (unique[0] == test):
        return True
    else:
        print "Bad {} in file {}".format(name, filename)
        return False # check_date


#************************************************************************
def read_global_attributes(attr_file):
    '''
    Reads attributes file and returns a dictionary of key/values
    '''
        
    try:
        with open(attr_file,'r') as infile:        
            lines = infile.readlines()
        
    except IOError:
        print "Attributes file not found at " + attr_file
    
    
    attributes = {}
    
    for line in lines:
        split_line = line.split()
        
        attributes[split_line[0]] = " ".join(split_line[1:])    
        
    return attributes # read_global_attributes

#*****************************************************
def netcdf_write(data, lats, lons, hours, year, month, do_zip = True):
    '''
    Write the relevant fields out to a netCDF file.

    '''


    
    filename = "out_test_1x1_3hr_{}_{}.nc".format(year, month)

    # remove file
    if os.path.exists(filename):
        os.remove(filename)

    outfile = ncdf.Dataset(filename,'w', format='NETCDF4')

    time_dim = outfile.createDimension('time',data.shape[1])
    lat_dim = outfile.createDimension('lat',data.shape[2])
    lon_dim = outfile.createDimension('lon',data.shape[3])

    
    # create variables:
    nc_var = outfile.createVariable("MAT", np.dtype(int), ('time','lat','lon',), zlib = do_zip)
    nc_var.long_name = "Marine Air Temperature"
    nc_var.units = "deg C"
    nc_var.missing_value = -9999
    nc_var.valid_min = np.min(data[0, :, :, :])
    nc_var.valid_max = np.min(data[0, :, :, :])
    nc_var.standard_name = "Marine Air Temperature"
    nc_var[:] = data[0, :, :, :]


    # Global Attributes
    # from file
    attribs = read_global_attributes("attributes.txt")
    
    for attr in attribs:
        
        outfile.__setattr__(attr, attribs[attr])
 
    outfile.date_created = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d, %H:%M")
    outfile.Conventions = 'CF-1.5' 
    outfile.Metadata_Conventions = 'Unidata Dataset Discovery v1.0,CF Discrete Sampling Geometries Conventions'
    outfile.featureType = 'gridded'
    
    outfile.close()

    return

#*****************************************************
def set_MetVar_attributes(name, long_name, standard_name, units, mdi, dtype, column):
    '''
    Wrapper to set up a new MetVar object and populate some of the attibute fields

    :param str name: name for variable - ideally CF compliant
    :param str long_name: longname for variable - ideally CF compliant
    :param str standard_name: standard_name for variable - ideally CF compliant
    :param str units: units for variable - ideally CF compliant
    :param float/int mdi: missing data indicator
    :param type dtype: dtype for variable
    :param int column: which column in the ascii file corresponds to this data

    :returns MetVar new_var: new MetVar variable.
    '''  

    new_var = MetVar(name, long_name)
    new_var.units = units
    new_var.dtype = dtype
    new_var.mdi = mdi
    new_var.standard_name = standard_name
    new_var.column = column
    
    return new_var # set_MetVar_attributes
 
#*****************************************************
def make_MetVars(mdi):
 
    mat = set_MetVar_attributes("marine_air_temperature", "Marine Air Temperature", "marine air temperature", "C", mdi, np.dtype('float64'), 0)
    mat_an = set_MetVar_attributes("marine_air_temperature_anomalies", "Marine Air Temperature", "marine air temperature anomalies", "C", mdi, np.dtype('float64'), 1)

    sst = set_MetVar_attributes("sea_surface_temperature", "Sea Surface Temperature", "sea surface temperature", "C", mdi, np.dtype('float64'), 2)
    sst_an = set_MetVar_attributes("sea_surface_temperature_anomalies", "Sea Surface Temperature", "sea surface temperature anomalies", "C", mdi, np.dtype('float64'), 3)

    slp = set_MetVar_attributes("sea_level_pressure", "Sea Level Pressure", "sea level pressure", "hPa", mdi, np.dtype('float64'), 4)

    dpt = set_MetVar_attributes("dew_point_temperature", "Dew Point Temperature", "dew point temperature", "C", mdi, np.dtype('float64'), 5)
    dpt_an = set_MetVar_attributes("dew_point_temperature_anomalies", "Dew Point Temperature", "dew point temperature anomalies", "C", mdi, np.dtype('float64'), 6)

    shu = utils.set_MetVar_attributes("specific_humidity", "Specific humidity", "specific_humidity", "g/kg", temperatures.mdi, np.dtype('float64'), 7)
    shu_an = utils.set_MetVar_attributes("specific_humidity_anomalies", "Specific humidity", "specific_humidity_anomalies", "g/kg", temperatures.mdi, np.dtype('float64'), 8)
 
    vap = utils.set_MetVar_attributes("vapor_pressure", "Vapor pressure calculated w.r.t water", "water vapor pressure", "hPa", temperatures.mdi, np.dtype('float64'), 9)
    vap_an = utils.set_MetVar_attributes("vapor_pressure_anomalies", "Vapor pressure calculated w.r.t water", "water vapor pressure anomalies", "hPa", temperatures.mdi, np.dtype('float64'), 10)

    crh = utils.set_MetVar_attributes("relative_humidity", "Relative humidity", "relative humidity", "%rh", temperatures.mdi, np.dtype('float64'), 11)
    crh_an = utils.set_MetVar_attributes("relative_humidity_anomalies", "Relative humidity", "relative humidity anomalies", "%rh", temperatures.mdi, np.dtype('float64'), 12)


    cwb = utils.set_MetVar_attributes("wet_bulb_temperature", "Wet bulb temperatures", "wet bulb temperature", "C", temperatures.mdi, np.dtype('float64'), 13)
    cwb_an = utils.set_MetVar_attributes("wet_bulb_temperature_anomalies", "Wet bulb temperatures", "wet bulb temperature anomalies", "C", temperatures.mdi, np.dtype('float64'), 14)

    dpd = set_MetVar_attributes("dew_point_depression", "Dew Point Depression", "dew point depression", "C", mdi, np.dtype('float64'), 15)
    dpd_an = set_MetVar_attributes("dew_point_depression_anomalies", "Dew Point Depression", "dew point depression anomalies", "C", mdi, np.dtype('float64'), 16)

    return [mat, mat_an, sst, sst_an, slp, dpt, dpt_an, shu, shu_an, vap, vap_an, crh, crh_an, cwb, cwb_an, dpd, dpd_an]
