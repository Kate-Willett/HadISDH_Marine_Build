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

Version 2 (29 Sep 2016) Kate Willett
---------
 
Enhancements
Can now cope with the three BC options
 
Changes
Added values_vs_lat_dist which plots the original value vs lat but adds a histogram of the distribution using a right sided Y axis
 
Bug fixes
Latitudes should always be divided by 100 regardless of anomalies or absolutes so I've hard wired this in.


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

import pdb


#*****************************************************
# KATE modified - BC options
#def values_vs_lat(var, lats, data, qc_flags, these_flags, filename, multiplier = 100., doBC = False):
def values_vs_lat(var, lats, data, qc_flags, these_flags, filename, multiplier = 100., doBC = False, doBCtotal = False, doBChgt = False, doBCscn = False):
# end
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
# KATE modified - BC options
    :param bool doBCtotal: work on the full bias corrected QC flag definitions
    :param bool doBChgt: work on the height only bias corrected QC flag definitions
    :param bool doBCscn: work on the screen only bias corrected QC flag definitions
# end
    '''

    # get the final data mask
# KATE modified - QC options
#    data_mask = utils.process_qc_flags(qc_flags, these_flags, doBC = doBC)
    data_mask = utils.process_qc_flags(qc_flags, these_flags, doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn)
# end
    # apportion the mask
    clean_data = np.ma.masked_array(data, data_mask)
    dirty_data = np.ma.masked_array(data, np.logical_not(data_mask))

    # make a 2-panel plot
    plt.clf()

    # all data
    plt.subplot(1,2,1)
# KATE modified - lats should only be div 100, not 10 (absolute.multiplier) so hard wired to 100.
    plt.scatter(data/multiplier, lats/100., c = 'gold', marker = '.') # KATE changed to gold
    plt.scatter(dirty_data/multiplier, lats/100., c = 'r', marker = '.')
    #plt.scatter(data/multiplier, lats/multiplier, c = 'k', marker = '.')
    #plt.scatter(dirty_data/multiplier, lats/multiplier, c = 'r', marker = '.')
# end
    plt.ylim([-90,90])
    plt.yticks(np.arange(-90,120,30), fontsize = 12)
    plt.title("All data", fontsize = 12)
    plt.xlabel(var.units)
    plt.ylabel("latitude")


    # clean data
    plt.subplot(1,2,2)
# KATE modified - lats should only be div 100, not 10 (absolute.multiplier) so hard wired to 100.
    plt.scatter(clean_data/multiplier, lats/100., c = 'b', marker = '.')
    #plt.scatter(clean_data/multiplier, lats/multiplier, c = 'b', marker = '.')
# end

    plt.ylim([-90,90])
    plt.yticks(np.arange(-90,120,30), fontsize = 12)
    plt.title("Clean data", fontsize = 12)
    plt.xlabel(var.units)

    plt.figtext(0.5, 0.95, var.long_name, ha = 'center', fontsize = 14)

    plt.savefig(filename)

    return # plot_values_vs_lat


#*****************************************************
# KATE modified - BC options
#def values_vs_lat_dist(var, lats, data, qc_flags, these_flags, filename, multiplier = 100., doBC = False):
def values_vs_lat_dist(var, lats, data, qc_flags, these_flags, filename, multiplier = 100., doBC = False, doBCtotal = False, doBChgt = False, doBCscn = False):
# end
    '''
    Plots showing benefit of QC using all QC flags bar day/night
    This version adds a line for each set of data to show the frequency distribution of all values

    :param MetVar variable: input variable
    :param array lats: latitudes
    :param array data: indata
    :param array qc_flags: QC flag array
    :param array these_flags: QC flags to apply
    :param str filename: output filename
    :param float multiplier: multiplier which has been applied to the data already.
    :param bool doBC: work on the bias corrected QC flag definitions
# KATE modified - BC options
    :param bool doBCtotal: work on the full bias corrected QC flag definitions
    :param bool doBChgt: work on the height only bias corrected QC flag definitions
    :param bool doBCscn: work on the screen only bias corrected QC flag definitions
# end
    '''

    # get the final data mask
# KATE modified - BC options
#    data_mask = utils.process_qc_flags(qc_flags, these_flags, doBC = doBC)
    data_mask = utils.process_qc_flags(qc_flags, these_flags, doBC = doBC, doBCtotal = doBCtotal, doBChgt = doBChgt, doBCscn = doBCscn)
# end

    # apportion the mask
    clean_data = np.ma.masked_array(data, data_mask)
    dirty_data = np.ma.masked_array(data, np.logical_not(data_mask))

    # make a 2-panel plot
    plt.clf()

    # all data
    ax1 = plt.subplot(1,2,1)
# KATE modified - lats should only be div 100, not 10 (absolute.multiplier) so hard wired to 100.
    ax1.scatter(data/multiplier, lats/100., s=10, c = 'deepskyblue', marker = 'o', edgecolor='none') # KATE changed to gold
    ax1.scatter(dirty_data/multiplier, lats/100., s=10, c = 'r', marker = 'o', edgecolor='none') # KATE changed to gold
#    ax1.scatter(data/multiplier, lats/100., c = 'gold', marker = '.')
#    ax1.scatter(dirty_data/multiplier, lats/100., c = 'r', marker = '.')
    #plt.scatter(data/multiplier, lats/multiplier, c = 'k', marker = '.')
    #plt.scatter(dirty_data/multiplier, lats/multiplier, c = 'r', marker = '.')
# end

    # Make histograms of the distribution of values and plot 
    # What are the xaxis limits?
    xMin = np.min(data/multiplier)
    xMax = np.max(data/multiplier)
    xRange = xMax - xMin
    xMin = np.floor(xMin - (0.1*xRange))
    xMax = np.ceil(xMax + (0.1*xRange))    
    
    # Set up equally spaced histogram bins between min and max range (including end point as a value for 51 bins, 
    binsies = np.linspace(xMin,xMax,51) # a range of bins from left most to right most point

    # Set up the second axes
    ax2 = ax1.twinx()
    
    # Plot for all data
    ThisHist = np.histogram(data/multiplier,binsies)
    y2Max = np.max(ThisHist[0])
    HalfX = (ThisHist[1][1] - ThisHist[1][0]) / 2.
    ax2.plot(ThisHist[1][0:50]+HalfX,ThisHist[0],c='deepskyblue',linestyle='solid',linewidth=4) 
    meanHist = '{:5.1f}'.format(np.mean(data/multiplier))
    sdHist = '{:5.1f}'.format(np.std(data/multiplier))
    ax2.annotate('All ('+meanHist+', '+sdHist+')',xy=(0.05,0.96),xycoords='axes fraction',size=12,color='deepskyblue')

    # Plot for failed data
    ThisHist = np.histogram(dirty_data[~dirty_data.mask]/multiplier,binsies)
    HalfX = (ThisHist[1][1] - ThisHist[1][0]) / 2.
    ax2.plot(ThisHist[1][0:50]+HalfX,ThisHist[0],c='r',linestyle='solid',linewidth=4) 
    meanHist = '{:5.1f}'.format(np.mean(dirty_data[~dirty_data.mask]/multiplier))
    sdHist = '{:5.1f}'.format(np.std(dirty_data[~dirty_data.mask]/multiplier))
    PctFail = '{:5.1f}'.format((len(dirty_data[~dirty_data.mask]) / np.float(len(data))) * 100.)+'%'
    ax2.annotate('Bad Obs ('+meanHist+', '+sdHist+', '+PctFail+')',xy=(0.05,0.92),xycoords='axes fraction',size=12,color='r')

    ax1.set_ylim([-90,90])
    ax1.set_xlim([xMin,xMax])
    ax2.set_ylim([0,y2Max*1.1])
    ax1.set_yticks(np.arange(-90,120,30))
    #ax1.yticks(np.arange(-90,120,30), fontsize = 12)
    ax1.set_title("All data")
    #ax1.title("All data", fontsize = 12)
    ax1.set_xlabel(var.units)
    ax1.set_ylabel("latitude")
    labels = [item.get_text() for item in ax2.get_yticklabels()]
    empty_string_labels = ['']*len(labels)
    ax2.set_yticklabels(empty_string_labels)
    #ax2.set_ylabel("number of observations")

    #pdb.set_trace()

    # clean data
    ax1 = plt.subplot(1,2,2)
# KATE modified - lats should only be div 100, not 10 (absolute.multiplier) so hard wired to 100.
    ax1.scatter(clean_data/multiplier, lats/100., s=10, c = 'b', marker = 'o', edgecolor='none')
#    ax1.scatter(clean_data/multiplier, lats/100., c = 'b', marker = '.')
    #plt.scatter(clean_data/multiplier, lats/multiplier, c = 'b', marker = '.')
# end

    # Make histograms of the distribution of values and plot 
    # xaxis limits already established from above

    # Set up the second axes
    ax2 = plt.twinx()
    
    # Plot for all data
    ThisHist = np.histogram(clean_data[~clean_data.mask]/multiplier,binsies)
#    y2Max = np.max(ThisHist[0])
    HalfX = (ThisHist[1][1] - ThisHist[1][0]) / 2.
    ax2.plot(ThisHist[1][0:50]+HalfX,ThisHist[0],c='b',linestyle='solid',linewidth=4) 
    meanHist = '{:5.1f}'.format(np.mean(clean_data[~clean_data.mask]/multiplier))
    sdHist = '{:5.1f}'.format(np.std(clean_data[~clean_data.mask]/multiplier))
    ax2.annotate('Clean Obs ('+meanHist+', '+sdHist+')',xy=(0.05,0.96),xycoords='axes fraction',size=12,color='b')

    ax1.set_ylim([-90,90])
    ax1.set_xlim([xMin,xMax])
    ax2.set_ylim([0,y2Max*1.1])
    ax1.set_yticks(np.arange(-90,120,30))
    #ax1.set_yticks(np.arange(-90,120,30), fontsize = 12)
    labels = [item.get_text() for item in ax1.get_yticklabels()]
    empty_string_labels = ['']*len(labels)
    ax1.set_yticklabels(empty_string_labels)
    ax1.set_title("Clean data")
    #ax1.set_title("Clean data", fontsize = 12)
    ax1.set_xlabel(var.units)
    ax2.set_ylabel("number of observations")

    plt.figtext(0.5, 0.95, var.long_name, ha = 'center', fontsize = 14)

    plt.savefig(filename)

    return # values_vs_lat_dist
