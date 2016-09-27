#!/usr/local/sci/bin/python2.7
#*****************************
#
# general Python gridding script
#
#
#************************************************************************
"""
Author: Robert Dunn
Created: March 2016
Last update: 12 April 2016
Location: /project/hadobs2/hadisdh/marine/PROGS/Build

-----------------------
CODE PURPOSE AND OUTPUT
-----------------------
Sets paths and fixed variables centrally to prevent issues with multiple versions in the same place

-----------------------
LIST OF MODULES
-----------------------
None

-----------------------
DATA
-----------------------
No external data required.  Data paths set here in code

-----------------------
HOW TO RUN THE CODE
-----------------------
Called from all scripts with a from .... import * command

-----------------------
OUTPUT
-----------------------
None


-----------------------
VERSION/RELEASE NOTES
-----------------------

Version 2 26 Sep 2016 (Kate Willett)
---------
 
Enhancements
This can now cope with additional options for an iterative approach
--doQCit1 - ERAclimNBC, all QC ex. no buddy check
--doQCit2 - OBSclim1NBC, all QC ex. no buddy check
--doQCit3 - OBSclim2NBC, all QC inc buddy check
--doBC - as previously but reads in from OBSclim2BC
if neither doQC... or doBC are set then this is a raw run from OBSclim2NBC data

still has original --doQC option!
 
Changes
 
Bug fixes


Version 1 (release date)
---------
 
Enhancements
 
Changes
 
Bug fixes
 

-----------------------
OTHER INFORMATION
-----------------------
Sets a load of paths and defaults.

Should be the only place to edit these each time around.
"""


import datetime as dt


#*********************************************
class Settings(object):
    '''
    Class to hold all settings information
    '''
    
    def __init__(self, OUTROOT, ICOADS_LOCATION, DATA_LOCATION, PLOT_LOCATION, START_YEAR, END_YEAR, doMedian, plots, mdi):
        self.OUTROOT = OUTROOT
        self.ICOADS_LOCATION = ICOADS_LOCATION
        self.DATA_LOCATION = DATA_LOCATION
        self.PLOT_LOCATION = PLOT_LOCATION
        self.START_YEAR = START_YEAR
        self.END_YEAR = END_YEAR
        self.doMedian = doMedian
        self.plots = plots
        self.mdi = mdi

    def __str__(self):     

        outstring = "Settings are:\n OUTROOT = {}\n ICOADS_LOCATION = {}\n DATA_LOCATION = {}\n PLOT_LOCATION = {}\n START_YEAR = {}\n END_YEAR = {}\n doMedian = {}\n plots = {}".format(self.OUTROOT, self.ICOADS_LOCATION, self.DATA_LOCATION, self.PLOT_LOCATION, self.START_YEAR, self.END_YEAR, self.doMedian, self.plots)

        return outstring

    __repr__ = __str__

#*********************************************
#*********************************************

#*********************************************
# *** KATE MODIFIED
def set(doBC = False, doQC = True, doQC1it = False, doQC2it = False, doQC3it = False):
#def set(doBC = False, doQC = True):
# end
    '''
    Create a settings object and return

    :param bool doBC: set up for bias correction
    :param bool doQC: set up for quality control
# *** KATE MODIFIED
    :param bool doQC1it: set up for 1st iteration quality control with no buddy check
    :param bool doQC2it: set up for 2nd iteration quality control with no buddy check
    :param bool doQC3it: set up for 3rd iteration quality control with buddy check
# end

    :returns: Settings object
    '''


    plots = True
    doMedian = False

    if doBC:
        # Constants in CAPS
# *** KATE MODIFIED
        OUTROOT = "OBSclim2BC"
        #OUTROOT = "ERAclimBC"
# end

        ICOADS_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)
# *** KATE MODIFIED
        DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDSOBSclim2BC/"
        PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTSOBSclim2BC/"
        #DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS_BC/"
        #PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS_BC/"
# end

    elif doQC:
        # Constants in CAPS
        OUTROOT = "ERAclimNBC"

        ICOADS_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)
        # KW Changed GRIDS to GRIDS2 adn PLOTS to PLOTS2 to make sure I don't write over what has been done already
        DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS3/"
        PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS3/"

# *** KATE MODIFIED
    elif doQC1it:
        # Constants in CAPS
        OUTROOT = "ERAclimNBC"

        ICOADS_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)
        DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDSERAclimNBC/"
        PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTSERAclimNBC/"

    elif doQC2it:
        # Constants in CAPS
        OUTROOT = "OBSclim1NBC"

        ICOADS_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)
        DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDSOBSclim1NBC/"
        PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTSOBSclim1NBC/"

    elif doQC3it:
        # Constants in CAPS
        OUTROOT = "OBSclim2NBC"

        ICOADS_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)
        DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDSOBSclim2NBC/"
        PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTSOBSclim2NBC/"

# end
# KATE modified
    else:
        # Constants in CAPS
        OUTROOT = "OBSclim2NBC"

        ICOADS_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)
        DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDSOBSclim2noQC/"
        PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTSOBSclim2noQC/"
    #else:
    #    # Constants in CAPS
    #    OUTROOT = "ERAclimNBC"

    #    ICOADS_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)
    #    # KW Changed GRIDS to GRIDS2 adn PLOTS to PLOTS2 to make sure I don't write over what has been done already
    #    DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS_noQC/"
    #    PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS_noQC/"
# end

    START_YEAR = 1973
    END_YEAR = dt.datetime.now().year - 1

    mdi = -1.e30


    return Settings(OUTROOT, ICOADS_LOCATION, DATA_LOCATION, PLOT_LOCATION, START_YEAR, END_YEAR, doMedian, plots, mdi) # set


#------------------------------------------------------------
# END
#------------------------------------------------------------
