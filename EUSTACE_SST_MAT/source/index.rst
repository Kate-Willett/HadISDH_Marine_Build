.. MDS_QC documentation master file, created by
   sphinx-quickstart on Wed Oct 14 07:04:52 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MDS QC documentation
==================================

Introduction and Rationale
--------------------------

This is the documentation for the MDS QC system's latest incarnation 
in Python. The purpose of the code is

1. to read in marine meteorological reports in IMMA1 format
2. to put them in a database
3. to pull them out of the database, quality control (QC) them and stick them back in the database

The code itself lives in the CMA FCM repository which can be found here

http://fcm9/projects/ClimateMonitoringAttribution/browser/EUSTACE/EUSTACE_SST_MAT

The routines use the MarineReport class to store information about individual 
marine reports. The class stores information about the position of the observation, 
the time of observation, the ship's speed and direction and a set of variables such 
as sea-surface temperature (SST) and marine air temperature (MAT). Additional information 
like the climatological average SST can also be stored along with a number of quality 
control flags.

The basic QC routines operate on a pass/fail basis. An observation is either good 
or it's bad. Some checks are simple - is the ob within 8 degrees of climatology - 
some are *really* simple - is there an SST - but others are complex. For example, 
the track check is based on a series of observations from a single ship which are 
subjected to numerous separate tests leading to an overall decision about which observations in a 
longer sequence look like they have serious positional errors.

The initial port of the code was a simple (haha) recode of the MDS3 system, 
aided by the extensive documentation produced for the MDS2 system, which 
had functional specifications and other useful documentation. However, as good as 
that system was the aims of recoding the system were:

1. to remove the dependency on the old binary tenday format.
2. to make the QC more modular, separating data storage formats from processing code so that 
   we can defer decisions about database architecture or file formats for a little while. Also, 
   this makes it easier in principle to code and makes the code more portable.
3. to reduce the number of programming languages involved from shell, perl and fortran to just 
   Python. The downside of this is that the perl code worked beautifully.
4. Python is also desirable because it makes the code easier to share (again, in principle) 
   and one of the outcomes of the recent SST workshop was an effort to share code.
5. Recoding the system means that someone understands it (at least temporarily) and they 
   can improve it (a step which is long overdue and now substantially easier) and add to 
   it; it would be nice to incorporate `IQUAM <http://www.star.nesdis.noaa.gov/sod/sst/iquam/>`_ QC tests 
   for example.

That's it, I'm done with reasons. This beautiful documentation was put together 
automatically by Sphinx which also does latex-based pdfs. If you are not familiar with this 
layout, the index and module index links below take you to actual indexes which link back 
to the documentation for each function in the QC module suite.

Running the damn thing
----------------------

First you will have to check the code out of the FCM repository. I have no idea how to do this, 
but the repository is here::

  http://fcm9/projects/ClimateMonitoringAttribution/browser/EUSTACE/EUSTACE_SST_MAT

Running the code to build and populate the data base with the raw data is done from the 
command line by invoking::

  python2.7 make_db.py -i configuration.txt --year1 1850 --year2 1899

The year1 and year2 arguments tell it the first and last years which you want to add to the 
database. It will generate all years between these two years. So the command above will 
generate tables from 1850 to 1899 inclusive and populate them from the IMMA1 files.

The configuration.txt file needs to contain the following lines::

  data_base_dir,/data/local/hadjj/ICOADS.2.5.1/
  data_base_name,ICOADS.db
  ICOADS_dir,/data/local/hadjj/ICOADS.2.5.1/
  SST_climatology,/home/h04/hadjj/HadSST2_pentad_climatology.nc
  MAT_climatology,/home/h04/hadjj/HadNMAT2_pentad_climatology.nc
  SST_stdev_climatology,/home/h04/hadjj/HadSST2_pentad_stdev_climatology.nc
  NOC_adjustment_dir,/data/local2/hadjj/NMAT/
  IDs_to_exclude,/home/h04/hadjj/PyWorkspace/EUSTACE_SST_MAT/list_of_ids_that_are_not_ships.txt

The first two tell the code where to build the database and what to call it. The ICOADS_dir is the 
location of the IMMA1 files. The next three elements (SST_climatology, MAT_climatology and 
SST_stdev_climatology) are the locations of the climatologies that are to be used for calculating 
anomalies and performing the QC. The next line (NOC_adjustment_dir) is the directory used 
for reading in air temperature adjustment files, which don't yet exist. The final file, 
IDs_to_exclude is a list of IDs that are associated with moorings of various kinds.

The next step is to run the basic quality control, which can be done by invoking the 
following command from the command line::

  python2.7 base_qc.py -i configuration.txt --year1 1850 --year2 1899

Once basic QC is done, you can run the track check. You need to run the basic QC for at 
least a month longer than you plan to run the track check because the track check needs 
data from before and after the segment it is working on. Running the track check is done 
like so::

  python2.7 track_check.py -i configuration.txt --year1 1850 --year2 1898

and finally the buddy check, as with the track check, you need data from before and 
after the segments that have had undergone basic QC and track check QC. Run buddy check QC 
like so::

  python2.7 buddy_check.py -i configuration.txt --year1 1850 --year2 1897

And that does it. There is a script::

  run_all.sh

which will run the QC modules in order and extract the observations from the data base 
and write them to ascii files.

Extracting data from the data base
----------------------------------

Data can be extracted from the data base via the usual means. There is a function for 
getting the data out in an ascii format::

  python2.7 extract_from_db.py -i configuration.txt --year1 1850 --year2 1897

which does the trick. It outputs the files in the ascii version of the tenday format, 
which is used in the HadSST3 and HadISST2 processing.

.. toctree::
   :maxdepth: 2



Some Navigation Aids
--------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

List of Classes and Functions
-----------------------------

Database building
^^^^^^^^^^^^^^^^^
.. automodule:: make_db
   :members:

Base QC
^^^^^^^^

.. automodule:: base_qc
   :members:

Track Check
^^^^^^^^^^^^

.. automodule:: track_check
   :members:

Buddy Check
^^^^^^^^^^^^

.. automodule:: buddy_check
   :members:

IMMA Reader
^^^^^^^^^^^^

.. automodule:: IMMA2
   :members:


QC routines
^^^^^^^^^^^

.. automodule:: qc
   :members:
   :special-members:

Track Check QC routines
^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: qc_track_check
   :members:
   :special-members:

Buddy Check QC routines
^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: qc_buddy_check
   :members:
   :special-members:

Database Handling routines
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: database_handler
   :members:
   :special-members:



Spherical Geometry
^^^^^^^^^^^^^^^^^^

The spherical geometry module contains some simple functions for calculating things 
on a sphere: distances, headings, interpolate positions and so on. The routines are 
coded from formulae found in `Ed Williams' Aviation Formulary <http://williams.best.vwh.net/avform.htm>`_

.. automodule:: spherical_geometry
   :members:

Glossary
^^^^^^^^

.. glossary::
   :sorted:

   SST
      Sea surface temperature.

   MAT
      Marine air temperature

   NMAT
      Night Marine Air temperature, the kind of :term:`MAT` that happens at :term:`night`.

   Night
      Defined for the purposes of marine QC as being any time between an hour after sunset and an hour 
      after sunrise. This was a trick, originally conceived to do for Vampires with an interest in 
      marine climatology.

   Badger
      naturally enemy of the grape

   MDS
      Marine Data System, used to process marine observations

   QC
      Quality control, which refers to the practice of disavowing certain measurements, though they be 
      made with diligence otherwise indistinguishable from the commonplace.

   ICOADS
      `International Comprehensive Ocean Atmosphere Data Set <http://icoads.noaa.gov/>`_ - the true 
      home of digital marine observations. This is the main resource for marine climatology and the 
      source of observations assumed in this documentation.

   IMMA
      International Marine Meteorological Archive - An ascii format used for the storage of marine 
      meteorological data in ICOADS.

   Glossary
      A compendium of words that gives the author of it license to abuse the English language in the 
      most wretched and obfuscating manner conceivable, safe in the assurance that his :term:`ass` is covered 
      whilst burying his meaning beneath a mouldering heap of :term:`TLA` and jargon.

   Ass
      An animal a bit like a donkey; Something better covered, perhaps by a :term:`Glossary`. 

   TLA
      Three Letter Acronym
