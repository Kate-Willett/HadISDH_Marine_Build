# Written by Kate Willett 6th April 2016

'''
UpdateUpdateUpdate!
There appear to be occasions where the iteration does not converge (e.g., ob 2513 from Jan 1973)
SST = 21.1999999999
AT = 21.5 (No slr or scn)
SHU = 13.5, 13.3379
U = 6.7
SLP = 1016.1 (ClimP = 1014.725)

So - if I change SST between 21.1999 and 21.19999 it stops working. It starts working at 21.201.
And - if I keep SST as 21.19999 and change q between 13.336 (ok) 13.337 (not ok) 13.339 (ok)
NO IDEA WHY - I've ADDED A CLAUSE TO SAY IF WE GET TO 100 iterations - fix L at mean of last 10 and recalculate

Update update!

It seems to be working very close to David Berry's code which is now in this file.

The Test_HeightCorrect.py figures look very different though. 
BIGGEST (VERY LARGE) adjustments in VERY STABLE conditions.
Smallest changes in VERY UNSTABLE or neutral conditions (where L is +ve but very large!)
Changes get bigger towards neutrality as a -VE L gets more -ve (is this neutral?).
This does seem to make some sense with fig. 9.5 in p377 of Stull 1988.

import HeightCorrect as hc

adjDB,hDB = hc.run_davidberry_final(10.,15.,8.,6.,20.,18.,18)
adjK,hK = hc.run_heightcorrection_final(10.,15.,8.,6.,20.,18.,18)
adjDB['at_10m'] = 13.788, adjDB['shu_10m'] = 7.872 (u_10m = 4.262)
hDB['L'] = 6.654, hDB['u_star'] = 0.085

adjK['at_10m'] = 13.750, adjK['shu_10m'] = 7.861  (u_10m = 4.246)
hK['L'] = 9.34, hK['u_star'] = 0.120 

# LOW WIND SPEED
adjDB,hDB = hc.run_davidberry_final(10.,15.,8.,3.,20.,18.,18)
adjK,hK = hc.run_heightcorrection_final(10.,15.,8.,3.,20.,18.,18)
adjDB['at_10m'] = 10.015, adjDB['shu_10m'] = 7.540 (u_10m = -0.300) NOTE - u=4 ok, u=3 or less = -ve u_10m!
hDB['L'] = 0.013, hDB['u_star'] = 0.0003

adjK['at_10m'] = 12.802, adjK['shu_10m'] = 7.757 (u_10m = 1.515)
hK['L'] = 0.054, hK['u_star'] = 0.0014 

Our t_star and q_star methods are still quite different.
In this version I now have Yx for zx/L and Yx10 for 10/L. (Y is PSI!!!)
I have altered the calc_flux from david berry to not include the PSI (I call them Y) parameters when calculating the neutral elements at 10m.
I have altered the PSI (Y!) calculations in david berry's code to include teh **-1 **-2 and **-1 that appeared to be missing.
I have changed david berry's GAMMA constant to 5 to match mine. I could make them both 8 instead as in David's original code.

My code differs in that I use the Bretherton iteration method.
I also have some catch for neutral conditions (where -0.01 < zx/L < 0.01) which forces PHIx = 1 and Y(PSI!!!)=0.

I don't change q (SHU) to q/1000. except for when calculating vpt and vt. This doesn't appear to have a large effect - perhaps because its usage is
in a relative sense? I should try this though.

I also don't convert AT to Kelvin using the adiabatic lapse rate adjustment and I use 273.15 instead of 273.16.

My calculation for qsat(sst)*0.98 uses a different equation for vapour pressure - see CalcHums.py

Update!

Annoying!! I kind of had this working but now its broken. I decided that I was stuck with Bretherton's method
- cannot just assume that B0 is the same as overbar_w'Tv's - its not! Although it did seem to work ok.

Now using Bretherton's method it only seems to result in either VERY stable or VERY unstable conditions. I just
don't understand which bit is wrong. Clearly B0 needs to be very very tiny to make L > +/- 20m. I just can't see
how this can result unless theta_v_0 is not the potential temperature at the surface and theta_v is not the 
potential temperature. Cd and Ch appear to be realistic magnitudes. As does u*.

So, I'm giving up for now - going to use David's code even though it doesn't entirely match up with my 
understanding of what should be done

----------------------------------------


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
Yt = stability correction for heat (
Yq = stability correction for moisture (
PHIm = 
PHIt = 
PHIq = 
w'Tv' = buoyancy flux - K m s-1 (Kelvin per m per s)

>import HeightCorrect as hc
>u10,t10,q10 = hc.run_heightcorrect_proxyLz0(10.,15.,8.,5.,20.,18.,18.) # sst, at, shu, u, zu, zt, zq
>(4.5408290319390296, 14.615283569135769, 7.9568606550888683)


Now that the above works for any given L (fixed or based on whether SST>AT (UNSTABLE) or SST<AT (STABLE)) lets try to code
up the iteration to resolve L.
Using the Bretherton Lecture notes: http://www.atmos.washington.edu/~breth/classes/AS547/lect/lect6.pdf

We know that L = -u_star**3 / kBo
Guessing L (start with -50 (SST>AT/UNSTABLE), 5000 (SST=AT/NEUTRAL), 50 (SST<AT/STABLE)) and z0 as 0.005
 - calculate Ym and Yt (using get_little_zeta, get_phis, get_psis)
 - calculate the drag coefficient: Cd (get_coefficient_drag)
 - calculate the heat coefficient: Ch (get_coefficient_heat)
 - calculate the virtual potential temperature at the surface: vpt0 (get_vpt_surf) - double check diff with virtual temperature: vt0 (get_vt_surf)
 - calculate the virtual potential temperature at reference height: vpt (get_vpt) - double check diff with virtual temperature: vt (get_vt)
 - calculate friction velocity: u_star (get_star_value vs get_bretherton_u_star check?)
 - calculate the Monin-Obukhov Length: L (get_MO_length)
 - repeat until L stabilises: Lresolved
 - get the height corrections for resolved L - run_heightcorrect_proxyLz0 with Lfix = Lresolved
 
    
'''

import numpy as np
import math
import CalcHums as ch
import copy as copy
import pdb # pdb.set_trace() or c

## DAVID BERRY CONSTANTS
#GRAVITY           = 9.812
#VISCOSITY_DYNAMIC = 0.000014
#VON_KARMAN        = 0.4
#MISSING_VALUE     = -9999.
#PI                = 3.14159265
#ALPHA             = 16.0
#BETA              = 0.25
#GAMMA             = 5.0 # 8.0 in David Berry's code
#ADIABATIC_LAPSE   = 0.00976 

#******************************************************************************
def run_davidberry_final(sst,at,shu,u,zu,zt,zq,dpt=(-99.9),vap=(-99.9),crh=(-99.9),cwb=(-99.9),dpd=(-99.9),climp=(-99.9)):
    '''
    I still can't quite figure out why this works
    The Ls seem very low
    It doesn't like very low winds/SST < AT so i've changed the wind_10m_neutral bit as it was
    using the PSI_m bit which should be 0 in neutral conditions - made it fall over!

    Given all paramters (including all humidity vars), this calls the run_iterate_L() program to find the best L
    and then gets together all of the necessary variables and calls get_heightcorrect
    to get the height adjustment for u, at and shu
    
    Reads in FLOATS MUST ALL BE FLOATS!!! (although I've added a catch for this):
      sst = sea surface temperature (deg C)
      at = air temperature (deg C)
      shu = specific humidity (g/kg)
      u = wind speed (m/s)
      zu = height of anemometer (m)
      zt = height of instrument (m0) # NOT REQUIRED HERE
      zq = height of instrument (m) # NOT REQUIRED HERE
      OPTIONAL: (should you want to convert height adjustment to other parameters)
      dpt = -99.9 dew point temperature (deg C)
      vap = -99.9 vapour pressure (hPa)
      crh = -99.9 relative humidity (%rh)
      cwb = -99.9 wet bulb temperature (deg C)
      dpd = -99.9 dew point depression (deg C)
      climp = -99.9 climatological mean sea level pressure for that ob (hPa)

    IF SST IS MISSING (test for sst < -60 or > 60) USE AT
    IF U IS V SMALL OR MISSING (test for u < 0.5 then u = 0.5, if u < 0 or > 100) USE 3m/s
    IF RESULTING ADJ MAKES dpt_10m>at_10m or crh_10m>100%rh:
      at_10m is set to equal dpt_10m
      crh_10m is set to equal 100%rh 
      This results in cwb_10m, dpd_10m being recalculated.
    
    Returns:
      A dictionary of all adjusted values - if vap_10m etc are not calculate then they will be set to -99.9
      AdjDict = {'at_10m':at_10m,
      	         'shu_10m':shu_10m,
                 'vap_10m':vap_10m,
                 'dpt_10m':dpt_10m,
                 'crh_10m':crh_10m,
                 'cwb_10m':cwb_10m,
                 'dpd_10m':dpd_10m}
      A dictionary of Height Correction Variables
      HeightVarsDict = {'L':L,
                        'little_zeta':little_zeta,
		        'PHIm':PHIm,
		        'PHIt':PHIt,
		        'PHIq':PHIq,
		        'Ym':Ym,
		        'Yt':Yt,
		        'Yq':Yq,
		        'u_star':u_star,
		        't_star':t_star,
		        'q_star':q_star,
		        'z0':z0}
   
    TESTED!!!
    adjDB,hDB = hc.run_davidberry_final(10.,15.,8.,6.,20.,18.,18,dpt=10.7,vap=12.9,crh=75.5,cwb=12.6,dpd=4.3,climp=1013.)
    'dpd_10m': 3.4, 
    'at_10m': 13.783202726300203, 
    'cwb_10m': 11.9, 
    'crh_10m': 80.0, 
    'dpt_10m': 10.4, 
    'vap_10m': 12.7, 
    'shu_10m': 7.842286987739419

    '''

    # Set up constants
    #GRAVITY           = 9.812
    #VISCOSITY_DYNAMIC = 0.000014
    #VON_KARMAN        = 0.4
    #MISSING_VALUE     = -9999.
    #PI                = 3.14159265
    #ALPHA             = 16.0
    #BETA              = 0.25
    #GAMMA             = 8.0 
    #ADIABATIC_LAPSE   = 0.00976 
    
    # CHECK THAT ALL IMPORTANT THINGS ARE FLOATS
    sst = float(sst)
    at = float(at)
    shu = float(shu)
    u = float(u)
    climp = float(climp)
    zu = float(zu)
    zt = float(zt)
    zq = float(zq)
    
    # Check if sst is missing (it could be) - use at instead (NOT IDEAL!!!! - PROBABLY WANT TO FLAG FOR INCREASED UNCERTAINTY)
    if ((sst < -60.) | (sst > 60.)):
        sst = at

    # Check if u is missing or very small (it could be) - use 3m/s or 0.5 instead (NOT IDEAL!!!! - PROBABLY WANT TO FLAG FOR INCREASED UNCERTAINTY)
    # NOTE THIS RESULTS IN -VE WIND SPEEDS IF ORIG WIND SPEED IS TOO LOW!
    if (u < 0.5):
        u = 0.5
    elif (u > 100):
        u = 3.
    
    # Iterate to find L
    if (climp == -99.9):
        climp = 998.1
    DBadjdict,DBheightdict  = calc_flux(u,at,shu,sst,climp,zu,zt,zq)
    
    at_10m = DBadjdict['at_10m']
    shu_10m = DBadjdict['shu_10m']
    
    # Convert t and q height adjustments to adjustments for other humidity variables   
    # Of course we're using the same P - not a height adjusted one!!! 
    # Check if all humidity vars and climp are present first
    if ((vap > -99.9) & (crh > -99.9) & (dpt > -99.9) & (cwb > -99.9) & (dpd > -99.9) & (climp > -99.9)):
    # Get vapour pressure from specific humidity
        vap_10m = ch.vap_from_sh(shu_10m,climp,roundit=False)
    # Get dew point temperature from vapour pressure (use at too to check for wet bulb <=0)
        dpt_10m = ch.td_from_vap(vap_10m,climp,at_10m,roundit=False)
    # Get wet bulb temperature from vapour pressure and dew point temperature and air temperature
        cwb_10m = ch.wb(dpt_10m,at_10m,climp,roundit=False)
    # Get relative humidity from dew point temperature and temperature
        crh_10m = ch.rh(dpt_10m,at_10m,climp,roundit=False)
    # Get dew point depression from temperautre and dew point depression
        dpd_10m = ch.dpd(dpt_10m,at_10m,roundit=False)   
	
    # Now cross-check at_10m and dpt_10m [and crh_10m and dpd_10m] - no supersaturation allowed!
        if ((at_10m - dpt_10m) < 0.):
	    # force 100% rh limit by adjusting at_10m to dpt_10m, preserving humidity???
	    at_10m = copy.copy(dpt_10m) 
	    # recalculate affected variables = which will all be at saturation
            cwb_10m = copy.copy(at_10m)
            crh_10m = 100.0
            dpd_10m = 0.   	    	 
    else:
        vap_10m = -99.9
        dpt_10m = -99.9
        cwb_10m = -99.9	
        crh_10m = -99.9
        dpd_10m = -99.9
	
    # Create a dictionary of the adjusted values
    AdjDict = {'at_10m':at_10m,
      	       'shu_10m':shu_10m,
               'vap_10m':vap_10m,
               'dpt_10m':dpt_10m,
               'crh_10m':crh_10m,
               'cwb_10m':cwb_10m,
               'dpd_10m':dpd_10m}
        
    # Create a dictionary of height vars for iteration
    HeightVarsDict = {'L':DBheightdict['L'],
                   'little_zeta':DBheightdict['little_zeta'],
		   'Ym':DBheightdict['Ym'],
		   'Yt':DBheightdict['Yt'],
		   'Yq':DBheightdict['Yq'],
		   'u_star':DBheightdict['u_star'],
		   't_star':DBheightdict['t_star'],
		   'q_star':DBheightdict['q_star'],
		   'z0':DBheightdict['z0'],
		   'zt0':DBheightdict['zt0'],
		   'zq0':DBheightdict['zq0']}
    
    return AdjDict, HeightVarsDict

#*******************************************************************************
def run_heightcorrection_final(sst,at,shu,u,zu,zt,zq,dpt=(-99.9),vap=(-99.9),crh=(-99.9),cwb=(-99.9),dpd=(-99.9),climp=(-99.9)):
    '''
    Given all paramters (including all humidity vars), this calls the run_iterate_L() program to find the best L
    and then gets together all of the necessary variables and calls get_heightcorrect
    to get the height adjustment for u, at and shu
    
    Reads in FLOATS!!! MUST BE FLOATS - HAVE ADDED A CHECK:
      sst = sea surface temperature (deg C)
      at = air temperature (deg C)
      shu = specific humidity (g/kg)
      u = wind speed (m/s)
      zu = height of anemometer (m)
      zt = height of instrument (m0) # NOT REQUIRED HERE
      zq = height of instrument (m) # NOT REQUIRED HERE
      OPTIONAL: (should you want to convert height adjustment to other parameters)
      dpt = -99.9 dew point temperature (deg C)
      vap = -99.9 vapour pressure (hPa)
      crh = -99.9 relative humidity (%rh)
      cwb = -99.9 wet bulb temperature (deg C)
      dpd = -99.9 dew point depression (deg C)
      climp = -99.9 climatological mean sea level pressure for that ob (hPa)

    IF SST IS MISSING (test for sst < -60 or > 60) USE AT
    IF U IS V SMALL OR MISSING (test for u < 0.5 then u = 0.5, or u < 0 or > 100 then u=3m/s
    IF RESULTING ADJ MAKES dpt_10m>at_10m or crh_10m>100%rh:
      at_10m is set to equal dpt_10m
      crh_10m is set to equal 100%rh 
      This results in cwb_10m, dpd_10m being recalculated.
    IF L does not converge - exits with VAR_10m = -99.99 if L is really silly (low and not converging), settling with L of last iteration if abs(L) > 500  
    
    Returns:
      A dictionary of all adjusted values - if vap_10m etc are not calculate then they will be set to -99.9
      AdjDict = {'at_10m':at_10m,
      	         'shu_10m':shu_10m,
                 'vap_10m':vap_10m,
                 'dpt_10m':dpt_10m,
                 'crh_10m':crh_10m,
                 'cwb_10m':cwb_10m,
                 'dpd_10m':dpd_10m}
      A dictionary of Height Correction Variables
      HeightVarsDict = {'L':L,
                        'little_zetau':little_zetau,
                        'little_zetat':little_zetat,
                        'little_zetaq':little_zetaq,
		        'PHIm':PHIm,
		        'PHIt':PHIt,
		        'PHIq':PHIq,
		        'Ym':Ym,
		        'Yt':Yt,
		        'Yq':Yq,
		        'PHIm10':PHIm10,
		        'PHIt10':PHIt10,
		        'PHIq10':PHIq10,
		        'Ym10':Ym10,
		        'Yt10':Yt10,
		        'Yq10':Yq10,
		        'u_star':u_star,
		        't_star':t_star,
		        'q_star':q_star,
		        'z0':z0}
    
    Constants:
    z0t = 0.001 # neutral stability heat transfer coeffieient Smith 1988
    z0q = 0.0012 # neutral stability moisture transfer coefficient Smith 1988
    k = 0.41 # von karman constant
    
    AdjDict,HeightVarsDict = run_heightcorrection_final(10.,15.,8.,3.,20.,18.,18.)
    If you do not want to read in the dictionary:
    AdjDict,_ = run_heightcorrection_final(10.,15.,8.,3.,20.,18.,18.)
    AdjDict['at_10m']
    
    adjK,hK = hc.run_heightcorrection_final(10.,15.,8.,6.,20.,18.,18,dpt=10.7,vap=12.9,crh=75.5,cwb=12.6,dpd=4.3,climp=1013.)
    'dpd_10m': 3.4, 
    'at_10m': 13.750023166125274, 
    'cwb_10m': 11.9, 
    'crh_10m': 80.2, 
    'dpt_10m': 10.4, 
    'vap_10m': 12.7, 
    'shu_10m': 7.8606914650250568
  
    '''

    # CHECK THAT ALL IMPORTANT THINGS ARE FLOATS
    sst = float(sst)
    at = float(at)
    shu = float(shu)
    u = float(u)
    climp = float(climp)
    zu = float(zu)
    zt = float(zt)
    zq = float(zq)

    # Set up constants
    z0t = 0.001
    z0q = 0.0012
    k = 0.41
    
    # Check if sst is missing (it could be) - use at instead (NOT IDEAL!!!! - PROBABLY WANT TO FLAG FOR INCREASED UNCERTAINTY)
    if ((sst < -60.) | (sst > 60.)):
        sst = at

    # Check if u is missing or very small (it could be) - use 3 or 0.5m/s instead (NOT IDEAL!!!! - PROBABLY WANT TO FLAG FOR INCREASED UNCERTAINTY)
    if (u < 0.5):
        u = 0.5
    elif (u > 100):
        u = 3.
    
    # Iterate to find L
    HeightDict = run_iterate_L(sst,at,shu,u,zu,zt,zq)
    
    # Check the run_iterate_L output to makesure its not nonsense u_star=9999. (has not converged!)
    if (HeightDict['u_star'] < 9999.):

        # Get the Surface values
        u0, t0, q0 = get_surface_values(sst)
        
        # Given iterated values get t_star and q_star
        # David uses a different equation requiring heat and moisture transfer coefficients
        t_star = get_value_star(k,zt,z0t,HeightDict['Yt'],at,t0)
        q_star = get_value_star(k,zq,z0q,HeightDict['Yq'],shu,q0)
    #    print("t_star, q_star: ",t_star," ",q_star)
        
        # Get the height adjustments for t and q (u unnecessary)
        u_10m = get_heightcorrected(u,HeightDict['u_star'],k,zu,HeightDict['Ym'],HeightDict['L'],HeightDict['Ym10'])
    #    print("u10: ",u_10m)
        at_10m = get_heightcorrected(at,t_star,k,zt,HeightDict['Yt'],HeightDict['L'],HeightDict['Yt10'])
        shu_10m = get_heightcorrected(shu,q_star,k,zq,HeightDict['Yq'],HeightDict['L'],HeightDict['Yq10'])
        
	# Check that shu_10m isn't -ve. This can happen if its very small to start with and leads to NaNs in DPT
	# If this happens, return as -99.9 for all vars
	# Also check that at_10m isn't super silly either - cases of starting ATs being 40+ degrees where SST is ~8 (ob 118659 in April 1974!
	if ((shu_10m > 0.) & (at_10m > -80.) & (at_10m < 65.)):
	
            # Convert t and q height adjustments to adjustments for other humidity variables   
            # Of course we're using the same P - not a height adjusted one!!! 
            # Check if all humidity vars and climp are present first
            if ((vap > -99.9) & (crh > -99.9) & (dpt > -99.9) & (cwb > -99.9) & (dpd > -99.9) & (climp > -99.9)):
                # Get vapour pressure from specific humidity
                vap_10m = ch.vap_from_sh(shu_10m,climp,roundit=False)
                # Get dew point temperature from vapour pressure (use at too to check for wet bulb <=0)
                dpt_10m = ch.td_from_vap(vap_10m,climp,at_10m,roundit=False)
                # Get wet bulb temperature from vapour pressure and dew point temperature and air temperature
                cwb_10m = ch.wb(dpt_10m,at_10m,climp,roundit=False)
                # Get relative humidity from dew point temperature and temperature
                crh_10m = ch.rh(dpt_10m,at_10m,climp,roundit=False)
                # Get dew point depression from temperautre and dew point depression
                dpd_10m = ch.dpd(dpt_10m,at_10m,roundit=False)   
	
                # Now cross-check at_10m and dpt_10m [and crh_10m and dpd_10m] - no supersaturation allowed!
                if ((at_10m - dpt_10m) < 0.):
	            # force 100% rh limit by adjusting at_10m to dpt_10m, preserving humidity???
	            at_10m = copy.copy(dpt_10m) 
	            # recalculate affected variables = which will all be at saturation
                    cwb_10m = copy.copy(at_10m)
                    crh_10m = 100.0
                    dpd_10m = 0.   	    	 
            else:
                vap_10m = -99.9
                dpt_10m = -99.9
                cwb_10m = -99.9	
                crh_10m = -99.9
                dpd_10m = -99.9
        else:
            at_10m = -99.9
            dpt_10m = -99.9
            vap_10m = -99.9
            shu_10m = -99.9
            cwb_10m = -99.9     
            crh_10m = -99.9
            dpd_10m = -99.9
    else:
        at_10m = -99.9
        dpt_10m = -99.9
        vap_10m = -99.9
        shu_10m = -99.9
        cwb_10m = -99.9     
        crh_10m = -99.9
        dpd_10m = -99.9

    # Create a dictionary of the adjusted values
    AdjDict = {'at_10m':at_10m,
      	       'shu_10m':shu_10m,
               'vap_10m':vap_10m,
               'dpt_10m':dpt_10m,
               'crh_10m':crh_10m,
               'cwb_10m':cwb_10m,
               'dpd_10m':dpd_10m}
        
    # Pass on the dictionary of height vars for iteration
    
    return AdjDict, HeightDict

#********************************************************************************
def run_iterate_L(sst,at,shu,u,zu,zt,zq,Lmin = -50., Lmax = 50., Lfix = 999): 
    '''
    Code to produce u,t,q converted to 10m using assumed L and z0 depending on stability
    
    Reads in FLOATS - MUST ALL BE FLOATS - HAVE ADDED CHECK:
      sst = sea surface temperature (deg C)
      at = air temperature (deg C)
      shu = specific humidity (g/kg)
      u = wind speed (m/s)
      zu = height of anemometer (m)
      zt = height of instrument (m0) # NOT REQUIRED HERE
      zq = height of instrument (m) # NOT REQUIRED HERE
      OPTIONAL:
      Lmin = set minimum value for the Monin-Obukhov length (m) - default -50
      Lmax = set maximum value for the Monin-Obukhov Length (m) - default 50
      Lfix = set a fixed value for L regardless of assessed stability based on SST-AT - default is 999 (not set)
      
    IF SST IS MISSING (test for sst < -60 or > 60) USE AT
    IF U IS MISSING (test for u < 0 or u > 100) USE 3m/s

    Returns - everything you need to calculate height apart from t_star and q_star:
      Lres = resolved Monin-Obukhov lenth (m)
      little_zeta = stability parameter (dimensionless)
      PHIm = dimensionless profile for momentum
      PHIt = dimensionless profile for heat
      PHIq = dimensionless profile for moisture
      Ym = stability correction for momentum
      Yt = stability correction for heat
      Yq = stability correction for moisture
      u_star = friction velocity (m/s)
      z0 = roughness length (m)
    
    # Normal run with fix Lmin= -50 and Lmax = 50  
    Lres = run_iterate_L(10.,15.,8.,3.,20.,18.,18.)  
    # Run with fixed Lmin and Lmax of your choice
    Lres = run_iterate_L(10.,15.,8.,3.,20.,18.,18.,Lmin = -50, Lmax = 50)  
    # Run with a fixed L regardless of SST-AT difference
    Lres = run_iterate_L(10.,15.,8.,3.,20.,18.,18.,Lfix = 999)  
    
    Constants:
    k = 0.41 # von Karman constant
    z0 = we have set this to 0.005 (Stull 1988 says between 0.001 and 0.01 for ocean)
    z0t = 0.001 # neutral stability heat transfer coeffieient Smith 1988
    z0q = 0.0012 # neutral stability moisture transfer coefficient Smith 1988
    For the PHIs (dimensionless profiles):
    alpha_s = 16.# Smith (1980,1988), Large and Pond (1981) Berry (2009)
    beta = 1./4. # Smith (1980,1988), Large and Pond (1981) Berry (2009)
    gamma_s = 5. # Smith (1980,1988), Large and Pond (1981) Berry (2009)

    We know that L = -u_star**3 / kBo (Actually the Stull 1988 is better! Assume B0 = (overbar_w'*overbar_vpt')s
    Guessing L (start with -50 (SST>AT/UNSTABLE), 5000 (SST=AT/NEUTRAL), 50 (SST<AT/STABLE)) and z0 as 0.005
     - calculate Ym and Yt (using get_little_zeta, get_phis, get_psis)
     - estimate roughness length z0$ based on u (get_roughness_length)
     - estimate the drag coefficient: Cd (get_coefficient_drag) - USES z0$ (estimated!)
     - estimate friction velocity: u_star (get_star_value vs get_bretherton_u_star check?)
     - estimate neutral wind speed at 10m u10n (get_heightcorrected)
     - calculate z0 based on u10n (get_roughness_length)
     - calculate the drag coefficient: Cd (get_coefficient_drag) - USES z0$ (estimated!)
     - calculate friction velocity: u_star (get_star_value vs get_bretherton_u_star check?)
     - calculate the heat coefficient: Ch (get_coefficient_heat)
     - calculate the virtual potential temperature at the surface: vpt0 (get_vpt_surf) - double check diff with virtual temperature: vt0 (get_vt_surf)
     - calculate the virtual potential temperature at reference height: vpt (get_vpt) - double check diff with virtual temperature: vt (get_vt)
     - calculate the Monin-Obukhov Length: L (get_MO_length)
     - repeat until L stabilises: Lresolved
     - get the height corrections for resolved L - run_heightcorrect_proxyLz0 with Lfix = Lresolved

    NOTES:
    
    There is sometimes an issue (noted so far for very large negative L) where certain combinations (within 0.002 deg C or 0.002 g/kg)
    lead to no convergence of L. I have set a limit for 100 iterations. Hopefully L is very large -ve or very large +ve in these cases = NEUTRAL.
    I have fixed L to the last iteration and exited if so. If L is small but unstable then there is something up so I've exited with L=9999 and u_star=9999
    
    Test:
    Larr=[]
    #LresB,LresS = hc.run_iterate_L(10.,15.,8.,3.,20.,18.,18.,)
    LresS = hc.run_iterate_L(10.,15.,8.,3.,20.,18.,18.,)
    Larr.append(LresS)
    for i in range(10):
    #    LresB,LresS = hc.run_iterate_L(10.,15.,8.,3.,20.,18.,18.,Lfix=LresS)
        LresS = hc.run_iterate_L(10.,15.,8.,3.,20.,18.,18.,Lfix=LresS)
	Larr.append(LresS)
    This only converges when I replaced the zt in Ch equation to zt0!
    This also only converges for LresS (the Stull 1988 equation!) - fewer than 10 iterations!
    So I've commented out the Bretherton version
    
    It is clear that the resulting L is very sensitive to z0. If I vary it from z0=0.001 to 0.0001.
    z0=0.001 hc.run_iterate_L(10.,15.,8.,3.,20.,18.,18.)
    LresB=4.606 LresS=136.021 
    z0=0.0001 hc.run_iterate_L(10.,15.,8.,3.,20.,18.,18.)
    LresB=3.119 LresS=92.112
    
    z0 = (0.61 + (0.063*u10n))/1000.
    It depends on u10n (neutral wind speed at 10m) 
    u10n = get_hieghtcorrected(u,u_star,k,zu,Ym,L) where Ym = 0 and L can be anything because it is not effective (multiplied by 0!)
    u10n = get_hieghtcorrected(1.,0.05 or 0.5,0.41,20.,0.1000.)
    u10n = 0.915 or 0.155 
    z0 = 0.0007 or 0.0006 (or at u 0.0007)	
    u10n = get_hieghtcorrected(5.,0.05 or 0.5,0.41,20.,0.1000.)
    u10n = 4.915 or 4.155 
    z0 = 0.0009 or 0.0009 (or at u 0.0009)	
    u10n = get_hieghtcorrected(10.,0.05 or 0.5,0.41,20.,0.1000.)
    u10n = 9.915 or 9.155  	
    z0 = 0.0013 or 0.0012 (or at u 0.0012)
    So - u10n isn't very much lower than actual wind speed and its not that sensitive to u_star.
    So - I think from an esimate of u_star we can estimate u10n and z0
    	
    '''

    # CHECK THAT ALL IMPORTANT THINGS ARE FLOATS
    sst = float(sst)
    at = float(at)
    shu = float(shu)
    u = float(u)
    zu = float(zu)
    zt = float(zt)
    zq = float(zq)

    # Check if sst is missing (it could be) - use at instead (NOT IDEAL!!!! - PROBABLY WANT TO FLAG FOR INCREASED UNCERTAINTY)
    # This will make zero height adjustment to temperature
    if ((sst < -60.) | (sst > 60.)):
        sst = at

    # Check if u is missing or very small (it could be) - use 3 or 0.5m/s instead (NOT IDEAL!!!! - PROBABLY WANT TO FLAG FOR INCREASED UNCERTAINTY)
    if (u < 0.5):
        u = 0.5
    elif (u > 100):
        u = 3.

    # get an estimated L to start with based on assumed stability (SST vs AT) or given a fixed L
    # I'm also using a fixed z0 here too because its very small
    # TURNS OUT z0 MAKES A BIG DIFFERENCE TO L!!!
    # Doesn't seem to matter what L you start with
    if (Lfix == 999):
        if ((sst-at) > 0.2): # UNSTABLE 
            L = Lmin # default = -50
        elif ((sst-at) < -0.2): # STABLE 
            L = Lmax # default = 50
        else: # NEUTRAL
            L = 5000. # should be infinity
    else:
        L = Lfix
	
    # Set up Lres starting value
    Lres = 999
    
    # Loop through until Lres converages with L
    counter=0
    
    # Initialise u10n as u to start with
    u10n = copy.copy(u)
    
    while (abs((Lres - L)) > 0.1):
        
#	print(counter,L,Lres,abs(Lres-L))
	
	# replace L with previous Lres value
	L = copy.copy(Lres)

        # Get the Surface values
        u0, t0, q0 = get_surface_values(sst)
#        print("Surface u, t, q: ",u0," ",t0," ",q0)
	
        # Calculate the stability parameter little_zetau
	# also calculate the zt/L (little_zetat) and zq/L (littlezetaq)
        little_zetau,little_zetat,little_zetaq = get_little_zeta(zu,zt,zq,L)
#        print("little_zeta: ",little_zetau," ",little_zetat," ",little_zetaq)
        
        # Calculate the PHIs for zx/L
        PHIm, PHIt, PHIq = get_phis(little_zetau,little_zetat,little_zetaq)
#        print("PHIm, PHIt, PHIq: ",PHIm," ",PHIt," ",PHIq)
        
        # Calculate the PSIs - we need Ym and Yt(same as Yq anyway) for zx/L
        Ym, Yt, Yq = get_psis(little_zetau,little_zetat,little_zetaq,PHIm,PHIt,PHIq)
#        print("Ym, Yt, Yq: ",Ym," ",Yt," ",Yq)

        # Calculate the PHIs for 10/L
	little_zeta10 = little_zetau*(10/zu)
        PHIm10, PHIt10, PHIq10 = get_phis(little_zeta10,little_zeta10,little_zeta10)
#        print("PHIm10, PHIt10, PHIq10: ",PHIm10," ",PHIt10," ",PHIq10)
        
        # Calculate the PSIs - we need Ym and Yt(same as Yq anyway) for zx/L
        Ym10, Yt10, Yq10 = get_psis(little_zeta10,little_zeta10,little_zeta10,PHIm10,PHIt10,PHIq10)
#        print("Ym10, Yt10, Yq10: ",Ym10," ",Yt10," ",Yq10)

        # Estimate the roughness length z0_est from u in first instance
        # Very little difference between u and u10n it seems
        z0_est = get_roughness_length(u10n)

        # Estimate the Coefficient of drag Cd using z0_est
        k = 0.41 # von Karman constant
        Cd_est = get_coefficient_drag(k,zu,z0_est,Ym,L)
        
        # Estimate friction velocity u* from Cd_est and u
        u_star_est = get_bretherton_u_star(Cd_est,u)

        # Calculate neutral wind speed at 10m based on u_star_est
        # Assumes neutral conditions so Ym = 0 and L can be anything because it is multiplied by Ym which is 0!
        # u_star doesn't make very much difference to u10n which isn't very different to u
        u10n = get_heightcorrected(u,u_star_est,k,zu,0,1000.,0)
#        print("u10n: ",u10n)
        
        # Calculate the roughness length z0 from u10n 
        # Very little difference between u and u10n it seems
        z0 = get_roughness_length(u10n)
#        print("z0_est: ",z0_est," z0: ",z0)

        # Calculate the Coefficient of drag Cd
        Cd = get_coefficient_drag(k,zu,z0,Ym,L)
#        print("Cd_est: ",Cd_est," Cd: ",Cd,)

        # Calculate friction velocity u* from Cd and u
        u_star = get_bretherton_u_star(Cd,u)
        other_u_star = get_value_star(k,zu,z0,Ym,u,u0)
#        print("u_star_est: ",u_star_est," u_star: ",u_star," other_u_star: ",other_u_star) # Ooooh - u_star == other_u_star !!! to at least 8 sig figures!

        # Calculate the Coefficient of heat Ch
        zt0 = 0.001 # I think the zt in this equation is the zt0 equivalent of z0 - neutral stability heat transfer coeffieient Smith 1988 
        Ch = get_coefficient_heat(k,zu,z0,Ym,L,zt,zt0,Yt) # could use zt or zq here as both should be the same
#        print("Ch: ",Ch)
        
        # Calculate the virtual temperature and print
        vt = get_vt(at,shu)
        
        # Calculate the virtual potential temperature and print
        vpt = get_vpt(at,shu,zt)

        # Calculate the virtual temperature at surface and print
        vt0 = get_vt_surf(t0,q0)
        
        # Calculate the virtual potential temperature at surface and print
        # Not setting z0t = 0.001 # neutral stability heat transfer coeffieient Smith 1988
        vpt0 = get_vpt_surf(t0,q0,0.)
        
#        print("vt, vt0, vpt, vpt0: ",vt," ",vt0," ",vpt," ",vpt0)
        
        # Calculate the surface buoyancy flux B0
        #B0 = get_buoyancy_flux(Ch,u,vpt0, vpt)  
        B0 = get_buoyancy_flux(Ch,u,vt0,vt)  
#        print("B0: ",B0)
        
        # Calculate the Monin-Obukov length
        #Lres = get_MO_length(u_star,k,B0,vpt)    
        Lres = get_MO_length(u_star,k,B0,vt)    
#	print("Lres: ",Lres)
	
	counter = counter + 1
	
	# Have a check to make sure this doesn't get stuck in an infinite loop
	# If abs(L) is VERY LARGE then exit as we are = very large L = very small little_zeta = close to NEUTRAL
	# If abs(L) is very small then it should have converged around zero anyway but force a fall over
	if (counter > 100):
	    if (abs(L) > 500):
	        break		
	    else:
	        # Exit loop and return some nonsense to make sure that the mother program knows somethign is awry
		L = 9999.
		u_star = 9999.
		break
			 
	#pdb.set_trace()
	
    # Return the values required for the height correction
    HeightVarsDict = {'L':Lres,
                        'little_zetau':little_zetau,
                        'little_zetat':little_zetat,
                        'little_zetaq':little_zetaq,
                        'little_zeta10':little_zeta10,
		        'PHIm':PHIm,
		        'PHIt':PHIt,
		        'PHIq':PHIq,
		        'Ym':Ym,
		        'Yt':Yt,
		        'Yq':Yq,
		        'PHIm10':PHIm10,
		        'PHIt10':PHIt10,
		        'PHIq10':PHIq10,
		        'Ym10':Ym10,
		        'Yt10':Yt10,
		        'Yq10':Yq10,
		        'u_star':u_star,
		        't_star':0.,
		        'q_star':0.,
		        'z0':z0}	
    return HeightVarsDict
    
#********************************************************************************
def run_heightcorrect_proxyLz0(sst,at,shu,u,zu,zt,zq,Lmin = -50, Lmax = 50, Lfix = 999):
    '''
    Code to produce u,t,q converted to 10m using assumed L and z0 depending on stability
    
    Reads in:
      sst = sea surface temperature (deg C)
      at = air temperature (deg C)
      shu = specific humidity (g/kg)
      u = wind speed (m/s)
      zu = height of anemometer (m)
      zt = height of instrument (m0)
      zq = height of instrument (m)
      OPTIONAL:
      Lmin = set minimum value for the Monin-Obukhov length (m) - default -50
      Lmax = set maximum value for the Monin-Obukhov Length (m) - default 50
      Lfix = set a fixed value for L regardless of assessed stability based on SST-AT - default is 999 (not set)
      
    IF SST IS MISSING (test for sst < -60 or > 60) USE AT
    IF U IS MISSING (test for u < 3 or u > 100) USE 3m/s
    
    Returns:
      u10 = wind speed at 10m (m/s)
      at10 = air temperature at 10m (deg C)
      shu10 = specific humidity at 10m (g/kg)
    
    # Normal run with fix Lmin= -50 and Lmax = 50  
    u10,at10,shu10 = run_heightcorrect_proxyLz0(sst,at,shu,u,zu,zt,zq)  
    # Run with fixed Lmin and Lmax of your choice
    u10,at10,shu10 = run_heightcorrect_proxyLz0(sst,at,shu,u,zu,zt,zq,Lmin = -50, Lmax = 50)  
    # Run with a fixed L regardless of SST-AT difference
    u10,at10,shu10 = run_heightcorrect_proxyLz0(sst,at,shu,u,zu,zt,zq,Lfix = 999)  
    
    Constants:
    k = 0.41 # von Karman constant
    z0 = we have set this to 0.005 (Stull 1988 says between 0.001 and 0.01 for ocean)
    z0t = 0.001 # neutral stability heat transfer coeffieient Smith 1988
    z0q = 0.0012 # neutral stability moisture transfer coefficient Smith 1988
    For the PHIs (dimensionless profiles):
    alpha_s = 16.# Smith (1980,1988), Large and Pond (1981) Berry (2009)
    beta = 1./4. # Smith (1980,1988), Large and Pond (1981) Berry (2009)
    gamma_s = 5. # Smith (1980,1988), Large and Pond (1981) Berry (2009) - could use 8?

    Works out surface values: get_surface_values:
        u0 = 0.
        t0 = SST
        q0 = qsat(SST)*0.98
    
    Depending on stability, assumes L and z0
        L = the Monin-Obukhov Length (50 - STABLE?) (-50m - UNSTABLE?) INFINITY for NEUTRAL!!!!
        z0 = roughness length (0.001 to 1m) - shouldn't be much larger than 0.01m over ocean
	
    Calculates:	
        little_zeta = stability parameter - calculate from zu and L: get_little_zeta
        The PHIs: get_phis for zx/L and 10/L
	    PHIm = dimensionless profiles - calculate depending on stability from alphas, little_zeta, beta (UNSTABLE) or gammas, little_zeta (STABLE)
            PHIt = dimensionless profiles - calculate depending on stability - calculate from PHIm depending on stability
            PHIq = dimensionless profiles - calculate depending on stability - same as PHIt
        The Ys: get_psis for zx/L and 10/L
            Ym = stability correction for momentum 0 = NEUTRAL [(-1 (UNSTABLE) to 2 (STABLE)] - or calculate from PHIm depending on stability 
            Yt = stability correction for heat - calculate from PHIt (UNSTABLE) or PHIm (STABLE)
            Yq = stability correction for moisture - same as Yt
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

    # Check if u is missing (it could be) - use 3m/s instead (NOT IDEAL!!!! - PROBABLY WANT TO FLAG FOR INCREASED UNCERTAINTY)
    if ((u < 0.) | (u > 100)):
        u = 3.

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
    # I've also added in an OPTIONAL Lmin, Lmax in case we want to change these from outside
    # I;ve also added in an Lfix optional. If this is set to something other than 999 then L is set to that

    if (Lfix == 999):
        if ((sst-at) > 0.2): # UNSTABLE 
            L = Lmin # default = -50
	    z0 = 0.001
        elif ((sst-at) < -0.2): # STABLE 
            L = Lmax # default = 50
	    z0 = 0.001
        else: # NEUTRAL
            L = 5000 # should be infinity
	    z0 = 0.001
    else:
        L = Lfix
	z0 = 0.001

    # Calculate the stability parameter little_zetau
    # also calculate the zt/L (little_zetat) and zq/L (littlezetaq)
    little_zetau,little_zetat,little_zetaq = get_little_zeta(zu,zt,zq,L)
    print("little_zeta: ",little_zetau," ",little_zetat," ",little_zetaq)
    
    # Calculate the PHIs for zx/L
    PHIm, PHIt, PHIq = get_phis(little_zetau,little_zetat,little_zetaq)
    print("PHIm, PHIt, PHIq: ",PHIm," ",PHIt," ",PHIq)
    
    # Calculate the PSIs - we need Ym and Yt(same as Yq anyway) for zx/L
    Ym, Yt, Yq = get_psis(little_zetau,little_zetat,little_zetaq,PHIm,PHIt,PHIq)
    print("Ym, Yt, Yq: ",Ym," ",Yt," ",Yq)

    # Calculate the PHIs for 10/L
    little_zeta10 = little_zetau*(10/zu)
    PHIm10, PHIt10, PHIq10 = get_phis(little_zeta10,little_zeta10,little_zeta10)
    print("PHIm10, PHIt10, PHIq10: ",PHIm10," ",PHIt10," ",PHIq10)
    
    # Calculate the PSIs - we need Ym and Yt(same as Yq anyway) for zx/L
    Ym10, Yt10, Yq10 = get_psis(little_zeta10,little_zeta10,little_zeta10,PHIm10,PHIt10,PHIq10)
    print("Ym10, Yt10, Yq10: ",Ym10," ",Yt10," ",Yq10)

    # Iterate to get a reasonable value for z0 rather than just assume - it makes a BIG difference! u_star also affects L quite a lot
    # Estimate the roughness length z0_est from u in first instance
    # Very little difference between u and u10n it seems
    u10n = copy.copy(u)
    z0_est = get_roughness_length(u10n)

    # Estimate the Coefficient of drag Cd using z0_est
    k = 0.41 # von Karman constant
    Cd_est = get_coefficient_drag(k,zu,z0_est,Ym,L)
    
    # Estimate friction velocity u* from Cd_est and u
    u_star_est = get_bretherton_u_star(Cd_est,u)

    # Calculate neutral wind speed at 10m based on u_star_est
    # Assumes neutral conditions so Ym = 0 and L can be anything because it is multiplied by Ym which is 0!
    # u_star doesn't make very much difference to u10n which isn't very different to u
    u10n = get_heightcorrected(u,u_star_est,k,zu,0,1000.,0)
#    print("u10n: ",u10n)
    
    # Calculate the roughness length z0 from u10n 
    # Very little difference between u and u10n it seems
    z0 = get_roughness_length(u10n)
#    print("z0_est: ",z0_est," z0: ",z0)

    # Calculate the Coefficient of drag Cd
    Cd = get_coefficient_drag(k,zu,z0,Ym,L)
#    print("Cd_est: ",Cd_est," Cd: ",Cd,)

    # Calculate friction velocity u* from Cd and u
    u_star = get_bretherton_u_star(Cd,u)
#    print("u_star_est: ",u_star_est," u_star: ",u_star)
    
	    
    # Calculate the friction velocity and characteristic temperature and specific humidity (the stars!)
    k = 0.41 # von Karman constant
#    u_star = get_value_star(k,zu,z0,Ym,u,u0)
    z0t = 0.001 # neutral stability heat transfer coeffieient Smith 1988
    z0q = 0.0012 # neutral stability moisture transfer coefficient Smith 1988
    t_star = get_value_star(k,zt,z0t,Yt,at,t0)
    q_star = get_value_star(k,zq,z0q,Yq,shu,q0)
    
    # Calculate the variable at 10m
    u10 = get_heightcorrected(u,u_star,k,zu,Ym,L,Ym10)
    at10 = get_heightcorrected(at,t_star,k,zt,Yt,L,Yt10)
    shu10 = get_heightcorrected(shu,q_star,k,zq,Yq,L,Yq10)
    
    return u10, at10, shu10

#********************************************************************************
def get_heightcorrected(x,x_star,k,zx,Yx,L,Yx10):
    '''
    Works out the variable converted to 10m height
    
    Reads in: 
      x - observed value at height (m/s, g/kg or deg C) NOT KELVIN?
      x_star - friction velocity/characteristic temperaure/characteristic specific humidity
      k - von Karman constant
      zx - height of anemometer/instrument (m)
      Yx - stability correction for zx/L
      L - Monin-Obukhov length (m)
      Yx10 - stability correction for 10/L
      
    Returns  
      x10 - value converted to 10m (m/s, g/kg or deg C) NOT KELVIN?
    
    u10 = get_heightcorrected(u,u_star,k,zu,Ym,L,Ym10)
    at10 = get_heightcorrected(at,t_star,k,zt,Yt,L,Yt10)
    shu10 = get_heightcorrected(shu,q_star,k,zq,Yq,L,Yq10)
    
    TESTED!!!
    OLD VERSION WITH Ym(zu/L) and Ym(10/L) rather than Ym and Ym10!!!
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
      Ym/Yt/Yq
    We have also estimated many other things but these look most important in that they appear in the final calculation. If we can prove that +/- some value doesn't make much difference
    then we're ok. Ideally - this would be the asumption of L = either -50 ro 50! This is because little_zeta, PHIs, Ys all depend on L - and u*/t*/q* really.
       
    NEW VALUES WITH Ym and Ym10
                    
    '''

#    x10 = x - (x_star/k) * (np.log(zx/10.) - Yx*(zx/L) + Yx*(10./L))     
    x10 = x - (x_star/k) * (np.log(zx/10.) - Yx + Yx10)     
    	
    return x10

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
    
    q0 = 0.98*(ch.sh(sst,sst,1013.0,roundit=False)) # ideally would use the climslp but annoying to read in and match up and OBS slp not always there

    return u0,t0,q0

#********************************************************************************
def get_little_zeta(zu,zt,zq,L):
    '''
    Works out stability parameter
    
    Reads in: 
      zu - height of anemometer (m) ??(only momentum related things are calculated from this so no need for instrument heights)
      zt - height of instrument (m) 
      zq - height of instrument (m) 
      L - Monin-Obukhov length (m)
      
    Returns  
      little_zetau/t/q - stability parameter (dimensionless: -ve = UNSTABLE, +ve = STABLE)
                  - over ocean generally ranges between -1 and 0.5 (Berry 2009)
		  - at zu = 20 and L -50 to 50 little_zeta is -0.4 to 0.4
    
    little_zetau,little_zetat,little_zetq = get_little_zeta(zu,zt,zq,L)
    
    TESTED!!!
    
    '''
    little_zetau = zu/L
    little_zetat = zt/L
    little_zetaq = zq/L
    	
    return little_zetau,little_zetat,little_zetaq

#********************************************************************************
def get_phis(little_zetau,little_zetat,little_zetaq):
    '''
    Works out the dimensionless profiles
    
    Reads in: 
      little_zetau/t/q - stability parameter (dimensionless: -ve = UNSTABLE, +ve = STABLE)
                       - these can also be 10/L so shouldnn't be used to test for stability?
		       - THEY ARE IN DAVID BERRY'S CODE 
    Returns  
      PHIm - dimensionless profile for momentum
      PHIt - dimensionless profile for heat
      PHIq - dimensionless profile for moisture
    
    PHIm,PHIt,PHIq = get_phis(little_zeta)
    
    TESTED!!!
    These appear to vary between PHIm = 0.49, PHIt/PHIq = 0.24 (UNSTABLE little_zeta = -1) and PHIm/PHIt/PHIq = 3.5 (STABLE little_zeta = 0.5)
    These appear to vary between PHIm = 0.61, PHIt/PHIq = 0.37 (UNSTABLE little_zeta = -0.4) and PHIm/PHIt/PHIq = 3.0 (STABLE little_zeta = 0.4)
    
    '''
    # set up the required constants Smith (1980,1988), Large and Pond (1981) Berry (2009)
    alpha_s = 16.
    beta = 1./4.
    gamma_s = 5.
    
    # calculate depending on stability - tried -0.1 to 0.1 for NEUTRAL but resulted in jumps - better to keep smooth?
    if (little_zetau < -0.01): # UNSTABLE
        PHIm = (1. - (alpha_s*little_zetau))**(-beta)
	#PHIt = PHIm**2
	#PHIq = copy.copy(PHIt)
    elif (little_zetau > 0.01): # STABLE
        PHIm = (1. + (gamma_s*little_zetau))
	#PHIt = copy.copy(PHIm)
	#PHIq = copy.copy(PHIt)
    else: # NEUTRAL
        PHIm = 1.
	#PHIt = 1.
	#PHIq = 1.

    if (little_zetat < -0.01): # UNSTABLE
	PHIt = ((1. - (alpha_s*little_zetat))**(-beta))**2
    elif (little_zetat > 0.01): # STABLE
	PHIt = (1. + (gamma_s*little_zetat))
    else:    	
	PHIt = 1.

    if (little_zetaq < -0.01): # UNSTABLE
	PHIq = ((1. - (alpha_s*little_zetat))**(-beta))**2
    elif (little_zetau > 0.01): # STABLE
	PHIq = (1. + (gamma_s*little_zetaq))
    else:
        PHIq = 1.
	
    return PHIm,PHIt,PHIq

#********************************************************************************
def get_psis(little_zetau,little_zetat,little_zetaq,PHIm,PHIt,PHIq):
    '''
    Works out the stability corrections
    
    Reads in: 
      little_zetau/t/q - stability parameter (dimensionless: -ve = UNSTABLE, +ve = STABLE)
      PHIm - dimensionless profile for momentum
      PHIt - dimensionless profile for heat
      PHIq - dimensionless profile for moisture
      
    Returns  
      Ym - stability correction for momentum
      Yt - stability correction for heat
      Yq - stability correction for moisture
    
    Ym,Yt,Yq = get_psis(little_zeta,PHIm,PHIt,PHIq)
    
    TESTED!!!
    These appear to vary between Ym = 1.12, Yt/Yq = 1.88 (UNSTABLE little_zeta = -1) and Ym/Yt/Yq = -2.5 (STABLE little_zeta = 0.5)
    These appear to vary between Ym = 0.70, Yt/Yq = 1.24 (UNSTABLE little_zeta = -0.4) and Ym/Yt/Yq = -2.0 (STABLE little_zeta = 0.4)
    
    '''
        
    # calculate depending on stability
    if (little_zetau < -0.01): # UNSTABLE
        Ym = 2 * np.log((1+(PHIm**-1))/2.) + np.log((1+(PHIm**-2))/2.) - 2*np.arctan(PHIm**-1) + (np.pi/2.)  # not 100% sure about the np.arctan(PHIm**-1) notation was 2tan**-1 PHIm**-1
	#Yt = 2 * np.log((1+(PHIt**-1))/2.)
	#Yq = copy.copy(Yt)
    elif (little_zetau > 0.01): # STABLE
        Ym = 1. - PHIm
	#Yt = copy.copy(Ym)
	#Yq = copy.copy(Yt)
    else: # NEUTRAL
        Ym = 0.
	#Yt = 0.
	#Yq = 0.

    if (little_zetat < -0.01): # UNSTABLE
        Yt = 2 * np.log((1+(PHIt**-1))/2.)
    elif (little_zetat > 0.01): # STABLE
        Yt = 1. - PHIt
    else: # NEUTRAL
	Yt = 0.

    if (little_zetaq < -0.01): # UNSTABLE
	Yq = 2 * np.log((1+(PHIq**-1))/2.)
    elif (little_zetaq > 0.01): # STABLE
        Yq = 1. - PHIq
    else: # NEUTRAL
	Yq = 0.
    	
    return Ym,Yt,Yq

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
    q_star = get_value_star(k,zq,z0q,Yq,q,q0)
    
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
def get_coefficient_drag(k,zu,z0,Ym,L):
    '''
    Works out the coefficient of drag
    
    Reads in: 
      k - von karman constant
      zu - height of anemometer (m)
      z0 - roughness length
      Ym - stability correction for momentum
      L - Monin-Obukhov length (m)
      
    Returns  
      Cd - coefficient of drag
    
    Cd = get_coefficient_drag(k,zu,z0,Ym,L)
    
    TESTED!!!
    For k=0.41,zu=20,z0=0.005,Ym=-2,L=50
    Cd = 0.00147

    '''    
    
#    Cd = k**2 / ((np.log(zu/z0) - (Ym*(zu/L)))**2)
    Cd = k**2 / ((np.log(zu/z0) - Ym)**2)
    
    return Cd

#********************************************************************************
def get_coefficient_heat(k,zu,z0,Ym,L,zt,zt0,Yt):
    '''
    Works out the coefficient of heat
    
    Reads in: 
      k - von karman constant
      zu - height of anemometer (m)
      z0 - roughness length
      Ym - stability correction for momentum
      L - Monin-Obukhov length (m)
      zt/zh - height of instrument (m)
      zt0/zh0 - transfer coefficient for heat/moisture (m)
      Yt - stability correction for heat
      
    Returns  
      Ch - coefficient of heat
    
    Ch = get_coefficient_heat(k,zu,z0,Ym,L,zt,zt0,Yt)
    
    TESTED!!!

    For k=0.41,zu=20,z0=0.005,Ym=-2,L=50,zt=18.,zt0=0.001,Yt=-2.
    Ch = 0.00176

    '''    
    
#    Ch = k**2 / ((np.log(zu/z0) - (Ym*(zu/L))) * (np.log(zt/zt0) - (Yt*(zt/L)))) # not 100% sure about zt - slightly diff eq to Berry 2009
    Ch = k**2 / ((np.log(zu/z0) - Ym) * (np.log(zt/zt0) - Yt)) # not 100% sure about zt - slightly diff eq to Berry 2009
    
    return Ch

#********************************************************************************
def get_vt(at,shu):
    '''
    Works out the virtual temperature - using the specific humidity as a proxy for mixing ratio
    Based on AMS glossary - ignoring the density increment for liquid water

    Reads in: 
      at = air temperature in deg C (needs to be converted to Kelvin)
      shu = specific humidity in g/kg (needs to be converted to g/g)
      
    Returns  
      vt - virtual temperature in Kelvin
    
    vt = get_vt(15.,8.)
    
    TESTED!!!

    For at=10., shu=8.
    vt = 289.54 K (16.39 deg C)

    '''    
    
    # Convert air temperature from deg C to Kelvin
    conv_at = at + 273.15
    
    # Convert specific humidity from g/kg to g/g
    conv_shu = shu / 1000.
    
    # Calculate vt 
    epsilon = 0.622
    vt = (conv_at * (1 + conv_shu / epsilon)) / (1 + conv_shu)
    
    return vt

#********************************************************************************
def get_vt_surf(t0,q0):
    '''
    Works out the virtual temperature at the surface - using the specific humidity at surface (0.98 of qsat(SST)) as a proxy for mixing ratio
    Based on AMS glossary - ignoring the density increment for liquid water
    
    Reads in: 
      t0 = air temperature in deg C at surface (the SST!) (needs to be converted to Kelvin)
      q0 = specific humidity in g/kg at surface (0.98*qsat(SST)) (needs to be converted to g/g)
      
    Returns  
      vt0 - virtual temperature at the surface in Kelvin
    
    vt0 = get_vt_surf(10.,7.45)
    
    TESTED!!!

    For t0=10., q0=7.45
    vt0 = 284.42 K (11.27 deg C)

    '''    
    
    # Convert air temperature from deg C to Kelvin
    conv_t0 = t0 + 273.15
    
    # Convert specific humidity from g/kg to g/g
    conv_q0 = q0 / 1000.
    
    # Calculate vt 
    epsilon = 0.622
    vt0 = (conv_t0 * (1 + (conv_q0 / epsilon))) / (1 + conv_q0)
    
    return vt0
    
#********************************************************************************
def get_vpt(at,shu,zt):
    '''
    Works out the virtual potential temperature - using the specific humidity as a proxy for mixing ratio
    Based on Stull 1988 and AMS glossary - ignoring the density increment for liquid water
    
    Reads in: 
      at = air temperature in deg C (needs to be converted to Kelvin)
      shu = specific humidity in g/kg (needs to be converted to g/g)
      zt = height of instrument in (m) (all gets a bit interesting because at is usually lower than u)
      
    Returns  
      vpt - virtual potential temperature in Kelvin
    
    vpt = get_vpt(15.,8)
    
    TESTED!!!

    For at=15., shu=8, zt = 18.
    vpt = 289.72 K (16.57 deg C)

    NOTES: 
    Could use Pressure at obs height and standard pressure (1013 or 1000) to calculate potential temperature but we don't always have it
    Could have incorporated the density increment for liquid water but I don't know how to calculate that
    Could have used mixing ratio instead of specific humidity

    '''    
    
    # Convert air temperature from deg C to Kelvin
    conv_at = at + 273.15
    
    # Convert specific humidity from g/kg to g/g
    conv_shu = shu / 1000.

    # Calculate the potential temperature first
    g = 9.81 # accelaration due to gravity (m/s^2)
    Cp = 1004.67 * (1 + (0.84*conv_shu)) # specific heat capacity (J/kg/K) Stull 1988
    pt = conv_at + ((g * zt) / Cp)  # Stull 1988
    # This is usually calculated using pressure T*((P0/P)**0.286) but we don't always have a pressure ob
        
    # Calculate vpt 
    # Stull 1988 and AMS say this should be vpt = pt * (1 + (0.61*r) - rL) where rL is mixing ratio of liquid water.
    # Stull 1988 says virtual temperature should be vt = T * (1+ (0.61*r) - rL)
    # AMS says that virtual temperature without the density increment dur to liquid water is T * (1+r/epsilon)/(1+r)
    # So - does that mean that we can calculate the vpt ignoring the density component because we have no info on it? 
    epsilon = 0.622
    vpt = (pt * (1 + (conv_shu / epsilon))) / (1 + conv_shu)
    
    return vpt 

#********************************************************************************
def get_vpt_surf(t0,q0,zt_surf):
    '''
    Works out the virtual potential temperature at the surface - using the specific humidity at the surface (0.98*qsat(SST) 
    as a proxy for mixing ratio and the neutral stability heat transfer coeficient 0.001 (Smith 1988)
    Based on Stull 1988 and AMS glossary - ignoring the density increment for liquid water
    
    Reads in: 
      t0 = air temperature at the surface (SST) in deg C (needs to be converted to Kelvin)
      q0 = specific humidity at the surface (0.98*qsat(SST)) in g/kg (needs to be converted to g/g)
      zt_surf = height at surface is 0? Not the neutral stability heat transfer coeficient 0.001 (Smith 1988) - or should it be?
      
    Returns  
      vpt0 - virtual potential temperature at the surface in Kelvin
    
    vpt0 = get_vpt_surf(10.,7.45,0.0)
    
    TESTED!!!

    For t0=10., q0=7.45, zt_surf = 0
    vpt0 = 284.42 K (11.27 deg C)
    
    NOTES: 
    Could use Pressure at obs height and standard pressure (1013 or 1000) to calculate potential temperature but we don't always have it
    Could have incorporated the density increment for liquid water but I don't know how to calculate that
    Could have used mixing ratio instead of specific humidity

    '''    
    
    # Convert air temperature from deg C to Kelvin
    conv_t0 = t0 + 273.15
    
    # Convert specific humidity from g/kg to g/g
    conv_q0 = q0 / 1000.

    # Calculate the potential temperature first
    g = 9.81 # accelaration due to gravity (m/s^2)
    Cp = 1004.67 * (1 + (0.84*conv_q0)) # specific heat capacity (J/kg/K) Stull 1988
    pt0 = conv_t0 + ((g * zt_surf) / Cp)  # Stull 1988
    # This is usually calculated using pressure T*((P0/P)**0.286) but we don't always have a pressure ob
        
    # Calculate vpt 
    # Stull 1988 and AMS say this should be vpt = pt * (1 + (0.61*r) - rL) where rL is mixing ratio of liquid water.
    # Stull 1988 says virtual temperature should be vt = T * (1+ (0.61*r) - rL)
    # AMS says that virtual temperature without the density increment dur to liquid water is T * (1+r/epsilon)/(1+r)
    # So - does that mean that we can calculate the vpt ignoring the density component because we have no info on it? 
    epsilon = 0.622
    vpt0 = (pt0 * (1 + (conv_q0 / epsilon))) / (1 + conv_q0)
    
    return vpt0 

#********************************************************************************
def get_buoyancy_flux(Ch,u,vpt0,vpt):
    '''
    Works out the surface buoyancy flux
    Not 100% sure whether this requuires virtual temperature or virtual potential temperature
    
    Reads in: 
      Ch = coefficient of heat
      u = wind speed (m/s)
      vpt0/v/vtt0 = virtual (potential) temperature at the surface (K) (could be virtual temperature at surface?)
      vpt = virtual (potential) temperature (K) (could be virtual temperature)
      
    Returns  
      B0 - surface buoyancy flux
    
    # With vpt and vpt0
    B0 = get_buoyancy_flux(0.00176,3.,284.42,289.72)
    # With vt and vt0
    B0 = get_buoyancy_flux(0.00176,3.,284.42,289.54)
    
    TESTED!!!

    For Ch=0.00176,u=3.,vpt0=284.42,vpt=289.72
    B0 = -0.00096
    For Ch=0.00176,u=3.,vt0=284.42,vt=289.54
    B0 = -0.00093
    
    NOTES: 
    Virtual potential temperature or potential temperature?

    '''    
    
    g = 9.81 # accelaration due to gravity (m/s^2)
    B0 = Ch * u * (g/vpt0) * (vpt0 - vpt)
    
    return B0 

#********************************************************************************
def get_bretherton_u_star(Cd,u):
    '''
    Works out the friction velocity from Bretherton Lecture 6
    
    Reads in: 
      Cd = coefficient of drag
      u = wind speed (m/s)
      
    Returns  
      u_star - friction velocity
    
    u_star = get_bretherton_u_star(0.0015,3.)
    
    TESTED!!!

    For Cd=0.00147,u=3.
    u_star = 0.1150
    
    NOTES: 
    Getting a little confused with what height we should be using. Cd based on 
    height of anemometer. Ch based on height of anemometer and height of thermometer.

    '''    
    
    u_star = np.sqrt(Cd * (u**2))
        
    return u_star

#********************************************************************************
def get_roughness_length(u10n):
    '''
    Works out the roughness length Smith 1980
    
    Reads in: 
      u10n = neutral wind speed at 10m (m/s)
      
    Returns  
      z0 - roughness length
    
    z0 = get_roughness_length(4.915)
    
    TESTED!!!

    For u10n=4.915
    z0 = 0.0009
    
    NOTES: 
    u10n = 0.915 or 0.155 
    z0 = 0.0007 or 0.0006 (or at u=1. 0.0007)	
    u10n = 4.915 or 4.155 
    z0 = 0.0009 or 0.0009 (or at u=5. 0.0009)	
    u10n = 9.915 or 9.155  	
    z0 = 0.0013 or 0.0012 (or at u=10. 0.0012)

    '''    
    
    z0 = (0.61 + (0.063 * u10n)) / 1000.
        
    return z0

#********************************************************************************
def get_MO_length(u_star,k,B0,vpt):
    '''
    Works out the Monin-Obukhov length from Bretherton Lecture 6
    
    Reads in: 
      u_star = friction velocity (m/s)
      k = von karman constant
      B0 = surface buoyancy flux
      vpt = virtual (potential) temperature (K) - only if using Stull 1988 algorithm
      
    Returns  
      Lres = Monin-Obukhov length (m)
    
    # Using BO calculated from vpt and vpt0
    Lres = get_MO_length(0.1150,0.41,-0.0095,289.72)
    # Using BO calculated from vt and vt0
    Lres = get_MO_length(0.1150,0.41,-0.0092,289.54)
    
    TESTED!!!

    The Bretherton method gives a very small L. This could be correct and just need iteration.
    However, it seems unlikley that L would be 0.04m. Perhaps I've got Ch wrong? Or B0? For L to 
    be a reasonable number B0 would need to be < 0.0009.
    I have therefore also tried Stull 1988 which has a different equation. This then assumes that 
    B0 is equal to the (overbar_w' * overbar_vpt')s in Stull 1988. I'm not 100% sure this is the 
    case but it looks better. Best to try iterating and see where we end up.
    For u_star=0.1150,k=0.41,B0=-0.0095 (vpt=289.72,vpt0=284.42)
    LresB = 0.3896, LresS = 11.5054
    For u_star=0.1150,k=0.41,B0=-0.0092 (vt=289.54,vt0=284.42)
    LresB = 0.4160, LresS = 12.2768
    
    NOTES: 
    After testing the Bretherton version just doesn't seem to work so I'm finalising it using Stull 1988

    '''    
    
    # Bretherton (seems too small, unless Ch isn't right - too large? B0 basically needs to be tiny!
    Lres = - (u_star**3 / (k*B0))
    # Stull 1988 - assuming B0 is the same as the (overbar_w' * overbar_vpt')s ?
    #g = 9.81 # accelaration due to gravity (m/s/s)
    #Lres = (-vpt * (u_star**3)) / (k*g*B0)
        
    return Lres

# DAVID BERRY'S CODE
# =============================================================================
# Function to calculate fluxes and perform height corrections
# =============================================================================
def calc_flux(wind_speed_observed, air_temp_observed, spec_hum_observed, sea_temp, sea_level_pressure, height_wind, height_temp, height_hum):
# convert values to expected units
    air_temp_observed = air_temp_observed + 273.16 + height_temp*ADIABATIC_LAPSE
    spec_hum_observed = spec_hum_observed * 0.001
    sea_temp = sea_temp + 273.16
    spec_hum_sea      = calc_spec_hum_sea( sea_temp, sea_level_pressure )*0.001
# set initial z/L to 0
    zol = 0.0 # z/L
    tol = 0.0 # 10 / L
# set 10m neutral values to observed
    wind_speed_10m_neutral = copy.copy(wind_speed_observed)
    air_temp_10m_neutral   = copy.copy(air_temp_observed)
    spec_hum_10m_neutral   = copy.copy(spec_hum_observed)
    virt_temp_10m_neutral  = air_temp_10m_neutral*(1.0 + 0.61*spec_hum_10m_neutral)
# set initial cdn
    cdn = calc_drag_coeff_neutral( wind_speed_10m_neutral )
# set initial cd
    cd  = calc_drag_coeff( cdn, height_wind, zol )
# calculate u* based on cdn
    ustar = math.pow(cd*wind_speed_observed*wind_speed_observed, 0.5)
# set t*, q* to zero
    tstar = 0.0
    qstar = 0.0
    # iterate
    iteration = 0
    converged = 0
    while (converged == 0) & (iteration < 10) :
#     copy old / initial values to store
        wind_old     = copy.copy(wind_speed_10m_neutral)
        air_temp_old = copy.copy(air_temp_10m_neutral)
        spec_hum_old = copy.copy(spec_hum_10m_neutral)
        ustar_old    = copy.copy(ustar)
        tstar_old    = copy.copy(tstar)
        qstar_old    = copy.copy(qstar)
#     calculate u10n
        print("u10n): ",wind_speed_10m_neutral,wind_speed_observed,calc_psi_m(zol),zol)
	# KW In neutral conditions - shouldn't psi_m be 0 and so not be present?
        #wind_speed_10m_neutral = wind_speed_observed - (ustar/VON_KARMAN)*( math.log( height_wind / 10.0) - calc_psi_m(zol))
        wind_speed_10m_neutral = wind_speed_observed - (ustar/VON_KARMAN)*( math.log( height_wind / 10.0))
#     calculate cdn, cd
        cdn = calc_drag_coeff_neutral( wind_speed_10m_neutral )
        cd  = calc_drag_coeff( cdn , height_wind, zol )
#     update u*
        ustar = math.pow(cd*wind_speed_observed*wind_speed_observed, 0.5)
#     calculate ct, cq
        ct = calc_ct(height_temp, height_wind, zol, cd, cdn)
        cq = calc_cq(height_hum,  height_wind, zol, cd, cdn)
#     now t*, q*
        tstar = ct * wind_speed_observed*(air_temp_observed - sea_temp) / ustar
        qstar = cq * wind_speed_observed*(spec_hum_observed - spec_hum_sea) / ustar
#     update t10n, q10n
        # KW Not sure why the PSI element is included here so have tried without
        #air_temp_10m_neutral = air_temp_observed - (tstar / VON_KARMAN)*( math.log(height_temp / 10.0) - calc_psi_t(height_temp * zol / height_wind)   )
        #spec_hum_10m_neutral = spec_hum_observed - (qstar / VON_KARMAN)*( math.log(height_hum  / 10.0) - calc_psi_q(height_hum  * zol / height_wind)   )
        air_temp_10m_neutral = air_temp_observed - (tstar / VON_KARMAN)*( math.log(height_temp / 10.0) )
        spec_hum_10m_neutral = spec_hum_observed - (qstar / VON_KARMAN)*( math.log(height_hum  / 10.0) )
#     calculate virtual temperature and virtual temperature flux
        virt_temp_10m_neutral = air_temp_10m_neutral*(1.0 + 0.61*spec_hum_10m_neutral)
        tstarv                = tstar + 0.61*air_temp_10m_neutral*qstar
#     calculate z/L etc
        # KW Should this not be ustar cubed? Stull 1988 p181 - apparently not as it doesn't work
        zol = GRAVITY*VON_KARMAN*height_wind*tstarv / ( virt_temp_10m_neutral * ustar * ustar )
        tol = 10*zol / height_wind
#     check if converged
        converged = 1
        if abs( wind_old - wind_speed_10m_neutral ) > 0.01 :
            converged = 0
        if abs( air_temp_old - air_temp_10m_neutral ) > 0.01 :
            converged = 0
        if abs( spec_hum_old - spec_hum_10m_neutral )*1000 > 0.05 :
            converged = 0
        if abs( ustar_old - ustar ) > 0.005 :
            converged = 0
        if abs( tstar_old - tstar ) > 0.001 :
            converged = 0
        if abs( qstar_old - qstar )*1000 > 0.0005 :
            converged = 0
        iteration += 1
# calculate fluxes
    rho = (0.34838*sea_level_pressure)/virt_temp_10m_neutral # density of air
    spec_heat_capacity = 1004.67 * (1+0.00084*spec_hum_sea) # specific heat
    lat_heat_vapourization = (2.501 - 0.00237*(sea_temp - 273.16))*1000000. # latent heat of vapourization
    flux_sensible = -tstar*ustar*spec_heat_capacity*rho # sensible heat flux
    flux_latent   = -qstar*ustar*lat_heat_vapourization*rho # latent heat flux
    flux_momentum = -rho*ustar*ustar # wind stress
# convert return values back to input units (degC, g / kg)
    wind_speed_10m = wind_speed_observed - (ustar / VON_KARMAN) * ( math.log( height_wind / 10.0   ) - calc_psi_m( zol ) + calc_psi_m( tol )     )
    air_temp_10m   = air_temp_observed   - (tstar / VON_KARMAN) * ( math.log( height_temp / 10.0   ) - calc_psi_t( (height_temp / height_wind)*zol ) + calc_psi_t( tol ) )
    spec_hum_10m   = spec_hum_observed   - (qstar / VON_KARMAN) * ( math.log( height_hum  / 10.0   ) - calc_psi_q( (height_hum  / height_wind)*zol ) + calc_psi_q( tol ) )
    air_temp_10m = air_temp_10m - 273.16 - ADIABATIC_LAPSE*10.0
    spec_hum_10m = spec_hum_10m * 1000.0
    air_temp_10m_neutral = air_temp_10m_neutral - 273.16 - ADIABATIC_LAPSE*10.0
    spec_hum_10m_neutral = spec_hum_10m_neutral * 1000.0
    spec_hum_sea = spec_hum_sea * 1000.0
# 2 m values would be given by 
#    air_temp_10m   = air_temp_observed   - (tstar / VON_KARMAN) * ( math.log( height_temp / 2.0   ) - calc_psi_t( (height_temp / height_wind)*zol ) + calc_psi_t( (2.0/10.0)*tol ) )
#    air_temp_10m   = air_temp_10m - 273.16 - ADIABATIC_LAPSE*2.0
#    similar for spec hum.
# return
    #print(tstar,qstar,20./zol,cd, cdn, ct, cq)
    print("u10m: ",wind_speed_10m)
    
    # KW I only want the relevant bits
    # Create a dictionary of the adjusted values
    AdjDict = {'at_10m':air_temp_10m,
      	       'shu_10m':spec_hum_10m}
        
    # Create a dictionary of height vars for iteration
    HeightVarsDict = {'L':height_wind/zol,
                      'little_zeta':zol,
		      'Ym':calc_psi_m(zol),
		      'Yt':calc_psi_t(zol),
		      'Yq':calc_psi_q(zol),
		      'u_star':ustar,
		      't_star':tstar,
		      'q_star':qstar,
		      'z0':cd,
		      'zt0':ct,
		      'zq0':cq}
    
    return AdjDict, HeightVarsDict

# =============================================================================
# constants
# =============================================================================
GRAVITY           = 9.812
VISCOSITY_DYNAMIC = 0.000014
VON_KARMAN        = 0.4
MISSING_VALUE     = -9999.
PI                = 3.14159265
ALPHA             = 16.0
BETA              = 0.25
GAMMA             = 5.0 # 8.0
ADIABATIC_LAPSE   = 0.00976
# =============================================================================
# function to calculate 10m neutral drag coefficient
# =============================================================================
def calc_drag_coeff_neutral( wind_speed_10m_neutral ):
    # -------------------------------------------------------------------------
    # Inputs 10 m neutral equivalent wind speed (m/s)
    # Outputs 10 m neutral drag coefficient following Smith (1980)
    # -------------------------------------------------------------------------
    # First set to Smith 88 as starting point
    cdn_current = (0.61 + 0.063*wind_speed_10m_neutral)*1E-3
    # Following code is for Smith 1988
    #convergence = 1
    #iteration = 0
    #while convergence > 1E-6:
    #    #  start iteration
    #    cdn_old = cdn_current
    #    ustar2 = cdn_current * wind_speed_10m_neutral * wind_speed_10m_neutral
    #    ustar  = pow(ustar2, 0.5)
    #    # z0 from s88
    #    z0 = (0.011*ustar2)/GRAVITY + 0.11*VISCOSITY_DYNAMIC/ustar
    #    # update cdn_current
    #    cdn_current = pow((VON_KARMAN / math.log( 10 / z0)),2.0)
    #    convergence = abs( cdn_current - cdn_old )
    #    if iteration > 50:
    #        convergence = 0.0
    #        cdn_current = MISSING_VALUE
    #    iteration = iteration + 1
    return cdn_current
# =============================================================================
# function to calculate drag coefficient
# =============================================================================
def calc_drag_coeff( cdn, z, zol):
    # -------------------------------------------------------------------------
    # Inputs:
    #    cdn:            10 m neutral drag coefficient
    #    z:              height of wind speed observation
    #    zol:            z / L (L = Monin Obukhov length
    # -------------------------------------------------------------------------
    stability_correction = calc_psi_m( zol )
    print(cdn, stability_correction)
    cd = 1 + (pow(cdn,0.5)*( math.log(z / 10.0) - stability_correction)) / VON_KARMAN
    cd = cdn / (cd*cd)
    return cd
# =============================================================================
# Function to calculate momentum stability correction
# =============================================================================
def calc_psi_m( zol ):
    if zol < 0:
        x   = pow(1.0 - ALPHA * zol, BETA)
        #psi = 2.0 * math.log( 0.5*(1.0 + x)) + math.log( 0.5*( 1.0 + x*x ) ) - 2*math.atan(x) + 0.5*PI
	# KW This seems to be missing the phi**-1, **-2 and **-1 which makes a difference - doesn't seem to make very much difference in the end
        psi = 2.0 * math.log( 0.5*(1.0 + (x**(-1)))) + math.log( 0.5*( 1.0 + (x**(-2))) ) - 2*math.atan((x**(-1))) + 0.5*PI	
    else:
        psi = -GAMMA * zol
    return psi
# =============================================================================
# Function to calculate momentum stability correction
# =============================================================================
def calc_psi_t( zol ):
    if zol < 0:
        x   = pow((1.0 - ALPHA * zol ), BETA)
        #psi = 2.0 * math.log(  0.5 * (1 + x * x) )
        # KW no x**-1 in the above - doesn't seem to make very much difference in the end
	psi = 2.0 * math.log(  0.5 * (1 + (x**(-1))) )
    else:
        psi = -GAMMA * zol
    return psi
# =============================================================================
# Function to calculate humidity stability correction
# =============================================================================
def calc_psi_q( zol ):
    if zol < 0:
        x   = pow((1.0 - ALPHA * zol ), BETA)
        #psi = 2.0 * math.log(  0.5 * (1 + x * x) )
        # no x**-1 in the above - doesn't seem to make very much difference in the end
	psi = 2.0 * math.log(  0.5 * (1 + (x**(-1))) )
    else:
        psi = -GAMMA * zol
    return psi
# =============================================================================
# Functions to return neutral stanton and dalton numbers
# =============================================================================
def calc_ctn( ):
   return 1.0E-3
def calc_cqn( ):
   return 1.2E-3
# =============================================================================
# Functions to calculate stanton and dalton numbers
# =============================================================================
def calc_ct(zt, zu, zol, cd, cdn ):
    tmp = (math.log( 0.10 * zt ) - calc_psi_t( zt*zol / zu )) / (  VON_KARMAN*pow(cdn, 0.5) )
    ct = calc_ctn() * pow( (cd/cdn) ,0.5) / ( 1.0 + calc_ctn() * tmp )
    return ct
# =============================================================================
def calc_cq(zq, zu, zol, cd, cdn ):
    tmp = (math.log( 0.10 * zq ) - calc_psi_q( zq*zol / zu )) / (  VON_KARMAN*pow(cdn, 0.5) )
    cq = calc_cqn() * pow( (cd/cdn) ,0.5) / ( 1.0 + calc_cqn() * tmp )
    return cq

# =============================================================================
# Function to calculate specific humidity just above the sea surface
# =============================================================================
def calc_spec_hum_sea( sea_temp, sea_level_pressure ):
    svp = 2.1718E08*math.exp( -4157.0 / (sea_temp - 33.91 - 0.16)  )
    vp  = 0.98*svp
    spec_hum_sea = 1000.0*((0.622*vp)/(sea_level_pressure-0.378*vp))
    return spec_hum_sea
