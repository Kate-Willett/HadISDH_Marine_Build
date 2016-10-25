#!/usr/local/sci/bin/python
# PYTHON2.7
# 
# Author: Kate Willett
# Created: 4 April 2016
# Last update: 4 April 2016
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/EUSTACE_SST_MAT/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code reads the ERA 1x1 pentad clims and the OBS 1x1 pentad clims
# It assesses the difference for each obs gridbox and plots some diagnostics
# It tries to characterise any bias, bias adjust ERA and resave as ERAOBS clims
#
# These can then be used to climatology check the marine data
#  
# -----------------------
# LIST OF MODULES
# -----------------------
# inbuilt:
# import datetime as dt
## Folling two lines should be uncommented if using with SPICE or screen
## import matplotlib
## matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import numpy as np
# from matplotlib.dates import date2num,num2date
# import sys, os
# import sys, getopt
# from scipy.optimize import curve_fit,fsolve,leastsq
# from scipy import pi,sqrt,exp
# from scipy.special import erf
# import scipy.stats
# from math import sqrt,pi
# import struct
# from netCDF4 import Dataset
# import pdb # pdb.set_trace() or c 
#
# -----------------------
# DATA
# -----------------------
# ERA 1981-2010 clims:
# /project/hadobs2/hadisdh/marine/otherdata/t2m_pentad_1by1marine_ERA-Interim_data_19792015.nc
# /project/hadobs2/hadisdh/marine/otherdata/td2m_pentad_1by1marine_ERA-Interim_data_19792015.nc
#
# OBS 1981-2010 clims:
# /project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS/ERAclimNBC_1x1_pentad_climatology_from_3hrly.nc
#
# -----------------------
# HOW TO RUN THE CODE
# -----------------------
# make sure the file paths are ok - are we always using ERAclimNBC?
#
# python2.7 CompareERAOBSclims_APR2016.py --typee ERAclimNBC
#
# This runs the code, outputs the plots and stops mid-process so you can then interact with the
# data and then carries on.
# 
# -----------------------
# OUTPUT
# -----------------------
# some plots - 
# differences by latitude for 6 pentads 1, 13, 25, 37, 49, 61:
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/ERAOBSclimdiffs_latdiffs_ERAclimNBC_APR2016.py
# difference maps for 6 pentads 1, 13, 25, 37, 49, 61:
# /data/local/hadkw/HADCRUH2/MARINE/IMAGES/ERAOBSclimdiffs_mapdiffs_ERAclimNBC_APR2016.py
# 
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
# 
# Version 1 (4 April 2016)
# ---------
#  
# Enhancements
#  
# Changes
#  
# Bug fixes
#  
# -----------------------
# OTHER INFORMATION
# -----------------------
#
#************************************************************************
#                                 START
#************************************************************************
import datetime as dt
# Folling two lines should be uncommented if using with SPICE or screen
## import matplotlib
## matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import matplotlib.cm as mpl_cm
import numpy as np
from matplotlib.dates import date2num,num2date
from mpl_toolkits.basemap import Basemap
import sys, os
import sys, getopt
from scipy.optimize import curve_fit,fsolve,leastsq
from scipy import pi,sqrt,exp
from scipy.special import erf
import scipy.stats
from math import sqrt,pi
import struct
from netCDF4 import Dataset
import pdb # pdb.set_trace() or c 

# What date stamp?
nowmon = 'OCT'
nowyear = '2016'

# What are we differencing?
innee1 = 'OBS1' # 'ERA', 'OBS', 'OBS1'
innee2 = 'OBS2' # 'OBS', 'OBS1', 'OBS2'

# What threshold for clim/buddy?
thresh = '55' # '35', '45', '55'

# What source?
source = 'I300' # 'I251' or 'I300'	    					   

#************************************************************************
# Main
#************************************************************************

def main(argv):
    # INPUT PARAMETERS AS STRINGS!!!!
    typee = 'ERAclimNBC'
    ptsplt= [0,12,24,36,48,60]

    try:
        opts, args = getopt.getopt(argv, "hi:",
	                           ["typee="])
    except getopt.GetoptError:
        print 'Usage (as strings) CompareERAOBSclims_APR2016.py --typee <ERAclimNBC>'
	sys.exit(2)

    for opt, arg in opts:
        if opt == "--typee":
            try:
                typee = arg
            except:
                sys.exit("Failed: typee not a string")

    print(typee)
#    pdb.set_trace()
    			
    mdi=-1e30
		
    INDIR = '/project/hadobs2/hadisdh/marine/'
    if (innee1 == 'ERA'):
        InERAclimAT = 'otherdata/t2m_pentad_1by1marine_ERA-Interim_data_19792015.nc'
        InERAclimDPT = 'otherdata/td2m_pentad_1by1marine_ERA-Interim_data_19792015.nc'
        InERAclimSHU = 'otherdata/q2m_pentad_1by1marine_ERA-Interim_data_19792015.nc'
        InERAclimVAP = 'otherdata/e2m_pentad_1by1marine_ERA-Interim_data_19792015.nc'
        InERAclimCRH = 'otherdata/rh2m_pentad_1by1marine_ERA-Interim_data_19792015.nc'
        InERAclimCWB = 'otherdata/tw2m_pentad_1by1marine_ERA-Interim_data_19792015.nc'
        InERAclimDPD = 'otherdata/dpd2m_pentad_1by1marine_ERA-Interim_data_19792015.nc'
    elif (innee1 == 'OBS'):
        InERAclimAT = 'otherdata/t2m_ERAclimNBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
        InERAclimDPT = 'otherdata/td2m_ERAclimNBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
        InERAclimSHU = 'otherdata/q2m_ERAclimNBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
        InERAclimVAP = 'otherdata/e2m_ERAclimNBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
        InERAclimCRH = 'otherdata/rh2m_ERAclimNBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
        InERAclimCWB = 'otherdata/tw2m_ERAclimNBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
        InERAclimDPD = 'otherdata/dpd2m_ERAclimNBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    elif (innee1 == 'OBS1'):
        InERAclimAT = 'otherdata/t2m_OBSclim1NBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
        InERAclimDPT = 'otherdata/td2m_OBSclim1NBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
        InERAclimSHU = 'otherdata/q2m_OBSclim1NBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
        InERAclimVAP = 'otherdata/e2m_OBSclim1NBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
        InERAclimCRH = 'otherdata/rh2m_OBSclim1NBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
        InERAclimCWB = 'otherdata/tw2m_OBSclim1NBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
        InERAclimDPD = 'otherdata/dpd2m_OBSclim1NBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    
    InOBSclimAT = 'otherdata/t2m_'+typee+'_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    InOBSclimDPT = 'otherdata/td2m_'+typee+'_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    InOBSclimSHU = 'otherdata/q2m_'+typee+'_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    InOBSclimVAP = 'otherdata/e2m_'+typee+'_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    InOBSclimCRH = 'otherdata/rh2m_'+typee+'_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    InOBSclimCWB = 'otherdata/tw2m_'+typee+'_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    InOBSclimDPD = 'otherdata/dpd2m_'+typee+'_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    
    OUTDIR = '/data/local/hadkw/HADCRUH2/MARINE/'
    if ((innee1 == 'ERA') & (innee2 == 'OBS')):
        OutLatsFilAT = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_latdiffs_AT_'+typee+'_'+nowmon+nowyear
        OutMapsFilAT = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_mapdiffs_AT_'+typee+'_'+nowmon+nowyear
        OutLatsFilDPT = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_latdiffs_DPT_'+typee+'_'+nowmon+nowyear
        OutMapsFilDPT = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_mapdiffs_DPT_'+typee+'_'+nowmon+nowyear
        OutLatsFilSHU = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_latdiffs_SHU_'+typee+'_'+nowmon+nowyear
        OutMapsFilSHU = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_mapdiffs_SHU_'+typee+'_'+nowmon+nowyear
        OutLatsFilVAP = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_latdiffs_VAP_'+typee+'_'+nowmon+nowyear
        OutMapsFilVAP = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_mapdiffs_VAP_'+typee+'_'+nowmon+nowyear
        OutLatsFilCRH = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_latdiffs_CRH_'+typee+'_'+nowmon+nowyear
        OutMapsFilCRH = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_mapdiffs_CRH_'+typee+'_'+nowmon+nowyear
        OutLatsFilCWB = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_latdiffs_CWB_'+typee+'_'+nowmon+nowyear
        OutMapsFilCWB = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_mapdiffs_CWB_'+typee+'_'+nowmon+nowyear
        OutLatsFilDPD = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_latdiffs_DPD_'+typee+'_'+nowmon+nowyear
        OutMapsFilDPD = 'IMAGES/ERAOBSclimdiffs_'+source+'_'+thresh+'_mapdiffs_DPD_'+typee+'_'+nowmon+nowyear

        OutSDLatsFilAT = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_latdiffs_AT_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilAT = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_mapdiffs_AT_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilDPT = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_latdiffs_DPT_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilDPT = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_mapdiffs_DPT_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilSHU = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_latdiffs_SHU_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilSHU = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_mapdiffs_SHU_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilVAP = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_latdiffs_VAP_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilVAP = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_mapdiffs_VAP_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilCRH = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_latdiffs_CRH_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilCRH = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_mapdiffs_CRH_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilCWB = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_latdiffs_CWB_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilCWB = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_mapdiffs_CWB_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilDPD = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_latdiffs_DPD_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilDPD = 'IMAGES/ERAOBSclimSDdiffs_'+source+'_'+thresh+'_mapdiffs_DPD_'+typee+'_'+nowmon+nowyear
    elif ((innee1 == 'OBS') & (innee2 == 'OBS1')):
        OutLatsFilAT = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_latdiffs_AT_'+typee+'_'+nowmon+nowyear
        OutMapsFilAT = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_mapdiffs_AT_'+typee+'_'+nowmon+nowyear
        OutLatsFilDPT = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_latdiffs_DPT_'+typee+'_'+nowmon+nowyear
        OutMapsFilDPT = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_mapdiffs_DPT_'+typee+'_'+nowmon+nowyear
        OutLatsFilSHU = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_latdiffs_SHU_'+typee+'_'+nowmon+nowyear
        OutMapsFilSHU = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_mapdiffs_SHU_'+typee+'_'+nowmon+nowyear
        OutLatsFilVAP = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_latdiffs_VAP_'+typee+'_'+nowmon+nowyear
        OutMapsFilVAP = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_mapdiffs_VAP_'+typee+'_'+nowmon+nowyear
        OutLatsFilCRH = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_latdiffs_CRH_'+typee+'_'+nowmon+nowyear
        OutMapsFilCRH = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_mapdiffs_CRH_'+typee+'_'+nowmon+nowyear
        OutLatsFilCWB = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_latdiffs_CWB_'+typee+'_'+nowmon+nowyear
        OutMapsFilCWB = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_mapdiffs_CWB_'+typee+'_'+nowmon+nowyear
        OutLatsFilDPD = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_latdiffs_DPD_'+typee+'_'+nowmon+nowyear
        OutMapsFilDPD = 'IMAGES/OBSOBS1climdiffs_'+source+'_'+thresh+'_mapdiffs_DPD_'+typee+'_'+nowmon+nowyear

        OutSDLatsFilAT = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_latdiffs_AT_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilAT = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_mapdiffs_AT_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilDPT = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_latdiffs_DPT_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilDPT = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_mapdiffs_DPT_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilSHU = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_latdiffs_SHU_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilSHU = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_mapdiffs_SHU_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilVAP = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_latdiffs_VAP_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilVAP = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_mapdiffs_VAP_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilCRH = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_latdiffs_CRH_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilCRH = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_mapdiffs_CRH_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilCWB = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_latdiffs_CWB_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilCWB = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_mapdiffs_CWB_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilDPD = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_latdiffs_DPD_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilDPD = 'IMAGES/OBSOBS1climSDdiffs_'+source+'_'+thresh+'_mapdiffs_DPD_'+typee+'_'+nowmon+nowyear
    elif ((innee1 == 'OBS1') & (innee2 == 'OBS2')):
        OutLatsFilAT = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_latdiffs_AT_'+typee+'_'+nowmon+nowyear
        OutMapsFilAT = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_mapdiffs_AT_'+typee+'_'+nowmon+nowyear
        OutLatsFilDPT = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_latdiffs_DPT_'+typee+'_'+nowmon+nowyear
        OutMapsFilDPT = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_mapdiffs_DPT_'+typee+'_'+nowmon+nowyear
        OutLatsFilSHU = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_latdiffs_SHU_'+typee+'_'+nowmon+nowyear
        OutMapsFilSHU = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_mapdiffs_SHU_'+typee+'_'+nowmon+nowyear
        OutLatsFilVAP = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_latdiffs_VAP_'+typee+'_'+nowmon+nowyear
        OutMapsFilVAP = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_mapdiffs_VAP_'+typee+'_'+nowmon+nowyear
        OutLatsFilCRH = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_latdiffs_CRH_'+typee+'_'+nowmon+nowyear
        OutMapsFilCRH = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_mapdiffs_CRH_'+typee+'_'+nowmon+nowyear
        OutLatsFilCWB = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_latdiffs_CWB_'+typee+'_'+nowmon+nowyear
        OutMapsFilCWB = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_mapdiffs_CWB_'+typee+'_'+nowmon+nowyear
        OutLatsFilDPD = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_latdiffs_DPD_'+typee+'_'+nowmon+nowyear
        OutMapsFilDPD = 'IMAGES/OBS1OBS2climdiffs_'+source+'_'+thresh+'_mapdiffs_DPD_'+typee+'_'+nowmon+nowyear

        OutSDLatsFilAT = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_latdiffs_AT_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilAT = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_mapdiffs_AT_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilDPT = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_latdiffs_DPT_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilDPT = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_mapdiffs_DPT_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilSHU = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_latdiffs_SHU_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilSHU = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_mapdiffs_SHU_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilVAP = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_latdiffs_VAP_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilVAP = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_mapdiffs_VAP_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilCRH = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_latdiffs_CRH_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilCRH = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_mapdiffs_CRH_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilCWB = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_latdiffs_CWB_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilCWB = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_mapdiffs_CWB_'+typee+'_'+nowmon+nowyear
        OutSDLatsFilDPD = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_latdiffs_DPD_'+typee+'_'+nowmon+nowyear
        OutSDMapsFilDPD = 'IMAGES/OBS1OBS2climSDdiffs_'+source+'_'+thresh+'_mapdiffs_DPD_'+typee+'_'+nowmon+nowyear
    
    # create empty arrays for lats
    lats = np.arange(180,0,-1)-90.5
    lons = np.arange(0,360,1)-179.5
    longrid,latgrid = np.meshgrid(lons,lats) # latgrid should have latitudes repeated along each row of longitude
    
    # read in ERA ncs - these files have their lats from 90 to -90
    clim = Dataset(INDIR+InERAclimAT)
    ERAAT = np.array(clim.variables['t2m_clims'][:])
    ERAATsd = np.array(clim.variables['t2m_stdevs'][:])
    clim = Dataset(INDIR+InERAclimDPT)
    ERADPT = np.array(clim.variables['td2m_clims'][:])
    ERADPTsd = np.array(clim.variables['td2m_stdevs'][:])
    clim = Dataset(INDIR+InERAclimSHU)
    ERASHU = np.array(clim.variables['q2m_clims'][:])
    ERASHUsd = np.array(clim.variables['q2m_stdevs'][:])
    clim = Dataset(INDIR+InERAclimVAP)
    ERAVAP = np.array(clim.variables['e2m_clims'][:])
    ERAVAPsd = np.array(clim.variables['e2m_stdevs'][:])
    clim = Dataset(INDIR+InERAclimCRH)
    ERACRH = np.array(clim.variables['rh2m_clims'][:])
    ERACRHsd = np.array(clim.variables['rh2m_stdevs'][:])
    clim = Dataset(INDIR+InERAclimCWB)
    ERACWB = np.array(clim.variables['tw2m_clims'][:])
    ERACWBsd = np.array(clim.variables['tw2m_stdevs'][:])
    clim = Dataset(INDIR+InERAclimDPD)
    ERADPD = np.array(clim.variables['dpd2m_clims'][:])
    ERADPDsd = np.array(clim.variables['dpd2m_stdevs'][:])
    
    # read in OBS ncs - these files have their lats from 90 to -90
    clim = Dataset(INDIR+InOBSclimAT)
    OBSAT = np.array(clim.variables['t2m_clims'][:])
    OBSATsd = np.array(clim.variables['t2m_stdevs'][:])
    clim = Dataset(INDIR+InOBSclimDPT)
    OBSDPT = np.array(clim.variables['td2m_clims'][:])
    OBSDPTsd = np.array(clim.variables['td2m_stdevs'][:])
    clim = Dataset(INDIR+InOBSclimSHU)
    OBSSHU = np.array(clim.variables['q2m_clims'][:])
    OBSSHUsd = np.array(clim.variables['q2m_stdevs'][:])
    clim = Dataset(INDIR+InOBSclimVAP)
    OBSVAP = np.array(clim.variables['e2m_clims'][:])
    OBSVAPsd = np.array(clim.variables['e2m_stdevs'][:])
    clim = Dataset(INDIR+InOBSclimCRH)
    OBSCRH = np.array(clim.variables['rh2m_clims'][:])
    OBSCRHsd = np.array(clim.variables['rh2m_stdevs'][:])
    clim = Dataset(INDIR+InOBSclimCWB)
    OBSCWB = np.array(clim.variables['tw2m_clims'][:])
    OBSCWBsd = np.array(clim.variables['tw2m_stdevs'][:])
    clim = Dataset(INDIR+InOBSclimDPD)
    OBSDPD = np.array(clim.variables['dpd2m_clims'][:])
    OBSDPDsd = np.array(clim.variables['dpd2m_stdevs'][:])
    
    del clim
    
    # create ATdiffs
    OBSminERAAT = np.empty_like(ERAAT)
    OBSminERAAT.fill(mdi)

    OBSminERAAT[np.where(OBSAT > mdi)] = OBSAT[np.where(OBSAT > mdi)] - ERAAT[np.where(OBSAT > mdi)]
            
    # create DPTdiffs
    OBSminERADPT = np.empty_like(ERAAT)
    OBSminERADPT.fill(mdi)
    
    OBSminERADPT[np.where(OBSDPT > mdi)] = OBSDPT[np.where(OBSDPT > mdi)] - ERADPT[np.where(OBSDPT > mdi)]

    # create SHUdiffs
    OBSminERASHU = np.empty_like(ERAAT)
    OBSminERASHU.fill(mdi)
    
    OBSminERASHU[np.where(OBSSHU > mdi)] = OBSSHU[np.where(OBSSHU > mdi)] - ERASHU[np.where(OBSSHU > mdi)]

    # create VAPdiffs
    OBSminERAVAP = np.empty_like(ERAAT)
    OBSminERAVAP.fill(mdi)
    
    OBSminERAVAP[np.where(OBSVAP > mdi)] = OBSVAP[np.where(OBSVAP > mdi)] - ERAVAP[np.where(OBSVAP > mdi)]

    # create CRHdiffs
    OBSminERACRH = np.empty_like(ERAAT)
    OBSminERACRH.fill(mdi)
    
    OBSminERACRH[np.where(OBSCRH > mdi)] = OBSCRH[np.where(OBSCRH > mdi)] - ERACRH[np.where(OBSCRH > mdi)]

    # create CWBdiffs
    OBSminERACWB = np.empty_like(ERAAT)
    OBSminERACWB.fill(mdi)
    
    OBSminERACWB[np.where(OBSCWB > mdi)] = OBSCWB[np.where(OBSCWB > mdi)] - ERACWB[np.where(OBSCWB > mdi)]

    # create DPDdiffs
    OBSminERADPD = np.empty_like(ERAAT)
    OBSminERADPD.fill(mdi)
    
    OBSminERADPD[np.where(OBSDPD > mdi)] = OBSDPD[np.where(OBSDPD > mdi)] - ERADPD[np.where(OBSDPD > mdi)]
    
    # plot diffs by latitude = this is a 3 row by 2 column plot
    
    xpos = [0.1, 0.6,0.1,0.6,0.1,0.6]
    ypos = [0.7,0.7,0.37,0.37,0.04,0.04]
    xfat = [0.37,0.37,0.37,0.37,0.37,0.37]
    ytall = [0.28,0.28,0.28,0.28,0.28,0.28]

    lettees = ['a)','b)','c)','d)','e)','f)']

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference ('+innee2+'-'+innee1+') degrees C')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERAAT[ptsplt[pp],:,:] # assuming time, lat, lon
#        pdb.set_trace()
	axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),
	                  np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
	axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        diff25 = np.empty_like(lats)
        diff25.fill(mdi)
        diff75 = np.empty_like(lats)
        diff75.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutLatsFilAT+".eps")
    plt.savefig(OUTDIR+OutLatsFilAT+".png")

    plt.clf()
    plt.close()
    
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference ('+innee2+'-'+innee1+') degrees C')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERADPT[ptsplt[pp],:,:] # assuming time, long, lat
        axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        sddiff = np.empty_like(lats)
        sddiff.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])   # np.median(pltdiff[np.where(pltdiff[:,ltts] > mdi)[0],ltts])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutLatsFilDPT+".eps")
    plt.savefig(OUTDIR+OutLatsFilDPT+".png")

    plt.clf()
    plt.close()
    
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference ('+innee2+'-'+innee1+') g/kg')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERASHU[ptsplt[pp],:,:] # assuming time, long, lat
        axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        sddiff = np.empty_like(lats)
        sddiff.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])   # np.median(pltdiff[np.where(pltdiff[:,ltts] > mdi)[0],ltts])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutLatsFilSHU+".eps")
    plt.savefig(OUTDIR+OutLatsFilSHU+".png")

    plt.clf()
    plt.close()
    
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference ('+innee2+'-'+innee1+') hPa')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERAVAP[ptsplt[pp],:,:] # assuming time, long, lat
        axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        sddiff = np.empty_like(lats)
        sddiff.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])   # np.median(pltdiff[np.where(pltdiff[:,ltts] > mdi)[0],ltts])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutLatsFilVAP+".eps")
    plt.savefig(OUTDIR+OutLatsFilVAP+".png")

    plt.clf()
    plt.close()
    
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference ('+innee2+'-'+innee1+') %rh')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERACRH[ptsplt[pp],:,:] # assuming time, long, lat
        axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        sddiff = np.empty_like(lats)
        sddiff.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])   # np.median(pltdiff[np.where(pltdiff[:,ltts] > mdi)[0],ltts])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutLatsFilCRH+".eps")
    plt.savefig(OUTDIR+OutLatsFilCRH+".png")

    plt.clf()
    plt.close()
    
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference ('+innee2+'-'+innee1+') degrees C')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERACWB[ptsplt[pp],:,:] # assuming time, long, lat
        axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        sddiff = np.empty_like(lats)
        sddiff.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])   # np.median(pltdiff[np.where(pltdiff[:,ltts] > mdi)[0],ltts])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutLatsFilCWB+".eps")
    plt.savefig(OUTDIR+OutLatsFilCWB+".png")

    plt.clf()
    plt.close()
    
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference ('+innee2+'-'+innee1+') degrees C')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERADPD[ptsplt[pp],:,:] # assuming time, long, lat
        axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        sddiff = np.empty_like(lats)
        sddiff.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])   # np.median(pltdiff[np.where(pltdiff[:,ltts] > mdi)[0],ltts])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutLatsFilDPD+".eps")
    plt.savefig(OUTDIR+OutLatsFilDPD+".png")


    # set up colour scheme red blue
    cmap=plt.get_cmap('RdYlBu') # PiYG
        
    cmaplist=[cmap(i) for i in range(cmap.N)]
    for loo in range((cmap.N/2)-30,(cmap.N/2)+30):
        cmaplist.remove(cmaplist[(cmap.N/2)-30]) # remove the very pale colours in the middle
    #cmaplist.remove(cmaplist[(cmap.N/2)-10:(cmap.N/2)+10]) # remove the very pale colours in the middle

# remove the darkest and lightest (white and black) - and reverse
#    for loo in range(40):
#        cmaplist.remove(cmaplist[loo])
    cmaplist.reverse()
#    for loo in range(10):
#        cmaplist.remove(cmaplist[loo])
#    cmaplist.reverse()

    cmap=cmap.from_list('this_cmap',cmaplist,cmap.N)
    
    bounds=np.array([-15,-10,-5,-2,0,2,5,10,15])
    strbounds=["%3d" % i for i in bounds]
    norm=mpl_cm.colors.BoundaryNorm(bounds,cmap.N)

    # plot diff maps
    
    xpos = [0.1, 0.6,0.1,0.6,0.1,0.6]
    ypos = [0.74,0.74,0.45,0.45,0.16,0.16]
    xfat = [0.37,0.37,0.37,0.37,0.37,0.37]
    ytall = [0.24,0.24,0.24,0.24,0.24,0.24]

    plt.clf()
    plt.close()
    
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERAAT[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,innee2+'-'+innee1+' difference (deg C)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutMapsFilAT+".eps")
    plt.savefig(OUTDIR+OutMapsFilAT+".png")

    # set up colour scheme red blue
    cmap=plt.get_cmap('BrBG') # PiYG
        
    cmaplist=[cmap(i) for i in range(cmap.N)]
    for loo in range((cmap.N/2)-30,(cmap.N/2)+30):
        cmaplist.remove(cmaplist[(cmap.N/2)-30]) # remove the very pale colours in the middle
    #cmaplist.remove(cmaplist[(cmap.N/2)-10:(cmap.N/2)+10]) # remove the very pale colours in the middle

# remove the darkest and lightest (white and black) - and reverse
#    for loo in range(40):
#        cmaplist.remove(cmaplist[loo])
#    cmaplist.reverse()
#    for loo in range(10):
#        cmaplist.remove(cmaplist[loo])
#    cmaplist.reverse()

    cmap=cmap.from_list('this_cmap',cmaplist,cmap.N)

    plt.clf()
    plt.close()
    
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERADPT[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,innee2+'-'+innee1+' difference (deg C)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutMapsFilDPT+".eps")
    plt.savefig(OUTDIR+OutMapsFilDPT+".png")


    plt.clf()
    plt.close()
    
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERASHU[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,innee2+'-'+innee1+' difference (g/kg)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutMapsFilSHU+".eps")
    plt.savefig(OUTDIR+OutMapsFilSHU+".png")

    plt.clf()
    plt.close()
    
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERAVAP[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,innee2+'-'+innee1+' difference (hPa)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutMapsFilVAP+".eps")
    plt.savefig(OUTDIR+OutMapsFilVAP+".png")

    plt.clf()
    plt.close()
    
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERACRH[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,innee2+'-'+innee1+' difference (%rh)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutMapsFilCRH+".eps")
    plt.savefig(OUTDIR+OutMapsFilCRH+".png")

    plt.clf()
    plt.close()
    
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERACWB[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,innee2+'-'+innee1+' difference (deg C)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutMapsFilCWB+".eps")
    plt.savefig(OUTDIR+OutMapsFilCWB+".png")

    plt.clf()
    plt.close()

    # set up colour scheme red blue
    cmap=plt.get_cmap('BrBG') # PiYG
        
    cmaplist=[cmap(i) for i in range(cmap.N)]
    for loo in range((cmap.N/2)-30,(cmap.N/2)+30):
        cmaplist.remove(cmaplist[(cmap.N/2)-30]) # remove the very pale colours in the middle
    #cmaplist.remove(cmaplist[(cmap.N/2)-10:(cmap.N/2)+10]) # remove the very pale colours in the middle

# remove the darkest and lightest (white and black) - and reverse
#    for loo in range(40):
#        cmaplist.remove(cmaplist[loo])
    cmaplist.reverse()
#    for loo in range(10):
#        cmaplist.remove(cmaplist[loo])
#    cmaplist.reverse()

    cmap=cmap.from_list('this_cmap',cmaplist,cmap.N)
    
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERADPD[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,innee2+'-'+innee1+' difference (deg C)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutMapsFilDPD+".eps")
    plt.savefig(OUTDIR+OutMapsFilDPD+".png")


    # create ATdiffs
    OBSminERAAT = np.empty_like(ERAAT)
    OBSminERAAT.fill(mdi)

    OBSminERAAT[np.where(OBSATsd > mdi)] = OBSATsd[np.where(OBSATsd > mdi)] - ERAATsd[np.where(OBSATsd > mdi)]
            
    # create DPTdiffs
    OBSminERADPT = np.empty_like(ERAAT)
    OBSminERADPT.fill(mdi)
    
    OBSminERADPT[np.where(OBSDPTsd > mdi)] = OBSDPTsd[np.where(OBSDPTsd > mdi)] - ERADPTsd[np.where(OBSDPTsd > mdi)]

    # create SHUdiffs
    OBSminERASHU = np.empty_like(ERAAT)
    OBSminERASHU.fill(mdi)
    
    OBSminERASHU[np.where(OBSSHUsd > mdi)] = OBSSHUsd[np.where(OBSSHUsd > mdi)] - ERASHUsd[np.where(OBSSHUsd > mdi)]

    # create VAPdiffs
    OBSminERAVAP = np.empty_like(ERAAT)
    OBSminERAVAP.fill(mdi)
    
    OBSminERAVAP[np.where(OBSVAPsd > mdi)] = OBSVAPsd[np.where(OBSVAPsd > mdi)] - ERAVAPsd[np.where(OBSVAPsd > mdi)]

    # create CRHdiffs
    OBSminERACRH = np.empty_like(ERAAT)
    OBSminERACRH.fill(mdi)
    
    OBSminERACRH[np.where(OBSCRHsd > mdi)] = OBSCRHsd[np.where(OBSCRHsd > mdi)] - ERACRHsd[np.where(OBSCRHsd > mdi)]

    # create CWBdiffs
    OBSminERACWB = np.empty_like(ERAAT)
    OBSminERACWB.fill(mdi)
    
    OBSminERACWB[np.where(OBSCWBsd > mdi)] = OBSCWBsd[np.where(OBSCWBsd > mdi)] - ERACWBsd[np.where(OBSCWBsd > mdi)]

    # create DPDdiffs
    OBSminERADPD = np.empty_like(ERAAT)
    OBSminERADPD.fill(mdi)
    
    OBSminERADPD[np.where(OBSDPDsd > mdi)] = OBSDPDsd[np.where(OBSDPDsd > mdi)] - ERADPDsd[np.where(OBSDPDsd > mdi)]
    
    # plot diffs by latitude = this is a 3 row by 2 column plot
    
    xpos = [0.1, 0.6,0.1,0.6,0.1,0.6]
    ypos = [0.7,0.7,0.37,0.37,0.04,0.04]
    xfat = [0.37,0.37,0.37,0.37,0.37,0.37]
    ytall = [0.28,0.28,0.28,0.28,0.28,0.28]

    lettees = ['a)','b)','c)','d)','e)','f)']

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference '+innee2+'-'+innee1+' degrees C')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERAAT[ptsplt[pp],:,:] # assuming time, lat, lon
#        pdb.set_trace()
	axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),
	                  np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
	axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        diff25 = np.empty_like(lats)
        diff25.fill(mdi)
        diff75 = np.empty_like(lats)
        diff75.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDLatsFilAT+".eps")
    plt.savefig(OUTDIR+OutSDLatsFilAT+".png")

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference '+innee2+'-'+innee1+' degrees C')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERADPT[ptsplt[pp],:,:] # assuming time, long, lat
        axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        sddiff = np.empty_like(lats)
        sddiff.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])   # np.median(pltdiff[np.where(pltdiff[:,ltts] > mdi)[0],ltts])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDLatsFilDPT+".eps")
    plt.savefig(OUTDIR+OutSDLatsFilDPT+".png")

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference '+innee2+'-'+innee1+' g/kg')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERASHU[ptsplt[pp],:,:] # assuming time, long, lat
        axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        sddiff = np.empty_like(lats)
        sddiff.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])   # np.median(pltdiff[np.where(pltdiff[:,ltts] > mdi)[0],ltts])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDLatsFilSHU+".eps")
    plt.savefig(OUTDIR+OutSDLatsFilSHU+".png")

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference '+innee2+'-'+innee1+' hPa')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERAVAP[ptsplt[pp],:,:] # assuming time, long, lat
        axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        sddiff = np.empty_like(lats)
        sddiff.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])   # np.median(pltdiff[np.where(pltdiff[:,ltts] > mdi)[0],ltts])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDLatsFilVAP+".eps")
    plt.savefig(OUTDIR+OutSDLatsFilVAP+".png")

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference '+innee2+'-'+innee1+' %rh')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERACRH[ptsplt[pp],:,:] # assuming time, long, lat
        axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        sddiff = np.empty_like(lats)
        sddiff.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])   # np.median(pltdiff[np.where(pltdiff[:,ltts] > mdi)[0],ltts])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDLatsFilCRH+".eps")
    plt.savefig(OUTDIR+OutSDLatsFilCRH+".png")

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference '+innee2+'-'+innee1+' degrees C')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERACWB[ptsplt[pp],:,:] # assuming time, long, lat
        axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        sddiff = np.empty_like(lats)
        sddiff.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])   # np.median(pltdiff[np.where(pltdiff[:,ltts] > mdi)[0],ltts])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDLatsFilCWB+".eps")
    plt.savefig(OUTDIR+OutSDLatsFilCWB+".png")

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        #axarr[pp].set_xlim(0,60)
        axarr[pp].set_ylim(-91,91)
        axarr[pp].set_xlabel('Difference '+innee2+'-'+innee1+' degrees C')
        axarr[pp].set_ylabel('Latitude')
        pltdiff = OBSminERADPD[ptsplt[pp],:,:] # assuming time, long, lat
        axarr[pp].scatter(np.reshape(pltdiff[np.where(pltdiff > mdi)],len(pltdiff[np.where(pltdiff > mdi)])),np.reshape(latgrid[np.where(pltdiff > mdi)],len(latgrid[np.where(pltdiff > mdi)])),c='grey',marker='o',linewidth=0.,s=1)
        axarr[pp].plot(np.zeros(180),lats,c='black')
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)
        # for each degree of latitude, plot a line for the median estimate
        # we may want to use some kind of polynomial?
        mediandiff = np.empty_like(lats)
        mediandiff.fill(mdi)
        sddiff = np.empty_like(lats)
        sddiff.fill(mdi)
        for ltt in range(180):
            if (len(pltdiff[np.where(pltdiff[:,ltt] > mdi)[0],ltt]) > 0):
	        if (ltt == 0):
		    ltts = [ltt,ltt+1]
	        if ((ltt > 0) & (ltt < 179)):
		    ltts = [ltt-1,ltt,ltt+1]
	        if (ltt == 179):
		    ltts = [ltt-1,ltt]
		diffmini = pltdiff[:,ltts]    
	        mediandiff[ltt] = np.median(diffmini[np.where(diffmini > mdi)])   # np.median(pltdiff[np.where(pltdiff[:,ltts] > mdi)[0],ltts])
	        diff25[ltt],diff75[ltt] = np.percentile(diffmini[np.where(diffmini > mdi)],[25,75])
        axarr[pp].plot(mediandiff[np.where(mediandiff > mdi)[0]],lats[np.where(mediandiff > mdi)[0]],c='red')
        axarr[pp].plot(diff25[np.where(diff25 > mdi)[0]],lats[np.where(diff25 > mdi)[0]],c='red',linestyle='dashed')
        axarr[pp].plot(diff75[np.where(diff75 > mdi)[0]],lats[np.where(diff75 > mdi)[0]],c='red',linestyle='dashed')
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDLatsFilDPD+".eps")
    plt.savefig(OUTDIR+OutSDLatsFilDPD+".png")


    # set up colour scheme
    cmap=plt.get_cmap('RdYlBu') # PiYG
        
    cmaplist=[cmap(i) for i in range(cmap.N)]
    for loo in range((cmap.N/2)-30,(cmap.N/2)+30):
        cmaplist.remove(cmaplist[(cmap.N/2)-30]) # remove the very pale colours in the middle
    #cmaplist.remove(cmaplist[(cmap.N/2)-10:(cmap.N/2)+10]) # remove the very pale colours in the middle

# remove the darkest and lightest (white and black) - and reverse
#    for loo in range(40):
#        cmaplist.remove(cmaplist[loo])
    cmaplist.reverse()
#    for loo in range(10):
#        cmaplist.remove(cmaplist[loo])
#    cmaplist.reverse()

    cmap=cmap.from_list('this_cmap',cmaplist,cmap.N)
    
    bounds=np.array([-15,-10,-5,-2,0,2,5,10,15])
    strbounds=["%3d" % i for i in bounds]
    norm=mpl_cm.colors.BoundaryNorm(bounds,cmap.N)

    # plot diff maps
    
    xpos = [0.1, 0.6,0.1,0.6,0.1,0.6]
    ypos = [0.74,0.74,0.45,0.45,0.16,0.16]
    xfat = [0.37,0.37,0.37,0.37,0.37,0.37]
    ytall = [0.24,0.24,0.24,0.24,0.24,0.24]

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERAAT[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,innee2+'-'+innee1+' difference (deg C)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDMapsFilAT+".eps")
    plt.savefig(OUTDIR+OutSDMapsFilAT+".png")

    # set up colour scheme red blue
    cmap=plt.get_cmap('BrBG') # PiYG
        
    cmaplist=[cmap(i) for i in range(cmap.N)]
    for loo in range((cmap.N/2)-30,(cmap.N/2)+30):
        cmaplist.remove(cmaplist[(cmap.N/2)-30]) # remove the very pale colours in the middle
    #cmaplist.remove(cmaplist[(cmap.N/2)-10:(cmap.N/2)+10]) # remove the very pale colours in the middle

# remove the darkest and lightest (white and black) - and reverse
#    for loo in range(40):
#        cmaplist.remove(cmaplist[loo])
#    cmaplist.reverse()
#    for loo in range(10):
#        cmaplist.remove(cmaplist[loo])
#    cmaplist.reverse()

    cmap=cmap.from_list('this_cmap',cmaplist,cmap.N)

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERADPT[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,innee2+'-'+innee1+' difference (deg C)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDMapsFilDPT+".eps")
    plt.savefig(OUTDIR+OutSDMapsFilDPT+".png")

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERASHU[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,innee2+'-'+innee1+' difference (g/kg)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDMapsFilSHU+".eps")
    plt.savefig(OUTDIR+OutSDMapsFilSHU+".png")

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERAVAP[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,innee2+'-'+innee1+' difference (hPa)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDMapsFilVAP+".eps")
    plt.savefig(OUTDIR+OutSDMapsFilVAP+".png")

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERACRH[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,'OBS-ERA difference (%rh)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDMapsFilCRH+".eps")
    plt.savefig(OUTDIR+OutSDMapsFilCRH+".png")

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERACWB[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,innee2+'-'+innee1+' difference (deg C)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDMapsFilCWB+".eps")
    plt.savefig(OUTDIR+OutSDMapsFilCWB+".png")

    # set up colour scheme red blue
    cmap=plt.get_cmap('BrBG') # PiYG
        
    cmaplist=[cmap(i) for i in range(cmap.N)]
    for loo in range((cmap.N/2)-30,(cmap.N/2)+30):
        cmaplist.remove(cmaplist[(cmap.N/2)-30]) # remove the very pale colours in the middle
    #cmaplist.remove(cmaplist[(cmap.N/2)-10:(cmap.N/2)+10]) # remove the very pale colours in the middle

# remove the darkest and lightest (white and black) - and reverse
#    for loo in range(40):
#        cmaplist.remove(cmaplist[loo])
    cmaplist.reverse()
#    for loo in range(10):
#        cmaplist.remove(cmaplist[loo])
#    cmaplist.reverse()

    cmap=cmap.from_list('this_cmap',cmaplist,cmap.N)

    plt.clf()
    f,axarr=plt.subplots(6,figsize=(10,12),sharex=False)	    #6,18

    for pp in range(6):
        axarr[pp].set_position([xpos[pp],ypos[pp],xfat[pp],ytall[pp]])
        axarr[pp].set_ylim(-91,90)
        axarr[pp].set_xlim(-180,180)
        axarr[pp].set_ylabel('Latitude')
        axarr[pp].set_xlabel('Longitude')
        pltdiff = OBSminERADPD[ptsplt[pp],:,:] # assuming time, long, lat
	plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,innee2+'-'+innee1+' difference (deg C)',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(OUTDIR+OutSDMapsFilDPD+".eps")
    plt.savefig(OUTDIR+OutSDMapsFilDPD+".png")

    #pdb.set_trace()

if __name__ == '__main__':
    
    main(sys.argv[1:])




#************************************************************************
