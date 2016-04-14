GRIDDING README

Robert Dunn
24th March 2016

***************************************************************
A description on how to run the gridding routines for HadISDH-Marine

***************************************************************

1) Run the main conversion scripts (gridding_cam.py) which takes the new_suite_* files and converts them
to gridded forms.  Firstly into 3-hourly 1x1 grids, then these are averaged up into daily 1x1, then
monthly 1x1 and finally monthly 5x5 grids.  One file is output per month for each of these versions.  This
also outputs versions for _all, _day and _night - to allow separation of day and night periods.  Any boxes
which are a mix of day and night are set as day.

2) Convert to pentads.  There are two options, one is to go from the daily files (dailies_to_pentads.py)
or to go from the 3hrly data (3hrlies_to_pentads.py).  Both account for Feb 29th.  The latter first
creates pentad-average values at the 8 3-hourly timesteps.  Then these 8 values are averaged to create a
value for the pentad.  This is run separately for day and night

3) Make the pentad climatology.  Currently (24th March 2016) this has been written to take in the pentads
created from the daily values.  The input filenames will need changing in the .py file if the alternative
calculation method is required.  Also run separately for day and night

4) Merge the day and night files to make _both.  Run for the 5x5 monthly and the 1x1 pentad climatologies
separately.

5) Make the complete data files, which merges all the annual files together to produce a single final
file.  For the pentad values, it was not possible to keep all the variables in the same file, so one file
per variable is output (Memory issues).  

***************************************************************

SPICE/SLURM

To run the gridding_cam.py on SPICE/SLURM, there is a submit_spice_jobs.bash script which will submit each
of jobs, one per month per year, to SPICE.  It only submits the next batch of 12 once there are fewer than 
96 processes owned by hadobs in the queue.

There are a number of other spice scripts present to help run the final sections:
  spice_dailies_to_pentads.bash
  spice_3hrlies_to_pentads.bash
  spice_make_pentad_climatology.bash
Which just run each of the python scripts alone.

***************************************************************

Files:

gridding_cam.py			Reads in the raw data.  
				Makes 1x1 3-hrly grids, then 1x1 daily, 1x1 monthly and then 5x5 monthly.
				Outputs all these individual stages
				
dailies_to_pentads.py		Reads in 1x1 daily files and makes annual pentad files
3hrlies_to_pentads.py		Reads in 1x1 3hrly files, makes pentad-averages of the 3hrly values, then
				outputs pentad 1x1 values from average of these 3hrly averages.
				
make_pentad_climatology.py	Takes in the pentads and makes a 1981-2010 climatology

merge_day_night.py		Merge the _day and _night files to make _both file.

make_complete_data_files.py	Takes the annual files to output full-period files.  For pentads only
				possible using one variable per file as there were memory issues.

submit_spice_jobs.bash		Sets the gridding_cam.py jobs running in sequence - a maximum of 24
				processes at once.  

***************************************************************

SPICE files

spice_hadisdh_grid_YYYYMM.bash	The SPICE batch file to set each individual month running

The following all have _day, _night and "all" versions to increase parallelisation

spice_3hrlies_to_pentads*.bash	The SPICE batch files to create the pentads from 3 hrly 1x1

spice_dailies_to_pentads*.bash	The SPICE batch files to create the pentads from daily 1x1

spice_make_pentad_climatology*.bash
				The SPICE batch files to create the pentad climatology, from both 3hrly and
				daily 1x1 versions.
