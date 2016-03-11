'''
Suite of functions to extend and work with IMMA data
'''

import qc
import math
import numpy as np
from datetime import datetime
import spherical_geometry as sph
import qc_new_track_check as tc
import CalcHums # KW a new package with all of the calculations for humidity in
# KW Added for debugging
import pdb # pdb.set_trace() or c

def get_threshold_multiplier(total_nobs, nob_limits, multiplier_values):

    '''
    Find the highest value of i such that total_nobs is greater 
    than nob_limits[i] and return multiplier_values[i]
    
    :param total_nobs: total number of neighbour observations
    :param nob_limits: list containing the limiting numbers of observations in 
                       ascending order first element must be zero
    :param multiplier_values: list containing the multiplier values associated.
    :type total_nobs: integer
    :type nob_limits: integer
    :type multiplier_values: float
    :return: the multiplier value
    :rtype: float
    '''

    assert len(nob_limits) == len(multiplier_values), \
    "length of input lists are different"
    assert min(multiplier_values) > 0, \
    "multiplier value less than zero"
    assert min(nob_limits) == 0, \
    "nob_limit of less than zero given"
    assert nob_limits[0] == 0, \
    "lowest nob_limit not equal to zero"

    if len(nob_limits) > 1:
        for i in range(1, len(nob_limits)):
            assert nob_limits[i] > nob_limits[i-1], \
            "nob_limits not in ascending order"
    
    multiplier = -1
    if total_nobs == 0:
        multiplier = 4.0
        
    for i in range(0, len(nob_limits)):
        if total_nobs > nob_limits[i]:
            multiplier = multiplier_values[i] 

    assert multiplier > 0, "output multiplier less than or equal to zero "

    return multiplier

class QC_filter:
    '''
    A simple QC filter that can have specific tests added to it, 
    which are then used to filter lists of MarineReports
    '''
    def __init__(self):
        self.filter = []
    
    def add_qc_filter(self, qc_type, specific_flag, qc_status):
        '''
        Add a QC test to a QC filter
        
        :param qc_type: the general class of QC test e.g SST, AT, POS
        :param specific_flag: the name of the QC flag to be tested.
        :param qc_status: the value the specific_flag should have
        :type qc_type: string
        :type specific_flag: string
        :type qc_status: integer
        '''
        self.filter.append([qc_type, specific_flag, qc_status])

    def test_report(self, rep):
        '''
        Find out if a particular MarineReport passes the QC filter
        
        :param rep: the MarineReport to be tested
        :type rep: MarineReport
        :return: 0 for pass 1 for fail
        :rtype: integer
        '''
        result = 0 #pass
        for filt in self.filter:
            if rep.get_qc(filt[0], filt[1]) != filt[2]:
                result = 1 #fail
        return result
        
    def split_reports(self, reps):
        '''
        Split a list of MarineReports into those that pass and those that fail 
        the QC filter.
        
        :param reps: the list of MarineReports to be filtered
        :type reps: list of MarineReports
        :return: two lists of MarineReports, those that pass and those that fail
        :rtype: list of MarineReports
        '''
        passes = Deck()
        fails = Deck()
        
        nobs = len(reps)
        
        for i in range(0, nobs):

            rep = reps.pop(0)
            
            if self.test_report(rep) == 0:
                passes.append(rep)
            else:
                fails.append(rep)

        return passes, fails
        
class QC_Status:

    '''
    A class to hold, set and retrieve QC flags
    '''

    def __init__(self):
        
        self.qc = {}
      
    def set_qc(self, qc_type, specific_flag, set_value):
        '''
        Set a particular QC flag
        
        :param qc_type: the general QC area e.g. SST, MAT...
        :param specific_flag: the name of the flag to be set e.g. buddy_check, repeated_value
        :param set_value: the value which is to be given to the flag
        :type qc_type: string
        :type specific_flag: string
        :type set_value: integer in 0-9
        
        The specified flag in the general QC area of qc_type is set to the given value. This 
        should be a reasonably flexible system to which new QC flags can be easily added. The 
        qc_type must be one of the standard ones (POS, SST, AT, AST, HUM, PRE) or previously 
        defined using new_qc_type.
        '''
        assert set_value in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], \
        "value not in 0-9"+str(set_value)

        self.qc[qc_type + specific_flag] = set_value

    def get_qc(self, qc_type, specific_flag):
        '''
        Get the value of a particular QC flag
        
        :param qc_type: the general QC area e.g. SST, MAT..
        :param specific_flag: the name of the flag whose value is to be returned e.g. buddy_check, repeated_value
        :type qc_type: string
        :type specific_flag: string
        :return: the value of the flag, or 9 if the flag is not set.
        :rtype: integer
        
        Returns the value of a specific_flag or 9 if the specific_flag is not set. Will fail if 
        asked to return QC flags for a qc_type that is not one of the standard ones 
        (POS, SST, AT, AST, HUM, PRE) or which has not been previously defined using new_qc_type.
        '''
    
        if qc_type + specific_flag in self.qc:
            return self.qc[qc_type + specific_flag]
        else:
            return 9
        
class ClimVariable:
    '''
    A simple class for defining a climate variable which is a variable with a climatology 
    and, consequently, an anomaly.
    '''
    def __init__(self, clim):
        self.clim = clim

    def getclim(self):
        '''
        Get the climatological average from the climate variable
        '''
        return self.clim

# KW added a class for containing and dealing with climatological standard deviations
class StdevVariable:
    '''
    A simple class for defining a stdev variable which is a variable with a stdev 
    '''
    def __init__(self, stdev):
        self.stdev = stdev

    def getstdev(self):
        '''
        Get the climatological stdev from the climate variable
        '''
        return self.stdev

class MarineReport:

    '''
    A class for holding and working with marine reports. The core of the report is a set of data 
    which are taken from an IMMA record used to initialise the class. The report also has an extendible 
    set of QC flags, climate variables and a dictionary for adding new variables that might be needed.
    '''
# KW Modified to contain the extra squillions of variables for humidity and humidity related QC
# May remove some later if they are not useful
    def __init__(self, imma_rec):

        self.data = {}
        for k in imma_rec.data:
            self.data[k] = imma_rec.data[k]
# KW Does the following line mean that it overwrites for each loop of k?
# Does this have to be initialised for each self.data[]???
	    self.qc = QC_Status()
        self.climate_variables = {}
# KW Added a new thing called stdev_variables to store the climatological stdev for that ob in the rep (not very efficient!)
        self.stdev_variables = {}	
# KW Notes that this may mean that nothing is actually in the reps.ext - all vars in reps.data?
        self.ext = {}
        
        self.calculate_dt()
        self.calculate_dsi_vsi()
       
# KW Added a routine to add .data[varname] spaces for the derived humidity variables q, rh, e, tw and dpd
    def setvar(self, spare_vars):
	   ''' 
	   A routine that reads in a list of parameter names and 
	   sets up blank .data[key] placeholders for them.
	   This was designed for the later calculation of humidity
	   variables from T(AT) and Td(DPT)
	   '''
	   for k in spare_vars:
	       self.data[k] = None
		   
    def calculate_dsi_vsi(self):

        ds_convert = [0, 45, 90, 135, 180, 225, 270, 315, 360, None]
     
        self.ext['dsi'] = None
        if self.data['DS'] != None:
            self.ext['dsi'] = ds_convert[self.data['DS']]

        self.ext['vsi'] = None
        if self.data['VS'] != None:
            if self.data['YR'] >= 1968:
                self.ext['vsi'] = self.data['VS'] * 5.0 - 2.0
            else:
                self.ext['vsi'] = self.data['VS'] * 3.0 - 1.0
            if self.data['VS'] == 0:
                self.ext['vsi'] = 0.0
        
        pass

    def reset_ext(self):
        self.ext = {}
        self.calculate_dsi_vsi()

    def calculate_dt(self):
        '''
        Used to set the internal julian day time in the marine report. This might need to be 
        updated if any of the time variables are changed.
        '''
        mlen = qc.month_lengths(self.data['YR'])
        if (self.data['HR'] != None and 
            self.data['DY'] != None and 
            self.data['DY'] > 0 and 
            self.data['DY'] <= mlen[self.data['MO']-1]):
            rounded_hour = int(math.floor(self.data['HR']))
            rounded_minute = int(math.floor(60 * 
                                            (self.data['HR']-rounded_hour)))
            self.dt = datetime(self.data['YR'], 
                               self.data['MO'], 
                               int(self.data['DY']), 
                               rounded_hour, 
                               rounded_minute)
        else:
            self.dt = None

    def __sub__(self, other):
        '''
        Subtracting one :class:`.MarineReport` from another will yield the speed, distance, course and 
        the time difference between the two reports.
        
        Usage: speed, distance, course, timediff = report_a - report_b
        '''
        distance = sph.sphere_distance( self.getvar('LAT'),  self.getvar('LON'),
                                       other.getvar('LAT'), other.getvar('LON'))

        timediff = qc.time_difference(other.getvar('YR'), other.getvar('MO'), 
                                      other.getvar('DY'), other.getvar('HR'),
                                       self.getvar('YR'),  self.getvar('MO'), 
                                       self.getvar('DY'),  self.getvar('HR'))
        speed = None
        if timediff != 0:
            speed = distance/timediff
        else:
            timediff = 0.0
            speed = distance

        course = sph.course_between_points(other.getvar('LAT'), 
                                           other.getvar('LON'), 
                                            self.getvar('LAT'),  
                                            self.getvar('LON'))

        return speed, distance, course, timediff

    def __eq__(self, other):
        '''
        Two marine reports are equal if their ID is equal and they were taken at the same time
        '''
        if self.getvar('ID') == other.getvar('ID') and self.dt == other.dt:
            return True
        else:
            return False
    
    def __gt__(self, other):
        '''
        One marine report is greater than another if its ID is higher in an alphabetical ordering. 
        For reports with the same ID, the later report is the greater.
        '''
        if self.getvar('ID') > other.getvar('ID'):
            return True
        if (self.getvar('ID') == other.getvar('ID') and 
            self.dt != None and 
            other.dt != None and 
            self.dt > other.dt):
            return True
        else:
            return False

    def __ge__(self, other):
        if self.getvar('ID') > other.getvar('ID'):
            return True
        if (self.getvar('ID') == other.getvar('ID') and 
            self.dt >= other.dt):
            return True
        else:
            return False
    
    def __le__(self, other):
        if self.getvar('ID') < other.getvar('ID'):
            return True
        if (self.getvar('ID') == other.getvar('ID') and 
            self.dt <= other.dt):
            return True
        else:
            return False
     
    def add_climate_variable(self, name, clim):
        '''
        Add a climate variable to a marine report
        
        :param name: the name of the climate variable
        :param clim: the climatological average of the climate variable
        :type name: string
        :type clim: float
        '''
        self.climate_variables[name] = ClimVariable(clim)
	#print(self.climate_variables[name].getclim())

# KW added function to read in stdev to stdev_variables (like climate_variables)
    def add_stdev_variable(self, name, stdev):
        '''
        Add a standard deviation stdev variable to a marine report
        
        :param name: the name of the stdev variable
        :param clim: the climatological stdev of the climate variable
        :type name: string
        :type clim: float
        '''
        self.stdev_variables[name] = StdevVariable(stdev)
	#print(self.climate_variables[name].getclim())

    def getnorm(self, varname):
        '''
        Retrieve the climatological average for a particular climate variable
        
        :param varname: the name of the climate variable for which you want the climatological average
        :return: the climatological average (if the climate variable exists), None otherwise.
        :rtpye: float
        '''
        if varname in self.climate_variables:
            return self.climate_variables[varname].getclim()
        else:
            return None

# KW Added getstdev to pull out the stdev from the rep (like getnorm)
    def getstdev(self, varname):
        '''
        Retrieve the climatological stdev for a particular climate variable
        
        :param varname: the name of the climate variable for which you want the climatological stdev
        :return: the climatological stdev (if the climate variable exists), None otherwise.
        :rtpye: float
        '''
        if varname in self.stdev_variables:
            return self.stdev_variables[varname].getstdev()
        else:
            return None

    def getanom(self, varname):
        '''
        Retrieve the anomaly for a particular climate variable
        
        :param varname: the name of the climate variable for which you want the anomaly
        :type varname: string
        :return: the anomaly (if the climate variable exists), None otherwise.
        :rtpye: float
        '''        
        if varname in self.climate_variables:
            clim = self.climate_variables[varname].getclim()
            if self.data[varname] != None and clim != None:
                return self.data[varname]-clim
            else:
                return None
        else:
            return None
    
    def getext(self, varname):
        '''
        Function to get a particular variable from the extended data

        :param varname: variable name to be retrieved from the extended data
        :type varname: string
        :return: the named variable
        :rtype: depends on the variable
        '''
        assert varname in self.ext, "unknown extended variable name "+varname
        return self.ext[varname]

    def setext(self, varname, varvalue):
        '''
        Set a particular variable in the extended data

        :param varname: variable name to be set in the extended data
        :type varname: string
        '''
        self.ext[varname] = varvalue
    
    def getvar(self, varname):
        '''
        Get a variable which is either in the data or extended data. Both data and extended data 
        will be queried and the function fails if the varname is not found in either one.
        
        :param varname: variable name to be retrieved
        :type varname: string
        :return: the named variable from either the data or extended data
        :rtype: depends on the variable
        '''
        assert (varname in self.data or 
                varname in self.ext), "unknown variable name "+varname
        if varname in self.data:
            return self.data[varname]
        else:
            return self.ext[varname]

    def set_qc(self, qc_type, specific_flag, set_value):
        '''
        Set a particular QC flag
        
        :param qc_type: the general QC area e.g. SST, MAT...
        :param specific_flag: the name of the flag to be set e.g. buddy_check, repeated_value
        :param set_value: the value which is to be given to the flag
        :type qc_type: string
        :type specific_flag: string
        :type set_value: integer in 0-9
        
        The specified flag in the general QC area of qc_type is set to the given value. This 
        should be a reasonably flexible system to which new QC flags can be easily added. The 
        qc_type must be one of the standard ones (POS, SST, AT, AST, HUM, PRE) or previously 
        defined using new_qc_type.
        '''
        self.qc.set_qc(qc_type, specific_flag, set_value)
    
    def get_qc(self, qc_type, specific_flag):
        '''
        Get the value of a particular QC flag
        
        :param qc_type: the general QC area e.g. SST, MAT..
        :param specific_flag: the name of the flag whose value is to be returned e.g. buddy_check, repeated_value
        :type qc_type: string
        :type specific_flag: string
        :return: the value of the flag, or 9 if the flag is not set.
        :rtype: integer
        
        Returns the value of a specific_flag or 9 if the specific_flag is not set. Will fail if 
        asked to return QC flags for a qc_type that is not one of the standard ones 
        (POS, SST, AT, AST, HUM, PRE) or which has not been previously defined using new_qc_type.
        '''
# KW The self.qc is of class QC_Status so the self.qc.get_qc is the routine specified in QC_Status
# (above).
        return self.qc.get_qc(qc_type, specific_flag)
   
    def printvar(self, var):
        '''Print a variable substituting -32768 for Nones'''
        if var in self.data:
            return int(pvar(self.data[var], -32768, 1.0))
        else:
            return int(pvar(-32768, -32768, 1.0))

    def printsim(self):
        '''Print the WMO pub47 field'''
        if 'SIM' in self.data:
            if self.data['SIM'] == None:
                return 'Missing'
            else:
                return self.data['SIM']
        else:
            return 'None'

    def print_report(self):
        '''
        A simple (ha ha) routine to print out the marine report in old-fashioned fixed-width ascii style.
        '''
# KW Modify this to output humidity variables and humidity related QC flags 
# KW Quite possibly most efficient to calculate q, RH, e, Tw, DPD here for output
# QC and buddy only on Td (first version at least)
# One issue is that in order to get anomalies in the same framework we need to
# add the humidity variables to self.data. I'm not sure whether this needs setting up 
# initially or whether they can be added now. We would read in the climatologies initially
# in make_and_full_qc.py so may have to set them up initially.
# I've now created a MarineReport.setvar routine to read in extra blank vars which is done
# at make_and_full_qc.py       
        day = int(pvar(self.data['DY'],  -32768,   1))
        hur = int(pvar(self.data['HR'],  -32768, 100))

# KW added code to call humidity calculation function (import CalcHums) and create a
# derived ob for q, rh, e, tw and dpd

        mat     = int(pvar(self.data['AT'],     -32768,  10))
        matanom = int(pvar(self.getanom('AT'),  -32768,  100))
        sst     = int(pvar(self.data['SST'],    -32768,  10))
        sstanom = int(pvar(self.getanom('SST'), -32768,  100))
        slp     = int(pvar(self.data['SLP'],    -32768,  10))
# Added vars for humidity variables and anomalies (anoms set to 0 for now until we sort out clims)
# For now I'm just going to use climatological SLP from ERA-Interim
# for all calculations - consistent with HadISDH.land (except that uses 20CR).
# Later I could choose to use reported SLP but if it doesn't exist or has failed qc then 
# call use climatological SLP which will have been read in at make_and_full_qc.py.
# If one of the other required variables does not exist then value is set to None.
# It may be quicker to build this into make_and_full_qc.py and apply simultaneously to all rep in reps 
# rather than individually???
# The calculations check whether to calculate relative to ice or water - so need AT as well as D
# The order in which these are calculated is important because they build on each other

        slpclim = self.climate_variables['SLP'].getclim()
#	print(slpclim)
#        slpclim = 1013 # KW temporary rather than read in file
        self.data['VAP'] = CalcHums.vap(self.data['DPT'],slpclim,self.data['AT'])
        self.data['SHU'] = CalcHums.shu(self.data['VAP'],slpclim)
        self.data['CRH'] = CalcHums.rh(self.data['VAP'],slpclim,self.data['AT'])
        self.data['CWB'] = CalcHums.wb(self.data['VAP'],self.data['DPT'],slpclim,self.data['AT'])
        self.data['DPD'] = CalcHums.dpd(self.data['DPT'],self.data['AT'])

        dpt     = int(pvar(self.data['DPT'],    -32768,  10))
        dptanom = int(pvar(self.getanom('DPT'), -32768,  100))
        shu     = int(pvar(self.data['SHU'],    -32768,  10))
        shuanom  = int(pvar(self.getanom('SHU'), -32768,  100))
        vap     = int(pvar(self.data['VAP'],    -32768,  10))
        vapanom  = int(pvar(self.getanom('VAP'), -32768,  100))
        crh     = int(pvar(self.data['CRH'],    -32768,  10))
        crhanom  = int(pvar(self.getanom('CRH'), -32768,  100))
        cwb     = int(pvar(self.data['CWB'],    -32768,  10))
        cwbanom  = int(pvar(self.getanom('CWB'), -32768,  100))
        dpd     = int(pvar(self.data['DPD'],    -32768,  10))
        dpdanom  = int(pvar(self.getanom('DPD'), -32768,  100))

# KW Notes DS = ship course and VS = ship speed - not sure what units.
        dsvs = 9999
        if self.data['DS'] != None and self.data['VS'] != None:
            dsvs = (self.data['DS']*100+self.data['VS'])

        lon = round(self.data['LON']*100, 0)
        if lon > 18000:
            lon = lon-36000

        shipid = self.data['ID']
        if shipid == None:
            shipid = '         '

# KW Added an extra {:d} on to qc_block because the DPT QC requires an extra two tests over AT
        qc_block = "{:d}{:d}{:d}{:d}{:d}{:d}{:d}{:d}{:d} "
        qc_end = "{:d}{:d}{:d}{:d}{:d}{:d}{:d}{:d}\n"
        #qc_end = "{:d}{:d}{:d}{:d}{:d}{:d}{:d}{:d}"
        
        repout = "{:9.9} ".format(shipid)
        repout = repout + "{:8.8}".format(self.data['UID'])
        repout = repout + "{:8d}".format(int(round(self.data['LAT']*100, 0)))
        repout = repout + "{:8d}".format(int(lon))
        repout = repout + "{:8d}".format(self.data['YR'])
        repout = repout + "{:8d}".format(self.data['MO'])
        repout = repout + "{:8d}".format(day)
        repout = repout + "{:8d}".format(hur)
        
        repout = repout + "{:8d}".format(mat)
        repout = repout + "{:8d}".format(matanom)
        repout = repout + "{:8d}".format(sst)
        repout = repout + "{:8d}".format(sstanom)
        repout = repout + "{:8d}".format(slp)
# KW The humidity variables
        repout = repout + "{:8d}".format(dpt)
        repout = repout + "{:8d}".format(dptanom)
        repout = repout + "{:8d}".format(shu)
        repout = repout + "{:8d}".format(shuanom)
        repout = repout + "{:8d}".format(vap)
        repout = repout + "{:8d}".format(vapanom)
        repout = repout + "{:8d}".format(crh)
        repout = repout + "{:8d}".format(crhanom)
        repout = repout + "{:8d}".format(cwb)
        repout = repout + "{:8d}".format(cwbanom)
        repout = repout + "{:8d}".format(dpd)
        repout = repout + "{:8d}".format(dpdanom)
        
        repout = repout + "{:8d}".format(dsvs)
        
        repout = repout + "{:8d}".format(self.data['DCK'])
        repout = repout + "{:8d}".format(self.data['SID'])
        repout = repout + "{:8d}".format(self.printvar('PT')) # seems to be present more than II
#PT: 0=US Navy/unknown - usually ship, 1=merchant ship/foreign military, 2=ocean station vessel off station (or unknown loc), 3=ocean station vessel on station, 4=lightship, 5=ship, 6=moored buiy, 7=drifting buoy, 8=ice buoy, 9=ice station, 10=oceanographic station, 11=MBT (bathythermograph), 12=XBT (bathythermograph), 13=Coastal-Marine Automated Network (C-MAN), 14=other coastal/island station, 15=fixed ocean platoform, 16=tide guage, 17=hi res CTD, 18=profiling float, 19=undulating oceanographic recorder, 10=auonomous pinneped bathythermograph (seal?),  21=glider
        repout = repout + "{:8d}".format(self.printvar('SI'))
        repout = repout + " {:8.8}".format(self.printsim())

# KW More output from the metadata - really for later humidity bias adjustment and uncertainty
# II: 0=unknown, 1=ship/ocean station vessel/ice station, 2=generic (SHIP/BUOY/RIGG/PLAT), 3=buoy (WMO 5 digit number), 4=buoy (other e.g. Argos or national), 5=Coastal-marine Automated Network (C-MAN), 6=station, 7=oceanographic platform/cruise number, 8=fishing vessel, 9=national ship, 10=early ship 
        repout = repout +  "{:4d}".format(int(pvar(self.data['II'],    -99,  1)))  #  ID Indicator
        repout = repout +  "{:3d}".format(int(pvar(self.data['IT'],    -9,  1)))  # AT Indicator 
        repout = repout +  "{:3d}".format(int(pvar(self.data['DPTI'],    -9,  1)))  # DPT Indicator
        repout = repout +  "{:3d}".format(int(pvar(self.data['WBTI'],    -9,  1)))  # WBT Indicator 
        repout = repout +  "{:8d}".format(int(pvar(self.data['WBT'],    -32768,  10)))  # WBT 
        repout = repout +  "{:3d}".format(int(pvar(self.data['DI'],    -9,  1)))  # Wind Direction Indicator 
        repout = repout +  "{:8d}".format(int(pvar(self.data['D'],    -32768,  1)))  # Wind Direction 
        repout = repout +  "{:3d}".format(int(pvar(self.data['WI'],    -9,  1)))  # Wind Speed Indicator 
        repout = repout +  "{:8d}".format(int(pvar(self.data['W'],    -32768,  10)))  # Wind Speed
        repout = repout +  "{:3d}".format(int(pvar(self.data['VI'],    -9,  1)))  # Visibility Indicator 
        repout = repout +  "{:8d}".format(int(pvar(self.data['VV'],    -32768,  1)))  # Visibility
	 
        repout = repout +  "{:4d}".format(int(pvar(self.data['DUPS'],    -99,  1)))  # Duplicate status (fine if <=2)
        repout = repout +  "{:3.3}".format(self.data['COR'])  # Country of residence
        repout = repout +  "{:4.4}".format(self.data['TOB'])  # Type of barometer
        repout = repout +  "{:4.4}".format(self.data['TOT'])  # Type of thermometer
        repout = repout +  "{:3.3}".format(self.data['EOT'])  # Exposure of thermometer
        repout = repout +  "{:2.2}".format(self.data['TOH'])  # Type of hygrometer
        repout = repout +  "{:3.3}".format(self.data['EOH'])  # Exposure of hygrometer
        repout = repout +  "{:5d}".format(int(pvar(self.data['LOV'],    -999,  1)))  # Length of vessel        
	repout = repout +  "{:5d}".format(int(pvar(self.data['HOP'],    -999,  1)))  # Height of vis obs platform
        repout = repout +  "{:5d}".format(int(pvar(self.data['HOT'],    -999,  1)))  # Height of AT sensor
        repout = repout +  "{:5d}".format(int(pvar(self.data['HOB'],    -999,  1)))  # Height of barometer
        repout = repout +  "{:5d}".format(int(pvar(self.data['HOA'],    -999,  1)))  # Height of anemometer
        repout = repout +  "{:7d}".format(int(pvar(self.data['SMF'],    -9999,  1)))  # Source Metadata file

        repout = repout + " "

        repout = repout + qc_block.format(self.qc.get_qc('POS','day'), #0=night, 1=day
                                          self.qc.get_qc('POS','land'), 
                                          self.qc.get_qc('POS','trk'), 
                                          self.qc.get_qc('POS','date'), 
                                          self.qc.get_qc('POS','date'), 
                                          self.qc.get_qc('POS','pos'), 
                                          self.qc.get_qc('POS','blklst'), 
                                          self.qc.get_qc('POS','dup'),
# KW Added a '9' to fill the now extra element of qc_block
					  9
                                          )
        repout = repout + qc_block.format(self.qc.get_qc('SST','bud'),    # 0 = pass, 1 = fail, 8 = not run due to filering, 9 = not set?
                                          self.qc.get_qc('SST','clim'),   # 0 = pass, 1 = fail, 8 = not run dur to filtering, 9 = not set?
                                          self.qc.get_qc('SST','nonorm'), 
                                          self.qc.get_qc('SST','freez'), 
                                          self.qc.get_qc('SST','noval'), 
# KW I can't see where nbud is set - is it just 0 if not set?
                                          self.qc.get_qc('SST', 'nbud'), 
                                          self.qc.get_qc('SST', 'bbud'), # 0 = pass, 1-9 = fail, 9 = not set?
                                          self.qc.get_qc('SST', 'rep'), 
# KW Added a '9' to fill the now extra element of qc_block
					  9
                                          )
        repout = repout + qc_block.format(self.qc.get_qc('AT','bud'),   # 0 = pass, 1 = fail, 8 = not run due to filering, 9 = not set?
                                          self.qc.get_qc('AT','clim'),  # 0 = pass, 1 = fail, 8 = not run due to filering, 9 = not set?
                                          self.qc.get_qc('AT','nonorm'), 
                                          9,
                                          self.qc.get_qc('AT','noval'),
# KW I can't see where nbud is set - is it just 0 if not set?
                                          self.qc.get_qc('AT',  'nbud'), 
                                          self.qc.get_qc('AT',  'bbud'), # 0 = pass, 1-9 = fail, 9 = not set?
                                          self.qc.get_qc('AT',  'rep'), # 0 = pass, 1 = fail, 9 = not set?
# KW Added a '9' to fill the now extra element of qc_block
					  9
                                          )
# KW Added a new block for DPT
        repout = repout + qc_block.format(self.qc.get_qc('DPT','bud'), # KW qc flag for buddy_check 0=pass, 1=fail, 7=fails filter, 8= 9=not set
                                          self.qc.get_qc('DPT','clim'), # KW qc flag for outliers from climatology 0=pass, 1=fail, 9=not set
                                          self.qc.get_qc('DPT','nonorm'), # KW qc flag for whether clim exists - may change to eranorm (0=obs, 1=era)
                                          self.qc.get_qc('DPT','ssat'), # KW NEW qc flag for supersaturation 0=pass, 1=td>t, 9=not set
                                          self.qc.get_qc('DPT','noval'), # KW qc flag for whether the variable is present in the ob - all present due to pre-filter
# KW I can't see where nbud is set - is it just 0 if not set?
                                          self.qc.get_qc('DPT',  'nbud'), # KW qc flag for ??? if a buddy check can be performed?
                                          self.qc.get_qc('DPT',  'bbud'), # KW qc flag for the bayesian buddy check - NOT USED 0 = pass, 1-9 = fail, 9 = not set?
                                          self.qc.get_qc('DPT',  'rep'), # KW qc flag for if this value is part of a repeat string (more than 70% of 21+obs are identical)
					  self.qc.get_qc('DPT',  'repsat')  # KW NEWqc flag for persistent saturation
                                          )
# KW Cut this out for now to save space - its a spare QC block (which I've used above???)
#        repout = repout + qc_block.format(9, 9, 9, 9, 9, 9, 9, 9, 9)
        repout = repout + qc_end.format(self.qc.get_qc('POS', 'few'), 
                                        self.qc.get_qc('POS', 'ntrk'), 
                                        9, 9, 9, 9, 9, 9 
                                        )

        #repout = repout +" "+ str(self.dt)
        
        return repout

def pvar(var, mdi, scale):
    '''
    Convert a variable to a rounded integer
    
    :param var: the variable to be scaled and rounded
    :param mdi: the value to set the variable to if missing or None
    :param scale: the factor by which to scale the number before rounding
    :type var: float
    :type mde: integer
    :type scale: integer
    '''
    if var == None:
        ret = mdi
    else:
        ret = round(var * scale)
    return ret

class Voyage:
    '''
    Class for handling lists of MarineReports as coherent sets of measurements 
    from a single ship. Includes track check and repeated value checks which 
    operate on "voyages".
    '''
    def __init__(self):
        self.reps = []
    
    def __len__(self):
        return len(self.reps)

    def rep_feed(self):
        '''
        Function for iterating over the MarineReports in a Voyage
        '''
        for rep in self.reps:
            yield rep

    def getrep(self, position):
        '''
        Get the report for a particular location in the list
        
        :param position: the position the desired report occupies in the list
        :type position: integer
        '''
        return self.reps[position]

    def last_rep(self):
        '''
        Get the last report in the Voyage
        
        :return: last ExtendedMarineReport in the Voyage
        :rtype: ExtendedMarineReport
        '''
        nreps = len(self.reps)
        return self.reps[nreps-1]
    
    def getvar(self, position, varname):
        '''
        Get a particular variable from a particular report
        
        :param position: the position the desired report occupies in the list
        :param varname: the variable name to recover
        :type position: integer
        :type varname: string
        '''
        return self.reps[position].getvar(varname)

    def set_qc(self, position, qc_type, specific_flag, set_value):
        '''
        Set the QC flag of a report at a specified position to a specified value
        
        :param position: the position the desired report occupies in the list
        :param qc_type: the general QC area e.g. SST, MAT...
        :param specific_flag: the name of the flag to be set e.g. buddy_check, repeated_value
        :param set_value: the value which is to be given to the flag
        :type position: integer
        :type qc_type: string
        :type specific_flag: string
        :type set_value: integer in 0-9
        '''
        self.reps[position].set_qc(qc_type, specific_flag, set_value)
        
    def add_report(self, rep):
        '''
        Add a MarineReport to the Voyage.
        
        :param rep: MarineReport to be added to the end of the Voyage
        :type rep: MareineReport
        '''
        self.reps.append(rep)
        
        if len(self.reps) > 1:
            i = len(self.reps)
            shpspd, shpdis, shpdir, tdiff = self.reps[i-1] - self.reps[i-2]
            self.reps[i-1].setext('speed', shpspd)
            self.reps[i-1].setext('course', shpdir)
            self.reps[i-1].setext('distance', shpdis)
            self.reps[i-1].setext('time_diff', tdiff)
        else:
            self.reps[0].setext('speed', None)
            self.reps[0].setext('course', None)
            self.reps[0].setext('distance', None)
            self.reps[0].setext('time_diff', None)

    def sort(self):
        '''
        Sorts the reports into time order
        '''
        self.reps.sort()
        #then recalculate times, speeds etc.
        if len(self.reps) > 1:
            for i in range(1, len(self.reps)):
                shpspd, shpdis, shpdir, tdiff = self.reps[i] - self.reps[i-1]
                self.reps[i].setext('speed', shpspd)
                self.reps[i].setext('course', shpdir)
                self.reps[i].setext('distance', shpdis)
                self.reps[i].setext('time_diff', tdiff)

    def get_speed(self):
        """
        Return a list containing the speeds of all the reports as 
        estimated from the positions of consecutive reports
        
        :return: list of speeds in km/hr
        :rtype: float
        """
        spd = []
        for i in range(0, len(self.reps)):
            spd.append(self.reps[i].getext('speed'))
            
        return spd

    def meansp(self):
        """
        Calculate the mean speed of the voyage based on speeds 
        estimated from the positions of consecutive reports.
        
        :return: mean voyage speed
        :rtype: float
        """
        spd = self.get_speed()

        if len(spd) > 1:
            amean = np.mean(spd[1:])
        else:
            amean = None

        return amean

    def calc_alternate_speeds(self):
        """
        The speeds and courses can also be calculated using alternating reports
        """
        for i in range(0, len(self.reps)):
            self.reps[i].setext('alt_speed', None)
            self.reps[i].setext('alt_course', None)
            self.reps[i].setext('alt_distance', None)
            self.reps[i].setext('alt_time_diff', None)

        if len(self.reps) > 2:
            for i in range(1, len(self.reps)-1):
                shpspd, shpdis, shpdir, tdiff = self.reps[i+1] - self.reps[i-1]
                self.reps[i].setext('alt_speed', shpspd)
                self.reps[i].setext('alt_course', shpdir)
                self.reps[i].setext('alt_distance', shpdis)
                self.reps[i].setext('alt_time_diff', tdiff)

    def find_repeated_values(self, threshold=0.7, intype='SST'):
        """
        Find cases where more than a given proportion of SSTs have the same value
        
        :param threshold: the maximum fraction of observations that can have a given value
        :param intype: either 'SST' or 'MAT' to find repeated SSTs or MATs
        :type threshold: float
        :type intype: string
        
        This method goes through a voyage and finds any cases where more than a threshold fraction of 
        the observations have the same SST or NMAT value.
# KW Ok to just do this on SST and or NMAT and then apply results to humidity - if screwy for those, it will be 
# for humidity too

# KW Added a component to also perform checks on persistence of 100% rh while going through the voyage.
        While going through the voyage repeated strings of 100 %rh (AT == DPT) are noted. If a string
	extends beyond two days/48 hrs in time then all values are set to fail the repsat qc flag.
        """

# KW Modified to include DPT

        assert threshold >= 0.0 and threshold <= 1.0
# KW Added DPT
        assert intype in ['SST', 'AT', 'DPT']

#initialise
        for rep in self.reps:
            rep.set_qc(intype, 'rep', 0)

        valcount = {}
        allcount = 0
# KW Added a satcount list for keeping locs of persisting strings of 100%Rh
        satcount = []	

        for i, rep in enumerate(self.reps):
            if rep.getvar(intype) != None:
                allcount += 1
                if str(rep.getvar(intype)) in valcount:
                    valcount[str(rep.getvar(intype))].append(i)
                else:
                    valcount[str(rep.getvar(intype))]  = [i]
#**********************************************************************************************
# KW Added the repsat flag check for persistent strings of 100%rh beyond two days - for DPT only
                if (intype == 'DPT'):
		    self.reps[i].set_qc(intype, 'repsat', 0)
		    if ((qc.value_check(rep.getvar('AT')) == 0) & (rep.data['DPT'] == rep.data['AT'])):
                        # If there is a saturation ob (AT == DPT) then begin or append to a group of DPT values
		        #print('Found a sat ',i,rep.getvar('DPT'),rep.getvar('AT'))
			satcount.append(i) # a locator for the reps with 100% RH
                    elif ((qc.value_check(rep.getvar('AT')) == 0) & (rep.data['DPT'] != rep.data['AT']) & (len(satcount) > 4)):
#		        print('Found the end of a long stretch of sats ',i,len(satcount))
		        # KW If there is no saturation event but a significant satcount object has been created then we need to either delete it (too shor) or set repsat qc vals (>=48hrs)
			# KW Test the duration of the satcount event
                        shpspd, shpdis, shpdir, tdiff = self.reps[satcount[len(satcount)-1]] - self.reps[satcount[0]]
			#print('Time Difference: ',tdiff)
			if (tdiff >= 48): # Making the assumption that time difference is in hours! IT IS!
#			    print("A long one! ",tdiff)
			    # KW flag all these values as repsat = 1 and then reset satcount
			    for loc in satcount:
                                self.reps[loc].set_qc(intype, 'repsat', 1)			        
			    satcount = []
			# If its too short then just reset and carry on
			else:
			    satcount = []    
		    else:
		        # KW set repsat to 0 (pass) and double check that the satcount object is empty ready for the next string
			#print('End of sats')
			satcount = []	

# Add a catch if at end of Voyage there is a 100%rh string longer than 4 obs
        if (len(satcount) > 4):
            #print('Found the end of a long stretch of sats at end of voyage',i,len(satcount))
	    # KW If there is no saturation event but a significant satcount object has been created then we need to either delete it (too shor) or set repsat qc vals (>=48hrs)
	    # KW Test the duration of the satcount event
            shpspd, shpdis, shpdir, tdiff = self.reps[satcount[len(satcount)-1]] - self.reps[satcount[0]]
	    #print('Time Difference: ',tdiff)
	    if (tdiff >= 48): # Making the assumption that time difference is in hours! 
	        # KW flag all these values as repsat = 1 and then reset satcount
	        for loc in satcount:
                    self.reps[loc].set_qc(intype, 'repsat', 1)			        
#************************************************************************************************
		
        if allcount > 20:
            for key in valcount:
                if float(len(valcount[key]))/float(allcount) > threshold:
                    for i in valcount[key]:
                        self.reps[i].set_qc(intype, 'rep', 1)
                else:
                    for i in valcount[key]:
                        self.reps[i].set_qc(intype, 'rep', 0)
                        
        return 

    def predict_next_point(self, timediff):
        """
        The latitude and longitude of the next point are estimated based on 
        an extrapolation of the great circle drawn between the previous two 
        points
        
        :param timediff: predict the latitude and longitude after this timediff has elapsed.
        :type timediff: float
        """
        assert timediff >= 0
        nreps = len(self.reps)
        
        assert nreps > 0, "Need at least one report in the voyage to predict"
       
        if nreps == 1:
            return self.reps[0].getvar('LAT'), self.reps[0].getvar('LON')

        if abs(self.reps[nreps-1].getvar('time_diff')) < 0.00001:
            return self.reps[nreps-1].getvar('LAT'), self.reps[nreps-1].getvar('LON')

        """take last-but-one and last point. Calculate a speed and 
        great circle course from them."""
        course = self.reps[nreps-1].getvar('course')
        distance = (self.reps[nreps-1].getvar('speed') * 
                    (self.reps[nreps-1].getvar('time_diff')+timediff))

        lat1 = self.reps[nreps-2].getvar('LAT')
        lon1 = self.reps[nreps-2].getvar('LON')
     
        lat, lon = sph.lat_lon_from_course_and_distance(lat1, lon1, course, distance)

        return lat, lon

    def distr1(self):
        '''
        calculate what the distance is between the projected position (based on the reported 
        speed and heading at the current and previous time steps) and the actual position. The 
        observations are taken in time order.

        :return: list of distances from estimated positions
        :rtype: list of floats

        This takes the speed and direction reported by the ship and projects it forwards half a 
        time step, it then projects it forwards another half time step using the speed and 
        direction for the next report, to which the projected location 
        is then compared. The distances between the projected and actual locations is returned
        '''
        
        km_to_nm = 0.539957
        
        nobs = len(self)
    
        distance_from_est_location = [None]
    
        for i in range(1, nobs):
            
            if (self.getvar(i,   'vsi') != None and 
                self.getvar(i-1, 'vsi') != None and
                self.getvar(i,   'dsi') != None and 
                self.getvar(i-1, 'dsi') != None and 
                self.getvar(i,   'time_diff') != None):
    
    #get increment from initial position
                lat1, lon1 = tc.increment_position(self.getvar(i-1, 'LAT'), 
                                                   self.getvar(i-1, 'LON'), 
                                                   self.getvar(i-1, 'vsi')/km_to_nm, 
                                                   self.getvar(i-1, 'dsi'), 
                                                   self.getvar(i,   'time_diff'))
    
                lat2, lon2 = tc.increment_position(self.getvar(i, 'LAT'), 
                                                   self.getvar(i, 'LON'), 
                                                   self.getvar(i, 'vsi')/km_to_nm, 
                                                   self.getvar(i, 'dsi'), 
                                                   self.getvar(i, 'time_diff'))
    #apply increments to the lat and lon at i-1            
                alatx = self.getvar(i-1, 'LAT') + lat1 + lat2
                alonx = self.getvar(i-1, 'LON') + lon1 + lon2
    
    #calculate distance between calculated position and the second reported position
                discrepancy = sph.sphere_distance(self.getvar(i, 'LAT'),
                                                  self.getvar(i, 'LON'),
                                                  alatx, alonx)
    
                distance_from_est_location.append(discrepancy)
    
            else:
    #in the absence of reported speed and direction set to None
                distance_from_est_location.append(None)
     
        return distance_from_est_location

    def distr2(self):
        '''
        calculate what the 
        distance is between the projected position (based on the reported speed and 
        heading at the current and 
        previous time steps) and the actual position. The calculation proceeds from the 
        final, later observation to the 
        first (in contrast to distr1 which runs in time order)

        :return: list of distances from estimated positions
        :rtype: list of floats
        
        This takes the speed and direction reported by the ship and projects it forwards half a time step, it then projects 
        it forwards another half time step using the speed and direction for the next report, to which the projected location 
        is then compared. The distances between the projeted and actual locations is returned
        '''

        km_to_nm = 0.539957
        
        nobs = len(self)
        
        distance_from_est_location = [None]
        
        for i in range(nobs-1, 0, -1):
            
            if (self.getvar(i,   'vsi') != None and 
                self.getvar(i-1, 'vsi') != None and
                self.getvar(i,   'dsi') != None and 
                self.getvar(i-1, 'dsi') != None and
                self.getvar(i,   'time_diff') != None):
    
    #get increment from initial position - backwards in time 
    #means reversing the direction by 180 degrees
                lat1, lon1 = tc.increment_position(self.getvar(i, 'LAT'), 
                                                   self.getvar(i, 'LON'), 
                                                   self.getvar(i, 'vsi') / km_to_nm, 
                                                   self.getvar(i, 'dsi') - 180.,
                                                   self.getvar(i, 'time_diff'))
                                                
                lat2, lon2 = tc.increment_position(self.getvar(i-1, 'LAT'), 
                                                   self.getvar(i-1, 'LON'), 
                                                   self.getvar(i-1, 'vsi') / km_to_nm, 
                                                   self.getvar(i-1, 'dsi') - 180.,
                                                   self.getvar(i,   'time_diff'))
    
    #apply increments to the lat and lon at i-1            
                alatx = self.getvar(i, 'LAT') + lat1 + lat2
                alonx = self.getvar(i, 'LON') + lon1 + lon2
    
    #calculate distance between calculated position and the second reported position
                discrepancy = sph.sphere_distance(self.getvar(i-1, 'LAT'), 
                                                  self.getvar(i-1, 'LON'), 
                                                  alatx, alonx)
                distance_from_est_location.append(discrepancy)

            else:
    #in the absence of reported speed and direction set to None
                distance_from_est_location.append(None)
    
    #that fancy bit at the end reverses the array  
        return distance_from_est_location[::-1]

    def midpt(self):
        '''
        interpolate between alternate reports and compare the 
        interpolated location to the actual location. e.g. take difference between 
        reports 2 and 4 and interpolate to get an estimate for the position at the time 
        of report 3. Then compare the estimated and actual positions at the time of 
        report 3.

        :return: list of distances from estimated positions in km
        :rtype: list of floats
        
        The calculation linearly interpolates the latitudes and longitudes (allowing for 
        wrapping around the dateline and so on).
        '''    

        nobs = len(self)

        midpoint_discrepancies = [None]

        for i in range(1, nobs-1):

            t0 = self.getvar(i,   'time_diff')
            t1 = self.getvar(i+1, 'time_diff')

            if (t0 != None and t1 != None):
                if t0 + t1 != 0:
                    fraction_of_time_diff = t0 / (t0 + t1)
                else:
                    fraction_of_time_diff = 0.0
            else:
                fraction_of_time_diff = 0.0

            if fraction_of_time_diff > 1.0:
                print fraction_of_time_diff,t0,t1

            estimated_lat_at_midpt, estimated_lon_at_midpt =\
            sph.intermediate_point(self.getvar(i-1, 'LAT'),self.getvar(i-1, 'LON'),
                                   self.getvar(i+1, 'LAT'),self.getvar(i+1, 'LON'),
                                   fraction_of_time_diff)

            discrepancy = sph.sphere_distance(self.getvar(i, 'LAT'), 
                                              self.getvar(i, 'LON'),
                                              estimated_lat_at_midpt,
                                              estimated_lon_at_midpt)

            midpoint_discrepancies.append(discrepancy)

        midpoint_discrepancies.append(None)

        return midpoint_discrepancies

    def track_check(self):
        
        '''
        Perform one pass of the track check
       
        This is an implementation of the MDS track check code 
        which was originally written in the 1990s. I don't know why this piece of 
        historic trivia so exercises my mind, but it does: the 1990s! I wish my code 
        would last so long.
        '''
        
        km_to_nm = 0.539957
        nobs = len(self)

    #no obs in, no qc outcomes out
        if nobs == 0:
            return

    #Generic ids get a free pass on the track check
        if (qc.id_is_generic(self.getvar(0, 'ID'), self.getvar(0, 'YR')) or 
            self.getvar(0, 'PT') == 15 or 
            self.getvar(0, 'PT') == 16):
            nobs = len(self)
            for i in range(0, nobs):
                self.set_qc(i, 'POS', 'trk', 0)
            return

    #fewer than three obs - set the fewsome flag
    #deck 720 gets a pass prior to 1891 see Carella, Kent, Berry 2015 Appendix A3
        if nobs < 3 and not(self.getvar(0, 'DCK') == 720 and self.getvar(0 ,'YR') < 1891):
            nobs = len(self)
            for i in range(0, nobs):
                self.set_qc(i, 'POS', 'few', 1)
            return

    #work out speeds and distances between alternating points
        self.calc_alternate_speeds()

    #what are the mean and mode speeds?
        mean_speed = self.meansp()
        modal_speed = tc.modesp(self.get_speed())
    #set speed limits based on modal speed
        amax, amaxx, amin = tc.set_speed_limits(modal_speed)

    #compare reported speeds and positions if we have them
        forward_diff_from_estimated  = self.distr1()
        reverse_diff_from_estimated  = self.distr2()
        midpoint_diff_from_estimated =  self.midpt()

    #do QC
        self.set_qc(0, 'POS', 'trk', 0)
        self.set_qc(0, 'POS', 'few', 0)

        for i in range(1, nobs-1):

            thisqc_a = 0
            thisqc_b = 0
    
    #together these cover the speeds calculate from point i        
            if   (self.getvar(i, 'speed')       > amax and 
                  self.getvar(i-1 ,'alt_speed') > amax):
                thisqc_a += 1.00
            elif (self.getvar(i+1, 'speed')     > amax and 
                  self.getvar(i+1, 'alt_speed') > amax):
                thisqc_a += 2.00
            elif (self.getvar(i, 'speed')       > amax and 
                  self.getvar(i+1, 'speed')     > amax):
                thisqc_a += 3.00 
    
    # Quality-control by examining the distance 
    #between the calculated and reported second position.
            thisqc_b += tc.check_distance_from_estimate(self.getvar(i ,  'vsi'), 
                                                        self.getvar(i-1, 'vsi'), 
                                                        self.getvar(i,   'time_diff'), 
                                                        forward_diff_from_estimated[i],
                                                        reverse_diff_from_estimated[i])
    #Check for continuity of direction                              
            thisqc_b += tc.direction_continuity(self.getvar(i,   'dsi'), 
                                                self.getvar(i-1, 'dsi'), 
                                                self.getvar(i,   'course'))
    #Check for continuity of speed.                                 
            thisqc_b += tc.speed_continuity(self.getvar(i,   'vsi'), 
                                            self.getvar(i-1, 'vsi'), 
                                            self.getvar(i,   'speed'))
    
    #check for speeds in excess of 40.00 knots
            if self.getvar(i, 'speed') > 40.00/km_to_nm:
                thisqc_b += 10.0
    
    #make the final decision
            if (midpoint_diff_from_estimated[i] > 150.0/km_to_nm and 
                thisqc_a > 0 and 
                thisqc_b > 0):
                self.set_qc(i, 'POS', 'trk', 1)
                self.set_qc(i, 'POS', 'few', 0)
            else:
                self.set_qc(i, 'POS', 'trk', 0)
                self.set_qc(i, 'POS', 'few', 0)

        self.set_qc(nobs-1, 'POS', 'trk', 0)
        self.set_qc(nobs-1, 'POS', 'few', 0)

class Gridpt:
    '''
    class used in buddy check which identifies the grid box occupied by 
    an observation on the 1x1xpentad qc grid the class is hashable so that 
    all observations from the same 1x1xpentad grid box can be indexed consistently.
    '''

    def __init__(self, lat, lon, year, month=None, day=None):
        '''
        Make a :class:`.Gridpt` object from lat, lon, year, month and day
        
        :param lat: latitude of the observation
        :param lon: longitude of observation
        :param year: year of the observation
        :param month: month of the observation
        :param day: day of the observation
        :type lat: float
        :type lon: float
        :type year: integer
        :type month: integer
        :type day: integer
        '''
        self.lat = lat
        self.lon = lon
        
        self.year = year
        self.month = month
        self.day = day
        
        if month == None:
            self.ptd = year
        else:
            self.ptd = qc.which_pentad(month, day)

        self.xindex = qc.lon_to_xindex(lon)
        self.yindex = qc.lat_to_yindex(lat)
        
        self.latitude_approx = 89.5 - self.yindex
        self.longitude_approx = -179.5 + self.xindex

        self.idstring = '%(lat)04d%(lon)04d%(ptd)04d' % {"lat": self.yindex, 
                                                         "lon": self.xindex, 
                                                         "ptd": self.ptd }
     
    def __hash__(self):
#make class hashable by defining hash and eq methods  
        hash = self.yindex * 10000*10000 + self.xindex*10000 + self.ptd 
        return hash
    
    def __eq__(self, other):
        result = False
        if (self.yindex * 10000*10000 + self.xindex*10000 + self.ptd == 
            other.yindex * 10000*10000 + other.xindex*10000 + other.ptd):
            result = True
        return result
    
    def get_neighbours(self, xspan, yspan, pspan):

        '''
        For an instance of the :class:`.Gridpt` class, find and return all neighbours 
        within +- xspan/cos(lat) of longitude +- yspan of latitude and +- pspan of pentads
        
        :param xspan: search span in longitude, equivalent to xspan degrees *at the equator*
        :param yspan: search span in latitude.
        :param pspan: search span in pentads
        :type xspan: integer
        :type yspan: integer
        :type pspan: integer
        :return: list of neighbouring grid points within the search area
        :rtype: :class:`.Gridpt`
        '''

        radcon = 3.1415928/180.
        
        latitude_approx = 89.5 - self.yindex
        longitude_approx = -179.5 + self.xindex
        
        full_xspan = int(xspan / math.cos(latitude_approx * radcon))
               
        neighbours = []
        
        for xpt in range(-1*full_xspan, full_xspan+1):
            for ypt in range(-1*yspan, yspan+1):
                for ppt in range(-1*pspan, pspan+1):
                    lat = latitude_approx + ypt
                    lon = longitude_approx + xpt
                    pen = self.ptd + ppt
                    if pen <= 0:
                        pen = 73+pen
                    if pen > 73:
                        pen = pen-73
                    if (lat >= -90 and lat <= 90 and 
                        not(xpt==0 and ypt==0 and ppt==0)):
                        g_of_neighbour = Gridpt(lat, lon, pen)
                        neighbours.append(g_of_neighbour)

        return neighbours

class Super_Ob:
    
    def __init__(self):
        self.grid = {}
    
    def add_rep(self, lat, lon, yr, mo, dy, anom):
        
        rep = Gridpt(lat, lon, yr, mo, dy)

        if anom != None:
            if rep in self.grid:
#                self.obs_by_grid[rep].append(anom)
                self.grid[rep][0] += anom
                self.grid[rep][1] += 1
            else:
#                self.obs_by_grid[rep] = [anom]
                self.grid[rep] = [anom, 1, None, None, None]

        return

    def take_average(self):

        for key in self.grid:
            self.grid[key][2] = self.grid[key][0]/self.grid[key][1]
#            anoms_by_grid.add_rep(key, 
#                                  qc.winsorised_mean(self.obs_by_grid[key]), 
#                                  len(self.obs_by_grid[key]))

        return

    def get_neighbour_anomalies(self, search_radius, key):

        assert len(search_radius) == 3, str(len(search_radius))
        
        temp_anom = []
        temp_nobs = []
    #get all neighbours within 1 degree and 2 pentads
        neighbours = key.get_neighbours(search_radius[0], 
                                        search_radius[1], 
                                        search_radius[2])

        for this_neighbour in neighbours:
            if this_neighbour in self.grid:
                temp_anom.append(self.grid[this_neighbour][2])
                temp_nobs.append(self.grid[this_neighbour][1])

        return temp_anom, temp_nobs

# KW Kate changed pentad_stdev to all_pentad_stdev which is a 73 layered field
    def get_buddy_limits(self, all_pentad_stdev):
        
    #for each populated grid box
        for key in self.grid:

# KW I think we can find the right stdev here - the Gridpt class has already initialised the ptd
# So we just need to point to the correct slice and then feed that through as before - but make sure its still 3D with first dim of 1
# all_pentad_stdev is a 73 by 180 by 360 element array (pentad, latitude, longitude)
# THIS APPEARED TO BE AN ERROR BEFORE WHERE IT WAS READING IN THE 73 PENTAD FILE FOR AT AND SST BUT ONLY PULLING OUT THE FIRST PENTAD!!!
            pentad_stdev = np.reshape(all_pentad_stdev[key.ptd-1,:,:],(1,180,360))
	    
            stdev = qc.get_sst_single_field(key.latitude_approx, key.longitude_approx, 
                                            pentad_stdev)
            if stdev == None or stdev < 0.0:
                stdev = 1.0

            match_not_found = True
    
    #if there is neighbour in that range then calculate a mean        
            if match_not_found:
                
                temp_anom, temp_nobs = self.get_neighbour_anomalies([1, 1, 2], 
                                                                    key)

                if len(temp_anom) > 0:
                
                    self.grid[key][3] = np.mean(temp_anom)
                    total_nobs = np.sum(temp_nobs)
                    
                    self.grid[key][4] = \
                    get_threshold_multiplier(total_nobs, 
                                             [0, 5, 15, 100], 
                                             [4.0, 3.5, 3.0, 2.5])*stdev
         
                    match_not_found = False
                    assert total_nobs != 0, "total number of observations is zero"
    
    #otherwise move out further in space and time to 2 degrees and 2 pentads
            if match_not_found:
                
                temp_anom, temp_nobs = self.get_neighbour_anomalies([2, 2, 2], 
                                                                    key)
                
                if len(temp_anom) > 0:
                    
                    self.grid[key][3] = np.mean(temp_anom)
                    total_nobs = np.sum(temp_nobs)
                    
                    self.grid[key][4] = \
                    get_threshold_multiplier(total_nobs, 
                                             [0], 
                                             [4.0])*stdev
                    
                    match_not_found = False
                    assert total_nobs != 0, "total number of observations is zero"
    
    #otherwise move out further in space and time to 2 degrees and 2 pentads
            if match_not_found:
                
                temp_anom, temp_nobs = self.get_neighbour_anomalies([1, 1, 4], 
                                                                    key)
                
                if len(temp_anom) > 0:
                    
                    self.grid[key][3] = np.mean(temp_anom)
                    total_nobs = np.sum(temp_nobs)
                    
                    self.grid[key][4] = \
                    get_threshold_multiplier(total_nobs, 
                                             [0, 5, 15, 100],
                                             [4.0, 3.5, 3.0, 2.5])*stdev
                    
                    match_not_found = False
                    assert total_nobs != 0, "total number of observations is zero"
    
    #final step out is to 2 degrees and 4 pentads
            if match_not_found:
                
                temp_anom, temp_nobs = self.get_neighbour_anomalies([2, 2, 4], 
                                                                    key)
                
                if len(temp_anom) > 0:
    
                    self.grid[key][3] = np.mean(temp_anom)
                    total_nobs = np.sum(temp_nobs)
                    
                    self.grid[key][4] = \
                    get_threshold_multiplier(total_nobs,
                                             [0], 
                                             [4.0])*stdev
                    
                    match_not_found = False
                    assert total_nobs != 0  , "total number of observations is zero"                    
    
    #if there are no neighbours then any observation will get a pass
            if match_not_found:
                
                self.grid[key][3] = 0.0
                self.grid[key][4] = 500.0
    
        return

    def get_new_buddy_limits(self, stdev1, stdev2, stdev3, sigma_m=1.0):

#for each populated grid box
        for key in self.grid:
            
            stdev1_ex = qc.get_sst_single_field(key.latitude_approx, key.longitude_approx, 
                                                stdev1)
            stdev2_ex = qc.get_sst_single_field(key.latitude_approx, key.longitude_approx, 
                                                stdev2)
            stdev3_ex = qc.get_sst_single_field(key.latitude_approx, key.longitude_approx, 
                                                stdev3)

            if stdev1_ex == None or stdev1_ex < 0.0:
                stdev1_ex = 1.0
            if stdev2_ex == None or stdev2_ex < 0.0:
                stdev2_ex = 1.0
            if stdev3_ex == None or stdev3_ex < 0.0:
                stdev3_ex = 1.0

    #if there is neighbour in that range then calculate a mean        
            temp_anom, temp_nobs = self.get_neighbour_anomalies([2, 2, 4], key)

            if len(temp_anom) > 0:
            
                self.grid[key][3] = np.mean(temp_anom)
                total_nobs = np.sum(temp_nobs)
    
                tot = 0.0
                ntot = 0.0
                for n in temp_nobs:
                    tot += ( sigma_m**2. / n ) #measurement error for each 1x1x5day cell
                    tot += 2 * ( stdev2_ex**2. / n)  #sampling error for each 1x1x5day cell
                    ntot += 1.0
    
                sigma_buddy = tot / (ntot**2.)
                sigma_buddy += stdev3_ex**2. / ntot
    
                self.grid[key][4] = math.sqrt( sigma_m**2. + 
                                               stdev1_ex**2. +
                                               2 * stdev2_ex**2. +
                                               sigma_buddy ) 

            else:
    
                self.grid[key][3] = 0.0
                self.grid[key][4] = 500.

        return
    
    def get_buddy_mean(self, key):
        return self.grid[key][3]

    def get_buddy_stdev(self, key):
        return self.grid[key][4]

class Deck:
    '''
    A class for aggregating individual MarineReports and buddychecking them.
    '''
    def __init__(self):
        self.reps = []
    
    def __len__(self):
        return len(self.reps)

    def append(self, rep):
        self.reps.append(rep)

    def sort(self):
        self.reps.sort()
        
    def pop(self, pos):
        return self.reps.pop(pos)

    def set_qc(self, qc_type, specific_flag, set_value):
        for rep in self.reps:
            rep.set_qc(qc_type, specific_flag, set_value)
        return

    def mds_buddy_check(self, intype, pentad_stdev):

# KW Added capability to cope with DPT
        assert (intype == 'SST' or intype == 'AT' or intype == 'DPT'),intype

#calculate superob averages and numbers of observations
        grid = Super_Ob()
        for rep in self.reps:
            grid.add_rep(rep.getvar('LAT'), rep.getvar('LON'), 
                         rep.getvar('YR'),  rep.getvar('MO'), 
                         rep.getvar('DY'),  rep.getanom(intype))
        grid.take_average()
        grid.get_buddy_limits(pentad_stdev)

    #finally loop over all reports and update buddy QC
        for this_report in self.reps:

# KW I think we could put an if (this_report(getvar('YR') == CandYr && this_report(getvar('MO') == CandYr): clause in here
# This would require CandYR and CandMO being parsed somehow though.
            key = Gridpt(this_report.getvar('LAT'), this_report.getvar('LON'), 
                         this_report.getvar('YR'),  this_report.getvar('MO'), 
                         this_report.getvar('DY'))

    #if the SST anomaly differs from the neighbour average 
    #by more than the calculated range then reject
            x = this_report.getanom(intype)

            if (abs(x - grid.get_buddy_mean(key)) >= grid.get_buddy_stdev(key)):
                this_report.set_qc(intype, 'bud', 1)
            else:
                this_report.set_qc(intype, 'bud', 0)

        del grid

        return

# Kate's version of the MDS buddy check - for AT and DPT
# This requires that the candiate year and month are input - so that checks are only applied to that month
# This uses a stdev field that varies with each pentad seasonally - so has a search on the right pentad
# The stdev fields are currently from 1by1 pentad ERA-Interim - so most likely underestimates of the standard deviation!
# WE'RE LIKELY TO REMOVE GOOD DATA!!!

    def mdsKATE_buddy_check(self, intype, all_pentad_stdev, thisyear, thismonth):
        ''' all_pentad_stdev: a lon,lat,73 pentad field of climatological standard deviations of all obs (ERA 1by1 daily grids) going into pentad clim '''
        ''' thisyear: the candidate year '''
        ''' thismonth: the candidate month '''

# KW Added capability to cope with DPT
        assert (intype == 'SST' or intype == 'AT' or intype == 'DPT'),intype

#calculate superob averages and numbers of observations
        grid = Super_Ob()
        for rep in self.reps:
            grid.add_rep(rep.getvar('LAT'), rep.getvar('LON'), 
                         rep.getvar('YR'),  rep.getvar('MO'), 
                         rep.getvar('DY'),  rep.getanom(intype))
        grid.take_average()
	
# KW This now has the 73 pentad field and has to find the correct pentad
# the Super_Ob() object (now called grid() has some relationship to the class Gridpt which has a function call self.ptd which should return the pentad of interest (1 to 73)
# SO - pull out the correct slice from all_pentad_stdev, call it pentad_stdev and feed it in.
# I have added a line to do this in get_buddy_limits which utilises the Gridpt class for each element of grid()
# This isn't perfect - perhaps you'd want the slice of pentads that covers the range of 'buddy' obs - too complex for now
# At least this has some seasonal variability
#        pdb.set_trace()
# So i've changed pentad_stdev to all_pentad_stdev
        grid.get_buddy_limits(all_pentad_stdev)

    #finally loop over all reports and update buddy QC
        for this_report in self.reps:

# KW Added a filter to only work on reps with YR and MO matching candidate YR and MO
            if ((this_report.getvar('YR') == thisyear) & (this_report.getvar('MO') == thismonth)):
                key = Gridpt(this_report.getvar('LAT'), this_report.getvar('LON'), 
                             this_report.getvar('YR'),  this_report.getvar('MO'), 
                             this_report.getvar('DY'))

        #if the SST anomaly differs from the neighbour average 
        #by more than the calculated range then reject
                x = this_report.getanom(intype)

                if (abs(x - grid.get_buddy_mean(key)) >= grid.get_buddy_stdev(key)):
                    this_report.set_qc(intype, 'bud', 1)
                else:
                    this_report.set_qc(intype, 'bud', 0)
# KW a catch to double check we are checking the right month
            else:
	        this_report.set_qc(intype, 'bud', 8)

        del grid

        return

    def bayesian_buddy_check(self, intype, stdev1, stdev2, stdev3, sigma_m=1.0):

# KW Added capability to cope with DPT *** BUT - NOT ACTUALLY GOING TO APPLY BAYESIAN TO AT OR TO DPT BECAUSE WE DO NOT HAVE APPROPRIATE AT OR DPT FIELDS ***
        assert (intype == 'SST' or intype == 'AT' or intype == 'DPT'), "Unknown intype: "+intype
    
        p0 = 0.05      #prior probability of gross error
        Q = 0.1        #rounding leve of data
        R_hi = 8.0     #previous upper QC limits set
        R_lo = -8.0    #previous lower QC limit set
        
# KW Added DPT to the R_hi/lo = 10/-10 deg - could be better to narrow later on?
        if ((intype == 'AT') | (intype == 'DPT')):
            R_hi = 10.0     #previous upper QC limits set
            R_lo = -10.0    #previous lower QC limit set

#        sigma_m = 1.0  #estimated uncertainty in single ob
        p_threshold_sst = 0.10    #threshold cutoff for bayesian check
        p_threshold_nmat = 0.50 #threshold for NMAT check

        grid = Super_Ob()
        for rep in self.reps:
            grid.add_rep(rep.getvar('LAT'), rep.getvar('LON'), 
                         rep.getvar('YR'),  rep.getvar('MO'), 
                         rep.getvar('DY'),  rep.getanom(intype))
        grid.take_average()
        grid.get_new_buddy_limits(stdev1, stdev2, stdev3, sigma_m)

        for this_report in self.reps:

# KW I think we could put an if (this_report(getvar('YR') == CandYr && this_report(getvar('MO') == CandYr): clause in here
# This would require CandYR and CandMO being parsed somehow though.
        
            key = Gridpt(this_report.getvar('LAT'), this_report.getvar('LON'), 
                         this_report.getvar('YR'), this_report.getvar('MO'), 
                         this_report.getvar('DY'))

#if the SST anomaly differs from the neighbour average 
#by more than the calculated range then reject

            ppp = qc.p_gross(p0, Q, R_hi, R_lo, 
                             this_report.getanom(intype), 
                             grid.get_buddy_mean(key), 
                             grid.get_buddy_stdev(key))

            if ppp > 0:
                flag = int(math.floor(ppp*10))
                if flag > 9: flag = 9
                this_report.set_qc(intype, 'bbud', flag)
            else:
                this_report.set_qc(intype, 'bbud', int(0))

        del grid

        return

    def get_one_ship_at_a_time(self):

        id_of_ship = self.reps[0].getvar('ID')
        out_voyage = Voyage()

        while len(self.reps) > 0:

            rep = self.reps.pop(0)

            if rep.getvar('ID') != id_of_ship:
                id_of_ship = rep.getvar('ID')
                yield out_voyage
                out_voyage = Voyage()

            out_voyage.add_report(rep)

        if len(out_voyage) > 0:
            yield out_voyage

