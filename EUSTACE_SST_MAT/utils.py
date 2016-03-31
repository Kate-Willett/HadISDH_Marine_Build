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

QC_FLAGS = np.array(["day","land","trk","date1","date2","pos","blklst","dup","POSblank1",\
"SSTbud","SSTclim","SSTnonorm","SSTfreez","SSTnoval","SSTnbud","SSTbbud","SSTrep","SSTblank",\
"ATbud","ATclim","ATnonorm","ATblank1","ATnoval","ATnbud","ATbbud","ATrep","ATblank2",\
"DPTbud","DPTclim","DPTnonorm","DPTssat","DPTnoval","DPTnbud","DPTbbud","DPTrep","DPTrepsat",\
"few","ntrk","DUMblank1","DUMblank2","DUMblank3","DUMblank4","DUMblank5","DUMblank6"])

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
        for line in infile:

            try:
                # some lines might not be the correct length
                assert len(line) == 410
                
                fields = parse(line)
                
                # now unpack and process
                
                platform_data += [fields[: 8]]
                platform_obs += [fields[8: 8+17]]
                platform_meta += [fields[8+17: 8+17+30]]
                platform_qc += [fields[8+17+30:]]

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


    # filter PT=14
    PT = np.array([int(x) for x in platform_meta[:,3]])
    goods, = np.where(PT != 14)


    return platform_data[goods], \
        platform_obs[goods].astype(int), \
        platform_meta[goods], \
        platform_qc[goods].astype(int) # read_qc_data


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
    :param int v: sequency number of variable
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
def netcdf_write(filename, data, variables, lats, lons, time, do_zip = True, frequency = "H", single = ""):
    '''
    Write the relevant fields out to a netCDF file.
    
    :param str filename: output filename
    :param array data: the whole data array [nvars, nhours, nlats, nlons]
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
def make_MetVars(mdi, doSST_SLP = False, multiplier = False):
    '''
    Set up the MetVars and return a list.  
    Had hard-coded columns for the input files.
    
    :param flt mdi: missing data indicator
    :param bool doSST_SLP: do the extra variables
    :param bool multiplier: add a non-unity multiplier
   
    :returns: list [mat, mat_an, dpt, dpt_an, shu, shu_an, vap, vap_an, crh, crh_an, cwb, cwb_an, dpd, dpd_an]
      if doSST_SLP:
      [mat, mat_an, sst, sst_an, slp, dpt, dpt_an, shu, shu_an, vap, vap_an, crh, crh_an, cwb, cwb_an, dpd, dpd_an]
    '''

 
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
def process_qc_flags(qc_flags, these_flags):
    '''
    :param array qc_flags: names of QC flags in column order
    :param dict these_flags: names and values of QC flags to test.

    Test values
    0 - pass
    1 - fail
    8 - unable to test
    9 - not run (failure further up chain?)
    '''

    mask = np.ones((qc_flags.shape[0], len(these_flags.keys())))

    fl_loc = 0
    for flag, value in these_flags.iteritems():

        fl, = np.where(QC_FLAGS == flag)[0]

        # settings of 0 or 9 allowed - unset these.
        good_locs, = np.where(qc_flags[:,fl] == value)          
        mask[good_locs, fl_loc] = 0

        fl_loc += 1

    complete_mask = np.sum(mask, axis = 1) # get sum for each obs.  If zero, then fine, if not then mask
    complete_mask[complete_mask > 0] = 1

    return complete_mask # process_qc_flags


#*********************************************************
def day_or_night(qc_flags):
    '''
    Return locations of observations which are day or night
    
    :param array qc_flags: array of QC flags (0 --> 9)

    :returns: day_locs, night_locs - locations of day/night obs
    '''
       
    daycol = np.where(QC_FLAGS == "day")

    day_locs = np.where(qc_flags[daycol, :] == 0)
    night_locs = np.where(qc_flags[daycol, :] == 1)

    return day_locs, night_locs # day_or_night

#*********************************************************
def grid_5by5(data, grid_lats, grid_lons, doMedian = True):
    '''
    Make a coarser grid

    :param array data: input 1x1 data
    :param array grid_lats: input 1degree lats (box edges)
    :param array grid_lons: input 1degree lons (box edges)
    :param bool doMedian: use the median (default) instead of the mean
    
    :returns: new_data, new_llats, new_lons - updated to 5x5
    '''

    # assert the shapes are correct - blc at -89, -179, trc at 90, 180
    #    Using upper right corner of box as index, and have nothing at -90, -180
    assert len(grid_lats) == 180
    assert len(grid_lons) == 360

    N_OBS = 1 # out of possible 25
    DELTA = 5
    # box edges
    new_lats = np.arange(-90+DELTA, 90+DELTA, DELTA)
    new_lons = np.arange(-180+DELTA, 180+DELTA, DELTA)

    new_data = np.ma.zeros((data.shape[0], len(new_lats), len(new_lons)))
    new_data.mask = np.ones((data.shape[0], len(new_lats), len(new_lons)))
    new_data.fill_value = data.fill_value
    
    for lt, lat in enumerate(np.arange(0, len(grid_lats), DELTA) + 1):
        for ln, lon in enumerate(np.arange(0, len(grid_lons), DELTA) + 1):
           
            for var in range(data.shape[0]):
                if doMedian:
                    new_data[var, lt-1, ln-1] = np.ma.median(data[var, lat-DELTA:lat, lon-DELTA:lon])
                else:
                    new_data[var, lt-1, ln-1] = np.ma.mean(data[var, lat-DELTA:lat, lon-DELTA:lon])

                n_obs = np.ma.count(data[var, lat-DELTA:lat, lon-DELTA:lon])

                if n_obs < N_OBS:
                    new_data.mask[var, lt-1, ln-1] = True

    return new_data, new_lats, new_lons # grid_5by5

#*********************************************************
def grid_1by1_cam(clean_data, hours_since, lat_index, lon_index, grid_hours, grid_lats, grid_lons, OBS_ORDER, mdi, doMedian = True):
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
    '''


    # set up the array
    this_month_grid = np.ma.zeros([len(OBS_ORDER),len(grid_hours),len(grid_lats), len(grid_lons)], fill_value = mdi)
    this_month_grid.mask = np.ones([len(OBS_ORDER),len(grid_hours),len(grid_lats), len(grid_lons)])

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
                                this_month_grid[:, gh, lt, ln] = np.ma.median(clean_data[locs, :][:, cols], axis = 0)
                            else:
                                this_month_grid[:, gh, lt, ln] = np.ma.mean(clean_data[locs, :][:, cols], axis = 0)

                            this_month_grid.mask[:, gh, lt, ln] = False # unset the mask

#                        if timestamp >= 21: break

#                        raw_input("stop hr {}".format(timestamp))
#                raw_input("stop lon{}".format(glon))
#        raw_input("stop lat {}".format(glat))

    return this_month_grid # grid_1by1_cam

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

# END
# ************************************************************************
