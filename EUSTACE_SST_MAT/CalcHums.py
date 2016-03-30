# Written by Kate Willett 7th Feb 2016

'''
The CalcHums module contains a set of functions for calculating humidity
variables. In theory it should be able to be applied to arrays/objects as
well as scalars.

There are routines for:
specific humidity (REF)
vapour pressure (REF)
relative humidity
wet bulb temperature (REF)
dew point depression

Where vapour pressure is used as part of the equation a pseudo wet bulb 
temperature is calculated. If this is at or below 0 deg C then the ice bulb
equation is used.

ALL NUMBERS ARE RETURNED TO ONE SIGNIFICANT DECIMAL FIGURE.

THIS ROUTINE CANNOT COPE WITH MISSING DATA
'''

import numpy as np
import math

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

    '''
    dp = None

    dp = t - td
	
    return round(dp*10.)/10.
