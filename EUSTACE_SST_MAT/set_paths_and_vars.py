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

Version 3 7 May 2020 (Kate Willett)
---------
 
Enhancements
--doNOWHOLE - BC total but without any data that have whole number rounding flag
 
Changes
 
Bug fixes


Version 2 26 Sep 2016 (Kate Willett)
---------
 
Enhancements
This can now cope with additional options for an iterative approach
--doQCit1 - ERAclimNBC, all QC ex. no buddy check
--doQCit2 - OBSclim1NBC, all QC ex. no buddy check
--doQCit3 - OBSclim2NBC, all QC inc buddy check
--doBC - as previously but reads in from OBSclim2BC
--doBCtotal - as previously but reads in from OBSclim2BClocal
--doBChgt - as previously but reads in from OBSclim2BClocal and out to GRIDSOBSclim2BClocalHGT
--doBCscn - as previously but reads in from OBSclim2BClocal and out to GRIDSOBSclim2BClocalSCN
if neither doQC... or doBC are set then this is a raw run from OBSclim2NBC data

still has original --doQC option!

This also has a --ShipOnly option to work with only ship platform data
 
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
def set(doBC = False, doBCtotal = False, doBChgt = False, doBCscn = False, doNOWHOLE = False, doQC = True, doQC1it = False, doQC2it = False, doQC3it = False, 
        doUSLR = False, doUSCN = False, doUHGT = False, doUR = False, doUM = False, doUC = False, doUTOT = False, ShipOnly = False):
#def set(doBC = False, doQC = True):
# end
    '''
    Create a settings object and return

    :param bool doBC: set up for bias correction
# *** KATE MODIFIED
    :param bool doBCtotal: set up for full bias correction
    :param bool doBChgt: set up for height only bias correction
    :param bool doBCscn: set up for screen only bias correction
# end
    :param bool doNOWHOLE: set up for bias correction and no whole numbers
    :param bool doQC: set up for quality control
# *** KATE MODIFIED
    :param bool doQC1it: set up for 1st iteration quality control with no buddy check
    :param bool doQC2it: set up for 2nd iteration quality control with no buddy check
    :param bool doQC3it: set up for 3rd iteration quality control with buddy check
# end
# UNC NEW
    :param bool doUSLR: work on BC and solar adj uncertainty with correlation
    :param bool doUSCN: work on BC and instrument adj uncertainty with correlation
    :param bool doUHGT: work on BC and height adj uncertainty with correlation
    :param bool doUR: work on BC and rounding uncertainty with no correlation
    :param bool doUM: work on BC and measurement uncertainty with no correlation
    :param bool doUC: work on BC and climatological uncertainty with no correlation
    :param bool doUTOT: work on BC and total uncertainty with no correlation
# *** KATE MODIFIED
    :param bool ShipOnly: set up for working with ship data only
# end

    :returns: Settings object
    '''


    plots = False
    doMedian = False
    
# KATE MODIFIED TO BRING OUT COMMON DIR PATHS
## ICOADS.2.5.1
#    ICOADS_DIR="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/"
#    DATA_DIR="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/"
#    PLOT_DIR="/project/hadobs2/hadisdh/marine/"
# ICOADS 3.0.0    
    ICOADS_DIR="/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/"
    DATA_DIR="/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/"
    PLOT_DIR="/project/hadobs2/hadisdh/marine/ICOADS.3.0.0/"
# end

    if doBC:
        # Constants in CAPS
# *** KATE MODIFIED
        OUTROOT = "OBSclim2BClocal"
        #OUTROOT = "ERAclimBC"
# end

# KATE MODIFIED - using common dir strings
        ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
        #ICOADS_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)

        DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2BClocal/"
        PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2BClocal/"
        #DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS_BC/"
        #PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS_BC/"

        if ShipOnly:
	    OUTROOT = "OBSclim2BClocal"
            ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
            DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2BClocalship/"
            PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2BClocalship/"
# end

# KATE MODIFIED - othe BC options
    elif doBCtotal:
        # Constants in CAPS
        OUTROOT = "OBSclim2BClocal"

        ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)

        DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2BClocal/"
        PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2BClocal/"

        if ShipOnly:
	    OUTROOT = "OBSclim2BClocal"
            ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
            DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2BClocalship/"
            PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2BClocalship/"

    elif doNOWHOLE:
        # Constants in CAPS
        OUTROOT = "OBSclim2BClocal"

        ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)

        DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2BClocalNOWHOLE/"
        PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2BClocalNOWHOLE/"

        if ShipOnly:
	    OUTROOT = "OBSclim2BClocal"
            ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
            DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2BClocalshipNOWHOLE/"
            PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2BClocalshipNOWHOLE/"

    elif doBChgt:
        # Constants in CAPS
        OUTROOT = "OBSclim2BClocal"

        ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)

        DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2BClocalHGT/"
        PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2BClocalHGT/"

        if ShipOnly:
	    OUTROOT = "OBSclim2BClocal"
            ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
            DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2BClocalHGTship/"
            PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2BClocalHGTship/"

    elif doBCscn:
        # Constants in CAPS
        OUTROOT = "OBSclim2BClocal"

        ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)

        DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2BClocalINST/"
        PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2BClocalINST/"

        if ShipOnly:
	    OUTROOT = "OBSclim2BClocal"
            ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
            DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2BClocalINSTship/"
            PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2BClocalINSTship/"

# end

    elif doQC:
        # Constants in CAPS
        OUTROOT = "ERAclimNBC"

# KATE MODIFIED - using common dir strings
        ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
        DATA_LOCATION=DATA_DIR+"GRIDS3/"
        PLOT_LOCATION=PLOT_DIR+"PLOTS3/"
        #ICOADS_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)
        #DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS3/"
        #PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS3/"
# end

# *** KATE MODIFIED
    elif doQC1it:
        # Constants in CAPS
        OUTROOT = "ERAclimNBC"

        ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
        DATA_LOCATION=DATA_DIR+"GRIDSERAclimNBC/"
        PLOT_LOCATION=PLOT_DIR+"PLOTSERAclimNBC/"

        if ShipOnly:
	    OUTROOT = "ERAclimNBC"
            ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
            DATA_LOCATION=DATA_DIR+"GRIDSERAclimNBCship/"
            PLOT_LOCATION=PLOT_DIR+"PLOTSERAclimNBCship/"

    elif doQC2it:
        # Constants in CAPS
        OUTROOT = "OBSclim1NBC"

        ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
        DATA_LOCATION=DATA_DIR+"GRIDSOBSclim1NBC/"
        PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim1NBC/"

        if ShipOnly:
	    OUTROOT = "OBSclim1NBC"
            ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
            DATA_LOCATION=DATA_DIR+"GRIDSOBSclim1NBCship/"
            PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim1NBCship/"

    elif doQC3it:
        # Constants in CAPS
        OUTROOT = "OBSclim2NBC"

        ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
        DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2NBC/"
        PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2NBC/"

        if ShipOnly:
	    OUTROOT = "OBSclim2NBC"
            ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
            DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2NBCship/"
            PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2NBCship/"

# end
# KATE modified
    else:
        # Constants in CAPS
        OUTROOT = "OBSclim2NBC"

        ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
        DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2noQC/"
        PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2noQC/"

        if ShipOnly:
	    OUTROOT = "OBSclim2NBC"
            ICOADS_LOCATION=ICOADS_DIR+"{}/".format(OUTROOT)
            DATA_LOCATION=DATA_DIR+"GRIDSOBSclim2noQCship/"
            PLOT_LOCATION=PLOT_DIR+"PLOTSOBSclim2noQCship/"

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
