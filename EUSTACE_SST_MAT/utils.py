#!/usr/local/sci/bin/python2.7
#*****************************
#
# general utilities & classes for Python gridding.
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
A set of class definitions and routines to help with the gridding of HadISDH Marine

-----------------------
LIST OF MODULES
-----------------------
None

-----------------------
DATA
-----------------------
None

-----------------------
HOW TO RUN THE CODE
-----------------------
All routines to be called from external scripts.

-----------------------
OUTPUT
-----------------------
None

-----------------------
VERSION/RELEASE NOTES
-----------------------

Version 2 (26 Sep 2016) Kate Willett
---------
 
Enhancements
This can now work with the 3 QC iterations and BC options
This has a ShipOnly option in read_qc_data to pull through only ship data --ShipOnly
Bug fixed to work with ship only bias corrected data - platform_meta[:,2] rather than the QConly platform_meta[:,3]
 
Changes
 
Bug fixes
Possible bug fix in set_qc_flag_list
This had an incomplete list of QC flags for the full list and wasn't matching the QC flags up correctly.
This is now based on MDS_RWtools standard list.

Possible number of elements mistake in read_qc_data
This was causing an error where it was trying to treat 'None' as an intefer. I think it was miscounting the elements.
This is now based on MDS_RWtools standard list.

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
   
#*********************************************
class TimeVar(object):
    '''
    Bare bones class for times
    '''
    
    def __init__(self, name, long_name, units, standard_name):
        self.name = name
        self.long_name = long_name
        self.units = units
        self.standard_name = standard_name
        

    def __str__(self):     
        return "time: {}, long_name: {}, units: {}".format(self.name, self.long_name, self.units)

    __repr__ = __str__
   
  

#*****************************************************
# KATE modified - added BC options
#def set_qc_flag_list(doBC = False, doUncert = False):
def set_qc_flag_list(doBC = False, doBCtotal = False, doBChgt = False, doBCscn = False, doUncert = False):
# end 
    '''
    Set the QC flags present in the raw data

    :param bool doBC: run for bias corrected data
    :param bool doUncert: work on files with uncertainty information (not currently used)

    :returns: QC_FLAGS - np string array
    '''


# KATE modified - added BC options
#    if doBC:
    if doBC | doBCtotal | doBChgt | doBCscn:
# end
        # reduced number of QC flags.
        return np.array(["day","land","trk","date1","date2","pos","blklst","dup",\
"SSTbud","SSTclim","SSTnonorm","SSTfreez","SSTrep",\
"ATbud","ATclim","ATnonorm","ATround","ATrep",\
"DPTbud","DPTclim","DPTssat","DPTround","DPTrep","DPTrepsat"])
    else:
# KATE modified - this doesn't seem to be working and I can't quite see how the subset listed below would work without any former subsetting of the read in data
# This now uses the complete list from MDS_RWtools.py standard version
        # full list
        return np.array(["day","land","trk","date1","date2","pos","blklst","dup","POSblank1",\
                         "SSTbud","SSTclim","SSTnonorm","SSTfreez","SSTnoval","SSTnbud","SSTbbud","SSTrep","SSTblank",\
                         "ATbud","ATclim","ATnonorm","ATblank1","ATnoval","ATround","ATbbud","ATrep","ATblank2",\
                         "DPTbud","DPTclim","DPTnonorm","DPTssat","DPTnoval","DPTround","DPTbbud","DPTrep","DPTrepsat",\
                         "few","ntrk","POSblank2","POSblank3","POSblank4","POSblank5","POSblank6","POSblank7"]) # set_qc_flag_list
	
#        # full number
#        return np.array(["day","land","trk","date1","date2","pos","blklst","dup",\
#"SSTbud","SSTclim","SSTnonorm","SSTfreez","SSTrep",\
#"ATbud","ATclim","ATnonorm","ATnoval","ATround","ATrep",\
#"DPTbud","DPTclim","DPTnonorm","DPTssat","DPTnoval","DPTround","DPTrep","DPTrepsat"]) # set_qc_flag_list
# end

# RD - kept original flag array here just in case MDS_RWtools isn't used before next read
#np.array(["day","land","trk","date1","date2","pos","blklst","dup","POSblank1",\
#"SSTbud","SSTclim","SSTnonorm","SSTfreez","SSTnoval","SSTnbud","SSTbbud","SSTrep","SSTblank",\
#"ATbud","ATclim","ATnonorm","ATblank1","ATnoval","ATnbud","ATbbud","ATrep","ATblank2",\
#"DPTbud","DPTclim","DPTnonorm","DPTssat","DPTnoval","DPTnbud","DPTbbud","DPTrep","DPTrepsat",\
#"few","ntrk","DUMblank1","DUMblank2","DUMblank3","DUMblank4","DUMblank5","DUMblank6"])

#*****************************************************
# KATE modified - added BC options
#def read_qc_data(filename, location, fieldwidths, doBC = False):
def read_qc_data(filename, location, fieldwidths, doBC = False, doBCtotal = False, doBChgt = False, doBCscn = False, ShipOnly = False):
# end
    """
    Read in the QC'd data and return
    Expects fixed field format

    http://stackoverflow.com/questions/4914008/efficient-way-of-parsing-fixed-width-files-in-python


    :param str filename: filename to read
    :param str location: location of file
    :param str fieldwidths: fixed field widths to use
    :param bool doBC: run on the bias corrected data
# KATE modified - added BC options
    :param bool doBCtotal: run on the full bias corrected data
    :param bool doBChgt: run on the height only bias corrected data
    :param bool doBCscn: run on the screen only bias corrected data
# end
# KATE modified - added BC options
    :param bool ShipOnly: select only ship platform (0:5) data
# end

    :returns: data - np.array of string data
    """

    fmtstring = ''.join('%ds' % f for f in fieldwidths)
    parse = struct.Struct(fmtstring).unpack_from

    platform_data = []
    platform_meta = []
    platform_obs = []
    platform_qc = []


    with open(os.path.join(location, filename), 'r') as infile:
        for line in infile:

            try:
                if doBC:
                    # some lines might not be the correct length
                    assert len(line) == 751
                
                    fields = parse(line)
                
                    # now unpack and process
                    platform_data += [fields[: 8]]
                    dummy_obs = [fields[8: 8+18]] # used to help counting the fields
                    platform_obs += [fields[8+18: 8+18+14]] # the ???tbc fields
                    dummy_obs = [fields[8+18+14: 8+18+14+14+14+14]] # ditto
                    platform_meta += [fields[8+18+14+14+14+14: 8+18+14+14+14+14+12]]
                    platform_qc += [fields[8+18+14+14+14+14+12:]]

# KATE modified - added BC options
                elif doBCtotal:
                    # some lines might not be the correct length
                    assert len(line) == 751
                
                    fields = parse(line)
                
                    # now unpack and process
                    platform_data += [fields[: 8]]
                    dummy_obs = [fields[8: 8+18]] # used to help counting the fields
                    platform_obs += [fields[8+18: 8+18+14]] # the ???tbc fields
                    dummy_obs = [fields[8+18+14: 8+18+14+14+14+14]] # ditto
                    platform_meta += [fields[8+18+14+14+14+14: 8+18+14+14+14+14+12]] # 3rd element is PT
                    platform_qc += [fields[8+18+14+14+14+14+12:]]

                elif doBChgt:
                    # some lines might not be the correct length
                    assert len(line) == 751
                
                    fields = parse(line)
                
                    # now unpack and process
                    platform_data += [fields[: 8]]
                    dummy_obs = [fields[8: 8+18+14]] # used to help counting the fields
                    platform_obs += [fields[8+18+14: 8+18+14+14]] # the ???tbc fields
                    dummy_obs = [fields[8+18+14+14: 8+18+14+14+14+14]] # ditto
                    platform_meta += [fields[8+18+14+14+14+14: 8+18+14+14+14+14+12]] # 3rd element is PT
                    platform_qc += [fields[8+18+14+14+14+14+12:]]

                elif doBCscn:
                    # some lines might not be the correct length
                    assert len(line) == 751
                
                    fields = parse(line)
                
                    # now unpack and process
                    platform_data += [fields[: 8]]
                    dummy_obs = [fields[8: 8+18+14+14]] # used to help counting the fields
                    platform_obs += [fields[8+18+14+14: 8+18+14+14+14]] # the ???tbc fields
                    dummy_obs = [fields[8+18+14+14+14: 8+18+14+14+14+14]] # ditto
                    platform_meta += [fields[8+18+14+14+14+14: 8+18+14+14+14+14+12]] # 3rd element is PT
                    platform_qc += [fields[8+18+14+14+14+14+12:]]
# end

                else:
                    # some lines might not be the correct length
                    assert len(line) == 410
                
                    fields = parse(line)
                
                    # now unpack and process
                    platform_data += [fields[: 8]]
                    platform_obs += [fields[8: 8+17]]
# KATE modified - this seems to be wrong
                    platform_meta += [fields[8+17: 8+17+30]] # 4th element is PT
                    platform_qc += [fields[8+17+30:]]
                    #platform_meta += [fields[8+17: 8+17+20]]
                    #platform_qc += [fields[8+17+20:]]
# end
            except AssertionError:
                print "skipping line in {} - malformed data".format(filename)
                print line
                               
            except OSError:
                print "file {} missing".format(filename)
                sys.exit()

    # convert to arrays
    platform_qc = np.array(platform_qc)
    platform_obs = np.array(platform_obs)
    platform_meta = np.array(platform_meta)
    platform_data = np.array(platform_data)


# KATE modified - copied out as no longer needed for I300 run - already removed PT = 14 in make_and_full_qc.py
# SHOULD HAVE BEEN platform_meta[:,3] anyway!!! so we have accidentally removed any SIDs of 14 - there are some!!!
#    # filter PT=14
#    PT = np.array([int(x) for x in platform_meta[:,2]])
#
#    goods, = np.where(PT != 14)
#    # should no longer be needed but retained for completeness
# end

# KATE modified - if ShipOnly is set then pull out only ship data
    if ShipOnly:

        # filter PT=0:5 only
	# If its a BC run then PT is element 2 (3rd) but if its QC only then PT is element 3 (4th)
        if doBC | doBCtotal | doBChgt | doBCscn:
	    PT = np.array([int(x) for x in platform_meta[:,2]])
	else:
	    PT = np.array([int(x) for x in platform_meta[:,3]])
        
	goods, = np.where(PT <= 5)
	print("Pulling out SHIPS only ",len(goods))
        return platform_data[goods], \
            platform_obs[goods].astype(int), \
            platform_meta[goods], \
            platform_qc[goods].astype(int) # read_qc_data
	
    else:
        return platform_data, \
            platform_obs.astype(int), \
            platform_meta, \
            platform_qc.astype(int) # read_qc_data
# end    

# KATE modified - copmmented out because above loops make this redundant
#    return platform_data[goods], \
#        platform_obs[goods].astype(int), \
#        platform_meta[goods], \
#        platform_qc[goods].astype(int) # read_qc_data
# end

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

    attr_file = os.path.join(os.getcwd(), attr_file)

    try:
        with open(attr_file,'r') as infile:        
            lines = infile.readlines()
        
    except IOError:
        print "Attributes file not found at " + attr_file
        raise IOError
    
    attributes = {}
    
    for line in lines:
        split_line = line.split()
        
        attributes[split_line[0]] = " ".join(split_line[1:])    
        
    return attributes # read_global_attributes

#************************************************************************
def write_netcdf_variable(outfile, var, v, data, frequency, do_zip = True):
    '''
    Create the netcdf variable
    
    :param obj outfile: output file object
    :param obj var: variable object
    :param int v: sequence number of variable
    :param array data: data to write
    :param str frequency: frequency of input data
    :param bool do_zip: allow compression?
    '''

    nc_var = outfile.createVariable(var.name, var.dtype, ('time','latitude','longitude',), zlib = do_zip, fill_value = var.mdi)

    nc_var.long_name = var.long_name
    nc_var.units = var.units
    nc_var.missing_value = var.mdi
    nc_var.standard_name = var.standard_name
    
    if frequency == "M":
        nc_var.valid_min = np.min(data[v, :, :]) / var.multiplier
        nc_var.valid_max = np.max(data[v, :, :]) / var.multiplier
        nc_var[:] = np.ma.array([data[v, :, :]]) / var.multiplier
        
    else:
        nc_var.valid_min = np.min(data[v, :, :, :]) / var.multiplier
        nc_var.valid_max = np.max(data[v, :, :, :]) / var.multiplier
        nc_var[:] = data[v, :, :, :] / var.multiplier

    return # write_netcdf_variable

#*****************************************************
def netcdf_write(filename, data, n_grids, n_obs, variables, lats, lons, time, do_zip = True, frequency = "H", single = ""):
    '''
    Write the relevant fields out to a netCDF file.
    
    :param str filename: output filename
    :param array data: the whole data array [nvars, nhours, nlats, nlons]
    :param array n_grids: number of grid boxes/days/hours for each field from prior processing step
    :param array n_obs: number of observations for each field
    :param list variables: the variables in order to output
    :param array lats: the latitudes
    :param array lons: the longitudes
    :param array time: the times as TimeVar object
    :param bool do_zip: allow compression?
    :param str frequency: frequency of input data
    :param str single: only write a single variable if != ""
    '''

    # remove file
    if os.path.exists(filename):
        os.remove(filename)

    outfile = ncdf.Dataset(filename,'w', format='NETCDF4')

    if frequency == "M":
        time_dim = outfile.createDimension('time',1)
    elif frequency == "P":
        time_dim = outfile.createDimension('time',data.shape[1])
    elif frequency == "Y":
        time_dim = outfile.createDimension('time',data.shape[1])
    else:
        time_dim = outfile.createDimension('time',data.shape[1])

    lat_dim = outfile.createDimension('latitude',len(lats)) # as TRC of box edges given, size = # box centres to be written
    lon_dim = outfile.createDimension('longitude',len(lons))
    
    #***********
    # set up basic variables linked to dimensions
    # make time variable
    nc_var = outfile.createVariable(time.name, np.dtype('int'), ('time'), zlib = do_zip)
    nc_var.long_name = time.long_name
    nc_var.units = time.units
    nc_var.standard_name = time.standard_name
    nc_var[:] = time.data
    
    # make latitude variable
    nc_var = outfile.createVariable('latitude', np.dtype('float32'), ('latitude'), zlib = do_zip)
    nc_var.long_name = "latitude"
    nc_var.units = "degrees north"
    nc_var.standard_name = "latitude"
    nc_var[:] = lats[:] - (lats[1] - lats[0])/2.
    

    # make longitude variable
    nc_var = outfile.createVariable('longitude', np.dtype('float32'), ('longitude'), zlib = do_zip)
    nc_var.long_name = "longitude"
    nc_var.units = "degrees east"
    nc_var.standard_name = "longitude"
    nc_var[:] = lons[:] - (lons[1] - lons[0])/2.

    #***********
    # create variables:
    if single != "":
        var = single
        v = 0

        write_netcdf_variable(outfile, var, v, data, frequency, do_zip = do_zip)
        
    else: # spin through all of the variables

        for v, var in enumerate(variables):
            write_netcdf_variable(outfile, var, v, data, frequency, do_zip = do_zip)

    # write number of observations 


    nc_var = outfile.createVariable("n_grids", np.dtype('int32'), ('time','latitude','longitude',), zlib = do_zip, fill_value = -1)

    nc_var.long_name = "Number of grid boxes/days/hours going into this grid box"
    nc_var.units = "1"
    nc_var.missing_value = -1
    nc_var.standard_name = "Number of grid boxes/days/hours"
    nc_var[:] = np.ma.masked_where(n_grids <=0, n_grids)

    nc_var = outfile.createVariable("n_obs", np.dtype('int32'), ('time','latitude','longitude',), zlib = do_zip, fill_value = -1)

    nc_var.long_name = "Number of raw observations going into this grid box"
    nc_var.units = "1"
    nc_var.missing_value = -1
    nc_var.standard_name = "Number of Observations"
    nc_var[:] = np.ma.masked_where(n_obs <= 0, n_obs)

    # Global Attributes
    # from file
    attribs = read_global_attributes("attributes.dat")
    
    for attr in attribs:
        
        outfile.__setattr__(attr, attribs[attr])
 
    outfile.date_created = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d, %H:%M")
    outfile.Conventions = 'CF-1.5' 
    outfile.Metadata_Conventions = 'Unidata Dataset Discovery v1.0,CF Discrete Sampling Geometries Conventions'
    outfile.featureType = 'gridded'
    
    outfile.close()

    return # netcdf_write

#*****************************************************
def set_MetVar_attributes(name, long_name, standard_name, units, mdi, dtype, column, multiplier = False):
    '''
    Wrapper to set up a new MetVar object and populate some of the attibute fields

    :param str name: name for variable - ideally CF compliant
    :param str long_name: longname for variable - ideally CF compliant
    :param str standard_name: standard_name for variable - ideally CF compliant
    :param str units: units for variable - ideally CF compliant
    :param float/int mdi: missing data indicator
    :param type dtype: dtype for variable
    :param int column: which column in the ascii file corresponds to this data
    :param bool multiplier: add a non-unity multiplier

    :returns MetVar new_var: new MetVar variable.
    '''  

    new_var = MetVar(name, long_name)
    new_var.units = units
    new_var.dtype = dtype
    new_var.mdi = mdi
    new_var.standard_name = standard_name
    new_var.column = column

    if multiplier:
        if "anomalies" in name: # all anomalies x100
            new_var.multiplier = 100.
        else: # everything else x10
            new_var.multiplier = 10.
    else:
        new_var.multiplier = 1.
    
    return new_var # set_MetVar_attributes
 
#*****************************************************
# KATE modified - BC options
#def make_MetVars(mdi, doSST_SLP = False, multiplier = False, doBC = False):
def make_MetVars(mdi, doSST_SLP = False, multiplier = False, doBC = False, doBCtotal = False, doBChgt = False, doBCscn = False):
# end
    '''
    Set up the MetVars and return a list.  
    Had hard-coded columns for the input files.
    
    :param flt mdi: missing data indicator
    :param bool doSST_SLP: do the extra variables
    :param bool multiplier: add a non-unity multiplier
    :param bool doBC: run on bias corrected data (adjusts the columns to read in from data array)
# KATE modified - BC optiosn
    :param bool doBCtotal: run on full bias corrected data (adjusts the columns to read in from data array)
    :param bool doBChgt: run on height only bias corrected data (adjusts the columns to read in from data array)
    :param bool doBCscn: run on screen only bias corrected data (adjusts the columns to read in from data array)
# end
   
    :returns: list [mat, mat_an, dpt, dpt_an, shu, shu_an, vap, vap_an, crh, crh_an, cwb, cwb_an, dpd, dpd_an]
      if doSST_SLP:
      [mat, mat_an, sst, sst_an, slp, dpt, dpt_an, shu, shu_an, vap, vap_an, crh, crh_an, cwb, cwb_an, dpd, dpd_an]
      
    '''
    if doBC and doSST_SLP:
        raise RuntimeError("Cannot have doBC and doSST_SLP set at the same tiem")

# KATE modified - BC options
#    if doBC:
    if doBC | doBCtotal | doBChgt | doBCscn:
# end    
        mat = set_MetVar_attributes("marine_air_temperature", "Marine Air Temperature", "marine air temperature", "degrees C", mdi, np.dtype('float64'), 0, multiplier = multiplier)
        mat_an = set_MetVar_attributes("marine_air_temperature_anomalies", "Marine Air Temperature Anomalies", "marine air temperature anomalies", "degrees C", mdi, np.dtype('float64'), 1, multiplier = multiplier)

        dpt = set_MetVar_attributes("dew_point_temperature", "Dew Point Temperature", "dew point temperature", "degrees C", mdi, np.dtype('float64'), 2, multiplier = multiplier)
        dpt_an = set_MetVar_attributes("dew_point_temperature_anomalies", "Dew Point Temperature Anomalies", "dew point temperature anomalies", "degrees C", mdi, np.dtype('float64'), 3, multiplier = multiplier)

        shu = set_MetVar_attributes("specific_humidity", "Specific humidity", "specific_humidity", "g/kg", mdi, np.dtype('float64'), 4, multiplier = multiplier)
        shu_an = set_MetVar_attributes("specific_humidity_anomalies", "Specific humidity Anomalies", "specific_humidity_anomalies", "g/kg", mdi, np.dtype('float64'), 5, multiplier = multiplier)

        vap = set_MetVar_attributes("vapor_pressure", "Vapor pressure calculated w.r.t water", "water vapor pressure", "hPa", mdi, np.dtype('float64'), 6, multiplier = multiplier)
        vap_an = set_MetVar_attributes("vapor_pressure_anomalies", "Vapor pressure Anomalies calculated w.r.t water", "water vapor pressure anomalies", "hPa", mdi, np.dtype('float64'), 7, multiplier = multiplier)

        crh = set_MetVar_attributes("relative_humidity", "Relative humidity", "relative humidity", "%rh", mdi, np.dtype('float64'), 8, multiplier = multiplier)
        crh_an = set_MetVar_attributes("relative_humidity_anomalies", "Relative humidity Anomalies", "relative humidity anomalies", "%rh", mdi, np.dtype('float64'), 9, multiplier = multiplier)

        cwb = set_MetVar_attributes("wet_bulb_temperature", "Wet bulb temperatures", "wet bulb temperature", "degrees C", mdi, np.dtype('float64'), 10, multiplier = multiplier)
        cwb_an = set_MetVar_attributes("wet_bulb_temperature_anomalies", "Wet bulb temperatures Anomalies", "wet bulb temperature anomalies", "degrees C", mdi, np.dtype('float64'), 11, multiplier = multiplier)

        dpd = set_MetVar_attributes("dew_point_depression", "Dew Point Depression", "dew point depression", "degrees C", mdi, np.dtype('float64'), 12, multiplier = multiplier)
        dpd_an = set_MetVar_attributes("dew_point_depression_anomalies", "Dew Point Depression Anomalies", "dew point depression anomalies", "degrees C", mdi, np.dtype('float64'), 13, multiplier = multiplier)

    else:
        mat = set_MetVar_attributes("marine_air_temperature", "Marine Air Temperature", "marine air temperature", "degrees C", mdi, np.dtype('float64'), 0, multiplier = multiplier)
        mat_an = set_MetVar_attributes("marine_air_temperature_anomalies", "Marine Air Temperature Anomalies", "marine air temperature anomalies", "degrees C", mdi, np.dtype('float64'), 1, multiplier = multiplier)

        sst = set_MetVar_attributes("sea_surface_temperature", "Sea Surface Temperature", "sea surface temperature", "degrees C", mdi, np.dtype('float64'), 2, multiplier = multiplier)
        sst_an = set_MetVar_attributes("sea_surface_temperature_anomalies", "Sea Surface Temperature Anomalies", "sea surface temperature anomalies", "degrees C", mdi, np.dtype('float64'), 3, multiplier = multiplier)

        slp = set_MetVar_attributes("sea_level_pressure", "Sea Level Pressure", "sea level pressure", "hPa", mdi, np.dtype('float64'), 4, multiplier = multiplier)

        dpt = set_MetVar_attributes("dew_point_temperature", "Dew Point Temperature", "dew point temperature", "degrees C", mdi, np.dtype('float64'), 5, multiplier = multiplier)
        dpt_an = set_MetVar_attributes("dew_point_temperature_anomalies", "Dew Point Temperature Anomalies", "dew point temperature anomalies", "degrees C", mdi, np.dtype('float64'), 6, multiplier = multiplier)

        shu = set_MetVar_attributes("specific_humidity", "Specific humidity", "specific_humidity", "g/kg", mdi, np.dtype('float64'), 7, multiplier = multiplier)
        shu_an = set_MetVar_attributes("specific_humidity_anomalies", "Specific humidity Anomalies", "specific_humidity_anomalies", "g/kg", mdi, np.dtype('float64'), 8, multiplier = multiplier)

        vap = set_MetVar_attributes("vapor_pressure", "Vapor pressure calculated w.r.t water", "water vapor pressure", "hPa", mdi, np.dtype('float64'), 9, multiplier = multiplier)
        vap_an = set_MetVar_attributes("vapor_pressure_anomalies", "Vapor pressure Anomalies calculated w.r.t water", "water vapor pressure anomalies", "hPa", mdi, np.dtype('float64'), 10, multiplier = multiplier)

        crh = set_MetVar_attributes("relative_humidity", "Relative humidity", "relative humidity", "%rh", mdi, np.dtype('float64'), 11, multiplier = multiplier)
        crh_an = set_MetVar_attributes("relative_humidity_anomalies", "Relative humidity Anomalies", "relative humidity anomalies", "%rh", mdi, np.dtype('float64'), 12, multiplier = multiplier)

        cwb = set_MetVar_attributes("wet_bulb_temperature", "Wet bulb temperatures", "wet bulb temperature", "degrees C", mdi, np.dtype('float64'), 13, multiplier = multiplier)
        cwb_an = set_MetVar_attributes("wet_bulb_temperature_anomalies", "Wet bulb temperatures Anomalies", "wet bulb temperature anomalies", "degrees C", mdi, np.dtype('float64'), 14, multiplier = multiplier)

        dpd = set_MetVar_attributes("dew_point_depression", "Dew Point Depression", "dew point depression", "degrees C", mdi, np.dtype('float64'), 15, multiplier = multiplier)
        dpd_an = set_MetVar_attributes("dew_point_depression_anomalies", "Dew Point Depression Anomalies", "dew point depression anomalies", "degrees C", mdi, np.dtype('float64'), 16, multiplier = multiplier)

    if doSST_SLP:
        return [mat, mat_an, sst, sst_an, slp, dpt, dpt_an, shu, shu_an, vap, vap_an, crh, crh_an, cwb, cwb_an, dpd, dpd_an] # make_MetVars
    else:
        return [mat, mat_an, dpt, dpt_an, shu, shu_an, vap, vap_an, crh, crh_an, cwb, cwb_an, dpd, dpd_an] # make_MetVars


#*********************************************************
def PlotFirstField(filename, variable = "Marine Air Temperature", vmin = None,vmax = None, field = 0):
    '''
    Plot the first field of the data in the netcdf file
    - i.e. a map of the humidities in the first month
    uses iris

    :param cube cube: the input cube
    :returns: None
    '''
    
    import matplotlib.pyplot as plt
    import iris.quickplot as qplt
    import cartopy.crs as ccrs
    import iris
    
    cube = iris.load_cube(filename, variable)

    plt.clf()
    ax = plt.axes(projection=ccrs.Robinson())
    ax.gridlines() #draw_labels=True)
    ax.coastlines()
    qplt.pcolor(cube[field], cmap=plt.cm.PiYG,vmin=vmin,vmax=vmax)
    plt.show()
    
    return # PlotFirstField

#*********************************************************
# KATE modified - added BC options
#def process_qc_flags(qc_flags, these_flags, doBC = False):
def process_qc_flags(qc_flags, these_flags, doBC = False, doBCtotal = False, doBChgt = False, doBCscn = False):
# end
    '''
    :param array qc_flags: names of QC flags in column order
    :param dict these_flags: names and values of QC flags to test.
    :param bool doBC: work on the bias corrected QC flag definitions
# KATE modified - BC optiosn
    :param bool doBCtotal: run on full bias corrected data (adjusts the columns to read in from data array)
    :param bool doBChgt: run on height only bias corrected data (adjusts the columns to read in from data array)
    :param bool doBCscn: run on screen only bias corrected data (adjusts the columns to read in from data array)
# end

    Test values
    0 - pass
    1 - fail
    8 - unable to test
    9 - not run (failure further up chain?)
    '''

# KATE modified - BC options
#    QC_FLAGS = set_qc_flag_list(doBC = doBC)
    QC_FLAGS = set_qc_flag_list(doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn)
# end

    # set up a mask with every point set
    mask = np.ones((qc_flags.shape[0], len(these_flags.keys())))

    fl_loc = 0
    for flag, value in these_flags.iteritems():

        fl, = np.where(QC_FLAGS == flag)[0]

        # specified settings allowed - unset these locations
        good_locs, = np.where(qc_flags[:,fl] == value)          
        mask[good_locs, fl_loc] = 0

        fl_loc += 1

    complete_mask = np.sum(mask, axis = 1) # get sum for each obs.  If zero, then fine, if not then mask
    complete_mask[complete_mask > 0] = 1

    # RJHD 31 March 2016
    # checked against December 1973.  Have 138144 obs, of which 108988 are good and 29156 are bad.

    return complete_mask # process_qc_flags


#*********************************************************
# KATE modified - added BC options
#def day_or_night(qc_flags, doBC = False):
def day_or_night(qc_flags, doBC = False, doBCtotal = False, doBChgt = False, doBCscn = False):
# end
    '''
    Return locations of observations which are day or night
    
    :param array qc_flags: array of QC flags (0 --> 9)
    :param bool doBC: work on the bias corrected QC flag definitions
# KATE modified - BC optiosn
    :param bool doBCtotal: run on full bias corrected data (adjusts the columns to read in from data array)
    :param bool doBChgt: run on height only bias corrected data (adjusts the columns to read in from data array)
    :param bool doBCscn: run on screen only bias corrected data (adjusts the columns to read in from data array)
# end

    :returns: day_locs, night_locs - locations of day/night obs
    '''
# KATE modified - BC options
#    QC_FLAGS = set_qc_flag_list(doBC = doBC)
    QC_FLAGS = set_qc_flag_list(doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn)
# end
      
    daycol = np.where(QC_FLAGS == "day")

    day_locs = np.where(qc_flags[daycol, :] == 0)
    night_locs = np.where(qc_flags[daycol, :] == 1)

    return day_locs, night_locs # day_or_night

#*********************************************************
# KATE modified - added BC options
#def grid_1by1_cam(clean_data, raw_qc, hours_since, lat_index, lon_index, grid_hours, grid_lats, grid_lons, OBS_ORDER, mdi, doMedian = True, doBC = False):
def grid_1by1_cam(clean_data, raw_qc, hours_since, lat_index, lon_index, grid_hours, grid_lats, grid_lons, OBS_ORDER, mdi, doMedian = True, doBC = False, doBCtotal = False, doBChgt = False, doBCscn = False):
# end
    '''
    Grid using the Climate Anomaly Method on 1x1 degree for each month

    :param array clean_data: input data
    :param array hours_since: counting in hours since start of month
    :param array lat_index: discretised input latitudes
    :param array lon_index: discretised input longitudes
    :param array grid_hours: discretised hours
    :param array grid_lats: grid box corner lats
    :param array grid_lons: grid box corner lons
    :param list OBS_ORDER: list of MetVar variables
    :param float mdi: missing data indicator
    :param bool doMedian: use the median (default) instead of the mean
    :param bool doBC: work on the bias corrected QC flag definitions
# KATE modified - BC optiosn
    :param bool doBCtotal: run on full bias corrected data (adjusts the columns to read in from data array)
    :param bool doBChgt: run on height only bias corrected data (adjusts the columns to read in from data array)
    :param bool doBCscn: run on screen only bias corrected data (adjusts the columns to read in from data array)
# end
    '''

# KATE modified - BC options
#    QC_FLAGS = set_qc_flag_list(doBC = doBC)
    QC_FLAGS = set_qc_flag_list(doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn)
# end

    day_flag_loc, = np.where(QC_FLAGS == 'day')[0]

    # set up the arrays
    this_month_grid = np.ma.zeros([len(OBS_ORDER),len(grid_hours),len(grid_lats), len(grid_lons)], fill_value = mdi)
    this_month_grid.mask = np.zeros([len(OBS_ORDER),len(grid_hours),len(grid_lats), len(grid_lons)])
    this_month_obs = np.zeros([len(grid_hours),len(grid_lats), len(grid_lons)]) # number of raw observations
    this_month_time = np.zeros([len(grid_hours),len(grid_lats), len(grid_lons)]) # day or night

    mesh_lats, mesh_lons = np.meshgrid(grid_lats, grid_lons)

    cols = np.array([obs.column for obs in OBS_ORDER])

    for lt, glat in enumerate(grid_lats):
        locs_lat, = np.where(lat_index == lt)
        
        if len(locs_lat) > 0: # only continue if there are data to process
            
            for ln, glon in enumerate(grid_lons):
                locs_lon, = np.where(lon_index == ln)
                locs_ll = np.intersect1d(locs_lat, locs_lon) # get the combination
                
                if len(locs_ll) > 0: # only continue if there are data to process
                    
                    for gh, timestamp in enumerate(grid_hours):                        
                        locs_h, = np.where(hours_since == timestamp)

                        locs = np.intersect1d(locs_h, locs_ll)

                        if len(locs) > 0: # only continue if there are data to process
                      
                            if doMedian:
                                average = np.ma.median(clean_data[locs, :][:, cols], axis = 0)
                            else:
                                average = np.ma.mean(clean_data[locs, :][:, cols], axis = 0)

                            day_flags = raw_qc[locs, :][:, day_flag_loc]                            

                            # if there is data then copy into final array
                            if len(average.compressed()) > 0:
                                this_month_grid[:, gh, lt, ln] = average
                                this_month_grid.mask[:, gh, lt, ln] = False # unset the mask

                                # number of raw observations going into this grid box time stamp
                                this_month_obs[gh, lt, ln] = np.ma.compress_rows(clean_data[locs, :][:, cols]).shape[0]

                                # restricting to day or night then set the flag and it's allowed value (Extended_IMMA.py line 668 - #0=night, 1=day)
                                if len(np.unique(day_flags)) == 1:
                                    this_month_time[gh, lt, ln] = np.unique(day_flags)
                                else: # if a mix then force to be a day (KW in discussion with RD, 6 April 2016)
                                    this_month_time[gh, lt, ln] = 1

                            # ensure that mask is set otherwise
                            else:
                                this_month_grid.mask[:, gh, lt, ln] = True

                        # ensure that mask is set otherwise
                        else:
                            this_month_grid.mask[:, gh, lt, ln] = True # ensure mask is set
                else:
                    this_month_grid.mask[:, :, lt, ln] = True # ensure mask is set
        else:
            this_month_grid.mask[:, :, lt, :] = True # ensure mask is set

    return this_month_grid, this_month_obs, this_month_time # grid_1by1_cam

#*********************************************************
def grid_5by5(data, n_obs, grid_lats, grid_lons, doMedian = True, daily = True):
    '''
    Make a coarser grid and go from daily to monthly

    As passing in only one month at a time, just average over all timestamps

    :param array data: input 1x1 data (daily)
    :param array n_obs: number of raw observations going into each daily 1x1 grid box
    :param array grid_lats: input 1degree lats (box edges)
    :param array grid_lons: input 1degree lons (box edges)
    :param bool doMedian: use the median (default) instead of the mean
    :param bool daily: input data is daily or not (i.e. monthly)
    
    :returns: new_data, new_lats, new_lons - updated to 5x5
    '''

    # assert the shapes are correct - blc at -89, -179, trc at 90, 180
    #    Using upper right corner of box as index, and have nothing at -90, -180
    assert len(grid_lats) == 180
    assert len(grid_lons) == 360

    if daily:
        N_OBS = 0.3 * data.shape[1]  # 30% of days in month
    else:
        N_OBS = 1 # out of possible 25 1x1 monthly fields

    DELTA = 5
    # box edges
    new_lats = np.arange(-90+DELTA, 90+DELTA, DELTA)
    new_lons = np.arange(-180+DELTA, 180+DELTA, DELTA)

    new_data = np.ma.zeros((data.shape[0], len(new_lats), len(new_lons)))
    new_data.mask = np.ones((data.shape[0], len(new_lats), len(new_lons)))
    new_data.fill_value = data.fill_value
    
    n_grids_array = np.ma.zeros((len(new_lats), len(new_lons)))
    n_grids_array.mask = np.zeros((len(new_lats), len(new_lons)))
    n_obs_array = np.ma.zeros((len(new_lats), len(new_lons)))
    n_obs_array.mask = np.zeros((len(new_lats), len(new_lons)))

    for lt, lat in enumerate(np.arange(0, len(grid_lats), DELTA) + DELTA):
        for ln, lon in enumerate(np.arange(0, len(grid_lons), DELTA) + DELTA):
           
            # difficult to do over both space (and time) axes all at once
            for var in range(data.shape[0]):
                if doMedian:
                    if daily:
                        new_data[var, lt, ln] = np.ma.median(data[var, :, lat-DELTA:lat, lon-DELTA:lon])
                    else:
                        new_data[var, lt, ln] = np.ma.median(data[var, lat-DELTA:lat, lon-DELTA:lon])
                else:
                    if daily:
                        new_data[var, lt, ln] = np.ma.mean(data[var, :, lat-DELTA:lat, lon-DELTA:lon])
                    else:
                        new_data[var, lt, ln] = np.ma.mean(data[var, lat-DELTA:lat, lon-DELTA:lon])

                if daily:
                    n_grids = np.ma.count(data[var, :, lat-DELTA:lat, lon-DELTA:lon])
                else:
                    n_grids = np.ma.count(data[var, lat-DELTA:lat, lon-DELTA:lon])

                n_grids_array[lt, ln] = n_grids

                if n_grids < N_OBS:
                    new_data.mask[var, lt, ln] = True
                 
                if daily:
                    n_obs_array[lt, ln] = np.ma.sum(n_obs[:, lat-DELTA:lat, lon-DELTA:lon])
                else:
                    n_obs_array[lt, ln] = np.ma.sum(n_obs[lat-DELTA:lat, lon-DELTA:lon])

    return new_data, n_grids_array, n_obs_array, new_lats, new_lons # grid_5by5

#*********************************************************
def days_in_year(year):
    '''
    Calculate the number of days in year

    :param int year: year
    :returns: days
    '''

    start = dt.datetime(year, 1, 1, 0, 0)
    end = dt.datetime(year+1, 1, 1, 0, 0)
   
    diff = end-start

    return diff.days # days_in_year

#*********************************************************
def day_of_year(year, month):
    '''
    Calculate the day of the year the 1st of a given month is.

    :param int year: year
    :param int month: month
    :returns: days
    '''

    start = dt.datetime(year, 1, 1, 0, 0)
    end = dt.datetime(year, month, 1, 0, 0)
   
    diff = end-start

    return diff.days # day_of_year

#*******************************************************
def bn_median(masked_array, axis=None):
    """
    https://github.com/astropy/ccdproc/blob/122cdbd5713140174f057eaa8fdb6f9ce03312df/docs/ccdproc/bottleneck_example.rst
    Perform fast median on masked array

    Parameters

    masked_array : `numpy.ma.masked_array`
        Array of which to find the median.

    axis : int, optional
        Axis along which to perform the median. Default is to find the median of
        the flattened array.
    """
    import bottleneck as bn
    data = masked_array.filled(fill_value=np.NaN)
    med = bn.nanmedian(data, axis=axis)
    # construct a masked array result, setting the mask from any NaN entries
    return np.ma.array(med, mask=np.isnan(med)) # bn_median


#*******************************************************
def boxes_with_n_obs(outfile, all_obs, data, N_YEARS_PRESENT):
    """
    Output text file showing number of grid boxes derived from 1, 2, 3.... raw observations
    and the actual number in the climatologies passing completeness
    
    :param file outfile: the output file
    :param array all_obs: all n_obs values for each pentad
    :param array data: data array for each pentad.
    :param str N_YEARS_PRESENT: number of years required to calculate a climatology
    """

    outfile.write("Below shows the number of grid boxes in the climatology file which \n would be derived from 1, 2, 3 .. >15 raw hourly obs in the absence of any completeness \n checks.  The second number in each pair shows the number of grid boxes which are \n actually present as a result of the cut on the number of years present ({} years). \n\n To be read into spreadsheet or as a word table.".format(N_YEARS_PRESENT))

    outfile.write("max number of boxes = {}\n\n".format(all_obs.shape[1] * all_obs.shape[2]))

    outfile.write("{}, {},{}, {},{}, {},{}, {},{}, {},{}, {},{}, {},{}, {},{}, {},{}, {},{}, {},{}, {},{}, {},{}, {},{}, {},{}, {},{}\n\n".format("pent", 1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13,14,14,15,15,">15",">15"))

    # spin through each pentad
    for p in range(all_obs.shape[0]):
        
        # get the number of observations
        t_obs = all_obs[p]
        
        outstring = "{}, ".format(p)
        
        for value in range(1,16):

            locs = np.ma.where(t_obs == value)

            outstring = "{} {},{},".format(outstring, len(locs[0]), len(data[p][locs].compressed()))

        # and do greater than 15
        locs = np.ma.where(t_obs > 15)
        outstring = "{} {},{}\n".format(outstring, len(locs[0]), len(data[p][locs].compressed()))
        
        outfile.write(outstring)

    outfile.close()

    return # boxes_with_n_obs

#*******************************************************
def ma_append(orig, extra, axis = 0):
    '''
    A replacement for np.ma.array which is only available in v1.9 (we've 1.8.2)

    :param array orig: original data
    :param array extra: data to be appended
    :param int axis: axis along which to do the appending

    :returns: new - masked array
    '''    
    new = np.append(orig.data, extra.data, axis = axis)
    new = np.ma.array(new)

    new.mask = np.append(orig.mask, extra.mask, axis = axis) 

    return new # ma_append

# END
# ************************************************************************
