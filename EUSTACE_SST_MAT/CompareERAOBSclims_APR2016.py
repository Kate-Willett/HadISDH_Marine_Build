#!/usr/local/sci/bin/python
# PYTHON3
# 
# Author: Kate Willett
# Created: 4 April 2016
# Last update: 5 April 2019
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/EUSTACE_SST_MAT/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code reads 1x1 pentad clims from two runs (e.g. ERA then ERAclimNBC
# It assesses the difference for each obs gridbox and plots some diagnostics
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
## python2.7 CompareERAOBSclims_APR2016.py --typee1 ERA-Interim --typee2 OBSclim2NBC
#
# module load scitools/default-current
# python CompareERAOBSclims_APR2016.py --typee1 ERA-Interim --typee2 OBSclim2NBC
#
# typee1 and typee2 can be: ERA-Interim, ERAclimNBC, OBSclim1NBC, OBSclim2NBC, OBSclim2BClocal, OBSclim2BClocalship 
#
# This runs the code, outputs the plots and stops mid-process so you can then interact with the
# data and then carries on.
# 
# -----------------------
# OUTPUT
# -----------------------
# some plots - 
# differences by latitude for 6 pentads 1, 13, 25, 37, 49, 61:
# /data/users/hadkw/WORKING_HADISDH/MARINE/IMAGES/ERAOBSclimdiffs_latdiffs_ERAclimNBC_APR2016.py
# difference maps for 6 pentads 1, 13, 25, 37, 49, 61:
# /data/users/hadkw/WORKING_HADISDH/MARINE/IMAGES/ERAOBSclimdiffs_mapdiffs_ERAclimNBC_APR2016.py
# 
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
#
# Version 2 (5 April 2019)
# ---------
#  
# Enhancements
# This can now compare any two climatologies at 1x1 pentad - might later add capacity to compare 5x5 monthly
#  
# Changes
# This is now based on functions rather than straight code - clearer
# This now uses python 3
#  
# Bug fixes 
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
#from mpl_toolkits.basemap import Basemap
import cartopy.crs as ccrs
import cartopy.feature as cpf
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
nowmon = 'MAR'
nowyear = '2019'

# What threshold for clim/buddy?
thresh = '55' # '35', '45', '55'

# What source?
source = 'I300' # 'I251' or 'I300'	    					   

#************************************************************************
# SUBROUTINES #
#************************************************************************
# PlotLatDistDiffs
def PlotLatDistDiffs(TheFile,BminA,latgrid,lats,mdi,ptsplt,typee1,typee2,Unit):

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
        axarr[pp].set_xlabel('Difference ('+typee2+'-'+typee1+') '+Unit)
        axarr[pp].set_ylabel('Latitude')
        pltdiff = BminA[ptsplt[pp],:,:] # assuming time, lat, lon
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
#    plt.savefig(TheFile+".eps")
    plt.savefig(TheFile+".png")

    return
    
#************************************************************************
# PlotClimMapDiffs
def PlotClimMapDiffs(TheFile,BminA,longrid,latgrid,mdi,ptsplt,VarColour,ColourDir,typee1,typee2,Unit):

    lettees = ['a)','b)','c)','d)','e)','f)']

    # set up colour scheme red blue
    cmap=plt.get_cmap(VarColour) # PiYG
        
    cmaplist=[cmap(i) for i in range(cmap.N)]
    for loo in range(int((cmap.N/2)-30),int((cmap.N/2)+30)):
        cmaplist.remove(cmaplist[int((cmap.N/2)-30)]) # remove the very pale colours in the middle
    #cmaplist.remove(cmaplist[(cmap.N/2)-10:(cmap.N/2)+10]) # remove the very pale colours in the middle

# remove the darkest and lightest (white and black) - and reverse
#    for loo in range(40):
#        cmaplist.remove(cmaplist[loo])
    if (ColourDir == 'Reverse'):
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
        pltdiff = BminA[ptsplt[pp],:,:] # assuming time, long, lat
        plottee=axarr[pp].scatter(longrid[np.where(pltdiff > mdi)],latgrid[np.where(pltdiff > mdi)],c=pltdiff[np.where(pltdiff > mdi)],cmap=cmap,norm=norm,marker='o',linewidth=0.,s=4)
        axarr[pp].annotate(lettees[pp]+' Pentad: '+str((pp*12)+1),xy=(0.03,0.92),xycoords='axes fraction',size=12)

    cbax=f.add_axes([0.1,0.06,0.8,0.02])
    cb=plt.colorbar(plottee,cax=cbax,orientation='horizontal',ticks=bounds) #, extend=extend
    cb.ax.tick_params(labelsize=12) 
    cb.ax.set_xticklabels(strbounds)
    plt.figtext(0.5,0.02,typee2+'-'+typee1+' difference ('+Unit+')',size=14,ha='center')    
    
     # save plots as eps and png
#    plt.savefig(TheFile+".eps")
    plt.savefig(TheFile+".png")

    return

#************************************************************************
# Main
#************************************************************************
def main(argv):
    # INPUT PARAMETERS AS STRINGS!!!!
    typee1 = 'ERA-Interim'
    typee2 = 'ERAclimNBC'
    ptsplt= [0,12,24,36,48,60]

    try:
        opts, args = getopt.getopt(argv, "hi:",
	                           ["typee1=", "typee2="])
    except getopt.GetoptError:
        print('Usage (as strings) CompareERAOBSclims_APR2016.py --typee1 <ERA-Interim> --typee2 <OBSclim2NBC>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == "--typee1":
            try:
                typee1 = arg 
            except:
                sys.exit("Failed: typee1 not a string")

        if opt == "--typee2":
            try:
                typee2 = arg 
            except:
                sys.exit("Failed: typee2 not a string")

    print(typee1,typee2)
#    pdb.set_trace()
    			
    mdi=-1e30
		
    INDIR = '/project/hadobs2/hadisdh/marine/'
    if (typee1 == 'ERA-Interim'):
        MiddleBit = 'pentad_1by1marine_ERA-Interim_data_19792015.nc'
    if (typee1 == 'ERAclimNBC'):
        MiddleBit = 'ERAclimNBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    if (typee1 == 'OBSclim1NBC'):
        MiddleBit = 'OBSclim1NBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    if (typee1 == 'OBSclim2NBC'):
        MiddleBit = 'OBSclim2NBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    if (typee1 == 'OBSclim2BClocal'):
        MiddleBit = 'OBSclim2BClocal_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    if (typee1 == 'OBSclim2BClocalship'): # When I copied these files to /otherdata I added 'ship' to be clear
        MiddleBit = 'OBSclim2BClocalship_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'

    InAclimAT = 'otherdata/t2m_'+MiddleBit
    InAclimDPT = 'otherdata/td2m_'+MiddleBit
    InAclimSHU = 'otherdata/q2m_'+MiddleBit
    InAclimVAP = 'otherdata/e2m_'+MiddleBit
    InAclimCRH = 'otherdata/rh2m_'+MiddleBit
    InAclimCWB = 'otherdata/tw2m_'+MiddleBit
    InAclimDPD = 'otherdata/dpd2m_'+MiddleBit

    if (typee2 == 'ERA-Interim'):
        MiddleBit = 'pentad_1by1marine_ERA-Interim_data_19792015.nc'
    if (typee2 == 'ERAclimNBC'):
        MiddleBit = 'ERAclimNBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    if (typee2 == 'OBSclim1NBC'):
        MiddleBit = 'OBSclim1NBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    if (typee2 == 'OBSclim2NBC'):
        MiddleBit = 'OBSclim2NBC_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    if (typee2 == 'OBSclim2BClocal'):
        MiddleBit = 'OBSclim2BClocal_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    if (typee2 == 'OBSclim2BClocalship'): # When I copied these files to /otherdata I added 'ship' to be clear
        MiddleBit = 'OBSclim2BClocalship_1x1_pentad_climatology_stdev_from_5x5_monthly_both_relax_INFILLED.nc'
    
    InBclimAT = 'otherdata/t2m_'+MiddleBit
    InBclimDPT = 'otherdata/td2m_'+MiddleBit
    InBclimSHU = 'otherdata/q2m_'+MiddleBit
    InBclimVAP = 'otherdata/e2m_'+MiddleBit
    InBclimCRH = 'otherdata/rh2m_'+MiddleBit
    InBclimCWB = 'otherdata/tw2m_'+MiddleBit
    InBclimDPD = 'otherdata/dpd2m_'+MiddleBit
    
    OUTDIR = '/data/users/hadkw/WORKING_HADISDH/MARINE/IMAGES/CLIMDIFFS/'+typee1+typee2
    OutLatsFilAT = 'climdiffs_'+source+'_'+thresh+'_latdiffs_AT_'+nowmon+nowyear
    OutMapsFilAT = 'climdiffs_'+source+'_'+thresh+'_mapdiffs_AT_'+nowmon+nowyear
    OutLatsFilDPT = 'climdiffs_'+source+'_'+thresh+'_latdiffs_DPT_'+nowmon+nowyear
    OutMapsFilDPT = 'climdiffs_'+source+'_'+thresh+'_mapdiffs_DPT_'+nowmon+nowyear
    OutLatsFilSHU = 'climdiffs_'+source+'_'+thresh+'_latdiffs_SHU_'+nowmon+nowyear
    OutMapsFilSHU = 'climdiffs_'+source+'_'+thresh+'_mapdiffs_SHU_'+nowmon+nowyear
    OutLatsFilVAP = 'climdiffs_'+source+'_'+thresh+'_latdiffs_VAP_'+nowmon+nowyear
    OutMapsFilVAP = 'climdiffs_'+source+'_'+thresh+'_mapdiffs_VAP_'+nowmon+nowyear
    OutLatsFilCRH = 'climdiffs_'+source+'_'+thresh+'_latdiffs_CRH_'+nowmon+nowyear
    OutMapsFilCRH = 'climdiffs_'+source+'_'+thresh+'_mapdiffs_CRH_'+nowmon+nowyear
    OutLatsFilCWB = 'climdiffs_'+source+'_'+thresh+'_latdiffs_CWB_'+nowmon+nowyear
    OutMapsFilCWB = 'climdiffs_'+source+'_'+thresh+'_mapdiffs_CWB_'+nowmon+nowyear
    OutLatsFilDPD = 'climdiffs_'+source+'_'+thresh+'_latdiffs_DPD_'+nowmon+nowyear
    OutMapsFilDPD = 'climdiffs_'+source+'_'+thresh+'_mapdiffs_DPD_'+nowmon+nowyear

    OutSDLatsFilAT = 'climSDdiffs_'+source+'_'+thresh+'_latdiffs_AT_'+nowmon+nowyear
    OutSDMapsFilAT = 'climSDdiffs_'+source+'_'+thresh+'_mapdiffs_AT_'+nowmon+nowyear
    OutSDLatsFilDPT = 'climSDdiffs_'+source+'_'+thresh+'_latdiffs_DPT_'+nowmon+nowyear
    OutSDMapsFilDPT = 'climSDdiffs_'+source+'_'+thresh+'_mapdiffs_DPT_'+nowmon+nowyear
    OutSDLatsFilSHU = 'climSDdiffs_'+source+'_'+thresh+'_latdiffs_SHU_'+nowmon+nowyear
    OutSDMapsFilSHU = 'climSDdiffs_'+source+'_'+thresh+'_mapdiffs_SHU_'+nowmon+nowyear
    OutSDLatsFilVAP = 'climSDdiffs_'+source+'_'+thresh+'_latdiffs_VAP_'+nowmon+nowyear
    OutSDMapsFilVAP = 'climSDdiffs_'+source+'_'+thresh+'_mapdiffs_VAP_'+nowmon+nowyear
    OutSDLatsFilCRH = 'climSDdiffs_'+source+'_'+thresh+'_latdiffs_CRH_'+nowmon+nowyear
    OutSDMapsFilCRH = 'climSDdiffs_'+source+'_'+thresh+'_mapdiffs_CRH_'+nowmon+nowyear
    OutSDLatsFilCWB = 'climSDdiffs_'+source+'_'+thresh+'_latdiffs_CWB_'+nowmon+nowyear
    OutSDMapsFilCWB = 'climSDdiffs_'+source+'_'+thresh+'_mapdiffs_CWB_'+nowmon+nowyear
    OutSDLatsFilDPD = 'climSDdiffs_'+source+'_'+thresh+'_latdiffs_DPD_'+nowmon+nowyear
    OutSDMapsFilDPD = 'climSDdiffs_'+source+'_'+thresh+'_mapdiffs_DPD_'+nowmon+nowyear
    
    # create empty arrays for lats
    lats = np.arange(180,0,-1)-90.5
    lons = np.arange(0,360,1)-179.5
    longrid,latgrid = np.meshgrid(lons,lats) # latgrid should have latitudes repeated along each row of longitude
    
    # read in A ncs - these files have their lats from 90 to -90
    clim = Dataset(INDIR+InAclimAT)
    AAT = np.array(clim.variables['t2m_clims'][:])
    AATsd = np.array(clim.variables['t2m_stdevs'][:])
    clim = Dataset(INDIR+InAclimDPT)
    ADPT = np.array(clim.variables['td2m_clims'][:])
    ADPTsd = np.array(clim.variables['td2m_stdevs'][:])
    clim = Dataset(INDIR+InAclimSHU)
    ASHU = np.array(clim.variables['q2m_clims'][:])
    ASHUsd = np.array(clim.variables['q2m_stdevs'][:])
    clim = Dataset(INDIR+InAclimVAP)
    AVAP = np.array(clim.variables['e2m_clims'][:])
    AVAPsd = np.array(clim.variables['e2m_stdevs'][:])
    clim = Dataset(INDIR+InAclimCRH)
    ACRH = np.array(clim.variables['rh2m_clims'][:])
    ACRHsd = np.array(clim.variables['rh2m_stdevs'][:])
    clim = Dataset(INDIR+InAclimCWB)
    ACWB = np.array(clim.variables['tw2m_clims'][:])
    ACWBsd = np.array(clim.variables['tw2m_stdevs'][:])
    clim = Dataset(INDIR+InAclimDPD)
    ADPD = np.array(clim.variables['dpd2m_clims'][:])
    ADPDsd = np.array(clim.variables['dpd2m_stdevs'][:])
    
    # read in B ncs - these files have their lats from 90 to -90
    clim = Dataset(INDIR+InBclimAT)
    BAT = np.array(clim.variables['t2m_clims'][:])
    BATsd = np.array(clim.variables['t2m_stdevs'][:])
    clim = Dataset(INDIR+InBclimDPT)
    BDPT = np.array(clim.variables['td2m_clims'][:])
    BDPTsd = np.array(clim.variables['td2m_stdevs'][:])
    clim = Dataset(INDIR+InBclimSHU)
    BSHU = np.array(clim.variables['q2m_clims'][:])
    BSHUsd = np.array(clim.variables['q2m_stdevs'][:])
    clim = Dataset(INDIR+InBclimVAP)
    BVAP = np.array(clim.variables['e2m_clims'][:])
    BVAPsd = np.array(clim.variables['e2m_stdevs'][:])
    clim = Dataset(INDIR+InBclimCRH)
    BCRH = np.array(clim.variables['rh2m_clims'][:])
    BCRHsd = np.array(clim.variables['rh2m_stdevs'][:])
    clim = Dataset(INDIR+InBclimCWB)
    BCWB = np.array(clim.variables['tw2m_clims'][:])
    BCWBsd = np.array(clim.variables['tw2m_stdevs'][:])
    clim = Dataset(INDIR+InBclimDPD)
    BDPD = np.array(clim.variables['dpd2m_clims'][:])
    BDPDsd = np.array(clim.variables['dpd2m_stdevs'][:])
    
    del clim
    
    # Create CLIMATOLOGY difference fields where there are non-missing data
    # create ATdiffs
    BminAAT = np.empty_like(AAT)
    BminAAT.fill(mdi)

    BminAAT[np.where((BAT > mdi) & (AAT > mdi))] = BAT[np.where((BAT > mdi) & (AAT > mdi))] - AAT[np.where((BAT > mdi) & (AAT > mdi))]
#    print('Check the differencing')
#    pdb.set_trace()
            
    # create DPTdiffs
    BminADPT = np.empty_like(AAT)
    BminADPT.fill(mdi)
    
    BminADPT[np.where((BDPT > mdi) & (ADPT > mdi))] = BDPT[np.where((BDPT > mdi) & (ADPT > mdi))] - ADPT[np.where((BDPT > mdi) & (ADPT > mdi))]

    # create SHUdiffs
    BminASHU = np.empty_like(AAT)
    BminASHU.fill(mdi)
    
    BminASHU[np.where((BSHU > mdi) & (ASHU > mdi))] = BSHU[np.where((BSHU > mdi) & (ASHU > mdi))] - ASHU[np.where((BSHU > mdi) & (ASHU > mdi))]

    # create VAPdiffs
    BminAVAP = np.empty_like(AAT)
    BminAVAP.fill(mdi)
    
    BminAVAP[np.where((BVAP > mdi) & (AVAP > mdi))] = BVAP[np.where((BVAP > mdi) & (AVAP > mdi))] - AVAP[np.where((BVAP > mdi) & (AVAP > mdi))]

    # create CRHdiffs
    BminACRH = np.empty_like(AAT)
    BminACRH.fill(mdi)
    
    BminACRH[np.where((BCRH > mdi) & (ACRH > mdi))] = BCRH[np.where((BCRH > mdi) & (ACRH > mdi))] - ACRH[np.where((BCRH > mdi) & (ACRH > mdi))]

    # create CWBdiffs
    BminACWB = np.empty_like(AAT)
    BminACWB.fill(mdi)
    
    BminACWB[np.where((BCWB > mdi) & (ACWB > mdi))] = BCWB[np.where((BCWB > mdi) & (ACWB > mdi))] - ACWB[np.where((BCWB > mdi) & (ACWB > mdi))]

    # create DPDdiffs
    BminADPD = np.empty_like(AAT)
    BminADPD.fill(mdi)
    
    BminADPD[np.where((BDPD > mdi) & (ADPD > mdi))] = BDPD[np.where((BDPD > mdi) & (ADPD > mdi))] - ADPD[np.where((BDPD > mdi) & (ADPD > mdi))]
    
    # plot diffs by latitude for each variable = this is a 3 row by 2 column plot
    PlotLatDistDiffs(OUTDIR+OutLatsFilAT,BminAAT,latgrid,lats,mdi,ptsplt,typee1,typee2,'deg C')  
    PlotLatDistDiffs(OUTDIR+OutLatsFilDPT,BminADPT,latgrid,lats,mdi,ptsplt,typee1,typee2,'deg C')  
    PlotLatDistDiffs(OUTDIR+OutLatsFilSHU,BminASHU,latgrid,lats,mdi,ptsplt,typee1,typee2,'g/kg')  
    PlotLatDistDiffs(OUTDIR+OutLatsFilVAP,BminAVAP,latgrid,lats,mdi,ptsplt,typee1,typee2,'hPa')  
    PlotLatDistDiffs(OUTDIR+OutLatsFilCRH,BminACRH,latgrid,lats,mdi,ptsplt,typee1,typee2,'%rh')  
    PlotLatDistDiffs(OUTDIR+OutLatsFilCWB,BminACWB,latgrid,lats,mdi,ptsplt,typee1,typee2,'deg C')  
    PlotLatDistDiffs(OUTDIR+OutLatsFilDPD,BminADPD,latgrid,lats,mdi,ptsplt,typee1,typee2,'deg C')  

    # plot diff maps for each variables
    PlotClimMapDiffs(OUTDIR+OutMapsFilAT,BminAAT,longrid,latgrid,mdi,ptsplt,'RdYlBu','Reverse',typee1,typee2,'deg C')
    PlotClimMapDiffs(OUTDIR+OutMapsFilDPT,BminADPT,longrid,latgrid,mdi,ptsplt,'BrBG','Normal',typee1,typee2,'deg C')
    PlotClimMapDiffs(OUTDIR+OutMapsFilSHU,BminASHU,longrid,latgrid,mdi,ptsplt,'BrBG','Normal',typee1,typee2,'g/kg')
    PlotClimMapDiffs(OUTDIR+OutMapsFilVAP,BminAVAP,longrid,latgrid,mdi,ptsplt,'BrBG','Normal',typee1,typee2,'hPa')
    PlotClimMapDiffs(OUTDIR+OutMapsFilCRH,BminACRH,longrid,latgrid,mdi,ptsplt,'BrBG','Normal',typee1,typee2,'%rh')
    PlotClimMapDiffs(OUTDIR+OutMapsFilCWB,BminACWB,longrid,latgrid,mdi,ptsplt,'BrBG','Normal',typee1,typee2,'deg C')
    PlotClimMapDiffs(OUTDIR+OutMapsFilDPD,BminADPD,longrid,latgrid,mdi,ptsplt,'BrBG','Reverse',typee1,typee2,'deg C')

    # Create CLIMATOLOGY difference fields where there are non-missing data
    # create ATdiffs
    BminAAT = np.empty_like(AAT)
    BminAAT.fill(mdi)

    BminAAT[np.where((BATsd > mdi) & (AATsd > mdi))] = BATsd[np.where((BATsd > mdi) & (AATsd > mdi))] - AATsd[np.where((BATsd > mdi) & (AATsd > mdi))]
#    print('Check differencing')
#    pdb.set_trace()
            
    # create DPTdiffs
    BminADPT = np.empty_like(AAT)
    BminADPT.fill(mdi)
    
    BminADPT[np.where((BDPTsd > mdi) & (ADPTsd > mdi))] = BDPTsd[np.where((BDPTsd > mdi) & (ADPTsd > mdi))] - ADPTsd[np.where((BDPTsd > mdi) & (ADPTsd > mdi))]

    # create SHUdiffs
    BminASHU = np.empty_like(AAT)
    BminASHU.fill(mdi)
    
    BminASHU[np.where((BSHUsd > mdi) & (ASHUsd > mdi))] = BSHUsd[np.where((BSHUsd > mdi) & (ASHUsd > mdi))] - ASHUsd[np.where((BSHUsd > mdi) & (ASHUsd > mdi))]

    # create VAPdiffs
    BminAVAP = np.empty_like(AAT)
    BminAVAP.fill(mdi)
    
    BminAVAP[np.where((BVAPsd > mdi) & (AVAPsd > mdi))] = BVAPsd[np.where((BVAPsd > mdi) & (AVAPsd > mdi))] - AVAPsd[np.where((BVAPsd > mdi) & (AVAPsd > mdi))]

    # create CRHdiffs
    BminACRH = np.empty_like(AAT)
    BminACRH.fill(mdi)
    
    BminACRH[np.where((BCRHsd > mdi) & (ACRHsd > mdi))] = BCRHsd[np.where((BCRHsd > mdi) & (ACRHsd > mdi))] - ACRHsd[np.where((BCRHsd > mdi) & (ACRHsd > mdi))]

    # create CWBdiffs
    BminACWB = np.empty_like(AAT)
    BminACWB.fill(mdi)
    
    BminACWB[np.where((BCWBsd > mdi) & (ACWBsd > mdi))] = BCWBsd[np.where((BCWBsd > mdi) & (ACWBsd > mdi))] - ACWBsd[np.where((BCWBsd > mdi) & (ACWBsd > mdi))]

    # create DPDdiffs
    BminADPD = np.empty_like(AAT)
    BminADPD.fill(mdi)
    
    BminADPD[np.where((BDPDsd > mdi) & (ADPDsd > mdi))] = BDPDsd[np.where((BDPDsd > mdi) & (ADPDsd > mdi))] - ADPDsd[np.where((BDPDsd > mdi) & (ADPDsd > mdi))]
    
    # plot diffs by latitude for each variable = this is a 3 row by 2 column plot
    PlotLatDistDiffs(OUTDIR+OutSDLatsFilAT,BminAAT,latgrid,lats,mdi,ptsplt,typee1,typee2,'deg C')  
    PlotLatDistDiffs(OUTDIR+OutSDLatsFilDPT,BminADPT,latgrid,lats,mdi,ptsplt,typee1,typee2,'deg C')  
    PlotLatDistDiffs(OUTDIR+OutSDLatsFilSHU,BminASHU,latgrid,lats,mdi,ptsplt,typee1,typee2,'g/kg')  
    PlotLatDistDiffs(OUTDIR+OutSDLatsFilVAP,BminAVAP,latgrid,lats,mdi,ptsplt,typee1,typee2,'hPa')  
    PlotLatDistDiffs(OUTDIR+OutSDLatsFilCRH,BminACRH,latgrid,lats,mdi,ptsplt,typee1,typee2,'%rh')  
    PlotLatDistDiffs(OUTDIR+OutSDLatsFilCWB,BminACWB,latgrid,lats,mdi,ptsplt,typee1,typee2,'deg C')  
    PlotLatDistDiffs(OUTDIR+OutSDLatsFilDPD,BminADPD,latgrid,lats,mdi,ptsplt,typee1,typee2,'deg C')  

    # plot diff maps for each variables
    PlotClimMapDiffs(OUTDIR+OutSDMapsFilAT,BminAAT,longrid,latgrid,mdi,ptsplt,'RdYlBu','Reverse',typee1,typee2,'deg C')
    PlotClimMapDiffs(OUTDIR+OutSDMapsFilDPT,BminADPT,longrid,latgrid,mdi,ptsplt,'BrBG','Normal',typee1,typee2,'deg C')
    PlotClimMapDiffs(OUTDIR+OutSDMapsFilSHU,BminASHU,longrid,latgrid,mdi,ptsplt,'BrBG','Normal',typee1,typee2,'g/kg')
    PlotClimMapDiffs(OUTDIR+OutSDMapsFilVAP,BminAVAP,longrid,latgrid,mdi,ptsplt,'BrBG','Normal',typee1,typee2,'hPa')
    PlotClimMapDiffs(OUTDIR+OutSDMapsFilCRH,BminACRH,longrid,latgrid,mdi,ptsplt,'BrBG','Normal',typee1,typee2,'%rh')
    PlotClimMapDiffs(OUTDIR+OutSDMapsFilCWB,BminACWB,longrid,latgrid,mdi,ptsplt,'BrBG','Normal',typee1,typee2,'deg C')
    PlotClimMapDiffs(OUTDIR+OutSDMapsFilDPD,BminADPD,longrid,latgrid,mdi,ptsplt,'BrBG','Reverse',typee1,typee2,'deg C')
    
    #pdb.set_trace()

if __name__ == '__main__':
    
    main(sys.argv[1:])




#************************************************************************
