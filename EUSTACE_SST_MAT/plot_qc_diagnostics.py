#!/usr/local/sci/bin/python2.7
#*****************************
#
# plot each month's obs and highlight QC flags
#
#
#************************************************************************
'''
Author: Robert Dunn
Created: March 2016
Last update: 12 April 2016
Location: /project/hadobs2/hadisdh/marine/PROGS/Build

-----------------------
CODE PURPOSE AND OUTPUT
-----------------------
Small script to plot the observations and show those retained by applying QC flags

-----------------------
LIST OF MODULES
-----------------------
utils.py

-----------------------
DATA
-----------------------
/project/hadobs2/hadisdh/marine/

Called from gridding_cam.py

-----------------------
HOW TO RUN THE CODE
-----------------------
Called from external code.

-----------------------
OUTPUT
-----------------------
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS2/

Plots to appear in 
/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/PLOTS2/

-----------------------
VERSION/RELEASE NOTES
-----------------------

Version 1 (release date)
---------
 
Enhancements
 
Changes
 
Bug fixes
 

-----------------------
OTHER INFORMATION
-----------------------
'''

import matplotlib.pyplot as plt
import numpy as np

import utils as utils



#*****************************************************
def values_vs_lat(var, lats, data, qc_flags, these_flags, filename, multiplier = 100., doBC = False):
    '''
    Plots showing benefit of QC using all QC flags bar day/night

    :param MetVar variable: input variable
    :param array lats: latitudes
    :param array data: indata
    :param array qc_flags: QC flag array
    :param array these_flags: QC flags to apply
    :param str filename: output filename
    :param float multiplier: multiplier which has been applied to the data already.
    :param bool doBC: work on the bias corrected QC flag definitions
    '''

    # get the final data mask
    data_mask = utils.process_qc_flags(qc_flags, these_flags, doBC = doBC)

    # apportion the mask
    clean_data = np.ma.masked_array(data, data_mask)
    dirty_data = np.ma.masked_array(data, np.logical_not(data_mask))

    # make a 2-panel plot
    plt.clf()

    # all data
    plt.subplot(1,2,1)
    plt.scatter(data/multiplier, lats/multiplier, c = 'k', marker = '.')
    plt.scatter(dirty_data/multiplier, lats/multiplier, c = 'r', marker = '.')

    plt.ylim([-90,90])
    plt.yticks(np.arange(-90,120,30), fontsize = 12)
    plt.title("All data", fontsize = 12)
    plt.xlabel(var.units)
    plt.ylabel("latitude")


    # clean data
    plt.subplot(1,2,2)
    plt.scatter(clean_data/multiplier, lats/multiplier, c = 'b', marker = '.')

    plt.ylim([-90,90])
    plt.yticks(np.arange(-90,120,30), fontsize = 12)
    plt.title("Clean data", fontsize = 12)
    plt.xlabel(var.units)

    plt.figtext(0.5, 0.95, var.long_name, ha = 'center', fontsize = 14)

    plt.savefig(filename)

    return # plot_values_vs_lat
