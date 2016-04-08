#!/usr/local/sci/bin/python2.7
#*****************************
#
# plot each month's obs and highlight QC flags
#
#
#************************************************************************

import matplotlib.pyplot as plt
import numpy as np

import utils as utils



#*****************************************************
def values_vs_lat(var, lats, data, qc_flags, these_flags, filename, multiplier = 100.):
    '''
    Plots showing benefit of QC using all QC flags bar day/night

    :param MetVar variable: input variable
    :param array lats: latitudes
    :param array data: indata
    :param array qc_flags: QC flag array
    :param array these_flags: QC flags to apply
    :param str filename: output filename
    :param float multiplier: multiplier which has been applied to the data already.
    '''

    # get the final data mask
    data_mask = utils.process_qc_flags(qc_flags, these_flags)

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
