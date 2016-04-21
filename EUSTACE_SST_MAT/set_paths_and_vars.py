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


plots = True
doMedian = False

doBC = True

if doBC:
    # Constants in CAPS
    OUTROOT = "ERAclimBC"

    ICOADS_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)
    # KW Changed GRIDS to GRIDS2 adn PLOTS to PLOTS2 to make sure I don't write over what has been done already
    DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS_BC/"
    PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS_BC/"

else:
    # Constants in CAPS
    OUTROOT = "ERAclimNBC"

    ICOADS_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/{}/".format(OUTROOT)
    # KW Changed GRIDS to GRIDS2 adn PLOTS to PLOTS2 to make sure I don't write over what has been done already
    DATA_LOCATION="/project/hadobs2/hadisdh/marine/ICOADS.2.5.1/GRIDS3/"
    PLOT_LOCATION="/project/hadobs2/hadisdh/marine/PLOTS3/"


START_YEAR = 1973
END_YEAR = dt.datetime.now().year - 1

mdi = -1.e30

#------------------------------------------------------------
# END
#------------------------------------------------------------
