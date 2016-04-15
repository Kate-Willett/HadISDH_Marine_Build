# Written by Kate Willett 7th Feb 2016

'''
The CalcHums module contains a set of functions for calculating humidity
variables. At present it can only cope with scalars, not arrays.

There are routines for:
specific humidity from dew point temperautre and temperature and pressure
vapour pressure from dew point temperautre and temperature and pressure
relative humidity from dew point temperautre and temperature and pressure
wet bulb temperature from dew point temperautre and temperature and pressure
dew point depression from dew point temperautre and temperature

There are also routines for:
vapour pressure from specific humidity and pressure and temperature
dew point temperature from vapour pressure and temperature and pressure
relative humidity from vapour pressure and temperature and pressure
wet bulb temperature from vapour pressure and dew point temperature and temperature (and pressure?)

Where vapour pressure is used as part of the equation a pseudo wet bulb 
temperature is calculated. If this is at or below 0 deg C then the ice bulb
equation is used.

ALL NUMBERS ARE RETURNED TO ONE SIGNIFICANT DECIMAL FIGURE.

THIS ROUTINE CANNOT COPE WITH MISSING DATA
'''

import numpy as np
import math

#******************************************************************************
def vap(td,t,p):
    '''
    This function calculates a vapour pressure scalar or array
    from a scalar or array of dew point temperature and returns it.
    It requires a sea (station actually but sea level ok for marine data)
    level pressure value. This can be a scalar or an array, even if dewpoint
    temperautre is an array (CHECK). To test whether to apply the ice or water
    calculation a dry bulb temperature is needed. This allows calculation of a 
    pseudo-wet bulb temperature (imprecise) first. If the wet bulb temperature is
    at or below 0 deg C then the ice calculation is used.

    Inputs: 
    td = dew point temperature in degrees C (array or scalar)
    p = pressure at observation level in hPa (array or scalar - can be scalar even if others are arrays)
    t = dry bulb temperature in degrees C (array or scalar)

    Outputs:
    e = vapour pressure in hPa (array or scalar)

    Ref:
    Buck 1981
    Buck, A. L.: New equations for computing vapor pressure and enhancement factor, J. Appl. 
    Meteorol., 20, 1527?1532, 1981.
    Jenson et al 1990
    Jensen, M. E., Burman, R. D., and Allen, R. G. (Eds.): Evapotranspiration and 
    Irrigation Water Requirements: ASCE Manuals and Reports on Engineering Practices No. 
    70, American Society of Civil Engineers, New York, 360 pp., 1990.

    TESTED!
    e = vap(10.,15.,1013.)
    e = 12.3

    '''
    e = None

    # Calculate pseudo-e assuming wet bulb to calculate a pseudo-wet bulb (see wb below)
    f = 1 + (7.*(10**(-4.))) + ((3.46*(10**(-6.)))*p)
    e = 6.1121*f*np.exp(((18.729 - (td/227.3))*td) / (257.87 + td))

    a = 0.000066*p
    b = ((409.8*e) / ((td + 237.3)**2))
    w = (((a*t) + (b*td)) / (a + b))

    # Now test for whether pseudo-wetbulb is above or below/equal to zero
    # to establish whether to calculate e with respect to ice or water
    # recalc if ice
    if (w <= 0.0):
        f = 1 + (3.*(10**(-4.))) + ((4.18*(10**(-6.)))*p)
        e = 6.1115*f*np.exp(((23.036 - (td/333.7))*td) / (279.82+td))
	     
    return round(e*10.)/10.

#***************************************************************************
def vap_from_sh(sh,p):
    '''
    This function calculates a vapour pressure scalar or array
    from a scalar or array of specific humidity and pressure and returns it.
    It requires a sea (station actually but sea level ok for marine data)
    level pressure value. This can be a scalar or an array, even if specific humidity
    is an array (CHECK). 

    Inputs: 
    sh = specific humidity in g/kg (array or scalar)
    p = pressure at observation level in hPa (array or scalar - can be scalar even if others are arrays)

    Outputs:
    e = vapour pressure in hPa (array or scalar)

    Ref:
    Peixoto & Oort, 1996, Ross & Elliott, 1996
    Peixoto, J. P. and Oort, A. H.: The climatology of relative humidity in the atmosphere, J. 
    Climate, 9, 3443?3463, 1996.

    TESTED!
    e = vap_from_sh(7.6,1013.)
    e = 12.3

    '''
    e = None

    e = ((sh/1000.) * p) / (0.622 + (0.378 * (sh/1000.)))
	     
    return round(e*10.)/10.

#****************************************************************************	
def sh(td,t,p):
    '''
    This function calculates a specific humidity scalar or array
    from a scalar or array of vapour pressure and returns it.
    It requires a sea (station actually but sea level ok for marine data)
    level pressure value. This can be a scalar or an array, even if vapour 
    pressure is an array (CHECK).   
    
    Inputs:	
    td = dew point temperature in degrees C (array or scalar)
    t = dry bulb temperature in degrees C (array or scalar)    
    p = pressure at observation level in hPa (array or scalar - can be scalar even if others are arrays)
    	GIVES: e = vapour pressure in hPa (array or scalar) - see vap()
	
    Outputs:
    q = specific humidity in g/kg (array or scalar)
	
    Ref:
    Peixoto & Oort, 1996, Ross & Elliott, 1996
    Peixoto, J. P. and Oort, A. H.: The climatology of relative humidity in the atmosphere, J. 
    Climate, 9, 3443?3463, 1996.

    TESTED!
    sh = sh(10.,15.,1013.)
    sh = 7.6

    '''
    q = None

    e = None

    # Calculate pseudo-e assuming wet bulb to calculate a pseudo-wet bulb (see wb below)
    f = 1 + (7.*(10**(-4.))) + ((3.46*(10**(-6.)))*p)
    e = 6.1121*f*np.exp(((18.729 - (td/227.3))*td) / (257.87 + td))

    a = 0.000066*p
    b = ((409.8*e) / ((td + 237.3)**2))
    w = (((a*t) + (b*td)) / (a + b))

    # Now test for whether pseudo-wetbulb is above or below/equal to zero
    # to establish whether to calculate e with respect to ice or water
    # recalc if ice
    if (w <= 0.0):
        f = 1 + (3.*(10**(-4.))) + ((4.18*(10**(-6.)))*p)
        e = 6.1115*f*np.exp(((23.036 - (td/333.7))*td) / (279.82+td))

    q = 1000.*((0.622*e) / (p - ((1 - 0.622)*e)))
	
    return round(q*10.)/10.

#*******************************************************************************
def rh(td,t,p):
    '''
    This function calculates a relative humidity scalar or array
    from a scalar or array of vapour pressure and temperature and returns 
    it. It calculates the saturated vapour pressure from t.
    It requires a sea (station actually but sea level ok for marine data)
    level pressure value. This can be a scalar or an array, even if vapour pressure
    is an array (CHECK). To test whether to apply the ice or water
    calculation a dewpoint and dry bulb temperature are needed. We can assume that the
    dry bulb t is the same as the wet bulb t at saturation. This allows 
    calculation of a pseudo-wet bulb temperature (imprecise) first. If the
    wet bulb temperature is at or below 0 deg C then the ice calculation is used.
   
    Inputs:	
    td = dew point temperature in degrees C (array or scalar)
    p = pressure at observation level in hPa (array or scalar - can be scalar even if others are arrays)
    t = dry bulb temperature in degrees C (array or scalar)
    	GIVES: e = vapour pressure in hPa (array or scalar)
    	GIVES: es = saturated vapour pressure in hPa (array or scalar)

    Outputs:
    r = relative humidity in %rh (array or scalar)

    Ref:

    TESTED!
    rh = rh(10.,15.,1013.)
    rh = 72.0
    
    '''
    r = None

    e = None

    # Calculate pseudo-e assuming wet bulb to calculate a pseudo-wet bulb (see wb below)
    f = 1 + (7.*(10**(-4.))) + ((3.46*(10**(-6.)))*p)
    e = 6.1121*f*np.exp(((18.729 - (td/227.3))*td) / (257.87 + td))

    a = 0.000066*p
    b = ((409.8*e) / ((td + 237.3)**2))
    w = (((a*t) + (b*td)) / (a + b))

    # Now test for whether pseudo-wetbulb is above or below/equal to zero
    # to establish whether to calculate e with respect to ice or water
    # recalc if ice
    if (w <= 0.0):
        f = 1 + (3.*(10**(-4.))) + ((4.18*(10**(-6.)))*p)
        e = 6.1115*f*np.exp(((23.036 - (td/333.7))*td) / (279.82+td))

    es = None

    # Calculate pseudo-es assuming wet bulb to calculate a pseudo-wet bulb (see wb below)
    # USING t INSTEAD OF td FOR SATURATED VAPOUR PRESSURE (WET BULB T = T AT SATURATION)
    f = 1 + (7.*(10**(-4.))) + ((3.46*(10**(-6.)))*p)
    es = 6.1121*f*np.exp(((18.729 - (t/227.3))*t) / (257.87 + t))

    a = 0.000066*p
    b = ((409.8*es) / ((t + 237.3)**2)) # t here rather than td because for es, t==td
    w = (((a*t) + (b*t)) / (a + b)) # second t is t here rather than td because for ex, t==td

    # Now test for whether pseudo-wetbulb is above or below/equal to zero
    # to establish whether to calculate e with respect to ice or water
    # recalc if ice
    if (w <= 0.0):
        f = 1 + (3.*(10**(-4.))) + ((4.18*(10**(-6.)))*p)
        es = 6.1115*f*np.exp(((23.036 - (t/333.7))*t) / (279.82+t))
	     	
    r = (e / es)*100.

    return round(r*10.)/10.

#**************************************************************************	
def wb(td,t,p):
    '''
    This function calculates a wet bulb temperature scalar or array
    from a scalar or array of vapour pressure and temperature and
    dew point temperature and returns it. 
    It requires a sea (station actually but sea level ok for marine data)
    level pressure value. This can be a scalar or an array, even ifvapour pressure
    is an array (CHECK). To test whether to apply the ice or water
    calculation a dewpoint and dry bulb temperature are needed. This allows 
    calculation of a pseudo-wet bulb temperature (imprecise) first. If the
    wet bulb temperature is at or below 0 deg C then the ice calculation is used.

    Inputs:	
    td = dew point temperature in degrees C (array or scalar)
    t = dry bulb temperature in degrees C (array or scalar)
    p = pressure at observation level in hPa (array or scalar - can be scalar even if others are arrays)
    	GIVES: e = vapour pressure in hPa (array or scalar)

    Outputs:
    w = wet bulb temperature in degrees C (array or scalar)

    Ref:
    Jenson et al 1990
    Jensen, M. E., Burman, R. D., and Allen, R. G. (Eds.): Evapotranspiration and 
    Irrigation Water Requirements: ASCE Manuals and Reports on Engineering Practices No. 
    70, American Society of Civil Engineers, New York, 360 pp., 1990.

    TESTED!
    wb = wb(10.,15.,1013)
    wb = 12.2

    '''
    
    w = None

    e = None

    # Calculate pseudo-e assuming wet bulb to calculate a pseudo-wet bulb (see wb below)
    f = 1 + (7.*(10**(-4.))) + ((3.46*(10**(-6.)))*p)
    e = 6.1121*f*np.exp(((18.729 - (td/227.3))*td) / (257.87 + td))

    a = 0.000066*p
    b = ((409.8*e) / ((td + 237.3)**2))
    w = (((a*t) + (b*td)) / (a + b))

    # Now test for whether pseudo-wetbulb is above or below/equal to zero
    # to establish whether to calculate e with respect to ice or water
    # recalc if ice
    if (w <= 0.0):
        f = 1 + (3.*(10**(-4.))) + ((4.18*(10**(-6.)))*p)
        e = 6.1115*f*np.exp(((23.036 - (td/333.7))*td) / (279.82+td))

    # Now calculate a slightly better w
    a = 0.000066*p
    b = ((409.8*e) / ((td + 237.3)**2))

    w = (((a*t) + (b*td)) / (a + b))

    return round(w*10.)/10.

#*********************************************************************
def dpd(td,t):
    '''
    This function calculates a dew point depression scalar or array
    from a scalar or array of temperature and dew point temperature and returns it.

    Inputs:	
    td = dew point temperature in degrees C (array or scalar)
    t = dry bulb temperature in degrees C (array or scalar)

    Outputs:
    dp = dew point depression in degrees C (array or scalar)

    Ref:

    TESTED!
    dpd = dpd(10..,15.)
    dpd = 5.0

    '''
    dp = None

    dp = t - td
	
    return round(dp*10.)/10.

#*********************************************************************
def td_from_vap(e,p,t):
    '''
    This function calculates a dew point depression scalar or array
    from a scalar or array of vapour pressure and pressure and returns it.
    It also requires temperature to check whether the wet bulb temperature 
    is <= 0.0 - if so the ice bulb calculation is used.
    
    Inputs:	
    e = vapour pressure in hPa (array or scalar)
    t = dry bulb temperature in degrees C (array or scalar)
    p = pressure at observation level in hPa (array or scalar - can be scalar even if others are arrays)

    Outputs:
    dp = dew point depression in degrees C (array or scalar)

    Ref:
    Buck 1981
    Buck, A. L.: New equations for computing vapor pressure and enhancement factor, J. Appl. 
    Meteorol., 20, 1527?1532, 1981.
    Jenson et al 1990
    Jensen, M. E., Burman, R. D., and Allen, R. G. (Eds.): Evapotranspiration and 
    Irrigation Water Requirements: ASCE Manuals and Reports on Engineering Practices No. 
    70, American Society of Civil Engineers, New York, 360 pp., 1990.
    
    TESTED!
    td = td_from_vap(12.3,1013.,15.)
    td = 10.0

    '''
    td = None
    
    # First calculate an estimated dew point T
    f = 1 + (7.*10.**(-4.)) + ((3.46*10.**(-6.)) * p)

    a = 1
    b = (227.3 * np.log(e / (6.1121*f))) - (18.729 * 227.3)
    c = (257.87 * 227.3 * np.log(e / (6.1121 * f)))

    td = (-b - np.sqrt(b**2 - (4 * a * c))) / (2 * a)

    # Now calculate an estimated wet bulb T
    a = 0.000066 * p
    b = ((409.8 * e) / ((td + 237.3)**2))
    w = (((a * t) + (b * td)) / (a + b))
    
    # Now test for whether pseudo-wetbulb is above or below/equal to zero
    # to establish whether to calculate td with respect to ice or water
    # recalc if ice
    if (w <= 0.0):
        f = 1 + (3.*10.**(-4.)) + ((4.18*10.**(-6.)) * p)

        a = 1
        b = (333.7 * np.log(e / (6.1115 * f))) - (23.036 * 333.7)
        c = (279.82 * 333.7 * np.log(e / (6.1115 * f)))

        td = (-b - np.sqrt(b**2 - (4 * a * c))) / (2 * a)
    
    return round(td*10.)/10.
