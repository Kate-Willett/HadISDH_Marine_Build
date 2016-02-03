'''
Buddy check routines for MDS. Buddy checking compares individual observations to 
a background average. The routines in this module are used to buddy check 
collections of MarineReports.
'''

import numpy as np
import math
import qc
import sys

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
        self.obs_by_grid = {}
    
    def add_rep(self, lat, lon, yr, mo, dy, anom):
        
        rep = Gridpt(lat, lon, yr, mo, dy)

        if anom != None:
            if rep in self.obs_by_grid:
                self.obs_by_grid[rep].append(anom)
            else:
                self.obs_by_grid[rep] = [anom]

        return

    def take_average(self):

        anoms_by_grid = {}
        for key in self.obs_by_grid:
            anoms_by_grid[key] = [qc.winsorised_mean(self.obs_by_grid[key]), 
                                  len(self.obs_by_grid[key])]

        self.obs_by_grid = {}

        return anoms_by_grid

def grid_super_obs(reps, intype):

    '''
    Aggregate a list of :class:`.MarineReport` onto a 1x1x5-day grid using resistant averages
    
    :param reps: list of MarineReports to be gridded
    :param intype: one of either 'SST' for gridding SST or 'MAT' for gridding MAT
    :type reps: :class:`.MarineReport`
    :type intype: string
    :return: a dictionary whose keys are :class:`.Gridpt` instances and which contain two-element lists with the robust average and the number of observations contributing to it.
    :rtype: dictionary of list of floats. Keys are :class:`.Gridpt`
    
    The function grids anomalies from a list of marine reports. To save space and generally speed things up, 
    the whole grid is never calculated. Instead, a dictionary is used. The keys are the populated grid boxes 
    (as :class:`.Gridpt` objects) and lists are stored for each key. The output is in this format with the list under each key 
    containing an average anomaly and a count of observations. 
    '''

    assert (intype == 'SST' or intype == 'AT'), intype

# this does a simple gridding of observations of type "MarineReport" 
# with observations and averages for each grid cell held in dictionaries
# it returns a dictionary with an entry for each occupied grid cell 
# and each entry is a list with two elements:
# the gridcell average and the number of obs contributing to that average 

    #make dictionary (obs_by_grid) of all anomalies referenced by grid point
    obs_by_grid = {}
    for this_report in reps:
        rep = Gridpt(this_report.getvar('LAT'), this_report.getvar('LON'), 
                     this_report.getvar('YR'),  this_report.getvar('MO'), 
                     this_report.getvar('DY'))

        x = this_report.getanom(intype)
        if x != None:
            if rep in obs_by_grid:
                obs_by_grid[rep].append(x)
            else:
                obs_by_grid[rep] = [x]

#calculate the trimmed mean of the super obs in each grid box
#loop over all the keys in obs_by_grid. Each key is the 
#index for a different grid box
#and each entry in obs_by_grid is a list of anomalies for 
#which we want to take the trimmed mean
#and count the available observations
    anoms_by_grid = {}
    for key in obs_by_grid:
        anoms_by_grid[key] = [qc.winsorised_mean(obs_by_grid[key]), 
                              len(obs_by_grid[key])]

    return anoms_by_grid

def get_neighbour_anomalies(search_radius, key, anoms_by_grid):
    '''
    given a search radius and a key get all the neighbour anomalies
    
    :param search_radius: a list with three elements which define the 
                          lat, lon and time limits for the neighbour search
    :param key: the :class:`.Gridpt` for which we want to find the neighbours
    :param anoms_by_grid: the gridded anomalies in a dictinoary with :class:`.Gridpt` keys
    :type search_radius: integer 
    :type key: :class:`.Gridpt`
    :type anoms_by_grid: dictionary
    :return: A list of neighbour anomalies and a list of the number of 
             observations contributing to each of those anomalies
    :rtype: float
    '''
    assert len(search_radius) == 3, str(len(search_radius))
    
    temp_anom = []
    temp_nobs = []
#get all neighbours within 1 degree and 2 pentads
    neighbours = key.get_neighbours(search_radius[0], 
                                    search_radius[1], 
                                    search_radius[2])
    for this_neighbour in neighbours:
        if this_neighbour in anoms_by_grid:
            temp_anom.append(anoms_by_grid[this_neighbour][0])
            temp_nobs.append(anoms_by_grid[this_neighbour][1])

    return temp_anom, temp_nobs

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

def get_new_buddy_limits(anoms_by_grid, stdev1, stdev2, stdev3, sigma_m=1.0):
    
    """
    This returns the buddy mean and buddy uncertainty given a whole set of input fields.
    
    :param anoms_by_grid: a set of gridded anomalies
    :param stdev1: a field of standard deviations of the difference between a single grid box and a buddy average
    :param stdev2: a field of standard deviations of the sampling error for a single 1x1x5-day grid cell
    :param stdev3: a field of standard deviations of the sampling error from estimating a buddy average by one grid box
    :param sigma_m: the estimated measurement error uncertainty on a single observation
    :type anoms_by_grid: dictionary containing two-element lists [anom, number of observations]. 
                         The keys of the dictionary are :class:`.Gridpt` objects
    :type stdev1: numpy masked array
    :type stdev2: numpy masked array
    :type stdev3: numpy masked array
    :type sigma_m: float
    :return: buddy average anomaly and expected standard deviation of difference between an ob and the buddy average
    :rtype: dictionaries containing two-element lists [anom, number of observations]. 
            The keys of the dictionary are :class:`.Gridpt` objects
            
    This is the updated estimate of the buddy limits used internally in the new buddy check and 
    bayesian buddy check. An observation will be compared to the buddy average (the first returned 
    value) with the limits set by the standard deviation (the second returned value). 
    """
    
    buddy_anom_by_grid = {}
    buddy_multiplier_by_grid = {}
#for each populated grid box
    for key in anoms_by_grid:
        
        stdev1_ex = qc.get_sst(key.latitude_approx, key.longitude_approx, 
                               key.month, key.day, stdev1)
        stdev2_ex = qc.get_sst(key.latitude_approx, key.longitude_approx, 
                               key.month, key.day, stdev2)
        stdev3_ex = qc.get_sst(key.latitude_approx, key.longitude_approx, 
                               key.month, key.day, stdev3)

        if stdev1_ex == None or stdev1_ex < 0.0:
            stdev1_ex = 1.0
        if stdev2_ex == None or stdev2_ex < 0.0:
            stdev2_ex = 1.0
        if stdev3_ex == None or stdev3_ex < 0.0:
            stdev3_ex = 1.0

#if there is neighbour in that range then calculate a mean        
        temp_anom, temp_nobs = \
        get_neighbour_anomalies([2, 2, 4], 
                                key, 
                                anoms_by_grid)

        if len(temp_anom) > 0:
        
            buddy_anom_by_grid[key] = np.mean(temp_anom)
            total_nobs = np.sum(temp_nobs)

            tot = 0.0
            ntot = 0.0
            for n in temp_nobs:
                tot += ( sigma_m**2. / n ) #measurement error for each 1x1x5day cell
                tot += 2 * ( stdev2_ex**2. / n)  #sampling error for each 1x1x5day cell
                ntot += 1.0

            sigma_buddy = tot / (ntot**2.)
            sigma_buddy += stdev3_ex**2. / ntot

            """The uncertainty in the buddy average as a prediction of the measurement is as given
            the sum of the uncertainty in the buddy average, the uncertainty associated with using 
            the buddy average to estimate the point value and the uncertainty in a single measurement"""
            buddy_multiplier_by_grid[key] = math.sqrt( sigma_m**2. + 
                                                       stdev1_ex**2. + 
                                                       2 * stdev2_ex**2. +
                                                       sigma_buddy ) 

        else:

            buddy_anom_by_grid[key] = 0.0
            buddy_multiplier_by_grid[key] = 500.

    return buddy_anom_by_grid, buddy_multiplier_by_grid

def get_buddy_limits(anoms_by_grid, pentad_stdev):

    '''
    This is an internal routine for the buddy check. It takes gridded obs in a dictionary and a field of standard 
    deviations and returns the neighbour-average for each populated gridcell as well as bounds based on the number 
    of neighbours.
    
    :param anoms_by_grid: gridded anomalies and counts of observations 
    :param pentad_stdev: grid of climatological standard deviations
    :type anoms_by_grid: dictionary containing two-element lists [anom, number of observations]. The keys of the dictionary are :class:`.Gridpt` objects
    :type pentad_stdev: numpy array
    :return: gridded buddy anomalies and gridded buddy multipliers
    :rtype: dictionaries containing buddy anomalies and multipliers referenced by :class:`Gridpt` 
    
    A neighbour average and allowed range are calculated for each populated grid cell. Neighbours are initially 
    sought within 1 degree and 2 pentads. If neighbours are found then for N observations the allowed ranges R are:
    
    * If N > 100:      R = SD*2.5
    * If 15 < N < 100: R = SD*3.0
    * If 5 < N < 15:   R = SD*3.5
    * If 0 < N < 5:    R = SD*4.0
    
    Where SD is the input standard deviation for that grid box. M, the mean of the anomalies, is also calculated.
    
    If no neighbours are found then the search area is expanded to 2 degrees and 2 pentads and then to 1 degrees 
    and 4 pentads and then 2 degrees and 4 pentads. If neighbours are found then the allowed ranges R are:
    
    * R = SD*4.0
    
    If no neighbours are found at all then the range is set to be infinite.
    
    The function returns M and R for each grid box
    '''
#this takes a dictionary (anoms_by_grid) whose keys 
#are instances of type Gridpt.
#each key relates to a single 1x1xpentad grid box and 
#the entries are each a two-element list
#the first element is the grid box average and the 
#second is the number of obs in the average.
#for each of these populated grid boxes, neighbours 
#are sought and a neighbour average and
#tolerance is calculated.

    buddy_anom_by_grid = {}
    buddy_multiplier_by_grid = {}
#for each populated grid box
    for key in anoms_by_grid:
        
        stdev = qc.get_sst(key.latitude_approx, key.longitude_approx, 
                           key.month, key.day, pentad_stdev)
        if stdev == None or stdev < 0.0:
            stdev = 1.0

        match_not_found = True

#if there is neighbour in that range then calculate a mean        
        if match_not_found:
            
            temp_anom, temp_nobs = \
            get_neighbour_anomalies([1, 1, 2], 
                                    key, 
                                    anoms_by_grid)
            
            if len(temp_anom) > 0:
            
                buddy_anom_by_grid[key] = np.mean(temp_anom)
                total_nobs = np.sum(temp_nobs)
                
                buddy_multiplier_by_grid[key] = \
                get_threshold_multiplier(total_nobs, 
                                         [0, 5, 15, 100], 
                                         [4.0, 3.5, 3.0, 2.5])*stdev
                                         
                match_not_found = False
                assert total_nobs != 0, "total number of observations is zero"

#otherwise move out further in space and time to 2 degrees and 2 pentads
        if match_not_found:
            
            temp_anom, temp_nobs = \
            get_neighbour_anomalies([2, 2, 2], 
                                    key, 
                                    anoms_by_grid)
            
            if len(temp_anom) > 0:
                
                buddy_anom_by_grid[key] = np.mean(temp_anom)
                total_nobs = np.sum(temp_nobs)
                
                buddy_multiplier_by_grid[key] = \
                get_threshold_multiplier(total_nobs, 
                                         [0], 
                                         [4.0])*stdev
                
                match_not_found = False
                assert total_nobs != 0, "total number of observations is zero"

#otherwise move out further in space and time to 2 degrees and 2 pentads
        if match_not_found:
            
            temp_anom, temp_nobs = \
            get_neighbour_anomalies([1, 1, 4], 
                                    key, 
                                    anoms_by_grid)
            
            if len(temp_anom) > 0:
                
                buddy_anom_by_grid[key] = np.mean(temp_anom)
                total_nobs = np.sum(temp_nobs)
                
                buddy_multiplier_by_grid[key] = \
                get_threshold_multiplier(total_nobs, 
                                         [0, 5, 15, 100],
                                         [4.0, 3.5, 3.0, 2.5])*stdev
                
                match_not_found = False
                assert total_nobs != 0, "total number of observations is zero"

#final step out is to 2 degrees and 4 pentads
        if match_not_found:
            
            temp_anom, temp_nobs = \
            get_neighbour_anomalies([2, 2, 4], 
                                    key, 
                                    anoms_by_grid)
            
            if len(temp_anom) > 0:

                buddy_anom_by_grid[key] = np.mean(temp_anom)
                total_nobs = np.sum(temp_nobs)
                
                buddy_multiplier_by_grid[key] = \
                get_threshold_multiplier(total_nobs,
                                         [0], 
                                         [4.0])*stdev
                
                match_not_found = False
                assert total_nobs != 0  , "total number of observations is zero"                    

#if there are no neighbours then any observation will get a pass
        if match_not_found:
            
            buddy_anom_by_grid[key] = 0.0
            buddy_multiplier_by_grid[key] = 500.0

    return buddy_anom_by_grid, buddy_multiplier_by_grid

def mds_buddy_check(reps, pentad_stdev, intype, month=-1):

    '''
    Do the buddy check, which compares observations to other nearby observations to check for consistency
    
    :param reps: a list of MarineReports that are to be buddy checked
    :param pentad_stdev: a grid of climatological standard deviations
    :param type: one of 'SST' for and SST buddy check, or 'MAT' for an MAT buddy check
    :type reps: :class:`.MarineReport`
    :type pentad_stdev: float
    :type intype: string
    :return: a list of qc outcomes, either 1 for fail or 0 for pass for each input report
    :rtype: list of integers
    
    The buddy check first grids all the input observations at 1x1xpentad resolution. It then calculates the neighbour 
    averages and allowed deviations from the neighbour averages for each populated grid box. Each observation is then 
    checked to see if it falls inside or outside that range.
    '''
    assert (intype == 'SST' or intype == 'AT'),intype

# this is an implementation of the MDS buddy check
# it robustly grids observations at 1x1xpentad resolution and for each 
# populated gridcell calculates a neighbour average and tolerances
# each observation is then compared to these

    qcs = []
    
#calculate superob averages and numbers of observations
    grid = Super_Ob()
    for rep in reps:
        grid.add_rep(rep.getvar('LAT'), rep.getvar('LON'), 
                     rep.getvar('YR'),  rep.getvar('MO'), 
                     rep.getvar('DY'),  rep.getanom(intype))
    anoms_by_grid = grid.take_average()
#    anoms_by_grid = grid_super_obs(reps, intype)

#get the buddy limits given gridded super obs
    buddy_anom_by_grid, buddy_multiplier_by_grid = \
    get_buddy_limits(anoms_by_grid, pentad_stdev)

#finally loop over all reports and update buddy QC
    for this_report in reps:
        if this_report.getvar('MO') == month or month == -1:
            key = Gridpt(this_report.getvar('LAT'), this_report.getvar('LON'), 
                         this_report.getvar('YR'),  this_report.getvar('MO'), 
                         this_report.getvar('DY'))
    
    #if the SST anomaly differs from the neighbour average 
    #by more than the calculated range then reject
            x = this_report.getanom(intype)
               
            if (abs(x - buddy_anom_by_grid[key]) >= 
                buddy_multiplier_by_grid[key]):
                
                this_report.set_qc(intype, 'buddy_fail', 1)
                qcs.append(1)
                
            else:
                this_report.set_qc(intype, 'buddy_fail', 0)
                qcs.append(0)

    return reps

def new_buddy_check(reps, pentad_stdev, intype):

    '''
    Do the new buddy check, which compares observations to other nearby observations to check for consistency
    
    :param reps: a list of MarineReports that are to be buddy checked
    :param pentad_stdev: a grid of climatological standard deviations
    :param type: one of 'SST' for and SST buddy check, or 'MAT' for an MAT buddy check
    :type reps: :class:`.MarineReport`
    :type pentad_stdev: float
    :type intype: string
    :return: a list of qc outcomes, either 1 for fail or 0 for pass for each input report
    :rtype: list of integers
    
    The buddy check first grids all the input observations at 1x1xpentad resolution. It then calculates the neighbour 
    averages and allowed deviations from the neighbour averages for each populated grid box. Each observation is then 
    checked to see if it falls inside or outside that range.
    '''
    assert (intype == 'SST' or intype == 'AT'), intype

    sigma_m = 1.0  #measurement uncertainty in one ob
    
# this is an implementation of the MDS buddy check
# it robustly grids observations at 1x1xpentad resolution and for each 
# populated gridcell calculates a neighbour average and tolerances
# each observation is then compared to these

    qcs = []
    
#calculate superob averages and numbers of observations
    grid = Super_Ob()
    for rep in reps:
        grid.add_rep(rep.getvar('LAT'), rep.getvar('LON'), 
                     rep.getvar('YR'),  rep.getvar('MO'), 
                     rep.getvar('DY'),  rep.getanom(intype))
    anoms_by_grid = grid.take_average()
#    anoms_by_grid = grid_super_obs(reps, intype)

#get the buddy limits given gridded super obs
    buddy_anom_by_grid, buddy_multiplier_by_grid = \
    get_new_buddy_limits(anoms_by_grid, pentad_stdev,sigma_m)

#finally loop over all reports and update buddy QC
    for this_report in reps:
        key = Gridpt(this_report.getvar('LAT'), this_report.getvar('LON'), 
                     this_report.getvar('YR'),  this_report.getvar('MO'), 
                     this_report.getvar('DY'))

#if the SST anomaly differs from the neighbour average 
#by more than the calculated range then reject

        x = this_report.getanom(intype)

        if (abs(x - buddy_anom_by_grid[key]) >= 
            3*buddy_multiplier_by_grid[key]):

            this_report.set_qc(intype, 'buddy_fail', 1)
            qcs.append(1)

        else:
            this_report.set_qc(intype, 'buddy_fail', 0)
            qcs.append(0)

    return qcs

def bayesian_buddy_check(reps, stdev1, stdev2, stdev3, intype, month=-1):

    '''
    Do the bayesian buddy check, which compares observations to other nearby observations to check for consistency
    
    :param reps: a list of MarineReports that are to be buddy checked
    :param pentad_stdev: a grid of climatological standard deviations
    :param type: one of 'SST' for and SST buddy check, or 'MAT' for an MAT buddy check
    :type reps: :class:`.MarineReport`
    :type pentad_stdev: float
    :type intype: string
    :return: a list of qc outcomes, flags are between 0 and 9, indicating the approximate probability that the 
             observation is in gross error. e.g 2 indicates Probability between 0.2 and 0.299999
    :rtype: list of integers
    
    The buddy check first grids all the input observations at 1x1xpentad resolution. It then calculates the neighbour 
    averages and allowed deviations from the neighbour averages for each populated grid box. The probability that 
    each observation is in gross error is then calculated using a simple bayesian update. Various parameters are 
    specified within the function.
    '''
    assert (intype == 'SST' or intype == 'AT'), "Unknown intype: "+intype
    
    p0 = 0.05      #prior probability of gross error
    Q = 0.1        #rounding leve of data
    R_hi = 8.0     #previous upper QC limits set
    R_lo = -8.0    #previous lower QC limit set

    if intype == 'AT':
        R_hi = 10.0     #previous upper QC limits set
        R_lo = -10.0    #previous lower QC limit set
   
    sigma_m = 1.0  #estimated uncertainty in single ob
    p_threshold_sst = 0.10    #threshold cutoff for bayesian check
    p_threshold_nmat = 0.50 #threshold for NMAT check

# this is an implementation of the MDS buddy check
# it robustly grids observations at 1x1xpentad resolution and for each 
# populated gridcell calculates a neighbour average and tolerances
# each observation is then compared to these

    qcs = []
    
#calculate superob averages and numbers of observations
    grid = Super_Ob()
    for rep in reps:
        grid.add_rep(rep.getvar('LAT'), rep.getvar('LON'), 
                     rep.getvar('YR'),  rep.getvar('MO'), 
                     rep.getvar('DY'),  rep.getanom(intype))

    anoms_by_grid = grid.take_average()
#    anoms_by_grid = grid_super_obs(reps, intype)

#get the buddy limits given gridded super obs
    buddy_anom_by_grid, buddy_multiplier_by_grid = \
    get_new_buddy_limits(anoms_by_grid, stdev1, stdev2, stdev3, sigma_m)

#finally loop over all reports and update buddy QC
    for this_report in reps:
        
        if this_report.getvar('MO') == month or month == -1:
            key = Gridpt(this_report.getvar('LAT'), this_report.getvar('LON'), 
                         this_report.getvar('YR'), this_report.getvar('MO'), 
                         this_report.getvar('DY'))
    
            assert key in buddy_anom_by_grid, "key not in buddy_anom_by_grid \n"+this_report.print_report()
            assert key in buddy_multiplier_by_grid, "key not in buddy_multiplier_by_grid \n"+this_report.print_report()
    
    #if the SST anomaly differs from the neighbour average 
    #by more than the calculated range then reject
    
            x = this_report.getanom(intype)
    
            mu = buddy_anom_by_grid[key]
            sigma = buddy_multiplier_by_grid[key]
            ppp = qc.p_gross(p0, Q, R_hi, R_lo, x, mu, sigma)
    
            if ppp > 0:
                flag = int(math.floor(ppp*10))
                if flag > 9: flag = 9
                this_report.set_qc(intype, 'bayesian_buddy_check', flag)
                qcs.append(1)
            else:
                this_report.set_qc(intype, 'bayesian_buddy_check', int(0))
                qcs.append(0)

    return reps
