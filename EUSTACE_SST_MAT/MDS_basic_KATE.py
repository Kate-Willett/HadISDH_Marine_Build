#!/usr/local/sci/bin/python
# PYTHON2.7
# 
# Author: Kate Willett
# Created: 11 March 2016
# Last update: 11 March 2016
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/EUSTACE_SST_MAT/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code reads in the ICOADS data output from QC into a 'useful' dictionary
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
# from scipy.optimize import curve_fit,fsolve,leastsq
# from scipy import pi,sqrt,exp
# from scipy.special import erf
# import scipy.stats
# from math import sqrt,pi
# import struct
# import pdb # pdb.set_trace() or c 
#
# Kates:
# from LinearTrends import MedianPairwise - fits linear trend using Median Pairwise
#
# -----------------------
# DATA
# -----------------------
# /project/hadobs2/hadisdh/marine/ICOADS.2.5.1/beta/new_suite_197312_ERAclimNBC.txt
#
# -----------------------
# HOW TO RUN THE CODE
# -----------------------
# python2.7 
# import MDS_basic_KATE as MDStool
#
# MDSdict=MDStool.ReadMDSkate('year', 'month', 'type')
# year='1973' # string
# month='01' # string
# type='ERAclimNBC' # which iteration of output?
#
# This runs the code and stops mid-process so you can then interact with the
# data. You should be able to call this from another program too.
# 
# -----------------------
# OUTPUT
# -----------------------
# a dictionary to play with 
# -----------------------
# VERSION/RELEASE NOTES
# -----------------------
# 
# Version 1 (11 March 2016)
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
import numpy as np
from matplotlib.dates import date2num,num2date
import sys, os
from scipy.optimize import curve_fit,fsolve,leastsq
from scipy import pi,sqrt,exp
from scipy.special import erf
import scipy.stats
from math import sqrt,pi
import struct
import pdb # pdb.set_trace() or c 

from LinearTrends import MedianPairwise 


TheTypes=("|S9","|S8","int","int","int","int","int","int",
          "int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","|S8",
          "int","int","int","int","int","int","int","int","int","int","int",
          "int","|S3","|S4","|S4","|S3","|S2","|S3","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int")

TheDelimiters=(10,8,8,8,8,8,8,8,
               8,8,8,8,8,
               8,8,8,8,8,8,8,8,8,8,8,8,
               8,8,8,8,8,9,
               4,3,3,3,8,3,8,3,8,3,8,
               4,3,4,4,3,2,3,5,5,5,5,5,7,
               2,1,1,1,1,1,1,1,1,
               2,1,1,1,1,1,1,1,1,
               2,1,1,1,1,1,1,1,1,
               2,1,1,1,1,1,1,1,1,
               2,1,1,1,1,1,1,1)

#************************************************************************
# ReadMDSkate
#************************************************************************
def ReadMDSkate(TheYear,TheMonth,TheType):

    InDir = '/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/ERAclimNBC/'
#    InDir = '/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/beta/'
    InFil = 'new_suite_'+TheYear+TheMonth+'_'+TheType+'.txt'
    
    TheFilee = InDir+InFil
    
    print(TheFilee)
    
    # RD - moved the TheTypes and TheDelimiters to outside of definition
    #     so I can call them from another routine

    RawData=ReadData(TheFilee,TheTypes,TheDelimiters)
    
    MDSDict=dict([])
    
    MDSDict['shipid']=np.array(RawData['f0'])
    MDSDict['UID']=np.array(RawData['f1'])
    MDSDict['LAT']=np.array(RawData['f2'])/100.
    MDSDict['LON']=np.array(RawData['f3'])/100.
    MDSDict['YR']=np.array(RawData['f4'])
    MDSDict['MO']=np.array(RawData['f5'])
    MDSDict['DY']=np.array(RawData['f6'])
    MDSDict['HR']=np.array(RawData['f7'])

    MDSDict['AT']=np.array(RawData['f8'])/10.
    MDSDict['ATA']=np.array(RawData['f9'])/100.
    MDSDict['SST']=np.array(RawData['f10'])/10.
    MDSDict['SSTA']=np.array(RawData['f11'])/100.
    MDSDict['SLP']=np.array(RawData['f12'])/10.

    MDSDict['DPT']=np.array(RawData['f13'])/10.
    MDSDict['DPTA']=np.array(RawData['f14'])/100.
    MDSDict['SHU']=np.array(RawData['f15'])/10.
    MDSDict['SHUA']=np.array(RawData['f16'])/100.
    MDSDict['VAP']=np.array(RawData['f17'])/10.
    MDSDict['VAPA']=np.array(RawData['f18'])/100.
    MDSDict['CRH']=np.array(RawData['f19'])/10.
    MDSDict['CRHA']=np.array(RawData['f20'])/100.
    MDSDict['CWB']=np.array(RawData['f21'])/10.
    MDSDict['CWBA']=np.array(RawData['f22'])/100.
    MDSDict['DPD']=np.array(RawData['f23'])/10.
    MDSDict['DPDA']=np.array(RawData['f24'])/100.

#    MDSDict['DSVS']=np.array(RawData['f25'])
    MDSDict['DCK']=np.array(RawData['f26'])
#    MDSDict['SID']=np.array(RawData['f27'])
    MDSDict['PT']=np.array(RawData['f28'])
#    MDSDict['SI']=np.array(RawData['f29'])
#    MDSDict['printsim']=np.array(RawData['f30'])

    MDSDict['II']=np.array(RawData['f31'])
    MDSDict['IT']=np.array(RawData['f32'])
    MDSDict['DPTI']=np.array(RawData['f33'])
    MDSDict['WBTI']=np.array(RawData['f34'])
    MDSDict['WBT']=np.array(RawData['f35'])/10.
#    MDSDict['DI']=np.array(RawData['f36'])
#    MDSDict['D']=np.array(RawData['f37'])
    MDSDict['WI']=np.array(RawData['f38'])
    MDSDict['W']=np.array(RawData['f39'])/10. # Wind speed m/s
#    MDSDict['VI']=np.array(RawData['f40'])
#    MDSDict['VV']=np.array(RawData['f41'])

#    MDSDict['DUPS']=np.array(RawData['f42'])
#    MDSDict['COR']=np.array(RawData['f43'])
    MDSDict['TOB']=np.array(RawData['f44'])
    MDSDict['TOT']=np.array(RawData['f45'])
    MDSDict['EOT']=np.array(RawData['f46'])
    MDSDict['TOH']=np.array(RawData['f47'])
    MDSDict['EOH']=np.array(RawData['f48'])
    MDSDict['LOV']=np.array(RawData['f49'])
    MDSDict['HOP']=np.array(RawData['f50'])
    MDSDict['HOT']=np.array(RawData['f51'])
    MDSDict['HOB']=np.array(RawData['f52'])
    MDSDict['HOA']=np.array(RawData['f53'])
#    MDSDict['SMF']=np.array(RawData['f54'])

    MDSDict['day']=np.array(RawData['f55'])
    MDSDict['land']=np.array(RawData['f56'])
    MDSDict['trk']=np.array(RawData['f57'])
#    MDSDict['date1']=np.array(RawData['f58'])
#    MDSDict['date2']=np.array(RawData['f59'])
#    MDSDict['pos']=np.array(RawData['f60'])
#    MDSDict['blklst']=np.array(RawData['f61'])
    MDSDict['dup']=np.array(RawData['f62'])
#    MDSDict['POSblank1']=np.array(RawData['f63'])

#    MDSDict['SSTbud']=np.array(RawData['f64'])
    MDSDict['SSTclim']=np.array(RawData['f65'])
#    MDSDict['SSTnonorm']=np.array(RawData['f66'])
#    MDSDict['SSTfreez']=np.array(RawData['f67'])
#    MDSDict['SSTnoval']=np.array(RawData['f68'])
#    MDSDict['SSTnbud']=np.array(RawData['f69'])
#    MDSDict['SSTbbud']=np.array(RawData['f70'])
    MDSDict['SSTrep']=np.array(RawData['f71'])
#    MDSDict['SSTblank']=np.array(RawData['f72'])

    MDSDict['ATbud']=np.array(RawData['f73'])
    MDSDict['ATclim']=np.array(RawData['f74'])
    MDSDict['ATnonorm']=np.array(RawData['f75'])
#    MDSDict['ATblank1']=np.array(RawData['f76'])
    MDSDict['ATnoval']=np.array(RawData['f77'])
#    MDSDict['ATnbud']=np.array(RawData['f78'])
    MDSDict['ATround']=np.array(RawData['f78']) # round in place of nbud
#    MDSDict['ATbbud']=np.array(RawData['f79'])
    MDSDict['ATrep']=np.array(RawData['f80'])
#    MDSDict['ATblank2']=np.array(RawData['f81'])

    MDSDict['DPTbud']=np.array(RawData['f82'])
    MDSDict['DPTclim']=np.array(RawData['f83'])
    MDSDict['DPTnonorm']=np.array(RawData['f84'])
    MDSDict['DPTssat']=np.array(RawData['f85'])
    MDSDict['DPTnoval']=np.array(RawData['f86'])
#    MDSDict['DPTnbud']=np.array(RawData['f87'])
    MDSDict['DPTround']=np.array(RawData['f87']) # round in place of nbud
#    MDSDict['DPTbbud']=np.array(RawData['f88'])
    MDSDict['DPTrep']=np.array(RawData['f89'])
    MDSDict['DPTrepsat']=np.array(RawData['f90'])

#    MDSDict['few']=np.array(RawData['f91'])
#    MDSDict['ntrk']=np.array(RawData['f92'])
#    MDSDict['POSblank2']=np.array(RawData['f93'])
#    MDSDict['POSblank3']=np.array(RawData['f94'])
#    MDSDict['POSblank4']=np.array(RawData['f95'])
#    MDSDict['POSblank5']=np.array(RawData['f96'])
#    MDSDict['POSblank6']=np.array(RawData['f97'])
#    MDSDict['POSblank7']=np.array(RawData['f98'])

    nobs=len(MDSDict['shipid'])
    print('Number of obs read in: ',nobs)
    
    return MDSDict

#*************************************************************************
# READDATA
#*************************************************************************
def ReadData(FileName,typee,delimee):
    ''' Use numpy genfromtxt reading to read in all rows from a complex array '''
    ''' Need to specify format as it is complex '''
    ''' outputs an array of tuples that in turn need to be subscripted by their names defaults f0...f8 '''

    return np.genfromtxt(FileName, dtype=typee,delimiter=delimee) # ReadData

#*************************************************************************
