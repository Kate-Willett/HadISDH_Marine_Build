'''
The Track Check QC module provides the functions needed to perform the 
track check. The main routine is mds_full_track_check which takes a 
list of :class:`.MarineReport` from a single ship and runs the track check on them
'''

import math
import qc
import numpy as np

def xdist(alat1, alon1, alat2, alon2):
    '''
    Legacy routine for calculating distance between two lat,lon points as used in MDS3 and earlier
    
    :param alat1: Latitude of first point
    :param alon1: Longitude of first point
    :param alat2: Latitude of second point
    :param alon2: Longitude of second point
    :type alat1: float
    :type alon1: float
    :type alat2: float
    :type alon2: float
    :return: Distance between the points in Nautical Miles (of course)
    :rtype: float
    
    This piece of code treats the earth as if it was geometrically something other than a sphere. It calculates the 
    angular distance between the points in latitude and the angular distance in longitude, turns each of those into a distance in 
    nautical miles, and pythagorises them. This is not how to calculate the distance between two points on a sphere. 
    I'm not sure there is any consistent geometry for which this is the correct formula. However, for short distances 
    it is a reasonable approximation.
    '''
#calculate distance between two point in nautical miles
#radius of earth in nautical miles = 3440 so 1degree = 
#60 nautical miles (actually 60.0393)
    radcon = 0.0174532925    
#     Calculate sides of triangle                                       
    side1 = (alat2 - alat1) * 60                                       
#     Allow for crossing dateline or zero meridian.                     
    tspec = alon2 - alon1                   
    if abs(tspec) > 300:
        tspec = math.copysign(360 - abs(tspec), alon1)
#   IF (ABS (TSPEC) .GT. 300) TSPEC = SIGN (360 -ABS (TSPEC), ALON1)  
    side2 = tspec * 60 * math.cos(((alat2 + alat1) /2) * radcon)
 
    xdistout = math.sqrt(side1*side1 + side2*side2)

    return xdistout, side1, side2

def speed1(lat1, lat2, lon1, lon2, timdif):
    '''
    Given a pair of lat, lon points and the time it took to travel between them, 
    calculates the speed, distance and direction the ship is headed.
    
    :param lat1: latitude of first point
    :param lat2: latitude of second point
    :param lon1: longitude of first point
    :param lon2: longitude of second point
    :param timdif: time difference in hours between the two points
    :type lat1: float
    :type lat2: float
    :type lon1: float
    :type lon2: float
    :type timdif: float
    :return: speed in knots, distance covered in nautical miles, heading in degrees from north, longitudinal distance and latitudinal distance
    :rtype: float
    
    Another legacy routine from the old MDS. This uses slightly incorrect formulae for calculating the distance between points. 
    The heading is also calculated in a way that will be slightly wrong. Nevertheless, the method works OK for small distances 
    and is necessary to reproduce the behaviour of the old QC system.    
    '''
#To compute ship's speed and distance of travel.                   
#at1,at2 first and second latitudes
#an1,an2 first and second longitudes
#timdif time in hours between positions
#shpspd  speed in knots
#shpdis  distance travelled
#side1,side2 are lat and longitudinal distances travelled
#shpdir direction travelled in degrees

# Conversion factor between degrees and radians
    degrad = 0.017453292384743690

    shpdis, side1, side2 = xdist(lat1, lon1, lat2, lon2)          

    if timdif > 0:
        shpspd = shpdis / timdif
    else:
        timdif = 1.0
        shpspd = shpdis
    
#direction of travel
    if shpdis == 0:
        shpdir = None
        shpspd = 0.00
    else:
        shpdir = math.atan2(side1, side2)
        shpdir = shpdir/degrad
        
#adjust to compass direction of travel
        if side1 >= 0 and side2 >= 0:
            shpdir = 90 - shpdir
        elif side1 < 0 and side2 >= 0:
            shpdir = 90 - shpdir
        elif side1 < 0  and side2 < 0:
            shpdir = 90 - shpdir
        elif side1 >= 0 and side2 < 0:
            shpdir = 450 - shpdir

#assert (shpdir == None) or (shpdir >= 0  and shpdir <= 360),
#"Ship direction outside range 0-360 or not None "+str(shpdir)+\
#"with inputs "+str(at1)+" "+str(at2)+" "+
#str(an1)+" "+str(an2)+" "+str(timdif)

    return shpspd, shpdis, shpdir, side1, side2

def meansp(awork):
    '''
    MDS3 (and earlier) routine for calculating the mean of a list of speeds. 
    It ignores the first entry which will usually be None.
    
    :param awork: list of input speeds
    :type awork: float
    :return: mean of the input speeds except for the first, if only one or no elements are input, returns None
    :rtype: float
    
    Slightly idiosyncratic way of calculating the mean of speeds in the MDS3 QC checks.
    '''
#Compute mean speed for ship.
#As these are calculated speeds, the first entry will be 
#zero, so ignore this in calculation.
    if len(awork) > 1:
        amean = np.mean(awork[1:])
    else:
        amean = None

    return amean

def modesp(awork):
    '''
    Calculate the modal speed from the input array in 3 knot bins. Returns the 
    bin-centre for the modal group.
    
    :param awork: list of input speeds
    :type awork: float
    :return: bin-centre speed for the 3 knot bin which contains most speeds in 
             input array, or 8.5, whichever is higher
    :rtype: float
    
    The data are binned into 3-knot bins with the first from 0-3 knots having a 
    bin centre of 1.5 and the highest containing all speed in excess of 33 knots 
    with a bin centre of 34.5. The bin with the most speeds in it is found. The higher of 
    the modal speed or 8.5 is returned::

      Bins-   0-3, 3-6, 6-9, 9-12, 12-15, 15-18, 18-21, 21-24, 24-27, 27-30, 30-33, 33-36
      Centres-1.5, 4.5, 7.5, 10.5, 13.5,  16.5,  19.5,  22.5,  25.5,  28.5,  31.5,  34.5
    '''

# if there is one or no observations then return None
# if the speed is on a bin edge then it rounds up to higher bin
# if the modal speed is less than 8.50 then it is set to 8.50 
# anything exceeding 36 knots is assigned to the top bin

    ikmode = -32768
    acint = []
    ifreq = []
    for i in range(1, 13):
        acint.append(i*3.0)
        ifreq.append(0.0)

    ntime = len(awork)

    if ntime > 1:
        for i in range(1, ntime):
            #fixed so that indexing starts at zero
            index = int(math.floor(awork[i]/3.0))  
            if index < 0:
                index = 0
            elif index > 11:
                index = 11
            ifreq[index] = ifreq[index] + 1

        for index in range(0, 12):
            if ifreq[index] > ikmode:
                ikmode = ifreq[index]
                icmode = 1
                atmode = acint[index] - 1.50

        amode = atmode/icmode
        if amode <= 8.50:
            amode = 8.50
    
    else:
        amode = None
    
    return amode

def calc_1step_speeds(inreps):

    '''
    For an input set of :class:`.MarineReport`, return the time differences, speeds, distance and directions between each consecutive report
    
    :param inreps: Input list of type :class:`.MarineReport` in time order
    :type inreps: :class:`.MarineReport`
    :return: time differences, speeds, distance and directions between each consecutive report
    :rtype: list of floats
    
    The routine steps through the input list and calculates various things between consecutive data points. Consequently, the 
    first value in the list has no corresponding output (there's nothing to calculate its difference from). The output is four 
    lists each as long as the input containing time differences, speeds, distances and directions.
    '''

    nobs = len(inreps)
    
    if nobs > 0:
    
        speeds = [None]
        time_differences = [None]
        distances = [None]
        ship_directions = [None]

        for i in range(1, nobs):
                
            tdiff = qc.time_difference(inreps[i-1].year, inreps[i-1].month, 
                                       inreps[i-1].day, inreps[i-1].hour,
                                       inreps[i].year,   inreps[i].month,   
                                       inreps[i].day,   inreps[i].hour)

            shpspd, shpdis, shpdir, side1, side2 = speed1(inreps[i-1].lat, 
                                                          inreps[i].lat,
                                                          inreps[i-1].lon, 
                                                          inreps[i].lon, tdiff)

            time_differences.append(tdiff)
            speeds.append(shpspd)
            distances.append(shpdis)
            ship_directions.append(shpdir)

    else:
        speeds = []
        time_differences = []
        distances = []
        ship_directions = []

    lin = len(inreps)
    assert (len(time_differences) == lin and 
            len(speeds) == lin and 
            len(distances) == lin and 
            len(ship_directions) == lin)

    return time_differences, speeds, distances, ship_directions

def calc_alternate_step_speeds(inreps):
    '''
    For an input list of :class:`.MarineReport`, return the time differences, speeds, distance and directions between alternate reports, e.g. 
    1 and 3, 2 and 4, 3 and 5 etc..
    
    :param inreps: Input list of :class:`.MarineReport` in time order
    :type inreps: :class:`.MarineReport`
    :return: time differences, speeds, distance and directions between each consecutive report
    :rtype: list of floats
    
    The routine steps through the input list and calculates various things between alternating data points. Consequently, the 
    first and second values in the list have no corresponding outputs (there's nothing to calculate its difference from). The 
    output is four lists each as long as the input containing time differences, speeds, distances and directions.
    '''

    nobs = len(inreps)
    if nobs > 0:
        speeds = [None]
        time_differences = [None]
        distances = [None]
        ship_directions = [None]
    
        for i in range(1, nobs-1):
                
            tdiff = qc.time_difference(inreps[i-1].year, inreps[i-1].month, 
                                       inreps[i-1].day, inreps[i-1].hour,
                                       inreps[i+1].year, inreps[i+1].month, 
                                       inreps[i+1].day, inreps[i+1].hour)

            shpspd, shpdis, shpdir, side1, side2 = speed1(inreps[i-1].lat, 
                                                          inreps[i+1].lat,
                                                          inreps[i-1].lon, 
                                                          inreps[i+1].lon, 
                                                          tdiff)

            time_differences.append(tdiff)
            speeds.append(shpspd)
            distances.append(shpdis)
            ship_directions.append(shpdir)
    
        time_differences.append(None)
        speeds.append(None)
        distances.append(None)
        ship_directions.append(None)
    else:
        speeds = []
        time_differences = []
        distances = []
        ship_directions = []

    lin = len(inreps)
    assert (len(time_differences) == lin and 
            len(speeds) == lin and 
            len(distances) == lin and 
            len(ship_directions) == lin)

    return time_differences, speeds, distances, ship_directions

def set_speed_limits(amode):
    '''
    Takes a modal speed and calculates speed limits for the track checker
    
    :param amode: modal speed
    :type amode: float
    :return: max speed, max max speed and min speed
    :rtype: float
    '''    
    amax  = 15.00
    amaxx = 20.00
    amin  = 0.00

    if amode != None:
        if amode <= 8.51:
            amax  = 15.00
            amaxx = 20.00
            amin  = 0.00
        else:
            amax = amode * 1.25
            amaxx = 30.00
            amin = amode * 0.75
        
    return amax, amaxx, amin

def increment_position(alat1, alat2, avs, ads, timdif):
    '''
    Increment_position takes two latitudes at the start 
    and end points of a line segment, a speed, a direction and a time difference and 
    returns increments of latitude and longitude which correspond to half the time difference.
    
    :param alat1: Latitude at starting point
    :param alat2: Latitude at finishing point
    :param avs: speed of ship in knots
    :param ads: heading of ship in degrees
    :param timdif: time difference between the points
    :type alat1: float
    :type alat2: float
    :type avs: float
    :type ads: float
    :type timdif: float
    '''
    radcon = 0.0174532925      

    assert alat1 >= -90 and alat1 <= 90 and alat2 >= -90 and alat2 <= 90
    
    if timdif != None:
        
        latitude_increment = 0.0
        longitude_increment = 0.0

# Compute distance travelled -                                    
# speed at first position * half time interval.        
        ad1 = avs * timdif/2.
#Compute components Lat and Long.         
        au1 = ad1 * math.cos(ads * radcon)
        av1 = ad1 * math.sin(ads * radcon)
#Convert from Miles to degrees (adjust Long component for Latitude).   
        aud1 = au1 / 60.0
        avd1 = av1 / 60.0 / math.cos(((alat1+alat2)/2.) * radcon)

    else:
        
        return None, None

    return aud1, avd1

def distr1(inreps, time_differences):
    '''
    Given a list of :class:`.MarineReport` and the calculated time_differences between them, calculate what the 
    distance is between the projected position (based on the reported speed and heading at the current and 
    previous time steps) and the actual position. The observations are taken in time order.
    
    :param inreps: List of :class:`.MarineReport`
    :param time_differences: list of time differences between the MarineReports
    :type inreps: :class:`.MarineReport`
    :type time_differences: list of floats
    :return: list of distances from estimated positions
    :rtype: list of floats
    
    This takes the speed and direction reported by the ship and projects it forwards half a time step, it then projects 
    it forwards another half time step using the speed and direction for the next report, to which the projected location 
    is then compared. The distances between the projeted and actual locations is returned
    '''
#Compute difference between actual and expected positions after
#two observations.
#Each vessel travels at its reported speed and direction for
#half the time interval; the difference (in miles) between
#the calculated and observed positions is calculatered.

    nobs = len(time_differences)
    
    distance_from_est_location = [None]
    
    for i in range(1, nobs):
        
        if (inreps[i].vsi != None and inreps[i-1].vsi != None and
            inreps[i].dsi != None and inreps[i-1].dsi != None and 
            time_differences[i] != None):

#get increment from initial position
            aud1, avd1 = increment_position(inreps[i-1].lat, inreps[i].lat, 
                                            inreps[i-1].vsi, inreps[i-1].dsi, 
                                            time_differences[i])
            aud2, avd2 = increment_position(inreps[i-1].lat, inreps[i].lat, 
                                            inreps[i].vsi, inreps[i].dsi, 
                                            time_differences[i])
#apply increments to the lat and lon at i-1            
            alatx = inreps[i-1].lat + aud1 + aud2
            alonx = inreps[i-1].lon + avd1 + avd2

#calculate distance between calculated position and the second reported position
            discrepancy, side1, side2 = xdist(inreps[i].lat, inreps[i].lon, 
                                              alatx, alonx)
            distance_from_est_location.append(discrepancy)

        else:
#in the absence of reported speed and direction set to None
            distance_from_est_location.append(None)
 
    return distance_from_est_location

def distr2(inreps, time_differences):
    '''
    Given a list of :class:`.MarineReport` and the calculated time_differences between them, calculate what the 
    distance is between the projected position (based on the reported speed and heading at the current and 
    previous time steps) and the actual position. The calculation proceeds from the final, later observation to the 
    first (in contrast to distr1 which runs in time order)
    
    :param inreps: List of :class:`.MarineReport`
    :param time_differences: list of time differences between the reports
    :type inreps: :class:`.MarineReport`
    :type time_differences: list of floats
    :return: list of distances from estimated positions
    :rtype: list of floats
    
    This takes the speed and direction reported by the ship and projects it forwards half a time step, it then projects 
    it forwards another half time step using the speed and direction for the next report, to which the projected location 
    is then compared. The distances between the projeted and actual locations is returned
    '''
#Compute difference between actual and expected positions after
#two observations IN REVERSE ORDER
#Each vessel travels at its reported speed and direction for
#half the time interval; the difference (in miles) between
#the calculated and observed positions is calculatered.
    
    nobs = len(time_differences)
    
    distance_from_est_location = [None]
    
    for i in range(nobs-1, 0, -1):
        
        if (inreps[i].vsi != None and inreps[i-1].vsi != None and
            inreps[i].dsi != None and inreps[i-1].dsi != None and
            time_differences[i]):
 
#get increment from initial position - backwards in time 
#means reversing the direction by 180 degrees
            aud1, avd1 = increment_position(inreps[i].lat, inreps[i-1].lat, 
                                            inreps[i].vsi, 
                                            inreps[i].dsi - 180.,
                                            time_differences[i])
            aud2, avd2 = increment_position(inreps[i].lat, inreps[i-1].lat, 
                                            inreps[i-1].vsi, 
                                            inreps[i-1].dsi - 180.,
                                            time_differences[i])

#apply increments to the lat and lon at i-1            
            alatx = inreps[i].lat + aud1 + aud2
            alonx = inreps[i].lon + avd1 + avd2

#calculate distance between calculated position and the second reported position
            discrepancy, side1, side2 = xdist(inreps[i-1].lat, inreps[i-1].lon, 
                                              alatx, alonx)
            distance_from_est_location.append(discrepancy)

        else:
#in the absence of reported speed and direction set to None
            distance_from_est_location.append(None)

#that fancy bit at the end reverses the array  
    return distance_from_est_location[::-1]

def midpt(inreps, time_differences):
    '''
    Given a list of :class:`.MarineReport` and the corresponding time differences 
    between those reports, interpolate between alternate reports and compare the 
    interpolated location to the actual location. e.g. take difference between 
    reports 2 and 4 and interpolate to get an estimate for the position at the time 
    of report 3. Then compare the estimated and actual positions at the time of 
    report 3.
    
    :param inreps: List of :class:`.MarineReport`
    :param time_differences: list of time differences between the MarineReports
    :type inreps: :class:`.MarineReport`
    :type time_differences: list of floats
    :return: list of distances from estimated positions
    :rtype: list of floats
    
    The calculation linearly interpolates the latitudes and longitudes (allowing for wrapping around the dateline and so on).
    '''    
#    Compute distance from time-proportional position between          
#       outside reported positions to middle reported position.
    nobs = len(inreps)
    
    midpoint_discrepancies = [None]
    
    for i in range(1, nobs-1):
        
#        alat1 = inreps[i-1].lat
#        alon1 = inreps[i-1].lon
#        alat2 = inreps[i].lat
#        alon2 = inreps[i].lon
#        alat3 = inreps[i+1].lat
#        alon3 = inreps[i+1].lon
       
        if time_differences[i] != None and time_differences[i+1] != None:
            
            if time_differences[i] + time_differences[i+1] != 0:
                
                fraction_of_time_diff = \
                time_differences[i]/(time_differences[i]+time_differences[i+1])

            else:
            
                fraction_of_time_diff = 0.0
        
        else:
        
            fraction_of_time_diff = 0.0
        
        lat_diff = inreps[i+1].lat - inreps[i-1].lat
        
        estimated_lat_at_midpt = (inreps[i-1].lat + 
                                  lat_diff * fraction_of_time_diff)
        
        lon_diff = inreps[i+1].lon - inreps[i-1].lon
        if abs(lon_diff) > 200:
            if inreps[i-1].lon < -150:
                lon_diff = inreps[i+1].lon - (360 + inreps[i-1].lon)
                
            if inreps[i+1].lon < -150:
                lon_diff = 360 + inreps[i+1].lon - inreps[i-1].lon
                
        estimated_lon_at_midpt = (inreps[i-1].lon + 
                                  lon_diff * fraction_of_time_diff)

#      Time-proportional position is at AT3 (N/S) and AN3 (E/W)         
#      Reported mid-point will be at    AT4 (N/S) and AN4 (E/W)         
#      Compute distance between time/prop posn and reported mid-point.  
#        SIDE1 is distance travelled North/South                        
        discrepancy, side1, side2 = xdist(inreps[i].lat, inreps[i].lon, 
                                          estimated_lat_at_midpt, 
                                          estimated_lon_at_midpt)

        midpoint_discrepancies.append(discrepancy)

    midpoint_discrepancies.append(None)

    return midpoint_discrepancies

def direction_continuity(dsi, dsi_previous, ship_directions):
    '''
    Check that the reported direction at the previous time step and the actual 
    direction taken are within 60 degree of one another.
    
    :param dsi: heading at current time step in degrees
    :param dsi_previous: heading at previous time step in degrees
    :param ship_directions: calculated ship direction from reported positions in degrees
    :type dsi: float
    :type dsi_previous: float
    :type ship_directions: float
    :return: 10.0 if the difference between reported and calculated direction is greater than 60 degrees, 0.0 otherwise
    :rtype: float
    '''
#Check for continuity of direction                              
#          Error if actual direction is not within 60 degrees           
#            of reported direction of travel or previous reported       
#            direction of travel.
    result = 0.0

    assert dsi in [0, 45, 90, 135, 180, 225, 270, 315, 360, None]
    assert dsi_previous in [0, 45, 90, 135, 180, 225, 270, 315, 360, None]

    if dsi != None and dsi_previous != None and ship_directions != None:        
        if ((abs(dsi - ship_directions) > 60 and
             abs(dsi - ship_directions) < 300 ) or
             (abs(dsi_previous - ship_directions) > 60 and
              abs(dsi_previous - ship_directions) < 300 )):
            result = 10.0

    return result

def speed_continuity(vsi, vsi_previous, speeds):
    '''
    Check if reported speed at this and previous time step is within 10 
    knots of calculated speed between those two time steps
    
    :param vsi: Reported speed in knots at current time step
    :param vsi_previous: Reported speed in knots at previous time step
    :param speeds: Speed of ship calculated from locations at current and previous time steps
    :type vsi: float
    :type vsi_previous: float
    :type speeds: float
    :return: 10 if the reported and calculated speeds differ by more than 10 knots, 0 otherwise
    :rtype: float
    '''

    result = 0.0
    
    if vsi != None and vsi_previous != None and speeds != None:
        if (abs(vsi          - speeds) > 10.00 and 
            abs(vsi_previous - speeds) > 10.00):
            result = 10.0
    
    return result

def check_distance_from_estimate(vsi, vsi_previous, 
                                 time_differences, 
                                 fwd_diff_from_estimated, 
                                 rev_diff_from_estimated):
    '''
    Check that distances from estimated positions (calculated forward 
    and backwards in time) are less than time difference multiplied by 
    the average reported speeds
    
    :param vsi: reported speed in knots at current time step
    :param vsi_previous: reported speed in knots at previous time step
    :param time_differences: calculated time differences between reports in hours
    :param fwd_diff_from_estimated: distance from estimated position, estimates made forward in time 
    :param rev_diff_from_estimated: distance from estimated position, estimates made backward in time
    :type vsi: float
    :type vsi_previous: float
    :type time_differences: float
    :type fwd_diff_from_estimated: float 
    :type rev_diff_from_estimated: float
    :return: 10 if estimated and reported positions differ by more than the reported 
             speed multiplied by the calculated time difference, 0 otherwise
    :rtype: float
    '''
# Quality-control by examining the distance between
# the calculated and reported second position.

    result = 0.0
    if vsi > 0 and vsi_previous > 0 and time_differences > 0:
        
        alwdis = time_differences * ((vsi + vsi_previous)/2.)
        
        if (fwd_diff_from_estimated > alwdis and
            rev_diff_from_estimated > alwdis):
            
            result = 10.0

    return result

def mds_track_check(inreps):

    '''
    Perform one pass of the track check
    
    :param inreps: A list of :class:`.MarineReport` that you want track checked
    :type inreps: :class:`.MarineReport`
    :return: list of QC flags 0 for pass and 1 for fail
    :rtype: integer
    
    This is an implementation of the MDS track check code 
    which was originally written in the 1990s. I don't know why this piece of 
    historic trivia so exercises my mind, but it does: the 1990s! I wish my code 
    would last so long.
    '''

    nobs = len(inreps)

#no obs in, no qc outcomes out
    if nobs == 0:
        return []

#Generic ids get a free pass on the track check
    if qc.id_is_generic(inreps[0].id, inreps[0].year) or nobs < 3:
        qcs = []
        nobs = len(inreps)
        for i in range(0, nobs):
            inreps[i].bad_track = 0
            qcs.append(0)
        return qcs
    
#work out speeds and distances between consecutive 
#points and alternating points
    time_diffs, speeds, distances, ship_directions = calc_1step_speeds(inreps)
    alt_time_diffs, alt_speeds, alt_distances, alt_ship_directions = \
    calc_alternate_step_speeds(inreps)

#what are the mean and mode speeds?
    mean_speed = meansp(speeds)
    modal_speed = modesp(speeds)
#set speed limits based on modal speed
    amax, amaxx, amin = set_speed_limits(modal_speed)

#compare reported speeds and positions if we have them
    forward_diff_from_estimated  = distr1(inreps, time_diffs)
    reverse_diff_from_estimated  = distr2(inreps, time_diffs)
    midpoint_diff_from_estimated =  midpt(inreps, time_diffs)

#do QC
    qcs = [0]
    all_alwdis = [0]
    for i in range(1, nobs-1):
        
        thisqc_a = 0
        thisqc_b = 0

#together these cover the speeds calculate from point i        
        if   speeds[i]   > amax and alt_speeds[i-1] > amax:
            thisqc_a += 1.00
        elif speeds[i+1] > amax and alt_speeds[i+1] > amax:
            thisqc_a += 2.00
        elif speeds[i]   > amax and speeds[i+1]     > amax:
            thisqc_a += 3.00 

# Quality-control by examining the distance 
#between the calculated and reported second position.
        thisqc_b += check_distance_from_estimate(inreps[i].vsi, 
                                                 inreps[i-1].vsi, 
                                                 time_diffs[i], 
                                                 forward_diff_from_estimated[i],
                                                 reverse_diff_from_estimated[i])
#Check for continuity of direction                              
        thisqc_b += direction_continuity(inreps[i].dsi, 
                                         inreps[i-1].dsi, 
                                         ship_directions[i])
#Check for continuity of speed.                                 
        thisqc_b += speed_continuity(inreps[i].vsi, 
                                     inreps[i-1].vsi, 
                                     speeds[i])

#check for speeds in excess of 40.00 knots
        if speeds[i] > 40.00:
            thisqc_b += 10.0

#make the final decision
        if (midpoint_diff_from_estimated[i] > 150.0 and 
            thisqc_a > 0 and 
            thisqc_b > 0):
            qcs.append(1)
            inreps[i].bad_track = 1
        else:
            qcs.append(0)
            inreps[i].bad_track = 0
    
    qcs.append(0)
            
    return qcs

def mds_full_track_check(inreps):
    '''
    Do the full 5-pass track check (which sounds like a kung-fu move requiring years of dedication and eating 
    nothing but rainwater, but is in fact just doing the track check repeatedly)
    
    :param inreps: list of :class:`.MarineReport` to be track checked
    :type inreps: list of :class:`.MarineReport`
    
    The basic 1-pass track check is repeated 5 times, with obs failing track check excluded from subsequent passes.
    '''
    master_qc = mds_track_check(inreps)
    repititions = 0
    
    qcs = master_qc
    
    if len(qcs) > 0:
        while max(qcs) > 0 and repititions < 4:
            tempreps = []
            qc_refs = []

            for i, rep in enumerate(inreps):
                if master_qc[i] == 0:
                    tempreps.append(rep)
                    qc_refs.append(i)
            qcs = mds_track_check(tempreps)

            for i, qc_ref in enumerate(qc_refs):
                master_qc[qc_ref] = qcs[i]
            
            repititions += 1

    for i, rep in enumerate(inreps):
        if master_qc[i] == 0:
            inreps[i].bad_track = 0
        if master_qc[i] == 1:
            inreps[i].bad_track = 1

    return master_qc
