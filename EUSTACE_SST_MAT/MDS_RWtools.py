#!/usr/local/sci/bin/python
# PYTHON2.7
# 
# Author: Kate Willett
# Created: 7 April 2016
# Last update: 7 April 2016
# Location: /data/local/hadkw/HADCRUH2/MARINE/EUSTACEMDS/EUSTACE_SST_MAT/
# GitHub: https://github.com/Kate-Willett/HadISDH_Marine_Build/					
# -----------------------
# CODE PURPOSE AND OUTPUT
# -----------------------
# This code provides tools to read new_suite files and write new_suite*extended and new_suite*uncertainty files.
# It reads the files into a dictionary where each column can be explored through its 'key'.
#  
# -----------------------
# LIST OF MODULES
# -----------------------
# inbuilt:
# import numpy as np
# import copy
# import sys, os
# import pdb # pdb.set_trace() or c 
#
# Kates:
#
# -----------------------
# DATA
# -----------------------
# /project/hadobs2/hadisdh/marine/ICOADS.2.5.1/*/new_suite_197312_ERAclimNBC.txt
#
# -----------------------
# HOW TO RUN THE CODE
# -----------------------
# python2.7 
# import MDS_RWtools as MDStool
#
# MDSdict=MDStool.ReadMDSstandard('year', 'month', 'type')
# year='1973' # string
# month='01' # string
# type='ERAclimNBC' # which iteration of output?
#
# MDSdict=MDStool.ReadMDSextended('year', 'month', 'type')
# year='1973' # string
# month='01' # string
# type='ERAclimBC' # which iteration of output?
#
# MDSdict=MDStool.ReadMDSuncertainty('year', 'month', 'type')
# year='1973' # string
# month='01' # string
# type='ERAclimBC' # which iteration of output?
#
# Writing is slightly more complex
# Can't really think where this one would be used bu just in case
# MDStool.WriteMDSstandard('year', 'month', 'type',MDSDict)
# year='1973' # string
# month='01' # string
# type='ERAclimNBC' # which iteration of output - should also be the name of the directory the file sits in so the program can figure out the filename and path
# MDSDict = {} # A dictionary created by MakeExtDict()
#
# Writing is slightly more complex
# MDStool.WriteMDSextended('year', 'month', 'type',MDSDict)
# year='1973' # string
# month='01' # string
# type='ERAclimBC' # which iteration of output - should also be the name of the directory the file sits in so the program can figure out the filename and path
# MDSDict = {} # A dictionary created by MakeExtDict()
#
# MDStool.WriteMDSuncertainty('year', 'month', 'type',MDSDict)
# year='1973' # string
# month='01' # string
# type='ERAclimBC' # which iteration of output - should also be the name of the directory the file sits in so the program can figure out the filename and path
# MDSDict = {} # A dictionary created by MakeExtDict()
#
# MDSDict=MDStool.MakeStdDict()
#
# MDSDict=MDStool.MakeExtDict()
#
# MDSDict=MDStool.MakeUncDict()
#
#

#
# For reading this runs the code and stops mid-process so you can then interact with the
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
# Version 1 (7 April 2016)
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
import numpy as np
import sys, os
import copy
import struct
import pdb # pdb.set_trace() or c 

# first element is 9 characters lon with a space - so delimiters = 10.
TheTypesStd=("|S9","|S8","int","int","int","int","int","int",
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

TheDelimitersStd=(10,8,8,8,8,8,8,8, 		# 8 8 ID, Location and time metadata 
               8,8,8,8,8,			# 5 Temperature and pressure OBS values AT, SST and SLP
               8,8,8,8,8,8,8,8,8,8,8,8,		# 12 Humidity related OBS values DPT, SHU, VAP, CRH, CWB and DPD
               8,8,8,8,8,9,			# 6 Deck and Platform ID and other platform related metadata
               4,3,3,3,8,3,8,3,8,3,8,		# 11 OBS related metadata
               4,3,4,4,3,2,3,5,5,5,5,5,7,	# 13 Instrument related metadata
               2,1,1,1,1,1,1,1,1,		# 9 BASE QC
               2,1,1,1,1,1,1,1,1,		# 9 SST QC
               2,1,1,1,1,1,1,1,1,		# 9 AT QC	
               2,1,1,1,1,1,1,1,1,		# 9 DPT QC
               2,1,1,1,1,1,1,1)			# 8 Additional QC

# first element is 9 characters lon with a space - so delimiters = 10.
TheTypesExt=("|S9","|S8","int","int","int","int","int","int",
          "int","int","int","int",
          "int","int","int","int","int","int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int","int","int","int","int","int",
          "int","int","int",
          "|S3","|S3","|S3","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int",
          "int","int","int","int","int",
          "int","int","int","int","int",
          "int","int","int","int","int","int")

TheDelimitersExt=(10,8,8,8,8,8,8,8,
               8,8,8,8,
               8,8,8,8,8,8,8,8,8,8,8,8,8,8,
               8,8,8,8,8,8,8,8,8,8,8,8,8,8,
               8,8,8,8,8,8,8,8,8,8,8,8,8,8,
               8,8,8,8,8,8,8,8,8,8,8,8,8,8,
               8,8,8,8,8,8,8,8,8,8,8,8,8,8,
	       8,8,9,
               3,3,3,5,5,5,5,5,5,
               2,1,1,1,1,1,1,1,    
               2,1,1,1,1,	       
               2,1,1,1,1,
               2,1,1,1,1,1)

# first element is 9 characters lon with a space - so delimiters = 10.
TheTypesUnc=("|S9","|S8","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int","int","int","int","int","int","int",
          "int","int","int",
          "|S3","|S3","|S3","int","int","int","int","int","int",
          "int","int","int","int","int","int","int","int",
          "int","int","int","int","int",
          "int","int","int","int","int",
          "int","int","int","int","int","int")

TheDelimitersUnc=(10,8,8,8,8,8,8,8,
               8,8,8,8,8,8,8,8,8,8,8,8,8,8,
               8,8,8,8,8,8,8,8,8,8,8,8,8,8,
               8,8,8,8,8,8,8,8,8,8,8,8,8,8,
               8,8,8,8,8,8,8,8,8,8,8,8,8,8,
               8,8,8,8,8,8,8,8,8,8,8,8,8,8,
               8,8,8,8,8,8,8,8,8,8,8,8,8,8,
               8,8,8,8,8,8,8,8,8,8,8,8,8,8,
	       8,8,9,
               3,3,3,5,5,5,5,5,5,
               2,1,1,1,1,1,1,1,    
               2,1,1,1,1,	       
               2,1,1,1,1,
               2,1,1,1,1,1)

#************************************************************************
# ReadMDSstandard
#************************************************************************
def ReadMDSstandard(TheYear,TheMonth,TheType):

    InDir = '/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/'+TheType+'/' # THRESH5_5
    InFil = 'new_suite_'+TheYear+TheMonth+'_'+TheType+'.txt'
    
    TheFilee = InDir+InFil
    
    print(TheFilee)
    
    # RD - moved the TheTypes and TheDelimiters to outside of definition
    #     so I can call them from another routine

    RawData=ReadData(TheFilee,TheTypesStd,TheDelimitersStd)
    
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
    MDSDict['SID']=np.array(RawData['f27'])
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
    MDSDict['W']=np.array(RawData['f39'])/10.
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
    MDSDict['date1']=np.array(RawData['f58'])
    MDSDict['date2']=np.array(RawData['f59'])
    MDSDict['pos']=np.array(RawData['f60'])
    MDSDict['blklst']=np.array(RawData['f61'])
    MDSDict['dup']=np.array(RawData['f62'])
#    MDSDict['POSblank1']=np.array(RawData['f63'])

    MDSDict['SSTbud']=np.array(RawData['f64'])
    MDSDict['SSTclim']=np.array(RawData['f65'])
    MDSDict['SSTnonorm']=np.array(RawData['f66'])
    MDSDict['SSTfreez']=np.array(RawData['f67'])
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

#************************************************************************
# ReadMDSextended
#************************************************************************
def ReadMDSextended(TheYear,TheMonth,TheType):

    InDir = '/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/'+TheType+'/'
#    InDir = '/data/local/hadkw/HADCRUH2/MARINE/'
    InFil = 'new_suite_'+TheYear+TheMonth+'_'+TheType+'_extended.txt'
    
    TheFilee = InDir+InFil
    
    print(TheFilee)
    
    RawData=ReadData(TheFilee,TheTypesExt,TheDelimitersExt)
    
    MDSDict=dict([])
    
    MDSDict['shipid']=np.array(RawData['f0'])
    MDSDict['UID']=np.array(RawData['f1'])
    MDSDict['LAT']=np.array(RawData['f2'])/100.
    MDSDict['LON']=np.array(RawData['f3'])/100.
    MDSDict['YR']=np.array(RawData['f4'])
    MDSDict['MO']=np.array(RawData['f5'])
    MDSDict['DY']=np.array(RawData['f6'])
    MDSDict['HR']=np.array(RawData['f7'])

    MDSDict['SST']=np.array(RawData['f8'])/10.
    MDSDict['SSTA']=np.array(RawData['f9'])/100.
    MDSDict['SLP']=np.array(RawData['f10'])/10.
    MDSDict['W']=np.array(RawData['f11'])/10.

    MDSDict['AT']=np.array(RawData['f12'])/10.
    MDSDict['ATA']=np.array(RawData['f13'])/100.
    MDSDict['DPT']=np.array(RawData['f14'])/10.
    MDSDict['DPTA']=np.array(RawData['f15'])/100.
    MDSDict['SHU']=np.array(RawData['f16'])/10.
    MDSDict['SHUA']=np.array(RawData['f17'])/100.
    MDSDict['VAP']=np.array(RawData['f18'])/10.
    MDSDict['VAPA']=np.array(RawData['f19'])/100.
    MDSDict['CRH']=np.array(RawData['f20'])/10.
    MDSDict['CRHA']=np.array(RawData['f21'])/100.
    MDSDict['CWB']=np.array(RawData['f22'])/10.
    MDSDict['CWBA']=np.array(RawData['f23'])/100.
    MDSDict['DPD']=np.array(RawData['f24'])/10.
    MDSDict['DPDA']=np.array(RawData['f25'])/100.

    MDSDict['ATtbc']=np.array(RawData['f26'])/10.
    MDSDict['ATAtbc']=np.array(RawData['f27'])/100.
    MDSDict['DPTtbc']=np.array(RawData['f28'])/10.
    MDSDict['DPTAtbc']=np.array(RawData['f29'])/100.
    MDSDict['SHUtbc']=np.array(RawData['f30'])/10.
    MDSDict['SHUAtbc']=np.array(RawData['f31'])/100.
    MDSDict['VAPtbc']=np.array(RawData['f32'])/10.
    MDSDict['VAPAtbc']=np.array(RawData['f33'])/100.
    MDSDict['CRHtbc']=np.array(RawData['f34'])/10.
    MDSDict['CRHAtbc']=np.array(RawData['f35'])/100.
    MDSDict['CWBtbc']=np.array(RawData['f36'])/10.
    MDSDict['CWBAtbc']=np.array(RawData['f37'])/100.
    MDSDict['DPDtbc']=np.array(RawData['f38'])/10.
    MDSDict['DPDAtbc']=np.array(RawData['f39'])/100.

    MDSDict['AThc']=np.array(RawData['f40'])/10.
    MDSDict['ATAhc']=np.array(RawData['f41'])/100.
    MDSDict['DPThc']=np.array(RawData['f42'])/10.
    MDSDict['DPTAhc']=np.array(RawData['f43'])/100.
    MDSDict['SHUhc']=np.array(RawData['f44'])/10.
    MDSDict['SHUAhc']=np.array(RawData['f45'])/100.
    MDSDict['VAPhc']=np.array(RawData['f46'])/10.
    MDSDict['VAPAhc']=np.array(RawData['f47'])/100.
    MDSDict['CRHhc']=np.array(RawData['f48'])/10.
    MDSDict['CRHAhc']=np.array(RawData['f49'])/100.
    MDSDict['CWBhc']=np.array(RawData['f50'])/10.
    MDSDict['CWBAhc']=np.array(RawData['f51'])/100.
    MDSDict['DPDhc']=np.array(RawData['f52'])/10.
    MDSDict['DPDAhc']=np.array(RawData['f53'])/100.

    MDSDict['ATscn']=np.array(RawData['f54'])/10.
    MDSDict['ATAscn']=np.array(RawData['f55'])/100.
    MDSDict['DPTscn']=np.array(RawData['f56'])/10.
    MDSDict['DPTAscn']=np.array(RawData['f57'])/100.
    MDSDict['SHUscn']=np.array(RawData['f58'])/10.
    MDSDict['SHUAscn']=np.array(RawData['f59'])/100.
    MDSDict['VAPscn']=np.array(RawData['f60'])/10.
    MDSDict['VAPAscn']=np.array(RawData['f61'])/100.
    MDSDict['CRHscn']=np.array(RawData['f62'])/10.
    MDSDict['CRHAscn']=np.array(RawData['f63'])/100.
    MDSDict['CWBscn']=np.array(RawData['f64'])/10.
    MDSDict['CWBAscn']=np.array(RawData['f65'])/100.
    MDSDict['DPDscn']=np.array(RawData['f66'])/10.
    MDSDict['DPDAscn']=np.array(RawData['f67'])/100.

    MDSDict['ATslr']=np.array(RawData['f68'])/10.
    MDSDict['ATAslr']=np.array(RawData['f69'])/100.
    MDSDict['DPTslr']=np.array(RawData['f70'])/10.
    MDSDict['DPTAslr']=np.array(RawData['f71'])/100.
    MDSDict['SHUslr']=np.array(RawData['f72'])/10.
    MDSDict['SHUAslr']=np.array(RawData['f73'])/100.
    MDSDict['VAPslr']=np.array(RawData['f74'])/10.
    MDSDict['VAPAslr']=np.array(RawData['f75'])/100.
    MDSDict['CRHslr']=np.array(RawData['f76'])/10.
    MDSDict['CRHAslr']=np.array(RawData['f77'])/100.
    MDSDict['CWBslr']=np.array(RawData['f78'])/10.
    MDSDict['CWBAslr']=np.array(RawData['f79'])/100.
    MDSDict['DPDslr']=np.array(RawData['f80'])/10.
    MDSDict['DPDAslr']=np.array(RawData['f81'])/100.

    MDSDict['DCK']=np.array(RawData['f82'])
    MDSDict['SID']=np.array(RawData['f83'])
    MDSDict['PT']=np.array(RawData['f84'])

    MDSDict['EOT']=np.array(RawData['f85']) # something up here
    MDSDict['EOH']=np.array(RawData['f86'])
    MDSDict['ESTE']=np.array(RawData['f87'])
    MDSDict['LOV']=np.array(RawData['f88'])
    MDSDict['HOP']=np.array(RawData['f89'])
    MDSDict['HOT']=np.array(RawData['f90'])
    MDSDict['HOB']=np.array(RawData['f91'])
    MDSDict['HOA']=np.array(RawData['f92'])
    MDSDict['ESTH']=np.array(RawData['f93'])

    MDSDict['day']=np.array(RawData['f94'])
    MDSDict['land']=np.array(RawData['f95'])
    MDSDict['trk']=np.array(RawData['f96'])
    MDSDict['date1']=np.array(RawData['f97'])
    MDSDict['date2']=np.array(RawData['f98'])
    MDSDict['pos']=np.array(RawData['f99'])
    MDSDict['blklst']=np.array(RawData['f100'])
    MDSDict['dup']=np.array(RawData['f101'])

    MDSDict['SSTbud']=np.array(RawData['f102'])
    MDSDict['SSTclim']=np.array(RawData['f103'])
    MDSDict['SSTnonorm']=np.array(RawData['f104'])
    MDSDict['SSTfreez']=np.array(RawData['f105'])
    MDSDict['SSTrep']=np.array(RawData['f106'])

    MDSDict['ATbud']=np.array(RawData['f107'])
    MDSDict['ATclim']=np.array(RawData['f108'])
    MDSDict['ATnonorm']=np.array(RawData['f109'])
    MDSDict['ATround']=np.array(RawData['f110']) # round in place of nbud
    MDSDict['ATrep']=np.array(RawData['f111'])

    MDSDict['DPTbud']=np.array(RawData['f112'])
    MDSDict['DPTclim']=np.array(RawData['f113'])
    MDSDict['DPTssat']=np.array(RawData['f114'])
    MDSDict['DPTround']=np.array(RawData['f115']) # round in place of nbud
    MDSDict['DPTrep']=np.array(RawData['f116'])
    MDSDict['DPTrepsat']=np.array(RawData['f117'])

    nobs=len(MDSDict['shipid'])
    print('Number of obs read in: ',nobs)
    
    return MDSDict

#************************************************************************
# ReadMDSuncertainty
#************************************************************************
def ReadMDSuncertainty(TheYear,TheMonth,TheType):

    InDir = '/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/'+TheType+'/'
#    InDir = '/data/local/hadkw/HADCRUH2/MARINE/'
    InFil = 'new_suite_'+TheYear+TheMonth+'_'+TheType+'_uncertainty.txt'
    
    TheFilee = InDir+InFil
    
    print(TheFilee)
    
    RawData=ReadData(TheFilee,TheTypesUnc,TheDelimitersUnc)
    
    MDSDict=dict([])

    MDSDict['shipid']=np.array(RawData['f0'])
    MDSDict['UID']=np.array(RawData['f1'])
    MDSDict['LAT']=np.array(RawData['f2'])/100.
    MDSDict['LON']=np.array(RawData['f3'])/100.
    MDSDict['YR']=np.array(RawData['f4'])
    MDSDict['MO']=np.array(RawData['f5'])
    MDSDict['DY']=np.array(RawData['f6'])
    MDSDict['HR']=np.array(RawData['f7'])

    MDSDict['ATtbc']=np.array(RawData['f8'])/10.
    MDSDict['ATAtbc']=np.array(RawData['f9'])/100.
    MDSDict['DPTtbc']=np.array(RawData['f10'])/10.
    MDSDict['DPTAtbc']=np.array(RawData['f11'])/100.
    MDSDict['SHUtbc']=np.array(RawData['f12'])/10.
    MDSDict['SHUAtbc']=np.array(RawData['f13'])/100.
    MDSDict['VAPtbc']=np.array(RawData['f14'])/10.
    MDSDict['VAPAtbc']=np.array(RawData['f15'])/100.
    MDSDict['CRHtbc']=np.array(RawData['f16'])/10.
    MDSDict['CRHAtbc']=np.array(RawData['f17'])/100.
    MDSDict['CWBtbc']=np.array(RawData['f18'])/10.
    MDSDict['CWBAtbc']=np.array(RawData['f19'])/100.
    MDSDict['DPDtbc']=np.array(RawData['f20'])/10.
    MDSDict['DPDAtbc']=np.array(RawData['f21'])/100.

    MDSDict['ATuncT']=np.array(RawData['f22'])/10.
    MDSDict['ATAuncT']=np.array(RawData['f23'])/100.
    MDSDict['DPTuncT']=np.array(RawData['f24'])/10.
    MDSDict['DPTAuncT']=np.array(RawData['f25'])/100.
    MDSDict['SHUuncT']=np.array(RawData['f26'])/10.
    MDSDict['SHUAuncT']=np.array(RawData['f27'])/100.
    MDSDict['VAPuncT']=np.array(RawData['f28'])/10.
    MDSDict['VAPAuncT']=np.array(RawData['f29'])/100.
    MDSDict['CRHuncT']=np.array(RawData['f30'])/10.
    MDSDict['CRHAuncT']=np.array(RawData['f31'])/100.
    MDSDict['CWBuncT']=np.array(RawData['f32'])/10.
    MDSDict['CWBAuncT']=np.array(RawData['f33'])/100.
    MDSDict['DPDuncT']=np.array(RawData['f34'])/10.
    MDSDict['DPDAuncT']=np.array(RawData['f35'])/100.

    MDSDict['ATuncSLR']=np.array(RawData['f36'])/10.
    MDSDict['ATAuncSLR']=np.array(RawData['f37'])/100.
    MDSDict['DPTuncSLR']=np.array(RawData['f38'])/10.
    MDSDict['DPTAuncSLR']=np.array(RawData['f39'])/100.
    MDSDict['SHUuncSLR']=np.array(RawData['f40'])/10.
    MDSDict['SHUAuncSLR']=np.array(RawData['f41'])/100.
    MDSDict['VAPuncSLR']=np.array(RawData['f42'])/10.
    MDSDict['VAPAuncSLR']=np.array(RawData['f43'])/100.
    MDSDict['CRHuncSLR']=np.array(RawData['f44'])/10.
    MDSDict['CRHAuncSLR']=np.array(RawData['f45'])/100.
    MDSDict['CWBuncSLR']=np.array(RawData['f46'])/10.
    MDSDict['CWBAuncSLR']=np.array(RawData['f47'])/100.
    MDSDict['DPDuncSLR']=np.array(RawData['f48'])/10.
    MDSDict['DPDAuncSLR']=np.array(RawData['f49'])/100.

    MDSDict['ATuncSCN']=np.array(RawData['f50'])/10.
    MDSDict['ATAuncSCN']=np.array(RawData['f51'])/100.
    MDSDict['DPTuncSCN']=np.array(RawData['f52'])/10.
    MDSDict['DPTAuncSCN']=np.array(RawData['f53'])/100.
    MDSDict['SHUuncSCN']=np.array(RawData['f54'])/10.
    MDSDict['SHUAuncSCN']=np.array(RawData['f55'])/100.
    MDSDict['VAPuncSCN']=np.array(RawData['f56'])/10.
    MDSDict['VAPAuncSCN']=np.array(RawData['f57'])/100.
    MDSDict['CRHuncSCN']=np.array(RawData['f58'])/10.
    MDSDict['CRHAuncSCN']=np.array(RawData['f59'])/100.
    MDSDict['CWBuncSCN']=np.array(RawData['f60'])/10.
    MDSDict['CWBAuncSCN']=np.array(RawData['f61'])/100.
    MDSDict['DPDuncSCN']=np.array(RawData['f62'])/10.
    MDSDict['DPDAuncSCN']=np.array(RawData['f63'])/100.

    MDSDict['ATuncHGT']=np.array(RawData['f64'])/10.
    MDSDict['ATAuncHGT']=np.array(RawData['f65'])/100.
    MDSDict['DPTuncHGT']=np.array(RawData['f66'])/10.
    MDSDict['DPTAuncHGT']=np.array(RawData['f67'])/100.
    MDSDict['SHUuncHGT']=np.array(RawData['f68'])/10.
    MDSDict['SHUAuncHGT']=np.array(RawData['f69'])/100.
    MDSDict['VAPuncHGT']=np.array(RawData['f70'])/10.
    MDSDict['VAPAuncHGT']=np.array(RawData['f71'])/100.
    MDSDict['CRHuncHGT']=np.array(RawData['f72'])/10.
    MDSDict['CRHAuncHGT']=np.array(RawData['f73'])/100.
    MDSDict['CWBuncHGT']=np.array(RawData['f74'])/10.
    MDSDict['CWBAuncHGT']=np.array(RawData['f75'])/100.
    MDSDict['DPDuncHGT']=np.array(RawData['f76'])/10.
    MDSDict['DPDAuncHGT']=np.array(RawData['f77'])/100.

    MDSDict['ATuncM']=np.array(RawData['f78'])/10.
    MDSDict['ATAuncM']=np.array(RawData['f79'])/100.
    MDSDict['DPTuncM']=np.array(RawData['f80'])/10.
    MDSDict['DPTAuncM']=np.array(RawData['f81'])/100.
    MDSDict['SHUuncM']=np.array(RawData['f82'])/10.
    MDSDict['SHUAuncM']=np.array(RawData['f83'])/100.
    MDSDict['VAPuncM']=np.array(RawData['f84'])/10.
    MDSDict['VAPAuncM']=np.array(RawData['f85'])/100.
    MDSDict['CRHuncM']=np.array(RawData['f86'])/10.
    MDSDict['CRHAuncM']=np.array(RawData['f87'])/100.
    MDSDict['CWBuncM']=np.array(RawData['f88'])/10.
    MDSDict['CWBAuncM']=np.array(RawData['f89'])/100.
    MDSDict['DPDuncM']=np.array(RawData['f90'])/10.
    MDSDict['DPDAuncM']=np.array(RawData['f91'])/100.

    MDSDict['ATuncR']=np.array(RawData['f92'])/10.
    MDSDict['ATAuncR']=np.array(RawData['f93'])/100.
    MDSDict['DPTuncR']=np.array(RawData['f94'])/10.
    MDSDict['DPTAuncR']=np.array(RawData['f95'])/100.
    MDSDict['SHUuncR']=np.array(RawData['f96'])/10.
    MDSDict['SHUAuncR']=np.array(RawData['f97'])/100.
    MDSDict['VAPuncR']=np.array(RawData['f98'])/10.
    MDSDict['VAPAuncR']=np.array(RawData['f99'])/100.
    MDSDict['CRHuncR']=np.array(RawData['f100'])/10.
    MDSDict['CRHAuncR']=np.array(RawData['f101'])/100.
    MDSDict['CWBuncR']=np.array(RawData['f102'])/10.
    MDSDict['CWBAuncR']=np.array(RawData['f103'])/100.
    MDSDict['DPDuncR']=np.array(RawData['f104'])/10.
    MDSDict['DPDAuncR']=np.array(RawData['f105'])/100.

    MDSDict['DCK']=np.array(RawData['f106'])
    MDSDict['SID']=np.array(RawData['f107'])
    MDSDict['PT']=np.array(RawData['f108'])

    MDSDict['EOT']=np.array(RawData['f109'])
    MDSDict['EOH']=np.array(RawData['f110'])
    MDSDict['ESTE']=np.array(RawData['f111'])
    MDSDict['LOV']=np.array(RawData['f112'])
    MDSDict['HOP']=np.array(RawData['f113'])
    MDSDict['HOT']=np.array(RawData['f114'])
    MDSDict['HOB']=np.array(RawData['f115'])
    MDSDict['HOA']=np.array(RawData['f116'])
    MDSDict['ESTH']=np.array(RawData['f117'])

    MDSDict['day']=np.array(RawData['f118'])
    MDSDict['land']=np.array(RawData['f119'])
    MDSDict['trk']=np.array(RawData['f120'])
    MDSDict['date1']=np.array(RawData['f121'])
    MDSDict['date2']=np.array(RawData['f122'])
    MDSDict['pos']=np.array(RawData['f123'])
    MDSDict['blklst']=np.array(RawData['f124'])
    MDSDict['dup']=np.array(RawData['f125'])

    MDSDict['SSTbud']=np.array(RawData['f126'])
    MDSDict['SSTclim']=np.array(RawData['f127'])
    MDSDict['SSTnonorm']=np.array(RawData['f128'])
    MDSDict['SSTfreez']=np.array(RawData['f129'])
    MDSDict['SSTrep']=np.array(RawData['f130'])

    MDSDict['ATbud']=np.array(RawData['f131'])
    MDSDict['ATclim']=np.array(RawData['f132'])
    MDSDict['ATnonorm']=np.array(RawData['f133'])
    MDSDict['ATround']=np.array(RawData['f134']) # round in place of nbud
    MDSDict['ATrep']=np.array(RawData['f135'])

    MDSDict['DPTbud']=np.array(RawData['f136'])
    MDSDict['DPTclim']=np.array(RawData['f137'])
    MDSDict['DPTssat']=np.array(RawData['f138'])
    MDSDict['DPTround']=np.array(RawData['f139']) # round in place of nbud
    MDSDict['DPTrep']=np.array(RawData['f140'])
    MDSDict['DPTrepsat']=np.array(RawData['f141'])


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

    return np.genfromtxt(FileName, dtype=typee,delimiter=delimee,comments=False) # ReadData

#************************************************************************
# WriteMDSstandard
#************************************************************************
def WriteMDSstandard(TheYear,TheMonth,TheType):

    # I've deliberately put a bug in this filepath to protect the data
    OutDir = '/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/'+TheType+'a/'
    OutFil = 'new_suite_'+TheYear+TheMonth+'_'+TheType+'.txt'
    
    TheFilee = OutDir+OutFil
    
    print(TheFilee)

    RawData=ReadData(TheFilee,TheTypesStd,TheDelimitersStd)
    
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
    MDSDict['SID']=np.array(RawData['f27'])
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
    MDSDict['W']=np.array(RawData['f39'])
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
    MDSDict['date1']=np.array(RawData['f58'])
    MDSDict['date2']=np.array(RawData['f59'])
    MDSDict['pos']=np.array(RawData['f60'])
    MDSDict['blklst']=np.array(RawData['f61'])
    MDSDict['dup']=np.array(RawData['f62'])
#    MDSDict['POSblank1']=np.array(RawData['f63'])

    MDSDict['SSTbud']=np.array(RawData['f64'])
    MDSDict['SSTclim']=np.array(RawData['f65'])
    MDSDict['SSTnonorm']=np.array(RawData['f66'])
    MDSDict['SSTfreez']=np.array(RawData['f67'])
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

#************************************************************************
# WriteMDSextended
#************************************************************************
def WriteMDSextended(TheYear,TheMonth,TheType,MDSDict):

    OutDir = '/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/'+TheType+'/'
#    OutDir = '/data/local/hadkw/HADCRUH2/MARINE/'
    OutFil = 'new_suite_'+TheYear+TheMonth+'_'+TheType+'_extended.txt'
    
    TheFilee = OutDir+OutFil
    
    print(TheFilee)

    nobs=len(MDSDict['shipid'])
    print('Number of obs to print: ',nobs)

    filee=open(TheFilee,'a+')
    
    for linee in range(nobs):
        print(linee)
        filee.write(str("{:9.9} ".format(MDSDict['shipid'][linee])+\
	                "{:8.8}".format(MDSDict['UID'][linee])+\
                        "{:8d}".format(int(round(MDSDict['LAT'][linee]*100.,0)))+\
                        "{:8d}".format(int(round(MDSDict['LON'][linee]*100.,0)))+\
                        "{:8d}".format(MDSDict['YR'][linee])+\
                        "{:8d}".format(MDSDict['MO'][linee])+\
                        "{:8d}".format(MDSDict['DY'][linee])+\
                        "{:8d}".format(MDSDict['HR'][linee])+\
			
			"{:8d}".format(int(round(MDSDict['SST'][linee]*10.,0)))+\
                        "{:8d}".format(int(round(MDSDict['SSTA'][linee]*100.,0)))+\
                        "{:8d}".format(int(round(MDSDict['SLP'][linee]*10.,0)))+\
                        "{:8d}".format(int(round(MDSDict['W'][linee]*10.,0)))+\

			"{:8d}".format(int(round(MDSDict['AT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['ATA'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTA'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHU'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUA'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAP'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPA'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRH'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHA'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWB'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBA'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPD'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDA'][linee]*100.,0)))+\

			"{:8d}".format(int(round(MDSDict['ATtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['ATAtbc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTAtbc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUAtbc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPAtbc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHAtbc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBAtbc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDAtbc'][linee]*100.,0)))+\

			"{:8d}".format(int(round(MDSDict['AThc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['ATAhc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPThc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTAhc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUhc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUAhc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPhc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPAhc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHhc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHAhc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBhc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBAhc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDhc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDAhc'][linee]*100.,0)))+\

			"{:8d}".format(int(round(MDSDict['ATscn'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['ATAscn'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTscn'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTAscn'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUscn'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUAscn'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPscn'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPAscn'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHscn'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHAscn'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBscn'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBAscn'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDscn'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDAscn'][linee]*100.,0)))+\

			"{:8d}".format(int(round(MDSDict['ATslr'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['ATAslr'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTslr'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTAslr'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUslr'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUAslr'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPslr'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPAslr'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHslr'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHAslr'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBslr'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBAslr'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDslr'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDAslr'][linee]*100.,0)))+\
	
			"{:8d}".format(MDSDict['DCK'][linee])+\
			"{:8d}".format(MDSDict['SID'][linee])+\
			"{:8d} ".format(MDSDict['PT'][linee])+\

			"{:3.3}".format(MDSDict['EOT'][linee])+\
			"{:3.3}".format(MDSDict['EOH'][linee])+\
			"{:3.3}".format(MDSDict['ESTE'][linee])+\
			"{:5d}".format(MDSDict['LOV'][linee])+\
			"{:5d}".format(MDSDict['HOP'][linee])+\
			"{:5d}".format(MDSDict['HOT'][linee])+\
			"{:5d}".format(MDSDict['HOB'][linee])+\
			"{:5d}".format(MDSDict['HOA'][linee])+\
			"{:5d}".format(int(round(MDSDict['ESTH'][linee])))+\

			"{:2d}".format(MDSDict['day'][linee])+\
			"{:1d}".format(MDSDict['land'][linee])+\
			"{:1d}".format(MDSDict['trk'][linee])+\
			"{:1d}".format(MDSDict['date1'][linee])+\
			"{:1d}".format(MDSDict['date2'][linee])+\
			"{:1d}".format(MDSDict['pos'][linee])+\
			"{:1d}".format(MDSDict['blklst'][linee])+\
			"{:1d}".format(MDSDict['dup'][linee])+\

			"{:2d}".format(MDSDict['SSTbud'][linee])+\
			"{:1d}".format(MDSDict['SSTclim'][linee])+\
			"{:1d}".format(MDSDict['SSTnonorm'][linee])+\
			"{:1d}".format(MDSDict['SSTfreez'][linee])+\
			"{:1d}".format(MDSDict['SSTrep'][linee])+\

			"{:2d}".format(MDSDict['ATbud'][linee])+\
			"{:1d}".format(MDSDict['ATclim'][linee])+\
			"{:1d}".format(MDSDict['ATnonorm'][linee])+\
			"{:1d}".format(MDSDict['ATround'][linee])+\
			"{:1d}".format(MDSDict['ATrep'][linee])+\

			"{:2d}".format(MDSDict['DPTbud'][linee])+\
			"{:1d}".format(MDSDict['DPTclim'][linee])+\
			"{:1d}".format(MDSDict['DPTssat'][linee])+\
			"{:1d}".format(MDSDict['DPTround'][linee])+\
			"{:1d}".format(MDSDict['DPTrep'][linee])+\
			"{:1d}".format(MDSDict['DPTrepsat'][linee])+\
                        "\n"))

    filee.close()
    
    return

#************************************************************************
# WriteMDSuncertainty
#************************************************************************
def WriteMDSuncertainty(TheYear,TheMonth,TheType,MDSDict):

    OutDir = '/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/'+TheType+'/'
#    OutDir = '/data/local/hadkw/HADCRUH2/MARINE/'
    OutFil = 'new_suite_'+TheYear+TheMonth+'_'+TheType+'_uncertainty.txt'
    
    TheFilee = OutDir+OutFil
    
    print(TheFilee)

    filee=open(TheFilee,'a+')

    nobs=len(MDSDict['shipid'])
    print('Number of obs to print: ',nobs)

    for linee in range(nobs):
        print(linee)
        filee.write(str("{:9.9} ".format(MDSDict['shipid'][linee])+\
	                "{:8.8}".format(MDSDict['UID'][linee])+\
                        "{:8d}".format(int(round(MDSDict['LAT'][linee]*100, 0)))+\
                        "{:8d}".format(int(round(MDSDict['LON'][linee]*100,0)))+\
                        "{:8d}".format(MDSDict['YR'][linee])+\
                        "{:8d}".format(MDSDict['MO'][linee])+\
                        "{:8d}".format(MDSDict['DY'][linee])+\
                        "{:8d}".format(MDSDict['HR'][linee])+\

			"{:8d}".format(int(round(MDSDict['ATtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['ATAtbc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTAtbc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUAtbc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPAtbc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHAtbc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBAtbc'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDtbc'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDAtbc'][linee]*100.,0)))+\

                        # Better to write out ALL uncertainties to two decimal places rather than just anomalies?
			"{:8d}".format(int(round(MDSDict['ATuncT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['ATAuncT'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTuncT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTAuncT'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUuncT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUAuncT'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPuncT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPAuncT'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHuncT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHAuncT'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBuncT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBAuncT'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDuncT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDAuncT'][linee]*100.,0)))+\

			"{:8d}".format(int(round(MDSDict['ATuncSLR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['ATAuncSLR'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTuncSLR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTAuncSLR'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUuncSLR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUAuncSLR'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPuncSLR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPAuncSLR'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHuncSLR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHAuncSLR'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBuncSLR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBAuncSLR'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDuncSLR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDAuncSLR'][linee]*100.,0)))+\

			"{:8d}".format(int(round(MDSDict['ATuncSCN'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['ATAuncSCN'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTuncSCN'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTAuncSCN'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUuncSCN'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUAuncSCN'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPuncSCN'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPAuncSCN'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHuncSCN'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHAuncSCN'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBuncSCN'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBAuncSCN'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDuncSCN'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDAuncSCN'][linee]*100.,0)))+\

			"{:8d}".format(int(round(MDSDict['ATuncHGT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['ATAuncHGT'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTuncHGT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTAuncHGT'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUuncHGT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUAuncHGT'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPuncHGT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPAuncHGT'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHuncHGT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHAuncHGT'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBuncHGT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBAuncHGT'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDuncHGT'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDAuncHGT'][linee]*100.,0)))+\

			"{:8d}".format(int(round(MDSDict['ATuncM'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['ATAuncM'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTuncM'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTAuncM'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUuncM'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUAuncM'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPuncM'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPAuncM'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHuncM'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHAuncM'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBuncM'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBAuncM'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDuncM'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDAuncM'][linee]*100.,0)))+\

			"{:8d}".format(int(round(MDSDict['ATuncR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['ATAuncR'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTuncR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPTAuncR'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUuncR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['SHUAuncR'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPuncR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['VAPAuncR'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHuncR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CRHAuncR'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBuncR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['CWBAuncR'][linee]*100.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDuncR'][linee]*10.,0)))+\
			"{:8d}".format(int(round(MDSDict['DPDAuncR'][linee]*100.,0)))+\
	
			"{:8d}".format(MDSDict['DCK'][linee])+\
			"{:8d}".format(MDSDict['SID'][linee])+\
			"{:8d} ".format(MDSDict['PT'][linee])+\

			"{:3.3}".format(MDSDict['EOT'][linee])+\
			"{:3.3}".format(MDSDict['EOH'][linee])+\
			"{:3.3}".format(MDSDict['ESTE'][linee])+\
			"{:5d}".format(MDSDict['LOV'][linee])+\
			"{:5d}".format(MDSDict['HOP'][linee])+\
			"{:5d}".format(MDSDict['HOT'][linee])+\
			"{:5d}".format(MDSDict['HOB'][linee])+\
			"{:5d}".format(MDSDict['HOA'][linee])+\
			"{:5d}".format(int(round(MDSDict['ESTH'][linee])))+\

			"{:2d}".format(MDSDict['day'][linee])+\
			"{:1d}".format(MDSDict['land'][linee])+\
			"{:1d}".format(MDSDict['trk'][linee])+\
			"{:1d}".format(MDSDict['date1'][linee])+\
			"{:1d}".format(MDSDict['date2'][linee])+\
			"{:1d}".format(MDSDict['pos'][linee])+\
			"{:1d}".format(MDSDict['blklst'][linee])+\
			"{:1d}".format(MDSDict['dup'][linee])+\

			"{:2d}".format(MDSDict['SSTbud'][linee])+\
			"{:1d}".format(MDSDict['SSTclim'][linee])+\
			"{:1d}".format(MDSDict['SSTnonorm'][linee])+\
			"{:1d}".format(MDSDict['SSTfreez'][linee])+\
			"{:1d}".format(MDSDict['SSTrep'][linee])+\

			"{:2d}".format(MDSDict['ATbud'][linee])+\
			"{:1d}".format(MDSDict['ATclim'][linee])+\
			"{:1d}".format(MDSDict['ATnonorm'][linee])+\
			"{:1d}".format(MDSDict['ATround'][linee])+\
			"{:1d}".format(MDSDict['ATrep'][linee])+\

			"{:2d}".format(MDSDict['DPTbud'][linee])+\
			"{:1d}".format(MDSDict['DPTclim'][linee])+\
			"{:1d}".format(MDSDict['DPTssat'][linee])+\
			"{:1d}".format(MDSDict['DPTround'][linee])+\
			"{:1d}".format(MDSDict['DPTrep'][linee])+\
			"{:1d}".format(MDSDict['DPTrepsat'][linee])+\
                        "\n"))

    filee.close()
    
    return

#************************************************************************
# MakeStdDict
#************************************************************************
def MakeStdDict():

    MDSDict = {}



    return MDSDict

#************************************************************************
# MakeExtDict
#************************************************************************
def MakeExtDict(FillDict=False):
    
    ''' 
    If FillDict is supplied it should be StdDict.
    The matching fields are used to infill ExtDict on initialisation
    '''
    
    MDSDict = {}
    
    if (FillDict != False):
        MDSDict['shipid'] = copy.copy(FillDict['shipid'])
        MDSDict['UID'] = copy.copy(FillDict['UID']) 
        MDSDict['LAT'] = copy.copy(FillDict['LAT']) 
        MDSDict['LON'] = copy.copy(FillDict['LON']) 
        MDSDict['YR'] = copy.copy(FillDict['YR']) 
        MDSDict['MO'] = copy.copy(FillDict['MO']) 
        MDSDict['DY'] = copy.copy(FillDict['DY'])
        MDSDict['HR'] = copy.copy(FillDict['HR']) 

        MDSDict['SST'] = copy.copy(FillDict['SST']) 
        MDSDict['SSTA'] = copy.copy(FillDict['SSTA'])
        MDSDict['SLP'] = copy.copy(FillDict['SLP']) 
        MDSDict['W'] = copy.copy(FillDict['W']) 

        MDSDict['AT'] = copy.copy(FillDict['AT'])
        MDSDict['ATA'] = copy.copy(FillDict['ATA']) 
        MDSDict['DPT'] = copy.copy(FillDict['DPT']) 
        MDSDict['DPTA'] = copy.copy(FillDict['DPTA'])
        MDSDict['SHU'] = copy.copy(FillDict['SHU']) 
        MDSDict['SHUA'] = copy.copy(FillDict['SHUA'])
        MDSDict['VAP'] = copy.copy(FillDict['VAP']) 
        MDSDict['VAPA'] = copy.copy(FillDict['VAPA'])
        MDSDict['CRH'] = copy.copy(FillDict['CRH']) 
        MDSDict['CRHA'] = copy.copy(FillDict['CRHA'])
        MDSDict['CWB'] = copy.copy(FillDict['CWB']) 
        MDSDict['CWBA'] = copy.copy(FillDict['CWBA'])
        MDSDict['DPD'] = copy.copy(FillDict['DPD']) 
        MDSDict['DPDA'] = copy.copy(FillDict['DPDA'])

        MDSDict['ATtbc'] = copy.copy(FillDict['AT'])      # height screen and solar - set up as original to start and then add to as we go along
        MDSDict['ATAtbc'] = copy.copy(FillDict['ATA']) 
        MDSDict['DPTtbc'] = copy.copy(FillDict['DPT']) 
        MDSDict['DPTAtbc'] = copy.copy(FillDict['DPTA'])
        MDSDict['SHUtbc'] = copy.copy(FillDict['SHU']) 
        MDSDict['SHUAtbc'] = copy.copy(FillDict['SHUA'])
        MDSDict['VAPtbc'] = copy.copy(FillDict['VAP']) 
        MDSDict['VAPAtbc'] = copy.copy(FillDict['VAPA'])
        MDSDict['CRHtbc'] = copy.copy(FillDict['CRH']) 
        MDSDict['CRHAtbc'] = copy.copy(FillDict['CRHA'])
        MDSDict['CWBtbc'] = copy.copy(FillDict['CWB']) 
        MDSDict['CWBAtbc'] = copy.copy(FillDict['CWBA'])
        MDSDict['DPDtbc'] = copy.copy(FillDict['DPD']) 
        MDSDict['DPDAtbc'] = copy.copy(FillDict['DPDA'])
    else:
        MDSDict['shipid'] = []
        MDSDict['UID'] = []
        MDSDict['LAT'] = []
        MDSDict['LON'] = []
        MDSDict['YR'] = []
        MDSDict['MO'] = []
        MDSDict['DY'] = []
        MDSDict['HR'] = []

        MDSDict['SST'] = []
        MDSDict['SSTA'] = []
        MDSDict['SLP'] = []
        MDSDict['W'] = []

        MDSDict['AT'] = []
        MDSDict['ATA'] = []
        MDSDict['DPT'] = []
        MDSDict['DPTA'] = []
        MDSDict['SHU'] = []
        MDSDict['SHUA'] = []
        MDSDict['VAP'] = []
        MDSDict['VAPA'] = []
        MDSDict['CRH'] = []
        MDSDict['CRHA'] = []
        MDSDict['CWB'] = []
        MDSDict['CWBA'] = []
        MDSDict['DPD'] = []
        MDSDict['DPDA'] = []

        MDSDict['ATtbc'] = [] # height screen and solar
        MDSDict['ATAtbc'] = []
        MDSDict['DPTtbc'] = []
        MDSDict['DPTAtbc'] = []
        MDSDict['SHUtbc'] = []
        MDSDict['SHUAtbc'] = []
        MDSDict['VAPtbc'] = []
        MDSDict['VAPAtbc'] = []
        MDSDict['CRHtbc'] = []
        MDSDict['CRHAtbc'] = []
        MDSDict['CWBtbc'] = []
        MDSDict['CWBAtbc'] = []
        MDSDict['DPDtbc'] = []
        MDSDict['DPDAtbc'] = []

    MDSDict['AThc'] = [] # just height
    MDSDict['ATAhc'] = []
    MDSDict['DPThc'] = []
    MDSDict['DPTAhc'] = []
    MDSDict['SHUhc'] = []
    MDSDict['SHUAhc'] = []
    MDSDict['VAPhc'] = []
    MDSDict['VAPAhc'] = []
    MDSDict['CRHhc'] = []
    MDSDict['CRHAhc'] = []
    MDSDict['CWBhc'] = []
    MDSDict['CWBAhc'] = []
    MDSDict['DPDhc'] = []
    MDSDict['DPDAhc'] = []

    MDSDict['ATscn'] = [] # just screen
    MDSDict['ATAscn'] = []
    MDSDict['DPTscn'] = []
    MDSDict['DPTAscn'] = []
    MDSDict['SHUscn'] = []
    MDSDict['SHUAscn'] = []
    MDSDict['VAPscn'] = []
    MDSDict['VAPAscn'] = []
    MDSDict['CRHscn'] = []
    MDSDict['CRHAscn'] = []
    MDSDict['CWBscn'] = []
    MDSDict['CWBAscn'] = []
    MDSDict['DPDscn'] = []
    MDSDict['DPDAscn'] = []

    MDSDict['ATslr'] = [] # just solar
    MDSDict['ATAslr'] = []
    MDSDict['DPTslr'] = []
    MDSDict['DPTAslr'] = []
    MDSDict['SHUslr'] = []
    MDSDict['SHUAslr'] = []
    MDSDict['VAPslr'] = []
    MDSDict['VAPAslr'] = []
    MDSDict['CRHslr'] = []
    MDSDict['CRHAslr'] = []
    MDSDict['CWBslr'] = []
    MDSDict['CWBAslr'] = []
    MDSDict['DPDslr'] = []
    MDSDict['DPDAslr'] = []

    if (FillDict != False):
        MDSDict['DCK'] = copy.copy(FillDict['DCK'])  
        MDSDict['SID'] = copy.copy(FillDict['SID'])  
        MDSDict['PT'] = copy.copy(FillDict['PT']) 

        MDSDict['EOT'] = copy.copy(FillDict['EOT'])  
        MDSDict['EOH'] = copy.copy(FillDict['EOH'])  
        MDSDict['ESTE'] = []
        MDSDict['LOV'] = copy.copy(FillDict['LOV'])  
        MDSDict['HOP'] = copy.copy(FillDict['HOP'])  
        MDSDict['HOT'] = copy.copy(FillDict['HOT'])  
        MDSDict['HOB'] = copy.copy(FillDict['HOB'])  
        MDSDict['HOA'] = copy.copy(FillDict['HOA'])  
        MDSDict['ESTH'] = []

        MDSDict['day'] = copy.copy(FillDict['day']) 
        MDSDict['land'] = copy.copy(FillDict['land'])
        MDSDict['trk'] = copy.copy(FillDict['trk'])  
        MDSDict['date1'] = copy.copy(FillDict['date1']) 
        MDSDict['date2'] = copy.copy(FillDict['date2']) 
        MDSDict['pos'] = copy.copy(FillDict['pos'])  
        MDSDict['blklst'] = copy.copy(FillDict['blklst'])
        MDSDict['dup'] = copy.copy(FillDict['dup'])  

        MDSDict['SSTbud'] = copy.copy(FillDict['SSTbud']) 
        MDSDict['SSTclim'] = copy.copy(FillDict['SSTclim']) 
        MDSDict['SSTnonorm'] = copy.copy(FillDict['SSTnonorm'])
        MDSDict['SSTfreez'] = copy.copy(FillDict['SSTfreez']) 
        MDSDict['SSTrep'] = copy.copy(FillDict['SSTrep']) 

        MDSDict['ATbud'] = copy.copy(FillDict['ATbud']) 
        MDSDict['ATclim'] = copy.copy(FillDict['ATclim'])  
        MDSDict['ATnonorm'] = copy.copy(FillDict['ATnonorm']) 
        MDSDict['ATround'] = copy.copy(FillDict['ATround']) 
        MDSDict['ATrep'] = copy.copy(FillDict['ATrep']) 

        MDSDict['DPTbud'] = copy.copy(FillDict['DPTbud'])  
        MDSDict['DPTclim'] = copy.copy(FillDict['DPTclim']) 
        MDSDict['DPTssat'] = copy.copy(FillDict['DPTssat']) 
        MDSDict['DPTround'] = copy.copy(FillDict['DPTround']) 
        MDSDict['DPTrep'] = copy.copy(FillDict['DPTrep']) 
        MDSDict['DPTrepsat'] = copy.copy(FillDict['DPTrepsat'])
    else:
        MDSDict['DCK'] = []
        MDSDict['SID'] = []
        MDSDict['PT'] = []

        MDSDict['EOT'] = []
        MDSDict['EOH'] = []
        MDSDict['ESTE'] = []
        MDSDict['LOV'] = []
        MDSDict['HOP'] = []
        MDSDict['HOT'] = []
        MDSDict['HOB'] = []
        MDSDict['HOA'] = []
        MDSDict['ESTH'] = []

        MDSDict['day'] = []
        MDSDict['land'] = []
        MDSDict['trk'] = []
        MDSDict['date1'] = []
        MDSDict['date2'] = []
        MDSDict['pos'] = []
        MDSDict['blklst'] = []
        MDSDict['dup'] = []

        MDSDict['SSTbud'] = []
        MDSDict['SSTclim'] = []
        MDSDict['SSTnonorm'] = []
        MDSDict['SSTfreez'] = []
        MDSDict['SSTrep'] = []

        MDSDict['ATbud'] = []
        MDSDict['ATclim'] = []
        MDSDict['ATnonorm'] = []
        MDSDict['ATround'] = []
        MDSDict['ATrep'] = []

        MDSDict['DPTbud'] = []
        MDSDict['DPTclim'] = []
        MDSDict['DPTssat'] = []
        MDSDict['DPTround'] = []
        MDSDict['DPTrep'] = []
        MDSDict['DPTrepsat'] = []
    
    return MDSDict

#************************************************************************
# MakeUncDict
#************************************************************************
def MakeUncDict(FillDict=False):
    
    ''' 
    If FillDict is supplied it should be ExtDict.
    The matching fields are used to infill UncDict on initialisation
    '''
    
    MDSDict = {}
    
    if (FillDict != False):
        MDSDict['shipid'] = copy.copy(FillDict['shipid'])
        MDSDict['UID'] = copy.copy(FillDict['UID']) 
        MDSDict['LAT'] = copy.copy(FillDict['LAT']) 
        MDSDict['LON'] = copy.copy(FillDict['LON']) 
        MDSDict['YR'] = copy.copy(FillDict['YR']) 
        MDSDict['MO'] = copy.copy(FillDict['MO']) 
        MDSDict['DY'] = copy.copy(FillDict['DY'])
        MDSDict['HR'] = copy.copy(FillDict['HR']) 

#        MDSDict['AT'] = copy.copy(FillDict['AT'])
#        MDSDict['ATA'] = copy.copy(FillDict['ATA']) 
#        MDSDict['DPT'] = copy.copy(FillDict['DPT']) 
#        MDSDict['DPTA'] = copy.copy(FillDict['DPTA'])
#        MDSDict['SHU'] = copy.copy(FillDict['SHU']) 
#        MDSDict['SHUA'] = copy.copy(FillDict['SHUA'])
#        MDSDict['VAP'] = copy.copy(FillDict['VAP']) 
#        MDSDict['VAPA'] = copy.copy(FillDict['VAPA'])
#        MDSDict['CRH'] = copy.copy(FillDict['CRH']) 
#        MDSDict['CRHA'] = copy.copy(FillDict['CRHA'])
#        MDSDict['CWB'] = copy.copy(FillDict['CWB']) 
#        MDSDict['CWBA'] = copy.copy(FillDict['CWBA'])
#        MDSDict['DPD'] = copy.copy(FillDict['DPD']) 
#        MDSDict['DPDA'] = copy.copy(FillDict['DPDA'])
    else:
        MDSDict['shipid'] = []
        MDSDict['UID'] = []
        MDSDict['LAT'] = []
        MDSDict['LON'] = []
        MDSDict['YR'] = []
        MDSDict['MO'] = []
        MDSDict['DY'] = []
        MDSDict['HR'] = []

#        MDSDict['AT'] = []
#        MDSDict['ATA'] = []
#        MDSDict['DPT'] = []
#        MDSDict['DPTA'] = []
#        MDSDict['SHU'] = []
#        MDSDict['SHUA'] = []
#        MDSDict['VAP'] = []
#        MDSDict['VAPA'] = []
#        MDSDict['CRH'] = []
#        MDSDict['CRHA'] = []
#        MDSDict['CWB'] = []
#        MDSDict['CWBA'] = []
#        MDSDict['DPD'] = []
#        MDSDict['DPDA'] = []

    MDSDict['ATtbc'] = []
    MDSDict['ATAtbc'] = []
    MDSDict['DPTtbc'] = []
    MDSDict['DPTAtbc'] = []
    MDSDict['SHUtbc'] = []
    MDSDict['SHUAtbc'] = []
    MDSDict['VAPtbc'] = []
    MDSDict['VAPAtbc'] = []
    MDSDict['CRHtbc'] = []
    MDSDict['CRHAtbc'] = []
    MDSDict['CWBtbc'] = []
    MDSDict['CWBAtbc'] = []
    MDSDict['DPDtbc'] = []
    MDSDict['DPDAtbc'] = []

    MDSDict['ATuncT'] = [] # total uncertainty (on the total bias corrected ob)
    MDSDict['ATAuncT'] = []
    MDSDict['DPTuncT'] = []
    MDSDict['DPTAuncT'] = []
    MDSDict['SHUuncT'] = []
    MDSDict['SHUAuncT'] = []
    MDSDict['VAPuncT'] = []
    MDSDict['VAPAuncT'] = []
    MDSDict['CRHuncT'] = []
    MDSDict['CRHAuncT'] = []
    MDSDict['CWBuncT'] = []
    MDSDict['CWBAuncT'] = []
    MDSDict['DPDuncT'] = []
    MDSDict['DPDAuncT'] = []

    MDSDict['ATuncSLR'] = [] # solar bias adjustment uncertainties
    MDSDict['ATAuncSLR'] = []
    MDSDict['DPTuncSLR'] = []
    MDSDict['DPTAuncSLR'] = []
    MDSDict['SHUuncSLR'] = []
    MDSDict['SHUAuncSLR'] = []
    MDSDict['VAPuncSLR'] = []
    MDSDict['VAPAuncSLR'] = []
    MDSDict['CRHuncSLR'] = []
    MDSDict['CRHAuncSLR'] = []
    MDSDict['CWBuncSLR'] = []
    MDSDict['CWBAuncSLR'] = []
    MDSDict['DPDuncSLR'] = []
    MDSDict['DPDAuncSLR'] = []

    MDSDict['ATuncSCN'] = [] # screen adjustment uncertainties
    MDSDict['ATAuncSCN'] = []
    MDSDict['DPTuncSCN'] = []
    MDSDict['DPTAuncSCN'] = []
    MDSDict['SHUuncSCN'] = []
    MDSDict['SHUAuncSCN'] = []
    MDSDict['VAPuncSCN'] = []
    MDSDict['VAPAuncSCN'] = []
    MDSDict['CRHuncSCN'] = []
    MDSDict['CRHAuncSCN'] = []
    MDSDict['CWBuncSCN'] = []
    MDSDict['CWBAuncSCN'] = []
    MDSDict['DPDuncSCN'] = []
    MDSDict['DPDAuncSCN'] = []

    MDSDict['ATuncHGT'] = [] # height adjustment uncertainties
    MDSDict['ATAuncHGT'] = []
    MDSDict['DPTuncHGT'] = []
    MDSDict['DPTAuncHGT'] = []
    MDSDict['SHUuncHGT'] = []
    MDSDict['SHUAuncHGT'] = []
    MDSDict['VAPuncHGT'] = []
    MDSDict['VAPAuncHGT'] = []
    MDSDict['CRHuncHGT'] = []
    MDSDict['CRHAuncHGT'] = []
    MDSDict['CWBuncHGT'] = []
    MDSDict['CWBAuncHGT'] = []
    MDSDict['DPDuncHGT'] = []
    MDSDict['DPDAuncHGT'] = []

    MDSDict['ATuncM'] = [] # measurement uncertainties
    MDSDict['ATAuncM'] = []
    MDSDict['DPTuncM'] = []
    MDSDict['DPTAuncM'] = []
    MDSDict['SHUuncM'] = []
    MDSDict['SHUAuncM'] = []
    MDSDict['VAPuncM'] = []
    MDSDict['VAPAuncM'] = []
    MDSDict['CRHuncM'] = []
    MDSDict['CRHAuncM'] = []
    MDSDict['CWBuncM'] = []
    MDSDict['CWBAuncM'] = []
    MDSDict['DPDuncM'] = []
    MDSDict['DPDAuncM'] = []

    MDSDict['ATuncR'] = [] # rounding uncertainties
    MDSDict['ATAuncR'] = []
    MDSDict['DPTuncR'] = []
    MDSDict['DPTAuncR'] = []
    MDSDict['SHUuncR'] = []
    MDSDict['SHUAuncR'] = []
    MDSDict['VAPuncR'] = []
    MDSDict['VAPAuncR'] = []
    MDSDict['CRHuncR'] = []
    MDSDict['CRHAuncR'] = []
    MDSDict['CWBuncR'] = []
    MDSDict['CWBAuncR'] = []
    MDSDict['DPDuncR'] = []
    MDSDict['DPDAuncR'] = []

    if (FillDict != False):
        MDSDict['DCK'] = copy.copy(FillDict['DCK'])  
        MDSDict['SID'] = copy.copy(FillDict['SID'])  
        MDSDict['PT'] = copy.copy(FillDict['PT']) 

        MDSDict['EOT'] = copy.copy(FillDict['EOT'])  
        MDSDict['EOH'] = copy.copy(FillDict['EOH'])  
        MDSDict['ESTE'] = [] # not yet assessed
        MDSDict['LOV'] = copy.copy(FillDict['LOV'])  
        MDSDict['HOP'] = copy.copy(FillDict['HOP'])  
        MDSDict['HOT'] = copy.copy(FillDict['HOT'])  
        MDSDict['HOB'] = copy.copy(FillDict['HOB'])  
        MDSDict['HOA'] = copy.copy(FillDict['HOA'])  
        MDSDict['ESTH'] = [] # not yet assessed

        MDSDict['day'] = copy.copy(FillDict['day']) 
        MDSDict['land'] = copy.copy(FillDict['land'])
        MDSDict['trk'] = copy.copy(FillDict['trk'])  
        MDSDict['date1'] = copy.copy(FillDict['date1']) 
        MDSDict['date2'] = copy.copy(FillDict['date2']) 
        MDSDict['pos'] = copy.copy(FillDict['pos'])  
        MDSDict['blklst'] = copy.copy(FillDict['blklst'])
        MDSDict['dup'] = copy.copy(FillDict['dup'])  

        MDSDict['SSTbud'] = copy.copy(FillDict['SSTbud']) 
        MDSDict['SSTclim'] = copy.copy(FillDict['SSTclim']) 
        MDSDict['SSTnonorm'] = copy.copy(FillDict['SSTnonorm'])
        MDSDict['SSTfreez'] = copy.copy(FillDict['SSTfreez']) 
        MDSDict['SSTrep'] = copy.copy(FillDict['SSTrep']) 

        MDSDict['ATbud'] = copy.copy(FillDict['ATbud']) 
        MDSDict['ATclim'] = copy.copy(FillDict['ATclim'])  
        MDSDict['ATnonorm'] = copy.copy(FillDict['ATnonorm']) 
        MDSDict['ATround'] = copy.copy(FillDict['ATround']) 
        MDSDict['ATrep'] = copy.copy(FillDict['ATrep']) 

        MDSDict['DPTbud'] = copy.copy(FillDict['DPTbud'])  
        MDSDict['DPTclim'] = copy.copy(FillDict['DPTclim']) 
        MDSDict['DPTssat'] = copy.copy(FillDict['DPTssat']) 
        MDSDict['DPTround'] = copy.copy(FillDict['DPTround']) 
        MDSDict['DPTrep'] = copy.copy(FillDict['DPTrep']) 
        MDSDict['DPTrepsat'] = copy.copy(FillDict['DPTrepsat'])
    else:
        MDSDict['DCK'] = []
        MDSDict['SID'] = []
        MDSDict['PT'] = []

        MDSDict['EOT'] = []
        MDSDict['EOH'] = []
        MDSDict['ESTE'] = []
        MDSDict['LOV'] = []
        MDSDict['HOP'] = []
        MDSDict['HOT'] = []
        MDSDict['HOB'] = []
        MDSDict['HOA'] = []
        MDSDict['ESTH'] = []

        MDSDict['day'] = []
        MDSDict['land'] = []
        MDSDict['trk'] = []
        MDSDict['date1'] = []
        MDSDict['date2'] = []
        MDSDict['pos'] = []
        MDSDict['blklst'] = []
        MDSDict['dup'] = []

        MDSDict['SSTbud'] = []
        MDSDict['SSTclim'] = []
        MDSDict['SSTnonorm'] = []
        MDSDict['SSTfreez'] = []
        MDSDict['SSTrep'] = []

        MDSDict['ATbud'] = []
        MDSDict['ATclim'] = []
        MDSDict['ATnonorm'] = []
        MDSDict['ATround'] = []
        MDSDict['ATrep'] = []

        MDSDict['DPTbud'] = []
        MDSDict['DPTclim'] = []
        MDSDict['DPTssat'] = []
        MDSDict['DPTround'] = []
        MDSDict['DPTrep'] = []
        MDSDict['DPTrepsat'] = []
    
    return MDSDict
