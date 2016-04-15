import math
import copy
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
GAMMA             = 5.0   # 8.0
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
        # KW Why is psi included in the calculation for neutral - and why only once?
        #air_temp_10m_neutral = air_temp_observed - (tstar / VON_KARMAN)*( math.log(height_temp / 10.0) - calc_psi_t(height_temp * zol / height_wind)   )
        #spec_hum_10m_neutral = spec_hum_observed - (qstar / VON_KARMAN)*( math.log(height_hum  / 10.0) - calc_psi_q(height_hum  * zol / height_wind)   )
        air_temp_10m_neutral = air_temp_observed - (tstar / VON_KARMAN)*( math.log(height_temp / 10.0)  )
        spec_hum_10m_neutral = spec_hum_observed - (qstar / VON_KARMAN)*( math.log(height_hum  / 10.0)  )
#     calculate virtual temperature and virtual temperature flux
        virt_temp_10m_neutral = air_temp_10m_neutral*(1.0 + 0.61*spec_hum_10m_neutral)
	# KW I don't really understand what this is - how it is the vertical flux of mementum and heat
        tstarv                = tstar + 0.61*air_temp_10m_neutral*qstar
	print("T_v and tstarv: ",tstarv," ",virt_temp_10m_neutral)
#     calculate z/L etc
        # KW Should this not be ustar**3? Stull 1988 p181 It doesn't work if it is.
	# Is this because tstarv is already divided by ustar?
        zol = GRAVITY*VON_KARMAN*height_wind*tstarv / ( virt_temp_10m_neutral * ustar * ustar )
        print("zol: ",zol)
	print("zu / zol: ",height_wind / zol)
	print("L: ",-(virt_temp_10m_neutral*(ustar**3)) / (GRAVITY*VON_KARMAN*tstarv))
        #zol = GRAVITY*VON_KARMAN*height_wind*tstarv / ( virt_temp_10m_neutral * ustar**3 )
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
    print(tstarv,tstar,qstar,20./zol,cd, cdn, ct, cq)
    return flux_sensible, flux_latent, flux_momentum, wind_speed_10m, wind_speed_10m_neutral, air_temp_10m, air_temp_10m_neutral, spec_hum_10m, spec_hum_10m_neutral, spec_hum_sea, ustar, tol

def main():
    ta = 15. # 18.0
    u = 3 # 8.0 DOESN'T LIKE IT IF u is too low in very stable conditions
    q = 8. # 12.0
    ts = 10. # 20.0
#    sen, lat, mom, u10, u10n, t10, t10n, q10, q10n, qsea, ustar, tol  = calc_flux( u, ta, q, ts, 998.1, 20.0, 20.0, 20.0   )
    sen, lat, mom, u10, u10n, t10, t10n, q10, q10n, qsea, ustar, tol  = calc_flux( u, ta, q, ts, 998.1, 20.0, 18.0, 18.0   )
    print u, u10n, u10
    print ta, t10n, t10
    print q, q10n, q10
    print ts, qsea
    print ustar, tol

main()




