# Written by Kate Willett 6th April 2016

'''
The HeightCorrect module contains all of the code and flow for adjusting the wind, air temperature and specific humidity to
10m. This is based entirely on the thesis of Berry 2009: Berry, D., 2009: Surface forcing of the North Atlantic: accuracy 
and variability, University of Southampton, 176p. The main other references are:

NOCSv2.0 methodology - which we base our height corrections on
Berry, D. I. and E. C. Kent, 2011: Air-sea fluxes from ICOADS: the construction of a new gridded dataset with uncertainty 
estimates. International Journal of Climatology, 31, 987-1001.

Drag coefficient z0
Smith, S. D, 1980: Wind stress and heat flux over the ocean in glae force winds. Journal of Physical Oceanography, 10,
709-726.

Heat and Moisture coefficient z0t and z0q
Smith, S. D, 1988. Coefficients for sea surface wind stress, heat flux and wind profiles as a function of wind speed and 
temperature. Journal of Geophysical Research, 93, 15467-15472.

WGASF 2000 and then Berry 2009 for the scaling parameters u*, t* and q*

WGASF 2000 for the dimensionless profiles PHIm, PHIt and PHIq and Smith 1980, 1988 for ALPHAs = 16, BETAs = 1/4, GAMMAs = 5
WGASF, 2000: Intercomparison and validation of ocean-atmosphere energy flux fields
- Final report of the Joint WCRP/SCOR Working Group on Air-Sea Fluxes.
WCRP-112, WMO/TD-1036. P. K. Taylor, Ed., 306 pp.

An alternative / easier approximation for the dimensionless stability parmeter?
Stull, R. B., 1988: An Introduction to Boundary Layer Meteorology Klewer Academic Publishers, 666 pp.


The whole process has to be iterated for each ob, first assuming a stable atmospheric profile, then assessing the stability,
then reaplying using the correct atmospheric stability measure.

REQUIRED VARIABLES
zu, zt and zq = observation height for wind, temperature and specific humidity (m)
z10 = desired height of 10m
uz = wind speed at obs height (m)
tz = air temperature at obs height (deg C?) - already corrected for solar bias in an ideal world
qz = specific humidity at obs height (g/kg?) - already corrected for screen bias
sst = sea surface temperature
p = actual pressure

CONSTANTS
k = von Karman constand = 0.41
g = acelaration due to gravity 9.81 ms-1
epsilon = 0.622
z0t = neutral stability heat transfer coeffieient = 0.001
z0q = neutral stability moisture transfer coefficient = 0.0012

VARIABLES TO ESTIMATE THROUGH ITERATION
L = the Monin-Obukhov Length (1m to 200m - STABLE?) (-1 to 150m - UNSTABLE?) INFINITY for NEUTRAL!!!!
u* = friction velocity (0.05 (STABLE) to 0.3m (UNSTABLE))
u10n = wind speed at 10m in neutral conditions
z0 = roughness length (0.001 to 1m) - shouldn't be much larger than 0.01m over ocean
Ym = stability correction for momentum (-1 (UNSTABLE) to 3.5 (STABLE), 0 = NEUTRAL
Yh = stability correction for heat (
Yt = stability correction for temperature (
PHIm = 
PHIt = 
PHIh = 
w'Tv' = buoyancy flux - K m s-1 (Kelvin per m per s)

VARIABLES TO CALCULATE
Tv = virtual temperature (in Kelvin)

Note '$' implies an estimated parameter!!!

1. Obtain wind, temperature and specific humidity at the surface u0, t0 and q0 as 0, sst and 0.98*qsat(esat(sst))

 2. Calculate virtual potential temperature Tv from tz (in Kelvin?), qz (in g/g), and epsilon (0.622)
    Tv = tz(1+qz/epsilon) / (1+qz)   NOTE THIS SHOULD BE MIXING RATIO g(water)/q(dry air) - v sim to q (g(water)/g(moist air))

 3. Estimate friction velocity u*$ assuming NEUTRAL conditions from k, z, z0$, Ym$, uz and u0 - Ym is between 0 to -4 in STABLE conditions (Berry 2009 Fig 2.1)
     - u*$ = k(ln(z/z0$) - Ym$)^-1 * (uz - u0)
     - ASSUME Ym$ = 0 to start with?
     - ASSUME z0$ is 0.0002 to start with? Wikipedia says that is a fair assumption for stable conditions over a smooth sea.
     - COULD WE ASSUME A STARTING VALUE FOR u* and L?
         
 *4. Estimate the Monin-Obukhov length L$ assuming neutral conditions from u*$, Tv, g, k, w' and Tv' (w' and Tv' are 0/-ve under STABLE atmosphere!)
     Could this be estimated from first estimating stability parameter little_zeta$ from -u*$^3, Tv, k and z? Then L$ = z/little_zeta$ - NO
     - L = - (u*$^3*Tv) / (gkw'$Tv'$) (-ve = unstable, +ve = stable)
     - w'Tv +ve = UNSTABLE, w'Tv' -ve = STABLE, close to zero = NEUTRAL

 5. Estimate wind speed at 10m u10n$ assuming NEUTRAL conditions from uz, u*$, k, zu, Ym$ and L$
    - u10n = uz - (u*$/k) * (ln(zu/10) - Ym$(zu/L$) + Ym$(10/L)) 
    - NEUTRAL ? u10n = uz - (u*$/k) * (ln(zu/10) - 0 + 0) (Ym$ is zero in neutral!)
 
 
 6. Estimate roughness length/neutral stability drag coefficient z0$ from Smith constants and u10n$

 7a. Estimate dimensionless stability parameter little_zeta$ assuming STABLE conditions from height z and L$ (should be +ve in STABLE conditions! - is it here?)
 7b. Can this actually be estimated using Stull 1988 little_zera$ = -u*$^3 / kz ???? MUCH EASIER!!! (no need for steps 2 or 4!!!)

 8. Estimate dimensionless profile PHIm$ assuming STABLE conditions depending on little_zeta$ < 0 > little_zeta$ and from little_zeta$, ALPHAs 
 or GAMMAs and BETAs- (should be >1 in stable conditions!!! - are they here?)

 9. Estimate stability corrections Ym$ from integrating PHIm$ over z in small steps - (should be -ve (0 to -4) in stable conditions - is it here?)

 10. Repeat 3 to 7 until you resolve on a non-varying Ym (still not sure what to do about w'Tv' in the L calculation unless using option 7b!)
 
  11. Repeat step 3. to obtain a better u*$ from k, z, z0$  Ym uz and u0
  
  12. Repeat step 4. to obtain a better u10$ from uz, u*$, k, zu, Ym, zu, L
  
  13. Repeat step 5. to obtain a better z0$ from Smith constants and u10$
  
  14. Repeat steps 11 to 13 until you resolve on non-varying u*
  
    15. Calculate dimensionless profiles for temperature and humidity PHIt and PHIq depending on little_zeta$ from PHIm
  
     16. Calculate stability corrections for temperature and humidity Yt and Yq from PHIt/PHIq and z and integration

      17. Calculate characteristic temperature and characteristic specific humdidity t* and q* from k, z, z0t/z0q, Yt/Yq, tz/qz and t0/q0
  
       18. Repeat step 4. to obtain L from u*, Tv, g, k, w' and Tv' (still not sure what to do about w'Tv' in the L calculation)
           w'Tv' is the vertical flux -ve when stable, +ve when unstable
   
        19. Assuming we don't need to iterate for ever (and that PHIs and Ys are now stable?), calculate u10, t10 and q10 from uz/tz/qz, u*/t*/q*, k, zu/zt/zq, 
	    Ym/Yt/Yq and L


Could also try having assumptions for stable (SST<AT), neutral(SST=AT) and unstable(SST>AT) conditions.
u0 = 0.
t0 = SST
q0 = qsat(SST)*0.98

L$ = the Monin-Obukhov Length (50 - STABLE?) (-50m - UNSTABLE?) INFINITY for NEUTRAL!!!!
z0$ = roughness length (0.001 to 1m) - shouldn't be much larger than 0.01m over ocean
little_zeta = stability parameter - calculate from z and L
PHIm = dimensionless profiles - calculate depending on stability from alphas, little_zeta, beta (UNSTABLE) or gammas, little_zeta (STABLE)
PHIt = dimensionless profiles - calculate depending on stability - calculate from PHIm depending on stability
PHIh = dimensionless profiles - calculate depending on stability - same as PHIt
Ym = stability correction for momentum 0 = NEUTRAL [(-1 (UNSTABLE) to 2 (STABLE)] - or calculate from PHIm depending on stability 
Yt = stability correction for temperature - calculate from PHIt (UNSTABLE) or PHIm (STABLE)
Yh = stability correction for heat - same as Yt
u* = friction velocity (0.1 (STABLE) to 0.2m (UNSTABLE)) - calculate from k, z, z0$, Ym (0 in NEUTRAL), uz, u0
??? u10n = wind speed at 10m in neutral conditions - calculate??? only needed for calculating Z0
u10 = wind speed at 10m - calculate from uz, u*, k, zu (NEUTRAL), uz, u*, k, zu, Ym, L$ (STABLE or UNSTABLE)
t* = characteristic temperature - calculate from k, zt, z0t, Yt (0 in NEUTRAL), tz, t0
q* = characteristic specific humidity - calculate from k, zq, z0q, Yq (0 in NEUTRAL), qz, q0
t10 = temperature at 10m - calculate from tz, t*, k, zt (NEUTRAL), tz, t*, k, zt, Yt, L$ (STABLE or UNSTABLE)
q10 = temperature at 10m - calculate from qz, q*, k, zq (NEUTRAL), qz, q*, k, zq, Yq, L$ (STABLE or UNSTABLE)

Try this for a few different starting points of L and z0 to see how much difference it makes, for a range of stabilities and climates

This now works and produces sensible values

>import HeightCorrect as hc
>u10,t10,q10 = hc.run_heightcorrect_proxyLz0(10.,15.,8.,5.,20.,18.,18.) # sst, at, shu, u, zu, zt, zq
>(4.5408290319390296, 14.615283569135769, 7.9568606550888683)
'''

import numpy as np
import math
import CalcHums as ch
import copy as copy

#********************************************************************************
def get_surface_values(sst):
    '''
    Works out surface values of wind, temperature and specific humidity
    
    Reads in: 
      sst - sea surface temperature (deg C)
      
    Returns  
      u0 = 0. - wind speed
      t0 = SST - air temperature
      q0 = qsat(SST)*0.98 - specific humidity
    
    u0,t0,q0 = get_surface_values(sst)
    
    TESTED!!!
    
    '''
    u0 = 0.0
    	
    t0 = sst
    
    q0 = 0.98*(ch.sh(sst,sst,1013.0)) # ideally would use the climslp but annoying to read in and match up and OBS slp not always there

    return u0,t0,q0

#********************************************************************************
def get_little_zeta(zu,L):
    '''
    Works out stability parameter
    
    Reads in: 
      zu - height of anemometer (m)
      L - Monin-Obukhov length (m)
      
    Returns  
      little_zeta - stability parameter (dimensionless: -ve = UNSTABLE, +ve = STABLE)
                  - over ocean generally ranges between -1 and 0.5 (Berry 2009)
		  - at zu = 20 and L -50 to 50 little_zeta is -0.4 to 0.4
    
    little_zeta = get_little_zeta(zu,L)
    
    TESTED!!!
    
    '''
    little_zeta = zu/L
    	
    return little_zeta

#********************************************************************************
def get_phis(little_zeta):
    '''
    Works out the dimensionless profiles
    
    Reads in: 
      little_zeta - stability parameter (dimensionless: -ve = UNSTABLE, +ve = STABLE)
      
    Returns  
      PHIm - dimensionless profile for momentum
      PHIt - dimensionless profile for temperature
      PHIh - dimensionless profile for heat
    
    PHIm,PHIt,PHIh = get_phis(little_zeta)
    
    TESTED!!!
    These appear to vary between PHIm = 0.49, PHIt/PHIh = 0.24 (UNSTABLE little_zeta = -1) and PHIm/PHIt/PHIh = 3.5 (STABLE little_zeta = 0.5)
    These appear to vary between PHIm = 0.61, PHIt/PHIh = 0.37 (UNSTABLE little_zeta = -0.4) and PHIm/PHIt/PHIh = 3.0 (STABLE little_zeta = 0.4)
    
    '''
    # set up the required constants Smith (1980,1988), Large and Pond (1981) Berry (2009)
    alpha_s = 16.
    beta = 1./4.
    gamma_s = 5.
    
    # calculate depending on stability
    if (little_zeta < -0.1): # UNSTABLE
        PHIm = (1. - (alpha_s*little_zeta))**(-beta)
	PHIt = PHIm**2
	PHIh = copy.copy(PHIt)
    elif (little_zeta > 0.1): # STABLE
        PHIm = (1. + (gamma_s*little_zeta))
	PHIt = copy.copy(PHIm)
	PHIh = copy.copy(PHIt)
    else: # NEUTRAL
        PHIm = 1.
	PHIt = 1.
	PHIh = 1.
    	
    return PHIm,PHIt,PHIh

#********************************************************************************
def get_psis(little_zeta,PHIm,PHIt,PHIh):
    '''
    Works out the stability corrections
    
    Reads in: 
      little_zeta - stability parameter (dimensionless: -ve = UNSTABLE, +ve = STABLE)
      PHIm - dimensionless profile for momentum
      PHIt - dimensionless profile for temperature
      PHIh - dimensionless profile for heat
      
    Returns  
      Ym - stability correction for momentum
      Yt - stability correction for temperature
      Yh - stability correction for heat
    
    Ym,Yt,Yh = get_psis(little_zeta,PHIm,PHIt,PHIh)
    
    TESTED!!!
    These appear to vary between Ym = 1.12, Yt/Yh = 1.88 (UNSTABLE little_zeta = -1) and Ym/Yt/Yh = -2.5 (STABLE little_zeta = 0.5)
    These appear to vary between Ym = 0.70, Yt/Yh = 1.24 (UNSTABLE little_zeta = -0.4) and Ym/Yt/Yh = -2.0 (STABLE little_zeta = 0.4)
    
    '''
        
    # calculate depending on stability
    if (little_zeta < -0.1): # UNSTABLE
        Ym = 2 * np.log((1+(PHIm**-1))/2.) + np.log((1+(PHIm**-2))/2.) - 2*np.arctan(PHIm**-1) + (np.pi/2.)  # not 100% sure about the np.arctan(PHIm**-1) notation was 2tan**-1 PHIm**-1
	Yt = 2 * np.log((1+(PHIt**-1))/2.)
	Yh = copy.copy(Yt)
    elif (little_zeta > 0.1): # STABLE
        Ym = 1. - PHIm
	Yt = copy.copy(Ym)
	Yh = copy.copy(Yt)
    else: # NEUTRAL
        Ym = 0.
	Yt = 0.
	Yh = 0.
    	
    return Ym,Yt,Yh

#********************************************************************************
def get_value_star(k,zx,z0x,Yx,x,x0):
    '''
    Works out the friction velocity/characteristic temperaure/characteristic specific humidity (*)
    
    Reads in: 
      little_zeta - stability parameter (dimensionless: -ve = UNSTABLE, +ve = STABLE)
      k - von Karman constant
      zx - height of anemometer/instrument (m)
      z0x - transfer coefficient for momentum (roughness length), temperature or moisture
      Yx - stability correction
      x - observed value at height (m/s, g/kg or deg C) NOT KELVIN?
      x0 - observed value at surface (m/s, g/kg or deg C) NOT KELVIN?
      
    Returns  
      x_star - friction velocity/characteristic temperaure/characteristic specific humidity
    
    u_star = get_value_star(k,zu,z0,Ym,u,u0)
    t_star = get_value_star(k,zt,z0t,Yt,t,t0)
    q_star = get_value_star(k,zq,z0q,Yh,q,q0)
    
    TESTED!!!
    For zu=20, z0=0.005, u=1/u=5/u=10 (~1mph,10mph,>30mph)
    This appears to vary between u* = 0.06/0.29/0.57 (UNSTABLE little_zeta = -1) and u* = 0.04/0.12/0.34(STABLE little_zeta = 0.5)
    This appears to vary between u* = 0.05/0.27/0.54 (UNSTABLE little_zeta = -0.4) and u* = 0.04/0.20/0.40 (STABLE little_zeta = 0.4)

    For zt=18, z0t=0.001, t=-20/t=0./t=20 t0=0/t0=0/t0=0  NOTE: doesn't matter what actual t and t0 are - just the difference between!
    This appears to vary between t* = -1.04/0.0/1.04 (UNSTABLE little_zeta = -1) and t* = -0.67/0.0/0.67 (STABLE little_zeta = 0.5)
    This appears to vary between t* = -0.96/0.0/0.96 (UNSTABLE little_zeta = -0.4) and t* = -0.70/0.0/0.70 (STABLE little_zeta = 0.4)

    For zq=18, z0q=0.0012, q=8/q=8/q=8 q0=0/8/16 NOTE: q0 cannot be MUCH lower than q because q0 is saturated at a tempererature that cannot be very low compared to air T
    This appears to vary between q* = 0.42/0.0/-0.42 (UNSTABLE little_zeta = -1) and q* = 0.27/0.0/-0.27 (STABLE little_zeta = 0.5)
    This appears to vary between q* = 0.39/0.0/-0.39 (UNSTABLE little_zeta = -0.4) and q* = 0.28/0.0/-0.28 (STABLE little_zeta = 0.4)
    
    '''

    x_star = k * (np.log(zx / z0x) - Yx)**-1 * (x - x0)        
    	
    return x_star

#********************************************************************************
def get_heightcorrected(x,x_star,k,zx,Yx,L):
    '''
    Works out the variable converted to 10m height
    
    Reads in: 
      x - observed value at height (m/s, g/kg or deg C) NOT KELVIN?
      x_star - friction velocity/characteristic temperaure/characteristic specific humidity
      k - von Karman constant
      zx - height of anemometer/instrument (m)
      Yx - stability correction
      L - Monin-Obukhov length (m)
      
    Returns  
      x10 - value converted to 10m (m/s, g/kg or deg C) NOT KELVIN?
    
    u10 = get_heightcorrected(u,u_star,k,zu,Ym,L)
    at10 = get_heightcorrected(at,t_star,k,zt,Yt,L)
    shu10 = get_heightcorrected(shu,q_star,k,zq,Yh,L)
    
    TESTED!!!

    For zu=20, z0=0.005, u=1/u=5/u=10 (~1mph,10mph,>30mph)
    This appears to vary between u* = 0.87/4.35/8.72 (UNSTABLE little_zeta = -1) and u* = 0.88/4.65/9.01 (STABLE little_zeta = 0.5)
    This appears to vary between u* = 0.90/4.45/8.90 (UNSTABLE little_zeta = -0.4) and u* = 0.89/4.47/8.93 (STABLE little_zeta = 0.4)

    For zt=18, z0t=0.001, t=-20/t=0./t=20 t0=0/t0=0/t0=0  NOTE: last element in UNSTABLE (AT>>SST) and first element in STABLE (AT<<SST) are a bit dodge 
    This appears to vary between t* = -17.75/0.0/17.75(SCREWY) (UNSTABLE little_zeta = -1) and t* = -18.39(SCREWY)/0.0/18.39 (STABLE little_zeta = 0.5)
    This appears to vary between t* = -18.16/0.0/18.16(SCREWY) (UNSTABLE little_zeta = -0.4) and t* = -18.45(SCREWY)/0.0/18.45 (STABLE little_zeta = 0.4)
    NOTE: where SST == AT - there is no change to temperature!!!

    For zq=18, z0q=0.0012, q=8/q=8/q=8 q0=0/8/16 NOTE: q0 cannot be MUCH lower than q because q0 is saturated at a tempererature that cannot be very low compared to air T
    This appears to vary between q* = 7.09(UNLIKELY)/8.0/8.91 (UNSTABLE little_zeta = -1) and q* = 7.88(UNLIKELY)/0.0/8.12 (STABLE little_zeta = 0.5)
    This appears to vary between q* = 7.25(UNLIKELY)/8.0/8.75 (UNSTABLE little_zeta = -0.4) and q* = 7.82(UNLIKELY)/0.0/8.18 (STABLE little_zeta = 0.4)
    
    So - we're getting at least plausible values out but now we need to test sensitivity to the things we have estimated: 
      L
      u*/t*/q*
      Ym/Yt/Yh
    We have also estimated many other things but these look most important in that they appear in the final calculation. If we can prove that +/- some value doesn't make much difference
    then we're ok. Ideally - this would be the asumption of L = either -50 ro 50! This is because little_zeta, PHIs, Ys all depend on L - and u*/t*/q* really.
                    
    '''

    x10 = x - (x_star/k) * (np.log(zx/10.) - Yx*(zx/L) + Yx*(10./L))     
    	
    return x10

#********************************************************************************
# MAIN #
def run_heightcorrect_proxyLz0(sst,at,shu,u,zu,zt,zq):
    '''
    Code to produce u,t,q converted to 10m using assumed L and z0 depending on stability
    
    Reads in:
      sst - sea surface temperature (deg C)
      at - air temperature (deg C)
      shu - specific humidity (g/kg)
      u - wind speed (m/s)
      zu = height of anemometer (m)
      zt = height of instrument (m0)
      zq = height of instrument (m)
      
    IF SST IS MISSING (test for sst < -60 or > 60) USE AT
    
    Constants:
    k = 0.41 # von Karman constant
    z0 = we have set this to 0.005 (Stull 1988 says between 0.001 and 0.01 for ocean)
    z0t = 0.001 # neutral stability heat transfer coeffieient Smith 1988
    z0q = 0.0012 # neutral stability moisture transfer coefficient Smith 1988
    For the PHIs (dimensionless profiles):
    alpha_s = 16.# Smith (1980,1988), Large and Pond (1981) Berry (2009)
    beta = 1./4. # Smith (1980,1988), Large and Pond (1981) Berry (2009)
    gamma_s = 5. # Smith (1980,1988), Large and Pond (1981) Berry (2009)

    Works out surface values: get_surface_values:
        u0 = 0.
        t0 = SST
        q0 = qsat(SST)*0.98
    
    Depending on stability, assumes L and z0
        L = the Monin-Obukhov Length (50 - STABLE?) (-50m - UNSTABLE?) INFINITY for NEUTRAL!!!!
        z0 = roughness length (0.001 to 1m) - shouldn't be much larger than 0.01m over ocean
	
    Calculates:	
        little_zeta = stability parameter - calculate from zu and L: get_little_zeta
        The PHIs: get_phis
	    PHIm = dimensionless profiles - calculate depending on stability from alphas, little_zeta, beta (UNSTABLE) or gammas, little_zeta (STABLE)
            PHIt = dimensionless profiles - calculate depending on stability - calculate from PHIm depending on stability
            PHIh = dimensionless profiles - calculate depending on stability - same as PHIt
        The Ys: get_psis
            Ym = stability correction for momentum 0 = NEUTRAL [(-1 (UNSTABLE) to 2 (STABLE)] - or calculate from PHIm depending on stability 
            Yt = stability correction for temperature - calculate from PHIt (UNSTABLE) or PHIm (STABLE)
            Yh = stability correction for heat - same as Yt
        u* = friction velocity (0.1 (STABLE) to 0.2m (UNSTABLE)) - calculate from k, z, z0$, Ym (0 in NEUTRAL), uz, u0: get_value_star
        t* = characteristic temperature - calculate from k, zt, z0t, Yt (0 in NEUTRAL), tz, t0: get_value_star
        q* = characteristic specific humidity - calculate from k, zq, z0q, Yq (0 in NEUTRAL), qz, q0: get_value_star
    ??? u10n = wind speed at 10m in neutral conditions - calculate??? only needed for calculating Z0
        u10 = wind speed at 10m - calculate from uz, u*, k, zu (NEUTRAL), uz, u*, k, zu, Ym, L$ (STABLE or UNSTABLE): get_heightcorrected
        t10 = temperature at 10m - calculate from tz, t*, k, zt (NEUTRAL), tz, t*, k, zt, Yt, L$ (STABLE or UNSTABLE): get_heightcorrected
        q10 = temperature at 10m - calculate from qz, q*, k, zq (NEUTRAL), qz, q*, k, zq, Yq, L$ (STABLE or UNSTABLE): get_heightcorrected
    
    '''
    # Check if sst is missing (it could be) - use at instead (NOT IDEAL!!!! - PROBABLY WANT TO FLAG FOR INCREASED UNCERTAINTY)
    if ((sst < -60.) | (sst > 60)):
        sst = at

    # Get the Surface values
    u0, t0, q0 = get_surface_values(sst)
    
    # Work out stability dependent assumptions for L and z0
    # Berry 2009 states that typical values of little_zeta over oceans are -1 to 0.5
    # little_zeta = z/L therefore L = z/little_zeta
    # z = 10., little_zeta = -1 or 0.5, L = -10 or 20
    # z = 20., little_zeta = -1 or 0.5, L = -20 or 40
    # z = 40., little_zeta = -1 or 0.5, L = -40 or 80
    # So we could select L at little_zeta = -0.5 for UNSTABLE and 0.25 for STABLE and use height (zu/zt/zq) to get L
    # But then we're making the assumption about little_zeta rather than calculating it - either way
    # For now - go with L = -50 or 50, which at zu=20m gives little_zeta of -0.4 to 0.4
    if ((sst-at) > 0.2): # UNSTABLE 
        L = -50
	z0 = 0.001
    elif ((sst-at) < -0.2): # STABLE 
        L = 50
	z0 = 0.001
    else: # NEUTRAL
        L = 5000 # should be infinity
	z0 = 0.001
    
    # Calculate the stability parameter little_zeta
    little_zeta = get_little_zeta(zu,L)
    
    # Calculate the PHIs
    PHIm, PHIt, PHIh = get_phis(little_zeta)
    
    # Calculate the PSIs
    Ym, Yt, Yh = get_psis(little_zeta,PHIm,PHIt,PHIh)
    
    # Calculate the friction velocity and characteristic temperature and specific humidity (the stars!)
    k = 0.41 # von Karman constant
    u_star = get_value_star(k,zu,z0,Ym,u,u0)
    z0t = 0.001 # neutral stability heat transfer coeffieient Smith 1988
    z0q = 0.0012 # neutral stability moisture transfer coefficient Smith 1988
    t_star = get_value_star(k,zt,z0t,Yt,at,t0)
    q_star = get_value_star(k,zq,z0q,Yh,shu,q0)
    
    # Calculate the variable at 10m
    u10 = get_heightcorrected(u,u_star,k,zu,Ym,L)
    at10 = get_heightcorrected(at,t_star,k,zt,Yt,L)
    shu10 = get_heightcorrected(shu,q_star,k,zq,Yh,L)
    
    return u10, at10, shu10

#********************************************************************************
